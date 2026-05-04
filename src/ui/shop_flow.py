"""Fluxo de interação da loja (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.navigation_menu import navigate_shop_buy, navigate_shop_sell

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_shop_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Orquestra o fluxo completo da loja."""

    while True:
        screens.render_shop_main(shop, player.coins)

        from src.ui.prompts import get_key
        choice = get_key()

        if choice == "1":
            _run_buy_flow(player, shop, dungeon_level)
        elif choice == "2":
            _run_sell_flow(player, shop, dungeon_level)
        elif choice == "3" or choice.lower() == "q":
            screens.render_shop_farewell()
            break


def _run_buy_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Fluxo de compra de itens usando menu navegável."""
    player_class = player.get_classname()
    items_for_sale = shop.get_available_items(dungeon_level, player_class)

    if not items_for_sale:
        return

    while True:
        if not items_for_sale:
            break
            
        selected_idx = navigate_shop_buy(items_for_sale, player.coins, player)

        if selected_idx is None:
            break

        chosen_item_data = items_for_sale[selected_idx]
        item_to_buy = chosen_item_data["item"]
        price = chosen_item_data["price"]

        if player.coins >= price:
            if shop.buy_item(player, item_to_buy, dungeon_level):
                screens.render_shop_purchase_success(item_to_buy.name, price)
                # Remove o item da lista (não rerrola, mantém os outros)
                items_for_sale.pop(selected_idx)
        else:
            screens.render_shop_insufficient_gold()


def _run_sell_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Fluxo de venda de itens usando menu navegável."""
    if not player.inventory:
        return

    while True:
        selected_idx = navigate_shop_sell(player.inventory, player.coins)

        if selected_idx is None:
            break

        item_to_sell = player.inventory[selected_idx]

        if shop.sell_item(player, item_to_sell, dungeon_level):
            from src.content.items import get_all_items
            all_items = get_all_items()
            base_item = all_items.get(item_to_sell.name)
            sell_price = int(base_item.price * 0.5) if base_item else 10
            screens.render_shop_sell_success(item_to_sell.name, sell_price)