"""O que a Arena offline guarda de cada partida, e onde o MMR vai se ligar.

A Fase 5 deixa os PONTOS DE EXTENSÃO; a Fase 6 escolhe a fórmula do rating e a
persistência local. Nada aqui calcula rating nem grava em disco.

- `ResultadoDaPartida`: o registro imutável de uma partida terminada, com a
  identidade estável dos dois lados e a força de referência do oponente.
- `Historico`: onde os resultados se acumulam. `HistoricoDaSessao` guarda em
  memória enquanto o jogo está aberto.
- `Classificacao`: quem lê cada resultado e mantém um rating por gladiador.
  `SemClassificacao` é a implementação nula: não há fórmula escolhida.
- `identidade_do_gladiador`: a identidade do gladiador do jogador.

A força de referência é o OP medido na geração da população. Ela não é rating:
é o ponto de partida que a Fase 6 pode usar, ou não, para o rating inicial.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol

from src.storage.save_manager import CAMPOS_DE_EQUIPAMENTO


def identidade_do_gladiador(snapshot: dict, slot: int) -> str:
    """A identidade do gladiador extraído do jogador, estável entre partidas.

    É o slot e o conteúdo do save sem o que a preparação da Arena pode mudar
    (`CAMPOS_DE_EQUIPAMENTO`): trocar e gravar equipamento não muda a
    identidade, e uma run nova no mesmo slot é outro gladiador.
    """
    fixo = {campo: valor for campo, valor in snapshot.items() if campo not in CAMPOS_DE_EQUIPAMENTO}
    texto = json.dumps(fixo, sort_keys=True, ensure_ascii=False, default=str)
    return f"jogador:slot{slot}:{hashlib.sha256(texto.encode('utf-8')).hexdigest()[:16]}"


@dataclass(frozen=True)
class Participante:
    """Um lado da partida, como o histórico o lembra."""

    identidade: str
    nome: str
    classe: str
    nivel: int
    # O OP da geração, para o oponente da população. `None` para o gladiador
    # do jogador: o jogo não mede OP em tempo de partida.
    forca_de_referencia: float | None = None


@dataclass(frozen=True)
class ResultadoDaPartida:
    """Uma partida offline terminada, do ponto de vista do jogador."""

    jogador: Participante
    oponente: Participante
    venceu: bool
    motivo: str  # o `DuelResult.reason` do motor: "ko" ou "surrender"
    rodadas: int
    versao_do_catalogo: int

    @property
    def vencedor(self) -> Participante:
        return self.jogador if self.venceu else self.oponente

    @property
    def perdedor(self) -> Participante:
        return self.oponente if self.venceu else self.jogador


class Historico(Protocol):
    def registrar(self, resultado: ResultadoDaPartida) -> None: ...

    def partidas(self, identidade: str | None = None) -> list[ResultadoDaPartida]: ...

    def placar(self, identidade: str) -> tuple[int, int]: ...


class HistoricoDaSessao:
    """Os resultados desta sessão do jogo, em memória e na ordem em que saíram."""

    def __init__(self) -> None:
        self._partidas: list[ResultadoDaPartida] = []

    def registrar(self, resultado: ResultadoDaPartida) -> None:
        self._partidas.append(resultado)

    def partidas(self, identidade: str | None = None) -> list[ResultadoDaPartida]:
        return [
            p
            for p in self._partidas
            if identidade is None or identidade in (p.jogador.identidade, p.oponente.identidade)
        ]

    def placar(self, identidade: str) -> tuple[int, int]:
        """(vitórias, derrotas) do gladiador nesta sessão."""
        jogos = self.partidas(identidade)
        vitorias = sum(p.vencedor.identidade == identidade for p in jogos)
        return vitorias, len(jogos) - vitorias


class Classificacao(Protocol):
    def atualizar(self, resultado: ResultadoDaPartida) -> None: ...

    def rating(self, identidade: str) -> float | None: ...


class SemClassificacao:
    """Nenhum rating: a fórmula do MMR é decisão da Fase 6."""

    def atualizar(self, resultado: ResultadoDaPartida) -> None:
        return None

    def rating(self, identidade: str) -> float | None:
        return None
