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

from src.content.factories.dungeons import (
    altar_hp_cost,
    apply_altar_blessing,
    apply_fountain_heal,
    roll_random_event,
)
from src.content.shop import Shop
from src.entities.heroes import Mage, Rogue, Warrior
from src.mechanics.battle import run_battle
from src.shared.constants import FLOOR_CLEAR_RESTORE_PERCENT
from src.sim import progression
from src.sim.encounters import build_encounter
from src.sim.loadouts import apply_loadout
from src.sim.policies import get_policy
from src.sim.telemetry import RunTelemetry
from src.sim.toggles import Toggles

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
            lambda h, m, t: decide(h, m, t),
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
    toggles: Toggles | None = None,
    collect_telemetry: bool = True,
) -> dict:
    """Simula runs completas de masmorra, com todos os sistemas que o jogo roda.

    A run é a unidade que importa para a curva de dificuldade: um combate isolado
    pode ser fácil e a sequência de oito combates sem cura ainda matar o jogador.
    O herói **não** é curado entre combates do mesmo andar — é justamente esse
    atrito que o rebalanceamento existe para criar.

    A run reproduz o `engine/loop.py`: escolha de passiva a cada nível, escolha
    de skill nos níveis ímpares a partir do 5, drop de item a cada vitória,
    multiplicador de Essência por andar, evento aleatório, loja entre andares e
    descanso parcial. Simular só o combate mede um herói que atravessa vinte
    andares com quatro skills comuns e o equipamento do andar 1 — que não é o
    herói que o jogo entrega.
    """
    decide = get_policy(policy)
    cfg = toggles or Toggles()
    telemetry = RunTelemetry() if collect_telemetry else None
    shop = Shop()
    deepest: list[int] = []
    survival = {floor: 0 for floor in range(1, max_floor + 1)}
    level_at_floor: dict[int, list[int]] = {floor: [] for floor in range(1, max_floor + 1)}
    skills_at_end: list[int] = []
    passives_at_end: list[int] = []

    for i in range(iterations):
        rng = random.Random(seed + i)
        hero = make_hero(hero_class, 1, loadout)
        reached = 0

        for floor in range(1, max_floor + 1):
            essence = progression.floor_essence_multiplier(floor) if cfg.essence else 1.0
            if telemetry is not None:
                telemetry.essence_rolls.append(essence)
            fights = encounters_per_floor(floor) if encounters_per_floor else _default_floor_plan(floor)
            died = False

            for name in fights:
                # O nível do encontro vem do ANDAR, não do herói — é assim que o
                # jogo real gera monstros. Amarrar ao nível do herói esconderia
                # justamente a defasagem que cria a dificuldade crescente.
                monsters = build_encounter(name, floor)
                outcome = run_battle(hero, monsters, lambda h, m, t: decide(h, m, t), rng=rng, publish=None)
                if not hero.get_isalive() or hero.get_hp() <= 0:
                    died = True
                    break
                if telemetry is not None:
                    telemetry.record_battle(outcome)
                if outcome.hero_won:
                    _award(hero, monsters, essence, rng, cfg, telemetry)

            if died:
                break

            reached = floor
            survival[floor] += 1
            level_at_floor[floor].append(hero.get_level())

            # Fim do andar, na ordem do jogo: evento aleatório, loja, descanso.
            if cfg.events:
                _apply_random_event(hero, shop, floor, rng, cfg, telemetry)
            if not hero.get_isalive() or hero.get_hp() <= 0:
                break
            progression.visit_shop(hero, shop, floor, rng, cfg, telemetry)
            hero.recover(FLOOR_CLEAR_RESTORE_PERCENT)

        deepest.append(reached)
        skills_at_end.append(len(hero.skills))
        passives_at_end.append(len(hero.passives))
        if telemetry is not None:
            telemetry.runs += 1
            telemetry.gold_unspent += hero.coins
            telemetry.final_power_equipped.append(hero.get_avg_damage())
            telemetry.final_power_naked.append(_power_without_equipment(hero))

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
        "skills_at_end_mean": statistics.fmean(skills_at_end),
        "passives_at_end_mean": statistics.fmean(passives_at_end),
        "toggles": cfg.label(),
        "telemetry": telemetry.to_dict() if telemetry is not None else None,
    }


