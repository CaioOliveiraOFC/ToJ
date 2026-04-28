from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from typing import Any, Generic, TypeVar

from src.shared.types import GameEvent

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class _Subscription:
    topic: str
    handler: Callable[[GameEvent], Any]


class EventBus:
    """
    Pub/Sub simples: subscribe(topic, handler) e publish(topic, event).

    - topic pode ser um nome (ex: "combat.resolved") ou "*" para receber tudo.
    - handler sempre recebe um GameEvent.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._subs: dict[str, list[Callable[[GameEvent], Any]]] = {}

    def subscribe(self, topic: str, handler: Callable[[GameEvent], Any]) -> Callable[[], None]:
        with self._lock:
            self._subs.setdefault(topic, []).append(handler)

        def unsubscribe() -> None:
            with self._lock:
                handlers = self._subs.get(topic)
                if not handlers:
                    return
                try:
                    handlers.remove(handler)
                except ValueError:
                    return
                if not handlers:
                    self._subs.pop(topic, None)

        return unsubscribe

    def publish(self, topic: str, event: GameEvent) -> None:
        with self._lock:
            handlers = list(self._subs.get(topic, ()))
            wildcard = list(self._subs.get("*", ()))

        for h in handlers:
            h(event)
        for h in wildcard:
            h(event)

