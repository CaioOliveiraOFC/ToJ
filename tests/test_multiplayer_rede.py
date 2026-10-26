"""Multiplayer humano × humano pela rede de verdade (Fase 4, §2, §5, §6).

Tudo aqui passa por WebSocket real: um servidor escutando no loopback e clientes
em conexões próprias, como dois computadores. Nada fala direto com o objeto do
servidor, a não ser para conferir o estado depois.
"""

from __future__ import annotations

import json
import logging
import random
import shutil
import ssl
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from websockets.exceptions import ConnectionClosed

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mechanics.pvp_duel import Duel  # noqa: E402
from src.multiplayer import compatibilidade as compat  # noqa: E402
from src.multiplayer import protocolo  # noqa: E402
from src.multiplayer.rede import (  # noqa: E402
    ConexaoDeRede,
    ConfiguracaoInseguraError,
    ServidorDeRede,
    ServidorEmThread,
    tls_do_cliente,
    tls_do_servidor,
)
from src.multiplayer.servidor import CONCLUIDA, reproduzir  # noqa: E402
from tests._multiplayer_apoio import (  # noqa: E402
    SENHAS,
    SNAPSHOTS,
    Ataca,
    PrimeiraSkill,
    cliente,
    conta_id,
    manifesto_de_outra_versao,
    outra_identidade,
    registro,
    servidor,
    sha256_do_arquivo,
)
from tools import toj_multiplayer as terminal  # noqa: E402


class Jogador:
    """Um jogador num "computador" próprio: uma conexão WebSocket só dele."""

    def __init__(self, url: str, usuario: str, controlador=None, *, identidade=None, **rede):
        self.usuario = usuario
        self.cli = cliente(usuario, controlador, identidade)
        self.con = ConexaoDeRede(url, **rede)

    def mandar(self, texto: str) -> None:
        self.con.enviar(texto)

    def proxima(self, prazo: float = 5.0) -> dict:
        texto = self.con.receber(prazo)
        for resposta in self.cli.receber(texto):
            self.con.enviar(resposta)
        return self.cli.recebidas[-1]

    def esperar(self, *tipos: str, prazo: float = 10.0) -> dict:
        limite = time.monotonic() + prazo
        while True:
            mensagem = self.proxima(max(0.05, limite - time.monotonic()))
            if mensagem["tipo"] in tipos or mensagem["tipo"] == "recusado":
                return mensagem

    def silencio(self, prazo: float = 0.3) -> bool:
        try:
            self.con.receber(prazo)
        except TimeoutError:
            return True
        return False

    def entrar(self, senha: str | None = None) -> dict:
        self.mandar(self.cli.login(self.usuario, senha or SENHAS[self.usuario]))
        resposta = self.esperar("autenticado")
        if resposta["tipo"] == "recusado":
            return resposta
        self.mandar(self.cli.ola())
        return self.esperar("bem_vindo")

    def fechar(self) -> None:
        self.con.fechar()


@pytest.fixture
def no_ar():
    """Um servidor de verdade, escutando numa porta livre do loopback."""
    srv = servidor(registro(ana=("W23", "W01"), bia=("W64", "W02"), caio="W03"))
    with ServidorEmThread(ServidorDeRede(srv, "127.0.0.1", 0)) as rodando:
        yield srv, rodando


def _sala(url, anfitriao_ctl=None, convidado_ctl=None, gladiadores=("W23", "W64")):
    """ana cria a sala, bia entra com o código. Devolve os dois jogadores já em partida."""
    ana, bia = Jogador(url, "ana", anfitriao_ctl), Jogador(url, "bia", convidado_ctl)
    assert ana.entrar()["tipo"] == "bem_vindo"
    assert bia.entrar()["tipo"] == "bem_vindo"
    ana.mandar(ana.cli.criar_sala(gladiadores[0]))
    sala = ana.esperar("sala_criada")["sala"]
    bia.mandar(bia.cli.entrar_na_sala(sala, gladiadores[1]))
    return ana, bia


