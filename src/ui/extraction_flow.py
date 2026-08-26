"""Fluxo de decisão de extração entre andares (engine publica, UI decide)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_extraction_prompt(
    player: "Player",
    dungeon_level: int,
    essence_multiplier: float = 1.0,
) -> str:
    """Mostra a tela de extração e retorna 'extract' ou 'continue'.

    Esta função bloqueia até o jogador escolher 1 ou 2.
    """
    screens.render_extraction_prompt(
        player_name=player.get_nick_name(),
        dungeon_level=dungeon_level,
        xp_points=player.xp_points,
        level=player.get_level(),
        hp=player.get_hp(),
        max_hp=getattr(player, "base_hp", player.get_hp()),
        coins=player.coins,
        essence_multiplier=essence_multiplier,
    )
    while True:
        choice = safe_get_key(valid_keys=["1", "2"])
        if choice == "1":
            return "extract"
        if choice == "2":
            return "continue"
