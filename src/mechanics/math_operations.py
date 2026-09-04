"""Funções matemáticas para recompensas e progressão.

As fórmulas de atributo de monstro saíram daqui: elas eram aritméticas
(`base + (nível-1) * passo`) enquanto o herói crescia em percentual composto, e
duas curvas de formas diferentes divergem para sempre. Hoje o monstro é montado
em `content/factories/archetypes.py`, com a mesma razão geométrica do herói.

Todas as constantes são importadas de src.shared.constants.
"""

from __future__ import annotations

import random

from src.shared.constants import (
    ESSENCE_MULT_LEVEL_BONUS,
    ESSENCE_MULT_MAX,
    ESSENCE_MULT_MAX_BONUS,
    ESSENCE_MULT_MIN,
    ESSENCE_MULT_NORMAL_MEAN,
    ESSENCE_MULT_NORMAL_STD,
    GROWTH_RATE,
    MINI_BOSS_BASE_COIN_REWARD,
    MINI_BOSS_BASE_XP_REWARD,
    MINI_BOSS_LEVEL_BONUS,
    MONSTER_BASE_COIN_REWARD,
    MONSTER_BASE_XP_REWARD,
    XP_BASE_COST,
    XP_LEVEL_RATIO,
)


def percentage(percent: int | float, whole: int | float, remainder: bool = True) -> int | float:
    """Calcula a porcentagem de um valor.

    Args:
        percent: A porcentagem a ser calculada.
        whole: O valor base sobre o qual calcular a porcentagem.
        remainder: Se True, retorna float; se False, retorna int (divisão inteira).

    Returns:
        O resultado do cálculo percentual.
    """
    if remainder:
        return (percent * whole) / 100
    return (percent * whole) // 100


def calculate_xp_for_next_level(current_level: int) -> int:
    """XP necessária para sair de `current_level` para o próximo.

    Geométrica, com razão maior que a de crescimento dos atributos. Isso faz o
    número de combates por nível subir ao longo da run: o herói fica cada vez
    mais para trás do andar, e é daí que vem a dificuldade crescente — não de
    inflar os números do monstro.

    Antes existiam duas curvas de XP no código: esta, que ninguém chamava, e
    `Player.need_to_up`. Agora só existe esta, e `need_to_up` delega a ela.

    Args:
        current_level: Nível atual do jogador.

    Returns:
        Quantidade de XP necessária para o próximo nível.
    """
    return int(XP_BASE_COST * (XP_LEVEL_RATIO ** (max(1, current_level) - 1)))


def calculate_monster_xp_reward(monster_level: int) -> int:
    """XP concedida por derrotar um monstro do nível dado."""
    return int(MONSTER_BASE_XP_REWARD * (GROWTH_RATE ** (max(1, monster_level) - 1)))


def calculate_monster_coin_reward(monster_level: int) -> int:
    """Moedas concedidas por derrotar um monstro do nível dado."""
    return int(MONSTER_BASE_COIN_REWARD * (GROWTH_RATE ** (max(1, monster_level) - 1)))


def _calculate_mini_boss_effective_level(dungeon_level: int) -> int:
    """Nível efetivo de um mini-chefe: o andar mais o bônus de chefe."""
    return dungeon_level + MINI_BOSS_LEVEL_BONUS


def calculate_mini_boss_xp_reward(dungeon_level: int) -> int:
    """XP concedida por derrotar um mini-chefe."""
    level = _calculate_mini_boss_effective_level(dungeon_level)
    return int(MINI_BOSS_BASE_XP_REWARD * (GROWTH_RATE ** (max(1, level) - 1)))


def calculate_mini_boss_coin_reward(dungeon_level: int) -> int:
    """Moedas concedidas por derrotar um mini-chefe."""
    level = _calculate_mini_boss_effective_level(dungeon_level)
    return int(MINI_BOSS_BASE_COIN_REWARD * (GROWTH_RATE ** (max(1, level) - 1)))


def generate_essence_multiplier(dungeon_level: int = 1) -> float:
    """Gera multiplicador de Essência para o andar usando distribuição gaussiana truncada.

    A média cresce levemente com o andar (0.02 por nível, teto +0.4),
    dando sensação de progressão sem quebrar o RNG como fator principal.
    Andares profundos tendem a pagar um pouco melhor em média.

    Args:
        dungeon_level: Andar atual (1 = início). Afeta a média da distribuição.

    Returns:
        Multiplicador entre ESSENCE_MULT_MIN e ESSENCE_MULT_MAX, arredondado para 1 casa.
        Valores intermediários são mais prováveis que extremos.
    """
    bonus = min(ESSENCE_MULT_MAX_BONUS, (dungeon_level - 1) * ESSENCE_MULT_LEVEL_BONUS)
    mean = ESSENCE_MULT_NORMAL_MEAN + bonus
    value = random.gauss(mean, ESSENCE_MULT_NORMAL_STD)
    clamped = max(ESSENCE_MULT_MIN, min(ESSENCE_MULT_MAX, value))
    return round(clamped, 1)


def estimate_next_essence_multiplier(dungeon_level: int) -> float:
    """Estimativa da média do próximo andar para a tela de extração.

    Não sorteia — retorna a média esperada para dungeon_level+1, para que a
    UI possa mostrar "Estimativa: ~1.4x" sem prometer um número exato que o
    RNG depois não confirme. Mantém a mesma progressão da função real.

    Args:
        dungeon_level: Andar atual (o próximo é +1).

    Returns:
        Média estimada para o próximo andar, já arredondada a 1 casa.
    """
    next_level = dungeon_level + 1
    bonus = min(ESSENCE_MULT_MAX_BONUS, (next_level - 1) * ESSENCE_MULT_LEVEL_BONUS)
    mean = ESSENCE_MULT_NORMAL_MEAN + bonus
    # Mostra a média como estimativa, clamped no mesmo intervalo
    clamped = max(ESSENCE_MULT_MIN, min(ESSENCE_MULT_MAX, mean))
    return round(clamped, 1)

