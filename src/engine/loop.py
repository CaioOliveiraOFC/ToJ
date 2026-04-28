"""Orquestração de fluxos de jogo (ex.: combate) — motor de escolhas; UI via EventBus + `screens.render_*` / `prompts`."""

from __future__ import annotations

import random
from time import sleep

from src.content.items import Potion
from src.engine.events import EventBus
from src.mechanics import combat as combat_mech
from src.mechanics.combat import PublishFn
from src.shared import combat_topics as T
from src.shared.types import GameEvent
from src.ui import screens
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.prompts import safe_get_key, wait_enter_to_continue


def _run_human_battle_turn(
    player,
    monster,
    rng: random.Random | None,
    publish: PublishFn,
) -> str | None:
    """
    Motor de escolhas do turno do jogador (sem Rich aqui — só orquestração e teclas).

    Retorna ``\"flee\"`` se a fuga for bem-sucedida; caso contrário ``None``.
    """
    action_taken = False
    while not action_taken:
        screens.render_battle_frame(player, monster)
        screens.render_battle_action_panel()

        choice = safe_get_key(valid_keys=["1", "2", "3", "4"])

        if choice == "1":
            combat_mech.resolve_physical_attack(
                player, monster, player.get_avg_damage(), "", rng=rng, publish=publish
            )
            action_taken = True

        elif choice == "2":
            if not player.skills:
                screens.render_battle_no_skills_message()
                sleep(1)
                continue

            while True:
                screens.render_battle_frame(player, monster)
                screens.render_skill_select_panel(player)

                skill_keys = [str(k) for k in player.skills.keys()] + ["0"]
                skill_choice = safe_get_key(skill_keys)

                if skill_choice == "0":
                    break

                if skill_choice and skill_choice.isdigit() and int(skill_choice) in player.skills:
                    chosen_skill = player.skills[int(skill_choice)]
                    if player.get_mp() < chosen_skill.mana_cost:
                        screens.render_battle_insufficient_mana_message()
                        sleep(1)
                        continue

                    combat_mech.apply_skill(player, monster, chosen_skill, rng=rng, publish=publish)
                    action_taken = True
                    break

        elif choice == "3":
            potions = [item for item in player.inventory if isinstance(item, Potion)]
            if not potions:
                screens.render_battle_no_potions_message()
                sleep(1)
                continue

            while True:
                screens.render_battle_frame(player, monster)
                screens.render_potion_select_panel(potions)

                potion_keys = [str(i) for i in range(1, len(potions) + 1)] + ["0"]
                potion_choice = safe_get_key(potion_keys)

                if potion_choice == "0":
                    break

                if potion_choice and potion_choice.isdigit():
                    if 0 < int(potion_choice) <= len(potions):
                        player.use_potion(potions[int(potion_choice) - 1])
                        action_taken = True
                        sleep(1.5)
                        break

                    screens.render_battle_invalid_potion_message()
                    sleep(1)

        elif choice == "4":
            if combat_mech.roll_flee_success(rng=rng):
                if publish:
                    publish(
                        T.COMBAT_FLEE_RESULT,
                        GameEvent(type="flee_result", payload={"success": True}, source="engine.loop"),
                    )
                player.rest()
                return "flee"
            if publish:
                publish(
                    T.COMBAT_FLEE_RESULT,
                    GameEvent(type="flee_result", payload={"success": False}, source="engine.loop"),
                )
            action_taken = True

    return None


def run_fight(player, monster, rng: random.Random | None = None) -> None:
    """Loop principal de batalha: mecânica publica eventos; UI reage via inscrições no bus."""
    rng = rng or random.Random()
    bus = EventBus()
    cleanup_ui = register_combat_ui_handlers(bus)
    publish = bus.publish

    try:
        screens.render_fight_intro(player, monster)
        wait_enter_to_continue()

        turn_order = [player, monster]
        if player.get_ag() < monster.get_ag():
            turn_order = [monster, player]

        attacker_index = 0

        while player.get_isalive() and monster.get_isalive():
            attacker = turn_order[attacker_index]
            defender = turn_order[(attacker_index + 1) % 2]

            screens.render_battle_frame(player, monster)
            screens.render_turn_banner(attacker)

            skip_turn = combat_mech.process_turn_start_effects(attacker, rng=rng, publish=publish)
            if skip_turn:
                attacker_index = (attacker_index + 1) % 2
                continue

            if attacker.my_type() == "Human":
                outcome = _run_human_battle_turn(player, monster, rng, publish)
                if outcome == "flee":
                    return
            else:
                screens.render_battle_frame(player, monster)
                combat_mech.resolve_physical_attack(
                    monster, player, monster.get_avg_damage(), "", rng=rng, publish=publish
                )

            if defender.get_hp() <= 0:
                defender.set_isalive(False)
                break

            attacker_index = (attacker_index + 1) % 2

        screens.render_post_battle(player, monster)
    finally:
        cleanup_ui()


def fight(player, monster, rng: random.Random | None = None) -> None:
    """Alias legível para `run_fight` (compatível com chamadas antigas)."""
    run_fight(player, monster, rng=rng)
