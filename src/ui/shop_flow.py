"""Fluxo de interação da loja (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.shop import Shop
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_shop_flow(player: "Player", dungeon_level: int) -> None:
    """
    Orquestra o fluxo completo da loja.
    Separa a lógica de interação (engine) da renderização (ui/screens).
    """
    shop = Shop()

    while True:
        screens.render_shop_main(shop, player.coins)

        choice = safe_get_key(valid_keys=["1", "2", "3"])

        if choice == "1":
            _run_buy_flow(player, shop, dungeon_level)
        elif choice == "2":
            _run_sell_flow(player, shop, dungeon_level)
        elif choice == "3":
            screens.render_shop_farewell()
            break


def _run_buy_flow(player: "Player", shop: Shop, dungeon_level: int) -> None:
    """Fluxo de compra de itens."""
    while True:
        items_for_sale = shop.get_available_items(dungeon_level)
        screens.render_shop_buy_menu(items_for_sale, player.coins)

        if not items_for_sale:
            break

        item_choices = [str(i) for i in range(1, len(items_for_sale) + 1)] + ["0"]
        item_choice = safe_get_key(valid_keys=item_choices)

        if item_choice == "0":
            break

        try:
            chosen_item_id = int(item_choice)
            chosen_item_data = items_for_sale[chosen_item_id - 1]
            item_to_buy = chosen_item_data["item"]
            price = chosen_item_data["price"]

            if player.coins >= price:
                if shop.buy_item(player, item_to_buy, dungeon_level):
                    screens.render_shop_purchase_success(item_to_buy.name, price)
            else:
                screens.render_shop_insufficient_gold()
        except (ValueError, IndexError):
            screens.render_shop_invalid_choice()


def _run_sell_flow(player: "Player", shop: Shop, dungeon_level: int) -> None:
    """Fluxo de venda de itens."""
    while True:
        screens.render_shop_sell_menu(player.inventory, shop, dungeon_level, player.coins)

        if not player.inventory:
            break

        sell_choices = [str(i) for i in range(1, len(player.inventory) + 1)] + ["0"]
        sell_choice = safe_get_key(valid_keys=sell_choices)

        if sell_choice == "0":
            break

        try:
            chosen_item_id = int(sell_choice)
            item_to_sell = player.inventory[chosen_item_id - 1]
            sell_price = int(shop.get_price(item_to_sell, dungeon_level) * 0.5)

            if shop.sell_item(player, item_to_sell, dungeon_level):
                screens.render_shop_sell_success(item_to_sell.name, sell_price)
        except (ValueError, IndexError):
            screens.render_shop_invalid_choice()