def _jogar_em_paralelo(*jogadores: Jogador, prazo: float = 60.0) -> dict:
    """Cada jogador no seu thread, como em computadores diferentes, até o fim."""
    fins: dict[str, dict] = {}
    erros: list[BaseException] = []

    def rodar(jogador: Jogador) -> None:
        try:
            fins[jogador.usuario] = jogador.esperar("fim", prazo=prazo)
        except BaseException as erro:  # devolvido ao teste
            erros.append(erro)

    threads = [threading.Thread(target=rodar, args=(j,)) for j in jogadores]
    for t in threads:
        t.start()
    for t in threads:
        t.join(prazo + 5)
    assert not erros, erros
    return fins


# --- dois clientes reais -----------------------------------------------------------------


def test_dois_clientes_reais_jogam_uma_partida_inteira(no_ar):
    srv, rodando = no_ar
    antes = {p.name: sha256_do_arquivo(p) for p in SNAPSHOTS.glob("*.json")}
    ana, bia = _sala(rodando.url, PrimeiraSkill(), Ataca())
    criada_ana = ana.esperar("partida_criada")
    criada_bia = bia.esperar("partida_criada")
    # As informações públicas do confronto, dos dois lados.
    assert criada_ana["adversario"]["usuario"] == "bia"
    assert criada_bia["adversario"]["usuario"] == "ana"
    assert criada_ana["voce"] == {
        k: v for k, v in criada_bia["adversario"].items() if k != "usuario"
    }

    fins = _jogar_em_paralelo(ana, bia)
    assert fins["ana"] == fins["bia"]
    fim = fins["ana"]
    assert fim["estado"] == CONCLUIDA and fim["motivo"] == "ko"

    # O desfecho é do servidor, por conta: ninguém o declarou.
    (desfecho,) = rodando.executar(srv.resultados.classificaveis)
    vencedor = conta_id("ana") if fim["vencedor"] == "p1" else conta_id("bia")
    assert desfecho.vencedor == vencedor

    # O motor canônico rejoga o mesmo duelo, rodada a rodada, com a mesma semente.
    exportado = rodando.executar(srv.exportar, fim["partida"])
    rejogado = reproduzir(exportado, srv.gladiadores, srv.impressao)
    original = rodando.executar(lambda: srv.partida(fim["partida"]).duelo)
    assert rejogado.history == original.history
    assert rejogado.result == original.result

    direto = Duel(
        srv.gladiadores.preparar("W23")[0],
        srv.gladiadores.preparar("W64")[0],
        rng=random.Random(exportado["semente"]),
    )
    for rodada in exportado["rodadas"]:
        direto.play_round({lado: protocolo.acao_de(a) for lado, a in rodada["acoes"].items()})
    assert direto.history == original.history

    # E os snapshots publicados não mudaram.
    assert {p.name: sha256_do_arquivo(p) for p in SNAPSHOTS.glob("*.json")} == antes
    ana.fechar()
    bia.fechar()


def test_partidas_e_sessoes_independentes(no_ar):
    """Duas salas ao mesmo tempo, quatro conexões: cada sessão só vê a própria partida."""
    srv, rodando = no_ar
    ana, bia = _sala(rodando.url, Ataca(), Ataca())
    caio = Jogador(rodando.url, "caio", Ataca())
    caio.entrar()
    caio.mandar(caio.cli.criar_sala("W03"))
    assert caio.esperar("sala_criada")["tipo"] == "sala_criada"
    fins = _jogar_em_paralelo(ana, bia)
    assert fins["ana"]["partida"] == fins["bia"]["partida"]
    assert caio.silencio()  # nada da partida dos outros chega a caio
    assert rodando.executar(srv.salas_abertas) == ("caio",)
    for j in (ana, bia, caio):
        j.fechar()


# --- handshake e autenticação pela rede ---------------------------------------------------


def test_handshake_valido_e_invalido_pela_rede(no_ar):
    srv, rodando = no_ar
    valido = Jogador(rodando.url, "ana")
    assert valido.entrar()["tipo"] == "bem_vindo"

    velho = Jogador(rodando.url, "bia", identidade=outra_identidade(jogo="0.3.9-arena.9"))
    resposta = velho.entrar()
    assert resposta["motivo"] == compat.VERSAO_DO_JOGO
    assert resposta["atualizacao_obrigatoria"] is True

    adulterado = Jogador(
        rodando.url, "bia", identidade=outra_identidade(grupos={"regras": "0" * 64})
    )
    assert adulterado.entrar()["motivo"] == compat.CONTEUDO
    for j in (valido, velho, adulterado):
        j.fechar()


