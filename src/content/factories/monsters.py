from __future__ import annotations

import random
from typing import Any

from src.data.loader import load_monsters_data
from src.entities.monsters import Monster
from src.mechanics.math_operations import (
    calculate_mini_boss_defense,
    calculate_mini_boss_hp,
    calculate_mini_boss_magic,
    calculate_mini_boss_strength,
    calculate_monster_defense,
    calculate_monster_hp,
    calculate_monster_magic,
    calculate_monster_strength,
)


def calculate_scaled_monster_level(
    dungeon_level: int,
    player_level: int,
) -> int:
    """
    Calcula o nível do monstro com base no dungeon_level e player_level.
    
    Implementa as regras de escalonamento inteligente:
    - 70% de chance: nível base (dungeon_level)
    - 25% de chance: nível base + 1
    - 5% de chance: nível base + 2
    
    Aplica as regras de segurança (anti-RNG injusto):
    - Nível do inimigo nunca ultrapassa dungeon_level + 3
    - Se player_level <= 3, nível do inimigo nunca > player_level + 2
    - Se dungeon_level == 1, nível do inimigo nunca >= 4
    
    Args:
        dungeon_level: Nível atual da masmorra.
        player_level: Nível atual do jogador.
    
    Returns:
        Nível do monstro calculado com segurança.
    """
    base_level = dungeon_level
    
    # Aplicar probabilidades: 70%, 25%, 5%
    population = [base_level, base_level + 1, base_level + 2]
    weights = [70, 25, 5]
    monster_level = random.choices(population, weights=weights, k=1)[0]
    
    # Aplicar regras de segurança
    # Regra 1: Nunca ultrapassa dungeon_level + 3
    monster_level = min(monster_level, dungeon_level + 3)
    
    # Regra 2: Se player_level <= 3, nunca > player_level + 2
    if player_level <= 3:
        monster_level = min(monster_level, player_level + 2)
    
    # Regra 3: Se dungeon_level == 1, nunca >= 4
    if dungeon_level == 1:
        monster_level = min(monster_level, 3)
    
    # Garantir nível mínimo de 1
    return max(1, monster_level)


def _get_monsters_data() -> dict[str, Any]:
    """Carrega e retorna os dados de monstros do JSON."""
    return load_monsters_data()


def create_monster(nick_name: str, level: int) -> Monster:
    """
    Cria uma instância de Monster com stats calculados.

    O código Python atua como injetor de dependências, aplicando
    as fórmulas de escalonamento sobre os dados base.
    """
    lvl = max(1, int(level))
    return Monster(
        nick_name,
        lvl,
        hp=calculate_monster_hp(lvl),
        st=calculate_monster_strength(lvl),
        df=calculate_monster_defense(lvl),
        mg=calculate_monster_magic(lvl),
    )


def generate_monsters_for_level(dungeon_level: int, player_level: int = 1) -> list[Monster]:
    """
    Gerador procedural que lê definições do JSON com escalonamento inteligente.

    Utiliza a função calculate_scaled_monster_level para gerar monstros
    com níveis apropriados ao dungeon_level, respeitando as regras de
    probabilidade e segurança.

    Args:
        dungeon_level: Nível atual da masmorra.
        player_level: Nível atual do jogador (default: 1).

    Returns:
        Lista de monstros gerados com níveis escalados.
    """
    data = _get_monsters_data()
    gen = data["generation"]
    categories = data["categories"]

    monsters: list[Monster] = []

    base_num = gen["base_count"]
    scaling = dungeon_level // gen["scaling_per_3_levels"]
    num_monsters = max(gen["min_monsters"], base_num + scaling)

    boss_chance = gen["boss_spawn_chance"]

    for _ in range(num_monsters):
        # Usar a nova lógica de escalonamento inteligente
        monster_level = calculate_scaled_monster_level(dungeon_level, player_level)

        chosen_type = _select_monster_type(dungeon_level, categories, boss_chance)

        if chosen_type == "boss":
            monster_level += categories["boss"].get("level_bonus", 0)

        base_name = random.choice(categories[chosen_type]["names"])
        monster_name = f"{base_name} Nv.{monster_level}"
        monsters.append(create_monster(monster_name, monster_level))

    return monsters


def _select_monster_type(
    dungeon_level: int, categories: dict[str, Any], boss_chance: float
) -> str:
    """Seleciona o tipo de monstro baseado no nível da masmorra."""
    if dungeon_level < 5:
        return "common"
    elif 5 <= dungeon_level < 10:
        return random.choice(["common", "uncommon"])
    elif 10 <= dungeon_level < 20:
        return random.choice(["uncommon", "rare"])
    else:
        if random.random() < boss_chance and dungeon_level >= categories["boss"]["min_level"]:
            return "boss"
        return "rare"


def create_boss_for_level(dungeon_level: int) -> Monster:
    """Cria mini-boss com stats escalados para o nível de masmorra.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Instância de Monster configurada como mini-boss.
    """
    boss_level = dungeon_level + 2
    boss = Monster(
        nick_name=f"Chefe Nv.{boss_level}",
        mob_level=boss_level,
        hp=calculate_mini_boss_hp(dungeon_level),
        st=calculate_mini_boss_strength(dungeon_level),
        df=calculate_mini_boss_defense(dungeon_level),
        mg=calculate_mini_boss_magic(dungeon_level),
    )
    boss.is_boss = True  # atributo público, ok fora de entities/
    return boss

