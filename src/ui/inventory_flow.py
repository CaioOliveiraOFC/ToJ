"""Fluxo de interação do inventário (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui.navigation_menu import navigate_inventory

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_inventory_flow_v2(player: "Player") -> None:
    """Fluxo do inventário usando menu navegável com 3 painéis."""

    while True:
        # Navigate - returns False for ESC, None for action (refresh)
        result = navigate_inventory(player.inventory, player, [])

        if result is False:
            # User pressed ESC - exit inventory
            break

        if result is None:
            # Action was performed (equip/use), inventory changed - continue loop to refresh
            continue


def run_arena_loadout_flow(player: "Player") -> None:
    """O mesmo inventário, na preparação da Arena: só equipar e desequipar.

    A mochila é a do próprio gladiador — a Arena não tem loja nem transferência
    —, e consumível continua listado mas não se usa.
    """
    while navigate_inventory(player.inventory, player, [], allow_use=False) is not False:
        continue
