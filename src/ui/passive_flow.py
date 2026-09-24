"""Fluxo de interação de seleção de passivas (orquestração UI → player)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content import level_up
from src.content.economy import reroll_cost
from src.content.passives import generate_passive_choices
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.content.passives import PassiveCard
    from src.entities.heroes import Player


def run_passive_selection_flow(
    player: "Player", choices: list["PassiveCard"], dungeon_level: int = 1
) -> None:
    """Exibe 3 cartas de passivas, com reroll pago, e aplica a escolha.

    Segue o padrão de inventory_flow.py:
    - A UI renderiza, o fluxo orquestra, a entidade aplica.
    - Não retorna nada; muta o estado do player via player.add_passive().

    O reroll aqui só compra OUTRA AMOSTRA: a distribuição por raridade continua
    a mesma, e não existe `seen_passive_ids` — passiva repetida é regra do
    catálogo, e o reroll não a altera.
    """
    rerolls = 0

    while True:
        custo = reroll_cost(dungeon_level, rerolls)
        screens.render_passive_selection(choices, reroll_cost=custo, coins=player.coins)
        choice = safe_get_key(valid_keys=["1", "2", "3", "r", "R"])

        if choice and choice.lower() == "r":
            if not player.spend_coins(custo, source="passive_reroll"):
                screens.render_offer_reroll_denied(custo, player.coins)
                continue
            choices = generate_passive_choices(count=len(choices))
            rerolls += 1
            continue

        if choice and choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(choices):
                # Aplicar pela MESMA função que o bot usa: escolher é do
                # jogador, aplicar é do jogo.
                msg = level_up.aplicar_passiva(player, choices[index])
                screens.render_passive_acquired(msg)
                return
