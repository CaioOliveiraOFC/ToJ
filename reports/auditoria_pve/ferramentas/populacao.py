"""Builds extraídas: os 186 gladiadores publicados, população inteira (sem amostra)."""
import json
import pathlib, glob, collections, statistics as st, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from src.content.items import get_all_items
from src.sim import progression as prog
CAT = {i.name: i for i in get_all_items().values()}
arqs = sorted(f for f in glob.glob(str(pathlib.Path(__file__).resolve().parents[3]) + "/src/data/arena_populacao/*.json") if not f.endswith("indice.json"))
c = collections.Counter(); por_classe = collections.defaultdict(collections.Counter)
ouro_parado = []; frac_parado = []; gastos = collections.Counter(); fam = collections.Counter()
pocoes = collections.Counter(); perda_arma = []
for f in arqs:
    d = json.load(open(f)); cl = d["player_class"]; k = por_classe[cl]; k["n"] += 1; c["n"] += 1
    eq = {p: v for p, v in d["equipment"].items() if v}
    mais = [v.get("enhancement_level", 0) for v in eq.values()]
    armas = {p: v for p, v in eq.items() if p.startswith("Weapon")}
    for chave, cond in (
        ("alguma_peca_+N", any(m > 0 for m in mais)),
        ("arma_+N", any(v.get("enhancement_level", 0) > 0 for v in armas.values())),
        ("gema_engastada", any(any(g for g in (v.get("gems") or [])) for v in eq.values())),
        ("socket_vazio_equipado", any((v.get("socket_count", 0) or 0) > len([g for g in (v.get("gems") or []) if g]) for v in eq.values())),
        ("gema_parada_na_bolsa", len(d.get("gems") or []) > 0),
        ("encantamento", any(v.get("enchantments") for v in eq.values())),
        ("starter_ainda_equipado", any(v.get("origin") == "starter" for v in eq.values())),
        ("epic_ou_legendary_equipado", any(str(getattr(CAT.get(v["name"]), "rarity", "")) in ("Epic", "Legendary") for v in eq.values())),
        ("reencantou", d["ledger"].get("gold_spent_on_reenchant", 0) > 0),
        ("retirou_gema", d["ledger"].get("gold_spent_on_unsocket", 0) > 0),
        ("reroll_loja", d["ledger"].get("gold_spent_on_shop_reroll", 0) > 0),
        ("reroll_skill_ou_passiva", d["ledger"].get("gold_spent_on_skill_reroll", 0) + d["ledger"].get("gold_spent_on_passive_reroll", 0) > 0),
        ("recuperacao_paga", d["ledger"].get("gold_spent_on_recovery", 0) > 0),
        ("vendeu", d["ledger"].get("items_sold", 0) > 0),
    ):
        c[chave] += bool(cond); k[chave] += bool(cond)
    c["pecas_+N"] += sum(1 for m in mais if m > 0); c["pecas_equipadas"] += len(eq)
    c["max_+N"] = max(c["max_+N"], max(mais) if mais else 0)
    # mochila x pior ocupante
    melhor = False
    for it in d.get("inventory") or []:
        cat = CAT.get(it["name"])
        if cat is None or getattr(cat, "consumable", False):
            if cat is not None: pocoes[str(cat.effect_type)] += 1
            continue
        if getattr(cat, "classes", None) and cl not in cat.classes: continue
        slot = str(cat.slot)
        pos = [p for p in eq if p.rstrip("12") == slot] if slot in ("Weapon", "Ring") else [slot]
        ocup = [CAT.get(eq[p]["name"]) for p in pos if p in eq]
        if len(ocup) < (2 if slot in ("Weapon", "Ring") else 1): continue
        pior = min(prog._peso_do_item(o) for o in ocup if o is not None)
        if prog._peso_do_item(cat) > pior:
            melhor = True
            if slot == "Weapon":
                eqp = sum(float(CAT[eq[p]["name"]].damage_bonus) for p in pos)
                perda_arma.append(float(cat.damage_bonus) - min(float(CAT[eq[p]["name"]].damage_bonus) for p in pos))
    c["peca_melhor_na_mochila"] += melhor; k["peca_melhor_na_mochila"] += melhor
    L = d["ledger"]; ouro_parado.append(d["coins"]); frac_parado.append(d["coins"] / max(1, L.get("gold_earned", 1)))
    for kk, vv in L.items():
        if kk.startswith("gold_spent_on_"): gastos[kk[14:]] += vv
    for p in d.get("passives") or []:
        fam[p.get("effect_type") if isinstance(p, dict) else str(p)] += 1
n = c["n"]
print(f"gladiadores: {n}", {cl: k["n"] for cl, k in por_classe.items()})
for chave in ("alguma_peca_+N","arma_+N","gema_engastada","socket_vazio_equipado","gema_parada_na_bolsa","encantamento","reencantou","retirou_gema","reroll_loja","reroll_skill_ou_passiva","recuperacao_paga","vendeu","starter_ainda_equipado","epic_ou_legendary_equipado","peca_melhor_na_mochila"):
    print(f"  {chave:28s} {c[chave]:3d}/{n} ({100*c[chave]/n:5.1f}%)  " + "  ".join(f"{cl[:1]} {k[chave]}/{k['n']}" for cl, k in sorted(por_classe.items())))
print(f"  peças equipadas com +N: {c['pecas_+N']}/{c['pecas_equipadas']} ({100*c['pecas_+N']/c['pecas_equipadas']:.1f}%), maior +N {c['max_+N']}")
print(f"  ouro parado no fim: mediana {st.median(ouro_parado):.0f}, P90 {sorted(ouro_parado)[int(.9*n)]}, máx {max(ouro_parado)}; fração do ouro ganho: mediana {st.median(frac_parado):.1%}")
print("  gasto total por destino:", dict(gastos.most_common()))
print("  consumíveis na mochila no fim:", dict(pocoes))
print(f"  armas melhores na mochila: {len(perda_arma)} casos, ganho de dano% mediana {st.median(perda_arma) if perda_arma else 0}, máx {max(perda_arma) if perda_arma else 0}")
print("  famílias de passiva (todas as cartas):", dict(fam.most_common()))
