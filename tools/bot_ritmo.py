"""Quanto o RITMO DE COMBATE muda a progressão da run.

Um experimento com uma variável só: o apetite do jogador por luta NO MAPA. Os
três perfis usam a mesma `smart_policy` dentro do duelo — mesma cura, mesma
fuga, mesmo uso de skill, mesmo alvo. Nenhum número do jogo é tocado.

    conservador  o BOT_PADRÃO de sempre, sem um limiar mexido
    moderado     aceita luta em condição razoável, não só quando está ótimo
    hardcore     acumula poder enquanto conseguir, e desiste quando não dá

    python -m tools.bot_ritmo
"""

from __future__ import annotations

import argparse

from tools.bot_padrao import PERFIS, BotPadrao

CLASSES = ("warrior", "mage", "rogue")
ORDEM = ("conservador", "moderado", "hardcore")


def coletar(classe: str, perfil: str, seed: int, max_andar: int) -> dict:
    bot = BotPadrao(classe, seed, max_andar, PERFIS[perfil])
    bot.jogar()
    hero, led = bot.hero, bot.hero.ledger
    oferecidos = sum(a["oferecidos"] for a in bot.por_andar)
    fatal = bot.fatal or {}
    return {
        "classe": classe,
        "perfil": perfil,
        "desfecho": bot.fim.split()[0],
        "andar": max(a["andar"] for a in bot.por_andar) if bot.por_andar else 0,
        "nivel": hero.get_level(),
        "xp": hero.xp_points,
        "combates": bot.combates_na_run,
        "oferecidos": oferecidos,
        "taxa": bot.combates_na_run / oferecidos if oferecidos else 0.0,
        "ganho": led.get("gold_earned", 0),
        "gasto": led.get("gold_spent", 0),
        "loot": led.get("items_dropped", 0),
        "equipou": led.get("items_equipped", 0),
        "gemas": led.get("gems_found", 0),
        "passivas": len(hero.passives),
        "skills": len(hero.skills),
        "lojas": bot.servicos.get("loja", 0),
        "ferreiros": bot.servicos.get("ferreiro", 0),
        "eventos": sum(v for k, v in bot.servicos.items() if k.startswith("evento:")),
        "pagas": led.get("paid_exits", 0),
        "nao_pagas": led.get("unpaid_exits", 0),
        "curva": [(a["andar"], a["nivel"]) for a in bot.por_andar],
        "por_andar": bot.por_andar,
        "fatal": fatal,
        "lutas_no_andar_fatal": (bot.por_andar[-1]["combates"] if bot.por_andar else 0),
    }


def relatorio(linhas: list[dict]) -> list[str]:
    out = ["", "=" * 100, "RITMO DE COMBATE — 1 seed, 3 classes, 3 perfis", "=" * 100, ""]
    out.append(
        f"{'classe':<8} {'perfil':<12} {'desfecho':<9} {'andar':>6} {'nível':>6} "
        f"{'combates':>9} {'disponíveis':>12} {'taxa':>6}"
    )
    out.append("-" * 100)
    for linha in linhas:
        out.append(
            f"{linha['classe']:<8} {linha['perfil']:<12} {linha['desfecho']:<9} "
            f"{linha['andar']:>6} {linha['nivel']:>6} {linha['combates']:>9} "
            f"{linha['oferecidos']:>12} {linha['taxa']:>5.0%}"
        )

    out += ["", "PROGRESSÃO E ECONOMIA", "-" * 100]
    out.append(
        f"{'classe':<8} {'perfil':<12} {'ganho':>7} {'gasto':>7} {'loot':>5} {'equip':>6} "
        f"{'gemas':>6} {'pass':>5} {'skl':>4} {'loja':>5} {'ferr':>5} {'evt':>4} "
        f"{'pagas':>6} {'n.pagas':>8}"
    )
    for linha in linhas:
        out.append(
            f"{linha['classe']:<8} {linha['perfil']:<12} {linha['ganho']:>7} "
            f"{linha['gasto']:>7} {linha['loot']:>5} {linha['equipou']:>6} "
            f"{linha['gemas']:>6} {linha['passivas']:>5} {linha['skills']:>4} "
            f"{linha['lojas']:>5} {linha['ferreiros']:>5} {linha['eventos']:>4} "
            f"{linha['pagas']:>6} {linha['nao_pagas']:>8}"
        )

    out += ["", "ANDAR x NÍVEL (nível ao ENTRAR em cada andar)", "-" * 100]
    for linha in linhas:
        pares = " ".join(f"{a}:{n}" for a, n in linha["curva"])
        out.append(f"{linha['classe']:<8} {linha['perfil']:<12} {pares}")

    out += ["", "COMBATE POR ANDAR — oferecidos/feitos", "-" * 100]
    for linha in linhas:
        pares = " ".join(
            f"{a['andar']}:{a['combates']}/{a['oferecidos']}" for a in linha["por_andar"]
        )
        out.append(f"{linha['classe']:<8} {linha['perfil']:<12} {pares}")

    out += ["", "MORTES", "-" * 100]
    for linha in linhas:
        f = linha["fatal"]
        if not f:
            out.append(f"{linha['classe']:<8} {linha['perfil']:<12} — sobreviveu")
            continue
        out.append(
            f"{linha['classe']:<8} {linha['perfil']:<12} andar {f['andar']}, herói Nv"
            f"{f['nivel'] - f['gap']}, {f['monstro']} Nv{f['nivel']} (gap {f['gap']:+d}), "
            f"HP {f['hp_antes']} ({f['hp_frac']:.0%}), MP {f['mp_frac']:.0%}, "
            f"{linha['lutas_no_andar_fatal']} luta(s) já feitas nesse andar"
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Ritmo de combate do BOT_PADRÃO.")
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--max-floor", type=int, default=50)
    args = parser.parse_args()
    linhas = [
        coletar(classe, perfil, args.seed, args.max_floor) for classe in CLASSES for perfil in ORDEM
    ]
    print("\n".join(relatorio(linhas)))


if __name__ == "__main__":
    main()
