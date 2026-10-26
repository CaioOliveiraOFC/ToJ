"""O servidor autoritativo da Arena multiplayer.

O cliente manda texto; o servidor decide tudo. Uma instância:

- só aceita quem tem a MESMA identidade de versão que ela, e confere de novo na
  entrada da fila ou da sala, na criação da partida e na reconexão;
- só abre sessão para quem se autenticou: a conta da sessão é a que o
  `Autenticador` extraiu do token, nunca um nome que o cliente declara;
- guarda os gladiadores e os donos (`RegistroDeGladiadores`): o cliente só nomeia
  o id, o servidor confere que é da conta da sessão, e a validação estrita roda a
  cada preparação. Uma conta nunca joga os dois lados da mesma partida;
- valida a ação contra `Duel.legal_actions` e roda o motor canônico
  (`Duel.play_round`); o cliente nunca informa HP, dano, atributo, equipamento,
  recarga, resultado nem MMR — o protocolo não tem onde;
- não mostra a ação de um lado ao outro antes do lock: quem age recebe só
  `acao_recebida`, e o adversário só vê a rodada resolvida;
- prende cada partida à impressão da versão em que ela nasceu.

Partidas começam por **sala direta** (um jogador cria e passa o código, o outro
entra) ou pela fila simples, que só junta os dois primeiros que esperam. Não há
matchmaking público, MMR nem bot.

Atualização:

- `drenar()`: a instância para de aceitar sessão, fila, sala e partida novas, e
  deixa as partidas em andamento terminarem;
- `retomar(registro)`: uma instância da MESMA versão continua uma partida
  exportada, rejogando as ações registradas e conferindo HP e MP de cada rodada
  — o motor é determinístico pela semente;
- `anular(...)`: quando nenhuma instância compatível pode continuar, a partida
  termina sem vencedor, sem derrota e fora da classificação.

O servidor não conhece rede: recebe `(conexão, texto)` e devolve os `Envio`s.
Quem transporta é a camada de cima (`rede.ServidorDeRede` na rede,
`transporte.RedeLocal` em processo). O relógio só serve para a expiração do
token; prazo de decisão e de reconexão ainda não existem.
"""

from __future__ import annotations

import random
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from src.mechanics.pvp_duel import SIDES, Duel, DuelAction, InvalidDuelActionError
from src.multiplayer import compatibilidade, protocolo
from src.multiplayer.compatibilidade import Decisao
from src.multiplayer.contas import (
    Autenticador,
    CredenciaisInvalidasError,
    TokenInvalidoError,
)
from src.multiplayer.gladiadores import GladiadorIncompativelError
from src.multiplayer.manifesto import (
    PASTA_DOS_MANIFESTOS,
    RAIZ,
    Identidade,
    Manifesto,
    manifesto_da_instalacao,
)

ATIVO, DRENANDO, DESLIGADO = "ativo", "drenando", "desligado"
EM_ANDAMENTO, CONCLUIDA, ANULADA, TRANSFERIDA = (
    "em_andamento",
    "concluida",
    "anulada",
    "transferida",
)
FORMATO_DO_REGISTRO = 2
TENTATIVAS_DE_LOGIN = 5
_ALFABETO_DA_SALA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _codigo_de_sala() -> str:
    return "".join(secrets.choice(_ALFABETO_DA_SALA) for _ in range(6))


@dataclass(frozen=True)
class Envio:
    """Um texto para uma conexão. Transportar é com a camada de cima."""

    conexao: str
    texto: str = field(repr=False)


class PartidaIncompativelError(RuntimeError):
    """Esta instância não pode continuar a partida: outra versão, outro gladiador
    ou um replay que não reproduz o registrado."""


@dataclass(frozen=True)
class Desfecho:
    """Como uma partida terminou, por conta. `anulada` não tem vencedor nem perdedor."""

    partida: str
    impressao: str
    estado: str
    vencedor: str | None
    perdedor: str | None
    motivo: str
    rodadas: int


class Resultados:
    """O livro de desfechos, compartilhado pelas instâncias.

    Uma classificação (MMR, ainda não implementada) lê só `classificaveis()`:
    partida anulada não registra vitória, derrota nem alteração de classificação.
    """

    def __init__(self) -> None:
        self._desfechos: dict[str, Desfecho] = {}

    def registrar(self, desfecho: Desfecho) -> None:
        if desfecho.partida in self._desfechos:
            raise ValueError(f"A partida {desfecho.partida} já tem desfecho.")
        self._desfechos[desfecho.partida] = desfecho

    def desfecho(self, partida: str) -> Desfecho | None:
        return self._desfechos.get(partida)

    def todos(self) -> tuple[Desfecho, ...]:
        return tuple(self._desfechos.values())

    def classificaveis(self) -> tuple[Desfecho, ...]:
        return tuple(d for d in self._desfechos.values() if d.estado == CONCLUIDA)

    def vitorias(self, conta: str) -> int:
        return sum(1 for d in self.classificaveis() if d.vencedor == conta)

    def derrotas(self, conta: str) -> int:
        return sum(1 for d in self.classificaveis() if d.perdedor == conta)


