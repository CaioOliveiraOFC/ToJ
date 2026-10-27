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
from src.ranked import matchmaking, sistema
from src.ranked.ladder import Ladder, Registro
from src.storage import save_manager

ARQUIVO = "ranked.json"
VERSAO = 1
INICIAL = Path(loader.__file__).resolve().parent / "arena_ranked" / "ladder_inicial.json"

PARTIDAS_DO_MUNDO_POR_PARTIDA = 2
PARTIDAS_DO_MUNDO_POR_HORA = 4
FILA_AO_RETORNAR = 24
FILA_MAXIMA = 60
DIAS_MAXIMOS = 30
SEGUNDOS_POR_DIA = 86_400


class RankedInvalidaError(RuntimeError):
    """O arquivo da Ranked não é legível nem desta versão: nada é sobrescrito."""


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
    ) -> None:
        self.ladder = ladder
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
        if os.path.exists(caminho):
            try:
                with open(caminho, encoding="utf-8") as f:
                    dados = json.load(f)
            except (OSError, json.JSONDecodeError) as erro:
                raise RankedInvalidaError(f"{caminho}: ilegível ({erro})") from erro
            if dados.get("versao") != VERSAO:
                raise RankedInvalidaError(f"{caminho}: versão {dados.get('versao')!r}")
        else:
            try:
                dados = json.loads(INICIAL.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as erro:
                raise RankedInvalidaError(f"estado inicial da Ranked ilegível: {erro}") from erro
            if dados.get("versao") != VERSAO:
                raise RankedInvalidaError("estado inicial da Ranked de outra versão")
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
        )
        mundo.sincronizar_populacao()
        return mundo

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
            "ladder": self.ladder.para_dict(),
        }

    def salvar(self) -> None:
        caminho = self.caminho or caminho_padrao()
        pasta = os.path.dirname(caminho) or "."
        os.makedirs(pasta, exist_ok=True)
        fd, temporario = tempfile.mkstemp(dir=pasta, prefix=".ranked-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.para_dict(), f, ensure_ascii=False)
            os.replace(temporario, caminho)
        except BaseException:
            Path(temporario).unlink(missing_ok=True)
            raise

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

    def registrar_do_jogador(self, identidade: str, oponente: str, venceu: bool):
        """O resultado da partida do jogador, e a fila do mundo cresce."""
        atualizacao = self.ladder.registrar(
            identidade, oponente, identidade if venceu else oponente, origem="ranqueada"
        )
        self.reservas.pop(identidade, None)
        self.fila = min(FILA_MAXIMA, self.fila + PARTIDAS_DO_MUNDO_POR_PARTIDA)
        self.salvar()
        return atualizacao

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

    def aplicar_do_mundo(self, confronto: ranked_partidas.Confronto) -> None:
        """O resultado entra na Ladder; sem vencedor, só no histórico. A vaga é consumida."""
        if confronto.vencedor is None:
            self.ladder.registrar_sem_resultado(confronto.a, confronto.b, origem="mundo")
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
            confronto = self._jogar(self.mundo.populacao, a, b, semente, parar=self._parar)
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
