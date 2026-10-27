"""TrueSkill 1 × 1 (Herbrich, Minka e Graepel, 2006), na forma fechada.

Cada gladiador é uma normal N(μ, σ²) sobre a habilidade. Numa partida, o
desempenho de cada lado é a habilidade mais ruído de variância β²; vence quem
rende mais. Com dois jogadores, o grafo de fatores tem solução fechada: as
funções v e w da normal truncada.

`tau` é a dinâmica: antes de cada partida σ² cresce τ², e a incerteza nunca
zera. Sem empate na Arena: `prob_empate` existe só para conferir a
implementação contra o exemplo publicado, que usa 10%.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

_NORMAL = NormalDist()
MU = 25.0
SIGMA = MU / 3.0


@dataclass(frozen=True)
class RatingTrueSkill:
    mu: float = MU
    sigma: float = SIGMA


def _v(t: float, eps: float) -> float:
    x = t - eps
    den = _NORMAL.cdf(x)
    if den < 1e-300:
        return -x
    return _NORMAL.pdf(x) / den


def _w(t: float, eps: float) -> float:
    v = _v(t, eps)
    return v * (v + t - eps)


class TrueSkill:
    """O sistema, com os parâmetros dele."""

    nome = "TrueSkill"

    def __init__(
        self,
        mu: float = MU,
        sigma: float = SIGMA,
        beta: float | None = None,
        tau: float | None = None,
        prob_empate: float = 0.0,
    ) -> None:
        self.mu = mu
        self.sigma = sigma
        self.beta = sigma / 2.0 if beta is None else beta
        self.tau = sigma / 100.0 if tau is None else tau
        self.prob_empate = prob_empate

    def novo(self, mu: float | None = None, sigma: float | None = None) -> RatingTrueSkill:
        return RatingTrueSkill(
            self.mu if mu is None else mu, self.sigma if sigma is None else sigma
        )

    # -- leitura --

    @staticmethod
    def exibicao(r: RatingTrueSkill) -> float:
        return r.mu

    @staticmethod
    def incerteza(r: RatingTrueSkill) -> float:
        return r.sigma

    @staticmethod
    def conservador(r: RatingTrueSkill) -> float:
        """O placar de leaderboard do TrueSkill: μ − 3σ."""
        return r.mu - 3.0 * r.sigma

    def esperado(self, a: RatingTrueSkill, b: RatingTrueSkill) -> float:
        """P(a vence b)."""
        c = math.sqrt(2.0 * self.beta**2 + a.sigma**2 + b.sigma**2)
        return _NORMAL.cdf((a.mu - b.mu) / c)

    @staticmethod
    def serializar(r: RatingTrueSkill) -> dict:
        return {"mu": r.mu, "sigma": r.sigma}

    @staticmethod
    def desserializar(d: dict) -> RatingTrueSkill:
        return RatingTrueSkill(float(d["mu"]), float(d["sigma"]))

    # -- atualização --

    def _margem(self) -> float:
        if self.prob_empate <= 0:
            return 0.0
        return _NORMAL.inv_cdf((self.prob_empate + 1.0) / 2.0) * math.sqrt(2.0) * self.beta

    def partida(
        self, a: RatingTrueSkill, b: RatingTrueSkill, a_venceu: bool
    ) -> tuple[RatingTrueSkill, RatingTrueSkill]:
        vencedor, perdedor = (a, b) if a_venceu else (b, a)
        var_v = vencedor.sigma**2 + self.tau**2
        var_p = perdedor.sigma**2 + self.tau**2
        c = math.sqrt(2.0 * self.beta**2 + var_v + var_p)
        t = (vencedor.mu - perdedor.mu) / c
        eps = self._margem() / c
        v, w = _v(t, eps), _w(t, eps)
        novo_v = RatingTrueSkill(
            vencedor.mu + var_v / c * v, math.sqrt(var_v * max(1e-12, 1.0 - var_v / c**2 * w))
        )
        novo_p = RatingTrueSkill(
            perdedor.mu - var_p / c * v, math.sqrt(var_p * max(1e-12, 1.0 - var_p / c**2 * w))
        )
        return (novo_v, novo_p) if a_venceu else (novo_p, novo_v)

    def inatividade(self, r: RatingTrueSkill, periodos: float) -> RatingTrueSkill:
        """A incerteza depois de `periodos` sem jogar: σ² cresce τ² por período."""
        if periodos <= 0:
            return r
        return RatingTrueSkill(
            r.mu, min(self.sigma, math.sqrt(r.sigma**2 + periodos * self.tau**2))
        )