@dataclass
class Sessao:
    """Uma sessão autenticada. `id` é o segredo de reconexão: não aparece no `repr`."""

    id: str = field(repr=False)
    conta: str
    usuario: str
    identidade: Identidade = field(repr=False)
    conexao: str | None
    expira_em: float = 0
    gladiador: str | None = None
    partida: str | None = None
    sala: str | None = None
    na_fila: bool = False

    @property
    def livre(self) -> bool:
        return self.partida is None and self.sala is None and not self.na_fila


@dataclass(frozen=True)
class LadoDaPartida:
    conta: str
    usuario: str
    sessao: str = field(repr=False)
    gladiador: str = ""
    impressao_do_gladiador: str = ""


@dataclass
class Partida:
    """Uma partida presa à versão (`impressao`) em que nasceu."""

    id: str
    impressao: str
    semente: int
    lados: dict[str, LadoDaPartida]
    duelo: Duel
    rodadas: list[dict] = field(default_factory=list)
    pendentes: dict[str, DuelAction] = field(default_factory=dict)
    estado: str = EM_ANDAMENTO
    desfecho: Desfecho | None = None

    def lado_da_sessao(self, sessao: str) -> str | None:
        return next((lado for lado, dados in self.lados.items() if dados.sessao == sessao), None)

    def registro(self) -> dict:
        """A partida em dado puro: o que outra instância precisa para continuar ou rejogar."""
        resultado = self.duelo.result
        return {
            "formato": FORMATO_DO_REGISTRO,
            "partida": self.id,
            "impressao": self.impressao,
            "semente": self.semente,
            "lados": {
                lado: {
                    "conta": dados.conta,
                    "usuario": dados.usuario,
                    "sessao": dados.sessao,
                    "gladiador": dados.gladiador,
                    "impressao_do_gladiador": dados.impressao_do_gladiador,
                }
                for lado, dados in self.lados.items()
            },
            "rodadas": [dict(r) for r in self.rodadas],
            "estado": self.estado,
            "resultado": None
            if resultado is None
            else {
                "vencedor": resultado.winner,
                "motivo": resultado.reason,
                "rodadas": resultado.rounds,
            },
        }


def reproduzir(registro: dict, gladiadores, impressao: str) -> Duel:
    """Rejoga uma partida registrada no motor canônico, conferindo cada rodada.

    Só roda na versão em que a partida nasceu: registro de outra versão é
    recusado, nunca rejogado com regras divergentes. O gladiador de cada lado
    tem de ser o MESMO registro (pela impressão), e HP e MP ao fim de cada rodada
    têm de bater com o registrado. `gladiadores` é qualquer coisa com
    `preparar(id)` (o registro do servidor ou um acervo).
    """
    if not isinstance(registro, dict) or registro.get("formato") != FORMATO_DO_REGISTRO:
        raise PartidaIncompativelError("Registro de partida em formato desconhecido.")
    if registro.get("impressao") != impressao:
        raise PartidaIncompativelError(
            "A partida pertence a outra versão do jogo: não roda com regras divergentes."
        )
    preparados = []
    for lado in SIDES:
        dados = registro["lados"][lado]
        try:
            gladiador, impressao_do_registro = gladiadores.preparar(dados["gladiador"])
        except GladiadorIncompativelError as erro:
            raise PartidaIncompativelError(f"Gladiador do lado {lado}: {erro}") from erro
        if impressao_do_registro != dados["impressao_do_gladiador"]:
            raise PartidaIncompativelError(
                f"O gladiador do lado {lado} não é o registro da partida."
            )
        preparados.append(gladiador)
    duelo = Duel(*preparados, rng=random.Random(registro["semente"]))
    for numero, rodada in enumerate(registro["rodadas"], start=1):
        try:
            acoes = {lado: protocolo.acao_de(acao) for lado, acao in rodada["acoes"].items()}
            feito = duelo.play_round(acoes)
        except (protocolo.ProtocoloInvalidoError, InvalidDuelActionError) as erro:
            raise PartidaIncompativelError(f"Rodada {numero} não rejoga: {erro}") from erro
        if dict(feito.hp_end) != rodada["hp_fim"] or dict(feito.mp_end) != rodada["mp_fim"]:
            raise PartidaIncompativelError(f"Replay divergente na rodada {numero}.")
    resultado = registro.get("resultado")
    if resultado is not None:
        obtido = duelo.result
        if obtido is None or (obtido.winner, obtido.reason, obtido.rounds) != (
            resultado["vencedor"],
            resultado["motivo"],
            resultado["rodadas"],
        ):
            raise PartidaIncompativelError("O replay não chega ao resultado registrado.")
    return duelo


