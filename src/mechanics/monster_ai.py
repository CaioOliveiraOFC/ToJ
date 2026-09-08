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


def _valor(skill) -> int:
    """Valor numérico de `effect_value`, ou 0 quando o efeito é um nome."""
    bruto = str(getattr(skill, "effect_value", 0))
    return int(bruto) if bruto.lstrip("-").isdigit() else 0


def _maior(skills: list):
    """A skill de maior valor da lista. `None` para lista vazia."""
    return max(skills, key=_valor) if skills else None


def _ja_esta_no_ar(monster, skill) -> bool:
    """Evita relançar o que já está ativo — gastar turno em nada é o defeito."""
    if skill.effect_type == "damage_reduction":
        return "damage_reduction" in getattr(monster, "active_effects", {})
    if skill.effect_type == "buff":
        return str(skill.name) in getattr(monster, "active_buffs", {})
    return False


def _usable_skills(monster) -> list:
    """Skills que o monstro pode usar agora: MP suficiente, fora de recarga e
    que ainda mudem alguma coisa."""
    skills = getattr(monster, "skills", None) or []
    cooldowns = getattr(monster, "skill_cooldowns", {})
    return [
        s
        for s in skills
        if monster.get_mp() >= int(s.mana_cost)
        and cooldowns.get(s.id, 0) <= 0
        and not _ja_esta_no_ar(monster, s)
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
        return _maior(damages), True

    # 2. Sobrevivência. Um suporte que morre com a cura na mão não cumpriu função.
    if heals and proprio < MONSTER_HEAL_HP_RATIO:
        return _maior(heals), True

    # 3. Desespero. Quem tem defesa se fecha para durar mais um turno; quem não
    #    tem gasta o maior dano que tiver, porque guardar recurso para um turno
    #    que não vai existir é o mesmo que não ter recurso.
    if proprio < MONSTER_DESPERATE_HP_RATIO:
        escolha = _maior(defensivas) if role in DEFENSIVE_ROLES else None
        escolha = escolha or _maior(damages) or _maior(defensivas) or _maior(statuses)
        if escolha is not None:
            return escolha, True

    # 4. Abertura. O buff vale pelos turnos que ainda existem à frente.
    if turnos < MONSTER_OPENER_TURNS and role in OPENER_ROLES and defensivas:
        return _maior(defensivas), True

    # 5. Rotina do papel. Aqui a moeda ainda vale: é a variação que impede o
    #    encontro de virar um roteiro decorado.
    if role == "controller":
        return (statuses or damages or defensivas)[0], False
    if role == "support":
        return (heals or defensivas or statuses or damages)[0], False
    if role == "tank":
        return (_maior(defensivas) or _maior(damages) or _maior(statuses)), False
    if role in ("glass_cannon", "boss", "elite", "bruiser", "skirmisher"):
        return (_maior(damages) or _maior(statuses) or _maior(defensivas)), False

    pool = damages or statuses or defensivas
    return (pool[0] if pool else None), False


def decide_monster_action(monster, hero, *, rng: random.Random | None = None, publish=None) -> None:
    """Executa o turno do monstro contra o herói.

    O monstro sem skills cai no ataque básico — que é o comportamento histórico e
    continua sendo o certo para um trash mob: o arquétipo dele é acúmulo, e a
    ameaça é o número, não a jogada.
    """
    r = rng if rng is not None else random
    try:
        usable = _usable_skills(monster)
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