def test_autenticacao_pela_rede_valida_errada_e_adulterada(no_ar):
    srv, rodando = no_ar
    errada = Jogador(rodando.url, "ana")
    assert errada.entrar(senha="senha-errada-123")["motivo"] == "credenciais_invalidas"

    adulterada = Jogador(rodando.url, "ana")
    adulterada.mandar(adulterada.cli.login("ana", SENHAS["ana"]))
    adulterada.esperar("autenticado")
    adulterada.cli.token = adulterada.cli.token[:-2] + "xx"
    adulterada.mandar(adulterada.cli.ola())
    assert adulterada.esperar("bem_vindo")["motivo"] == "token_invalido"

    valida = Jogador(rodando.url, "ana")
    assert valida.entrar()["usuario"] == "ana"
    for j in (errada, adulterada, valida):
        j.fechar()


def test_token_expirado_pela_rede(no_ar):
    srv, rodando = no_ar
    agora = [time.time()]

    def antecipado():
        return agora[0]

    from src.multiplayer.contas import ContasLocais, TokensAssinados

    curtas = ContasLocais(None, TokensAssinados(bytes(range(32)), 60, antecipado))
    curtas.criar("ana", SENHAS["ana"])
    token = curtas.entrar("ana", SENHAS["ana"]).token
    agora[0] += 120  # o relógio de quem valida já passou da expiração
    rodando.executar(setattr, srv, "autenticador", curtas)
    jogador = Jogador(rodando.url, "ana")
    jogador.cli.token = token
    jogador.mandar(jogador.cli.ola())
    resposta = jogador.esperar("bem_vindo")
    assert resposta["motivo"] == "token_invalido" and "expirado" in resposta["mensagem"]
    jogador.fechar()


def test_gladiador_alheio_e_mesma_conta_pela_rede(no_ar):
    srv, rodando = no_ar
    ana = Jogador(rodando.url, "ana")
    ana.entrar()
    ana.mandar(ana.cli.criar_sala("W64"))  # é da bia
    assert ana.esperar("sala_criada")["motivo"] == "gladiador_alheio"

    outra_ana = Jogador(rodando.url, "ana")
    assert outra_ana.entrar()["motivo"] == "conta_ja_conectada"
    ana.fechar()
    outra_ana.fechar()


# --- a rodada: sigilo, ilegalidade, queda ---------------------------------------------------


def test_decisoes_simultaneas_sem_revelar_a_escolha_antes_do_lock(no_ar):
    srv, rodando = no_ar
    ana, bia = _sala(rodando.url)
    ana.esperar("observacao")
    visao_de_bia = protocolo.visao_de_dict(bia.esperar("observacao")["visao"])

    ana.mandar(ana.cli.acao(1, protocolo.acao_de({"kind": "attack"})))
    assert ana.esperar("acao_recebida")["rodada"] == 1
    # bia não recebe nada: nem a ação, nem que ana já escolheu.
    assert bia.silencio(0.5)
    assert rodando.executar(lambda: srv.partida(ana.cli.partida).duelo.round_number) == 1

    carta = next(a.skill_id for a in visao_de_bia.legal_actions if a.kind == "skill")
    bia.mandar(bia.cli.acao(1, protocolo.acao_de({"kind": "skill", "skill_id": carta})))
    rodada_ana = ana.esperar("rodada")["rodada"]
    rodada_bia = bia.esperar("rodada")["rodada"]
    assert rodada_ana == rodada_bia
    assert rodada_ana["acoes"] == {
        "p1": {"kind": "attack", "skill_id": None},
        "p2": {"kind": "skill", "skill_id": carta},
    }
    assert "initiative" not in rodada_ana
    ana.fechar()
    bia.fechar()


