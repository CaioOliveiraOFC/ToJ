"""Glicko-2 e TrueSkill 1 × 1, conferidos contra os exemplos publicados.

As propriedades que a Ranked usa também: só vitória e derrota contam, a
surpresa move mais que o esperado, a incerteza cai com partidas e volta a subir
com a inatividade, e a previsão é simétrica.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ranked.glicko2 import Glicko2, RatingGlicko2  # noqa: E402
from src.ranked.trueskill import RatingTrueSkill, TrueSkill  # noqa: E402

SISTEMAS = [Glicko2(), TrueSkill()]


class TestReferencias:
    def test_exemplo_de_glickman_2012(self):
        """O exemplo do artigo: 1500/200/0,06 contra 1400/30 (V), 1550/100 (D), 1700/300 (D)."""
        g = Glicko2(tau=0.5)
        r = g.atualizar(
            RatingGlicko2(1500, 200, 0.06),
            [
                (RatingGlicko2(1400, 30), 1),
                (RatingGlicko2(1550, 100), 0),
                (RatingGlicko2(1700, 300), 0),
            ],
        )
        assert r.rating == pytest.approx(1464.06, abs=0.02)
        assert r.rd == pytest.approx(151.52, abs=0.01)
        assert r.volatilidade == pytest.approx(0.05999, abs=1e-5)

    def test_rate_1vs1_do_trueskill(self):
        """O exemplo da documentação: dois novatos, empate de 10%."""
        ts = TrueSkill(prob_empate=0.10)
        vencedor, perdedor = ts.partida(ts.novo(), ts.novo(), True)
        assert (vencedor.mu, vencedor.sigma) == pytest.approx((29.396, 7.171), abs=1e-3)
        assert (perdedor.mu, perdedor.sigma) == pytest.approx((20.604, 7.171), abs=1e-3)


@pytest.mark.parametrize("sistema", SISTEMAS, ids=lambda s: s.nome)
class TestPropriedades:
    def test_a_previsao_e_simetrica_e_igual_entre_iguais(self, sistema):
        a, b = sistema.novo(), sistema.novo()
        assert sistema.esperado(a, b) == pytest.approx(0.5)
        forte = sistema.partida(a, b, True)[0]
        assert sistema.esperado(forte, b) + sistema.esperado(b, forte) == pytest.approx(1.0)
        assert sistema.esperado(forte, b) > 0.5

    def test_o_vencedor_sobe_o_perdedor_desce_e_a_incerteza_cai(self, sistema):
        a, b = sistema.novo(), sistema.novo()
        novo_a, novo_b = sistema.partida(a, b, True)
        assert sistema.exibicao(novo_a) > sistema.exibicao(a)
        assert sistema.exibicao(novo_b) < sistema.exibicao(b)
        assert sistema.incerteza(novo_a) < sistema.incerteza(a)

    def test_a_ordem_dos_argumentos_nao_muda_o_resultado(self, sistema):
        a, b = sistema.novo(), sistema.partida(sistema.novo(), sistema.novo(), True)[0]
        x_a, x_b = sistema.partida(a, b, False)
        y_b, y_a = sistema.partida(b, a, True)
        assert (x_a, x_b) == (y_a, y_b)

    def test_a_surpresa_move_mais_que_o_esperado(self, sistema):
        fraco, forte = sistema.novo(), sistema.novo()
        for _ in range(6):
            forte, fraco = sistema.partida(forte, fraco, True)
        esperado = sistema.partida(forte, fraco, True)[0]
        zebra = sistema.partida(forte, fraco, False)[0]
        ganho = sistema.exibicao(esperado) - sistema.exibicao(forte)
        perda = sistema.exibicao(forte) - sistema.exibicao(zebra)
        assert 0 < ganho < perda

    def test_a_inatividade_devolve_incerteza(self, sistema):
        r = sistema.novo()
        for _ in range(10):
            r = sistema.partida(r, sistema.novo(), True)[0]
        parado = sistema.inatividade(r, 50)
        assert sistema.incerteza(parado) > sistema.incerteza(r)
        assert sistema.exibicao(parado) == sistema.exibicao(r)
        assert sistema.inatividade(r, 0) == r


def test_o_rd_do_glicko_tem_teto():
    g = Glicko2(rd_maximo=350)
    assert g.inatividade(RatingGlicko2(1500, 340, 0.06), 10_000).rd == 350


def test_o_sigma_do_trueskill_nao_passa_do_inicial():
    ts = TrueSkill()
    assert ts.inatividade(RatingTrueSkill(25, 8.0), 10_000).sigma == pytest.approx(ts.sigma)
