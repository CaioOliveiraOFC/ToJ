"""Mede o novo loop do andar: taxa de saída, punição de Essência e serviços.

Sair custa. Quem não paga sobe do mesmo jeito e perde Essência no andar
seguinte, até um piso. Nada disso é balanceamento ainda — são calibrações V1, e
esta ferramenta existe para elas passarem a ter número.

Duas runs sintéticas, além da simulação completa:

- **covarde**: contorna tudo, não visita nada, nunca extrai, sempre sobe. Mede
  o custo progressivo de fugir — e prova que fugir não trava.
- **recuperação**: acumula saídas não pagas, depois consegue pagar uma. Mede se
  a punição realmente acaba na hora.

Uso: `python tools/measure_floor_loop.py [runs]`
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.economy import exit_fee  # noqa: E402
from src.content.factories.features import roll_features  # noqa: E402
from src.content.floor_exit import current_penalty, effective_essence, use_exit  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.mechanics.math_operations import generate_essence_multiplier  # noqa: E402
from src.shared.constants import ESSENCE_PENALTY_FLOOR  # noqa: E402


def _heroi(capital: int) -> Warrior:
    h = Warrior("Medidor")
    h.set_level(10)
    if capital:
        h.earn_coins(capital, "combat")
    return h


def run_covarde(andares: int = 20, capital_inicial: int = 0, seed: int = 11) -> dict:
    """Sobe sem lutar, sem comprar e sem extrair. Só paga se já tiver ouro."""
    rng = random.Random(seed)
    heroi = _heroi(capital_inicial)
    sorteadas: list[float] = []
    efetivas: list[float] = []
    no_piso = 0

    for andar in range(1, andares + 1):
        rolled = generate_essence_multiplier(andar)
        efetiva = effective_essence(heroi, rolled)
        sorteadas.append(rolled)
        efetivas.append(efetiva)
        if efetiva <= ESSENCE_PENALTY_FLOOR:
            no_piso += 1
        roll_features(heroi, andar, rng)
        use_exit(heroi, andar)

    return {
        "andares": andares,
        "streak": heroi.unpaid_exit_streak,
        "penalidade": current_penalty(heroi),
        "essencia_sorteada": statistics.fmean(sorteadas),
        "essencia_efetiva": statistics.fmean(efetivas),
        "essencia_efetiva_min": min(efetivas),
        "andares_no_piso": no_piso,
        "ouro_final": heroi.coins,
    }


def run_recuperacao(faltas: int = 4, andar: int = 10) -> dict:
    """Acumula saídas não pagas e depois consegue pagar uma."""
    heroi = _heroi(0)
    for _ in range(faltas):
        use_exit(heroi, andar)
    antes = {
        "streak": heroi.unpaid_exit_streak,
        "penalidade": current_penalty(heroi),
        "essencia_de_um_roll_1_5": effective_essence(heroi, 1.5),
    }

    heroi.earn_coins(exit_fee(andar), "combat")
    pagou = use_exit(heroi, andar).was_paid

    return {
        "antes": antes,
        "pagou": pagou,
        "streak_depois": heroi.unpaid_exit_streak,
        "penalidade_depois": current_penalty(heroi),
        "essencia_depois": effective_essence(heroi, 1.5),
    }


def medir_runs(runs: int = 60) -> dict:
    """A simulação completa, com combate, loja, ferreiro e tudo o mais."""
    from src.sim.harness import simulate_run

    r = simulate_run("Warrior", max_floor=20, iterations=runs, policy="smart", seed=4242)
    return r["telemetry"]


def main(runs: int = 60) -> None:
    print("=== RUN COVARDE (contorna tudo, nunca paga, nunca extrai) ===\n")
    print(
        f"{'andares':>8} {'streak':>7} {'penalid.':>9} "
        f"{'roll méd':>9} {'efetiva':>8} {'no piso':>8}"
    )
    for andares in (5, 10, 20, 30):
        d = run_covarde(andares=andares)
        print(
            f"{d['andares']:>8} {d['streak']:>7} {d['penalidade']:>9.1f} "
            f"{d['essencia_sorteada']:>9.2f} {d['essencia_efetiva']:>8.2f} "
            f"{d['andares_no_piso']:>7}/{d['andares']}"
        )
    print("\nA run NUNCA trava: ela continua, e vai ficando menos eficiente.")

    print("\n=== RUN DE RECUPERAÇÃO (4 saídas não pagas, depois paga uma) ===\n")
    d = run_recuperacao()
    a = d["antes"]
    print(
        f"  antes : streak {a['streak']} | penalidade -{a['penalidade']:.1f}x "
        f"| roll 1,5x vira {a['essencia_de_um_roll_1_5']:.1f}x"
    )
    print(f"  pagou : {d['pagou']}")
    print(
        f"  depois: streak {d['streak_depois']} | penalidade -{d['penalidade_depois']:.1f}x "
        f"| roll 1,5x vira {d['essencia_depois']:.1f}x"
    )

    print(f"\n=== SIMULAÇÃO COMPLETA ({runs} runs, 20 andares, seed 4242) ===\n")
    tel = medir_runs(runs)
    saida, ess, feats = tel["exit"], tel["essence"], tel["features"]
    total = saida["paid"] + saida["unpaid"]
    print(f"  saídas pagas        : {saida['paid']:>6} ({saida['paid'] / max(1, total):.0%})")
    print(f"  saídas não pagas    : {saida['unpaid']:>6} ({saida['unpaid'] / max(1, total):.0%})")
    print(f"  ouro em taxa        : {saida['fee_paid'] / runs:>6.0f} por run")
    print(f"  sequências (streak) : {dict(sorted(saida['streaks'].items()))}")
    print()
    rolls = ess["rolls"] or 1
    print(f"  Essência sorteada   : {ess['sum'] / rolls:>6.2f}")
    print(f"  Essência efetiva    : {ess['effective_sum'] / rolls:>6.2f}")
    print(f"  andares no piso 0,5x: {ess['floor_hits']:>6} de {ess['rolls']}")
    print()
    andares_vistos = sum(feats["spawned"].values()) and rolls
    for nome in ("shop", "forge", "extraction"):
        visto = feats["spawned"].get(nome, 0)
        print(f"  {nome:<11} apareceu: {visto:>6} ({visto / andares_vistos:.0%} dos andares)")
    print(f"  maior seca de Extração: {feats.get('max_extraction_drought', 0)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