def test_acao_ilegal_pela_rede_nao_muda_o_estado(no_ar):
    srv, rodando = no_ar
    ana, bia = _sala(rodando.url)
    ana.esperar("observacao")

    def estado():
        partida = srv.partida(ana.cli.partida)
        return partida.duelo.round_number, partida.duelo.history, dict(partida.pendentes)

    antes = rodando.executar(estado)
    ana.mandar(
        ana.cli.acao(1, protocolo.acao_de({"kind": "skill", "skill_id": "carta_que_nao_tenho"}))
    )
    assert ana.esperar("acao_recusada")["motivo"] == "acao_ilegal"
    ana.mandar(
        json.dumps(
            {
                "tipo": "acao",
                "partida": ana.cli.partida,
                "rodada": 1,
                "acao": {"kind": "attack"},
                "hp": 99999,
            }
        )
    )
    assert ana.esperar("recusado")["motivo"] == "campos_invalidos"
    ana.mandar(json.dumps({"tipo": "resultado", "vencedor": "p1"}))
    assert ana.esperar("recusado")["motivo"] == "tipo_desconhecido"
    assert rodando.executar(estado) == antes
    assert rodando.executar(srv.resultados.todos) == ()
    ana.fechar()
    bia.fechar()


def test_queda_de_conexao_nao_corrompe_o_duelo(no_ar):
    srv, rodando = no_ar
    ana, bia = _sala(rodando.url, None, Ataca())
    # bia joga no "computador" dela o tempo todo, alheia à queda de ana.
    fim_de_bia: dict = {}
    computador_de_bia = threading.Thread(
        target=lambda: fim_de_bia.update(bia.esperar("fim", prazo=60))
    )
    computador_de_bia.start()
    partida_id = ana.esperar("partida_criada")["partida"]
    ataque = protocolo.acao_de({"kind": "attack"})
    for numero in (1, 2, 3):
        ana.esperar("observacao")
        ana.mandar(ana.cli.acao(numero, ataque))
        ana.esperar("rodada")
    ana.esperar("observacao")

    def fotografia():
        p = srv.partida(partida_id)
        return p.estado, p.duelo.round_number, p.duelo.history, dict(p.pendentes)

    antes = rodando.executar(fotografia)
    ana.fechar()  # a conexão cai no meio da partida
    time.sleep(0.3)
    depois = rodando.executar(fotografia)
    # bia já escolheu a rodada 4 (o controlador dela responde sozinho); nada mais mudou.
    assert depois[:3] == antes[:3]
    assert depois[0] == "em_andamento"
    assert rodando.executar(srv.resultados.todos) == ()

    # ana volta por outra conexão, com a sessão e um token da mesma conta.
    volta = Jogador(rodando.url, "ana", Ataca())
    volta.cli.sessao, volta.cli.token = ana.cli.sessao, ana.cli.token
    volta.mandar(volta.cli.reconectar())
    assert volta.esperar("bem_vindo")["sessao"] == ana.cli.sessao
    assert volta.esperar("partida_criada")["partida"] == partida_id

    fim_de_ana = volta.esperar("fim", prazo=60)
    computador_de_bia.join(65)
    assert fim_de_ana == fim_de_bia
    assert fim_de_ana["partida"] == partida_id and fim_de_ana["estado"] == CONCLUIDA
    exportado = rodando.executar(srv.exportar, partida_id)
    reproduzir(exportado, srv.gladiadores, srv.impressao)  # consistente do começo ao fim
    volta.fechar()
    bia.fechar()


# --- limites da conexão -------------------------------------------------------------------


def _fechada_com(jogador: Jogador, prazo: float = 3.0) -> int | None:
    try:
        while True:
            jogador.con.receber(prazo)
    except ConnectionClosed as fechada:
        return fechada.rcvd.code if fechada.rcvd else None
    except TimeoutError:
        return None


def test_mensagem_acima_do_limite_derruba_a_conexao(no_ar):
    _, rodando = no_ar
    jogador = Jogador(rodando.url, "ana")
    jogador.mandar("x" * (protocolo.TAMANHO_MAXIMO + 1))
    assert _fechada_com(jogador) == 1009  # message too big


def test_quadro_binario_e_recusado(no_ar):
    _, rodando = no_ar
    jogador = Jogador(rodando.url, "ana")
    jogador.con._ws.send(b"\x00\x01binario")
    assert _fechada_com(jogador) == 1003


