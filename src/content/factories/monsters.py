from __future__ import annotations

import random

from src.entities.monsters import Monster
from src.mechanics.math_operations import (
    calculate_monster_defense,
    calculate_monster_hp,
    calculate_monster_magic,
    calculate_monster_strength,
 )


def create_monster(nick_name: str, level: int) -> Monster:
    lvl = max(1, int(level))
    return Monster(
        nick_name,
        lvl,
        hp=calculate_monster_hp(lvl),
        st=calculate_monster_strength(lvl),
        df=calculate_monster_defense(lvl),
        mg=calculate_monster_magic(lvl),
    )


def generate_monsters_for_level(dungeon_level: int) -> list[Monster]:
    """
    Gerador procedural (migrado de `src/engine/game_logic.py`).

    Importante: este módulo existe para centralizar a geração de conteúdo.
    A lógica antiga continua existindo onde estava; esta é a versão equivalente.
    """

    monsters: list[Monster] = []

    base_num_monsters = 2
    num_monsters_scaling = dungeon_level // 3
    num_monsters = max(1, base_num_monsters + num_monsters_scaling)

    monster_types: dict[str, list[str]] = {
        "common": ["Goblin", "Orc", "Esqueleto", "Zumbi"],
        "uncommon": ["Aranha Gigante", "Lobo Mal", "Serpente Venenosa"],
        "rare": ["Minotauro", "Gárgula", "Cavaleiro Corrompido"],
        "boss": ["Dragão Jovem", "Lich Menor"],
    }

    for _ in range(num_monsters):
        monster_level = max(1, dungeon_level + random.randint(-2, 3))

        if dungeon_level < 5:
            chosen_type = random.choice(monster_types["common"])
        elif 5 <= dungeon_level < 10:
            chosen_type = random.choice(monster_types["common"] + monster_types["uncommon"])
        elif 10 <= dungeon_level < 20:
            chosen_type = random.choice(monster_types["uncommon"] + monster_types["rare"])
        else:
            if random.random() < 0.1 and dungeon_level > 20:
                chosen_type = random.choice(monster_types["boss"])
                monster_level += 5
            else:
                chosen_type = random.choice(monster_types["rare"])

        monster_name = f"{chosen_type} Nv.{monster_level}"
        monsters.append(create_monster(monster_name, monster_level))

    return monsters

