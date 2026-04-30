"""Utilitários para emitir eventos de UI via EventBus.

Este módulo permite que a engine envie mensagens de log e notificações
para a camada de UI sem violar a regra de importação entre camadas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.shared import combat_topics as topics
from src.shared.types import GameEvent

if TYPE_CHECKING:
    from src.engine.events import EventBus


def emit_log(bus: EventBus, message: str, level: str = "info") -> None:
    """Emite uma mensagem de log para a UI."""
    bus.publish(
        topics.SYSTEM_LOG_MESSAGE,
        GameEvent(
            type="log_message",
            payload={"message": message, "level": level},
            source="engine.ui_events",
        ),
    )


def emit_save_success(bus: EventBus, message: str = "Jogo salvo com sucesso!") -> None:
    """Emite evento de sucesso ao salvar."""
    bus.publish(
        topics.SYSTEM_SAVE_SUCCESS,
        GameEvent(
            type="save_success",
            payload={"message": message},
            source="engine.ui_events",
        ),
    )


def emit_save_error(bus: EventBus, error: str) -> None:
    """Emite evento de erro ao salvar."""
    bus.publish(
        topics.SYSTEM_SAVE_ERROR,
        GameEvent(
            type="save_error",
            payload={"error": error},
            source="engine.ui_events",
        ),
    )
