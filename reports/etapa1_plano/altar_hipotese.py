"""Hipótese D1: bênção = +15% de dano (`damage_percent` no +MULT) por 5 turnos.

Só simulação, sem tocar `src/`. Para cada seed, o mesmo herói passa por DUAS lutas
seguidas do plano do andar (o trecho que a bênção alcança), em três braços:
  A  sem Altar, HP cheio;
  B  paga 30% do HP máximo e recebe a bênção (a decisão real do jogador);
  C  recebe a bênção sem pagar (isola o benefício).
Pareado: o mesmo `random.seed` para os decks e o mesmo `Random(seed)` na luta.
Uma morte conta como 0% de HP. Rodar da raiz do repositório:
    python reports/etapa1_plano/altar_hipotese.py
"""

import pathlib
import random
import statistics as st
import sys
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.content.factories.dungeons import altar_hp_cost  # noqa: E402
from src.mechanics.battle import run_battle  # noqa: E402
from src.sim.encounters import build_encounter  # noqa: E402
from src.sim.harness import _default_floor_plan, make_hero  # noqa: E402
from src.sim.policies import get_policy  # noqa: E402

decide = get_policy("smart")
SEEDS = range(300)


def trecho(classe, andar, seed, braco):
    random.seed(seed * 7919 + andar)
    plano = _default_floor_plan(andar, random.Random(seed))
    heroi = make_hero(classe, andar, "expected")
    if braco == "B":
        heroi.take_damage(altar_hp_cost(heroi))
    if braco in ("B", "C"):
        heroi.active_buffs["Benção do Altar"] = {
            "stat": "damage_percent",
            "value": 15,
            "duration": 5,
        }
    r = random.Random(seed)
    for nome in plano[:2]:
        random.seed(seed * 104729 + zlib.crc32(nome.encode()) % 1000)
        monstros = build_encounter(nome, andar)
        run_battle(heroi, monstros, lambda h, m, t: decide(h, m, t), rng=r, publish=None)
        if heroi.get_hp() <= 0 or not heroi.get_isalive():
            return 0.0, True
    return heroi.get_hp() / heroi.base_hp, False


print("classe andar | ΔHP% B-A (paga+bênção) | ΔHP% C-A (só bênção) | morte A / B / C")
for classe in ("Warrior", "Mage", "Rogue"):
    for andar in (3, 8, 14, 20):
        res = {b: [trecho(classe, andar, s, b) for s in SEEDS] for b in "ABC"}
        hp = {b: [x[0] for x in res[b]] for b in "ABC"}
        mortes = {b: sum(x[1] for x in res[b]) for b in "ABC"}
        dba = [b - a for a, b in zip(hp["A"], hp["B"])]
        dca = [c - a for a, c in zip(hp["A"], hp["C"])]
        ep = lambda xs: st.stdev(xs) / len(xs) ** 0.5  # noqa: E731
        print(
            f"{classe:7s} {andar:2d}    | {100 * st.fmean(dba):+6.1f} (±{196 * ep(dba):.1f})"
            f"        | {100 * st.fmean(dca):+6.1f} (±{196 * ep(dca):.1f})      "
            f"| {mortes['A']}/{mortes['B']}/{mortes['C']} de {len(SEEDS)}"
        )
