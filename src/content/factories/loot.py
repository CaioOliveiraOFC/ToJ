from __future__ import annotations

import copy
import random
from typing import Any

from src.content.items import Armor, Item, Potion, Weapon
from src.data.loader import load_items_data


def _get_items_data() -> dict[str, Any]:
    """Carrega e retorna os dados de itens do JSON."""
    return load_items_data()


def _build_loot_table() -> list[Item]:
    """Constrói a tabela de loot a partir dos dados JSON."""
    data = _get_items_data()
    items_data = data["items"]

    loot_table: list[Item] = []

    for weapon in items_data["weapons"]:
        rarity = weapon["rarity"]
        item = Weapon(
            name=weapon["name"],
            description=weapon["description"],
            base_damage=weapon["base_damage"],
            rarity=rarity,
        )
        loot_table.append(item)

    for armor in items_data["armors"]:
        rarity = armor["rarity"]
        item = Armor(
            name=armor["name"],
            description=armor["description"],
            base_defense=armor["base_defense"],
            slot=armor["slot"],
            rarity=rarity,
        )
        loot_table.append(item)

    for potion in items_data["potions"]:
        rarity = potion["rarity"]
        item = Potion(
            name=potion["name"],
            description=potion["description"],
            base_effect_value=potion["base_effect_value"],
            potion_type=potion["potion_type"],
            rarity=rarity,
        )
        loot_table.append(item)

    return loot_table


# Cache da tabela de loot para evitar recarregar o JSON a cada chamada
_LOOT_TABLE: list[Item] | None = None


def get_loot() -> Item | None:
    """
    Gerador procedural que lê definições do JSON.

    Mantém o mesmo comportamento: chance configurável de dropar um item (cópia).
    O código Python atua como injetor, instanciando objetos a partir dos dados JSON.
    """
    global _LOOT_TABLE

    if _LOOT_TABLE is None:
        _LOOT_TABLE = _build_loot_table()

    data = _get_items_data()
    drop_chance = data.get("drop_chance_percent", 30)

    if random.randint(1, 100) <= drop_chance:
        return copy.copy(random.choice(_LOOT_TABLE))
    return None