def test_abuso_de_protocolo_fecha_a_conexao(no_ar):
    _, rodando = no_ar
    jogador = Jogador(rodando.url, "ana")
    for _ in range(10):
        jogador.mandar("isto não é json")
    assert _fechada_com(jogador) == 1008


def test_conexao_sem_autenticacao_no_prazo_e_fechada():
    srv = servidor()
    rede = ServidorDeRede(srv, "127.0.0.1", 0, prazo_para_autenticar=0.3)
    with ServidorEmThread(rede) as rodando:
        parado = Jogador(rodando.url, "ana")
        assert _fechada_com(parado) == 1008
        autenticado = Jogador(rodando.url, "bia")
        autenticado.entrar()
        assert autenticado.silencio(0.6)  # quem abriu sessão continua conectado


def test_limite_de_conexoes():
    with ServidorEmThread(ServidorDeRede(servidor(), "127.0.0.1", 0, limite_de_conexoes=1)) as r:
        primeira = Jogador(r.url, "ana")
        assert primeira.entrar()["tipo"] == "bem_vindo"
        segunda = Jogador(r.url, "bia")
        assert _fechada_com(segunda) == 1013


# --- TLS ------------------------------------------------------------------------------


def _certificado(pasta: Path) -> tuple[str, str]:
    if shutil.which("openssl") is None:
        pytest.skip("openssl ausente")
    chave, certificado = pasta / "chave.pem", pasta / "certificado.pem"
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-days",
            "1",
            "-keyout",
            str(chave),
            "-out",
            str(certificado),
            "-subj",
            "/CN=localhost",
            "-addext",
            "subjectAltName=DNS:localhost,IP:127.0.0.1",
        ],
        check=True,
        capture_output=True,
    )
    return str(certificado), str(chave)


def test_wss_com_certificado_verificado(tmp_path):
    certificado, chave = _certificado(tmp_path)
    rede = ServidorDeRede(servidor(), "127.0.0.1", 0, tls=tls_do_servidor(certificado, chave))
    with ServidorEmThread(rede) as rodando:
        assert rodando.url.startswith("wss://")
        seguro = Jogador(rodando.url, "ana", tls=tls_do_cliente(certificado))
        assert seguro.entrar()["tipo"] == "bem_vindo"
        seguro.fechar()
        # Sem a autoridade do certificado, o cliente não confia no servidor.
        with pytest.raises(ssl.SSLCertVerificationError):
            Jogador(rodando.url, "bia")
        # E ws:// puro contra o servidor TLS não passa do handshake.
        with pytest.raises(Exception):  # qualquer falha de handshake serve
            Jogador(rodando.url.replace("wss://", "ws://"), "bia").entrar()


def test_sem_tls_fora_do_loopback_e_recusado_dos_dois_lados():
    with pytest.raises(ConfiguracaoInseguraError):
        ServidorDeRede(servidor(), "0.0.0.0", 0)
    with pytest.raises(ConfiguracaoInseguraError):
        ConexaoDeRede("ws://192.0.2.10:8765")
    # Pedido explícito, só para desenvolvimento.
    ServidorDeRede(servidor(), "0.0.0.0", 0, permitir_sem_tls=True)


# --- log sem segredo -------------------------------------------------------------------------


def test_senha_e_token_nunca_vao_para_o_log(no_ar, caplog):
    srv, rodando = no_ar
    caplog.set_level(logging.DEBUG)
    ana, bia = _sala(rodando.url, Ataca(), Ataca())
    _jogar_em_paralelo(ana, bia)
    texto = caplog.text
    # O log estava em DEBUG de verdade, inclusive o do websocket...
    assert any(r.name.startswith("toj.multiplayer.rede") for r in caplog.records)
    assert "connection is OPEN" in texto or "conexão" in texto
    # ...e mesmo assim nenhuma senha nem token aparece.
    for segredo in (SENHAS["ana"], SENHAS["bia"], ana.cli.token, bia.cli.token):
        assert segredo not in texto
    assert ana.cli.sessao not in texto
    ana.fechar()
    bia.fechar()


# --- atualização durante a partida, pela rede --------------------------------------------------


