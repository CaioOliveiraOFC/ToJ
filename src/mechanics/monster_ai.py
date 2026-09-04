"""Decisão de turno dos monstros.

Antes deste módulo, o turno do monstro era um ataque básico incondicional: o
monstro nunca usava habilidade, nunca aplicava status e nunca reagia ao estado do
combate. Isso tornava todo encontro idêntico e removia qualquer counterplay.

A política aqui é deliberadamente simples — o objetivo não é uma IA que jogue bem,
e sim uma que force o jogador a responder a intenções diferentes. Um controlador
que rouba turnos exige uma resposta diferente de um glass cannon que precisa
morrer primeiro.
"""

from __future__ import annotations

import random

from src.mechanics import combat as combat_mech
from src.shared.constants import (
    DEFAULT_MONSTER_ROLE,
    MONSTER_HEAL_HP_RATIO,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
)


def _usable_skills(monster) -> list:
    """Skills que o monstro pode usar agora: MP suficiente e fora de recarga."""
    skills = getattr(monster, "skills", None) or []
    cooldowns = getattr(monster, "skill_cooldowns", {})
    return [
        s
        for s in skills
        if monster.get_mp() >= int(s.mana_cost) and cooldowns.get(s.id, 0) <= 0
    ]


def _pick_skill(monster, hero, usable: list, rng: random.Random):
    """Escolhe a skill conforme o papel do monstro, ou None para ataque básico."""
    if not usable:
        return None

    role = getattr(monster, "role", DEFAULT_MONSTER_ROLE)
    hp_ratio = monster.get_hp() / max(1, int(getattr(monster, "base_hp", 1)))

    heals = [s for s in usable if s.effect_type == "heal"]
    statuses = [s for s in usable if s.effect_type == "status"]
    buffs = [s for s in usable if s.effect_type in ("buff", "damage_reduction")]
    damages = [s for s in usable if s.effect_type == "damage"]

    # Curar-se quando ferido vem antes de qualquer outra intenção: um suporte que
    # morre com a cura na mão é um suporte que não cumpriu a função dele.
    if heals and hp_ratio < MONSTER_HEAL_HP_RATIO:
        return heals[0]

    if role == "controller" and statuses:
        return statuses[0]
    if role == "support":
        return (heals or buffs or statuses or damages)[0]
    if role == "tank" and buffs:
        return buffs[0]
    if role in ("glass_cannon", "boss", "elite") and damages:
        return max(damages, key=lambda s: int(s.effect_value) if str(s.effect_value).lstrip("-").isdigit() else 0)

    pool = damages or statuses or buffs
    return pool[0] if pool else None


def decide_monster_action(monster, hero, *, rng: random.Random | None = None, publish=None) -> None:
    """Executa o turno do monstro contra o herói.

    O monstro sem skills cai no ataque básico — que é o comportamento histórico e
    continua sendo o certo para um trash mob.
    """
    r = rng if rng is not None else random

    usable = _usable_skills(monster)
    if usable:
        skill_chance = int(getattr(monster, "skill_use_chance", 0))
        if skill_chance and r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= skill_chance:
            chosen = _pick_skill(monster, hero, usable, r)
            if chosen is not None:
                target = monster if chosen.target == "self" else hero
                combat_mech.apply_skill(monster, target, chosen, rng=r, publish=publish)
                return

    combat_mech.resolve_physical_attack(
        monster, hero, monster.get_avg_damage(), "", rng=r, publish=publish
    )
