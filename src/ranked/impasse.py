"""O impasse: quando um duelo da Ranked deixa de andar e vira empate técnico.

O motor do duelo não tem empate nem teto de rodadas — quem conduz a partida
decide quando parar (`mechanics/pvp_duel.py`). A Ranked para em dois casos, e
nos dois o resultado é EMPATE (½ ponto para cada lado no Glicko-2), nunca a
vitória de quem tem mais HP, OP, nível ou MMR:

- **impasse** — por `JANELA` rodadas seguidas, nenhum dos dois chegou a um HP
  ou a um MP mais baixo do que já tinha chegado na partida (com folga de
  `MARGEM` do máximo). Ninguém está sendo desgastado: os dois se recuperam tão
  rápido quanto se ferem, e o KO, se vier, é sorte. Uma build de cura,
  regeneração ou controle que ESTÁ ganhando empurra o outro para HP cada vez
  mais baixo, e cada mínimo novo zera a contagem.
- **teto** — a partida chegou a `TETO` rodadas, mesmo andando. É a rede de
  segurança; nos confrontos medidos, nenhuma partida que andava passou de 242.

A janela e a folga saem de 242 duelos reais da Fase 6, refeitos rodada a
rodada (`tools/ranked_progressao.py trajetorias` e `impasse`,
`reports/ranked/fase61/`): em todas as partidas que terminaram em KO com
desgaste contínuo, a maior espera por um mínimo novo foi de 50 rodadas;
`JANELA` é o triplo disso. As duplas em equilíbrio (Magos e Rogues de elite
que se curam tão rápido quanto apanham) esperaram de 134 a 826 rodadas — e
R31 × M33 não terminou em 1.500 rodadas em nenhuma das 7 seeds.

Este módulo só lê números (o HP e o MP de cada lado ao fim da rodada, e os
máximos); quem os tira do duelo é `engine/`.
"""

from __future__ import annotations

from dataclasses import dataclass

JANELA = 150
MARGEM = 0.01
TETO = 1000
IMPASSE = "impasse"
NO_TETO = "teto"


@dataclass(frozen=True)
class Veredito:
    motivo: str
    rodada: int


class ArbitroDeImpasse:
    """Acompanha a partida rodada a rodada e diz quando ela vira empate técnico."""

    def __init__(self, janela: int = JANELA, margem: float = MARGEM, teto: int = TETO) -> None:
        self.janela = janela
        self.margem = margem
        self.teto = teto
        self._minimos: list[float] | None = None
        self.ultimo_desgaste = 0
        self.rodada = 0
        self.veredito: Veredito | None = None

    @property
    def sem_desgaste(self) -> int:
        """Rodadas seguidas sem nenhum mínimo novo."""
        return self.rodada - self.ultimo_desgaste

    @property
    def faltam(self) -> int:
        """Rodadas até o empate técnico, se ninguém se desgastar mais."""
        return max(0, min(self.janela - self.sem_desgaste, self.teto - self.rodada))

    def observar(self, rodada: int, hp, mp, maximos) -> Veredito | None:
        """O estado ao fim da rodada: `hp` e `mp` dos dois lados; `maximos` = (hp, mp)."""
        self.rodada = rodada
        fracoes = [
            valor / maximo if maximo > 0 else 0.0
            for valores, limites in zip((hp, mp), maximos)
            for valor, maximo in zip(valores, limites)
        ]
        if self._minimos is None:
            self._minimos = fracoes
            self.ultimo_desgaste = rodada
        else:
            for i, fracao in enumerate(fracoes):
                if fracao < self._minimos[i] - self.margem:
                    self._minimos[i] = fracao
                    self.ultimo_desgaste = rodada
        if rodada >= self.teto:
            self.veredito = Veredito(NO_TETO, rodada)
        elif self.sem_desgaste >= self.janela:
            self.veredito = Veredito(IMPASSE, rodada)
        return self.veredito


class Observador:
    """Só registra o HP e o MP de cada rodada (para análise); encerra só no teto."""

    def __init__(self, teto: int = 1500) -> None:
        self.teto = teto
        self.maximos: list[list[int]] | None = None
        self.hp: list[list[int]] = []
        self.mp: list[list[int]] = []

    def observar(self, rodada: int, hp, mp, maximos) -> Veredito | None:
        if self.maximos is None:
            self.maximos = [list(m) for m in maximos]
        self.hp.append([int(v) for v in hp])
        self.mp.append([int(v) for v in mp])
        return Veredito(NO_TETO, rodada) if rodada >= self.teto else None
