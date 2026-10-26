"""O transporte de rede: WebSocket entre clientes e o servidor autoritativo (WSS em produção).

Esta camada só move texto. Cada conexão vira um id; o texto que chega vai para
`ServidorAutoritativo.receber`, e cada `Envio` que volta vai para a conexão que
ele nomeia. Ela não conhece regra de combate, conta nem gladiador.

Proteções da camada:

- **tamanho**: quadro acima de `protocolo.TAMANHO_MAXIMO` derruba a conexão (é o
  `max_size` do WebSocket); só texto é aceito;
- **conexões**: no máximo `LIMITE_DE_CONEXOES` simultâneas;
- **autenticação no prazo**: conexão que não abre sessão em
  `PRAZO_PARA_AUTENTICAR` segundos é fechada. É política de conexão, não de
  partida: não existe derrota por tempo;
- **abuso de protocolo**: depois de `LIMITE_DE_RECUSAS_DE_PROTOCOLO` mensagens
  malformadas, a conexão é fechada;
- **ordem**: cada conexão tem a sua fila de saída, escrita por uma única tarefa,
  então as mensagens chegam na ordem em que o servidor as produziu; cliente que
  não lê é desconectado em vez de travar os outros;
- **TLS**: o servidor recusa escutar fora do loopback sem certificado, e o
  cliente recusa `ws://` para fora do loopback, a menos que alguém peça
  explicitamente (`permitir_sem_tls`), só para desenvolvimento;
- **log**: os quadros do WebSocket carregam senha e token. O logger entregue à
  biblioteca descarta o conteúdo dos quadros; esta camada registra só ids de
  conexão.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import secrets
import ssl
import threading
from collections.abc import Callable
from urllib.parse import urlsplit

from websockets.asyncio.server import Server, ServerConnection, serve
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import ClientConnection, connect

from src.multiplayer.protocolo import TAMANHO_MAXIMO
from src.multiplayer.servidor import Envio, ServidorAutoritativo

LIMITE_DE_CONEXOES = 64
PRAZO_PARA_AUTENTICAR = 30.0
LIMITE_DE_RECUSAS_DE_PROTOCOLO = 10
FILA_DE_SAIDA = 256
PORTA_PADRAO = 8765
_RECUSAS_DE_PROTOCOLO = {
    "mensagem_invalida",
    "tipo_desconhecido",
    "campos_invalidos",
    "acao_invalida",
}

log = logging.getLogger("toj.multiplayer.rede")


class _SemConteudoDosQuadros(logging.Filter):
    """O `websockets` registra quadros como `"< %s"` e `"> %s"`: eles nunca passam."""

    def filter(self, record: logging.LogRecord) -> bool:
        return not (isinstance(record.msg, str) and record.msg[:2] in ("< ", "> "))


_log_do_websocket = logging.getLogger("toj.multiplayer.rede.websocket")
_log_do_websocket.addFilter(_SemConteudoDosQuadros())


class ConfiguracaoInseguraError(ValueError):
    """Tráfego de senha e token sem TLS fora do loopback, sem pedido explícito."""


def e_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def tls_do_servidor(certificado: str, chave: str) -> ssl.SSLContext:
    contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contexto.minimum_version = ssl.TLSVersion.TLSv1_2
    contexto.load_cert_chain(certificado, chave)
    return contexto


def tls_do_cliente(autoridade: str | None = None) -> ssl.SSLContext:
    """Verifica o certificado e o nome do servidor; `autoridade` aceita uma CA própria."""
    contexto = ssl.create_default_context(cafile=autoridade)
    contexto.minimum_version = ssl.TLSVersion.TLSv1_2
    return contexto


async def _esvaziar(saida: asyncio.Queue, prazo: float = 1.0) -> None:
    laco = asyncio.get_running_loop()
    limite = laco.time() + prazo
    while not saida.empty() and laco.time() < limite:
        await asyncio.sleep(0.01)


def _recusa_de_protocolo(envio: Envio) -> bool:
    try:
        mensagem = json.loads(envio.texto)
    except ValueError:
        return False
    return mensagem.get("tipo") == "recusado" and mensagem.get("motivo") in _RECUSAS_DE_PROTOCOLO


# --- servidor ------------------------------------------------------------------------


class ServidorDeRede:
    """O servidor autoritativo atrás de um WebSocket."""

    def __init__(
        self,
        servidor: ServidorAutoritativo,
        host: str = "127.0.0.1",
        porta: int = PORTA_PADRAO,
        *,
        tls: ssl.SSLContext | None = None,
        permitir_sem_tls: bool = False,
        limite_de_conexoes: int = LIMITE_DE_CONEXOES,
        prazo_para_autenticar: float = PRAZO_PARA_AUTENTICAR,
    ) -> None:
        if tls is None and not e_loopback(host) and not permitir_sem_tls:
            raise ConfiguracaoInseguraError(
                f"Escutar em {host} sem TLS exporia senhas e tokens: forneça certificado e "
                "chave, ou peça explicitamente o modo inseguro de desenvolvimento."
            )
        self.servidor = servidor
        self.host = host
        self.porta = porta
        self.tls = tls
        self.limite_de_conexoes = limite_de_conexoes
        self.prazo_para_autenticar = prazo_para_autenticar
        self._conexoes: dict[str, tuple[ServerConnection, asyncio.Queue]] = {}
        self._ws: Server | None = None

    @property
    def url(self) -> str:
        esquema = "wss" if self.tls is not None else "ws"
        return f"{esquema}://{self.host}:{self.porta}"

    @property
    def conexoes_abertas(self) -> int:
        return len(self._conexoes)

    async def iniciar(self) -> None:
        self._ws = await serve(
            self._atender,
            self.host,
            self.porta,
            ssl=self.tls,
            max_size=TAMANHO_MAXIMO,
            max_queue=16,
            open_timeout=10,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=5,
            logger=_log_do_websocket,
        )
        self.porta = self._ws.sockets[0].getsockname()[1]
        log.info("servidor escutando em %s", self.url)

    async def encerrar(self) -> None:
        if self._ws is not None:
            self._ws.close()
            await self._ws.wait_closed()
            self._ws = None

    async def servir_para_sempre(self) -> None:
        await self.iniciar()
        try:
            await asyncio.Future()
        finally:
            await self.encerrar()

    def entregar(self, envios) -> None:
        """Mensagens que o servidor produziu fora de uma requisição (atualização, anulação)."""
        for envio in envios:
            self._despachar(envio)

    def _despachar(self, envio: Envio) -> None:
        alvo = self._conexoes.get(envio.conexao)
        if alvo is None:
            return
        ws, saida = alvo
        try:
            saida.put_nowait(envio.texto)
        except asyncio.QueueFull:
            log.warning("conexão %s não lê as mensagens; fechando", envio.conexao)
            asyncio.ensure_future(ws.close(1008, "cliente lento demais"))

    async def _escrever(self, ws: ServerConnection, saida: asyncio.Queue) -> None:
        try:
            while True:
                await ws.send(await saida.get())
        except ConnectionClosed:
            return

    async def _vigiar(self, conexao: str, ws: ServerConnection) -> None:
        await asyncio.sleep(self.prazo_para_autenticar)
        if self.servidor.sessao_da_conexao(conexao) is None:
            log.info("conexão %s sem autenticação no prazo; fechando", conexao)
            await ws.close(1008, "autenticação fora do prazo")

    async def _atender(self, ws: ServerConnection) -> None:
        if len(self._conexoes) >= self.limite_de_conexoes:
            await ws.close(1013, "servidor cheio")
            return
        conexao = secrets.token_hex(8)
        saida: asyncio.Queue = asyncio.Queue(maxsize=FILA_DE_SAIDA)
        self._conexoes[conexao] = (ws, saida)
        escritor = asyncio.create_task(self._escrever(ws, saida))
        vigia = asyncio.create_task(self._vigiar(conexao, ws))
        log.info("conexão %s aberta", conexao)
        recusas = 0
        try:
            async for texto in ws:
                if not isinstance(texto, str):
                    await ws.close(1003, "o protocolo só aceita texto")
                    break
                envios = self.servidor.receber(conexao, texto)
                for envio in envios:
                    self._despachar(envio)
                recusas += sum(
                    1 for e in envios if e.conexao == conexao and _recusa_de_protocolo(e)
                )
                if recusas >= LIMITE_DE_RECUSAS_DE_PROTOCOLO:
                    await _esvaziar(saida)  # a última recusa sai antes do fechamento
                    await ws.close(1008, "mensagens inválidas demais")
                    break
        except ConnectionClosed:
            pass
        finally:
            vigia.cancel()
            self._conexoes.pop(conexao, None)
            self.servidor.desconectar(conexao)
            escritor.cancel()
            log.info("conexão %s fechada", conexao)


class ServidorEmThread:
    """O servidor de rede num thread próprio, com o seu laço asyncio.

    Para testes e para quem quer o servidor no mesmo processo de outra coisa.
    Mexer no `ServidorAutoritativo` por fora só é seguro por `executar`, que
    roda a função dentro do laço.
    """

    def __init__(self, rede: ServidorDeRede) -> None:
        self.rede = rede
        self._laco: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._pronto = threading.Event()
        self._erro: BaseException | None = None

    @property
    def url(self) -> str:
        return self.rede.url

    def __enter__(self) -> ServidorEmThread:
        def rodar() -> None:
            laco = asyncio.new_event_loop()
            self._laco = laco
            asyncio.set_event_loop(laco)
            try:
                laco.run_until_complete(self.rede.iniciar())
            except BaseException as erro:  # devolvido a quem abriu o servidor
                self._erro = erro
                self._pronto.set()
                return
            self._pronto.set()
            laco.run_forever()
            laco.run_until_complete(self.rede.encerrar())
            pendentes = asyncio.all_tasks(laco)
            for tarefa in pendentes:
                tarefa.cancel()
            laco.run_until_complete(asyncio.gather(*pendentes, return_exceptions=True))
            laco.close()

        self._thread = threading.Thread(target=rodar, name="toj-servidor-de-rede", daemon=True)
        self._thread.start()
        self._pronto.wait(10)
        if self._erro is not None:
            raise self._erro
        return self

    def executar(self, funcao: Callable, *args):
        async def chamar():
            return funcao(*args)

        return asyncio.run_coroutine_threadsafe(chamar(), self._laco).result(10)

    def entregar(self, envios) -> None:
        self.executar(self.rede.entregar, list(envios))

    def __exit__(self, *_exc) -> None:
        if self._laco is not None:
            self._laco.call_soon_threadsafe(self._laco.stop)
        if self._thread is not None:
            self._thread.join(10)


# --- cliente -------------------------------------------------------------------------


class ConexaoDeRede:
    """O lado do cliente: um WebSocket síncrono que manda e recebe texto."""

    def __init__(
        self,
        url: str,
        *,
        tls: ssl.SSLContext | None = None,
        permitir_sem_tls: bool = False,
        prazo: float = 10.0,
    ) -> None:
        partes = urlsplit(url)
        if partes.scheme not in ("ws", "wss") or not partes.hostname:
            raise ValueError("Endereço do servidor: ws://host:porta ou wss://host:porta.")
        if partes.scheme == "ws" and not e_loopback(partes.hostname) and not permitir_sem_tls:
            raise ConfiguracaoInseguraError(
                "ws:// fora do loopback mandaria senha e token sem criptografia: use wss://."
            )
        if partes.scheme == "wss" and tls is None:
            tls = tls_do_cliente()
        self._ws: ClientConnection = connect(
            url,
            ssl=tls if partes.scheme == "wss" else None,
            max_size=TAMANHO_MAXIMO,
            open_timeout=prazo,
            close_timeout=5,
            logger=_log_do_websocket,
        )

    def enviar(self, texto: str) -> None:
        self._ws.send(texto)

    def receber(self, prazo: float | None = None) -> str:
        """O próximo texto do servidor. `TimeoutError` se nada chegar no prazo."""
        mensagem = self._ws.recv(timeout=prazo)
        if not isinstance(mensagem, str):
            raise ValueError("O servidor mandou um quadro binário.")
        return mensagem

    def fechar(self) -> None:
        self._ws.close()

    def __enter__(self) -> ConexaoDeRede:
        return self

    def __exit__(self, *_exc) -> None:
        self.fechar()
