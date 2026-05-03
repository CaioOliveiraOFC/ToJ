"""Fluxo de interação de seleção de passivas (orquestração UI → player)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.content.passives import PassiveCard
    from src.entities.heroes import Player


def run_passive_selection_flow(player: "Player", choices: list["PassiveCard"]) -> None:
    """Exibe 3 cartas de passivas e aplica a escolha do jogador.

    Segue o padrão de inventory_flow.py:
    - A UI renderiza, o fluxo orquestra, a entidade aplica.
    - Não retorna nada; muta o estado do player via player.add_passive().
    """
    while True:
        screens.render_passive_selection(choices)
        choice = safe_get_key(valid_keys=["1", "2", "3"])
        if choice and choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(choices):
                msg = player.add_passive(choices[index])
                screens.render_passive_acquired(msg)
                return
