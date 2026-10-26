"""O servidor autoritativo da Arena multiplayer.

O cliente manda texto; o servidor decide tudo. Uma instância:

- só aceita quem tem a MESMA identidade de versão que ela, e confere de novo na
  entrada da fila, na criação da partida e na reconexão;
- guarda os gladiadores (`AcervoDeGladiadores`): o cliente só nomeia o id, e a
  validação estrita roda a cada preparação;
- valida a ação contra `Duel.legal_actions` e roda o motor canônico
  (`Duel.play_round`); o cliente nunca informa HP, dano, atributo, equipamento,
  recarga, resultado nem MMR — o protocolo não tem onde;
- prende cada partida à impressão da versão em que ela nasceu.

Atualização:

- `drenar()`: a instância para de aceitar sessão, fila e partida novas, e deixa
  as partidas em andamento terminarem;
- `retomar(registro)`: uma instância da MESMA versão continua uma partida
  exportada, rejogando as ações registradas e conferindo HP e MP de cada rodada
  — o motor é determinístico pela semente;
- `anular(...)`: quando nenhuma instância compatível pode continuar, a partida
  termina sem vencedor, sem derrota e fora da classificação.

O servidor não conhece rede, relógio nem fila por tempo: recebe `(conexão,
texto)` e devolve os `Envio`s. Quem transporta é a camada de cima
(`transporte.RedeLocal` nos testes e no modo local).
"""

from __future__ import annotations

import random
import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from src.mechanics.pvp_duel import SIDES, Duel, DuelAction, InvalidDuelActionError
from src.multiplayer import compatibilidade, protocolo
from src.multiplayer.compatibilidade import Decisao
from src.multiplayer.gladiadores import AcervoDeGladiadores, GladiadorIncompativelError
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
FORMATO_DO_REGISTRO = 1


@dataclass(frozen=True)
class Envio:
    """Um texto para uma conexão. Transportar é com a camada de cima."""

    conexao: str
    texto: str


class PartidaIncompativelError(RuntimeError):
    """Esta instância não pode continuar a partida: outra versão, outro gladiador
    ou um replay que não reproduz o registrado."""


@dataclass(frozen=True)
class Desfecho:
    """Como uma partida terminou. `anulada` não tem vencedor nem perdedor."""

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

    def vitorias(self, jogador: str) -> int:
        return sum(1 for d in self.classificaveis() if d.vencedor == jogador)

    def derrotas(self, jogador: str) -> int:
        return sum(1 for d in self.classificaveis() if d.perdedor == jogador)


@dataclass
class Sessao:
    token: str
    jogador: str
    identidade: Identidade
    conexao: str | None
    gladiador: str | None = None
    partida: str | None = None


@dataclass(frozen=True)
class LadoDaPartida:
    jogador: str
    token: str
    gladiador: str
    impressao_do_gladiador: str


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

    def lado_do_token(self, token: str) -> str | None:
        return next((lado for lado, dados in self.lados.items() if dados.token == token), None)

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
                    "jogador": dados.jogador,
                    "token": dados.token,
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


