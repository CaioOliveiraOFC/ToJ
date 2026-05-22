"""Handlers de eventos de UI (inscritos no EventBus) — chamadas de engine via eventos."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from src.shared.types import GameEvent
from src.shared import combat_topics as topics
from src.ui import screens
from src.ui.inventory_flow import run_inventory_flow_v2
from src.ui.passive_flow import run_passive_selection_flow
from src.ui.shop_flow import run_shop_flow
from src.ui.skill_flow import (
    run_skill_selection_flow,
    run_skill_selection_with_replacement,
)
from src.ui.toj_menu import (
    character_creation_flow as _character_creation,
    game_over_screen,
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
        sink.subscribe(topics.UI_GAME_OVER, _on_game_over),
        sink.subscribe(topics.UI_SAVE_SUCCESS, _on_save_success),
        sink.subscribe(topics.UI_MAIN_MENU, _on_main_menu),
        sink.subscribe(topics.UI_CHARACTER_CREATION, _on_character_creation),
    ]

    def cleanup() -> None:
        for u in unsubs:
            u()

    return cleanup