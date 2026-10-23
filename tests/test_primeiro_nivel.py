"""KI-002: o primeiro level-up custa o que o andar 1 paga — e só ele mudou.

Na auditoria `4d0a9a0a`, 178 de 266 runs entravam no andar 2 ainda no nível 1. A
fórmula pedia 140 de XP no nível 1, e o andar 1 tem 3 monstros que pagam 45 × a
Essência do andar cada: só o andar inteiro, com Essência média, fechava a conta.

O primeiro level-up passou a ter custo próprio, `FIRST_LEVEL_XP_COST`. Do nível 2
em diante a curva é exatamente a de antes: mesmo `XP_BASE_COST`, mesmo
amortecedor, mesma inclinação. Baixar o nível 1 mexendo na fórmula foi tentado
(`32a0a5d9`) e desfeito: barateava os níveis 2-20 e o herói passava à frente do
andar.
"""

from __future__ import annotations

import pytest

from src.content.factories.monsters import routine_monster_count
from src.mechanics.math_operations import calculate_monster_xp_reward
from src.shared.constants import (
    ESSENCE_MULT_NORMAL_MEAN,
    ESSENCE_MULT_NORMAL_STD,
    FIRST_LEVEL_XP_COST,
    GROWTH_RATE,
    XP_BASE_COST,
    XP_LEVEL_SOFTENER,
)
from src.shared.formulas import xp_for_level

# A curva de `eba37d01`, nível a nível, como ela era: 140 × (L+6)/7 × 1,12^(L-1).
CURVA_ANTERIOR = {1: 140, 2: 179, 5: 346, 10: 887, 20: 4478, 30: 19259}

VITORIA_NV1 = calculate_monster_xp_reward(1)
MONSTROS_DO_ANDAR_1 = routine_monster_count(1)
ESSENCIA_MEDIA = ESSENCE_MULT_NORMAL_MEAN
ESSENCIA_BAIXA = round(ESSENCE_MULT_NORMAL_MEAN - 2 * ESSENCE_MULT_NORMAL_STD, 1)


def _formula_anterior(nivel: int) -> int:
    """A fórmula de `eba37d01`, com os números dela escritos à mão."""
    return int(140 * (nivel + 6) / 7 * 1.12 ** (nivel - 1))


class TestSoOPrimeiroNivelMudou:
    def test_o_nivel_1_custa_100(self):
        assert FIRST_LEVEL_XP_COST == 100
        assert xp_for_level(1) == 100

    @pytest.mark.parametrize("nivel", [2, 5, 10, 20, 30])
    def test_os_niveis_seguintes_sao_os_de_antes(self, nivel):
        assert xp_for_level(nivel) == CURVA_ANTERIOR[nivel]

    def test_a_formula_e_os_parametros_sao_os_de_antes(self):
        assert (XP_BASE_COST, XP_LEVEL_SOFTENER, GROWTH_RATE) == (140, 6, 1.12)
        for nivel in range(2, 400):
            assert xp_for_level(nivel) == _formula_anterior(nivel), nivel

    def test_o_acumulado_fica_exatamente_40_abaixo_em_qualquer_nivel(self):
        acumulado_novo = acumulado_antigo = 0
        for nivel in range(1, 400):
            acumulado_novo += xp_for_level(nivel)
            acumulado_antigo += _formula_anterior(nivel)
            # Para chegar ao nível `nivel + 1`, que é 2 ou mais.
            assert acumulado_antigo - acumulado_novo == 40, nivel + 1


class TestOPrimeiroNivelCabeNoAndar1:
    def test_o_andar_1_tem_os_tres_monstros_de_sempre(self):
        """A correção não veio de pôr mais monstro no andar para entregar XP."""
        assert MONSTROS_DO_ANDAR_1 == 3

    def test_limpar_o_andar_sobe_de_nivel_ate_com_essencia_baixa(self):
        assert MONSTROS_DO_ANDAR_1 * VITORIA_NV1 * ESSENCIA_BAIXA >= xp_for_level(1)

    def test_duas_vitorias_sobem_com_a_essencia_media(self):
        assert 2 * VITORIA_NV1 * ESSENCIA_MEDIA >= xp_for_level(1)

    def test_nao_e_garantido(self):
        """Duas vitórias com Essência abaixo da média não bastam; uma nunca basta."""
        abaixo = ESSENCIA_MEDIA - ESSENCE_MULT_NORMAL_STD
        assert 2 * VITORIA_NV1 * abaixo < xp_for_level(1)
        assert VITORIA_NV1 * (ESSENCIA_MEDIA + 3 * ESSENCE_MULT_NORMAL_STD) < xp_for_level(1)

    def test_antes_so_o_andar_inteiro_pagava(self):
        assert 2 * VITORIA_NV1 * ESSENCIA_MEDIA < CURVA_ANTERIOR[1]


class TestGanhoGrandeDeXP:
    @pytest.mark.parametrize("classe", ["Warrior", "Mage", "Rogue"])
    def test_um_ganho_grande_processa_varios_niveis(self, classe):
        """O laço de `process_post_battle`: um level-up por vez até a XP acabar."""
        from src.sim.harness import make_hero

        heroi = make_hero(classe, 1, "naked")
        alvo, sobra = 7, 13
        heroi.add_xp_points(sum(xp_for_level(n) for n in range(1, alvo)) + sobra)
        subidas = 0
        while heroi.level_up(show=True):
            subidas += 1
        assert subidas == alvo - 1
        assert heroi.get_level() == alvo
        assert heroi.xp_points == sobra
