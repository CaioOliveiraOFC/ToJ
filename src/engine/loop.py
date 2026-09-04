"""Orquestração de fluxos de jogo (ex.: combate).

Motor de escolhas; UI via EventBus + `screens.render_*` / `prompts`.
"""

from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

from src.content.factories.dungeons import roll_random_event
from src.content.factories.loot import get_loot
from src.content.factories.monsters import (
    create_boss_for_level,
    generate_monsters_for_level,
)
from src.content.passives import generate_passive_choices
from src.content.shop import Shop
from src.content.skills_loader import generate_skill_choices
from src.engine.events import EventBus
from src.engine.map import MapOfGame
from src.entities.monsters import Monster
from src.mechanics import battle
from src.mechanics.math_operations import (
    calculate_mini_boss_coin_reward,
    calculate_mini_boss_xp_reward,
    calculate_monster_coin_reward,
    calculate_monster_xp_reward,
    estimate_next_essence_multiplier,
    generate_essence_multiplier,
)
from src.shared import combat_topics as topics
from src.shared.constants import (
    BASE_MAP_HEIGHT,
    BASE_MAP_WIDTH,
    FLOOR_CLEAR_RESTORE_PERCENT,
    MAP_HEIGHT_INCREMENT_PER_5_LEVELS,
    MAP_WIDTH_INCREMENT_PER_5_LEVELS,
    MAX_WALL_PERCENT_CAP,
    MIN_WALL_PERCENT,
    WALL_PERCENT_PER_LEVEL,
)
from src.shared.types import GameEvent
from src.storage.save_manager import add_trophy, delete_save, save_game
from src.ui import screens
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.prompts import safe_get_key
from src.ui.ui_event_handlers import register_ui_handlers
from src.ui.utils import clear_screen

if TYPE_CHECKING:
    from src.entities.heroes import Player
    from src.entities.monsters import Monster


_game_event_bus: EventBus | None = None
_ui_cleanup: callable | None = None


def _get_game_publish() -> callable:
    """Retorna publish callback para eventos de UI, criando o bus se necessário."""
    global _game_event_bus, _ui_cleanup
    if _game_event_bus is None:
        _game_event_bus = EventBus()
        register_combat_ui_handlers(_game_event_bus)
        _ui_cleanup = register_ui_handlers(_game_event_bus)

    def publish(topic: str, payload_or_event: dict | GameEvent) -> None:
        if isinstance(payload_or_event, GameEvent):
            _game_event_bus.publish(topic, payload_or_event)
        else:
            event = GameEvent(type=topic, payload=payload_or_event)
            _game_event_bus.publish(topic, event)

    return publish


def _choose_target(player: "Player", monsters: list) -> "Monster | None":
    """Seleção de alvo quando o encontro tem mais de um monstro.

    Escolher alvo é a decisão tática mais básica que existe, e ela não existia:
    o combate era sempre um contra um. Com um monstro só, não há pergunta a
    fazer — a função devolve o único alvo direto.
    """
    living = battle.alive(monsters)
    if len(living) <= 1:
        return living[0] if living else None

    screens.render_target_select_panel(living)
    keys = [str(i) for i in range(1, len(living) + 1)] + ["0"]
    choice = safe_get_key(keys)
    if choice == "0" or not choice or not choice.isdigit():
        return living[0]
    index = int(choice) - 1
    return living[index] if 0 <= index < len(living) else living[0]


def _human_decision(player: "Player", monsters: list) -> battle.Action:
    """Lê a ação do jogador para o turno dele.

    Só orquestra teclas e devolve a decisão; quem aplica a regra é
    `mechanics.battle`, o mesmo código que o simulador de balanceamento usa.
    """
    while True:
        living = battle.alive(monsters)
        primary = living[0] if living else None
        screens.render_battle_frame(player, primary, living)
        screens.render_battle_action_panel()

        choice = safe_get_key(valid_keys=["1", "2", "3", "4"])

        if choice == "1":
            target = _choose_target(player, monsters)
            return battle.Action(kind="attack", target=target)

        if choice == "2":
            if not player.skills:
                screens.render_battle_no_skills_message()
                sleep(0.5)
                continue
            action = _pick_skill_action(player, monsters, primary)
            if action is not None:
                return action

        elif choice == "3":
            potions = [item for item in player.inventory if item.is_potion]
            if not potions:
                screens.render_battle_no_potions_message()
                sleep(0.5)
                continue
            action = _pick_potion_action(player, potions, primary, living)
            if action is not None:
                return action

        elif choice == "4":
            return battle.Action(kind="flee")


