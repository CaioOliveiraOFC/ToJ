"""Sessenta partidas JOGADAS pelo BOT_PADRÃO, com o diário de cada uma.

20 seeds × 3 classes. Nenhum resultado é calculado por fórmula: cada linha desta
tabela saiu de uma run que andou pelo mapa, colidiu com monstro, gastou MP, pagou
saída e morreu (ou não). A matemática entra DEPOIS, sobre as 60 partidas — nunca
no lugar delas.

Tudo que esta ferramenta lê já existe: o barramento de combate (`Observador`), o
livro-caixa do herói e o próprio objeto no fim da run. Nada aqui altera gameplay.

    python -m tools.bot_60
"""

from __future__ import annotations

import argparse
import statistics
from collections import Counter
from pathlib import Path

from tools.bot_padrao import BotPadrao

CLASSES = ("warrior", "mage", "rogue")
SEEDS = tuple(20260916 + i for i in range(20))
DESTINO = Path("reports/bot_60_runs_detalhado.txt")
REGUA = "_" * 100


# -- coleta ---------------------------------------------------------------


def _item(item) -> str:
    """Uma peça como ela está no exemplar: rank, pedras e encantos incluídos."""
    if item is None:
        return "—"
    partes = [f"{item.display_name} [{getattr(item, 'rarity', '?')}]"]
    if getattr(item, "socket_count", 0):
        pedras = [f"{g.gem_type} Nv{g.level}" if g is not None else "vazio" for g in item.gems]
        partes.append(f"sockets {len(item.gems)}: {', '.join(pedras)}")
    if getattr(item, "enchantments", None):
        partes.append(
            "encantos: " + ", ".join(f"{e.effect}+{e.value}" for e in item.enchantments if e)
        )
    efeito = getattr(item, "effect_type", None)
    if efeito:
        partes.append(f"{efeito} {getattr(item, 'effect_value', 0)}")
    return " | ".join(partes)


