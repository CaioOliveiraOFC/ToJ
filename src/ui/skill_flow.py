"""Fluxo de interação de seleção de skills (orquestração UI → player)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.content.skills_loader import SkillCard
    from src.entities.heroes import Player


def run_skill_selection_flow(player: "Player", choices: list["SkillCard"]) -> "SkillCard | None":
    """Exibe 3 cartas de skill e retorna a escolha do jogador.

    Returns:
        A skill escolhida ou None se cancelado.
    """
    while True:
        screens.render_skill_selection(choices)
        choice = safe_get_key(valid_keys=["1", "2", "3", "0"])
        if choice == "0":
            return None
        if choice and choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(choices):
                return choices[index]


def run_skill_selection_with_replacement(player: "Player", new_skill: "SkillCard") -> None:
    """Exibe nova skill e pede para escolher qual das 4 atuais substituir.

    Se o jogador escolher 0, cancela a substituição.
    """
    while True:
        screens.render_skill_replacement_choice(player, new_skill)
        # Apenas as 4 primeiras skills (chaves 1-4)
        valid_keys = [str(k) for k in sorted(player.skills.keys()) if k <= 4] + ["0"]
        choice = safe_get_key(valid_keys=valid_keys)
        if choice == "0":
            screens.render_skill_not_replaced()
            return
        if choice and choice.isdigit():
            replace_key = int(choice)
            if replace_key in player.skills:
                msg = player.add_skill_with_replacement(new_skill, replace_key)
                screens.render_skill_acquired(msg)
                return
