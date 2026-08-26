"""Eventos aleatórios de masmorra (TASK-005).

Sistema simples sorteado ao entrar num andar, antes da decisão de
extração. Probabilidade configurável via RANDOM_EVENT_CHANCE (25%).
"""

from __future__ import annotations

import random

from src.shared.constants import (
    RANDOM_EVENT_ALTAR_BUFF_DURATION,
    RANDOM_EVENT_ALTAR_BUFF_VALUE,
    RANDOM_EVENT_ALTAR_HP_COST_PERCENT,
    RANDOM_EVENT_CHANCE,
    RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT,
    RANDOM_EVENT_MERCHANT_MAX_ITEMS,
    RANDOM_EVENT_MERCHANT_MIN_ITEMS,
)

RANDOM_EVENT_TYPES: tuple[str, ...] = ("merchant", "altar", "fountain")


def roll_random_event(rng: random.Random | None = None) -> str | None:
    """Sorteia se um evento ocorre e qual tipo.

    Returns:
        "merchant", "altar", "fountain" ou None (nenhum evento).
    """
    r = rng if rng is not None else random
    if r.random() >= RANDOM_EVENT_CHANCE:
        return None
    return r.choice(RANDOM_EVENT_TYPES)  # type: ignore[return-value]


def get_merchant_offers(dungeon_level: int, rng: random.Random | None = None) -> list[dict]:
    """Gera 1-3 ofertas para o Mercador Errante.

    Usa o pool da loja mas favorece itens mais raros (Rare/Epic) para
    diferenciar do mercador normal entre andares.
    """
    from src.content.items import get_all_items

    r = rng if rng is not None else random
    all_items = get_all_items()

    # Pool filtrado como na loja normal, mas sem limite de Legendary
    candidates: list[object] = []
    for item in all_items.values():
        if not getattr(item, "sold_in_shop", False):
            continue
        shop_min = getattr(item, "shop_min_floor", 1)
        shop_max = getattr(item, "shop_max_floor", None)
        if dungeon_level < shop_min:
            continue
        if shop_max is not None and dungeon_level > shop_max:
            continue
        candidates.append(item)

    if not candidates:
        return []

    # Favorece raridades maiores: peso 1.0 Common, 1.5 Rare, 2.0 Epic
    weighted: list[object] = []
    for item in candidates:
        rarity = getattr(item, "rarity", "Common")
        weight = {"Common": 1, "Rare": 3, "Epic": 6, "Legendary": 10}.get(rarity, 1)
        weighted.extend([item] * weight)

    count = r.randint(RANDOM_EVENT_MERCHANT_MIN_ITEMS, RANDOM_EVENT_MERCHANT_MAX_ITEMS)
    count = min(count, len(candidates))

    # Amostra sem repetição do pool ponderado, mas garantindo unicidade por nome
    seen: set[str] = set()
    offers: list[dict] = []
    attempts = 0
    while len(offers) < count and attempts < 50:
        item = r.choice(weighted)
        name = getattr(item, "name", str(item))
        if name not in seen:
            seen.add(name)
            # Preço com leve desconto do errante (-10%)
            base_price = getattr(item, "price", 50)
            price = int(base_price * (1 + dungeon_level * 0.05) * 0.9)
            offers.append({"item": item, "price": price})
        attempts += 1

    return offers


def altar_hp_cost(player) -> int:
    """HP a sacrificar no altar (30% da vida máxima)."""
    max_hp = int(getattr(player, "base_hp", player.get_hp()))
    return max(1, int(max_hp * RANDOM_EVENT_ALTAR_HP_COST_PERCENT / 100))


def apply_altar_blessing(player) -> None:
    """Aplica buff do altar: +15 por 5 turnos."""
    player.active_buffs["Benção do Altar"] = {
        "value": RANDOM_EVENT_ALTAR_BUFF_VALUE,
        "duration": RANDOM_EVENT_ALTAR_BUFF_DURATION,
    }


def fountain_heal_amount(player) -> int:
    """Quanto a fonte cura (50% da vida máxima)."""
    max_hp = int(getattr(player, "base_hp", player.get_hp()))
    return max(1, int(max_hp * RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT / 100))


def apply_fountain_heal(player) -> int:
    """Cura o jogador e tenta recuperar 1 poção. Retorna HP curado."""
    heal = fountain_heal_amount(player)
    before = player.get_hp()
    player.heal(heal)
    after = player.get_hp()
    healed = after - before

    # Tenta recuperar 1 poção aleatória se o inventário não estiver lotado
    # (simples: adiciona Poção de Cura Pequena se existir no registro)
    try:
        from src.content.items import get_all_items

        all_items = get_all_items()
        potion = all_items.get("Poção de Cura Pequena") or all_items.get("Potion")
        if potion and len(player.inventory) < 20:
            player.add_item_to_inventory(potion)
    except Exception:
        pass

    return healed
