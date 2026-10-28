"""Sonda passiva: só lê os logs reais de geração. Não executa nada."""
import json, collections, sys

FONTES = [
    ("warrior", "reports/pvp/copa_03/_trabalho/tentativas.jsonl"),
    ("warrior", "reports/pvp/copa_03/_trabalho/preenchimento.jsonl"),
    ("mage", "reports/pvp/arena_offline/_trabalho/mage/tentativas.jsonl"),
    ("rogue", "reports/pvp/arena_offline/_trabalho/rogue/tentativas.jsonl"),
]

def ler():
    for classe, f in FONTES:
        for l in open(f):
            if l.strip():
                r = json.loads(l); r["classe"] = classe; r["_fonte"] = f
                yield r

def resumo(rows, rotulo):
    n = len(rows)
    def pct(k): return f"{k}/{n} ({100*k/n:.1f}%)" if n else "-"
    c = collections.Counter()
    for r in rows:
        a = r.get("acoes") or {}; s = r.get("servicos") or {}
        c["usou_skill"] += a.get("skill", 0) > 0
        c["usou_item_combate"] += a.get("item", 0) > 0
        c["fugiu"] += a.get("flee", 0) > 0
        c["bebeu_no_mapa"] += r.get("pocoes_bebidas", 0) > 0
        c["loja"] += s.get("loja", 0) > 0
        c["ferreiro"] += s.get("ferreiro", 0) > 0
        for ev in ("fountain", "altar", "merchant"):
            c[f"evento:{ev}"] += s.get(f"evento:{ev}", 0) > 0
        c["reserva_quebrada"] += r.get("reserva_gasta", 0) > 0
        c["saida_nao_paga"] += r.get("saidas_nao_pagas", 0) > 0
        c["avaliou_extracao"] += bool(r.get("extracao"))
        c["chegou_andar3"] += r.get("andar", 0) >= 3
    tot = collections.Counter()
    for r in rows:
        for k, v in (r.get("acoes") or {}).items(): tot["acao:"+k] += v
        for k, v in (r.get("servicos") or {}).items(): tot["serv:"+k] += v
        tot["pocoes_bebidas"] += r.get("pocoes_bebidas", 0)
        tot["combates"] += r.get("combates", 0)
    print(f"\n== {rotulo}: n={n}")
    for k, v in c.items(): print(f"  {k:22s} {pct(v)}")
    print("  totais:", dict(tot))

rows = list(ler())
resumo(rows, "TODAS AS RUNS (cobertura de run completa)")
resumo([r for r in rows if r.get("desfecho") == "extraiu"], "SÓ AS EXTRAÍDAS (cobertura de build extraída)")
for cl in ("warrior", "mage", "rogue"):
    resumo([r for r in rows if r["classe"] == cl], f"classe {cl}, todas")
