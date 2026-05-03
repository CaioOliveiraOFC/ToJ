from __future__ import annotations

import copy
import random
from typing import Any

from src.content.items import Item, get_all_items
from src.data.loader import load_items_data


def _get_items_data() -> dict[str, Any]:
    """Carrega e retorna os dados de itens do JSON."""
    return load_items_data()


def _build_loot_table() -> list[Item]:
    """Constrói a tabela de loot a partir dos dados JSON."""
    data = _get_items_data()
    items_list = data.get("items", [])

    loot_table: list[Item] = []

    for item_data in items_list:
        if not item_data.get("droppable", True):
            continue
        
        rarity = item_data.get("rarity", "Common")
        
        item = Item(
            item_id=item_data.get("id", ""),
            name=item_data.get("name", ""),
            description=item_data.get("description", ""),
            rarity=rarity,
            slot=item_data.get("slot", "Body"),
            damage_bonus=item_data.get("damage_bonus", 0),
            defense_bonus=item_data.get("defense_bonus", 0),
            effect_type=item_data.get("effect_type"),
            effect_value=item_data.get("effect_value", 0),
            classes=item_data.get("classes"),
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


def reload_loot_table() -> None:
    """Recarrega a tabela de loot (útil para desenvolvimento)."""
    global _LOOT_TABLE
    _LOOT_TABLE = None
    _build_loot_table()