def _pick_skill_action(player, monsters, primary) -> "battle.Action | None":
    """Menu de skills. Devolve None se o jogador voltar sem escolher."""
    while True:
        screens.render_battle_frame(player, primary, battle.alive(monsters))
        screens.render_skill_select_panel(player)

        skill_keys = [str(k) for k in player.skills.keys()] + ["0"]
        skill_choice = safe_get_key(skill_keys)

        if skill_choice == "0":
            return None

        if not (skill_choice and skill_choice.isdigit() and int(skill_choice) in player.skills):
            continue

        skill = player.skills[int(skill_choice)]
        remaining = player.skill_cooldowns.get(getattr(skill, "id", ""), 0)
        if remaining > 0:
            screens.render_skill_on_cooldown_message(skill.name, remaining)
            sleep(0.5)
            continue
        if player.get_mp() < skill.mana_cost:
            screens.render_battle_insufficient_mana_message()
            sleep(0.5)
            continue

        # Skill que age sobre o próprio herói não pede alvo.
        if skill.effect_type in ("heal", "buff") or getattr(skill, "target", "enemy") == "self":
            return battle.Action(kind="skill", skill=skill, target=player)
        return battle.Action(kind="skill", skill=skill, target=_choose_target(player, monsters))


def _pick_potion_action(player, potions, primary, living) -> "battle.Action | None":
    """Menu de consumíveis. Devolve None se o jogador voltar sem escolher."""
    while True:
        screens.render_battle_frame(player, primary, living)
        screens.render_potion_select_panel(potions)

        potion_keys = [str(i) for i in range(1, len(potions) + 1)] + ["0"]
        potion_choice = safe_get_key(potion_keys)

        if potion_choice == "0":
            return None
        if potion_choice and potion_choice.isdigit() and 0 < int(potion_choice) <= len(potions):
            return battle.Action(kind="item", item=potions[int(potion_choice) - 1])
        screens.render_battle_invalid_potion_message()
        sleep(0.5)


def _on_turn_start(actor, player, monsters) -> None:
    """Redesenha a tela e anuncia de quem é o turno."""
    living = battle.alive(monsters)
    screens.render_battle_frame(player, living[0] if living else None, living)
    screens.render_turn_banner(actor)


def _render_battle_results(
    player: "Player",
    monster: "Monster",
    xp_gained: int,
    player_won: bool,
    dropped_item: object | None,
    level_up_msgs: list[str],
    coins_gained: int,
    essence_multiplier: float = 1.0,
) -> None:
    """Renderiza os resultados da batalha."""
    screens.render_post_battle(
        player_name=player.get_nick_name(),
        monster_name=monster.get_nick_name(),
        xp_gained=xp_gained,
        player_won=player_won,
        dropped_item_name=getattr(dropped_item, 'name', None) if dropped_item else None,
        level_up_messages=level_up_msgs,
        coins_gained=coins_gained,
        essence_multiplier=essence_multiplier,
    )


def run_fight(
    player: "Player",
    monster: "Monster | list",
    rng: random.Random | None = None,
    essence_multiplier: float = 1.0,
) -> None:
    """Loop principal de batalha: mecânica publica eventos; UI reage via inscrições no bus.

    Aceita um monstro ou uma lista deles. A assinatura de um monstro só é mantida
    porque o mapa entrega um encontro por vez, e porque o combate era 1 contra 1
    até aqui — escolher alvo passa a existir quando o encontro tem mais de um.
    """
    rng = rng or random.Random()
    bus = EventBus()
    cleanup_combat = register_combat_ui_handlers(bus)
    cleanup_ui = register_ui_handlers(bus)

    def publish(topic: str, payload_or_event: dict | GameEvent) -> None:
        if isinstance(payload_or_event, GameEvent):
            bus.publish(topic, payload_or_event)
        else:
            event = GameEvent(type=topic, payload=payload_or_event)
            bus.publish(topic, event)

    monsters = list(monster) if isinstance(monster, list) else [monster]
    level_before = player.get_level()

    try:
        screens.render_fight_intro(player, monsters[0])
        safe_get_key(allow_escape=False)

        outcome = battle.run_battle(
            player,
            monsters,
            _human_decision,
            rng=rng,
            publish=publish,
            on_turn_start=_on_turn_start,
        )

        if outcome.fled:
            return

        xp_gained, player_won, dropped_item, level_up_msgs, coins_gained, levels_gained = process_post_battle(
            player, monsters, essence_multiplier
        )
        _render_battle_results(
            player, monsters[0], xp_gained, player_won, dropped_item,
            level_up_msgs, coins_gained, essence_multiplier
        )

        if player_won and levels_gained > 0:
            # Para cada nível ganho, oferecer escolhas na ordem: passiva primeiro, depois skill
            for lvl in range(level_before + 1, player.get_level() + 1):
                # Escolha de passiva
                choices = generate_passive_choices(count=3)
                publish(topics.UI_OPEN_PASSIVES, {"player": player, "choices": choices})

                # Escolha de skill (apenas níveis ímpares >= 5)
                if lvl >= 5 and lvl % 2 == 1:
                    player_skill_ids = [s.id for s in player.skills.values()]
                    skill_choices = generate_skill_choices(
                        player.get_classname(), lvl, player_skill_ids, count=3
                    )
                    publish(topics.UI_OPEN_SKILLS, {"player": player, "choices": skill_choices})
    finally:
        cleanup_combat()
        cleanup_ui()


