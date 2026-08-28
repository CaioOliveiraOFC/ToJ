"""Fluxo de interação da loja (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.navigation_menu import navigate_shop_buy, navigate_shop_sell
from src.ui.prompts import get_key
from src.content.items import get_all_items

if TYPE_CHECKING:
    from src.entities.heroes import Player


def _has_equipable_in_inventory(player: "Player") -> bool:
    for it in getattr(player, "inventory", []):
        if getattr(it, "slot", None):
            return True
    return False


def _bonus_text(item) -> str:
    bonus_dmg = getattr(item, "damage_bonus", 0)
    bonus_def = getattr(item, "defense_bonus", 0)
    bonus_str = []
    if bonus_dmg:
        bonus_str.append(f"+{bonus_dmg} Dano")
    if bonus_def:
        bonus_str.append(f"+{bonus_def} Defesa")
    effect = getattr(item, "effect_type", None)
    eff_val = getattr(item, "effect_value", 0)
    if effect and eff_val:
        bonus_str.append(f"{effect} +{eff_val}")
    return ", ".join(bonus_str) if bonus_str else "benefícios"


def run_shop_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Orquestra o fluxo completo da loja."""

    while True:
        has_equipable = _has_equipable_in_inventory(player)
        screens.render_shop_main(shop, player.coins, has_equipable)

        choice = get_key()

        if choice == "1":
            _run_buy_flow(player, shop, dungeon_level)
        elif choice == "2":
            _run_sell_flow(player, shop, dungeon_level)
        elif choice == "3":
            if has_equipable:
                _run_equip_in_shop_flow(player, shop, dungeon_level)
            else:
                screens.render_shop_farewell()
                break
        elif choice == "4" or (choice and choice.lower() == "q"):
            screens.render_shop_farewell()
            break
        elif choice and choice.lower() == "q":
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
            slot = getattr(item_to_buy, "slot", None)
            # captura equipado antes da compra para comparativo
            old_item = None
            if slot and hasattr(player, "equipment"):
                old_item = player.equipment.get(slot)
            if shop.buy_item(player, item_to_buy, dungeon_level):
                screens.render_shop_purchase_success(item_to_buy.name, price)
                # Remove o item da lista (não rerrola, mantém os outros)
                items_for_sale.pop(selected_idx)
                # Oferece equipar diretamente na loja — com comparativo e opção de vender o antigo
                if slot and hasattr(player, "equipment"):
                    if old_item is None:
                        bonus_text = _bonus_text(item_to_buy)
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
                        # slot ocupado -> comparação simples + opção de vender/descartar antigo
                        screens.render_shop_swap_comparison(item_to_buy, old_item, slot)
                        equip_choice = get_key()
                        if equip_choice and equip_choice.lower() in ("s", "y", "1", "e"):
                            # tenta equipar; old_item ainda é referência válida
                            msg = player.equip(item_to_buy)
                            if "não pode" not in str(msg).lower():
                                screens.render_shop_equip_success(item_to_buy.name, slot)
                                # old_item agora está no inventário — oferece vender/descartar sem sair da loja
                                sell_price = int(shop.get_price(old_item, dungeon_level) * 0.5)
                                screens.render_shop_old_sell_prompt(old_item.name, sell_price, slot)
                                sell_choice = get_key()
                                if sell_choice and sell_choice.lower() in ("s", "y", "1"):
                                    # vender
                                    if old_item in player.inventory:
                                        if shop.sell_item(player, old_item, dungeon_level):
                                            screens.render_shop_sell_success(old_item.name, sell_price)
                                        else:
                                            screens.render_shop_equip_failed("Falha ao vender item antigo")
                                    else:
                                        screens.render_shop_equip_failed("Item antigo não encontrado no inventário")
                                elif sell_choice and sell_choice.lower() == "d":
                                    if old_item in player.inventory:
                                        player.remove_item_from_inventory(old_item)
                                        screens.render_shop_old_discarded(old_item.name)
                                    else:
                                        screens.render_shop_old_kept(old_item.name)
                                else:
                                    screens.render_shop_old_kept(old_item.name)
                            else:
                                screens.render_shop_equip_failed(msg)
                        else:
                            screens.render_shop_kept_in_inventory(item_to_buy.name)
        else:
            screens.render_shop_insufficient_gold()