def _power_without_equipment(hero) -> float:
    """Poder de ataque que o herói teria sem nada equipado.

    Comparado com o poder real, dá a fatia do dano que veio de equipamento —
    a resposta para "equipamento importa?" sem precisar de uma run separada.
    """
    equipado = dict(hero.equipment)
    for slot in hero.equipment:
        hero.equipment[slot] = None
    try:
        return float(hero.get_avg_damage())
    finally:
        hero.equipment.update(equipado)


def _apply_random_event(hero, shop, floor: int, rng: random.Random,
                        toggles=None, telemetry=None) -> None:
    """Evento aleatório de andar, com a mesma chance do jogo.

    O Altar cobra vida por um buff e pode matar; a Fonte cura; o Mercador é uma
    loja extra. O bot aceita a Fonte sempre e o Altar só com vida sobrando, que é
    a decisão que um jogador competente toma.
    """
    event = roll_random_event(rng)
    if event is None:
        return
    if telemetry is not None:
        telemetry.event_counts[event] += 1

    if event == "fountain":
        curado = apply_fountain_heal(hero)
        if telemetry is not None:
            telemetry.fountain_healed += int(curado)
    elif event == "altar":
        custo = altar_hp_cost(hero)
        if hero.get_hp() > custo * 2:
            hero.take_damage(custo)
            apply_altar_blessing(hero)
            if telemetry is not None:
                telemetry.altar_hp_paid += int(custo)
            if hero.get_hp() <= 0:
                hero.set_isalive(False)
                if telemetry is not None:
                    telemetry.altar_deaths += 1
        elif telemetry is not None:
            telemetry.event_declined["altar"] += 1
    elif event == "merchant":
        # Uma segunda passagem pela loja. Antes, o Mercador aparecia em um terço
        # dos eventos e a simulação não fazia nada com ele.
        progression.visit_shop(hero, shop, floor, rng, toggles, telemetry)


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


def _award(hero, monsters: list, essence: float, rng: random.Random,
           toggles: Toggles | None = None, telemetry=None) -> None:
    """Aplica XP, ouro, loot e as escolhas de nível, como o jogo faz.

    Espelha `engine.loop.process_post_battle`: a Essência multiplica o XP, as
    passivas de essência e de ouro entram na conta, e cada nível ganho abre uma
    escolha de passiva (e de skill, nos níveis ímpares a partir do 5).
    """
    from src.mechanics.math_operations import (
        calculate_mini_boss_coin_reward,
        calculate_mini_boss_xp_reward,
        calculate_monster_coin_reward,
        calculate_monster_xp_reward,
    )

    essence_passive = 1 + hero.get_passive_bonus("essence_bonus") / 100
    gold_passive = 1 + hero.get_passive_bonus("gold_drop_bonus") / 100

    xp = coins = 0
    for monster in monsters:
        if getattr(monster, "is_boss", False):
            xp += calculate_mini_boss_xp_reward(monster.level)
            coins += calculate_mini_boss_coin_reward(monster.level)
        else:
            xp += calculate_monster_xp_reward(monster.level)
            coins += calculate_monster_coin_reward(monster.level)

    xp_final = int(xp * essence * essence_passive)
    coins_final = int(coins * gold_passive)
    hero.add_xp_points(xp_final)
    hero.earn_coins(coins_final)
    if telemetry is not None:
        telemetry.xp_base += xp
        telemetry.xp_after_essence += xp_final
        telemetry.gold_earned += coins_final
    progression.collect_loot(hero, rng, toggles, telemetry)

    # Contar pela mudança de nível, não pelo retorno de `level_up`: com
    # `show=False` ele devolve lista vazia mesmo quando o nível sobe, e um laço
    # `while level_up(show=False)` nunca itera. Foi assim que a simulação passou
    # a rodar sem nenhuma passiva e sem nenhuma escolha de skill.
    level_before = hero.get_level()
    while hero.xp_points >= hero.need_to_up():
        hero.level_up(show=False)
    levels_gained = hero.get_level() - level_before
    if levels_gained > 0:
        progression.on_level_up(hero, levels_gained, rng, toggles, telemetry)


def _percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(q * len(ordered)))
    return float(ordered[index])
