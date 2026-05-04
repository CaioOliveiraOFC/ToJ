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