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
from src.shared.effects import TURN_SKIPPING_STATUSES

# Um combate que o herói vai perder de qualquer jeito vale mais como fuga do que
# como morte. Abaixo deste percentual de HP, e sem cura na mão, o bot esperto foge.
FLEE_HP_RATIO = 0.12
# Abaixo deste percentual o bot esperto gasta poção ou skill de cura.
HEAL_HP_RATIO = 0.35
# Papéis que matam rápido e por isso morrem primeiro.
PRIORITY_ROLES = ("glass_cannon", "support", "controller")
# Abaixo desta fração de mana, o bot bebe poção de mana se tiver uma.
MANA_POTION_RATIO = 0.25
# Efeitos de consumível que valem um turno no começo de um combate longo.
COMBAT_ELIXIR_EFFECTS = (
    "strength", "defense", "agility", "crit_chance",
    "damage_reduction", "life_steal", "evasion",
)
# A partir de quantos turnos estimados vale gastar um turno preparando buff.
LONG_FIGHT_TURNS = 5
# Quantos turnos contam como abertura do combate. Preparação (buff, elixir,
# status que só enfraquece) só vale aqui. Sem esse limite o bot reaplica o buff
# assim que ele expira e nunca ataca: como o inimigo continua com a vida cheia,
# qualquer teste baseado na vida acha que o combate ainda está começando. O laço
# inflava o combate do Ladino de 6 para 50 turnos.
OPENING_TURNS = 2


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


def _consumables(hero, effect_types: tuple[str, ...]) -> list:
    """Consumíveis do inventário cujo efeito está na lista pedida."""
    return [
        item
        for item in hero.inventory
        if getattr(item, "consumable", False)
        and getattr(item, "effect_type", None) in effect_types
        and getattr(item, "effect_value", 0) > 0
    ]


def _healing_potions(hero) -> list:
    return _consumables(hero, ("max_hp",))


def _mana_potions(hero) -> list:
    return _consumables(hero, ("max_mp",))


def _combat_elixirs(hero) -> list:
    """Elixires que valem a pena antes de um combate longo."""
    return _consumables(hero, COMBAT_ELIXIR_EFFECTS)


def _active_buff_stats(hero) -> set[str]:
    """Atributos que já estão sob efeito de buff, para não empilhar o mesmo."""
    from src.shared.effects import buff_stat

    return {
        buff_stat(name, data)
        for name, data in getattr(hero, "active_buffs", {}).items()
        if isinstance(data, dict)
    }


def greedy_policy(hero, monsters: list, turn: int = 0) -> Action:
    """Sempre ataque básico, sempre no primeiro alvo vivo.

    É o piso de referência: o jogador que nunca aprende nada. Se este bot chega
    ao nível 20, o jogo recompensa paciência em vez de competência.
    """
    living = alive(monsters)
    return Action(kind="attack", target=living[0] if living else None)


def random_policy(hero, monsters: list, turn: int = 0, rng: random.Random | None = None) -> Action:
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


def smart_policy(hero, monsters: list, turn: int = 0, rng: random.Random | None = None) -> Action:
    """Heurística de jogador competente.

    A ordem das verificações é a própria tese do que "jogar bem" significa aqui:
    não morrer, escolher o alvo certo, preparar o combate longo, e só então
    otimizar dano. Uma política que só ataca e cura mede um jogo em que buff,
    controle e elixir não existem — e o balanceamento sai calibrado para esse
    jogo, não para o que está no código.
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
    basic = _estimate_basic_damage(hero, target)
    turnos_estimados = _estimated_turns(living, basic)
    combate_longo = turnos_estimados >= LONG_FIGHT_TURNS

    # 4. Preparar o combate longo. Um buff de defesa no primeiro turno de uma
    #    luta de dez turnos rende mais que o dano daquele turno; num combate de
    #    três, é turno perdido.
    if combate_longo and turn < OPENING_TURNS:
        ativos = _active_buff_stats(hero)
        buffs = [
            s for s in _usable_skills(hero, ("buff", "damage_reduction"))
            if getattr(s, "effect_stat", "") not in ativos
        ]
        if buffs:
            return Action(kind="skill", target=hero, skill=buffs[0])

        elixires = [
            i for i in _combat_elixirs(hero)
            if _elixir_stat(i) not in ativos
        ]
        if elixires:
            return Action(kind="item", item=elixires[0])

    # 5. Repor mana quando ela é o gargalo e há poção em mãos.
    if _mp_ratio(hero) < MANA_POTION_RATIO and hero.skills:
        mana = _mana_potions(hero)
        if mana:
            return Action(kind="item", item=mana[0])

    # 6. Controle. Atordoar um alvo economiza mais vida do que qualquer skill de
    #    dano gasta em MP, e vale sempre que o efeito não estiver ativo. Já um
    #    status que só enfraquece não encurta a luta: reaplicá-lo a cada expiração
    #    é um turno perdido por rodada, e era o que inflava o combate do Ladino
    #    de 11 para 50 turnos. Esse tipo entra só na abertura.
    if len(living) > 1 or combate_longo:
        ativos_no_alvo = getattr(target, "active_effects", {})
        control = [
            s
            for s in _usable_skills(hero, ("status",))
            if str(s.effect_value) not in ativos_no_alvo
            and (str(s.effect_value) in TURN_SKIPPING_STATUSES or turn < OPENING_TURNS)
        ]
        if control:
            return Action(kind="skill", target=target, skill=control[0])

    # 7. Otimizar dano: usar a skill só quando ela bate mais que o ataque básico,
    #    que é gratuito. Skill que não supera o básico é MP jogado fora.
    best_skill, best_damage = None, basic
    for skill in _usable_skills(hero, ("damage",)):
        estimate = _estimate_skill_damage(hero, skill, target)
        if estimate > best_damage:
            best_skill, best_damage = skill, estimate

    if best_skill is not None:
        return Action(kind="skill", target=target, skill=best_skill)

    return Action(kind="attack", target=target)


def _mp_ratio(hero) -> float:
    return hero.get_mp() / max(1, int(getattr(hero, "base_mp", 1)))


def _elixir_stat(item) -> str:
    """Atributo que um elixir modifica, para não empilhar o mesmo buff."""
    from src.entities.heroes import POTION_BUFFS

    entry = POTION_BUFFS.get(getattr(item, "effect_type", ""), None)
    return entry[0] if entry else ""


def _estimated_turns(living: list, damage_per_turn: int) -> int:
    """Quantos turnos o encontro inteiro deve durar no ritmo atual."""
    total_hp = sum(m.get_hp() for m in living)
    return max(1, total_hp // max(1, damage_per_turn))


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
