"""Fluxo de interação da loja (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.navigation_menu import navigate_shop_buy, navigate_shop_sell
from src.ui.prompts import get_key
from src.content.items import get_all_items

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_shop_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Orquestra o fluxo completo da loja."""

    while True:
        screens.render_shop_main(shop, player.coins)

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
            # Verifica se slot está vazio antes da compra para oferecer equipar
            slot = getattr(item_to_buy, "slot", None)
            was_empty = False
            if slot and hasattr(player, "equipment"):
                was_empty = player.equipment.get(slot) is None
            if shop.buy_item(player, item_to_buy, dungeon_level):
                screens.render_shop_purchase_success(item_to_buy.name, price)
                # Remove o item da lista (não rerrola, mantém os outros)
                items_for_sale.pop(selected_idx)
                # Oferece equipar diretamente se slot estava vazio — puro benefício
                if was_empty and slot:
                    # Mostra detalhe do benefício antes de perguntar
                    bonus_dmg = getattr(item_to_buy, "damage_bonus", 0)
                    bonus_def = getattr(item_to_buy, "defense_bonus", 0)
                    bonus_str = []
                    if bonus_dmg:
                        bonus_str.append(f"+{bonus_dmg} Dano")
                    if bonus_def:
                        bonus_str.append(f"+{bonus_def} Defesa")
                    effect = getattr(item_to_buy, "effect_type", None)
                    eff_val = getattr(item_to_buy, "effect_value", 0)
                    if effect and eff_val:
                        bonus_str.append(f"{effect} +{eff_val}")
                    bonus_text = ", ".join(bonus_str) if bonus_str else "benefícios"
                    screens.render_shop_equip_prompt(item_to_buy.name, slot, bonus_text)
                    equip_choice = get_key()
                    if equip_choice and equip_choice.lower() in ("s", "y", "1", "e"):
                        msg = player.equip(item_to_buy)
                        if "não pode" not in str(msg).lower():
                            screens.render_shop_equip_success(item_to_buy.name, slot)
                        else:
                            screens.render_shop_equip_failed(msg)
                    else:
                        screens.render_shop_kept_in_inventory(item_to_buy.name)
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
            all_items = get_all_items()
            base_item = all_items.get(item_to_sell.name)
            sell_price = int(base_item.price * 0.5) if base_item else 10
            screens.render_shop_sell_success(item_to_sell.name, sell_price)