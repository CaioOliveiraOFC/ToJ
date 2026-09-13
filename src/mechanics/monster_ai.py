"""Decisão de turno dos monstros.

Antes deste módulo, o turno do monstro era um ataque básico incondicional: o
monstro nunca usava habilidade, nunca aplicava status e nunca reagia ao estado do
combate. Isso tornava todo encontro idêntico e removia qualquer counterplay.

A política aqui é deliberadamente simples — o objetivo não é uma IA que jogue bem,
e sim uma que force o jogador a responder a intenções diferentes. Um controlador
que rouba turnos exige uma resposta diferente de um glass cannon que precisa
morrer primeiro.

A segunda versão conserta o que faltava: a primeira era **estática**. Fora a
cura de emergência, o monstro escolhia sempre a mesma skill no mesmo papel, e o
uso passava por uma moeda (`skill_use_chance`) que ignorava a situação. Um tank
buffava a armadura no turno em que fosse sorteado, inclusive no último; um chefe
com o herói a um golpe da morte podia dar um tapa. Nada disso pedia adaptação do
jogador — pedia paciência.

Agora existem quatro momentos, e três deles **furam a moeda**, porque uma jogada
decisiva não é um sorteio:

1. **Execução** — o herói está abaixo do limiar de execução e o monstro tem dano
   guardado. Todo arquétipo executa. É o "porradão quando dá para matar".
2. **Sobrevivência** — o próprio monstro está ferido e tem cura.
3. **Desespero** — o monstro está perto de morrer: quem defende, se fecha; quem
   não defende, gasta o maior dano que tiver antes de cair.
4. **Abertura** — o primeiro turno de quem vive de defesa. Um buff de armadura
   lançado no turno 1 de uma luta de dez rende os três turnos inteiros; no
   oitavo, rende um. Aqui a moeda continua valendo para os papéis que não têm a
   defesa como identidade.

Fora esses momentos, a rotina do papel decide — e ela nunca repete um buff que
já está no ar, que era outra forma de gastar turno em nada.
"""

from __future__ import annotations

import random

from src.mechanics import combat as combat_mech
from src.shared.constants import (
    DEFAULT_MONSTER_ROLE,
    MONSTER_DESPERATE_HP_RATIO,
    MONSTER_EXECUTE_HP_RATIO,
    MONSTER_HEAL_HP_RATIO,
    MONSTER_OPENER_TURNS,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
)
from src.shared.effects import control_weight

# Papéis cuja identidade é aguentar. Eles abrem o combate se fechando, e é isso
# que obriga o jogador a trazer dano contínuo em vez de uma explosão só.
DEFENSIVE_ROLES = ("tank", "boss", "elite")

# Papéis que abrem com preparo. Suporte entra aqui porque o buff dele é o único
# valor que ele tem: um suporte que abre atacando é um trash mob caro.
OPENER_ROLES = DEFENSIVE_ROLES + ("support",)

# Efeitos que valem como "se fechar".
DEFENSIVE_EFFECTS = ("damage_reduction", "buff")


def _hp_ratio(entity) -> float:
    return entity.get_hp() / max(1, int(getattr(entity, "base_hp", 1)))


def _valor(skill, caster=None) -> float:
    """Quanto a jogada vale para QUEM vai lançá-la.

    Para uma skill de dano, o valor é o BASE que ela produz nas mãos deste
    monstro — a conta do motor, não uma segunda estimativa. Era
    `effect_value`, e depois da V2 esse campo é zero em toda carta de dano:
    `_maior` virava `max` de chave constante e devolvia o primeiro da lista.
    O chefe com o herói a um golpe da morte escolhia `Rajada Arcana` em vez de
    `Detonação Arcana` — a "execução" existia na forma e não na prática, que é
    o mesmo defeito que os status já tiveram aqui.

    Cura e buff continuam em `effect_value`: neles o campo é um percentual vivo,
    e não um número morto.
    """
    if skill.effect_type == "damage" and caster is not None:
        return float(combat_mech.skill_damage_base(caster, skill))
    bruto = str(getattr(skill, "effect_value", 0))
    return float(bruto) if bruto.lstrip("-").isdigit() else 0.0


