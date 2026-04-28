from __future__ import annotations

import copy
import random

from src.content.items import ALL_ITEMS


_LOOT_TABLE = list(ALL_ITEMS.values())


def get_loot():
    """
    Gerador procedural (migrado de `src/content/items.py`).

    Mantém o mesmo comportamento: 30% de chance de dropar um item (cópia).
    """

    if random.randint(1, 100) <= 30:
        return copy.copy(random.choice(_LOOT_TABLE))
    return None

