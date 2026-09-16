"""Uma amostra pequena do BOT_PADRÃO: poucas seeds, muitos detalhes.

Não é estatística. É o passo entre "revisei uma run inteira, decisão a decisão"
e "rodei centenas e olhei médias": com 5 seeds dá para perguntar se um
comportamento se REPETE ou se foi variância — e ainda dá para abrir o trace de
qualquer linha que chame atenção.

Nada aqui decide nada. O bot é o mesmo, sem um único `if` por classe.

    python -m tools.bot_amostra
"""

from __future__ import annotations

import argparse

from tools.bot_padrao import BotPadrao

CLASSES = ("warrior", "mage", "rogue")
SEEDS = (20260916, 20260917, 20260918, 20260919, 20260920)


def coletar(classe: str, seed: int, max_andar: int) -> dict:
    """Uma run, e o que ela deixou para trás."""
    bot = BotPadrao(classe, seed, max_andar)
    bot.jogar()
    hero = bot.hero
    fatal = bot.fatal or {}
    return {
        "classe": classe,
        "seed": seed,
        "desfecho": bot.fim.split()[0],
        "andar": int(bot.fim.split()[-1]) if bot.fim.split()[-1].isdigit() else max_andar,
        "nivel": hero.get_level(),
        "hp": hero.get_hp(),
        "hp_max": hero.base_hp,
        "mp": hero.get_mp(),
        "mp_max": hero.base_mp,
        "combates": bot.combates_na_run,
        "attack": bot.acoes.get("attack", 0),
        "skill": bot.acoes.get("skill", 0),
        "item": bot.acoes.get("item", 0),
        "flee": bot.acoes.get("flee", 0),
        "mp_gasto": bot.mp_gasto,
        "mp_disponivel": bot.mp_disponivel,
        "fatal": fatal.get("monstro", ""),
        "fatal_gap": fatal.get("gap"),
        "fatal_hp": fatal.get("hp_frac"),
        "fatal_mp": fatal.get("mp_frac"),
        "passivas": len(hero.passives),
        "skills": len(hero.skills),
    }


def _pct(valor) -> str:
    return "—" if valor is None else f"{valor:.0%}"


def _gap(valor) -> str:
    return "—" if valor is None else f"{valor:+d}"


def relatorio(linhas: list[dict]) -> list[str]:
    out = ["", "=" * 112, "BOT_PADRÃO — amostra por classe", "=" * 112]
    for classe in CLASSES:
        do_grupo = [x for x in linhas if x["classe"] == classe]
        out += ["", f"{classe.upper()}", "-" * 112]
        out.append(
            f"{'seed':>9} {'desfecho':<9} {'and':>4} {'nv':>3} {'HP fim':>10} {'MP fim':>10} "
            f"{'cbt':>4} {'atq':>4} {'skl':>4} {'itm':>4} {'fug':>4} "
            f"{'MP gasto':>14} {'fatal':<22} {'gap':>4} {'HP antes':>9}"
        )
        for x in do_grupo:
            uso = f"{x['mp_gasto']}/{x['mp_disponivel']}"
            frac = x["mp_gasto"] / x["mp_disponivel"] if x["mp_disponivel"] else 0.0
            out.append(
                f"{x['seed']:>9} {x['desfecho']:<9} {x['andar']:>4} {x['nivel']:>3} "
                f"{x['hp']:>5}/{x['hp_max']:<4} {x['mp']:>5}/{x['mp_max']:<4} "
                f"{x['combates']:>4} {x['attack']:>4} {x['skill']:>4} {x['item']:>4} "
                f"{x['flee']:>4} {uso:>9} {frac:>4.0%} {x['fatal'][:22]:<22} "
                f"{_gap(x['fatal_gap']):>4} {_pct(x['fatal_hp']):>9}"
            )
        mortes = sum(1 for x in do_grupo if x["desfecho"].startswith("MORREU"))
        andares = [x["andar"] for x in do_grupo]
        gasto = sum(x["mp_gasto"] for x in do_grupo)
        disp = sum(x["mp_disponivel"] for x in do_grupo)
        out.append(
            f"  -> {mortes}/{len(do_grupo)} mortes | andares {sorted(andares)} | "
            f"MP usado na classe: {gasto}/{disp} = {(gasto / disp if disp else 0):.0%}"
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Amostra pequena do BOT_PADRÃO.")
    parser.add_argument("--max-floor", type=int, default=20)
    args = parser.parse_args()
    linhas = [coletar(c, s, args.max_floor) for c in CLASSES for s in SEEDS]
    print("\n".join(relatorio(linhas)))


if __name__ == "__main__":
    main()
