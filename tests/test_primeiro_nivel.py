"""KI-002: limpar o andar 1 normalmente costuma render o primeiro nível.

Na auditoria `4d0a9a0a`, 178 de 266 runs entravam no andar 2 ainda no nível 1. A
causa era aritmética: o nível 2 custava 140 de XP, e o andar 1 tem 3 monstros
que pagam 45 × a Essência do andar cada. Só o andar inteiro, com Essência média,
pagava o nível. E uma largada ferida costuma sair do andar 1 com duas vitórias.

O custo do nível 1 passou a 100, mexendo só no começo da curva: a inclinação
funda, `XP_BASE_COST / (1 + XP_LEVEL_SOFTENER)`, é a mesma, e a curva posterior
converge para a de antes. Não há bônus por andar nem XP extra.
"""

from __future__ import annotations

import pytest

from src.content.factories.monsters import routine_monster_count
from src.mechanics.math_operations import calculate_monster_xp_reward
from src.shared.constants import (
    ESSENCE_MULT_NORMAL_MEAN,
    ESSENCE_MULT_NORMAL_STD,
    GROWTH_RATE,
    XP_BASE_COST,
    XP_LEVEL_SOFTENER,
)
from src.shared.formulas import xp_for_level

# A curva anterior, só para medir quanto o começo mudou e quanto o fundo não.
CUSTO_ANTIGO, AMORTECEDOR_ANTIGO = 140, 6

PRIMEIRO = xp_for_level(1)
VITORIA_NV1 = calculate_monster_xp_reward(1)
MONSTROS_DO_ANDAR_1 = routine_monster_count(1)
ESSENCIA_MEDIA = ESSENCE_MULT_NORMAL_MEAN
ESSENCIA_BAIXA = round(ESSENCE_MULT_NORMAL_MEAN - 2 * ESSENCE_MULT_NORMAL_STD, 1)


def _custo_antigo(nivel: int) -> int:
    amortecedor = (nivel + AMORTECEDOR_ANTIGO) / (1 + AMORTECEDOR_ANTIGO)
    return int(CUSTO_ANTIGO * amortecedor * GROWTH_RATE ** (nivel - 1))


class TestOPrimeiroNivelCabeNoAndar1:
    def test_o_andar_1_tem_os_tres_monstros_de_sempre(self):
        """A correção não veio de pôr mais monstro no andar para entregar XP."""
        assert MONSTROS_DO_ANDAR_1 == 3

    def test_limpar_o_andar_sobe_de_nivel_ate_com_essencia_baixa(self):
        """Dois desvios abaixo da média, o andar inteiro ainda paga o nível."""
        assert MONSTROS_DO_ANDAR_1 * VITORIA_NV1 * ESSENCIA_BAIXA >= PRIMEIRO

    def test_duas_vitorias_sobem_com_a_essencia_media(self):
        assert 2 * VITORIA_NV1 * ESSENCIA_MEDIA >= PRIMEIRO

    def test_nao_e_garantido(self):
        """Com Essência abaixo da média, duas vitórias não bastam; uma nunca basta."""
        assert 2 * VITORIA_NV1 * (ESSENCIA_MEDIA - ESSENCE_MULT_NORMAL_STD) < PRIMEIRO
        assert VITORIA_NV1 * 2 * ESSENCIA_MEDIA < PRIMEIRO * 2  # sanidade da conta
        assert VITORIA_NV1 * (ESSENCIA_MEDIA + 3 * ESSENCE_MULT_NORMAL_STD) < PRIMEIRO

    def test_antes_so_o_andar_inteiro_pagava(self):
        """A regressão que este arquivo existe para impedir."""
        assert 2 * VITORIA_NV1 * ESSENCIA_MEDIA < CUSTO_ANTIGO


class TestACurvaPosteriorFicaComoEra:
    def test_a_inclinacao_funda_e_a_mesma(self):
        assert XP_BASE_COST / (1 + XP_LEVEL_SOFTENER) == pytest.approx(
            CUSTO_ANTIGO / (1 + AMORTECEDOR_ANTIGO)
        )

    @pytest.mark.parametrize("nivel", [1, 2, 3, 5, 10, 20, 30, 50, 100, 200])
    def test_o_desvio_e_so_o_do_amortecedor(self, nivel):
        """Novo sobre antigo = (L + 4) / (L + 6): o começo muda, o fundo converge."""
        esperado = (nivel + XP_LEVEL_SOFTENER) / (nivel + AMORTECEDOR_ANTIGO)
        assert xp_for_level(nivel) / _custo_antigo(nivel) == pytest.approx(esperado, rel=0.01)

    def test_o_desvio_so_diminui_com_o_nivel(self):
        razoes = [xp_for_level(n) / _custo_antigo(n) for n in range(1, 300)]
        assert all(b >= a - 1e-3 for a, b in zip(razoes, razoes[1:]))
        assert razoes[-1] > 0.99

    def test_todo_nivel_continua_custando_mais_que_o_anterior(self):
        assert all(xp_for_level(n + 1) > xp_for_level(n) for n in range(1, 500))
