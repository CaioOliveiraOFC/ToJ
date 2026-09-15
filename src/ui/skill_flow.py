"""Fluxo de interação de seleção de skills (orquestração UI → player)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.economy import reroll_cost
from src.content.skills_loader import generate_skill_choices
from src.shared.constants import SKILL_OFFER_SIZE
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.content.skills_loader import SkillCard
    from src.entities.heroes import Player


def run_skill_selection_flow(
    player: "Player",
    choices: list["SkillCard"],
    dungeon_level: int = 1,
    offer_level: int | None = None,
) -> "SkillCard | None":
    """Exibe 3 cartas de skill, com reroll pago, e devolve a escolha.

    O contador de rerolls é LOCAL a esta oferta: ele nasce aqui e morre quando a
    função retorna. Escolher ou recusar encerra a oferta, e a próxima começa de
    novo em 15% da renda do andar — sem nenhuma regra de "resetar" que alguém
    possa esquecer de chamar.

    Returns:
        A skill escolhida ou None se cancelado.
    """
    nivel = int(offer_level if offer_level is not None else player.get_level())
    rerolls = 0

    while True:
        custo = reroll_cost(dungeon_level, rerolls)
        screens.render_skill_selection(choices, player, reroll_cost=custo, coins=player.coins)
        choice = safe_get_key(valid_keys=["1", "2", "3", "0", "r", "R"])

        if choice == "0":
            return None

        if choice and choice.lower() == "r":
            if not player.spend_coins(custo, source="skill_reroll"):
                screens.render_offer_reroll_denied(custo, player.coins)
                continue
            choices = generate_skill_choices(
                player.get_classname(),
                nivel,
                player.active_skill_ids(),
                count=SKILL_OFFER_SIZE,
                seen_ids=player.seen_skill_ids,
            )
            # Ver já é conhecer: as descartadas entraram em `seen_skill_ids` ao
            # serem geradas, e as novas entram agora. Sem isto, o reroll seguinte
            # devolveria as mesmas cartas que o jogador acabou de recusar.
            player.seen_skill_ids.update(c.id for c in choices)
            rerolls += 1
            continue

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
