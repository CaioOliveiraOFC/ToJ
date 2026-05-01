"""Orquestração de fluxos de jogo (ex.: combate) — motor de escolhas; UI via EventBus + `screens.render_*` / `prompts`."""

from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

from src.content.factories.loot import get_loot
from src.content.factories.monsters import create_boss_for_level, create_monster, generate_monsters_for_level
from src.content.items import Potion
from src.engine.events import EventBus
from src.ui.inventory_flow import run_inventory_flow
from src.engine.map import MapOfGame
from src.entities.monsters import Monster
from src.mechanics import combat as combat_mech
from src.mechanics.combat import PublishFn
from src.mechanics.math_operations import (
    calculate_mini_boss_xp_reward,
    calculate_monster_xp_reward,
)
from src.shared import combat_topics as topics
from src.shared.constants import (
    BASE_MAP_HEIGHT,
    BASE_MAP_WIDTH,
    MAP_HEIGHT_INCREMENT_PER_5_LEVELS,
    MAP_WIDTH_INCREMENT_PER_5_LEVELS,
    MAX_WALL_PERCENT_CAP,
    MIN_WALL_PERCENT,
    WALL_PERCENT_PER_LEVEL,
)
from src.shared.types import GameEvent
from src.storage.save_manager import save_game
from src.ui import screens
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.prompts import safe_get_key, wait_enter_to_continue
from src.ui.toj_menu import game_over_screen
from src.ui.utils import clear_screen

if TYPE_CHECKING:
    from src.entities.heroes import Player
    from src.entities.monsters import Monster


def _run_human_battle_turn(
    player: "Player",
    monster: "Monster",
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
                        topics.COMBAT_FLEE_RESULT,
                        GameEvent(type="flee_result", payload={"success": True}, source="engine.loop"),
                    )
                player.rest()
                return "flee"
            if publish:
                publish(
                    topics.COMBAT_FLEE_RESULT,
                    GameEvent(type="flee_result", payload={"success": False}, source="engine.loop"),
                )
            action_taken = True

    return None


def run_fight(
    player: "Player",
    monster: "Monster",
    rng: random.Random | None = None,
) -> None:
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

        # Processar lógica de pós-batalha (engine layer)
        xp_gained, player_won, dropped_item, level_up_msgs = process_post_battle(
            player, monster
        )

        # Renderizar resultados (UI layer)
        screens.render_post_battle(
            player_name=player.get_nick_name(),
            monster_name=monster.get_nick_name(),
            xp_gained=xp_gained,
            player_won=player_won,
            dropped_item_name=getattr(dropped_item, 'name', None) if dropped_item else None,
            level_up_messages=level_up_msgs,
        )
    finally:
        cleanup_ui()


def fight(
    player: "Player",
    monster: "Monster",
    rng: random.Random | None = None,
) -> None:
    """Alias legível para `run_fight` (compatível com chamadas antigas)."""
    run_fight(player, monster, rng=rng)


def process_post_battle(
    player: "Player", monster: "Monster"
) -> tuple[int, bool, object | None, list[str]]:
    """
    Processa a lógica de pós-combate (XP, loot, level up, rest).

    Esta função pertence à camada de engine - ela pode importar de
    mechanics/ e content/, e pode mutar estado de entidades.

    Retorna tupla com:
    - xp_gained: quantidade de XP ganhada
    - player_won: True se jogador venceu, False se foi derrotado
    - dropped_item: item dropado ou None
    - level_up_messages: lista de mensagens de level up (strings)
    """
    # Cálculo de XP base
    xp_base_reward = calculate_monster_xp_reward(monster.level)
    if getattr(monster, "is_boss", False):
        xp_base_reward = calculate_mini_boss_xp_reward(monster.level)

    player_won = player.get_isalive()
    dropped_item = None

    if not player_won:
        # Jogador derrotado - XP de piedade (10%)
        pity_xp = xp_base_reward // 10
        player.add_xp_points(pity_xp)
        xp_gained = pity_xp
    else:
        # Jogador venceu - XP completo e loot
        player.add_xp_points(xp_base_reward)
        xp_gained = xp_base_reward
        dropped_item = get_loot()
        if dropped_item:
            player.add_item_to_inventory(dropped_item)

    # Level up e rest (apenas se jogador vivo)
    level_up_messages: list[str] = []
    if player_won:
        level_up_messages = player.level_up(show=True)
        player.rest()

    return xp_gained, player_won, dropped_item, level_up_messages


def start_game(
    player: "Player",
    start_level: int = 1,
    initial_map_state: dict | None = None,
) -> None:
    """Loop principal do jogo: exploração de masmorras e combate."""
    dungeon_level = start_level
    while True:
        map_height = BASE_MAP_HEIGHT + (dungeon_level // 5) * MAP_HEIGHT_INCREMENT_PER_5_LEVELS
        map_width = BASE_MAP_WIDTH + (dungeon_level // 5) * MAP_WIDTH_INCREMENT_PER_5_LEVELS

        game_map = MapOfGame(height=map_height, width=map_width)

        if initial_map_state and dungeon_level == start_level:
            game_map.load_map_state(initial_map_state)
        else:
            wall_percent = MIN_WALL_PERCENT + min(
                dungeon_level * WALL_PERCENT_PER_LEVEL,
                MAX_WALL_PERCENT_CAP - MIN_WALL_PERCENT,
            )
            game_map.generate_map(percent_of_walls=wall_percent)
            game_map.place_player()
            game_map.place_exit()
            monsters_to_place = generate_monsters_for_level(dungeon_level)

            # Gerar Mini-Chefe a cada 5 níveis
            if dungeon_level % 5 == 0:
                boss = create_boss_for_level(dungeon_level)
                monsters_to_place.append(boss)

            for monster in monsters_to_place:
                game_map.place_enemy(monster)

        while True:
            clear_screen()
            screens.render_dungeon_status(
                dungeon_level, player.get_hp(), player.base_hp,
                player.get_mp(), player.base_mp
            )
            map_lines = game_map.draw_map()
            screens.render_map(map_lines)
            screens.render_dungeon_controls()

            move = safe_get_key(valid_keys=['w', 'a', 's', 'd', 'i', 'q', 'p'])

            if move is None or move == 'q':
                save_game(player, dungeon_level, game_map.get_map_state())
                screens.render_game_saved("Jogo salvo automaticamente ao sair.")
                return
            elif move == 'i':
                run_inventory_flow(player)
            elif move == 'p':
                save_game(player, dungeon_level, game_map.get_map_state())
                screens.render_game_saved()
            elif move in ['w', 'a', 's', 'd']:
                collided_object = game_map.move_player(move)

                if isinstance(collided_object, Monster):
                    fight(player, collided_object)
                    if not player.get_isalive():
                        game_over_screen(player.get_nick_name())
                        return
                    # After defeating a monster, update the map grid to reflect the empty space
                    game_map.grid[game_map.player_pos['y']][game_map.player_pos['x']] = '.'

                    screens.render_continue_prompt()
                    safe_get_key(allow_escape=False)

                elif collided_object == 'level_complete':
                    screens.render_level_complete(dungeon_level)
                    safe_get_key(allow_escape=False)
                    dungeon_level += 1
                    initial_map_state = None
                    break
