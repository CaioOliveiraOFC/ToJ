from __future__ import annotations

import random
from typing import Any

from src.content.items import Item, create_item_from_json
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

        # Constrói pelo MESMO caminho da loja. A cópia manual daqui omitia
        # `consumable`, então as 14 poções e elixires do jogo caíam do monstro
        # com `consumable=False`: `is_potion` dava falso e o item não aparecia
        # no menu de itens do combate. Poção achada em loot era poção morta.
        loot_table.append(create_item_from_json(item_data))

    _POR_RARIDADE.clear()
    for item in loot_table:
        raridade = str(getattr(item, "rarity", "Common"))
        _POR_RARIDADE[raridade] = _POR_RARIDADE.get(raridade, 0) + 1

    return loot_table


# Usados só quando o JSON não declara os seus. Ficam aqui para o sorteio nunca
# silenciosamente virar uniforme de novo se a chave sumir do arquivo.
DEFAULT_DROP_CHANCE_PERCENT = 30
DEFAULT_RARITY_WEIGHTS = {"Common": 60, "Rare": 28, "Epic": 10, "Legendary": 2}

# Cache da tabela de loot para evitar recarregar o JSON a cada chamada
_LOOT_TABLE: list[Item] | None = None
# Quantos itens existem em cada raridade. O peso da raridade é dividido por esta
# contagem, senão a raridade com mais itens no catálogo levaria a fatia dela
# multiplicada pelo número de itens — que é exatamente o defeito do sorteio
# uniforme, só que disfarçado de sorteio ponderado.
_POR_RARIDADE: dict[str, int] = {}


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
    drop_chance = data.get("drop_chance_percent", DEFAULT_DROP_CHANCE_PERCENT)

    if random.randint(1, 100) > drop_chance:
        return None

    # Sorteio ponderado por raridade. Era `random.choice` uniforme sobre a tabela
    # inteira, e como o catálogo tem 71 Common contra 8 Legendary, a raridade
    # efetiva do drop era só a contagem de itens de cada tipo no JSON — um
    # Legendary novo mudava a economia do jogo sem ninguém decidir isso.
    #
    # Os pesos já estavam em `items.json` (`rarity_weights`), declarados e nunca
    # lidos. Ficam fixos de propósito: o jogo é infinito e como a raridade deve
    # se comportar em profundidade alta ainda não foi decidido, então NÃO existe
    # escala por andar aqui. Andar 30 sorteia igual ao andar 1.
    pesos = data.get("rarity_weights", DEFAULT_RARITY_WEIGHTS)
    peso_por_item = [
        float(pesos.get(getattr(item, "rarity", "Common"), 0))
        / max(1, _POR_RARIDADE.get(getattr(item, "rarity", "Common"), 1))
        for item in _LOOT_TABLE
    ]
    if not any(peso_por_item):
        return random.choice(_LOOT_TABLE).spawn()
    # `.spawn()` e não `copy.copy`: o drop é um exemplar novo, e é aqui que os
    # sockets dele são sorteados pela raridade.
    return random.choices(_LOOT_TABLE, weights=peso_por_item, k=1)[0].spawn()


def reload_loot_table() -> None:
    """Recarrega a tabela de loot (útil para desenvolvimento)."""
    global _LOOT_TABLE
    _LOOT_TABLE = None
    _build_loot_table()
