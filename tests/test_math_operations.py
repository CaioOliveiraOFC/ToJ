"""Testes unitários de src/mechanics/math_operations.py — valores esperados calculados manualmente.

Constantes (src/shared/constants.py):
  MONSTER:  HP 100/+20 | ST 25/+15 | DF 20/+8 | MG 40/+12
            XP 50/+20  | moedas 30/+10
  MINI_BOSS (nível efetivo = dungeon_level + 2):
            HP 150/+40 | ST 80/+30 | DF 45/+10 | MG 75/+18
            XP 120/+25 | moedas = calculate_monster_coin_reward(d+2) * 3
  XP nível: 3000 + (nível-1)*750
  Essência: gauss(1.2, 0.5) truncada em [0.5, 3.0], arredondada a 1 casa.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from src.mechanics import math_operations as mo  # noqa: E402

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


# ------------------------------------------------- stats lineares de monstro


class TestMonsterStats:
    @pytest.mark.parametrize(
        "func,base,scaling",
        [
            (mo.calculate_monster_hp, 100, 20),
            (mo.calculate_monster_strength, 25, 15),
            (mo.calculate_monster_defense, 20, 8),
            (mo.calculate_monster_magic, 40, 12),
        ],
    )
    def test_nivel_1_retorna_o_base(self, func, base, scaling):
        assert func(1) == base

    @pytest.mark.parametrize(
        "func,base,scaling",
        [
            (mo.calculate_monster_hp, 100, 20),
            (mo.calculate_monster_strength, 25, 15),
            (mo.calculate_monster_defense, 20, 8),
            (mo.calculate_monster_magic, 40, 12),
        ],
    )
    def test_progressao_linear_nivel_5(self, func, base, scaling):
        assert func(5) == base + 4 * scaling


# --------------------------------------------------------------------- XP


class TestXpForNextLevel:
    @pytest.mark.parametrize(
        "level,expected",
        [
            (1, 3000),
            (2, 3750),
            (10, 9750),  # 3000 + 9*750
        ],
    )
    def test_formula_manual(self, level, expected):
        assert mo.calculate_xp_for_next_level(level) == expected


# ----------------------------------------------- recompensas de monstro comum


class TestMonsterRewards:
    @pytest.mark.parametrize(
        "level,expected",
        [(1, 50), (5, 130), (10, 230)],  # 50 + (n-1)*20
    )
    def test_xp_reward_manual(self, level, expected):
        assert mo.calculate_monster_xp_reward(level) == expected

    @pytest.mark.parametrize(
        "level,expected",
        [(1, 30), (7, 90)],  # 30 + (n-1)*10
    )
    def test_coin_reward_manual(self, level, expected):
        assert mo.calculate_monster_coin_reward(level) == expected


# --------------------------- recompensas/stats de mini-boss (captura de duplicação)
#
# NOTA DE AUDITORIA: as cinco funções calculate_mini_boss_* têm estrutura idêntica
# entre si (base + (nível_efetivo - 1) * scaling, com nível_efetivo = d + 2) —
# candidatos claros a uma única função parametrizada. Os testes abaixo pinam os
# valores exatos justamente para que qualquer divergência futura entre elas quebre.


class TestMiniBossStatsAndRewards:
    @pytest.mark.parametrize(
        "func,base,scaling,dungeon,expected",
        [
            # d=1 -> efetivo 3 ; d=4 -> efetivo 6
            (mo.calculate_mini_boss_hp, 150, 40, 1, 150 + 2 * 40),
            (mo.calculate_mini_boss_hp, 150, 40, 4, 150 + 5 * 40),
            (mo.calculate_mini_boss_strength, 80, 30, 1, 80 + 2 * 30),
            (mo.calculate_mini_boss_strength, 80, 30, 4, 80 + 5 * 30),
            (mo.calculate_mini_boss_defense, 45, 10, 1, 45 + 2 * 10),
            (mo.calculate_mini_boss_defense, 45, 10, 4, 45 + 5 * 10),
            (mo.calculate_mini_boss_magic, 75, 18, 1, 75 + 2 * 18),
            (mo.calculate_mini_boss_magic, 75, 18, 4, 75 + 5 * 18),
            (mo.calculate_mini_boss_xp_reward, 120, 25, 1, 120 + 2 * 25),
            (mo.calculate_mini_boss_xp_reward, 120, 25, 4, 120 + 5 * 25),
        ],
    )
    def test_valores_pinned(self, func, base, scaling, dungeon, expected):
        assert func(dungeon) == expected

    def test_mini_boss_coin_usa_composicao_com_monstro(self):
        # SUSPEITO (assimetria de duplicação): o XP do mini-boss tem constantes
        # próprias (MINI_BOSS_BASE_XP_REWARD/SCALING), mas a MOEDA reusa a fórmula
        # de monstro comum deslocada de +2 níveis e multiplica por 3. Duas vias
        # diferentes para recompensas irmãs — se um dia mudar o scaling de moeda
        # de monstro, o mini-boss muda junto, provavelmente sem intenção.
        assert mo.calculate_mini_boss_coin_reward(1) == mo.calculate_monster_coin_reward(3) * 3
        assert mo.calculate_mini_boss_coin_reward(10) == mo.calculate_monster_coin_reward(12) * 3

    @pytest.mark.parametrize(
        "dungeon,expected",
        [
            (1, 150),  # coin(3)=50 * 3
            (10, 420),  # coin(12)=140 * 3
        ],
    )
    def test_mini_boss_coin_valores_pinned(self, dungeon, expected):
        assert mo.calculate_mini_boss_coin_reward(dungeon) == expected


# --------------------------------------------------- generate_essence_multiplier
#
# NOTA DE AUDITORIA (design): a docstring diz "para o andar", mas a função NÃO
# recebe dungeon_level — é RNG pura por chamada. O teste cobre 3 seeds distintas;
# amarrar o multiplicador ao andar exigiria mudança na assinatura (fora de escopo).


class TestGenerateEssenceMultiplier:
    @pytest.mark.parametrize(
        "seed,expected",
        [
            (0, 1.7),
            (1, 1.8),
            (42, 1.1),
        ],
    )
    def test_seeds_fixas_valores_pinned(self, seed, expected):
        random.seed(seed)
        assert mo.generate_essence_multiplier() == expected

    @pytest.mark.parametrize("seed", [0, 7, 42, 123])
    def test_sempre_dentro_dos_limites_do_design(self, seed):
        random.seed(seed)
        value = mo.generate_essence_multiplier()
        assert 0.5 <= value <= 3.0
        assert round(value, 1) == value

    def test_replicacao_gauss_confere_valor_exato(self):
        random.seed(0)
        expected_raw = max(0.5, min(3.0, random.gauss(1.2, 0.5)))
        random.seed(0)
        assert mo.generate_essence_multiplier() == round(expected_raw, 1)