def coletar(classe: str, seed: int, max_andar: int) -> dict:
    """Uma partida inteira, jogada. Devolve o que ela deixou para trás."""
    bot = BotPadrao(classe, seed, max_andar)
    # Lida ANTES de jogar: `initial_skills_learned` é um contador, não a lista,
    # e depois do primeiro level-up não dá mais para saber com o que ele começou.
    iniciais = [s.name for s in bot.hero.skills.values()]
    bot.jogar()
    hero = bot.hero
    obs = bot.observador
    led = hero.ledger
    fatal = bot.fatal or {}

    andares = bot.por_andar
    essencias = [a["essencia_efetiva"] for a in andares]
    sorteadas = [a["essencia_sorteada"] for a in andares]
    penalizados = sum(1 for a in andares if a["essencia_efetiva"] < a["essencia_sorteada"] - 1e-9)

    gasto_por_fonte = {
        k[len("gold_spent_on_") :]: v for k, v in led.items() if k.startswith("gold_spent_on_")
    }
    ganho_por_fonte = {
        k[len("gold_from_") :]: v for k, v in led.items() if k.startswith("gold_from_")
    }

    palavra = bot.fim.split()
    return {
        "classe": classe,
        "seed": seed,
        "fim": bot.fim,
        "desfecho": palavra[0],
        "andar": int(palavra[-1]) if palavra[-1].isdigit() else max_andar,
        "andares_jogados": len(andares),
        # progressão
        "nivel": hero.get_level(),
        "xp": hero.xp_points,
        "xp_prox": hero.need_to_next(),
        "xp_para_subir": hero.need_to_up(),
        "hp": hero.get_hp(),
        "hp_max": hero.base_hp,
        "mp": hero.get_mp(),
        "mp_max": hero.base_mp,
        "st": hero.get_st(),
        "mg": hero.get_mg(),
        "ag": hero.get_ag(),
        "df": hero.get_df(),
        "passivas": [p.name for p in hero.passives],
        "skills": [f"slot {k}: {v.name}" for k, v in sorted(hero.skills.items())],
        "skills_iniciais": iniciais,
        "equipamento": {slot: _item(i) for slot, i in hero.equipment.items()},
        "equipadas": sum(1 for i in hero.equipment.values() if i),
        "mochila": [getattr(i, "name", str(i)) for i in hero.inventory],
        "gemas": len(getattr(hero, "gems", []) or []),
        # combate
        "combates": bot.combates_na_run,
        "acoes": dict(bot.acoes),
        "mp_gasto": bot.mp_gasto,
        "mp_disponivel": bot.mp_disponivel,
        "dado_total": obs.dado_total,
        "dado_max": obs.dado_max,
        "dado_min": obs.dado_min,
        "recebido_total": obs.recebido_total,
        "recebido_max": obs.recebido_max,
        "recebido_min": obs.recebido_min,
        "crit_dados": obs.crit_dados,
        "crit_recebidos": obs.crit_recebidos,
        "erros_meus": obs.erros_meus,
        "erros_deles": obs.erros_deles,
        "absorvido_egide": obs.absorvido_egide,
        "mp_egide": obs.mp_egide,
        "dot_sofrido": dict(obs.dot_sofrido),
        # essência
        "essencia_media": statistics.fmean(essencias) if essencias else 0.0,
        "essencia_min": min(essencias) if essencias else 0.0,
        "essencia_max": max(essencias) if essencias else 0.0,
        "essencia_sorteada_media": statistics.fmean(sorteadas) if sorteadas else 0.0,
        "andares_penalizados": penalizados,
        "bonus_passiva_essencia": andares[-1]["bonus_passiva"] if andares else 0,
        # economia
        "ouro": hero.coins,
        "ouro_ganho": led.get("gold_earned", 0),
        "ouro_gasto": led.get("gold_spent", 0),
        "ouro_pico": led.get("max_gold_held", 0),
        "ganho_por_fonte": ganho_por_fonte,
        "gasto_por_fonte": gasto_por_fonte,
        "compras": led.get("purchases", 0),
        "vendas": led.get("items_sold", 0),
        "drops": led.get("items_dropped", 0),
        "saidas_pagas": led.get("paid_exits", 0),
        "saidas_nao_pagas": led.get("unpaid_exits", 0),
        "streak_max": led.get("max_unpaid_exit_streak", 0),
        "juros": led.get("interest_payments", 0),
        "servicos": dict(bot.servicos),
        # morte
        "fatal": fatal,
        "por_andar": andares,
        "trace": str(bot.trace),
    }


# -- o arquivo detalhado --------------------------------------------------


