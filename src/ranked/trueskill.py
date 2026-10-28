"""TrueSkill 1 × 1 (Herbrich, Minka e Graepel, 2006), na forma fechada.

Cada gladiador é uma normal N(μ, σ²) sobre a habilidade. Numa partida, o
desempenho de cada lado é a habilidade mais ruído de variância β²; vence quem
rende mais. Com dois jogadores, o grafo de fatores tem solução fechada: as
funções v e w da normal truncada.

`tau` é a dinâmica: antes de cada partida σ² cresce τ², e a incerteza nunca
zera. O empate só existe com `prob_empate` maior que zero (a margem de empate
do modelo); com zero, o modelo não tem como explicar um empate e recusa. O
TrueSkill não é o sistema do jogo (`sistema.py`): fica para comparação.
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


def _v_empate(t: float, eps: float) -> float:
    a, b = eps - abs(t), -eps - abs(t)
    den = _NORMAL.cdf(a) - _NORMAL.cdf(b)
    v = (_NORMAL.pdf(b) - _NORMAL.pdf(a)) / den if den > 1e-300 else a
    return -v if t < 0 else v


def _w_empate(t: float, eps: float) -> float:
    a, b = eps - abs(t), -eps - abs(t)
    den = _NORMAL.cdf(a) - _NORMAL.cdf(b)
    v = _v_empate(abs(t), eps)
    return v * v + (a * _NORMAL.pdf(a) - b * _NORMAL.pdf(b)) / den


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
        self, a: RatingTrueSkill, b: RatingTrueSkill, pontos_de_a: float
    ) -> tuple[RatingTrueSkill, RatingTrueSkill]:
        """`pontos_de_a`: 1 (vitória de `a`), ½ (empate) ou 0; `True`/`False` valem 1 e 0."""
        pontos = float(pontos_de_a)
        if pontos not in (0.0, 0.5, 1.0):
            raise ValueError(f"resultado {pontos_de_a!r}: só 1, ½ ou 0")
        if pontos == 0.5 and self.prob_empate <= 0:
            raise ValueError("TrueSkill sem margem de empate (prob_empate = 0)")
        a_venceu = pontos >= 0.5
        vencedor, perdedor = (a, b) if a_venceu else (b, a)
        var_v = vencedor.sigma**2 + self.tau**2
        var_p = perdedor.sigma**2 + self.tau**2
        c = math.sqrt(2.0 * self.beta**2 + var_v + var_p)
        t = (vencedor.mu - perdedor.mu) / c
        eps = self._margem() / c
        if pontos == 0.5:
            v, w = _v_empate(t, eps), _w_empate(t, eps)
        else:
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
