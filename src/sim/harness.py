"""Simulação headless de combate para medir balanceamento.

O motor de combate já é rápido — 147 mil resoluções de ataque por segundo. O que
tornava a medição lenta era o acoplamento: `engine.loop.run_fight` instancia um
EventBus, registra handlers Rich, renderiza a cada turno e bloqueia no teclado.
Este módulo chama `mechanics/` direto, com `publish=None`, e por isso roda 10 mil
combates por cenário em menos de um segundo.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import asdict, dataclass, field

from src.entities.heroes import Mage, Rogue, Warrior
from src.mechanics.battle import run_battle
from src.shared.constants import FLOOR_CLEAR_RESTORE_PERCENT
from src.sim.encounters import build_encounter
from src.sim.loadouts import apply_loadout
from src.sim.policies import get_policy

HERO_CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}
ALL_CLASSES = ("Warrior", "Mage", "Rogue")


@dataclass
class SimResult:
    """Métricas agregadas de um cenário simulado."""

    hero_class: str
    encounter: str
    level: int
    policy: str
    loadout: str
    iterations: int

    win_rate: float = 0.0
    flee_rate: float = 0.0
    death_rate: float = 0.0
    turns_mean: float = 0.0
    turns_p90: float = 0.0
    damage_dealt_mean: float = 0.0
    damage_taken_mean: float = 0.0
    hp_left_pct_on_win: float = 0.0
    mp_spent_mean: float = 0.0
    items_used_mean: float = 0.0
    action_mix: dict[str, float] = field(default_factory=dict)
    skill_usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        """Bloco legível no terminal, no formato pedido pelo plano."""
        mix = " / ".join(f"{k} {v:.0%}" for k, v in sorted(self.action_mix.items()))
        return (
            f"Class: {self.hero_class}   Level: {self.level}   Encounter: {self.encounter}\n"
            f"Simulations: {self.iterations:,}   Policy: {self.policy}   Loadout: {self.loadout}\n"
            f"Win rate: {self.win_rate:.1%}   Death rate: {self.death_rate:.1%}   "
            f"Flee rate: {self.flee_rate:.1%}\n"
            f"Avg turns: {self.turns_mean:.1f} (p90 {self.turns_p90:.0f})   "
            f"Avg damage dealt: {self.damage_dealt_mean:.0f}   "
            f"Avg damage taken: {self.damage_taken_mean:.0f}\n"
            f"HP left on win: {self.hp_left_pct_on_win:.0%}   "
            f"MP spent: {self.mp_spent_mean:.0f}   Items: {self.items_used_mean:.1f}\n"
            f"Action mix: {mix or 'n/a'}"
        )


def make_hero(hero_class: str, level: int, loadout: str = "naked"):
    """Constrói um herói do zero no nível pedido.

    Construir é mais barato que clonar: `set_level` mede 49 mil heróis por
    segundo contra 15 mil de `copy.deepcopy` do mesmo herói pronto.
    """
    if hero_class not in HERO_CLASSES:
        raise ValueError(f"Classe desconhecida: {hero_class!r}. Use uma de {sorted(HERO_CLASSES)}.")
    hero = HERO_CLASSES[hero_class](f"Sim{hero_class}")
    hero.set_level(level)
    apply_loadout(hero, loadout, level)
    return hero


def simulate(
    hero_class: str,
    encounter: str,
    level: int,
    iterations: int = 10_000,
    policy: str = "smart",
    seed: int = 1337,
    loadout: str = "expected",
) -> SimResult:
    """Roda `iterations` combates do cenário e devolve as métricas agregadas.

    Cada iteração usa `random.Random(seed + i)`, nunca o gerador global do módulo.
    É isso que torna qualquer resultado reproduzível e qualquer regressão de
    balanceamento bissetável.
    """
    decide = get_policy(policy)

    wins = fled = 0
    turns: list[int] = []
    dealt: list[int] = []
    taken: list[int] = []
    mp: list[int] = []
    items: list[int] = []
    hp_left_ratios: list[float] = []
    actions: dict[str, int] = {}
    skills: dict[str, int] = {}

    for i in range(iterations):
        rng = random.Random(seed + i)
        hero = make_hero(hero_class, level, loadout)
        monsters = build_encounter(encounter, level)

        outcome = run_battle(
            hero,
            monsters,
            lambda h, m: decide(h, m),
            rng=rng,
            publish=None,
        )

        wins += outcome.hero_won
        fled += outcome.fled
        turns.append(outcome.turns)
        dealt.append(outcome.damage_dealt)
        taken.append(outcome.damage_taken)
        mp.append(outcome.mp_spent)
        items.append(outcome.items_used)
        if outcome.hero_won and outcome.hp_max:
            hp_left_ratios.append(outcome.hp_left / outcome.hp_max)
        for key, count in outcome.action_counts.items():
            actions[key] = actions.get(key, 0) + count
        for key, count in outcome.skill_uses.items():
            skills[key] = skills.get(key, 0) + count

    total_actions = sum(actions.values()) or 1
    return SimResult(
        hero_class=hero_class,
        encounter=encounter,
        level=level,
        policy=policy,
        loadout=loadout,
        iterations=iterations,
        win_rate=wins / iterations,
        flee_rate=fled / iterations,
        death_rate=(iterations - wins - fled) / iterations,
        turns_mean=statistics.fmean(turns),
        turns_p90=_percentile(turns, 0.90),
        damage_dealt_mean=statistics.fmean(dealt),
        damage_taken_mean=statistics.fmean(taken),
        hp_left_pct_on_win=statistics.fmean(hp_left_ratios) if hp_left_ratios else 0.0,
        mp_spent_mean=statistics.fmean(mp),
        items_used_mean=statistics.fmean(items),
        action_mix={k: v / total_actions for k, v in actions.items()},
        skill_usage=skills,
    )


def simulate_run(
    hero_class: str,
    max_floor: int = 20,
    iterations: int = 1_000,
    policy: str = "smart",
    seed: int = 1337,
    loadout: str = "expected",
    encounters_per_floor=None,
) -> dict:
    """Simula runs completas de masmorra, andar a andar, com atrito entre combates.

    A run é a unidade que importa para a curva de dificuldade: um combate isolado
    pode ser fácil e a sequência de oito combates sem cura ainda matar o jogador.
    O herói **não** é curado entre combates do mesmo andar — é justamente esse
    atrito que o rebalanceamento existe para criar.
    """

    decide = get_policy(policy)
    deepest: list[int] = []
    survival = {floor: 0 for floor in range(1, max_floor + 1)}
    level_at_floor: dict[int, list[int]] = {floor: [] for floor in range(1, max_floor + 1)}

    for i in range(iterations):
        rng = random.Random(seed + i)
        hero = make_hero(hero_class, 1, loadout)
        reached = 0

        for floor in range(1, max_floor + 1):
            fights = encounters_per_floor(floor) if encounters_per_floor else _default_floor_plan(floor)
            died = False
            for name in fights:
                # O nível do encontro vem do ANDAR, não do herói — é assim que o
                # jogo real gera monstros. Amarrar ao nível do herói esconderia
                # justamente a defasagem que cria a dificuldade crescente.
                monsters = build_encounter(name, floor)
                outcome = run_battle(hero, monsters, lambda h, m: decide(h, m), rng=rng, publish=None)
                if not hero.get_isalive() or hero.get_hp() <= 0:
                    died = True
                    break
                if outcome.hero_won:
                    _award(hero, monsters)
            if died:
                break
            reached = floor
            survival[floor] += 1
            level_at_floor[floor].append(hero.get_level())
            # Fim do andar: descanso parcial e reposição de consumíveis na loja,
            # como o jogo real oferece entre andares.
            hero.recover(FLOOR_CLEAR_RESTORE_PERCENT)
            _restock(hero, floor)

        deepest.append(reached)

    return {
        "levels_by_floor": {f: statistics.fmean(v) for f, v in sorted(level_at_floor.items()) if v},
        "hero_class": hero_class,
        "policy": policy,
        "loadout": loadout,
        "iterations": iterations,
        "median_floor": statistics.median(deepest),
        "mean_floor": statistics.fmean(deepest),
        "reached_20_rate": sum(1 for d in deepest if d >= max_floor) / iterations,
        "survival_by_floor": {floor: count / iterations for floor, count in survival.items()},
    }


def _default_floor_plan(floor: int) -> list[str]:
    """Composição de um andar, por faixa de profundidade.

    A faixa importa mais que a contagem: os primeiros andares ensinam com
    encontros isolados, e a partir do andar 6 as composições passam a exigir
    escolha de alvo, que é a decisão tática mais básica que o jogo tem.
    """
    if floor <= 2:
        return ["trash_solo", "trash_solo", "bruiser_solo"]
    if floor <= 5:
        plan = ["trash_solo", "trash_pair", "bruiser_solo", "skirmisher_solo"]
    elif floor <= 10:
        plan = ["trash_pair", "bruiser_solo", "glass_solo", "skirmisher_solo",
                "tank_solo", "controller_solo"]
    else:
        plan = ["trash_trio", "bruiser_solo", "tank_plus_glass", "controller_plus_bruiser",
                "skirmisher_pair", "support_plus_bruiser", "glass_solo"]

    count = min(len(plan), 3 + floor // 4)
    fights = [plan[(floor + i) % len(plan)] for i in range(count)]
    if floor % 5 == 0:
        fights.append("boss_solo")
    elif floor % 3 == 0:
        fights.append("elite_solo")
    return fights


# Quantos consumíveis o jogador repõe na loja ao concluir um andar. Sem isto a
# simulação mede uma run em que ninguém compra nada, que não é a run que existe.
RESTOCK_POTIONS = 2


def _restock(hero, floor: int) -> None:
    """Repõe poções de cura entre andares, gastando o ouro acumulado."""
    from src.content.items import get_all_items

    potions = [
        item
        for item in get_all_items().values()
        if getattr(item, "consumable", False)
        and getattr(item, "effect_type", None) == "max_hp"
        and getattr(item, "shop_min_floor", 1) <= floor
    ]
    if not potions:
        return
    best = max(potions, key=lambda i: i.effect_value)
    carried = sum(1 for i in hero.inventory if getattr(i, "effect_type", None) == "max_hp")
    for _ in range(max(0, RESTOCK_POTIONS - carried)):
        if hero.spend_coins(int(best.price)):
            hero.add_item_to_inventory(best)


def _award(hero, monsters: list) -> None:
    """Concede XP e sobe de nível como o jogo faz depois de uma vitória."""
    from src.mechanics.math_operations import (
        calculate_monster_coin_reward,
        calculate_monster_xp_reward,
    )

    for monster in monsters:
        hero.add_xp_points(calculate_monster_xp_reward(monster.level))
        hero.earn_coins(calculate_monster_coin_reward(monster.level))
    while hero.level_up(show=False):
        pass


def _percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(q * len(ordered)))
    return float(ordered[index])
