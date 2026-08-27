"""Regras puras de combate (sem I/O)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from src.shared import combat_topics as T
from src.shared.constants import (
    BASE_HIT_CHANCE,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_CHANCE_HIGH,
    CRIT_DAMAGE_BASE,
    DAMAGE_REDUCTION_DEFAULT_PERCENT,
    DAMAGE_REDUCTION_DURATION,
    DEFENSE_K,
    FLEE_RANGE_MAX,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
    POISON_DAMAGE_PER_TICK,
    SKILL_LEVEL_SCALING,
    STUN_CHANCE_DEFAULT,
    STUN_DURATION,
    XMULT_CAP,
)
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


def _defense_modifier(defense_target: int) -> float:
    """DEFENSE_MODIFIER = k / (k + defense_target) — curva hiperbólica."""
    return DEFENSE_K / (DEFENSE_K + max(0, defense_target))


def _apply_xmult_cap(xmult_raw: float) -> float:
    """min(xmult_raw, XMULT_CAP) — teto de multiplicadores puros."""
    return min(xmult_raw, XMULT_CAP)


def _calculate_damage(
    base_power: float,
    flat_mods: list[int] | None = None,
    mult_mods: list[float] | None = None,
    xmult_mods: list[float] | None = None,
    defense_target: int = 0,
) -> int:
    """
    Pipeline completo de dano:
    ((BASE_POWER + ΣFLAT) × ΠMULT × ΠXMULT_capped) × DEFENSE_MODIFIER
    """
    flat_total = sum(flat_mods) if flat_mods else 0
    mult_total = 1.0 + sum(mult_mods) if mult_mods else 1.0

    xmult_raw = 1.0
    if xmult_mods:
        for v in xmult_mods:
            xmult_raw *= v
    xmult_capped = _apply_xmult_cap(xmult_raw)

    def_mod = _defense_modifier(defense_target)

    raw = (base_power + flat_total) * mult_total * xmult_capped * def_mod
    return max(1, int(raw))


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
    Resolve um golpe físico: acerto, crítico, pipeline de dano e aplica `take_damage`.
    `base_damage` é o BASE_POWER (vindo de get_avg_damage() com pesos de classe).
    """
    r = _rng(rng)

    crit_chance = (
        CRIT_CHANCE_HIGH
        if hasattr(attacker, "get_classname")
        and attacker.get_classname() == "Rogue"
        and skill_name == "Ataque Furtivo"
        else CRIT_CHANCE_DEFAULT
    )
    if hasattr(attacker, "get_passive_bonus"):
        crit_chance += int(attacker.get_passive_bonus("crit_chance"))
    crit_chance = min(crit_chance, CRIT_CHANCE_CAP)

    hit_chance = BASE_HIT_CHANCE + (attacker.get_ag() - defender.get_ag())
    if hasattr(defender, "get_passive_bonus"):
        hit_chance -= int(defender.get_passive_bonus("dodge_chance"))
    if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) > hit_chance:
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

    defense_target = defender.get_df()
    xmult_mods: list[float] = []

    is_critical = r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= crit_chance
    if is_critical:
        xmult_mods.append(CRIT_DAMAGE_BASE)

    # Damage reduction: verifica se o defensor tem o efeito ativo
    damage_reduction_pct = 0
    if hasattr(defender, "active_effects") and "damage_reduction" in defender.active_effects:
        try:
            damage_reduction_pct = int(defender.active_effects["damage_reduction"].get("value", 0))
        except Exception:
            damage_reduction_pct = 0

    damage = _calculate_damage(
        base_power=float(base_damage),
        flat_mods=None,
        mult_mods=None,
        xmult_mods=xmult_mods if xmult_mods else None,
        defense_target=defense_target,
    )

    if damage_reduction_pct:
        damage = max(1, int(damage * (1 - damage_reduction_pct / 100)))

    # Stun chance: ao acertar, chance de atordoar o alvo
    # Usa STUN_CHANCE_DEFAULT para ataques físicos e skills com stun implícito (ex: Esmagar)
    stun_chance = 0
    if skill_name == "Esmagar":
        stun_chance = 30
    elif hasattr(attacker, "get_passive_bonus"):
        try:
            stun_chance = int(attacker.get_passive_bonus("stun_chance"))
        except Exception:
            stun_chance = 0
    if stun_chance and r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= stun_chance:
        if hasattr(target := defender, "active_effects"):
            target.active_effects["stun"] = {"duration": STUN_DURATION}
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": defender, "kind": "stun_applied"},
            )

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

    # Cooldown: verifica se skill está em recarga
    skill_id = getattr(skill, "id", None)
    skill_cooldown = int(getattr(skill, "cooldown", 0) or 0)
    if skill_id and hasattr(caster, "skill_cooldowns"):
        remaining = caster.skill_cooldowns.get(skill_id, 0)
        if remaining > 0:
            # Em cooldown — não consome MP nem aplica efeito
            out = SkillApplyResult(kind="damage", mp_spent=0, strike=None)
            _emit(
                publish,
                T.COMBAT_SKILL_CAST,
                type_="skill_cast",
                payload={"caster": caster, "skill": skill, "on_cooldown": True},
            )
            return out

    _emit(
        publish,
        T.COMBAT_SKILL_CAST,
        type_="skill_cast",
        payload={"caster": caster, "skill": skill},
    )
    caster.reduce_mp(int(skill.mana_cost))

    # Aplica cooldown após uso bem-sucedido (se houver)
    if skill_id and hasattr(caster, "skill_cooldowns") and skill_cooldown > 0:
        caster.skill_cooldowns[skill_id] = skill_cooldown

    if skill.effect_type == "damage":
        base_power = caster.get_avg_damage()
        scaling = 1.0 + (caster.level * SKILL_LEVEL_SCALING)
        skill_flat = int(skill.effect_value * scaling)
        total_base = base_power + skill_flat
        strike = resolve_physical_attack(caster, target, total_base, str(skill.name), rng=r, publish=None)
        # Stun chance específica da skill (se houver)
        stun_chance_skill = int(getattr(skill, "stun_chance", 0) or 0)
        if strike and not strike.was_evaded and stun_chance_skill:
            if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= stun_chance_skill:
                if hasattr(target, "active_effects"):
                    target.active_effects["stun"] = {"duration": STUN_DURATION}
                    _emit(
                        publish,
                        T.COMBAT_TURN_EFFECT,
                        type_="turn_effect",
                        payload={"entity": target, "kind": "stun_applied"},
                    )
        out = SkillApplyResult(kind="damage", mp_spent=int(skill.mana_cost), strike=strike)
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "heal":
        heal_amount = int(skill.effect_value)
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
        if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= int(skill.chance):
            target.active_effects[str(skill.effect_value)] = {"duration": int(skill.duration)}
            out = SkillApplyResult(
                kind="status",
                mp_spent=int(skill.mana_cost),
                status_effect=str(skill.effect_value),
                status_success=True,
            )
        else:
            out = SkillApplyResult(
                kind="status",
                mp_spent=int(skill.mana_cost),
                status_effect=str(skill.effect_value),
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
            "value": int(skill.effect_value),
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

    if skill.effect_type == "damage_reduction":
        value = int(skill.effect_value) if isinstance(skill.effect_value, int) else DAMAGE_REDUCTION_DEFAULT_PERCENT
        duration = int(skill.duration) if skill.duration else DAMAGE_REDUCTION_DURATION
        # Aplica no alvo indicado pelo skill (self -> caster, enemy -> target)
        recipient = caster if getattr(skill, "target", "self") == "self" else target
        recipient.active_effects["damage_reduction"] = {"value": value, "duration": duration}
        out = SkillApplyResult(
            kind="buff",
            mp_spent=int(skill.mana_cost),
            buff_name="damage_reduction",
        )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": recipient, "result": out},
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

    # Cooldowns: decrementa a cada turno
    if hasattr(entity, "skill_cooldowns"):
        for sid in list(entity.skill_cooldowns.keys()):
            entity.skill_cooldowns[sid] -= 1
            if entity.skill_cooldowns[sid] <= 0:
                del entity.skill_cooldowns[sid]
                _emit(
                    publish,
                    T.COMBAT_TURN_EFFECT,
                    type_="turn_effect",
                    payload={"entity": entity, "kind": "cooldown_expired", "skill_id": sid},
                )

    effects_to_remove: list[str] = []
    buffs_to_remove: list[str] = []

    for effect, data in list(getattr(entity, "active_effects", {}).items()):
        if effect == "poison":
            poison_damage = POISON_DAMAGE_PER_TICK + (entity.get_ag() // 5)
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
        if effect == "stun":
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "stun"},
            )
            skipped_turn = True
        if effect == "damage_reduction":
            # Apenas conta duração; a redução é aplicada em resolve_physical_attack
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "damage_reduction_active", "value": data.get("value", 0)},
            )

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
    return r.randrange(0, FLEE_RANGE_MAX) == 0
