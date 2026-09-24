"""Fluxo de interação da loja (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.economy import buy_recovery, recovery_offers
from src.ui import screens
from src.ui.navigation_menu import (
    equipar_escolhendo_posicao,
    navigate_shop_buy,
    navigate_shop_sell,
)
from src.ui.prompts import get_key

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
    """Orquestra o fluxo completo da loja.

    A VISITA é criada aqui, uma vez, e o estoque dela vale até o jogador sair.
    Era gerado a cada entrada na tela de compra, então sair e voltar rerrolava a
    loja de graça — e um reroll pago ao lado de um gratuito não é decisão
    nenhuma. Sair e voltar ao andar seguinte continua dando estoque novo, porque
    é uma visita nova; o contador de rerolls morre junto com esta.
    """
    visita = shop.visit(dungeon_level, player.get_classname())

    while True:
        has_equipable = _has_equipable_in_inventory(player)
        opcoes: dict[str, str] = {"1": "Comprar Itens", "2": "Vender Itens"}
        if has_equipable:
            opcoes[str(len(opcoes) + 1)] = "Equipar da Mochila"
        opcoes[str(len(opcoes) + 1)] = "Recuperar Vida/Mana"
        # O preço do próximo reroll fica na própria opção: o jogador precisa ver
        # 150 virar 300 virar 600 e decidir mesmo assim apertar de novo.
        opcoes[str(len(opcoes) + 1)] = f"Renovar Estoque — {visita.next_reroll_cost} ouro"
        opcoes[str(len(opcoes) + 1)] = "Sair da Loja"

        acoes = list(opcoes)
        screens.render_shop_main(opcoes, player.coins)

        choice = get_key()
        if choice and choice.lower() == "q":
            screens.render_shop_farewell()
            break
        if choice not in acoes:
            continue

        rotulo = opcoes[choice]
        if rotulo == "Comprar Itens":
            _run_buy_flow(player, visita, dungeon_level)
        elif rotulo == "Vender Itens":
            _run_sell_flow(player, shop, dungeon_level)
        elif rotulo == "Equipar da Mochila":
            _run_equip_in_shop_flow(player, shop, dungeon_level)
        elif rotulo == "Recuperar Vida/Mana":
            _run_recovery_flow(player, dungeon_level)
        elif rotulo.startswith("Renovar Estoque"):
            custo = visita.next_reroll_cost
            if visita.reroll(player):
                screens.render_shop_reroll_success(custo, visita.next_reroll_cost)
            else:
                screens.render_shop_reroll_denied(custo, player.coins)
        else:
            screens.render_shop_farewell()
            break


def _run_recovery_flow(player: "Player", dungeon_level: int) -> None:
    """Compra de recuperação entre andares.

    O descanso de fim de andar continua gratuito e parcial; isto é o resto. É o
    que faz um combate mal jogado ter consequência econômica em vez de ser
    apagado de graça — e é a terceira opção concorrendo pelo mesmo ouro que
    equipamento e poção.
    """
    while True:
        ofertas = recovery_offers(player, dungeon_level)
        screens.render_recovery_menu(
            ofertas,
            player.coins,
            player.get_hp(),
            int(player.base_hp),
            player.get_mp(),
            int(player.base_mp),
        )
        if not ofertas:
            get_key()
            return

        validas = [str(i) for i in range(1, len(ofertas) + 1)] + ["0"]
        escolha = get_key()
        if escolha not in validas or escolha == "0":
            return

        oferta = ofertas[int(escolha) - 1]
        paga = buy_recovery(player, dungeon_level, oferta["resource"])
        if paga is None:
            screens.render_shop_insufficient_gold()
        else:
            screens.render_recovery_success(paga["label"], paga["amount"], paga["price"])


def _run_buy_flow(player: "Player", visita, dungeon_level: int) -> None:
    """Fluxo de compra de itens usando menu navegável.

    O estoque é o da VISITA: entrar e sair desta tela não sorteia nada.
    """
    shop = visita.shop
    items_for_sale = visita.stock

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
                old_item = player.occupant_for(item_to_buy)
            if shop.buy_item(player, item_to_buy, dungeon_level):
                screens.render_shop_purchase_success(item_to_buy.display_name, price)
                # Sai da vitrine desta visita. Comprar não rerrola o resto.
                visita.take(selected_idx)
                # Oferece equipar diretamente na loja — com comparativo e opção de vender o antigo
                if slot and hasattr(player, "equipment"):
                    if old_item is None:
                        bonus_text = _bonus_text(item_to_buy)
                        screens.render_shop_equip_prompt(item_to_buy.display_name, slot, bonus_text)
                        equip_choice = get_key()
                        if equip_choice and equip_choice.lower() in ("s", "y", "1", "e"):
                            msg = equipar_escolhendo_posicao(player, item_to_buy)
                            if item_to_buy in player.equipment.values():
                                screens.render_shop_equip_success(item_to_buy.display_name, slot)
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
                            msg = equipar_escolhendo_posicao(player, item_to_buy)
                            if item_to_buy in player.equipment.values():
                                screens.render_shop_equip_success(item_to_buy.display_name, slot)
                                # old_item agora está no inventário — oferece
                                # vender ou descartar sem sair da loja
                                sell_price = shop.get_sell_price(old_item, dungeon_level)
                                screens.render_shop_old_sell_prompt(
                                    old_item.display_name, sell_price, slot
                                )
                                sell_choice = get_key()
                                if sell_choice and sell_choice.lower() in ("s", "y", "1"):
                                    # vender
                                    if old_item in player.inventory:
                                        if shop.sell_item(player, old_item, dungeon_level):
                                            screens.render_shop_sell_success(
                                                old_item.display_name, sell_price
                                            )
                                        else:
                                            screens.render_shop_equip_failed(
                                                "Falha ao vender item antigo"
                                            )
                                    else:
                                        screens.render_shop_equip_failed(
                                            "Item antigo não encontrado no inventário"
                                        )
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

    # `navigate_shop_sell` é reaproveitado como SELETOR, e não como venda: ele já
    # lista peça por peça com preço, que é a informação que interessa também na
    # hora de equipar. Um navegador próprio para isto seria um quarto navegador
    # com o mesmo corpo.
    while True:
        if not equipables:
            screens.render_shop_equip_inventory_empty()
            break
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
        old_item = player.occupant_for(item_to_equip) if slot else None
        if old_item is None:
            bonus_text = _bonus_text(item_to_equip)
            screens.render_shop_equip_prompt(item_to_equip.display_name, slot, bonus_text)
            choice = get_key()
            if choice and choice.lower() in ("s", "y", "1", "e"):
                msg = equipar_escolhendo_posicao(player, item_to_equip)
                if item_to_equip in player.equipment.values():
                    screens.render_shop_equip_success(item_to_equip.display_name, slot)
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
                    msg = equipar_escolhendo_posicao(player, item_to_equip)
                    if item_to_equip in player.equipment.values():
                        screens.render_shop_equip_success(item_to_equip.display_name, slot)
                        sell_price = shop.get_sell_price(old_item, dungeon_level)
                        screens.render_shop_old_sell_prompt(old_item.display_name, sell_price, slot)
                        sell_choice = get_key()
                        if sell_choice and sell_choice.lower() in ("s", "y", "1"):
                            if old_item in player.inventory:
                                if shop.sell_item(player, old_item, dungeon_level):
                                    screens.render_shop_sell_success(
                                        old_item.display_name, sell_price
                                    )
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

        # O preço tem de ser lido ANTES da venda: depois, o item já saiu do
        # inventário. A versão anterior recalculava do preço-base do JSON, sem
        # o andar e com um `0.5` próprio, então a tela anunciava um valor e o
        # saldo recebia outro.
        sell_price = shop.get_sell_price(item_to_sell, dungeon_level)
        if shop.sell_item(player, item_to_sell, dungeon_level):
            screens.render_shop_sell_success(item_to_sell.display_name, sell_price)
