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
from src.shared import constants  # noqa: E402
from src.shared.constants import (  # noqa: E402
    GROWTH_RATE,
    MONSTER_BASE_COIN_REWARD,
    MONSTER_BASE_XP_REWARD,
    XP_BASE_COST,
    XP_LEVEL_RATIO,
)
from src.shared.formulas import geometric, xp_for_level  # noqa: E402

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
        assert mo.calculate_monster_xp_reward(10) == geometric(MONSTER_BASE_XP_REWARD, 10)

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
        assert mo.calculate_xp_for_next_level(level) == xp_for_level(level)

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
        assert mo.calculate_monster_xp_reward(level) == geometric(MONSTER_BASE_XP_REWARD, level)
        assert mo.calculate_monster_coin_reward(level) == geometric(MONSTER_BASE_COIN_REWARD, level)


# --------------------------------------------------- generate_essence_multiplier
# Corrigido: agora recebe dungeon_level e a média sobe 0.02 por andar (teto +0.4),
# dando progressão suave. A UI de extração mostra estimativa do próximo andar.


class TestGenerateEssenceMultiplier:
    """O sorteio da Essência, verificado contra as constantes que o definem.

    Esta classe fixava três valores de saída para três seedes, mais os limites
    0.5 e 3.0 e os parâmetros 1.2 e 0.5 digitados à mão. Todo número aparecia
    duas vezes: uma em `shared/constants.py` e outra aqui. Quando o desvio caiu
    de 0.5 para 0.2 para tirar peso da sorte, os testes reprovaram uma mudança
    correta e não teriam notado se a fórmula tivesse mudado junto.

    Agora o teste deriva tudo das constantes e cobra a distribuição, que é o que
    o design promete: média, desvio e limites.
    """

    @pytest.mark.parametrize("seed", [0, 7, 42, 123])
    def test_sempre_dentro_dos_limites_do_design(self, seed):
        random.seed(seed)
        value = mo.generate_essence_multiplier(1)
        assert constants.ESSENCE_MULT_MIN <= value <= constants.ESSENCE_MULT_MAX
        assert round(value, 1) == value

    def test_replicacao_gauss_confere_valor_exato_nivel_1(self):
        random.seed(0)
        sorteio = random.gauss(
            constants.ESSENCE_MULT_NORMAL_MEAN, constants.ESSENCE_MULT_NORMAL_STD
        )
        bruto = max(
            constants.ESSENCE_MULT_MIN, min(constants.ESSENCE_MULT_MAX, sorteio)
        )
        random.seed(0)
        assert mo.generate_essence_multiplier(1) == round(bruto, 1)

    def test_a_amostra_tem_a_media_e_o_desvio_declarados(self):
        # O que o design promete não é um valor, é uma distribuição.
        import statistics

        random.seed(1337)
        amostra = [mo.generate_essence_multiplier(1) for _ in range(20000)]
        assert abs(statistics.fmean(amostra) - constants.ESSENCE_MULT_NORMAL_MEAN) < 0.02
        assert abs(statistics.pstdev(amostra) - constants.ESSENCE_MULT_NORMAL_STD) < 0.03

    def test_os_limites_cobrem_a_curva_sem_sobrar(self):
        """Os limites precisam ser alcançáveis e não podem cortar a curva.

        Limite longe demais é promessa que o sorteio não cumpre — a tela de
        extração anunciava "faixa 0.5x - 3.0x" quando 3.0 estava a mais de oito
        desvios da média. Perto demais empilha resultado no teto.
        """
        media = constants.ESSENCE_MULT_NORMAL_MEAN
        media_maxima = media + constants.ESSENCE_MULT_MAX_BONUS
        desvio = constants.ESSENCE_MULT_NORMAL_STD

        assert constants.ESSENCE_MULT_MIN <= media - 2 * desvio
        assert constants.ESSENCE_MULT_MAX >= media_maxima + 2 * desvio
        assert constants.ESSENCE_MULT_MIN >= media - 4 * desvio
        assert constants.ESSENCE_MULT_MAX <= media_maxima + 4 * desvio

    def test_as_faixas_de_leitura_seguem_a_curva(self):
        # A cor da tela não pode chamar de "bom" um andar que virou comum.
        assert constants.ESSENCE_MULT_POOR < constants.ESSENCE_MULT_NORMAL_MEAN
        assert constants.ESSENCE_MULT_NORMAL_MEAN < constants.ESSENCE_MULT_GOOD
        assert constants.ESSENCE_MULT_MIN < constants.ESSENCE_MULT_POOR
        assert constants.ESSENCE_MULT_GOOD < constants.ESSENCE_MULT_MAX

    def test_progressao_com_andar_aumenta_media(self):
        # Média em andar 20 deve ser maior que no andar 1.
        random.seed(0)
        v1 = mo.generate_essence_multiplier(1)
        random.seed(0)
        v20 = mo.generate_essence_multiplier(20)
        assert v20 >= v1

    def test_estimativa_proximo_andar(self):
        # Estimativa para o próximo andar é a média esperada, sem sortear
        assert mo.estimate_next_essence_multiplier(1) == 1.2  # 1.2 + 0.02
        assert mo.estimate_next_essence_multiplier(10) == 1.4  # 1.2 + 0.20
        assert mo.estimate_next_essence_multiplier(30) == 1.6  # teto +0.4
