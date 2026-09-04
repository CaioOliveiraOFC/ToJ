"""Handlers de eventos de UI (inscritos no EventBus) — chamadas de engine via eventos."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from src.shared import combat_topics as topics
from src.shared.types import GameEvent
from src.ui import screens
from src.ui.character_status_flow import run_character_status_flow
from src.ui.extraction_flow import run_extraction_prompt
from src.ui.inventory_flow import run_inventory_flow_v2
from src.ui.passive_flow import run_passive_selection_flow
from src.ui.random_event_flow import run_random_event
from src.ui.shop_flow import run_shop_flow
from src.ui.skill_flow import (
    run_skill_selection_flow,
    run_skill_selection_with_replacement,
)
from src.ui.toj_menu import (
    character_creation_flow as _character_creation,
)
from src.ui.toj_menu import (
    game_over_screen,
)
from src.ui.toj_menu import (
    main_menu as _main_menu,
)


class EventSink(Protocol):
    def subscribe(self, topic: str, handler: Callable[[GameEvent], Any]) -> Callable[[], None]: ...


# Funções síncronas para chamadas diretas (sem EventBus)
def call_main_menu() -> str | None:
    """Chamada direta para o menu principal (sem EventBus)."""
    return _main_menu()


def call_character_creation() -> tuple | None:
    """Chamada direta para criação de personagem (sem EventBus)."""
    return _character_creation()


def _on_open_inventory(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    if player:
        run_inventory_flow_v2(player)


def _on_open_shop(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    shop = ev.payload.get("shop")
    dungeon_level = ev.payload.get("dungeon_level", 1)
    if player and shop:
        run_shop_flow(player, shop, dungeon_level)


def _on_open_passives(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    choices = ev.payload.get("choices")
    if player and choices:
        run_passive_selection_flow(player, choices)


def _on_extraction_prompt(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    dungeon_level = ev.payload.get("dungeon_level", 1)
    essence_multiplier = ev.payload.get("essence_multiplier", 1.0)
    result = ev.payload.get("result")
    if player is not None and isinstance(result, dict):
        choice = run_extraction_prompt(player, dungeon_level, essence_multiplier)
        result["choice"] = choice


def _on_random_event(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    dungeon_level = ev.payload.get("dungeon_level", 1)
    event_type = ev.payload.get("event_type")
    if player and event_type:
        run_random_event(player, dungeon_level, event_type)


def _on_open_character_status(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    if player:
        run_character_status_flow(player)


def _on_game_over(ev: GameEvent) -> None:
    player_name = ev.payload.get("player_name", "Aventureiro")
    game_over_screen(player_name)


def _on_save_success(ev: GameEvent) -> None:
    message = ev.payload.get("message", "Jogo salvo!")
    screens.render_game_saved(message)


def _on_main_menu(ev: GameEvent) -> str | None:
    return _main_menu()


def _on_character_creation(ev: GameEvent) -> tuple | None:
    return _character_creation()


def _on_open_skills(ev: GameEvent) -> None:
    player = ev.payload.get("player")
    choices = ev.payload.get("choices")
    if player and choices:
        chosen_skill = run_skill_selection_flow(player, choices)
        if chosen_skill:
            run_skill_selection_with_replacement(player, chosen_skill)


def register_ui_handlers(sink: EventSink) -> Callable[[], None]:
    unsubs = [
        sink.subscribe(topics.UI_OPEN_INVENTORY, _on_open_inventory),
        sink.subscribe(topics.UI_OPEN_SHOP, _on_open_shop),
        sink.subscribe(topics.UI_OPEN_PASSIVES, _on_open_passives),
        sink.subscribe(topics.UI_OPEN_SKILLS, _on_open_skills),
        sink.subscribe(topics.UI_EXTRACTION_PROMPT, _on_extraction_prompt),
        sink.subscribe(topics.UI_RANDOM_EVENT, _on_random_event),
        sink.subscribe(topics.UI_OPEN_CHARACTER_STATUS, _on_open_character_status),
        sink.subscribe(topics.UI_GAME_OVER, _on_game_over),
        sink.subscribe(topics.UI_SAVE_SUCCESS, _on_save_success),
        sink.subscribe(topics.UI_MAIN_MENU, _on_main_menu),
        sink.subscribe(topics.UI_CHARACTER_CREATION, _on_character_creation),
    ]

    def cleanup() -> None:
        for u in unsubs:
            u()

    return cleanup
