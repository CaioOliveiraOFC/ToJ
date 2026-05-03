"""Skills — loader, modelo e gerador de escolhas."""

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
class SkillCard:
    """Carta de skill carregada do JSON."""

    id: str
    name: str
    skill_class: str
    level_required: int
    mana_cost: int
    effect_type: str
    effect_value: int | str
    description: str
    target: str
    duration: int
    chance: int
    rarity: str
    is_initial: bool


_SKILL_REGISTRY: dict[str, SkillCard] | None = None


def _get_registry() -> dict[str, SkillCard]:
    """Carrega e cacheia o registro de skills. Chave: id."""
    global _SKILL_REGISTRY
    if _SKILL_REGISTRY is None:
        data = load_json("skills.json")
        _SKILL_REGISTRY = {
            s["id"]: SkillCard(**{k: s[k] for k in SkillCard.__dataclass_fields__})
            for s in data["skills"]
        }
    return _SKILL_REGISTRY


def load_skills() -> list[SkillCard]:
    """Retorna lista de todas as skills disponíveis."""
    return list(_get_registry().values())


def get_skill_by_id(skill_id: str) -> SkillCard | None:
    """Busca skill pelo ID. Retorna None se não encontrada."""
    return _get_registry().get(skill_id)


def get_skill_by_name_fallback(skill_name: str) -> SkillCard | None:
    """Fallback para buscar skill pelo nome (para migração de saves antigos)."""
    for skill in _get_registry().values():
        if skill.name == skill_name:
            return skill
    return None


def get_skills_for_class(class_name: str) -> list[SkillCard]:
    """Retorna todas as skills de uma classe específica."""
    return [s for s in load_skills() if s.skill_class == class_name]


def get_initial_skills(class_name: str) -> list[SkillCard]:
    """Retorna as 4 skills iniciais (is_initial=True) de uma classe."""
    return [s for s in get_skills_for_class(class_name) if s.is_initial]


def generate_skill_choices(
    class_name: str, player_level: int, player_skill_ids: list[str], count: int = 3
) -> list[SkillCard]:
    """Gera N cartas únicas com distribuição ponderada por raridade.

    Exclui skills já conhecidas pelo jogador e skills iniciais.

    Args:
        class_name: Nome da classe do jogador.
        player_level: Nível atual do jogador.
        player_skill_ids: Lista de IDs de skills que o jogador já possui.
        count: Número de cartas a gerar (padrão: 3).

    Returns:
        Lista de SkillCard únicas para o jogador escolher.
    """
    all_skills = get_skills_for_class(class_name)
    # Filtrar: nível compatível, não é inicial, não está na lista do jogador
    available = [
        s for s in all_skills
        if s.level_required <= player_level
        and not s.is_initial
        and s.id not in player_skill_ids
    ]

    weights_map = {
        "Common": PASSIVE_COMMON_WEIGHT,
        "Rare": PASSIVE_RARE_WEIGHT,
        "Epic": PASSIVE_EPIC_WEIGHT,
        "Legendary": PASSIVE_LEGENDARY_WEIGHT,
    }
    weights = [weights_map.get(s.rarity, 1) for s in available]

    chosen: list[SkillCard] = []
    pool = list(available)
    pool_weights = list(weights)

    while len(chosen) < count and pool:
        [pick] = random.choices(pool, weights=pool_weights, k=1)
        idx = pool.index(pick)
        chosen.append(pick)
        pool.pop(idx)
        pool_weights.pop(idx)

    return chosen
