"""Fluxo de interação do inventário (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.navigation_menu import navigate_inventory
from src.ui.prompts import get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_inventory_flow(player: "Player") -> None:
    """Orquestra o fluxo do inventário."""

    while True:
        screens.render_inventory_main(player)

        valid_choices = [str(i) for i in range(len(player.inventory))] + ["0", "esc"]
        choice = get_key()

        if choice == "0" or choice.lower() == "esc":
            break

        try:
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                _run_item_action_flow(player, selected_item)
        except ValueError:
            pass


def run_inventory_flow_v2(player: "Player") -> None:
    """Fluxo do inventário usando menu navegável."""

    while True:
        if not player.inventory:
            screens._render_empty_inventory_message()
            get_key()
            break

        equipped_indices = []
        for slot, equipped_item in player.equipment.items():
            if equipped_item:
                try:
                    idx = player.inventory.index(equipped_item)
                    equipped_indices.append(idx)
                except ValueError:
                    pass

        selected_idx = navigate_inventory(player.inventory, equipped_indices)

        if selected_idx is None:
            break

        selected_item = player.inventory[selected_idx]
        _run_item_action_flow(player, selected_item)


def _run_item_action_flow(player: "Player", item: object) -> None:
    """Fluxo de ações para um item selecionado."""
    from src.content.items import Item
    
    is_equipped = _is_item_equipped(player, item)
    
    is_usable = isinstance(item, Item) and getattr(item, "is_usable", False)
    is_equippable = hasattr(item, "slot")

    while True:
        screens.render_inventory_item_details(item, is_equipped)

        valid_keys = []
        if is_usable:
            valid_keys.append("u")
        if is_equippable:
            valid_keys.append("e")
        valid_keys.extend(["c", "esc"])

        action_choice = get_key()

        if action_choice == "u" and is_usable:
            if isinstance(item, Item):
                msg = player.use_potion(item)
                screens.render_inventory_item_used(msg or getattr(item, "name", "item"))
                break
        elif action_choice == "e" and is_equippable:
            if is_equipped:
                slot = _find_equipped_slot(player, item)
                if slot:
                    msg = player.unequip(slot)
                    screens.render_inventory_item_unequipped(msg or getattr(item, "name", "item"))
            else:
                msg = player.equip(item)
                screens.render_inventory_item_equipped(msg or getattr(item, "name", "item"))
            break
        elif action_choice == "c" or action_choice.lower() == "esc":
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