def reproduzir(registro: dict, acervo: AcervoDeGladiadores, impressao: str) -> Duel:
    """Rejoga uma partida registrada no motor canônico, conferindo cada rodada.

    Só roda na versão em que a partida nasceu: registro de outra versão é
    recusado, nunca rejogado com regras divergentes. O gladiador de cada lado
    tem de ser o MESMO registro (pela impressão), e HP e MP ao fim de cada rodada
    têm de bater com o registrado.
    """
    if not isinstance(registro, dict) or registro.get("formato") != FORMATO_DO_REGISTRO:
        raise PartidaIncompativelError("Registro de partida em formato desconhecido.")
    if registro.get("impressao") != impressao:
        raise PartidaIncompativelError(
            "A partida pertence a outra versão do jogo: não roda com regras divergentes."
        )
    gladiadores = []
    for lado in SIDES:
        dados = registro["lados"][lado]
        try:
            gladiador, impressao_do_registro = acervo.preparar(dados["gladiador"])
        except GladiadorIncompativelError as erro:
            raise PartidaIncompativelError(f"Gladiador do lado {lado}: {erro}") from erro
        if impressao_do_registro != dados["impressao_do_gladiador"]:
            raise PartidaIncompativelError(
                f"O gladiador do lado {lado} não é o registro da partida."
            )
        gladiadores.append(gladiador)
    duelo = Duel(*gladiadores, rng=random.Random(registro["semente"]))
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
    """Uma instância do servidor, presa a UM manifesto."""

    def __init__(
        self,
        manifesto: Manifesto,
        acervo: AcervoDeGladiadores,
        resultados: Resultados | None = None,
        *,
        sementes: Callable[[], int] | None = None,
        tokens: Callable[[], str] | None = None,
        ids: Callable[[], str] | None = None,
    ) -> None:
        self.manifesto = manifesto
        self.acervo = acervo
        self.resultados = resultados if resultados is not None else Resultados()
        self.estado = ATIVO
        self._sementes = sementes or (lambda: secrets.randbits(63))
        self._tokens = tokens or (lambda: secrets.token_hex(16))
        self._ids = ids or (lambda: secrets.token_hex(8))
        self._sessoes: dict[str, Sessao] = {}
        self._por_conexao: dict[str, str] = {}
        self._fila: list[str] = []
        self._partidas: dict[str, Partida] = {}

    @classmethod
    def da_instalacao(
        cls,
        acervo: AcervoDeGladiadores,
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
        return cls(manifesto_da_instalacao(raiz, pasta), acervo, resultados, **opcoes)

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
        return tuple(self._sessoes[t].jogador for t in self._fila)

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
            "ola": self._ao_ola,
            "entrar_na_fila": self._ao_entrar_na_fila,
            "sair_da_fila": self._ao_sair_da_fila,
            "acao": self._ao_acao,
            "reconectar": self._ao_reconectar,
        }[mensagem["tipo"]]
        return tratar(conexao, mensagem)

    def desconectar(self, conexao: str) -> None:
        """A conexão caiu. A sessão fica, para reconectar; a fila a esquece.

        Prazo de reconexão e derrota por desconexão (`Duel.forfeit`) dependem do
        relógio, que ainda não existe.
        """
        token = self._por_conexao.pop(conexao, None)
        if token is None:
            return
        self._sessoes[token].conexao = None
        if token in self._fila:
            self._fila.remove(token)

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

    def _sessao_da(self, conexao: str) -> Sessao | None:
        token = self._por_conexao.get(conexao)
        return self._sessoes.get(token) if token else None

    def _para(self, sessao: str, tipo: str, /, **campos) -> list[Envio]:
        """A mensagem para a sessão (pelo token), se ela estiver conectada."""
        conexao = self._sessoes[sessao].conexao
        return [] if conexao is None else [Envio(conexao, protocolo.codificar(tipo, **campos))]

    def _ao_ola(self, conexao: str, mensagem: dict) -> list[Envio]:
        if conexao in self._por_conexao:
            return [self._recusa(conexao, "sessao_existente", "Esta conexão já tem sessão.")]
        decisao = self._decisao_de_versao(mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        token = self._tokens()
        self._sessoes[token] = Sessao(
            token, mensagem["jogador"], Identidade.de_dict(mensagem["identidade"]), conexao
        )
        self._por_conexao[conexao] = token
        return self._para(token, "bem_vindo", token=token, versao=self.identidade.jogo)

    def _ao_entrar_na_fila(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self._sessao_da(conexao)
        if sessao is None:
            return [self._recusa(conexao, "sem_sessao", "Conecte-se antes de entrar na fila.")]
        decisao = self._decisao_de_versao(mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        if sessao.partida is not None or sessao.token in self._fila:
            return [
                self._recusa(conexao, "ja_ocupado", "Esta sessão já está na fila ou em partida.")
            ]
        try:
            self.acervo.preparar(mensagem["gladiador"])
        except GladiadorIncompativelError as erro:
            return [
                self._recusa(
                    conexao,
                    "gladiador_incompativel",
                    "O gladiador não pode entrar em partida nesta versão.",
                    problemas=erro.problemas,
                )
            ]
        sessao.gladiador = mensagem["gladiador"]
        self._fila.append(sessao.token)
        envios = self._para(sessao.token, "na_fila", gladiador=sessao.gladiador)
        return envios + self._parear()

    def _ao_sair_da_fila(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self._sessao_da(conexao)
        if sessao is not None and sessao.token in self._fila:
            self._fila.remove(sessao.token)
        return []

    def _parear(self) -> list[Envio]:
        envios: list[Envio] = []
        while len(self._fila) >= 2:
            a, b = self._fila.pop(0), self._fila.pop(0)
            envios += self._criar_partida(a, b)
        return envios

    def _criar_partida(self, token_a: str, token_b: str) -> list[Envio]:
        """A partida só nasce depois de conferir, de novo, versão e gladiador dos dois."""
        envios: list[Envio] = []
        preparados = {}
        recusados = []
        for token in (token_a, token_b):
            sessao = self._sessoes[token]
            decisao = self._decisao_de_versao(sessao.identidade)
            if not decisao.aceita:
                recusados.append(token)
                if sessao.conexao:
                    envios.append(self._recusa_de(sessao.conexao, decisao))
                continue
            try:
                preparados[token] = self.acervo.preparar(sessao.gladiador)
            except GladiadorIncompativelError as erro:
                recusados.append(token)
                sessao.gladiador = None
                if sessao.conexao:
                    envios.append(
                        self._recusa(
                            sessao.conexao,
                            "gladiador_incompativel",
                            "O gladiador não pode entrar em partida nesta versão.",
                            problemas=erro.problemas,
                        )
                    )
        if recusados:
            # Quem passou nas conferências volta para a frente da fila.
            self._fila[:0] = [t for t in (token_a, token_b) if t not in recusados]
            return envios

        semente = self._sementes()
        (g1, imp1), (g2, imp2) = preparados[token_a], preparados[token_b]
        partida = Partida(
            id=self._ids(),
            impressao=self.impressao,
            semente=semente,
            lados={
                "p1": LadoDaPartida(
                    self._sessoes[token_a].jogador, token_a, self._sessoes[token_a].gladiador, imp1
                ),
                "p2": LadoDaPartida(
                    self._sessoes[token_b].jogador, token_b, self._sessoes[token_b].gladiador, imp2
                ),
            },
            duelo=Duel(g1, g2, rng=random.Random(semente)),
        )
        self._partidas[partida.id] = partida
        for dados in partida.lados.values():
            self._sessoes[dados.token].partida = partida.id
        for lado in SIDES:
            envios += self._anuncio(partida, lado)
        return envios + self._observacoes(partida)

    def _anuncio(self, partida: Partida, lado: str) -> list[Envio]:
        outro = partida.duelo.view(lado).opponent
        rival = partida.lados["p2" if lado == "p1" else "p1"]
        return self._para(
            partida.lados[lado].token,
            "partida_criada",
            partida=partida.id,
            lado=lado,
            adversario={
                "jogador": rival.jogador,
                "gladiador": outro.name,
                "classe": outro.class_name,
                "nivel": outro.level,
            },
        )

    def _observacoes(self, partida: Partida, lados=SIDES) -> list[Envio]:
        envios: list[Envio] = []
        for lado in lados:
            envios += self._para(
                partida.lados[lado].token,
                "observacao",
                partida=partida.id,
                visao=protocolo.visao_para_dict(partida.duelo.view(lado)),
            )
        return envios

    def _ao_acao(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self._sessao_da(conexao)
        partida = self._partidas.get(mensagem["partida"])
        if sessao is None or partida is None or sessao.partida != partida.id:
            return [
                self._recusa(conexao, "partida_desconhecida", "Esta sessão não joga essa partida.")
            ]

        def recusar(motivo: str, texto: str) -> list[Envio]:
            return self._para(
                sessao.token, "acao_recusada", partida=partida.id, motivo=motivo, mensagem=texto
            )

        if partida.estado != EM_ANDAMENTO:
            return recusar("partida_encerrada", "A partida não está em andamento.")
        lado = partida.lado_do_token(sessao.token)
        if mensagem["rodada"] != partida.duelo.round_number:
            return recusar("rodada_errada", f"A rodada em jogo é a {partida.duelo.round_number}.")
        if lado in partida.pendentes:
            return recusar("acao_ja_enviada", "A ação desta rodada já foi recebida.")
        acao = protocolo.acao_de(mensagem["acao"])
        if acao not in partida.duelo.legal_actions(lado):
            return recusar("acao_ilegal", "Ação ilegal neste momento; nada mudou.")
        partida.pendentes[lado] = acao
        envios = self._para(
            sessao.token, "acao_recebida", partida=partida.id, rodada=mensagem["rodada"]
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
                partida.lados[lado].token, "rodada", partida=partida.id, rodada=publico
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
            vencedor=partida.lados[resultado.winner].jogador,
            perdedor=partida.lados[resultado.loser].jogador,
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
                dados.token,
                "fim",
                partida=partida.id,
                estado=desfecho.estado,
                vencedor=vencedor,
                motivo=desfecho.motivo,
                rodadas=desfecho.rodadas,
            )
            sessao = self._sessoes.get(dados.token)
            if sessao is not None:
                sessao.partida = None
                sessao.gladiador = None
        return envios

    def _ao_reconectar(self, conexao: str, mensagem: dict) -> list[Envio]:
        sessao = self._sessoes.get(mensagem["token"])
        if sessao is None:
            return [
                self._recusa(conexao, "sessao_desconhecida", "Sessão desconhecida nesta instância.")
            ]
        decisao = compatibilidade.decidir(self.identidade, mensagem["identidade"])
        if not decisao.aceita:
            return [self._recusa_de(conexao, decisao)]
        if self.estado != ATIVO and sessao.partida is None:
            return [
                self._recusa_de(conexao, compatibilidade.recusa_por_atualizacao(self.identidade))
            ]
        if sessao.conexao is not None:
            self._por_conexao.pop(sessao.conexao, None)
        sessao.conexao = conexao
        sessao.identidade = Identidade.de_dict(mensagem["identidade"])
        self._por_conexao[conexao] = sessao.token
        envios = self._para(
            sessao.token, "bem_vindo", token=sessao.token, versao=self.identidade.jogo
        )
        partida = self._partidas.get(sessao.partida) if sessao.partida else None
        if partida is not None and partida.estado == EM_ANDAMENTO:
            lado = partida.lado_do_token(sessao.token)
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
        for token in self._fila:
            sessao = self._sessoes[token]
            sessao.gladiador = None
            if sessao.conexao:
                envios.append(self._recusa_de(sessao.conexao, recusa))
        self._fila.clear()
        return envios

    def retomar(self, registro: dict) -> list[Envio]:
        """Continua aqui uma partida exportada por outra instância DA MESMA VERSÃO.

        Rejoga as rodadas registradas e confere cada uma; qualquer diferença
        (versão, gladiador, estado) levanta `PartidaIncompativelError` e nada fica
        registrado aqui. Os jogadores voltam por `reconectar`, com o token.
        """
        if self.estado == DESLIGADO:
            raise PartidaIncompativelError("Esta instância está desligada.")
        if registro.get("estado") != EM_ANDAMENTO:
            raise PartidaIncompativelError("Só se retoma partida em andamento.")
        if registro.get("partida") in self._partidas:
            raise PartidaIncompativelError("A partida já existe nesta instância.")
        duelo = reproduzir(registro, self.acervo, self.impressao)
        if duelo.finished:
            raise PartidaIncompativelError("O registro diz em andamento, mas o replay terminou.")
        lados = {
            lado: LadoDaPartida(
                d["jogador"], d["token"], d["gladiador"], d["impressao_do_gladiador"]
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
            self._sessoes[dados.token] = Sessao(
                dados.token,
                dados.jogador,
                self.identidade,
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
                dados.token,
                "fim",
                partida=partida.id,
                estado=TRANSFERIDA,
                vencedor=None,
                motivo="reconectar",
                rodadas=len(partida.rodadas),
            )
            sessao = self._sessoes.get(dados.token)
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
        self._fila.clear()


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