def _run_equip_in_shop_flow(player: "Player", shop: object, dungeon_level: int) -> None:
    """Equipar item já na mochila sem sair da loja — com comparativo e venda do antigo."""
    # filtros só equipáveis
    equipables = [it for it in player.inventory if getattr(it, "slot", None)]
    if not equipables:
        screens.render_shop_equip_inventory_empty()
        return

    # Reutiliza navegação de venda mas com desempenho de equipar
    # Para simplicidade, lista com navegação simples e comparativo a cada seleção
    # Usa navigate_shop_sell adaptado? Vamos fazer loop manual com get_key e details via screens
    # Em vez de criar novo navigation, reaproveita navigate_shop_sell para escolher índice
    while True:
        if not equipables:
            screens.render_shop_equip_inventory_empty()
            break
        # Usa o menu de venda como seletor (mostra preço) mas título será equipar — ok para fluxo mínimo
        # Para manter UX coerente, usamos navigate_shop_sell como picker
        selected_idx = navigate_shop_sell(equipables, player.coins)
        if selected_idx is None:
            break
        # map back to actual inventory item (equipables is filtered view)
        item_to_equip = equipables[selected_idx]
        # verifica se item ainda está no inventário (pode ter sido equipado/vendido)
        if item_to_equip not in player.inventory:
            equipables = [it for it in player.inventory if getattr(it, "slot", None)]
            continue
        slot = getattr(item_to_equip, "slot", None)
        old_item = player.equipment.get(slot) if slot else None
        if old_item is None:
            bonus_text = _bonus_text(item_to_equip)
            screens.render_shop_equip_prompt(item_to_equip.name, slot, bonus_text)
            choice = get_key()
            if choice and choice.lower() in ("s", "y", "1", "e"):
                msg = player.equip(item_to_equip)
                if "não pode" not in str(msg).lower():
                    screens.render_shop_equip_success(item_to_equip.name, slot)
                else:
                    screens.render_shop_equip_failed(msg)
            else:
                screens.render_shop_kept_in_inventory(item_to_equip.name)
        else:
            if old_item is item_to_equip:
                # já equipado? não deveria estar no inventário, mas cobre
                screens.render_shop_old_kept(item_to_equip.name)
            else:
                screens.render_shop_swap_comparison(item_to_equip, old_item, slot)
                choice = get_key()
                if choice and choice.lower() in ("s", "y", "1", "e"):
                    msg = player.equip(item_to_equip)
                    if "não pode" not in str(msg).lower():
                        screens.render_shop_equip_success(item_to_equip.name, slot)
                        sell_price = int(shop.get_price(old_item, dungeon_level) * 0.5)
                        screens.render_shop_old_sell_prompt(old_item.name, sell_price, slot)
                        sell_choice = get_key()
                        if sell_choice and sell_choice.lower() in ("s", "y", "1"):
                            if old_item in player.inventory:
                                if shop.sell_item(player, old_item, dungeon_level):
                                    screens.render_shop_sell_success(old_item.name, sell_price)
                                else:
                                    screens.render_shop_equip_failed("Falha ao vender item antigo")
                        elif sell_choice and sell_choice.lower() == "d":
                            if old_item in player.inventory:
                                player.remove_item_from_inventory(old_item)
                                screens.render_shop_old_discarded(old_item.name)
                            else:
                                screens.render_shop_old_kept(old_item.name)
                        else:
                            screens.render_shop_old_kept(old_item.name)
                    else:
                        screens.render_shop_equip_failed(msg)
                else:
                    screens.render_shop_kept_in_inventory(item_to_equip.name)
        # refresh list (pode ter mudado inventário/equip)
        equipables = [it for it in player.inventory if getattr(it, "slot", None)]
        if not equipables:
            break
        # continua no loop da loja — não sai, permite equipar vários sem sair


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