class ServidorAutoritativo:
    """Uma instância do servidor, presa a UM manifesto.

    `gladiadores` responde `preparar(id)`, `dono_de(id)` e `de(conta)`
    (`registro.RegistroDeGladiadores`); `autenticador` responde `entrar` e
    `validar` (`contas.Autenticador`).
    """

    def __init__(
        self,
        manifesto: Manifesto,
        gladiadores,
        autenticador: Autenticador,
        resultados: Resultados | None = None,
        *,
        sementes: Callable[[], int] | None = None,
        sessoes: Callable[[], str] | None = None,
        ids: Callable[[], str] | None = None,
        salas: Callable[[], str] | None = None,
        relogio: Callable[[], float] = time.time,
    ) -> None:
        self.manifesto = manifesto
        self.gladiadores = gladiadores
        self.autenticador = autenticador
        self.resultados = resultados if resultados is not None else Resultados()
        self.estado = ATIVO
        self._sementes = sementes or (lambda: secrets.randbits(63))
        self._novas_sessoes = sessoes or (lambda: secrets.token_urlsafe(24))
        self._ids = ids or (lambda: secrets.token_hex(8))
        self._codigos = salas or _codigo_de_sala
        self._relogio = relogio
        self._sessoes: dict[str, Sessao] = {}
        self._por_conexao: dict[str, str] = {}
        self._fila: list[str] = []
        self._salas: dict[str, str] = {}
        self._partidas: dict[str, Partida] = {}
        self._falhas_de_login: dict[str, int] = {}

    @classmethod
    def da_instalacao(
        cls,
        gladiadores,
        autenticador: Autenticador,
        resultados: Resultados | None = None,
        *,
        raiz: Path = RAIZ,
        pasta: Path = PASTA_DOS_MANIFESTOS,
        **opcoes,
    ) -> ServidorAutoritativo:
        """O caminho de produção: o manifesto conferido contra o código que está rodando.

        Código que não bate com o manifesto da versão declarada não sobe
        (`InstalacaoDivergenteError`).
        """
        return cls(
            manifesto_da_instalacao(raiz, pasta), gladiadores, autenticador, resultados, **opcoes
        )

    @property
    def identidade(self) -> Identidade:
        return self.manifesto.identidade

    @property
    def impressao(self) -> str:
        return self.identidade.impressao

    # --- leitura ------------------------------------------------------------------

    def partida(self, partida_id: str) -> Partida | None:
        return self._partidas.get(partida_id)

    def partidas_em_andamento(self) -> tuple[str, ...]:
        return tuple(p.id for p in self._partidas.values() if p.estado == EM_ANDAMENTO)

    def na_fila(self) -> tuple[str, ...]:
        return tuple(self._sessoes[s].usuario for s in self._fila)

    def salas_abertas(self) -> tuple[str, ...]:
        return tuple(self._sessoes[s].usuario for s in self._salas.values())

    def sessao_da_conexao(self, conexao: str) -> Sessao | None:
        sessao = self._por_conexao.get(conexao)
        return self._sessoes.get(sessao) if sessao else None

    def exportar(self, partida_id: str) -> dict:
        return self._partidas[partida_id].registro()

    # --- entrada ------------------------------------------------------------------

    def receber(self, conexao: str, texto: str) -> list[Envio]:
        """Uma mensagem do cliente. Devolve o que mandar, para quem."""
        if self.estado == DESLIGADO:
            return [self._recusa(conexao, "servidor_desligado", "Esta instância foi desligada.")]
        try:
            mensagem = protocolo.decodificar_do_cliente(texto)
        except protocolo.ProtocoloInvalidoError as erro:
            return [self._recusa(conexao, erro.motivo, str(erro))]
        tratar = {
            "login": self._ao_login,
            "ola": self._ao_ola,
            "entrar_na_fila": self._ao_entrar_na_fila,
            "sair_da_fila": self._ao_sair_da_fila,
            "criar_sala": self._ao_criar_sala,
            "entrar_na_sala": self._ao_entrar_na_sala,
            "cancelar_sala": self._ao_cancelar_sala,
            "acao": self._ao_acao,
            "reconectar": self._ao_reconectar,
        }[mensagem["tipo"]]
        return tratar(conexao, mensagem)

    def desconectar(self, conexao: str) -> None:
        """A conexão caiu. A sessão fica, para reconectar; fila e sala a esquecem.

        A partida em andamento espera: prazo de reconexão e derrota por
        desconexão (`Duel.forfeit`) dependem do relógio competitivo, que ainda
        não existe — nenhuma política de derrota é inventada aqui.
        """
        self._falhas_de_login.pop(conexao, None)
        sessao_id = self._por_conexao.pop(conexao, None)
        if sessao_id is None:
            return
        sessao = self._sessoes[sessao_id]
        sessao.conexao = None
        self._liberar_espera(sessao)

    def _liberar_espera(self, sessao: Sessao) -> None:
        """Tira a sessão da fila e fecha a sala dela. Não mexe em partida."""
        if sessao.na_fila:
            self._fila.remove(sessao.id)
            sessao.na_fila = False
        if sessao.sala is not None:
            self._salas.pop(sessao.sala, None)
            sessao.sala = None
        if sessao.partida is None:
            sessao.gladiador = None

    # --- mensagens ----------------------------------------------------------------

    def _recusa(
        self,
        conexao: str,
        motivo: str,
        mensagem: str,
        *,
        decisao: Decisao | None = None,
        problemas: tuple[str, ...] = (),
    ) -> Envio:
        return Envio(
            conexao,
            protocolo.codificar(
                "recusado",
                motivo=motivo,
                mensagem=mensagem,
                atualizacao_obrigatoria=bool(
                    decisao is not None and decisao.atualizacao_obrigatoria
                ),
                versao_exigida=decisao.versao_exigida if decisao else None,
                problemas=list(problemas),
            ),
        )

    def _recusa_de(self, conexao: str, decisao: Decisao) -> Envio:
        return self._recusa(
            conexao, decisao.motivo or "recusado", decisao.mensagem, decisao=decisao
        )

    def _decisao_de_versao(self, identidade) -> Decisao:
        if self.estado != ATIVO:
            return compatibilidade.recusa_por_atualizacao(self.identidade)
        return compatibilidade.decidir(self.identidade, identidade)

    def _para(self, sessao: str, tipo: str, /, **campos) -> list[Envio]:
        """A mensagem para a sessão (pelo id), se ela estiver conectada."""
        conexao = self._sessoes[sessao].conexao
        return [] if conexao is None else [Envio(conexao, protocolo.codificar(tipo, **campos))]

    def _sessao_da_conta(self, conta: str) -> Sessao | None:
        return next((s for s in self._sessoes.values() if s.conta == conta), None)

    # --- autenticação ----------------------------------------------------------------

    def _ao_login(self, conexao: str, mensagem: dict) -> list[Envio]:
        decisao = self._decisao_de_versao(mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        falhas = self._falhas_de_login.get(conexao, 0)
        if falhas >= TENTATIVAS_DE_LOGIN:
            return [
                self._recusa(
                    conexao, "tentativas_esgotadas", "Tentativas de login esgotadas nesta conexão."
                )
            ]
        try:
            credencial = self.autenticador.entrar(mensagem["usuario"], mensagem["senha"])
        except CredenciaisInvalidasError:
            self._falhas_de_login[conexao] = falhas + 1
            return [self._recusa(conexao, "credenciais_invalidas", "Usuário ou senha incorretos.")]
        self._falhas_de_login.pop(conexao, None)
        return [
            Envio(
                conexao,
                protocolo.codificar(
                    "autenticado",
                    conta=credencial.conta.id,
                    usuario=credencial.conta.usuario,
                    token=credencial.token,
                    expira_em=credencial.expira_em,
                ),
            )
        ]

    def _validar_token(self, conexao: str, token: str):
        """A conta e a expiração do token, ou a recusa pronta."""
        try:
            conta, expira = self.autenticador.validar(token)
        except TokenInvalidoError as erro:
            return None, [
                self._recusa(conexao, "token_invalido", f"Autenticação recusada ({erro.motivo}).")
            ]
        return (conta, expira), []

    def _ao_ola(self, conexao: str, mensagem: dict) -> list[Envio]:
        if conexao in self._por_conexao:
            return [self._recusa(conexao, "sessao_existente", "Esta conexão já tem sessão.")]
        decisao = self._decisao_de_versao(mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        lido, recusa = self._validar_token(conexao, mensagem["token"])
        if lido is None:
            return recusa
        conta, expira = lido
        anterior = self._sessao_da_conta(conta.id)
        if anterior is not None:
            if anterior.conexao is not None:
                return [
                    self._recusa(
                        conexao,
                        "conta_ja_conectada",
                        "Esta conta já está conectada em outro lugar.",
                    )
                ]
            if anterior.partida is not None:
                return [
                    self._recusa(
                        conexao,
                        "use_reconectar",
                        "Esta conta tem uma partida em andamento: use a reconexão da sessão.",
                    )
                ]
            self._liberar_espera(anterior)
            del self._sessoes[anterior.id]
        sessao = Sessao(
            id=self._novas_sessoes(),
            conta=conta.id,
            usuario=conta.usuario,
            identidade=Identidade.de_dict(mensagem["identidade"]),
            conexao=conexao,
            expira_em=expira,
        )
        self._sessoes[sessao.id] = sessao
        self._por_conexao[conexao] = sessao.id
        return self._boas_vindas(sessao)

    def _boas_vindas(self, sessao: Sessao) -> list[Envio]:
        return self._para(
            sessao.id,
            "bem_vindo",
            sessao=sessao.id,
            conta=sessao.conta,
            usuario=sessao.usuario,
            versao=self.identidade.jogo,
            expira_em=sessao.expira_em,
            gladiadores=[f.como_dict() for f in self.gladiadores.de(sessao.conta)],
        )

    # --- compromissos: fila e sala ----------------------------------------------------

    def _compromisso(self, conexao: str, mensagem: dict):
        """As conferências antes de qualquer espera: sessão, versão, token, posse, validade."""
        sessao_id = self._por_conexao.get(conexao)
        sessao = self._sessoes.get(sessao_id) if sessao_id else None
        if sessao is None:
            return None, [self._recusa(conexao, "sem_sessao", "Autentique-se antes.")]
        decisao = self._decisao_de_versao(mensagem["identidade"])
        if not decisao.aceita:
            return None, [self._recusa_de(conexao, decisao)]
        if self._relogio() >= sessao.expira_em:
            return None, [
                self._recusa(conexao, "token_expirado", "A autenticação expirou: entre de novo.")
            ]
        if not sessao.livre:
            return None, [
                self._recusa(
                    conexao, "ja_ocupado", "Esta sessão já está na fila, numa sala ou em partida."
                )
            ]
        gladiador = mensagem["gladiador"]
        if self.gladiadores.dono_de(gladiador) != sessao.conta:
            # Mesmo motivo para gladiador alheio e inexistente: não se descobre
            # o acervo dos outros perguntando.
            return None, [
                self._recusa(conexao, "gladiador_alheio", "Este gladiador não é da sua conta.")
            ]
        try:
            self.gladiadores.preparar(gladiador)
        except GladiadorIncompativelError as erro:
            return None, [
                self._recusa(
                    conexao,
                    "gladiador_incompativel",
                    "O gladiador não pode entrar em partida nesta versão.",
                    problemas=erro.problemas,
                )
            ]
        return sessao, []

    def _ao_entrar_na_fila(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao, recusa = self._compromisso(conexao, mensagem)
        if sessao is None:
            return recusa
        sessao.gladiador = mensagem["gladiador"]
        sessao.na_fila = True
        self._fila.append(sessao.id)
        envios = self._para(sessao.id, "na_fila", gladiador=sessao.gladiador)
        return envios + self._parear()

    def _ao_sair_da_fila(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self.sessao_da_conexao(conexao)
        if sessao is not None and sessao.na_fila:
            self._liberar_espera(sessao)
        return []

    def _parear(self) -> list[Envio]:
        """A fila simples: junta as duas primeiras sessões de contas diferentes."""
        envios: list[Envio] = []
        while len(self._fila) >= 2:
            a, b = self._fila[0], self._fila[1]
            for sessao_id in (a, b):
                self._fila.remove(sessao_id)
                self._sessoes[sessao_id].na_fila = False
            envios += self._criar_partida(a, b)
        return envios

    def _ao_criar_sala(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao, recusa = self._compromisso(conexao, mensagem)
        if sessao is None:
            return recusa
        codigo = self._codigos()
        while codigo in self._salas:
            codigo = self._codigos()
        sessao.gladiador = mensagem["gladiador"]
        sessao.sala = codigo
        self._salas[codigo] = sessao.id
        return self._para(sessao.id, "sala_criada", sala=codigo, gladiador=sessao.gladiador)

    def _ao_entrar_na_sala(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao, recusa = self._compromisso(conexao, mensagem)
        if sessao is None:
            return recusa
        anfitriao_id = self._salas.get(str(mensagem["sala"]).strip().upper())
        if anfitriao_id is None:
            return [self._recusa(conexao, "sala_desconhecida", "Não existe sala com esse código.")]
        anfitriao = self._sessoes[anfitriao_id]
        if anfitriao.conta == sessao.conta:
            return [
                self._recusa(
                    conexao, "mesma_conta", "Uma conta não joga os dois lados da mesma partida."
                )
            ]
        sessao.gladiador = mensagem["gladiador"]
        return self._criar_partida(anfitriao.id, sessao.id, sala=anfitriao.sala)

    def _ao_cancelar_sala(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self.sessao_da_conexao(conexao)
        if sessao is not None and sessao.sala is not None:
            self._liberar_espera(sessao)
        return []

    # --- a partida ----------------------------------------------------------------------

    def _criar_partida(
        self, sessao_a: str, sessao_b: str, *, sala: str | None = None
    ) -> list[Envio]:
        """A partida só nasce depois de conferir, de novo, versão, posse e gladiador dos dois.

        `sala`: a partida vem de uma sala direta (`sessao_a` é o anfitrião); sem
        ela, as duas sessões vieram da fila.
        """
        a, b = self._sessoes[sessao_a], self._sessoes[sessao_b]
        recusas: dict[str, Envio | None] = {}
        if a.conta == b.conta:
            recusas[b.id] = self._recusa_para(
                b, "mesma_conta", "Uma conta não joga os dois lados da mesma partida."
            )
        preparados = {}
        for sessao in (a, b):
            if sessao.id in recusas:
                continue
            decisao = self._decisao_de_versao(sessao.identidade)
            if not decisao.aceita:
                recusas[sessao.id] = (
                    self._recusa_de(sessao.conexao, decisao) if sessao.conexao else None
                )
            elif self.gladiadores.dono_de(sessao.gladiador) != sessao.conta:
                recusas[sessao.id] = self._recusa_para(
                    sessao, "gladiador_alheio", "Este gladiador não é da sua conta."
                )
            else:
                try:
                    preparados[sessao.id] = self.gladiadores.preparar(sessao.gladiador)
                except GladiadorIncompativelError as erro:
                    recusas[sessao.id] = self._recusa_para(
                        sessao,
                        "gladiador_incompativel",
                        "O gladiador não pode entrar em partida nesta versão.",
                        erro.problemas,
                    )
        if recusas:
            return self._sem_partida(a, b, recusas, sala)

        if sala is not None:
            self._salas.pop(sala, None)
            a.sala = None
        semente = self._sementes()
        (g1, imp1), (g2, imp2) = preparados[a.id], preparados[b.id]
        partida = Partida(
            id=self._ids(),
            impressao=self.impressao,
            semente=semente,
            lados={
                "p1": LadoDaPartida(a.conta, a.usuario, a.id, a.gladiador, imp1),
                "p2": LadoDaPartida(b.conta, b.usuario, b.id, b.gladiador, imp2),
            },
            duelo=Duel(g1, g2, rng=random.Random(semente)),
        )
        self._partidas[partida.id] = partida
        a.partida = b.partida = partida.id
        envios: list[Envio] = []
        for lado in SIDES:
            envios += self._anuncio(partida, lado)
        return envios + self._observacoes(partida)

    def _recusa_para(
        self, sessao: Sessao, motivo: str, texto: str, problemas: tuple[str, ...] = ()
    ) -> Envio | None:
        if sessao.conexao is None:
            return None
        return self._recusa(sessao.conexao, motivo, texto, problemas=problemas)

    def _sem_partida(
        self, a: Sessao, b: Sessao, recusas: dict[str, Envio | None], sala: str | None
    ) -> list[Envio]:
        """A partida não nasceu: avisa os recusados e devolve os outros à espera."""
        envios = [e for e in recusas.values() if e is not None]
        for sessao in (a, b):
            if sessao.id in recusas:
                self._liberar_espera(sessao)
        if sala is None:
            # Da fila: quem passou nas conferências volta para a frente dela.
            for sessao in (b, a):
                if sessao.id not in recusas:
                    sessao.na_fila = True
                    self._fila.insert(0, sessao.id)
            return envios
        # Da sala: se o problema foi do convidado, a sala continua aberta; se foi
        # do anfitrião, ela fecha, e o convidado fica sabendo.
        if b.id not in recusas:
            b.gladiador = None
            aviso = self._recusa_para(
                b, "sala_indisponivel", "A sala fechou: o anfitrião não pode jogar agora."
            )
            envios += [aviso] if aviso else []
        return envios

    def _anuncio(self, partida: Partida, lado: str) -> list[Envio]:
        outro_lado = "p2" if lado == "p1" else "p1"
        rival = partida.lados[outro_lado]

        def ficha(de: str) -> dict:
            # O apelido publicado na origem só identifica; o duelo usa o personagem.
            apelido = self.gladiadores.ficha(partida.lados[de].gladiador).apelido
            return {"apelido": apelido, **protocolo.ficha_publica(partida.duelo.hero(de))}

        return self._para(
            partida.lados[lado].sessao,
            "partida_criada",
            partida=partida.id,
            lado=lado,
            voce=ficha(lado),
            adversario={"usuario": rival.usuario, **ficha(outro_lado)},
        )

    def _observacoes(self, partida: Partida, lados=SIDES) -> list[Envio]:
        envios: list[Envio] = []
        for lado in lados:
            envios += self._para(
                partida.lados[lado].sessao,
                "observacao",
                partida=partida.id,
                visao=protocolo.visao_para_dict(partida.duelo.view(lado)),
            )
        return envios

    def _ao_acao(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self.sessao_da_conexao(conexao)
        partida = self._partidas.get(mensagem["partida"])
        if sessao is None or partida is None or sessao.partida != partida.id:
            return [
                self._recusa(conexao, "partida_desconhecida", "Esta sessão não joga essa partida.")
            ]

        def recusar(motivo: str, texto: str) -> list[Envio]:
            return self._para(
                sessao.id, "acao_recusada", partida=partida.id, motivo=motivo, mensagem=texto
            )

        if partida.estado != EM_ANDAMENTO:
            return recusar("partida_encerrada", "A partida não está em andamento.")
        lado = partida.lado_da_sessao(sessao.id)
        if mensagem["rodada"] != partida.duelo.round_number:
            return recusar("rodada_errada", f"A rodada em jogo é a {partida.duelo.round_number}.")
        if lado in partida.pendentes:
            return recusar("acao_ja_enviada", "A ação desta rodada já foi recebida.")
        acao = protocolo.acao_de(mensagem["acao"])
        if acao not in partida.duelo.legal_actions(lado):
            return recusar("acao_ilegal", "Ação ilegal neste momento; nada mudou.")
        partida.pendentes[lado] = acao
        # Só quem agiu fica sabendo: o adversário não vê nem que houve escolha.
        envios = self._para(
            sessao.id, "acao_recebida", partida=partida.id, rodada=mensagem["rodada"]
        )
        if len(partida.pendentes) == len(SIDES):
            envios += self._resolver(partida)
        return envios

    def _resolver(self, partida: Partida) -> list[Envio]:
        acoes = dict(partida.pendentes)
        partida.pendentes.clear()
        registro = partida.duelo.play_round(acoes)
        partida.rodadas.append(
            {
                "acoes": {lado: protocolo.acao_para_dict(acoes[lado]) for lado in SIDES},
                "hp_fim": dict(registro.hp_end),
                "mp_fim": dict(registro.mp_end),
            }
        )
        publico = protocolo.rodada_publica(registro)
        envios: list[Envio] = []
        for lado in SIDES:
            envios += self._para(
                partida.lados[lado].sessao, "rodada", partida=partida.id, rodada=publico
            )
        if partida.duelo.finished:
            return envios + self._concluir(partida)
        return envios + self._observacoes(partida)

    def _concluir(self, partida: Partida) -> list[Envio]:
        resultado = partida.duelo.result
        desfecho = Desfecho(
            partida=partida.id,
            impressao=partida.impressao,
            estado=CONCLUIDA,
            vencedor=partida.lados[resultado.winner].conta,
            perdedor=partida.lados[resultado.loser].conta,
            motivo=resultado.reason,
            rodadas=resultado.rounds,
        )
        return self._encerrar(partida, desfecho, vencedor=resultado.winner)

    def _encerrar(self, partida: Partida, desfecho: Desfecho, vencedor: str | None) -> list[Envio]:
        self.resultados.registrar(desfecho)
        partida.estado = desfecho.estado
        partida.desfecho = desfecho
        envios: list[Envio] = []
        for dados in partida.lados.values():
            envios += self._para(
                dados.sessao,
                "fim",
                partida=partida.id,
                estado=desfecho.estado,
                vencedor=vencedor,
                motivo=desfecho.motivo,
                rodadas=desfecho.rodadas,
            )
            sessao = self._sessoes.get(dados.sessao)
            if sessao is not None:
                sessao.partida = None
                sessao.gladiador = None
        return envios

    def _ao_reconectar(self, conexao: str, mensagem: dict) -> list[Envio]:
        decisao = compatibilidade.decidir(self.identidade, mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        lido, recusa = self._validar_token(conexao, mensagem["token"])
        if lido is None:
            return recusa
        conta, expira = lido
        sessao = self._sessoes.get(mensagem["sessao"])
        if sessao is None or sessao.conta != conta.id:
            # Sessão alheia e inexistente dão a mesma resposta.
            return [
                self._recusa(conexao, "sessao_desconhecida", "Sessão desconhecida nesta instância.")
            ]
        if self.estado != ATIVO and sessao.partida is None:
            return [
                self._recusa_de(conexao, compatibilidade.recusa_por_atualizacao(self.identidade))
            ]
        if sessao.conexao is not None:
            self._por_conexao.pop(sessao.conexao, None)
        sessao.conexao = conexao
        sessao.expira_em = expira
        sessao.identidade = Identidade.de_dict(mensagem["identidade"])
        self._por_conexao[conexao] = sessao.id
        envios = self._boas_vindas(sessao)
        partida = self._partidas.get(sessao.partida) if sessao.partida else None
        if partida is not None and partida.estado == EM_ANDAMENTO:
            lado = partida.lado_da_sessao(sessao.id)
            envios += self._anuncio(partida, lado)
            if lado not in partida.pendentes:
                envios += self._observacoes(partida, (lado,))
        return envios

    # --- atualização ----------------------------------------------------------------

    def drenar(self) -> list[Envio]:
        """Nada novo começa nesta versão; as partidas em andamento seguem até o fim."""
        if self.estado == ATIVO:
            self.estado = DRENANDO
        envios: list[Envio] = []
        recusa = compatibilidade.recusa_por_atualizacao(self.identidade)
        for sessao in self._sessoes.values():
            if sessao.na_fila or sessao.sala is not None:
                self._liberar_espera(sessao)
                if sessao.conexao:
                    envios.append(self._recusa_de(sessao.conexao, recusa))
        return envios

    def retomar(self, registro: dict) -> list[Envio]:
        """Continua aqui uma partida exportada por outra instância DA MESMA VERSÃO.

        Rejoga as rodadas registradas e confere cada uma; qualquer diferença
        (versão, gladiador, estado) levanta `PartidaIncompativelError` e nada fica
        registrado aqui. Os jogadores voltam por `reconectar`, com a sessão e um
        token válido da mesma conta.
        """
        if self.estado == DESLIGADO:
            raise PartidaIncompativelError("Esta instância está desligada.")
        if registro.get("estado") != EM_ANDAMENTO:
            raise PartidaIncompativelError("Só se retoma partida em andamento.")
        if registro.get("partida") in self._partidas:
            raise PartidaIncompativelError("A partida já existe nesta instância.")
        duelo = reproduzir(registro, self.gladiadores, self.impressao)
        if duelo.finished:
            raise PartidaIncompativelError("O registro diz em andamento, mas o replay terminou.")
        lados = {
            lado: LadoDaPartida(
                d["conta"], d["usuario"], d["sessao"], d["gladiador"], d["impressao_do_gladiador"]
            )
            for lado, d in registro["lados"].items()
        }
        partida = Partida(
            id=registro["partida"],
            impressao=registro["impressao"],
            semente=registro["semente"],
            lados=lados,
            duelo=duelo,
            rodadas=[dict(r) for r in registro["rodadas"]],
        )
        self._partidas[partida.id] = partida
        for dados in lados.values():
            self._sessoes[dados.sessao] = Sessao(
                id=dados.sessao,
                conta=dados.conta,
                usuario=dados.usuario,
                identidade=self.identidade,
                conexao=None,
                gladiador=dados.gladiador,
                partida=partida.id,
            )
        return []

    def transferir(self, partida_id: str) -> list[Envio]:
        """A partida continua em outra instância: esta a solta e avisa os jogadores."""
        partida = self._partidas[partida_id]
        partida.estado = TRANSFERIDA
        envios: list[Envio] = []
        for dados in partida.lados.values():
            envios += self._para(
                dados.sessao,
                "fim",
                partida=partida.id,
                estado=TRANSFERIDA,
                vencedor=None,
                motivo="reconectar",
                rodadas=len(partida.rodadas),
            )
            sessao = self._sessoes.get(dados.sessao)
            if sessao is not None:
                sessao.partida = None
        return envios

    def anular(self, partida_id: str, motivo: str) -> list[Envio]:
        """Encerramento seguro: sem vencedor, sem derrota, fora da classificação."""
        partida = self._partidas[partida_id]
        if partida.estado != EM_ANDAMENTO:
            raise ValueError(f"A partida {partida_id} não está em andamento.")
        desfecho = Desfecho(
            partida=partida.id,
            impressao=partida.impressao,
            estado=ANULADA,
            vencedor=None,
            perdedor=None,
            motivo=motivo,
            rodadas=len(partida.rodadas),
        )
        partida.pendentes.clear()
        return self._encerrar(partida, desfecho, vencedor=None)

    def desligar(self) -> None:
        if self.partidas_em_andamento():
            raise RuntimeError(
                "Há partidas em andamento: transfira ou anule antes (`Frota.desligar`)."
            )
        self.estado = DESLIGADO
        for sessao in self._sessoes.values():
            self._liberar_espera(sessao)


class Frota:
    """As instâncias no ar durante uma atualização.

    `publicar(nova)` drena as antigas; `desligar(antiga)` passa cada partida em
    andamento para uma instância da MESMA versão, e anula a que não tiver para
    onde ir. Uma partida nunca muda de versão.
    """

    def __init__(self, *instancias: ServidorAutoritativo) -> None:
        self.instancias = list(instancias)

    def atual(self) -> ServidorAutoritativo | None:
        """Onde chegam conexões novas: a instância ativa mais recente."""
        return next((i for i in reversed(self.instancias) if i.estado == ATIVO), None)

    def publicar(self, nova: ServidorAutoritativo) -> list[Envio]:
        envios: list[Envio] = []
        for instancia in self.instancias:
            if instancia.estado == ATIVO:
                envios += instancia.drenar()
        self.instancias.append(nova)
        return envios

    def desligar(self, instancia: ServidorAutoritativo) -> list[Envio]:
        envios: list[Envio] = []
        compativeis = [
            o
            for o in self.instancias
            if o is not instancia and o.estado != DESLIGADO and o.impressao == instancia.impressao
        ]
        for partida_id in instancia.partidas_em_andamento():
            registro = instancia.exportar(partida_id)
            for destino in compativeis:
                try:
                    envios += destino.retomar(registro)
                except PartidaIncompativelError:
                    continue
                envios += instancia.transferir(partida_id)
                break
            else:
                envios += instancia.anular(partida_id, "sem_instancia_compativel")
        instancia.desligar()
        return envios

    def recolher(self) -> list[ServidorAutoritativo]:
        """Desliga as instâncias drenadas que já não têm partida. Devolve as desligadas."""
        ociosas = [
            i for i in self.instancias if i.estado == DRENANDO and not i.partidas_em_andamento()
        ]
        for instancia in ociosas:
            instancia.desligar()
        return ociosas