def _valor_de_status(skill) -> float:
    """Quanto um status vale como jogada, na mesma métrica que o herói usa.

    `_valor` devolve 0 para todo status, porque `effect_value` deles é um nome
    (`"stun"`, `"fear"`, `"mana_burn"`) e não um número. Com isso `_maior` virava
    `max` de chave constante — que devolve o primeiro elemento. A comparação
    existia na forma e não na prática: o `controller`, cujas três skills são
    status, lançava sempre `Torpor` e nunca `Queima de Mana` ou `Presságio`,
    apesar de `monsters.json` declarar para ele "Nega turnos e recurso".

    A métrica é a mesma que o herói aplica em
    `src/sim/policies.py::_valor_de_controle`: peso da família vezes duração
    vezes chance de aplicar. O peso vem de `control_weight`, que já existia e
    cujo docstring afirmava servir "na hora de lançá-la" — servia, mas só para o
    herói. `src/mechanics/` não a importava.

    A camada de mecânica não pode importar de `src/sim/`, então o que é
    compartilhado é `control_weight`, em `src/shared/`.
    """
    duracao = max(1, int(getattr(skill, "duration", 1) or 1))
    chance = float(getattr(skill, "chance", 100) or 100) / 100
    return control_weight(str(getattr(skill, "effect_value", ""))) * duracao * chance


def _maior(skills: list, caster=None):
    """A skill de maior valor da lista. `None` para lista vazia.

    `caster` é quem vai lançar: sem ele não há como saber quanto uma carta de
    dano vale, porque depois da V2 o dano nasce dos atributos de quem lança.
    """
    if not skills:
        return None
    if all(s.effect_type == "status" for s in skills):
        return max(skills, key=_valor_de_status)
    return max(skills, key=lambda s: _valor(s, caster))


def _ja_esta_no_ar(monster, skill, target=None) -> bool:
    """Evita relançar o que já está ativo — gastar turno em nada é o defeito."""
    if skill.effect_type in ("damage_reduction", "buff"):
        # As duas moram no mesmo lugar agora, com a fonte na chave.
        return str(skill.name) in getattr(monster, "active_buffs", {})
    if skill.effect_type == "status" and target is not None:
        # O status vive no ALVO, não em quem lança — por isso o alvo precisa
        # chegar até aqui. Sem isto o monstro reaplicava `Torpor` num herói já
        # atordoado, pagando MP por uma duração renovada que não muda nada. A
        # chave é `effect_value`, a mesma que o motor grava em `combat.py`.
        return str(skill.effect_value) in (getattr(target, "active_effects", {}) or {})
    return False


def _usable_skills(monster, target=None) -> list:
    """Skills que o monstro pode usar agora: MP suficiente, fora de recarga e
    que ainda mudem alguma coisa."""
    skills = getattr(monster, "skills", None) or []
    cooldowns = getattr(monster, "skill_cooldowns", {})
    # Monstro não tem equipamento e portanto satisfaz qualquer requisito; o
    # `getattr` existe para o dia em que ele tiver, e não para acomodar a
    # ausência do método. Uma gramática só para herói e monstro significa que o
    # filtro precisa perguntar a mesma coisa aos dois.
    pode_usar = getattr(monster, "can_use_skill", None)
    return [
        s
        for s in skills
        if monster.get_mp() >= monster.skill_mana_cost(s)
        and cooldowns.get(s.id, 0) <= 0
        and not _ja_esta_no_ar(monster, s, target)
        and (not callable(pode_usar) or pode_usar(s))
    ]


