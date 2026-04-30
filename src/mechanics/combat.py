"""Regras puras de combate (sem I/O)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from src.shared import combat_topics as T
from src.shared.types import CombatResult, GameEvent

PublishFn = Callable[[str, GameEvent], None] | None


def _emit(publish: PublishFn, topic: str, *, type_: str, payload: dict[str, Any]) -> None:
    if publish is None:
        return
    publish(topic, GameEvent(type=type_, payload=payload, source="mechanics.combat"))


@dataclass(frozen=True, slots=True)
class SkillApplyResult:
    """Resultado da aplicação mecânica de uma habilidade."""

    kind: Literal["damage", "heal", "status", "buff"]
    mp_spent: int
    strike: CombatResult | None = None
    heal_amount: int = 0
    status_effect: str | None = None
    status_success: bool | None = None
    buff_name: str | None = None


def _rng(rng: random.Random | None) -> random.Random:
    return rng if rng is not None else random


def resolve_physical_attack(
    attacker,
    defender,
    base_damage: int,
    skill_name: str = "",
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> CombatResult:
    """
    Resolve um golpe físico: acerto, crítico, dano após armadura e aplica `take_damage`.
    """
    r = _rng(rng)

    crit_chance = (
        25
        if hasattr(attacker, "get_classname")
        and attacker.get_classname() == "Rogue"
        and skill_name == "Ataque Furtivo"
        else 10
    )

    hit_chance = 85 + (attacker.get_ag() - defender.get_ag())
    if r.randrange(1, 101) > hit_chance:
        miss = CombatResult(
            attacker_id=attacker.get_nick_name(),
            defender_id=defender.get_nick_name(),
            damage=0,
            was_critical=False,
            was_evaded=True,
            did_defender_die=False,
            notes=("miss",),
        )
        _emit(
            publish,
            T.COMBAT_PHYSICAL_STRIKE,
            type_="physical_strike",
            payload={"attacker": attacker, "defender": defender, "strike": miss},
        )
        return miss

    defense_reduction = defender.get_df() // 2
    damage = max(1, int(base_damage) - int(defense_reduction))

    is_critical = r.randrange(1, 101) <= crit_chance
    if is_critical:
        damage *= 2

    defender.take_damage(damage)
    dead = defender.get_hp() <= 0
    if dead:
        defender.set_isalive(False)

    strike = CombatResult(
        attacker_id=attacker.get_nick_name(),
        defender_id=defender.get_nick_name(),
        damage=int(damage),
        was_critical=bool(is_critical),
        was_evaded=False,
        did_defender_die=bool(dead),
        notes=("hit",),
    )
    _emit(
        publish,
        T.COMBAT_PHYSICAL_STRIKE,
        type_="physical_strike",
        payload={"attacker": attacker, "defender": defender, "strike": strike},
    )
    return strike


def apply_skill(
    caster,
    target,
    skill: Any,
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> SkillApplyResult:
    """Aplica efeitos de habilidade no estado (sem prints)."""
    r = _rng(rng)
    _emit(
        publish,
        T.COMBAT_SKILL_CAST,
        type_="skill_cast",
        payload={"caster": caster, "skill": skill},
    )
    caster.reduce_mp(int(skill.mana_cost))

    if skill.effect_type == "damage":
        strike = resolve_physical_attack(caster, target, int(skill.value), str(skill.name), rng=r, publish=None)
        out = SkillApplyResult(kind="damage", mp_spent=int(skill.mana_cost), strike=strike)
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "heal":
        heal_amount = int(skill.value)
        caster.heal(heal_amount)
        out = SkillApplyResult(kind="heal", mp_spent=int(skill.mana_cost), heal_amount=heal_amount)
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "status":
        if r.randrange(1, 101) <= int(skill.chance):
            target.active_effects[str(skill.value)] = {"duration": int(skill.duration)}
            out = SkillApplyResult(
                kind="status",
                mp_spent=int(skill.mana_cost),
                status_effect=str(skill.value),
                status_success=True,
            )
        else:
            out = SkillApplyResult(
                kind="status",
                mp_spent=int(skill.mana_cost),
                status_effect=str(skill.value),
                status_success=False,
            )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "buff":
        caster.active_buffs[str(skill.name)] = {
            "value": int(skill.value),
            "duration": int(skill.duration),
        }
        out = SkillApplyResult(
            kind="buff",
            mp_spent=int(skill.mana_cost),
            buff_name=str(skill.name),
        )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    raise ValueError(f"Unknown skill.effect_type: {getattr(skill, 'effect_type', None)!r}")


def process_turn_start_effects(
    entity,
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> bool:
    """
    Processa efeitos no início do turno do `entity`.

    Publica `COMBAT_TURN_EFFECT` quando `publish` é fornecido.
    Retorna `True` se o turno deve ser pulado (ex.: congelado).
    """
    _ = _rng(rng)

    skipped_turn = False

    effects_to_remove: list[str] = []
    buffs_to_remove: list[str] = []

    for effect, data in list(getattr(entity, "active_effects", {}).items()):
        if effect == "poison":
            poison_damage = 5
            entity.take_damage(poison_damage)
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "poison_tick", "damage": poison_damage},
            )
        if effect == "frozen":
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "frozen"},
            )
            skipped_turn = True

        data["duration"] -= 1
        if data["duration"] <= 0:
            effects_to_remove.append(effect)

    for buff, data in list(getattr(entity, "active_buffs", {}).items()):
        data["duration"] -= 1
        if data["duration"] <= 0:
            buffs_to_remove.append(buff)

    for effect in effects_to_remove:
        del entity.active_effects[effect]
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": "effect_expired", "name": effect},
        )

    for buff in buffs_to_remove:
        del entity.active_buffs[buff]
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": "buff_expired", "name": buff},
        )

    if entity.get_hp() <= 0:
        entity.set_isalive(False)

    return skipped_turn


def roll_flee_success(*, rng: random.Random | None = None) -> bool:
    r = _rng(rng)
    return r.randrange(0, 2) == 0
