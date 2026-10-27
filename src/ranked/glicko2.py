"""Glicko-2 (Glickman, "Example of the Glicko-2 system", 2012), passo a passo.

O rating vive em duas escalas: a exibida (r, RD, em torno de 1500) e a interna
(μ, φ = (r − 1500)/173,7178). A volatilidade σ mede o quanto o rating do
gladiador costuma mudar de verdade; ela sobe com resultados que surpreendem em
sequência e desce com resultados esperados.

Na Ranked, cada partida é um período de rating para os dois lados, com os
valores de ANTES da partida — é a prática dos jogos que usam Glicko-2 partida a
partida. A inatividade entra por `inatividade`: φ cresce com o número de
períodos sem jogar, e a incerteza volta a subir.

Só vitória e derrota: o resultado é 1 ou 0, sem bônus por duração, HP ou dano.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

ESCALA = 173.7178
CENTRO = 1500.0
TOLERANCIA = 1e-6


@dataclass(frozen=True)
class RatingGlicko2:
    rating: float = CENTRO
    rd: float = 350.0
    volatilidade: float = 0.06

    @property
    def mu(self) -> float:
        return (self.rating - CENTRO) / ESCALA

    @property
    def phi(self) -> float:
        return self.rd / ESCALA


def _de_interno(mu: float, phi: float, sigma: float) -> RatingGlicko2:
    return RatingGlicko2(CENTRO + ESCALA * mu, ESCALA * phi, sigma)


def _g(phi: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))


def _e(mu: float, mu_j: float, phi_j: float) -> float:
    return 1.0 / (1.0 + math.exp(-_g(phi_j) * (mu - mu_j)))


class Glicko2:
    """O sistema, com os parâmetros dele. `tau` restringe a volatilidade."""

    nome = "Glicko-2"

    def __init__(
        self,
        tau: float = 0.5,
        rd_inicial: float = 350.0,
        volatilidade_inicial: float = 0.06,
        rd_maximo: float = 350.0,
    ) -> None:
        self.tau = tau
        self.rd_inicial = rd_inicial
        self.volatilidade_inicial = volatilidade_inicial
        self.rd_maximo = rd_maximo

    def novo(self, rating: float = CENTRO, rd: float | None = None) -> RatingGlicko2:
        return RatingGlicko2(
            rating, self.rd_inicial if rd is None else rd, self.volatilidade_inicial
        )

    # -- leitura --

    @staticmethod
    def exibicao(r: RatingGlicko2) -> float:
        return r.rating

    @staticmethod
    def incerteza(r: RatingGlicko2) -> float:
        return r.rd

    @staticmethod
    def conservador(r: RatingGlicko2) -> float:
        """O rating que o gladiador tem com ~97,5% de confiança."""
        return r.rating - 2.0 * r.rd

    @staticmethod
    def esperado(a: RatingGlicko2, b: RatingGlicko2) -> float:
        """P(a vence b), com a incerteza dos dois lados."""
        phi = math.sqrt(a.phi * a.phi + b.phi * b.phi)
        return 1.0 / (1.0 + math.exp(-_g(phi) * (a.mu - b.mu)))

    @staticmethod
    def serializar(r: RatingGlicko2) -> dict:
        return {"rating": r.rating, "rd": r.rd, "volatilidade": r.volatilidade}

    @staticmethod
    def desserializar(d: dict) -> RatingGlicko2:
        return RatingGlicko2(float(d["rating"]), float(d["rd"]), float(d["volatilidade"]))

    # -- atualização --

    def atualizar(
        self, jogador: RatingGlicko2, resultados: list[tuple[RatingGlicko2, float]]
    ) -> RatingGlicko2:
        """Um período de rating: os resultados (oponente, 1 ou 0) contra valores pré-período."""
        mu, phi, sigma = jogador.mu, jogador.phi, jogador.volatilidade
        if not resultados:
            return self.inatividade(jogador, 1)
        # Passos 3 e 4: variância estimada e melhora estimada.
        inv_v = 0.0
        soma = 0.0
        for oponente, pontos in resultados:
            g = _g(oponente.phi)
            e = _e(mu, oponente.mu, oponente.phi)
            inv_v += g * g * e * (1.0 - e)
            soma += g * (pontos - e)
        v = 1.0 / inv_v
        delta = v * soma
        # Passo 5: a nova volatilidade (algoritmo de Illinois).
        a = math.log(sigma * sigma)
        tau2 = self.tau * self.tau

        def f(x: float) -> float:
            ex = math.exp(x)
            return (ex * (delta * delta - phi * phi - v - ex)) / (
                2.0 * (phi * phi + v + ex) ** 2
            ) - (x - a) / tau2

        grande_a = a
        if delta * delta > phi * phi + v:
            grande_b = math.log(delta * delta - phi * phi - v)
        else:
            k = 1
            while f(a - k * self.tau) < 0:
                k += 1
            grande_b = a - k * self.tau
        f_a, f_b = f(grande_a), f(grande_b)
        while abs(grande_b - grande_a) > TOLERANCIA:
            c = grande_a + (grande_a - grande_b) * f_a / (f_b - f_a)
            f_c = f(c)
            if f_c * f_b <= 0:
                grande_a, f_a = grande_b, f_b
            else:
                f_a /= 2.0
            grande_b, f_b = c, f_c
        sigma_novo = math.exp(grande_a / 2.0)
        # Passos 6 a 8.
        phi_estrela = math.sqrt(phi * phi + sigma_novo * sigma_novo)
        phi_novo = 1.0 / math.sqrt(1.0 / (phi_estrela * phi_estrela) + 1.0 / v)
        mu_novo = mu + phi_novo * phi_novo * soma
        return self._limitar(_de_interno(mu_novo, phi_novo, sigma_novo))

    def partida(
        self, a: RatingGlicko2, b: RatingGlicko2, a_venceu: bool
    ) -> tuple[RatingGlicko2, RatingGlicko2]:
        """Uma partida, um período para cada lado, com os valores de antes."""
        pontos = 1.0 if a_venceu else 0.0
        return self.atualizar(a, [(b, pontos)]), self.atualizar(b, [(a, 1.0 - pontos)])

    def inatividade(self, r: RatingGlicko2, periodos: float) -> RatingGlicko2:
        """A incerteza depois de `periodos` sem jogar: φ² cresce σ² por período."""
        if periodos <= 0:
            return r
        phi = math.sqrt(r.phi * r.phi + periodos * r.volatilidade * r.volatilidade)
        return self._limitar(_de_interno(r.mu, phi, r.volatilidade))

    def _limitar(self, r: RatingGlicko2) -> RatingGlicko2:
        if r.rd <= self.rd_maximo:
            return r
        return RatingGlicko2(r.rating, self.rd_maximo, r.volatilidade)