def test_drenagem_pela_rede_termina_a_partida_e_recusa_o_que_e_novo(no_ar):
    srv, rodando = no_ar
    ana, bia = _sala(rodando.url, Ataca(), None)
    bia.esperar("observacao")
    caio = Jogador(rodando.url, "caio")
    caio.entrar()
    caio.mandar(caio.cli.criar_sala("W03"))
    caio.esperar("sala_criada")

    rodando.entregar(rodando.executar(srv.drenar))
    assert caio.esperar("recusado")["motivo"] == compat.SERVIDOR_EM_ATUALIZACAO
    atrasado = Jogador(rodando.url, "caio")
    atrasado.mandar(atrasado.cli.login("caio", SENHAS["caio"]))
    assert atrasado.esperar("autenticado")["motivo"] == compat.SERVIDOR_EM_ATUALIZACAO

    # A partida em andamento segue na versão em que nasceu, até o fim.
    bia.cli.controlador = Ataca()
    bia.mandar(bia.cli.acao(1, protocolo.acao_de({"kind": "attack"})))
    fins = _jogar_em_paralelo(ana, bia)
    assert fins["ana"]["estado"] == CONCLUIDA
    for j in (ana, bia, caio, atrasado):
        j.fechar()


def test_servidor_de_outra_versao_recusa_o_cliente_antigo():
    nova = servidor(manifesto=manifesto_de_outra_versao())
    with ServidorEmThread(ServidorDeRede(nova, "127.0.0.1", 0)) as rodando:
        antigo = Jogador(rodando.url, "ana")
        resposta = antigo.entrar()
        assert resposta["motivo"] == compat.VERSAO_DO_JOGO
        assert resposta["versao_exigida"] == nova.identidade.jogo
        atualizado = Jogador(rodando.url, "ana", identidade=nova.identidade)
        assert atualizado.entrar()["tipo"] == "bem_vindo"


# --- o terminal, humano × humano ---------------------------------------------------------


def test_o_cliente_de_terminal_joga_humano_contra_humano(no_ar):
    """O fluxo do terminal inteiro, com teclado roteirizado, em duas conexões reais."""
    srv, rodando = no_ar
    codigo: list[str] = []
    saidas: dict[str, list[str]] = {"ana": [], "bia": []}

    def teclado(usuario: str):
        def entrada(pergunta: str) -> str:
            if pergunta.startswith("Código da sala"):
                limite = time.monotonic() + 10
                while not codigo and time.monotonic() < limite:
                    time.sleep(0.02)
                return codigo[0]
            if pergunta.startswith("Render-se"):
                return "n"
            return "1"

        return entrada

    def saida(usuario: str):
        def escrever(texto: str) -> None:
            saidas[usuario].append(texto)
            if texto.startswith("Sala "):
                codigo.append(texto.split()[1])

        return escrever

    fins: dict[str, dict | None] = {}

    def jogar_como(usuario: str) -> None:
        tela = terminal.TerminalDeDuelo(teclado(usuario), saida(usuario))
        if usuario == "bia":
            # bia escolhe "Entrar na sala de alguém" (opção 2) no menu de partida.
            original = tela.escolher_numero

            def escolher(titulo, opcoes):
                if titulo == "Partida direta:":
                    tela.saida(titulo)
                    return 1
                return original(titulo, opcoes)

            tela.escolher_numero = escolher
        fins[usuario] = terminal.jogar(rodando.url, usuario, SENHAS[usuario], tela)

    threads = [
        threading.Thread(target=jogar_como, args=("ana",)),
        threading.Thread(target=jogar_como, args=("bia",)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(60)

    assert fins["ana"] is not None and fins["bia"] is not None
    assert fins["ana"] == fins["bia"]
    texto_ana, texto_bia = "\n".join(saidas["ana"]), "\n".join(saidas["bia"])
    assert "Sala " in texto_ana
    assert "Adversário (bia)" in texto_ana and "Adversário (ana)" in texto_bia
    vitorias = [t for t in (texto_ana, texto_bia) if "=== VITÓRIA" in t]
    derrotas = [t for t in (texto_ana, texto_bia) if "=== DERROTA" in t]
    assert len(vitorias) == len(derrotas) == 1
    # A senha não aparece em nada que o terminal mostrou.
    assert SENHAS["ana"] not in texto_ana and SENHAS["bia"] not in texto_bia