def _bloco(r: dict) -> str:
    out: list[str] = []
    out.append(REGUA)
    out.append(f"RUN {r['classe'].upper()} seed {r['seed']} — {r['fim']}")
    out.append(REGUA)
    out.append("")
    out.append(r["trace"])
    out.append("")
    out.append("SNAPSHOT FINAL")
    out.append("-" * 14)
    out.append(
        f"  Nível {r['nivel']} | XP {r['xp']} de {r['xp_para_subir']} para o próximo "
        f"(faltavam {r['xp_prox']}) | "
        f"HP {r['hp']}/{r['hp_max']} | MP {r['mp']}/{r['mp_max']}"
    )
    out.append(f"  ST {r['st']}  MG {r['mg']}  AG {r['ag']}  DF {r['df']}")
    out.append(f"  Skill(s) com que começou: {', '.join(r['skills_iniciais']) or '—'}")
    out.append(f"  Skills ativas ({len(r['skills'])}): {' | '.join(r['skills']) or '—'}")
    out.append(f"  Passivas ({len(r['passivas'])}): {', '.join(r['passivas']) or 'nenhuma'}")
    out.append(f"  Equipamento ({r['equipadas']} peças):")
    for slot, texto in r["equipamento"].items():
        if texto != "—":
            out.append(f"    {slot:<10} {texto}")
    if r["equipadas"] == 0:
        out.append("    (nada equipado)")
    out.append(f"  Mochila ({len(r['mochila'])}): {', '.join(r['mochila']) or 'vazia'}")
    out.append(f"  Gemas soltas: {r['gemas']}")
    out.append("")
    out.append("COMBATE NA RUN")
    out.append("-" * 14)
    out.append(
        f"  {r['combates']} combate(s) | ações: "
        + (", ".join(f"{k} {v}x" for k, v in sorted(r["acoes"].items())) or "—")
    )
    out.append(
        f"  Dano causado: total {r['dado_total']}, maior golpe {r['dado_max']}, "
        f"menor golpe {r['dado_min'] if r['dado_min'] is not None else '—'} "
        f"(golpes que ERRARAM, contados à parte: {r['erros_meus']})"
    )
    out.append(
        f"  Dano sofrido: total {r['recebido_total']}, maior golpe {r['recebido_max']}, "
        f"menor golpe {r['recebido_min'] if r['recebido_min'] is not None else '—'} "
        f"(golpes deles que erraram: {r['erros_deles']})"
    )
    out.append(f"  Críticos: {r['crit_dados']} dados, {r['crit_recebidos']} recebidos")
    out.append(
        f"  Égide de Mana: {r['absorvido_egide']} de dano absorvido, "
        f"{r['mp_egide']} de MP consumido"
        if r["absorvido_egide"] or r["mp_egide"]
        else "  Égide de Mana: não usou"
    )
    out.append(
        "  Dano por efeito ao longo do tempo sofrido: "
        + (", ".join(f"{k} {v}" for k, v in sorted(r["dot_sofrido"].items())) or "nenhum")
    )
    out.append(f"  MP: gastou {r['mp_gasto']} dos {r['mp_disponivel']} que teve disponível")
    out.append("  Dano MITIGADO pela curva de defesa: INDISPONÍVEL — o pipeline publica")
    out.append("    o dano final, não o de antes da mitigação. Número inventado seria pior.")
    out.append("")
    out.append("ESSÊNCIA, ANDAR A ANDAR")
    out.append("-" * 23)
    out.append(
        f"  {'and':>4} {'nv':>3} {'sorteada':>9} {'streak':>7} {'efetiva':>8} "
        f"{'passiva %':>10} {'saída':>10} {'juros':>6} {'cbt':>4}"
    )
    for a in r["por_andar"]:
        paga = {True: "paga", False: "NÃO paga", None: "—"}[a["saida_paga"]]
        out.append(
            f"  {a['andar']:>4} {a['nivel']:>3} {a['essencia_sorteada']:>9.2f} "
            f"{a['streak_antes']:>7} {a['essencia_efetiva']:>8.2f} "
            f"{a['bonus_passiva']:>10.0f} {paga:>10} {a['juros']:>6} {a['combates']:>4}"
        )
    out.append("")
    out.append("ECONOMIA")
    out.append("-" * 8)
    out.append(
        f"  Ouro final {r['ouro']} | ganhou {r['ouro_ganho']} | gastou {r['ouro_gasto']} | "
        f"pico {r['ouro_pico']}"
    )
    out.append(
        "  Entrou por: "
        + (", ".join(f"{k} {v}" for k, v in sorted(r["ganho_por_fonte"].items())) or "nada")
    )
    out.append(
        "  Saiu por: "
        + (", ".join(f"{k} {v}" for k, v in sorted(r["gasto_por_fonte"].items())) or "nada")
    )
    out.append(
        f"  Compras {r['compras']} | vendas {r['vendas']} | drops {r['drops']} | "
        f"saídas pagas {r['saidas_pagas']} / não pagas {r['saidas_nao_pagas']} "
        f"(pior streak {r['streak_max']}) | cobranças de juros {r['juros']}"
    )
    out.append(
        "  Serviços usados: "
        + (", ".join(f"{k} {v}x" for k, v in sorted(r["servicos"].items())) or "nenhum")
    )
    out.append("")
    out.append("CAUSA DA MORTE")
    out.append("-" * 14)
    f = r["fatal"]
    if not f:
        out.append(f"  Não morreu — {r['fim']}.")
    else:
        golpe = f.get("golpe_final") or {}
        out.append(
            f"  {f['monstro']} (Nv{f['nivel']}, {f['gap']:+d} de nível em relação a mim), "
            f"andar {f['andar']}."
        )
        out.append(
            f"  O que estava na tela ANTES de aceitar a luta: HP {f['hp_antes']} "
            f"({f['hp_frac']:.0%}), MP {f['mp_antes']} ({f['mp_frac']:.0%})."
        )
        out.append(
            f"  A luta durou {f.get('turnos', '?')} turno(s) e tirou "
            f"{f.get('dano_no_encontro', 0)} de HP; maior golpe nela: "
            f"{f.get('maior_no_encontro', 0)}."
        )
        if golpe:
            tipo = "golpe direto" if golpe["tipo"] == "golpe" else "efeito ao longo do tempo"
            out.append(
                f"  Último dano recebido: {golpe['dano']} de {golpe['de']} ({tipo}"
                + (", CRÍTICO" if golpe["critico"] else "")
                + ")."
            )
    out.append("")
    return "\n".join(out)


