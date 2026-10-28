"""A progressão visível: 45 divisões de 100 PR, a fórmula do PR, promoção, rebaixamento e escudo.

Tudo aqui é a matemática de `ranked/progressao.py`, sem Ladder: a régua (nomes
e alvo), a variação de PR (resultado contra expectativa, puxada para o alvo) e
as transições da barra.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ranked import progressao as pg  # noqa: E402
from src.ranked import ranks  # noqa: E402
from src.ranked.progressao import Progresso  # noqa: E402


class TestRegua:
    def test_quarenta_e_cinco_divisoes_de_iron_v_a_obsidian_i(self):
        nomes = [pg.nome_da_divisao(d) for d in range(pg.DIVISOES)]
        assert pg.DIVISOES == 45 and len(set(nomes)) == 45
        assert nomes[:6] == ["Iron V", "Iron IV", "Iron III", "Iron II", "Iron I", "Bronze V"]
        assert nomes[-1] == "Obsidian I" and nomes[22] == "Platinum III"
        assert pg.ELITE == ("Master", "International Master", "Distinguished Master")
        with pytest.raises(ValueError):
            pg.nome_da_divisao(45)

    def test_o_alvo_segue_os_limites_de_percentil(self):
        assert pg.alvo(0.0) == 0
        for i, minimo in enumerate(ranks.LIMITES):
            assert pg.alvo(minimo) == pytest.approx(i * pg.POR_RANK)
        assert pg.alvo(ranks.LIMITES[9]) == pg.TOPO  # o mínimo de Master
        assert pg.alvo(100.0) == pytest.approx(12 * pg.POR_RANK)
        valores = [pg.alvo(p / 10) for p in range(1001)]
        assert all(a <= b for a, b in zip(valores, valores[1:]))


class TestVariacao:
    def test_vitoria_sobe_derrota_desce_e_a_surpresa_vale_mais(self):
        assert pg.variacao(1.0, 0.5, 1000, 1000) == 20
        assert pg.variacao(0.0, 0.5, 1000, 1000) == -20
        assert pg.variacao(1.0, 0.2, 1000, 1000) > pg.variacao(1.0, 0.8, 1000, 1000) > 0
        assert pg.variacao(0.0, 0.8, 1000, 1000) < pg.variacao(0.0, 0.2, 1000, 1000) < 0

    def test_o_empate_vale_pelo_que_se_esperava(self):
        assert pg.variacao(0.5, 0.5, 1000, 1000) == 0
        assert pg.variacao(0.5, 0.2, 1000, 1000) > 0  # empatou com o favorito
        assert pg.variacao(0.5, 0.8, 1000, 1000) < 0  # empatou com o azarão

    def test_vitoria_quase_certa_ainda_rende_um(self):
        assert pg.variacao(1.0, 0.999, 1000, 1000) == 1
        assert pg.variacao(0.0, 0.001, 1000, 1000) == -1

    def test_abaixo_do_alvo_sobe_mais_rapido_e_cai_mais_devagar(self):
        ganho_abaixo = pg.variacao(1.0, 0.5, 1000, 1600)
        perda_abaixo = pg.variacao(0.0, 0.5, 1000, 1600)
        ganho_acima = pg.variacao(1.0, 0.5, 1600, 1000)
        perda_acima = pg.variacao(0.0, 0.5, 1600, 1000)
        assert ganho_abaixo > 20 > ganho_acima > 0
        assert 0 > perda_abaixo > -20 > perda_acima
        # O multiplicador tem teto: longe demais não vira salto.
        assert pg.variacao(1.0, 0.5, 0, 4400) == round(20 * pg.MULTIPLICADOR_MAXIMO)
        assert abs(pg.variacao(1.0, 0.01, 0, 4400)) <= pg.VARIACAO_MAXIMA

    def test_jogar_muito_no_lugar_certo_nao_sobe_ninguem(self):
        """No alvo, com a chance certa, a média de ΔPR é zero: não há progressão por volume."""
        rng = random.Random(7)
        for chance in (0.3, 0.5, 0.7):
            total = 0
            for _ in range(20_000):
                total += pg.variacao(1.0 if rng.random() < chance else 0.0, chance, 2000, 2000)
            assert abs(total / 20_000) < 0.35


class TestTransicoes:
    def test_promocao_leva_o_excedente_e_arma_o_escudo(self):
        p = Progresso(divisao=10, pr=90)
        eventos = pg.aplicar(p, 25, 1100)
        assert (p.divisao, p.pr, p.escudo) == (11, 15, pg.ESCUDO)
        assert eventos == [{"evento": "promocao", "de": 10, "para": 11}]

    def test_rebaixamento_pousa_em_no_maximo_75(self):
        p = Progresso(divisao=10, pr=5)
        assert pg.aplicar(p, -10, 900) == [{"evento": "rebaixamento", "de": 10, "para": 9}]
        assert (p.divisao, p.pr) == (9, pg.PR_APOS_REBAIXAMENTO)
        p = Progresso(divisao=10, pr=5)
        pg.aplicar(p, -45, 900)
        assert (p.divisao, p.pr) == (9, 60)

    def test_o_escudo_segura_a_fronteira_por_tres_partidas(self):
        p = Progresso(divisao=10, pr=0, escudo=pg.ESCUDO)
        for _ in range(pg.ESCUDO):
            eventos = pg.aplicar(p, -20, 1000)
            assert eventos == [{"evento": "escudo", "divisao": 10}] and (p.divisao, p.pr) == (10, 0)
        assert pg.aplicar(p, -20, 1000)[0]["evento"] == "rebaixamento"

    def test_o_escudo_nao_esconde_quem_esta_no_lugar_errado(self):
        """Com o alvo mais de uma divisão abaixo, o escudo não vale."""
        p = Progresso(divisao=10, pr=0, escudo=pg.ESCUDO)
        assert pg.aplicar(p, -20, 850)[0]["evento"] == "rebaixamento"

    def test_iron_v_e_o_chao(self):
        p = Progresso(divisao=0, pr=10)
        assert pg.aplicar(p, -40, 0) == [] and (p.divisao, p.pr) == (0, 0)

    def test_obsidian_i_com_100_e_candidato_e_a_candidatura_cai_com_a_divisao(self):
        p = Progresso(divisao=pg.ULTIMA, pr=90)
        assert pg.aplicar(p, 30, 4700) == [{"evento": "candidatura"}]
        assert (p.pr, p.candidato) == (100, True)
        assert pg.aplicar(p, 30, 4700) == [] and p.pr == 100  # não acumula além de 100
        pg.aplicar(p, -50, 4700)
        assert p.candidato and p.pr == 50  # ainda em Obsidian I: segue candidato
        eventos = pg.aplicar(p, -60, 4000)
        assert [e["evento"] for e in eventos] == ["rebaixamento", "candidatura_perdida"]
        assert not p.candidato and p.divisao == pg.ULTIMA - 1

    def test_uma_partida_move_no_maximo_uma_divisao(self):
        p = Progresso(divisao=10, pr=99)
        pg.aplicar(p, 200, 4000)
        assert p.divisao == 11 and p.pr == 99

    def test_elite_e_posicionamento_nao_tem_pr(self):
        for p in (Progresso(elite="Master"), Progresso()):
            antes = p.para_dict()
            assert pg.aplicar(p, 50, 3000) == [] and p.para_dict() == antes


class TestPosicionamento:
    def test_nasce_no_alvo_com_escudo(self):
        p = pg.posicionar(2345.6)
        assert (p.divisao, p.pr, p.escudo) == (23, 45, pg.ESCUDO)
        assert pg.posicionar(-3).coordenada == 0

    def test_o_teto_do_posicionamento_e_obsidian_i_com_zero(self):
        for alvo in (4400, 4499, 4500, 5800):
            p = pg.posicionar(alvo)
            assert (p.divisao, p.pr, p.candidato) == (pg.ULTIMA, 0, False)

    def test_ida_e_volta_pelo_dicionario(self):
        p = Progresso(divisao=44, pr=100, escudo=1, candidato=True)
        assert Progresso.de_dict(p.para_dict()) == p
        assert Progresso.de_dict(None) == Progresso()
