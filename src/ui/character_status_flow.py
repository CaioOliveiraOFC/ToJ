"""Fluxo de Status do Personagem (orquestração engine → UI via prompts)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.prompts import get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_character_status_flow(player: "Player") -> None:
    """Mostra a tela consolidada de status do personagem.

    Segue o mesmo padrão dos outros flows (inventory_flow, shop_flow):
    loop bloqueante que renderiza e aguarda input, sem acoplar engine.
    """
    while True:
        screens.render_character_status(player)
        key = get_key()
        if key is None or key.lower() == "q":
            break
        # Qualquer outra tecla apenas recarrega a tela (útil para ver cooldowns/effects atualizados)
        # Continua no loop para re-renderizar