def _pick_skill(monster, hero, usable: list, rng: random.Random) -> tuple[object | None, bool]:
    """Escolhe a skill conforme papel e situação.

    Returns:
        `(skill, decisiva)`. `decisiva=True` dispensa a rolagem de
        `skill_use_chance`: é uma jogada que o arquétipo faria sempre.
    """
    if not usable:
        return None, False

    role = getattr(monster, "role", DEFAULT_MONSTER_ROLE)
    proprio = _hp_ratio(monster)
    alvo = _hp_ratio(hero)
    turnos = int(getattr(monster, "turns_taken", 0))

    heals = [s for s in usable if s.effect_type == "heal"]
    statuses = [s for s in usable if s.effect_type == "status"]
    defensivas = [s for s in usable if s.effect_type in DEFENSIVE_EFFECTS]
    damages = [s for s in usable if s.effect_type == "damage"]

    # 1. Execução. O herói a um golpe da morte muda a prioridade de todo mundo:
    #    o suporte para de curar, o tank para de se fechar, e ambos tentam
    #    fechar a conta. É o momento em que o jogador precisa ter guardado a
    #    fuga, a cura ou o atordoamento — e é a razão de o combate ter turnos.
    if alvo < MONSTER_EXECUTE_HP_RATIO and damages:
        return _maior(damages, monster), True

    # 2. Sobrevivência. Um suporte que morre com a cura na mão não cumpriu função.
    if heals and proprio < MONSTER_HEAL_HP_RATIO:
        return _maior(heals, monster), True

    # 3. Desespero. Quem tem defesa se fecha para durar mais um turno; quem não
    #    tem gasta o maior dano que tiver, porque guardar recurso para um turno
    #    que não vai existir é o mesmo que não ter recurso.
    if proprio < MONSTER_DESPERATE_HP_RATIO:
        escolha = _maior(defensivas, monster) if role in DEFENSIVE_ROLES else None
        escolha = (
            escolha
            or _maior(damages, monster)
            or _maior(defensivas, monster)
            or _maior(statuses, monster)
        )
        if escolha is not None:
            return escolha, True

    # 4. Abertura. O buff vale pelos turnos que ainda existem à frente.
    if turnos < MONSTER_OPENER_TURNS and role in OPENER_ROLES and defensivas:
        return _maior(defensivas, monster), True

    # 5. Rotina do papel. Aqui a moeda ainda vale: é a variação que impede o
    #    encontro de virar um roteiro decorado.
    if role == "controller":
        return (
            _maior(statuses, monster) or _maior(damages, monster) or _maior(defensivas, monster)
        ), False
    if role == "support":
        return (
            _maior(heals, monster)
            or _maior(defensivas, monster)
            or _maior(statuses, monster)
            or _maior(damages, monster)
        ), False
    if role == "tank":
        return (
            _maior(defensivas, monster) or _maior(damages, monster) or _maior(statuses, monster)
        ), False
    if role in ("glass_cannon", "boss", "elite", "bruiser", "skirmisher"):
        return (
            _maior(damages, monster) or _maior(statuses, monster) or _maior(defensivas, monster)
        ), False

    return (
        _maior(damages, monster) or _maior(statuses, monster) or _maior(defensivas, monster)
    ), False


def decide_monster_action(monster, hero, *, rng: random.Random | None = None, publish=None) -> None:
    """Executa o turno do monstro contra o herói.

    O monstro sem skills cai no ataque básico — que é o comportamento histórico e
    continua sendo o certo para um trash mob: o arquétipo dele é acúmulo, e a
    ameaça é o número, não a jogada.
    """
    r = rng if rng is not None else random
    try:
        usable = _usable_skills(monster, hero)
        if usable:
            chosen, decisiva = _pick_skill(monster, hero, usable, r)
            if chosen is not None:
                chance = int(getattr(monster, "skill_use_chance", 0))
                sorteou = (
                    bool(chance)
                    and r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= chance
                )
                if decisiva or sorteou:
                    target = monster if chosen.target == "self" else hero
                    combat_mech.apply_skill(monster, target, chosen, rng=r, publish=publish)
                    return

        combat_mech.resolve_physical_attack(
            monster, hero, combat_mech.basic_attack_power(monster), "", rng=r, publish=publish
        )
    finally:
        # Contado no fim: durante a decisão, `turns_taken` é o número de turnos
        # JÁ tomados, então a abertura é `turns_taken < MONSTER_OPENER_TURNS`.
        monster.turns_taken = int(getattr(monster, "turns_taken", 0)) + 1