def fight(
    player: "Player",
    monster: "Monster | list",
    rng: random.Random | None = None,
    essence_multiplier: float = 1.0,
) -> None:
    """Alias legível para `run_fight` (compatível com chamadas antigas)."""
    run_fight(player, monster, rng=rng, essence_multiplier=essence_multiplier)


def process_post_battle(
    player: "Player",
    monster: "Monster | list",
    essence_multiplier: float = 1.0,
) -> tuple[int, bool, object | None, list[str], int, int]:
    """
    Processa a lógica de pós-combate (XP, loot, moedas, level up).

    Esta função pertence à camada de engine - ela pode importar de
    mechanics/ e content/, e pode mutar estado de entidades.

    Recompensa por monstro do encontro: um encontro com três inimigos deve pagar
    mais que um com um, senão a composição vira punição pura.

    Retorna tupla com:
    - xp_gained: quantidade de XP ganha
    - player_won: True se jogador venceu, False se foi derrotado
    - dropped_item: item dropado ou None
    - level_up_messages: lista de mensagens de level up (strings)
    - coins_gained: quantidade de moedas ganhas
    - levels_gained: quantidade de níveis ganhos
    """
    monsters = list(monster) if isinstance(monster, list) else [monster]
    level_before = player.get_level()

    xp_base_reward = 0
    coins_base_reward = 0
    for mob in monsters:
        if getattr(mob, "is_boss", False):
            xp_base_reward += calculate_mini_boss_xp_reward(mob.level)
            coins_base_reward += calculate_mini_boss_coin_reward(mob.level)
        else:
            xp_base_reward += calculate_monster_xp_reward(mob.level)
            coins_base_reward += calculate_monster_coin_reward(mob.level)

    player_won = player.get_isalive()
    dropped_item = None
    coins_gained = 0

    # Passivas de essência e de ouro eram lidas por ninguém: `essence_bonus`
    # (4 cartas) e `gold_drop_bonus` (2 cartas) não apareciam em nenhum cálculo.
    essence_passive = 1 + player.get_passive_bonus("essence_bonus") / 100
    gold_passive = 1 + player.get_passive_bonus("gold_drop_bonus") / 100

    if not player_won:
        pity_xp = int((xp_base_reward // 10) * essence_multiplier * essence_passive)
        pity_coins = int((coins_base_reward // 10) * gold_passive)
        player.add_xp_points(pity_xp)
        player.earn_coins(pity_coins)
        xp_gained = pity_xp
        coins_gained = pity_coins
    else:
        xp_gained = int(xp_base_reward * essence_multiplier * essence_passive)
        player.add_xp_points(xp_gained)
        coins_gained = int(coins_base_reward * gold_passive)
        player.earn_coins(coins_gained)
        dropped_item = get_loot()
        if dropped_item:
            player.add_item_to_inventory(dropped_item)

    level_up_messages: list[str] = []
    levels_gained = 0
    if player_won:
        # Processa um level up por vez para permitir escolhas apropriadas
        while True:
            msgs = player.level_up(show=True)
            if not msgs:
                break
            level_up_messages.extend(msgs)
            levels_gained += 1

    # Sem `rest()`: curar por completo depois de cada vitória tornava todo
    # combate independente do anterior e zerava o atrito do andar. Poções,
    # skills de cura e a Fonte existem justamente para pagar esse custo.

    return xp_gained, player_won, dropped_item, level_up_messages, coins_gained, levels_gained


def _calculate_map_dimensions(dungeon_level: int) -> tuple[int, int]:
    """Calcula as dimensões do mapa baseado no nível da masmorra."""
    map_height = BASE_MAP_HEIGHT + (dungeon_level // 5) * MAP_HEIGHT_INCREMENT_PER_5_LEVELS
    map_width = BASE_MAP_WIDTH + (dungeon_level // 5) * MAP_WIDTH_INCREMENT_PER_5_LEVELS
    return map_height, map_width


def _calculate_wall_percentage(dungeon_level: int) -> float:
    """Calcula a porcentagem de paredes baseada no nível da masmorra."""
    return MIN_WALL_PERCENT + min(
        dungeon_level * WALL_PERCENT_PER_LEVEL,
        MAX_WALL_PERCENT_CAP - MIN_WALL_PERCENT,
    )


def _setup_dungeon_map(
    dungeon_level: int,
    initial_map_state: dict | None,
    start_level: int,
    player: "Player",
) -> MapOfGame:
    """Configura o mapa da masmorra (novo ou carregado)."""
    map_height, map_width = _calculate_map_dimensions(dungeon_level)
    game_map = MapOfGame(height=map_height, width=map_width)

    if initial_map_state and dungeon_level == start_level:
        game_map.load_map_state(initial_map_state)
    else:
        wall_percent = _calculate_wall_percentage(dungeon_level)
        game_map.generate_map(percent_of_walls=wall_percent)
        game_map.place_player()
        game_map.place_exit()
        monsters_to_place = generate_monsters_for_level(dungeon_level, player.level)

        # Os monstros do andar são distribuídos em encontros, não um por casa:
        # um encontro composto exige escolha de alvo, que é a decisão tática mais
        # básica do jogo e que não existia enquanto o combate era 1 contra 1.
        for group in _build_encounters(monsters_to_place, dungeon_level):
            game_map.place_enemy(group)

        # Mini-chefe a cada 5 níveis, sempre sozinho: ele já é o encontro.
        if dungeon_level % 5 == 0:
            game_map.place_enemy([create_boss_for_level(dungeon_level)])

    return game_map


def _build_encounters(monsters: list, dungeon_level: int) -> list[list]:
    """Agrupa os monstros do andar em encontros.

    Andares rasos mantêm inimigos isolados, para ensinar; a partir do andar 4 os
    grupos aparecem, e ficam maiores conforme a profundidade. Elites e chefes
    nunca entram em grupo — eles já são o encontro.
    """
    solos = [m for m in monsters if getattr(m, "is_boss", False)]
    rest = [m for m in monsters if not getattr(m, "is_boss", False)]

    if dungeon_level < 4:
        max_size = 1
    elif dungeon_level < 10:
        max_size = 2
    else:
        max_size = 3

    groups: list[list] = [[m] for m in solos]
    index = 0
    while index < len(rest):
        size = random.randint(1, max_size)
        groups.append(rest[index:index + size])
        index += size
    return groups


def _render_dungeon_screen(
    player: "Player",
    dungeon_level: int,
    game_map: MapOfGame,
    essence_multiplier: float = 1.0,
) -> None:
    """Renderiza a tela principal da masmorra."""
    clear_screen()
    screens.render_dungeon_status(
        dungeon_level, player.get_hp(), player.base_hp,
        player.get_mp(), player.base_mp, essence_multiplier
    )
    map_lines = game_map.draw_map()
    screens.render_map(map_lines)
    screens.render_dungeon_controls()


def _handle_player_movement(
    player: "Player",
    game_map: MapOfGame,
    dungeon_level: int,
    move: str,
    essence_multiplier: float = 1.0,
    slot: int = 1,
) -> str | None:
    """
    Processa o movimento do jogador.
    Retorna 'level_complete' se o nível foi completado,
    'player_died' se o jogador morreu,
    None se nada aconteceu.
    """
    collided_object = game_map.move_player(move)

    if isinstance(collided_object, list) or isinstance(collided_object, Monster):
        fight(player, collided_object, essence_multiplier=essence_multiplier)
        if not player.get_isalive():
            _get_game_publish()(topics.UI_GAME_OVER, {"player_name": player.get_nick_name()})
            add_trophy(
                player.get_nick_name(),
                player.get_classname(),
                player.get_level(),
                dungeon_level,
                "Derrotado na masmorra"
            )
            delete_save(slot)
            return "player_died"
        # After defeating a monster, update the map grid to reflect the empty space
        game_map.grid[game_map.player_pos['y']][game_map.player_pos['x']] = '.'

        screens.render_continue_prompt()
        safe_get_key(allow_escape=False)

    elif collided_object == 'level_complete':
        screens.render_level_complete(dungeon_level)
        safe_get_key(allow_escape=False)
        return "level_complete"

    return None


def _handle_player_input(
    player: "Player",
    game_map: MapOfGame,
    dungeon_level: int,
    essence_multiplier: float = 1.0,
    slot: int = 1,
) -> str | None:
    """
    Processa o input do jogador.
    Retorna 'quit' para sair, 'level_complete' para próximo nível,
    None para continuar.
    """
    move = safe_get_key(valid_keys=['w', 'a', 's', 'd', 'i', 'c', 'q', 'p'])

    if move is None or move == 'q':
        return "quit"
    elif move == 'i':
        _get_game_publish()(topics.UI_OPEN_INVENTORY, {"player": player})
    elif move == 'c':
        _get_game_publish()(topics.UI_OPEN_CHARACTER_STATUS, {"player": player})
    elif move == 'p':
        save_game(player, dungeon_level, game_map.get_map_state(), slot=slot)
        screens.render_game_saved()
    elif move in ['w', 'a', 's', 'd']:
        return _handle_player_movement(player, game_map, dungeon_level, move, essence_multiplier, slot)

    return None


def start_game(
    player: "Player",
    start_level: int = 1,
    initial_map_state: dict | None = None,
    slot: int = 1,
) -> None:
    """Loop principal do jogo: exploração de masmorras e combate."""
    dungeon_level = start_level
    shop = Shop()
    essence_multiplier = 1.0  # Valor padrão ao carregar save

    while True:
        game_map = _setup_dungeon_map(dungeon_level, initial_map_state, start_level, player)

        # Gerar novo multiplicador apenas ao criar novo andar (não ao carregar)
        if not (initial_map_state and dungeon_level == start_level):
            essence_multiplier = generate_essence_multiplier(dungeon_level)

        while True:
            _render_dungeon_screen(player, dungeon_level, game_map, essence_multiplier)

            result = _handle_player_input(player, game_map, dungeon_level, essence_multiplier, slot)

            if result == "quit":
                return
            elif result == "level_complete":
                # Descanso parcial, não cura completa: o andar é a unidade de
                # risco, e chegar ferido ao próximo é o que dá peso à extração.
                player.recover(FLOOR_CLEAR_RESTORE_PERCENT)
                # --- Evento aleatório (TASK-005) — 25% antes da extração ---
                event_type = roll_random_event()
                if event_type:
                    _get_game_publish()(topics.UI_RANDOM_EVENT, {
                        "player": player,
                        "dungeon_level": dungeon_level,
                        "event_type": event_type,
                    })
                    if not player.get_isalive():
                        _get_game_publish()(topics.UI_GAME_OVER, {"player_name": player.get_nick_name()})
                        add_trophy(
                            player.get_nick_name(),
                            player.get_classname(),
                            player.get_level(),
                            dungeon_level,
                            "Altar sombrio",
                        )
                        delete_save(slot)
                        return
                # Loja sempre disponível ao concluir o andar — inclusive para quem vai extrair,
                # para não perder a recompensa do andar (corrige bug reportado).
                _get_game_publish()(topics.UI_OPEN_SHOP, {"player": player, "shop": shop, "dungeon_level": dungeon_level})
                # --- Decisão de extração (TASK-007) ---
                # Sem meta-progressão nova: "preservar" = salvar o personagem
                # no slot atual via save_game (xp/level/passivas/coins/inventário
                # já com o resultado da loja) e encerrar a run. Continuar mantém
                # o fluxo histórico.
                next_estimate = estimate_next_essence_multiplier(dungeon_level)
                decision: dict[str, str | None] = {"choice": None}
                _get_game_publish()(topics.UI_EXTRACTION_PROMPT, {
                    "player": player,
                    "dungeon_level": dungeon_level,
                    "essence_multiplier": next_estimate,
                    "is_estimate": True,
                    "result": decision,
                    "slot": slot,
                })
                if decision.get("choice") == "extract":
                    save_game(player, dungeon_level, None, slot=slot)
                    screens.render_extraction_success(dungeon_level)
                    return
                dungeon_level += 1
                initial_map_state = None
                break
            elif result == "player_died":
                return
