"""Fluxos de eventos aleatórios (TASK-005) — UI bloqueante chamada via EventBus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.factories.dungeons import (
    altar_hp_cost,
    apply_altar_blessing,
    apply_fountain_heal,
    fountain_heal_amount,
    get_merchant_offers,
)
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_merchant_event(player: "Player", dungeon_level: int) -> None:
    """Mercador Errante: 1-3 itens raros com desconto, compra opcional."""
    offers = get_merchant_offers(dungeon_level)
    if not offers:
        return

    while offers:
        screens.render_merchant_event(offers, player.coins)
        valid = [str(i) for i in range(1, len(offers) + 1)] + ["0"]
        choice = safe_get_key(valid_keys=valid)

        if choice is None or choice == "0":
            break

        idx = int(choice) - 1
        if 0 <= idx < len(offers):
            entry = offers[idx]
            price = entry["price"]
            item = entry["item"]
            if player.coins >= price:
                player.spend_coins(price)
                player.add_item_to_inventory(item)
                screens.render_merchant_purchase_success(getattr(item, "name", "?"), price)
                offers.pop(idx)
                if not offers:
                    break
            else:
                screens.render_shop_insufficient_gold()
        else:
            screens.render_shop_invalid_choice()


def run_altar_event(player: "Player") -> None:
    """Altar: sacrifica HP por buff temporário."""
    cost = altar_hp_cost(player)
    screens.render_altar_event(cost, player.get_hp(), getattr(player, "base_hp", player.get_hp()))

    # Impede sacrifício suicida
    if player.get_hp() <= cost:
        screens.render_altar_no_hp()
        return

    choice = safe_get_key(valid_keys=["1", "2"])
    if choice == "1":
        player.take_damage(cost)
        if player.get_hp() <= 0:
            player.set_isalive(False)
        apply_altar_blessing(player)
        screens.render_altar_success()
    else:
        screens.render_altar_refused()


def run_fountain_event(player: "Player") -> None:
    """Fonte: cura parcial + 1 poção, sem custo."""
    heal = fountain_heal_amount(player)
    screens.render_fountain_event(
        heal, player.get_hp(), getattr(player, "base_hp", player.get_hp())
    )

    choice = safe_get_key(valid_keys=["1", "2"])
    if choice == "1":
        # Snapshot antes para detectar poção adicionada
        inv_before = len(player.inventory)
        healed = apply_fountain_heal(player)
        potion_name = None
        if len(player.inventory) > inv_before:
            last = player.inventory[-1]
            if getattr(last, "is_potion", False):
                potion_name = getattr(last, "name", None)
        screens.render_fountain_healed(healed, potion_name)
    else:
        screens.render_fountain_ignored()


def run_random_event(player: "Player", dungeon_level: int, event_type: str) -> None:
    """Dispatcher para o tipo sorteado."""
    if event_type == "merchant":
        run_merchant_event(player, dungeon_level)
    elif event_type == "altar":
        run_altar_event(player)
    elif event_type == "fountain":
        run_fountain_event(player)
