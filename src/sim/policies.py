"""Políticas de decisão do herói para simulação.

A razão de existirem duas políticas sérias — uma gananciosa e uma competente — é
medir o *skill gap*: a diferença de resultado entre apertar sempre "atacar" e
jogar bem. Se as duas empatam, o jogo não tem decisão, e nenhum ajuste de número
conserta isso. Toda a suíte de balanceamento gira em torno dessa diferença.
"""

from __future__ import annotations

import random

from src.mechanics import combat as combat_mech
from src.mechanics.battle import Action, alive

# Um combate que o herói vai perder de qualquer jeito vale mais como fuga do que
# como morte. Abaixo deste percentual de HP, e sem cura na mão, o bot esperto foge.
FLEE_HP_RATIO = 0.12
# Abaixo deste percentual o bot esperto gasta poção ou skill de cura.
HEAL_HP_RATIO = 0.35
# Papéis que matam rápido e por isso morrem primeiro.
PRIORITY_ROLES = ("glass_cannon", "support", "controller")


def _hp_ratio(entity) -> float:
    return entity.get_hp() / max(1, int(getattr(entity, "base_hp", 1)))


def _effective_hp(entity) -> float:
    """HP dividido pela mitigação: quanto dano bruto o alvo ainda absorve."""
    mitigation = 100 / (100 + max(0, entity.get_df()))
    return entity.get_hp() / max(0.01, mitigation)


def _usable_skills(hero, kinds: tuple[str, ...]) -> list:
    cooldowns = getattr(hero, "skill_cooldowns", {})
    return [
        s
        for s in hero.skills.values()
        if s.effect_type in kinds
        and hero.get_mp() >= int(s.mana_cost)
        and cooldowns.get(s.id, 0) <= 0
    ]


def _healing_potions(hero) -> list:
    return [
        item
        for item in hero.inventory
        if getattr(item, "effect_type", None) == "max_hp" and getattr(item, "effect_value", 0) > 0
    ]


def greedy_policy(hero, monsters: list) -> Action:
    """Sempre ataque básico, sempre no primeiro alvo vivo.

    É o piso de referência: o jogador que nunca aprende nada. Se este bot chega
    ao nível 20, o jogo recompensa paciência em vez de competência.
    """
    living = alive(monsters)
    return Action(kind="attack", target=living[0] if living else None)


def random_policy(hero, monsters: list, rng: random.Random | None = None) -> Action:
    """Ações aleatórias entre as legais. Serve para separar sorte de decisão."""
    r = rng or random
    living = alive(monsters)
    if not living:
        return Action(kind="attack")
    target = r.choice(living)
    options = ["attack"]
    if _usable_skills(hero, ("damage", "status", "buff", "heal", "damage_reduction")):
        options.append("skill")
    if _healing_potions(hero):
        options.append("item")
    kind = r.choice(options)
    if kind == "skill":
        return Action(kind="skill", target=target, skill=r.choice(_usable_skills(hero, ("damage", "status", "buff", "heal", "damage_reduction"))))
    if kind == "item":
        return Action(kind="item", item=r.choice(_healing_potions(hero)))
    return Action(kind="attack", target=target)


def smart_policy(hero, monsters: list, rng: random.Random | None = None) -> Action:
    """Heurística de jogador competente.

    A ordem das verificações é a própria tese do que "jogar bem" significa aqui:
    não morrer, escolher o alvo certo, e só então otimizar dano.
    """
    living = alive(monsters)
    if not living:
        return Action(kind="attack")

    ratio = _hp_ratio(hero)
    heal_skills = _usable_skills(hero, ("heal",))
    potions = _healing_potions(hero)

    # 1. Sobreviver. Cura antes de qualquer coisa.
    if ratio < HEAL_HP_RATIO:
        if heal_skills:
            return Action(kind="skill", target=hero, skill=heal_skills[0])
        if potions:
            return Action(kind="item", item=potions[0])

    # 2. Fugir de combate perdido em vez de morrer nele.
    if ratio < FLEE_HP_RATIO and not heal_skills and not potions:
        return Action(kind="flee")

    # 3. Escolher alvo: papéis perigosos primeiro, depois o mais frágil.
    target = _choose_target(living)

    # 4. Controle enquanto o combate ainda é longo. Atordoar um alvo cedo
    #    economiza mais vida do que qualquer skill de dano gasta em MP.
    if len(living) > 1 or target.get_hp() > _estimate_basic_damage(hero, target) * 3:
        control = [
            s
            for s in _usable_skills(hero, ("status",))
            if not getattr(target, "active_effects", {}).get(str(s.effect_value))
        ]
        if control:
            return Action(kind="skill", target=target, skill=control[0])

    # 5. Otimizar dano: usar a skill só quando ela bate mais que o ataque básico,
    #    que é gratuito. Skill que não supera o básico é MP jogado fora.
    basic = _estimate_basic_damage(hero, target)
    best_skill, best_damage = None, basic
    for skill in _usable_skills(hero, ("damage",)):
        estimate = _estimate_skill_damage(hero, skill, target)
        if estimate > best_damage:
            best_skill, best_damage = skill, estimate

    if best_skill is not None:
        return Action(kind="skill", target=target, skill=best_skill)

    return Action(kind="attack", target=target)


def _choose_target(living: list):
    """Papel perigoso primeiro; entre iguais, o que morre mais rápido."""
    priority = [m for m in living if getattr(m, "role", "") in PRIORITY_ROLES]
    pool = priority or living
    return min(pool, key=_effective_hp)


def _estimate_basic_damage(hero, target) -> int:
    mitigation = 100 / (100 + max(0, target.get_df()))
    return max(1, int(hero.get_avg_damage() * mitigation))


def _estimate_skill_damage(hero, skill, target) -> int:
    mitigation = 100 / (100 + max(0, target.get_df()))
    return max(1, int(combat_mech.skill_damage_base(hero, skill) * mitigation))


POLICIES = {
    "greedy": greedy_policy,
    "smart": smart_policy,
    "random": random_policy,
}


def get_policy(name: str):
    """Resolve o nome da política. Erro explícito é melhor que cair no default."""
    if name not in POLICIES:
        raise ValueError(f"Política desconhecida: {name!r}. Use uma de {sorted(POLICIES)}.")
    return POLICIES[name]
