from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict


@dataclass(frozen=True, slots=True)
class CombatResult:
    """
    DTO imutável: resultado de uma resolução de combate (safe para UI).
    """

    attacker_id: str
    defender_id: str
    damage: int = 0
    was_critical: bool = False
    was_evaded: bool = False
    did_defender_die: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EntityStats:
    """
    Snapshot seguro de estado para UI (sem referência mutável à entidade real).
    """

    entity_id: str
    name: str
    kind: Literal["hero", "monster", "npc", "unknown"] = "unknown"
    level: int = 1

    hp: int = 0
    hp_max: int = 0
    mp: int = 0
    mp_max: int = 0

    st: int = 0
    ag: int = 0
    mg: int = 0
    df: int = 0

    status_effects: tuple[str, ...] = ()
    buffs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GameEvent:
    """
    Evento genérico do jogo para comunicação entre camadas via EventBus.
    """

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str | None = None
    ts: float | None = None


class MapState(TypedDict):
    """Estado serializável do mapa para persistência."""

    height: int
    width: int
    grid: list[list[str]]
    player_pos: dict[str, int]
    exit_pos: dict[str, int]
    enemies_pos: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class SaveData:
    """DTO para dados de save do jogo."""

    player_class: str
    player_name: str
    level: int
    xp: int
    coins: int
    dungeon_level: int
    map_state: MapState | None = None

