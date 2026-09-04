"""Testes de src/mechanics/math_operations.py.

As fórmulas de atributo de monstro saíram deste módulo: hoje o monstro é montado
por arquétipo em content/factories/archetypes.py, com a mesma razão geométrica
do herói. O que resta aqui é recompensa e progressão.

  Monstro:   XP e moedas = base * GROWTH_RATE^(nível-1)
  Mini-chefe: mesma forma, nível efetivo = andar + MINI_BOSS_LEVEL_BONUS
  Custo de nível: XP_BASE_COST * XP_LEVEL_RATIO^(nível-1), com
                  XP_LEVEL_RATIO > GROWTH_RATE de propósito
  Essência: gauss truncada em [0.5, 3.0], arredondada a 1 casa.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from src.mechanics import math_operations as mo  # noqa: E402
from src.shared.constants import (  # noqa: E402
    GROWTH_RATE,
    MONSTER_BASE_COIN_REWARD,
    MONSTER_BASE_XP_REWARD,
    XP_BASE_COST,
    XP_LEVEL_RATIO,
)

# ------------------------------------------------------------------ percentage


class TestPercentage:
    def test_float_padrao(self):
        assert mo.percentage(25, 200) == 50.0

    def test_inteiro_com_remainder_false(self):
        result = mo.percentage(33, 100, remainder=False)
        assert result == 33
        assert isinstance(result, int)

    def test_trunca_em_modo_inteiro(self):
        assert mo.percentage(33, 10, remainder=False) == 3  # 3.3 -> 3


# ------------------------------ escalonamento geométrico compartilhado
#
# A regra central do rebalanceamento: herói e monstro crescem pela MESMA razão.
# Antes, o herói crescia em percentual composto e o monstro em soma fixa, e duas
# curvas de formas diferentes divergem para sempre — era daí que vinha a taxa de
# vitória de 100% contra monstro comum em todos os níveis.


class TestEscalonamentoCompartilhado:
    def test_recompensas_usam_a_razao_comum(self):
        assert mo.calculate_monster_xp_reward(1) == MONSTER_BASE_XP_REWARD
        esperado_nv10 = int(MONSTER_BASE_XP_REWARD * GROWTH_RATE**9)
        assert mo.calculate_monster_xp_reward(10) == esperado_nv10

    def test_custo_de_xp_cresce_mais_rapido_que_a_recompensa(self):
        # É essa diferença que faz o número de combates por nível subir ao longo
        # da run, colocando o herói progressivamente atrás do andar.
        assert XP_LEVEL_RATIO > GROWTH_RATE

    def test_combates_por_nivel_sobem_com_o_nivel(self):
        def combates(nivel):
            return mo.calculate_xp_for_next_level(nivel) / mo.calculate_monster_xp_reward(nivel)

        assert combates(1) < combates(10) < combates(19)

    def test_mini_boss_recompensa_mais_que_monstro_do_mesmo_andar(self):
        for andar in (1, 5, 10, 15):
            assert mo.calculate_mini_boss_xp_reward(andar) > mo.calculate_monster_xp_reward(andar)
            assert mo.calculate_mini_boss_coin_reward(andar) > mo.calculate_monster_coin_reward(andar)


# --------------------------------------------------------------------- XP


class TestXpForNextLevel:
    def test_nivel_1_e_o_custo_base(self):
        assert mo.calculate_xp_for_next_level(1) == XP_BASE_COST

    @pytest.mark.parametrize("level", [2, 5, 10, 19])
    def test_formula_geometrica(self, level):
        assert mo.calculate_xp_for_next_level(level) == int(
            XP_BASE_COST * XP_LEVEL_RATIO ** (level - 1)
        )

    def test_curva_e_monotonica(self):
        custos = [mo.calculate_xp_for_next_level(n) for n in range(1, 21)]
        assert custos == sorted(custos)


# ----------------------------------------------- recompensas de monstro comum


class TestMonsterRewards:
    def test_nivel_1_retorna_a_base(self):
        assert mo.calculate_monster_xp_reward(1) == MONSTER_BASE_XP_REWARD
        assert mo.calculate_monster_coin_reward(1) == MONSTER_BASE_COIN_REWARD

    @pytest.mark.parametrize("level", [5, 10, 20])
    def test_progressao_geometrica(self, level):
        assert mo.calculate_monster_xp_reward(level) == int(
            MONSTER_BASE_XP_REWARD * GROWTH_RATE ** (level - 1)
        )
        assert mo.calculate_monster_coin_reward(level) == int(
            MONSTER_BASE_COIN_REWARD * GROWTH_RATE ** (level - 1)
        )


# --------------------------------------------------- generate_essence_multiplier
# Corrigido: agora recebe dungeon_level e a média sobe 0.02 por andar (teto +0.4),
# dando progressão suave. A UI de extração mostra estimativa do próximo andar.


class TestGenerateEssenceMultiplier:
    @pytest.mark.parametrize(
        "seed,expected",
        [
            (0, 1.7),
            (1, 1.8),
            (42, 1.1),
        ],
    )
    def test_seeds_fixas_valores_pinned_nivel_1(self, seed, expected):
        random.seed(seed)
        assert mo.generate_essence_multiplier(1) == expected

    @pytest.mark.parametrize("seed", [0, 7, 42, 123])
    def test_sempre_dentro_dos_limites_do_design(self, seed):
        random.seed(seed)
        value = mo.generate_essence_multiplier(1)
        assert 0.5 <= value <= 3.0
        assert round(value, 1) == value

    def test_replicacao_gauss_confere_valor_exato_nivel_1(self):
        random.seed(0)
        expected_raw = max(0.5, min(3.0, random.gauss(1.2, 0.5)))
        random.seed(0)
        assert mo.generate_essence_multiplier(1) == round(expected_raw, 1)

    def test_progressao_com_andar_aumenta_media(self):
        # Média em andar 20 deve ser maior que no andar 1 (0.02*19=0.38 de bônus)
        random.seed(0)
        v1 = mo.generate_essence_multiplier(1)
        random.seed(0)
        v20 = mo.generate_essence_multiplier(20)
        # Com mesma seed, o valor roll é o mesmo gauss, mas a média é maior, então v20 >= v1
        assert v20 >= v1

    def test_estimativa_proximo_andar(self):
        # Estimativa para o próximo andar é a média esperada, sem sortear
        assert mo.estimate_next_essence_multiplier(1) == 1.2  # 1.2 + 0.02
        assert mo.estimate_next_essence_multiplier(10) == 1.4  # 1.2 + 0.20
        assert mo.estimate_next_essence_multiplier(30) == 1.6  # teto +0.4
