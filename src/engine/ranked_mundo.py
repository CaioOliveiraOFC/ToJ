"""A Ranked offline em jogo: a Ladder local, o matchmaking do jogador e o mundo NPC × NPC.

O estado competitivo é um arquivo só, `saves/ranked.json`, ao lado dos saves:
a Ladder (todos os NPCs e os gladiadores do jogador), as reservas de
adversário, a semente e o relógio do mundo. Na primeira vez, ele nasce da
calibração publicada (`src/data/arena_ranked/ladder_inicial.json`).

- **Identidade.** O NPC é o id da população; o gladiador do jogador é
  `identidade_do_gladiador` (o slot e o save sem equipamento e mochila). Trocar
  equipamento não muda a identidade; uma run nova no mesmo slot é outro
  gladiador e começa do zero — não herda nada.
- **Catálogo novo.** Gladiador que entra na população ganha registro com a
  priori fraca do OP; nenhum registro existente é apagado ou reiniciado.
- **Sem escolha de adversário.** O adversário é sorteado pelo matchmaking e
  fica RESERVADO até a partida acontecer: sair e voltar não troca o oponente.
- **O mundo.** Depois de cada partida do jogador, `PARTIDAS_DO_MUNDO_POR_PARTIDA`
  confrontos NPC × NPC entram na fila. Ao voltar depois de um tempo fora, a
  incerteza de todos cresce com os dias (inatividade do sistema, até
  `DIAS_MAXIMOS`) e entram na fila até `FILA_AO_RETORNAR` confrontos — nunca as
  horas inteiras. Quem joga a fila é o `AgendadorDoMundo`, em segundo plano, e
  só enquanto o jogador está nos menus.
- **Reprodutível.** As duplas do mundo saem do gerador semeado por (semente,
  relógio do mundo), e cada confronto da sua própria semente.
- **A leaderboard publicada** (`ranked/leaderboard.py`) sai em ciclos
  (`Leaderboard.periodo`, 1 hora por padrão). Nada roda com o jogo fechado: ao
  abrir, depois de cada partida e em cada volta ao painel, quem conduz chama
  `atualizar_leaderboard(agora)`, e um atraso de muitos ciclos publica UM
  retrato só.
- **Versões do arquivo.** A versão 2 guarda também a progressão visível
  (divisão, PR, candidatura, elite), os empates e a leaderboard publicada. Um
  arquivo da versão 1 (Fase 6) é migrado na leitura: nada é perdido, a
  progressão nasce da FUNDAÇÃO (o retrato inicial: elite pelo percentil, os
  outros na divisão do alvo), e o arquivo antigo fica copiado em
  `ranked.v1.json` antes da primeira gravação. O estado inicial publicado
  (`ladder_inicial.json`) é a calibração da Fase 6 e passa pela mesma migração.
"""

from __future__ import annotations

import hashlib
import json
import os
import queue
import random
import tempfile
import threading
from pathlib import Path

from src.data import loader
from src.engine import ranked_partidas
from src.engine.arena_populacao import Populacao
from src.ranked import leaderboard, matchmaking, sistema
from src.ranked.ladder import ANULADA, DERROTA, EMPATE, VITORIA, Ladder, Registro
from src.ranked.leaderboard import Leaderboard
from src.storage import save_manager

ARQUIVO = "ranked.json"
COPIA_DA_V1 = "ranked.v1.json"
VERSAO = 2
VERSOES_LIDAS = (1, 2)
INICIAL = Path(loader.__file__).resolve().parent / "arena_ranked" / "ladder_inicial.json"

PARTIDAS_DO_MUNDO_POR_PARTIDA = 2
PARTIDAS_DO_MUNDO_POR_HORA = 4
FILA_AO_RETORNAR = 24
FILA_MAXIMA = 60
DIAS_MAXIMOS = 30
SEGUNDOS_POR_DIA = 86_400


class RankedInvalidaError(RuntimeError):
    """O arquivo da Ranked não é legível nem de uma versão conhecida: nada é sobrescrito."""


def migrar_v1(dados: dict) -> dict:
    """O estado da Fase 6 na versão 2, sem perder nada.

    Os registros ganham `empates` (zero) e o desfecho explícito no histórico: a
    partida que bateu o limite técnico na Fase 6 não mudou rating nem contou
    como partida — é exatamente uma partida ANULADA. A progressão visível e a
    leaderboard nascem depois, na fundação (`MundoRanqueado.fundar`).
    """
    novo = json.loads(json.dumps(dados))
    novo["versao"] = VERSAO
    for registro in novo["ladder"]["registros"]:
        registro.setdefault("empates", 0)
        for entrada in registro.get("historico") or []:
            if "resultado" in entrada:
                continue
            if entrada.get("venceu") is None:
                entrada["resultado"] = ANULADA
                entrada.setdefault("motivo", "limite")
            else:
                entrada["resultado"] = VITORIA if entrada["venceu"] else DERROTA
    novo.pop("leaderboard", None)
    return novo


