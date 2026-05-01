"""Fluxo de interação do inventário (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.items import Armor, Potion, Weapon
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_inventory_flow(player: "Player") -> None:
    """
    Orquestra o fluxo completo do inventário.
    Separa a lógica de interação (engine) da renderização (ui/screens).
    """
    while True:
        screens.render_inventory_main(player)

        valid_choices = ["x"] + [str(i + 1) for i in range(len(player.inventory))]
        choice = safe_get_key(valid_keys=valid_choices)

        if choice == "x":
            break

        if choice and choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                _run_item_action_flow(player, selected_item)


def _run_item_action_flow(player: "Player", item: object) -> None:
    """Fluxo de ações para um item selecionado."""
    while True:
        is_equipped = _is_item_equipped(player, item)
        screens.render_inventory_item_details(item, is_equipped)

        action_options = _build_action_options(item, is_equipped)
        action_choice = safe_get_key(valid_keys=action_options, allow_escape=False)

        if action_choice == "u":
            if isinstance(item, Potion):
                msg = player.use_potion(item)
                screens.render_inventory_item_used(msg or item.name)
                break
        elif action_choice == "e":
            if isinstance(item, (Weapon, Armor)):
                if is_equipped:
                    slot = _find_equipped_slot(player, item)
                    if slot:
                        msg = player.unequip(slot)
                        screens.render_inventory_item_unequipped(msg or item.name)
                else:
                    msg = player.equip(item)
                    screens.render_inventory_item_equipped(msg or item.name)
                break
        elif action_choice == "c":
            break


def _is_item_equipped(player: "Player", item: object) -> bool:
    """Verifica se o item está atualmente equipado."""
    for equipped_item in player.equipment.values():
        if equipped_item == item:
            return True
    return False


def _find_equipped_slot(player: "Player", item: object) -> str | None:
    """Encontra o slot onde o item está equipado."""
    for slot, equipped_item in player.equipment.items():
        if equipped_item == item:
            return slot
    return None


def _build_action_options(item: object, is_equipped: bool) -> list[str]:
    """Constrói a lista de opções de ação disponíveis para o item."""
    options = []

    if isinstance(item, Potion):
        options.append("u")

    if isinstance(item, (Weapon, Armor)):
        options.append("e")

    options.append("c")

    return options
