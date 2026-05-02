"""Funções matemáticas para cálculo de estatísticas e recompensas.

Todas as constantes são importadas de src.shared.constants.
"""

from __future__ import annotations

import random

from src.shared.constants import (
    ESSENCE_MULT_MAX,
    ESSENCE_MULT_MIN,
    ESSENCE_MULT_NORMAL_MEAN,
    ESSENCE_MULT_NORMAL_STD,
    MINI_BOSS_BASE_DEFENSE,
    MINI_BOSS_BASE_HP,
    MINI_BOSS_BASE_MAGIC,
    MINI_BOSS_BASE_STRENGTH,
    MINI_BOSS_BASE_XP_REWARD,
    MINI_BOSS_COIN_MULTIPLIER,
    MINI_BOSS_DEFENSE_SCALING_PER_LEVEL,
    MINI_BOSS_HP_SCALING_PER_LEVEL,
    MINI_BOSS_LEVEL_BONUS,
    MINI_BOSS_MAGIC_SCALING_PER_LEVEL,
    MINI_BOSS_STRENGTH_SCALING_PER_LEVEL,
    MINI_BOSS_XP_SCALING_PER_LEVEL,
    MONSTER_BASE_COIN_REWARD,
    MONSTER_BASE_DEFENSE,
    MONSTER_BASE_HP,
    MONSTER_BASE_MAGIC,
    MONSTER_BASE_STRENGTH,
    MONSTER_BASE_XP_REWARD,
    MONSTER_COIN_SCALING_PER_LEVEL,
    MONSTER_DEFENSE_SCALING_PER_LEVEL,
    MONSTER_HP_SCALING_PER_LEVEL,
    MONSTER_MAGIC_SCALING_PER_LEVEL,
    MONSTER_STRENGTH_SCALING_PER_LEVEL,
    MONSTER_XP_SCALING_PER_LEVEL,
    XP_GROWTH_PER_LEVEL,
    XP_INITIAL_COST,
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


def calculate_monster_hp(monster_level: int) -> int:
    """Calcula o HP total de um monstro baseado no seu nível.

    Args:
        monster_level: Nível do monstro (mínimo 1).

    Returns:
        HP total calculado.
    """
    return MONSTER_BASE_HP + (monster_level - 1) * MONSTER_HP_SCALING_PER_LEVEL


def calculate_monster_strength(monster_level: int) -> int:
    """Calcula a força (strength) de um monstro baseado no seu nível.

    Args:
        monster_level: Nível do monstro (mínimo 1).

    Returns:
        Valor de força calculado.
    """
    return MONSTER_BASE_STRENGTH + (monster_level - 1) * MONSTER_STRENGTH_SCALING_PER_LEVEL


def calculate_monster_defense(monster_level: int) -> int:
    """Calcula a defesa de um monstro baseado no seu nível.

    Args:
        monster_level: Nível do monstro (mínimo 1).

    Returns:
        Valor de defesa calculado.
    """
    return MONSTER_BASE_DEFENSE + (monster_level - 1) * MONSTER_DEFENSE_SCALING_PER_LEVEL


def calculate_monster_magic(monster_level: int) -> int:
    """Calcula o atributo mágico de um monstro baseado no seu nível.

    Args:
        monster_level: Nível do monstro (mínimo 1).

    Returns:
        Valor mágico calculado.
    """
    return MONSTER_BASE_MAGIC + (monster_level - 1) * MONSTER_MAGIC_SCALING_PER_LEVEL


def calculate_xp_for_next_level(current_level: int) -> int:
    """Calcula a quantidade de XP necessária para alcançar o próximo nível.

    Fórmula: XP_INITIAL_COST + (current_level - 1) * XP_GROWTH_PER_LEVEL

    Args:
        current_level: Nível atual do jogador.

    Returns:
        Quantidade de XP necessária para o próximo nível.
    """
    return XP_INITIAL_COST + (current_level - 1) * XP_GROWTH_PER_LEVEL


def calculate_monster_xp_reward(monster_level: int) -> int:
    """Calcula a recompensa de XP por derrotar um monstro.

    Args:
        monster_level: Nível do monstro derrotado.

    Returns:
        Quantidade de XP a ser concedida.
    """
    return MONSTER_BASE_XP_REWARD + (monster_level - 1) * MONSTER_XP_SCALING_PER_LEVEL


def _calculate_mini_boss_effective_level(dungeon_level: int) -> int:
    """Calcula o nível efetivo de um mini-boss.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Nível efetivo do mini-boss (dungeon_level + bônus).
    """
    return dungeon_level + MINI_BOSS_LEVEL_BONUS


def calculate_mini_boss_hp(dungeon_level: int) -> int:
    """Calcula o HP de um mini-boss para o nível da masmorra.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        HP total do mini-boss calculado.
    """
    effective_level = _calculate_mini_boss_effective_level(dungeon_level)
    return MINI_BOSS_BASE_HP + (effective_level - 1) * MINI_BOSS_HP_SCALING_PER_LEVEL


def calculate_mini_boss_strength(dungeon_level: int) -> int:
    """Calcula a força de um mini-boss para o nível da masmorra.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Valor de força do mini-boss calculado.
    """
    effective_level = _calculate_mini_boss_effective_level(dungeon_level)
    return MINI_BOSS_BASE_STRENGTH + (effective_level - 1) * MINI_BOSS_STRENGTH_SCALING_PER_LEVEL


def calculate_mini_boss_defense(dungeon_level: int) -> int:
    """Calcula a defesa de um mini-boss para o nível da masmorra.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Valor de defesa do mini-boss calculado.
    """
    effective_level = _calculate_mini_boss_effective_level(dungeon_level)
    return MINI_BOSS_BASE_DEFENSE + (effective_level - 1) * MINI_BOSS_DEFENSE_SCALING_PER_LEVEL


def calculate_mini_boss_magic(dungeon_level: int) -> int:
    """Calcula o atributo mágico de um mini-boss para o nível da masmorra.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Valor mágico do mini-boss calculado.
    """
    effective_level = _calculate_mini_boss_effective_level(dungeon_level)
    return MINI_BOSS_BASE_MAGIC + (effective_level - 1) * MINI_BOSS_MAGIC_SCALING_PER_LEVEL


def calculate_mini_boss_xp_reward(dungeon_level: int) -> int:
    """Calcula a recompensa de XP por derrotar um mini-boss.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Quantidade de XP a ser concedida pela vitória.
    """
    effective_level = _calculate_mini_boss_effective_level(dungeon_level)
    return MINI_BOSS_BASE_XP_REWARD + (effective_level - 1) * MINI_BOSS_XP_SCALING_PER_LEVEL


def calculate_monster_coin_reward(monster_level: int) -> int:
    """Calcula a recompensa de moedas por derrotar um monstro.

    Args:
        monster_level: Nível do monstro derrotado.

    Returns:
        Quantidade de moedas a ser concedida.
    """
    return MONSTER_BASE_COIN_REWARD + (monster_level - 1) * MONSTER_COIN_SCALING_PER_LEVEL


def calculate_mini_boss_coin_reward(dungeon_level: int) -> int:
    """Calcula a recompensa de moedas por derrotar um mini-boss.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Quantidade de moedas a ser concedida pela vitória.
    """
    base_reward = calculate_monster_coin_reward(dungeon_level + MINI_BOSS_LEVEL_BONUS)
    return base_reward * MINI_BOSS_COIN_MULTIPLIER


def generate_essence_multiplier() -> float:
    """Gera multiplicador de Essência para o andar usando distribuição gaussiana truncada.

    Returns:
        Multiplicador entre ESSENCE_MULT_MIN e ESSENCE_MULT_MAX, arredondado para 1 casa.
        Valores intermediários são mais prováveis que extremos.
    """
    value = random.gauss(ESSENCE_MULT_NORMAL_MEAN, ESSENCE_MULT_NORMAL_STD)
    clamped = max(ESSENCE_MULT_MIN, min(ESSENCE_MULT_MAX, value))
    return round(clamped, 1)

