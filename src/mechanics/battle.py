"""Laço de batalha puro — sem I/O, compartilhado entre o jogo e o simulador.

Este módulo existe para que `engine/loop.py` (jogo real, com UI) e `sim/harness.py`
(simulação headless de balanceamento) executem exatamente as mesmas regras. Um
harness que reimplementa o combate mede um jogo que não existe, então a ordem de
turnos, a condição de vitória e o turno do monstro vivem aqui e só aqui.

A única coisa que os dois lados fornecem de forma diferente é a decisão do herói:
o jogo passa um callback que lê o teclado, o simulador passa uma política.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from src.mechanics import combat as combat_mech
from src.mechanics.monster_ai import decide_monster_action
from src.shared.constants import MAX_BATTLE_TURNS

ActionKind = Literal["attack", "skill", "item", "flee"]


@dataclass(frozen=True, slots=True)
class Action:
    """Decisão de um turno do herói."""

    kind: ActionKind
    target: Any = None
    skill: Any = None
    item: Any = None


@dataclass(slots=True)
class BattleOutcome:
    """Resultado de uma batalha completa."""

    hero_won: bool = False
    fled: bool = False
    turns: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    mp_spent: int = 0
    items_used: int = 0
    hp_left: int = 0
    hp_max: int = 0
    action_counts: dict[str, int] = field(default_factory=dict)
    skill_uses: dict[str, int] = field(default_factory=dict)


# A decisão recebe o herói, o encontro e o índice do turno do herói (0 no
# primeiro). O turno é necessário para decisões de abertura — preparar buff, por
# exemplo. Inferir "início do combate" pela vida do inimigo é circular: enquanto
# o herói só prepara, o inimigo continua com a vida cheia e o combate parece
# estar sempre começando.
HeroDecision = Callable[[Any, list, int], Action]


def alive(entities: list) -> list:
    """Filtra as entidades ainda vivas."""
    return [e for e in entities if e.get_isalive() and e.get_hp() > 0]


def build_turn_order(hero, monsters: list) -> list:
    """Ordena os combatentes por agilidade, decrescente.

    O herói vence empates: quem investiu em agilidade deve sentir o benefício, e
    empatar com o monstro em AG não deve custar o primeiro turno.
    """
    combatants = [hero, *monsters]
    return sorted(combatants, key=lambda e: (e.get_ag(), e is hero), reverse=True)


def pick_default_target(monsters: list):
    """Alvo padrão quando a decisão não indica um: o primeiro monstro vivo."""
    living = alive(monsters)
    return living[0] if living else None


def run_battle(
    hero,
    monsters: list,
    hero_decision: HeroDecision,
    *,
    rng: random.Random | None = None,
    publish=None,
    on_turn_start=None,
    max_turns: int = MAX_BATTLE_TURNS,
) -> BattleOutcome:
    """Executa uma batalha até a morte de um dos lados, fuga, ou o teto de turnos.

    Args:
        hero: O jogador.
        monsters: Lista de monstros do encontro (pode ter um só).
        hero_decision: Callback que devolve a `Action` do herói no turno dele.
        rng: Gerador dedicado. Passe um `random.Random(seed)` para reprodutibilidade.
        publish: Callback de eventos para a UI. `None` deixa o motor mudo e rápido.
        on_turn_start: Callback opcional chamado antes de cada turno (a UI usa para redesenhar).
        max_turns: Teto de segurança contra empate infinito.

    Returns:
        `BattleOutcome` com o resultado e as métricas do combate.
    """
    r = rng if rng is not None else random.Random()
    out = BattleOutcome(hp_max=int(getattr(hero, "base_hp", hero.get_hp())))

    order = build_turn_order(hero, monsters)
    index = 0
    hero_turn = 0

    while out.turns < max_turns:
        if not alive(monsters):
            out.hero_won = True
            break
        if not hero.get_isalive() or hero.get_hp() <= 0:
            break

        actor = order[index % len(order)]
        index += 1

        if actor is not hero and (not actor.get_isalive() or actor.get_hp() <= 0):
            continue

        if on_turn_start is not None:
            on_turn_start(actor, hero, monsters)

        skipped = combat_mech.process_turn_start_effects(actor, rng=r, publish=publish)

        if hero.get_hp() <= 0:
            hero.set_isalive(False)
            break
        if actor is not hero and actor.get_hp() <= 0:
            actor.set_isalive(False)
            continue

        if skipped:
            out.turns += 1
            continue

        if actor is hero:
            _run_hero_turn(hero, monsters, hero_decision, r, publish, out, hero_turn)
            hero_turn += 1
            if out.fled:
                return out
        else:
            _run_monster_turn(actor, hero, r, publish, out)

        out.turns += 1

    if not alive(monsters) and hero.get_isalive() and hero.get_hp() > 0:
        out.hero_won = True

    out.hp_left = max(0, hero.get_hp())
    return out


def _run_hero_turn(
    hero, monsters, hero_decision, rng, publish, out: BattleOutcome, hero_turn: int = 0
) -> None:
    """Aplica a decisão do herói e contabiliza as métricas do turno."""
    action = hero_decision(hero, monsters, hero_turn)
    if action is None:
        action = Action(kind="attack")

    out.action_counts[action.kind] = out.action_counts.get(action.kind, 0) + 1

    if action.kind == "flee":
        if combat_mech.roll_flee_success(rng=rng):
            out.fled = True
        return

    target = action.target or pick_default_target(monsters)

    if action.kind == "item" and action.item is not None:
        hero.use_potion(action.item)
        out.items_used += 1
        return

    if target is None:
        return

    hp_before = target.get_hp()

    if action.kind == "skill" and action.skill is not None:
        mp_before = hero.get_mp()
        combat_mech.apply_skill(hero, target, action.skill, rng=rng, publish=publish)
        out.mp_spent += max(0, mp_before - hero.get_mp())
        skill_id = getattr(action.skill, "id", "?")
        out.skill_uses[skill_id] = out.skill_uses.get(skill_id, 0) + 1
    else:
        combat_mech.resolve_physical_attack(
            hero, target, hero.get_avg_damage(), "", rng=rng, publish=publish
        )

    out.damage_dealt += max(0, hp_before - target.get_hp())
    if target.get_hp() <= 0:
        target.set_isalive(False)


def _run_monster_turn(monster, hero, rng, publish, out: BattleOutcome) -> None:
    """Executa o turno de um monstro através da IA e contabiliza o dano recebido."""
    hp_before = hero.get_hp()
    decide_monster_action(monster, hero, rng=rng, publish=publish)
    out.damage_taken += max(0, hp_before - hero.get_hp())
    if hero.get_hp() <= 0:
        hero.set_isalive(False)
