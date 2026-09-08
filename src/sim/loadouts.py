"""Equipamento e passivas típicas por nível, para a simulação.

Medir com o herói pelado superestima a dificuldade; medir com o melhor
equipamento do jogo a subestima. O jogador real está no meio, e é esse meio que
a curva de dificuldade precisa mirar. Os três cenários abaixo são nomeados para
que um resultado sempre diga em qual deles foi medido.
"""

from __future__ import annotations

from src.content.items import get_all_items
from src.content.passives import load_passives


# Quantas passivas o jogador tem no nível N. Ele escolhe uma por nível, então o
# "esperado" é praticamente o nível menos um.
def expected_passive_count(level: int) -> int:
    return max(0, level - 1)


def _equippable(items, slot: str, hero_class: str):
    return [
        item
        for item in items
        if getattr(item, "slot", None) == slot
        and (not getattr(item, "classes", None) or hero_class in item.classes)
    ]


def _best_for_floor(candidates: list, level: int, cap_ratio: float):
    """Escolhe o item que um jogador daquele nível plausivelmente teria.

    `cap_ratio` limita o quão bom é o item em relação ao melhor do jogo: um
    jogador de nível 5 não anda com equipamento lendário.
    """
    if not candidates:
        return None
    ranked = sorted(
        candidates,
        key=lambda i: getattr(i, "damage_bonus", 0) + getattr(i, "defense_bonus", 0),
    )
    index = min(len(ranked) - 1, int(len(ranked) * cap_ratio))
    return ranked[index]


def apply_loadout(hero, loadout: str, level: int) -> None:
    """Aplica equipamento e passivas ao herói recém-construído.

    Loadouts:
        naked    — nada. Isola a contribuição dos atributos base.
        expected — o que um jogador daquele nível teria. É o cenário de referência.
        best     — o teto: melhor item por slot. Detecta build degenerada.
    """
    if loadout == "naked":
        return

    if loadout not in ("expected", "best"):
        raise ValueError(f"Loadout desconhecido: {loadout!r}. Use naked, expected ou best.")

    items = list(get_all_items().values())
    hero_class = hero.get_classname()
    cap_ratio = 0.99 if loadout == "best" else min(0.85, 0.25 + level * 0.03)

    for slot in ("Weapon", "Helmet", "Body", "Legs", "Shoes", "Hands", "Amulet", "Ring"):
        chosen = _best_for_floor(_equippable(items, slot, hero_class), level, cap_ratio)
        if chosen is not None:
            hero.add_item_to_inventory(chosen)
            hero.equip(chosen)

    # Poções de cura: o recurso que dá sentido ao atrito. Sem elas, medir um
    # andar inteiro sem cura mede um jogo que ninguém joga.
    potions = [
        item
        for item in items
        if getattr(item, "effect_type", None) == "max_hp" and getattr(item, "slot", None) is None
    ]
    if potions:
        best_potion = max(potions, key=lambda i: getattr(i, "effect_value", 0))
        for _ in range(3 if loadout == "expected" else 5):
            hero.add_item_to_inventory(best_potion)

    passives = load_passives()
    if passives:
        commons = [p for p in passives if p.rarity == "Common"] or passives
        for index in range(expected_passive_count(level)):
            hero.add_passive_load(commons[index % len(commons)])
