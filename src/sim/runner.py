"""CLI da simulação de balanceamento.

Uso:
    python -m src.sim.runner simulate --class Warrior --level 10 \\
        --encounter elite_plus_2_trash --iterations 10000 --policy smart
    python -m src.sim.runner baseline --out reports/baseline.json
    python -m src.sim.runner matrix --iterations 2000 --format table
    python -m src.sim.runner run --classes all --iterations 500
    python -m src.sim.runner compare --against reports/baseline.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.sim.encounters import ENCOUNTERS, MATRIX_ENCOUNTERS
from src.sim.harness import ALL_CLASSES, simulate, simulate_run
from src.sim.metrics import skill_gap

DEFAULT_LEVELS = (1, 5, 10, 15, 20)


def _classes(value: str) -> list[str]:
    return list(ALL_CLASSES) if value == "all" else [c.strip() for c in value.split(",")]


def _levels(value: str) -> list[int]:
    return [int(v) for v in value.split(",")]


def _encounters(value: str) -> list[str]:
    if value == "all":
        return list(MATRIX_ENCOUNTERS)
    if value == "legacy":
        return ["legacy_monster", "legacy_boss"]
    return [e.strip() for e in value.split(",")]


def cmd_simulate(args) -> None:
    result = simulate(
        hero_class=args.hero_class,
        encounter=args.encounter,
        level=args.level,
        iterations=args.iterations,
        policy=args.policy,
        seed=args.seed,
        loadout=args.loadout,
    )
    print(result.summary())
    if args.out:
        _write(args.out, result.to_dict())


def cmd_baseline(args) -> None:
    """Congela o estado atual do jogo em números versionados.

    A baseline precisa ser gerada antes de qualquer mudança de gameplay: é o
    "antes" contra o qual todo ajuste posterior se justifica.
    """
    started = time.time()
    encounters = _encounters(args.encounters)
    rows = []
    for level in _levels(args.levels):
        for hero_class in _classes(args.classes):
            for encounter in encounters:
                for policy in args.policies.split(","):
                    result = simulate(
                        hero_class, encounter, level, args.iterations,
                        policy.strip(), args.seed, args.loadout,
                    )
                    rows.append(result.to_dict())
                    print(
                        f"Nv{level:>2} {hero_class:8} {encounter:22} {policy:6} "
                        f"WR {result.win_rate:6.1%}  turnos {result.turns_mean:5.2f}  "
                        f"HP restante {result.hp_left_pct_on_win:5.0%}"
                    )
    payload = {
        "kind": "baseline",
        "iterations": args.iterations,
        "seed": args.seed,
        "loadout": args.loadout,
        "elapsed_seconds": round(time.time() - started, 2),
        "results": rows,
    }
    if args.out:
        _write(args.out, payload)
    print(f"\n{len(rows)} cenários em {payload['elapsed_seconds']}s")


def cmd_matrix(args) -> None:
    """Matriz classe x encontro x nível, nas duas políticas.

    O que a matriz precisa provar: nenhuma linha uniforme (classe sem fraqueza),
    nenhuma coluna toda verde (encontro decorativo).
    """
    started = time.time()
    levels = _levels(args.levels)
    encounters = _encounters(args.encounters)
    classes = _classes(args.classes)
    rows = []

    for level in levels:
        if args.format == "table":
            print(f"\n=== Nível {level} — taxa de vitória (política: smart) ===")
            header = f"{'Classe':10}" + "".join(f"{e[:13]:>15}" for e in encounters)
            print(header)
        for hero_class in classes:
            cells = []
            for encounter in encounters:
                smart = simulate(hero_class, encounter, level, args.iterations, "smart",
                                 args.seed, args.loadout)
                greedy = simulate(hero_class, encounter, level, args.iterations, "greedy",
                                  args.seed, args.loadout)
                rows.append({
                    "level": level, "hero_class": hero_class, "encounter": encounter,
                    "win_rate_smart": smart.win_rate, "win_rate_greedy": greedy.win_rate,
                    "skill_gap": skill_gap(smart.win_rate, greedy.win_rate),
                    "turns_mean": smart.turns_mean,
                    "hp_left_pct_on_win": smart.hp_left_pct_on_win,
                })
                cells.append(f"{smart.win_rate:>14.1%}")
            if args.format == "table":
                print(f"{hero_class:10}" + "".join(cells))

    payload = {
        "kind": "matrix", "iterations": args.iterations, "seed": args.seed,
        "loadout": args.loadout, "elapsed_seconds": round(time.time() - started, 2),
        "results": rows,
    }
    if args.out:
        _write(args.out, payload)
    print(f"\n{len(rows)} células em {payload['elapsed_seconds']}s")


def cmd_run(args) -> None:
    """Runs completas de masmorra: a curva de dificuldade em números."""
    started = time.time()
    rows = []
    for hero_class in _classes(args.classes):
        for policy in args.policies.split(","):
            data = simulate_run(
                hero_class, args.max_floor, args.iterations, policy.strip(),
                args.seed, args.loadout,
            )
            rows.append(data)
            print(
                f"{hero_class:8} {policy:6} andar mediano {data['median_floor']:>4.0f}  "
                f"medio {data['mean_floor']:>5.1f}  chega ao {args.max_floor}: "
                f"{data['reached_20_rate']:.1%}"
            )
    payload = {
        "kind": "run", "iterations": args.iterations, "seed": args.seed,
        "loadout": args.loadout, "elapsed_seconds": round(time.time() - started, 2),
        "results": rows,
    }
    if args.out:
        _write(args.out, payload)
    print(f"\n{len(rows)} runs agregadas em {payload['elapsed_seconds']}s")


def cmd_compare(args) -> None:
    """Compara a execução atual contra uma baseline congelada."""
    reference = json.loads(Path(args.against).read_text(encoding="utf-8"))
    changed = []
    for row in reference["results"]:
        current = simulate(
            row["hero_class"], row["encounter"], row["level"],
            args.iterations or row["iterations"], row["policy"],
            reference.get("seed", 1337), row.get("loadout", "expected"),
        )
        delta = current.win_rate - row["win_rate"]
        if abs(delta) > args.tolerance:
            changed.append((row, current.win_rate, delta))
            print(
                f"Nv{row['level']:>2} {row['hero_class']:8} {row['encounter']:22} "
                f"{row['policy']:6} {row['win_rate']:.1%} -> {current.win_rate:.1%} "
                f"({delta:+.1%})"
            )
    print(f"\n{len(changed)} de {len(reference['results'])} cenários fora da tolerância "
          f"de {args.tolerance:.0%}")


def _write(path: str, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Escrito: {target}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="src.sim.runner", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p, iterations=2000):
        p.add_argument("--classes", default="all")
        p.add_argument("--levels", default=",".join(str(v) for v in DEFAULT_LEVELS))
        p.add_argument("--iterations", type=int, default=iterations)
        p.add_argument("--seed", type=int, default=1337)
        p.add_argument("--loadout", default="expected", choices=["naked", "expected", "best"])
        p.add_argument("--out")

    p_sim = sub.add_parser("simulate", help="um cenário")
    p_sim.add_argument("--class", dest="hero_class", required=True)
    p_sim.add_argument("--level", type=int, required=True)
    p_sim.add_argument("--encounter", required=True, choices=sorted(ENCOUNTERS))
    p_sim.add_argument("--iterations", type=int, default=10000)
    p_sim.add_argument("--policy", default="smart", choices=["smart", "greedy", "random"])
    p_sim.add_argument("--seed", type=int, default=1337)
    p_sim.add_argument("--loadout", default="expected", choices=["naked", "expected", "best"])
    p_sim.add_argument("--out")
    p_sim.set_defaults(func=cmd_simulate)

    p_base = sub.add_parser("baseline", help="congela o estado atual")
    common(p_base)
    p_base.add_argument("--encounters", default="legacy")
    p_base.add_argument("--policies", default="smart,greedy")
    p_base.set_defaults(func=cmd_baseline)

    p_matrix = sub.add_parser("matrix", help="matriz de interações")
    common(p_matrix)
    p_matrix.add_argument("--encounters", default="all")
    p_matrix.add_argument("--format", default="table", choices=["table", "json"])
    p_matrix.set_defaults(func=cmd_matrix)

    p_run = sub.add_parser("run", help="runs completas de masmorra")
    common(p_run, iterations=500)
    p_run.add_argument("--policies", default="smart,greedy")
    p_run.add_argument("--max-floor", type=int, default=20)
    p_run.set_defaults(func=cmd_run)

    p_cmp = sub.add_parser("compare", help="compara contra uma baseline")
    p_cmp.add_argument("--against", required=True)
    p_cmp.add_argument("--iterations", type=int, default=0)
    p_cmp.add_argument("--tolerance", type=float, default=0.03)
    p_cmp.set_defaults(func=cmd_compare)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