def _gravar(caminho: str, texto: str) -> None:
    """Escrita atômica: arquivo temporário na mesma pasta e `os.replace`."""
    pasta = os.path.dirname(caminho) or "."
    os.makedirs(pasta, exist_ok=True)
    fd, temporario = tempfile.mkstemp(dir=pasta, prefix=".ranked-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        os.replace(temporario, caminho)
    except BaseException:
        Path(temporario).unlink(missing_ok=True)
        raise


class Anulada:
    """Um confronto do mundo que terminou em erro técnico: vira partida anulada."""

    def __init__(self, a: str, b: str, motivo: str) -> None:
        self.a, self.b, self.motivo = a, b, motivo


def _semente(*partes) -> int:
    texto = ":".join(str(p) for p in partes)
    return int.from_bytes(hashlib.sha256(texto.encode()).digest()[:8], "big")


def caminho_padrao() -> str:
    return os.path.join(save_manager.SAVE_DIR, ARQUIVO)


class MundoRanqueado:
    def __init__(
        self,
        ladder: Ladder,
        populacao: Populacao,
        *,
        semente: int,
        relogio: int = 0,
        fila: int = 0,
        ultima_sessao: float | None = None,
        reservas: dict | None = None,
        caminho: str | None = None,
        leaderboard: Leaderboard | None = None,
    ) -> None:
        self.ladder = ladder
        self.leaderboard = leaderboard if leaderboard is not None else Leaderboard()
        self.populacao = populacao
        self.semente = semente
        self.relogio = relogio
        self.fila = fila
        self.ultima_sessao = ultima_sessao
        self.reservas = dict(reservas or {})
        self.caminho = caminho

    # -- carregar e gravar --

    @classmethod
    def carregar(cls, populacao: Populacao, caminho: str | None = None) -> MundoRanqueado:
        caminho = caminho or caminho_padrao()
        existente = os.path.exists(caminho)
        if existente:
            try:
                with open(caminho, encoding="utf-8") as f:
                    texto = f.read()
                dados = json.loads(texto)
            except (OSError, json.JSONDecodeError) as erro:
                raise RankedInvalidaError(f"{caminho}: ilegível ({erro})") from erro
            if not isinstance(dados, dict) or dados.get("versao") not in VERSOES_LIDAS:
                versao = dados.get("versao") if isinstance(dados, dict) else None
                raise RankedInvalidaError(f"{caminho}: versão {versao!r}")
        else:
            try:
                dados = json.loads(INICIAL.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as erro:
                raise RankedInvalidaError(f"estado inicial da Ranked ilegível: {erro}") from erro
            if dados.get("versao") not in VERSOES_LIDAS:
                raise RankedInvalidaError("estado inicial da Ranked de outra versão")
        migrado = dados["versao"] == 1
        if migrado:
            dados = migrar_v1(dados)
        try:
            sis = sistema.criar(dados["algoritmo"], dados["parametros"])
            mundo = cls(
                Ladder.de_dict(sis, dados["ladder"]),
                populacao,
                semente=int(dados["semente"]),
                relogio=int(dados.get("relogio", 0)),
                fila=int(dados.get("fila", 0)),
                ultima_sessao=dados.get("ultima_sessao"),
                reservas=dados.get("reservas"),
                caminho=caminho,
                leaderboard=Leaderboard.de_dict(dados.get("leaderboard")),
            )
        except (KeyError, TypeError, ValueError) as erro:
            raise RankedInvalidaError(f"{caminho}: estado incompleto ({erro})") from erro
        if migrado:
            mundo.fundar()
        mundo.sincronizar_populacao()
        if migrado and existente:
            copia = os.path.join(os.path.dirname(caminho) or ".", COPIA_DA_V1)
            if not os.path.exists(copia):
                _gravar(copia, texto)
            mundo.salvar()
        return mundo

    def fundar(self) -> dict:
        """O retrato inicial: elite pelo percentil, os outros na divisão do alvo."""
        resumo = leaderboard.publicar(
            self.ladder, self.leaderboard, None, numero=None, fundacao=True
        )
        self.leaderboard.ciclo = None
        return resumo

    def sincronizar_populacao(self) -> list[str]:
        """Inscreve quem entrou no catálogo; não apaga nem reinicia ninguém."""
        novos = []
        for o in self.populacao.oponentes():
            if o.id not in self.ladder:
                self.ladder.adicionar(
                    Registro(
                        o.id,
                        o.apelido,
                        o.classe,
                        True,
                        sistema.inicial(self.ladder.sistema, o.op),
                        forca_de_referencia=o.op,
                    )
                )
                novos.append(o.id)
        for identidade in novos:
            self.ladder.posicionar_npc(identidade)
        return novos

    def para_dict(self) -> dict:
        return {
            "versao": VERSAO,
            "algoritmo": sistema.ALGORITMO,
            "parametros": sistema.PARAMETROS,
            "semente": self.semente,
            "relogio": self.relogio,
            "fila": self.fila,
            "ultima_sessao": self.ultima_sessao,
            "reservas": self.reservas,
            "leaderboard": self.leaderboard.para_dict(),
            "ladder": self.ladder.para_dict(),
        }

    def salvar(self) -> None:
        _gravar(self.caminho or caminho_padrao(), json.dumps(self.para_dict(), ensure_ascii=False))

    # -- o gladiador do jogador --

    def inscrever(self, identidade: str, nome: str, classe: str) -> Registro:
        """O registro do gladiador; criado do zero na primeira vez, sem herança."""
        if identidade not in self.ladder:
            self.ladder.adicionar(
                Registro(
                    identidade, nome, classe.lower(), False, sistema.inicial(self.ladder.sistema)
                )
            )
        return self.ladder[identidade]

    def adversario(self, identidade: str) -> str:
        """O adversário da próxima partida: o reservado, ou um novo do matchmaking."""
        reservado = self.reservas.get(identidade)
        if reservado in self.ladder and self.ladder[reservado].npc:
            return reservado
        registro = self.ladder[identidade]
        rng = random.Random(_semente(self.semente, "jogador", identidade, registro.partidas))
        escolha = matchmaking.escolher_oponente(self.ladder, identidade, rng)
        self.reservas[identidade] = escolha.oponente
        self.salvar()
        return escolha.oponente

    def semente_da_partida(self, identidade: str) -> int:
        return _semente(self.semente, "partida", identidade, self.ladder[identidade].partidas)

    def registrar_do_jogador(
        self, identidade: str, oponente: str, resultado, *, motivo: str | None = None
    ):
        """O resultado da partida do jogador, e a fila do mundo cresce.

        `resultado`: `vitoria`, `derrota`, `empate` (com o `motivo`, impasse ou
        teto) ou `anulada` (interrupção ou erro técnico); `True`/`False` valem
        vitória e derrota. A anulada não muda nada além do histórico; a
        interrompida mantém o adversário reservado (a partida volta igual), a
        de erro técnico libera a reserva.
        """
        if isinstance(resultado, bool):
            resultado = VITORIA if resultado else DERROTA
        if resultado == ANULADA:
            self.ladder.registrar_anulada(
                identidade, oponente, origem="ranqueada", motivo=motivo or "interrompida"
            )
            if motivo != "interrompida":
                self.reservas.pop(identidade, None)
            self.salvar()
            return None
        if resultado == EMPATE:
            atualizacao = self.ladder.registrar_empate(
                identidade, oponente, origem="ranqueada", motivo=motivo or "impasse"
            )
        elif resultado in (VITORIA, DERROTA):
            vencedor = identidade if resultado == VITORIA else oponente
            atualizacao = self.ladder.registrar(identidade, oponente, vencedor, origem="ranqueada")
        else:
            raise ValueError(f"resultado desconhecido: {resultado!r}")
        self.reservas.pop(identidade, None)
        self.fila = min(FILA_MAXIMA, self.fila + PARTIDAS_DO_MUNDO_POR_PARTIDA)
        self.salvar()
        return atualizacao

    # -- a leaderboard publicada --

    def atualizar_leaderboard(self, agora: float) -> dict | None:
        """Publica o retrato do ciclo atual, se ele ainda não saiu. No máximo um por chamada.

        Na primeira sessão, só marca o ciclo: o retrato que vale é o da
        fundação. Depois de muitos ciclos sem abrir o jogo, publica UM retrato,
        o do ciclo atual, com o estado gravado — os ciclos perdidos ficam
        registrados como pulados.
        """
        lb = self.leaderboard
        atual = leaderboard.ciclo(agora, lb.periodo, lb.origem)
        if lb.ciclo is None:
            lb.ciclo = atual
            lb.publicada_em = agora if lb.publicada_em is None else lb.publicada_em
            self.salvar()
            return None
        if atual <= lb.ciclo:
            return None
        pulados = atual - lb.ciclo - 1
        resumo = leaderboard.publicar(self.ladder, lb, agora, numero=atual)
        resumo["pulados"] = pulados
        self.salvar()
        return resumo

    # -- o mundo --

    def ao_retornar(self, agora: float) -> dict:
        """A volta ao jogo: incerteza pelos dias fora e uma fila limitada do mundo."""
        if self.ultima_sessao is None:
            self.ultima_sessao = agora
            self.salvar()
            return {"dias": 0.0, "fila_nova": 0}
        segundos = max(0.0, agora - float(self.ultima_sessao))
        dias = min(DIAS_MAXIMOS, segundos / SEGUNDOS_POR_DIA)
        if dias > 0:
            self.ladder.inatividade(dias)
        nova = min(FILA_AO_RETORNAR, int(segundos / 3600 * PARTIDAS_DO_MUNDO_POR_HORA))
        self.fila = min(FILA_MAXIMA, self.fila + nova)
        self.ultima_sessao = agora
        self.salvar()
        return {"dias": round(dias, 2), "fila_nova": nova}

    def planejar(self, quantidade: int) -> list[tuple[str, str, int]]:
        """As próximas duplas do mundo, a partir do relógio atual. Não muda o estado."""
        quantidade = min(quantidade, self.fila)
        if quantidade <= 0:
            return []
        reservados = set(self.reservas.values())
        rng = random.Random(_semente(self.semente, "mundo", self.relogio))
        pares = [
            (a, b)
            for a, b in matchmaking.parear_npcs(self.ladder, rng, quantidade + len(reservados))
            if a not in reservados and b not in reservados
        ][:quantidade]
        return [
            (a, b, _semente(self.semente, "confronto", self.relogio + i, a, b))
            for i, (a, b) in enumerate(pares)
        ]

    def aplicar_do_mundo(self, confronto) -> None:
        """O resultado entra na Ladder (vitória ou empate técnico) e a vaga é consumida.

        Um erro técnico (`Anulada`) também consome a vaga — a mesma dupla com a
        mesma semente falharia de novo —, e fica no histórico como anulada.
        """
        if isinstance(confronto, Anulada):
            self.ladder.registrar_anulada(
                confronto.a, confronto.b, origem="mundo", motivo=confronto.motivo
            )
        elif confronto.vencedor is None:
            self.ladder.registrar_empate(
                confronto.a, confronto.b, origem="mundo", motivo=confronto.motivo
            )
        else:
            self.ladder.registrar(confronto.a, confronto.b, confronto.vencedor, origem="mundo")
        self.relogio += 1
        self.fila = max(0, self.fila - 1)


class AgendadorDoMundo:
    """Joga a fila do mundo numa thread, sem tocar na Ladder.

    A thread só produz resultados; quem os aplica é `coletar`, chamado pelo
    fluxo do jogo entre telas. `parar` interrompe entre rodadas, e a partida
    interrompida não conta.
    """

    def __init__(self, mundo: MundoRanqueado, *, lote: int = 4, jogar=ranked_partidas.jogar):
        self.mundo = mundo
        self.lote = lote
        self._jogar = jogar
        self._parar = threading.Event()
        self._resultados: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

    @property
    def ativo(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def iniciar(self) -> None:
        if self.ativo:
            return
        plano = self.mundo.planejar(self.lote)
        if not plano:
            return
        self._parar.clear()
        self._thread = threading.Thread(target=self._rodar, args=(plano,), daemon=True)
        self._thread.start()

    def _rodar(self, plano) -> None:
        for a, b, semente in plano:
            if self._parar.is_set():
                return
            try:
                confronto = self._jogar(self.mundo.populacao, a, b, semente, parar=self._parar)
            except Exception as erro:  # noqa: BLE001 — o erro vira partida anulada
                self._resultados.put(Anulada(a, b, f"erro técnico: {type(erro).__name__}"))
                continue
            if confronto is None:
                return
            self._resultados.put(confronto)

    def coletar(self) -> int:
        """Aplica o que já terminou, na ordem do plano, e grava."""
        aplicados = 0
        while True:
            try:
                confronto = self._resultados.get_nowait()
            except queue.Empty:
                break
            self.mundo.aplicar_do_mundo(confronto)
            aplicados += 1
        if aplicados:
            self.mundo.salvar()
        return aplicados

    def parar(self, espera: float = 5.0) -> int:
        self._parar.set()
        if self._thread is not None:
            self._thread.join(espera)
        return self.coletar()
