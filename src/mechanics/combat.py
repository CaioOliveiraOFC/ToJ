"""Regras puras de combate (sem I/O)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from src.mechanics import effects as fx
from src.shared import combat_topics as T
from src.shared.constants import (
    BASE_HIT_CHANCE,
    BLEED_DAMAGE_PERCENT,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_CHANCE_HIGH,
    CRIT_DAMAGE_BASE,
    DAMAGE_REDUCTION_DEFAULT_PERCENT,
    DAMAGE_REDUCTION_DURATION,
    DEFENSE_K,
    FLEE_RANGE_MAX,
    HIT_AGILITY_SWING,
    HIT_CHANCE_CEIL,
    HIT_CHANCE_FLOOR,
    INVISIBLE_HIT_PENALTY,
    MANA_BURN_PER_TICK,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
    POISON_DAMAGE_PER_TICK,
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


def hit_chance(attacker, defender) -> int:
    """Chance de acerto, a partir da diferença *relativa* de agilidade.

    A fórmula antiga era `85 + AG_atacante - AG_defensor`, sem piso. Como a
    agilidade do Ladino crescia 18% ao nível e a do monstro era a constante 3,
    a chance de o monstro acertar caía a zero por volta do nível 13: a classe
    ficava imune a dano, e nenhum balanceamento de monstro alcançava isso.

    Usando a diferença relativa, a vantagem de quem investe em agilidade é
    grande, permanente e limitada — e continua valendo a mesma coisa no nível 1
    e no nível 20, porque os dois lados escalam juntos.
    """
    att_ag = max(0, attacker.get_ag())
    def_ag = max(0, defender.get_ag())
    total = att_ag + def_ag
    swing = 0.0 if total <= 0 else HIT_AGILITY_SWING * (att_ag - def_ag) / total

    chance = BASE_HIT_CHANCE + swing
    chance -= fx.combat_modifier(defender, "dodge_chance")
    chance -= fx.combat_modifier(defender, "evasion")
    if "invisible" in getattr(defender, "active_effects", {}):
        chance -= INVISIBLE_HIT_PENALTY

    return int(max(HIT_CHANCE_FLOOR, min(HIT_CHANCE_CEIL, chance)))


def skill_damage_base(caster, skill) -> int:
    """BASE_POWER total de uma skill de dano, antes de defesa e crítico.

    `effect_value` é um **percentual sobre o poder base**, não uma soma fixa.
    Como soma fixa, a skill anti-escalava: o poder base cresce a cada nível e o
    valor da skill não, então no nível 20 o Apocalipse entregava apenas +30%
    sobre um ataque básico que é gratuito e sem recarga. Como percentual, a
    skill mantém o mesmo peso relativo do nível 1 ao 20.

    Vive aqui, e não na política do simulador, porque o bot precisa estimar o
    dano com a mesma fórmula que o motor aplica. Duas cópias da fórmula divergem
    na primeira mudança de balanceamento.
    """
    base_power = caster.get_avg_damage()
    bonus_percent = int(skill.effect_value)
    return max(1, int(base_power * (1 + bonus_percent / 100)))


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

    if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) > hit_chance(attacker, defender):
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

    crit_chance = (
        CRIT_CHANCE_HIGH
        if hasattr(attacker, "get_classname")
        and attacker.get_classname() == "Rogue"
        and skill_name == "Ataque Furtivo"
        else CRIT_CHANCE_DEFAULT
    )
    crit_chance += int(fx.combat_modifier(attacker, "crit_chance"))
    crit_chance = min(crit_chance, CRIT_CHANCE_CAP)

    xmult_mods: list[float] = []
    is_critical = r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= crit_chance
    if is_critical:
        crit_damage = CRIT_DAMAGE_BASE + fx.combat_modifier(attacker, "crit_damage") / 100
        xmult_mods.append(crit_damage)

    damage = _calculate_damage(
        base_power=float(base_damage),
        flat_mods=None,
        mult_mods=None,
        xmult_mods=xmult_mods if xmult_mods else None,
        defense_target=defender.get_df(),
    )

    # Status do atacante que reduzem o dano causado (weakened, fear) e status do
    # defensor que reduzem o dano recebido (damage_reduction ativo ou passivo).
    damage = int(damage * fx.outgoing_damage_multiplier(attacker))
    damage = max(1, int(damage * fx.incoming_damage_multiplier(defender)))

    # Stun: por skill nomeada, ou pela passiva de atordoamento do atacante.
    stun_chance = 30 if skill_name == "Esmagar" else int(fx.combat_modifier(attacker, "stun_chance"))
    if stun_chance and r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= stun_chance:
        if hasattr(defender, "active_effects"):
            defender.active_effects["stun"] = {"duration": STUN_DURATION}
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": defender, "kind": "stun_applied"},
            )

    defender.take_damage(damage)
    fx.wake_on_damage(defender)

    # Roubo de vida: devolve ao atacante um percentual do dano causado.
    life_steal = fx.combat_modifier(attacker, "life_steal")
    if life_steal > 0:
        attacker.heal(max(1, int(damage * life_steal / 100)))

    dead = defender.get_hp() <= 0
    if dead and _survive_lethal_blow(defender):
        dead = False
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": defender, "kind": "death_ignored"},
        )
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


def _survive_lethal_blow(entity) -> bool:
    """Passiva `death_ignore`: sobrevive com 1 de HP a um golpe letal, uma vez por combate.

    Uma vez por combate, e não uma vez por run, porque uma passiva que ressuscita
    para sempre transforma qualquer encontro perdido em encontro vencido e apaga
    a decisão de fugir.
    """
    getter = getattr(entity, "get_passive_bonus", None)
    if not callable(getter) or getter("death_ignore") <= 0:
        return False
    if getattr(entity, "_death_ignore_used", False):
        return False
    entity._death_ignore_used = True
    entity._hp = 1
    return True


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
        total_base = skill_damage_base(caster, skill)
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
        # Percentual do HP máximo, não valor fixo: uma cura de 50 pontos era
        # irrelevante para um herói com milhares de HP no fim do jogo.
        max_hp = int(getattr(caster, "base_hp", caster.get_hp()))
        heal_amount = max(1, int(max_hp * int(skill.effect_value) / 100))
        heal_amount += int(heal_amount * fx.combat_modifier(caster, "potion_heal_bonus") / 100)
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
        # O buff declara qual atributo modifica. Sem isso, o motor precisava
        # reconhecer o buff pelo nome, e todo nome fora da lista era um no-op.
        recipient = caster if getattr(skill, "target", "self") == "self" else target
        stat = str(getattr(skill, "effect_stat", "") or "")
        recipient.active_buffs[str(skill.name)] = {
            "stat": stat,
            "value": fx.buff_value(recipient, stat, int(skill.effect_value)),
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
    Retorna `True` se o turno deve ser pulado (congelado, atordoado ou dormindo).
    """
    _ = _rng(rng)

    skipped_turn = False

    # Cooldowns: decrementa a cada turno.
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

    # Regeneração de mana vinda de buff ou passiva.
    mana_regen = fx.combat_modifier(entity, "mana_regen")
    if mana_regen > 0:
        entity.reduce_mp(-int(mana_regen))
        max_mp = int(getattr(entity, "base_mp", entity.get_mp()))
        if entity.get_mp() > max_mp:
            entity._mp = max_mp

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
        elif effect == "bleed":
            max_hp = int(getattr(entity, "base_hp", entity.get_hp()))
            bleed_damage = max(1, int(max_hp * BLEED_DAMAGE_PERCENT / 100))
            entity.take_damage(bleed_damage)
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "bleed_tick", "damage": bleed_damage},
            )
        elif effect == "mana_burn":
            entity.reduce_mp(MANA_BURN_PER_TICK)
            if entity.get_mp() < 0:
                entity._mp = 0
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": "mana_burn_tick", "amount": MANA_BURN_PER_TICK},
            )

        if effect in fx.TURN_SKIPPING_STATUSES:
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": entity, "kind": effect},
            )
            skipped_turn = True

        if effect == "damage_reduction":
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={
                    "entity": entity,
                    "kind": "damage_reduction_active",
                    "value": data.get("value", 0),
                },
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
