"""Inscrições no EventBus para feedback de combate (Rich + ritmo), sem importar `engine/`."""

from __future__ import annotations

from collections.abc import Callable
from time import sleep
from typing import Any, Protocol

from src.shared import combat_topics as T
from src.shared.types import GameEvent
from src.ui import renderer


class EventSink(Protocol):
    def subscribe(self, topic: str, handler: Callable[[GameEvent], Any]) -> Callable[[], None]: ...


def _on_physical_strike(ev: GameEvent) -> None:
    p = ev.payload
    renderer.render_physical_strike_result(p["attacker"], p["defender"], p["strike"])
    sleep(0.8)


def _on_skill_cast(ev: GameEvent) -> None:
    p = ev.payload
    renderer.render_skill_cast_banner(p["caster"], p["skill"])
    sleep(0.5)


def _on_skill_outcome(ev: GameEvent) -> None:
    p = ev.payload
    result = p["result"]
    caster = p["caster"]
    target = p["target"]

    if result.kind == "damage" and result.strike is not None:
        renderer.render_physical_strike_result(caster, target, result.strike)
        sleep(0.8)
    elif result.kind == "heal":
        renderer.render_heal_result(caster, result.heal_amount)
        sleep(0.8)
    elif result.kind == "status":
        if result.status_success:
            renderer.render_status_apply(target, str(result.status_effect))
        else:
            renderer.render_status_failed()
        sleep(0.8)
    elif result.kind == "buff":
        renderer.render_buff_applied(caster, str(result.buff_name))
        sleep(0.8)


def _on_turn_effect(ev: GameEvent) -> None:
    p = ev.payload
    entity = p["entity"]
    kind = p["kind"]
    if kind == "poison_tick":
        renderer.render_turn_effect_message(entity, ("poison_tick", str(p["damage"])))
    elif kind == "frozen":
        renderer.render_turn_effect_message(entity, ("frozen",))
    elif kind == "effect_expired":
        renderer.render_turn_effect_message(entity, ("effect_expired", str(p["name"])))
    elif kind == "buff_expired":
        renderer.render_turn_effect_message(entity, ("buff_expired", str(p["name"])))
    sleep(0.6)


def _on_flee_result(ev: GameEvent) -> None:
    success = bool(ev.payload.get("success"))
    if success:
        renderer.render_flee_success_message()
        sleep(1.0)
    else:
        renderer.render_flee_failed_message()
        sleep(0.8)


def register_combat_ui_handlers(sink: EventSink) -> Callable[[], None]:
    unsubs = [
        sink.subscribe(T.COMBAT_PHYSICAL_STRIKE, _on_physical_strike),
        sink.subscribe(T.COMBAT_SKILL_CAST, _on_skill_cast),
        sink.subscribe(T.COMBAT_SKILL_OUTCOME, _on_skill_outcome),
        sink.subscribe(T.COMBAT_TURN_EFFECT, _on_turn_effect),
        sink.subscribe(T.COMBAT_FLEE_RESULT, _on_flee_result),
    ]

    def cleanup() -> None:
        for u in unsubs:
            u()

    return cleanup