# -- o resumo -------------------------------------------------------------


def _frac(a: int, b: int) -> str:
    return f"{(a / b if b else 0):.0%}"


def _num(v) -> str:
    return "—" if v is None else str(v)


def resumo(linhas: list[dict]) -> list[str]:
    out = ["", "=" * 132, "BOT_PADRÃO — 60 partidas jogadas (20 seeds × 3 classes)", "=" * 132]

    for classe in CLASSES:
        g = [x for x in linhas if x["classe"] == classe]
        out += ["", f"{classe.upper()}  ({len(g)} runs)", "-" * 132]
        out.append(
            f"{'seed':>9} {'desfecho':<8} {'and':>4} {'nv':>3} {'cbt':>4} "
            f"{'dano dado':>10} {'maior':>6} {'menor':>6} {'dano sofr':>10} {'maior':>6} "
            f"{'crit':>5} {'miss':>5} {'MP':>9} {'ouro':>6} {'eq':>3} {'ps':>3} "
            f"{'ess':>5} {'fatal':<20}"
        )
        for x in g:
            out.append(
                f"{x['seed']:>9} {x['desfecho']:<8} {x['andar']:>4} {x['nivel']:>3} "
                f"{x['combates']:>4} {x['dado_total']:>10} {x['dado_max']:>6} "
                f"{_num(x['dado_min']):>6} {x['recebido_total']:>10} {x['recebido_max']:>6} "
                f"{x['crit_dados']:>5} {x['erros_meus']:>5} "
                f"{_frac(x['mp_gasto'], x['mp_disponivel']):>9} {x['ouro']:>6} "
                f"{x['equipadas']:>3} {len(x['passivas']):>3} "
                f"{x['essencia_media']:>5.2f} {str(x['fatal'].get('monstro', '—'))[:20]:<20}"
            )
        mortes = [x for x in g if x["desfecho"] == "MORREU"]
        andares = sorted(x["andar"] for x in g)
        out.append(
            f"  -> mortes {len(mortes)}/{len(g)} | andar mediano {statistics.median(andares):.1f} "
            f"| andar máximo {max(andares)} | nível mediano "
            f"{statistics.median([x['nivel'] for x in g]):.1f} | combates medianos "
            f"{statistics.median([x['combates'] for x in g]):.1f}"
        )
        disp = sum(x["mp_disponivel"] for x in g)
        out.append(
            f"  -> MP usado na classe: {sum(x['mp_gasto'] for x in g)}/{disp} = "
            f"{_frac(sum(x['mp_gasto'] for x in g), disp)} | "
            f"skill {sum(x['acoes'].get('skill', 0) for x in g)}x, "
            f"attack {sum(x['acoes'].get('attack', 0) for x in g)}x, "
            f"item {sum(x['acoes'].get('item', 0) for x in g)}x, "
            f"flee {sum(x['acoes'].get('flee', 0) for x in g)}x"
        )
        dado = sum(x["dado_total"] for x in g)
        sofrido = sum(x["recebido_total"] for x in g)
        out.append(
            f"  -> dano dado {dado} contra {sofrido} sofrido (razão "
            f"{(dado / sofrido if sofrido else 0):.2f}) | maior golpe dado "
            f"{max(x['dado_max'] for x in g)} | maior golpe sofrido "
            f"{max(x['recebido_max'] for x in g)}"
        )
        if mortes:
            gaps = Counter(x["fatal"].get("gap") for x in mortes)
            out.append(
                "  -> gap de nível na luta fatal: "
                + ", ".join(f"{k:+d}: {v}x" for k, v in sorted(gaps.items()))
            )
            out.append(
                "  -> HP ao ACEITAR a luta fatal: mediana "
                f"{statistics.median([x['fatal']['hp_frac'] for x in mortes]):.0%}, "
                f"mínimo {min(x['fatal']['hp_frac'] for x in mortes):.0%}, "
                f"máximo {max(x['fatal']['hp_frac'] for x in mortes):.0%}"
            )
            out.append(
                "  -> MP ao ACEITAR a luta fatal: mediana "
                f"{statistics.median([x['fatal']['mp_frac'] for x in mortes]):.0%}"
            )

    n = len(linhas)
    out += ["", f"DESTAQUES — as {n} partidas juntas", "-" * 132]
    contagem = Counter(x["desfecho"] for x in linhas)
    out.append(
        f"  Morreram: {contagem['MORREU']}/{n} | extraíram por decisão: "
        f"{contagem['EXTRAIU']}/{n} | chegaram vivos ao teto de andares: "
        f"{contagem['CHEGOU']}/{n}"
    )
    for rotulo, chave, melhor in (
        ("andar mais fundo", "andar", max),
        ("nível mais alto", "nivel", max),
        ("mais combates", "combates", max),
        ("maior golpe dado", "dado_max", max),
        ("maior golpe sofrido", "recebido_max", max),
        ("mais ouro no fim", "ouro", max),
        ("mais peças equipadas", "equipadas", max),
        ("menos combates", "combates", min),
    ):
        x = melhor(linhas, key=lambda r: r[chave])
        out.append(
            f"  {rotulo:<22} {x[chave]:>6}  ({x['classe']} seed {x['seed']}, {x['fim'].lower()})"
        )
    ess = [x["essencia_media"] for x in linhas]
    out.append(
        f"  Essência efetiva média das {n} runs: {statistics.fmean(ess):.2f}x "
        f"(sorteada média {statistics.fmean([x['essencia_sorteada_media'] for x in linhas]):.2f}x) "
        f"| andares com penalidade: {sum(x['andares_penalizados'] for x in linhas)} de "
        f"{sum(x['andares_jogados'] for x in linhas)}"
    )
    mortos = [x for x in linhas if x["fatal"]]
    if mortos:
        causas = Counter(x["fatal"]["monstro"] for x in mortos)
        out.append("  Quem mais matou: " + ", ".join(f"{k} {v}x" for k, v in causas.most_common(6)))
        de_uma_vez = [
            x
            for x in mortos
            if x["fatal"].get("maior_no_encontro", 0) >= 0.5 * x["fatal"]["hp_antes"]
        ]
        out.append(
            f"  Mortes em que UM único golpe levou metade ou mais do HP que ele tinha ao "
            f"aceitar a luta: {len(de_uma_vez)}/{len(mortos)}"
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="60 partidas jogadas pelo BOT_PADRÃO.")
    p.add_argument("--max-floor", type=int, default=20)
    p.add_argument("--saida", default=str(DESTINO))
    args = p.parse_args()

    linhas = [coletar(c, s, args.max_floor) for c in CLASSES for s in SEEDS]

    destino = Path(args.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    cabecalho = (
        "BOT_PADRÃO — 60 partidas detalhadas\n"
        f"20 seeds ({SEEDS[0]}..{SEEDS[-1]}) × warrior, mage, rogue. "
        f"Teto de {args.max_floor} andares.\n"
        "Cada bloco abaixo é uma partida REALMENTE JOGADA: o diário de decisões, o\n"
        "estado final do personagem, o combate medido pelo barramento, a essência andar\n"
        "a andar, a economia e a causa da morte.\n"
    )
    destino.write_text(cabecalho + "\n" + "\n".join(_bloco(r) for r in linhas), encoding="utf-8")

    print("\n".join(resumo(linhas)))
    print(f"\nArquivo detalhado: {destino} ({len(linhas)} blocos)")


if __name__ == "__main__":
    main()
