"""Passivas permanentes de nível — loader, modelo e gerador de escolhas."""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.data.loader import load_json
from src.shared.constants import (
    PASSIVE_COMMON_WEIGHT,
    PASSIVE_EPIC_WEIGHT,
    PASSIVE_LEGENDARY_WEIGHT,
    PASSIVE_RARE_WEIGHT,
)


@dataclass(frozen=True)
class PassiveCard:
    """Carta de passiva permanente carregada do JSON."""

    id: str
    name: str
    category: str
    rarity: str
    description: str
    effect_type: str
    effect_value: float


_PASSIVE_REGISTRY: dict[str, PassiveCard] | None = None


def _get_registry() -> dict[str, PassiveCard]:
    """Carrega e cacheia o registro de passivas. Chave: id."""
    global _PASSIVE_REGISTRY
    if _PASSIVE_REGISTRY is None:
        data = load_json("passives.json")
        _PASSIVE_REGISTRY = {
            p["id"]: PassiveCard(**{k: p[k] for k in PassiveCard.__dataclass_fields__})
            for p in data["passives"]
        }
    return _PASSIVE_REGISTRY


def load_passives() -> list[PassiveCard]:
    """Retorna lista de todas as passivas disponíveis."""
    return list(_get_registry().values())


def get_passive_by_id(passive_id: str) -> PassiveCard | None:
    """Busca passiva pelo ID. Retorna None se não encontrada."""
    return _get_registry().get(passive_id)


def generate_passive_choices(count: int = 3) -> list[PassiveCard]:
    """Gera N cartas únicas com distribuição ponderada por raridade.

    Args:
        count: Número de cartas a gerar (padrão: 3).

    Returns:
        Lista de PassiveCard únicas para o jogador escolher.
    """
    all_passives = load_passives()
    weights_map = {
        "Common": PASSIVE_COMMON_WEIGHT,
        "Rare": PASSIVE_RARE_WEIGHT,
        "Epic": PASSIVE_EPIC_WEIGHT,
        "Legendary": PASSIVE_LEGENDARY_WEIGHT,
    }
    weights = [weights_map.get(p.rarity, 1) for p in all_passives]

    chosen: list[PassiveCard] = []
    pool = list(all_passives)
    pool_weights = list(weights)

    while len(chosen) < count and pool:
        [pick] = random.choices(pool, weights=pool_weights, k=1)
        idx = pool.index(pick)
        chosen.append(pick)
        pool.pop(idx)
        pool_weights.pop(idx)

    return chosen
