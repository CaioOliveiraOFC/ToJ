"""Agrega a baseline de 3.000 runs. Le, conta e imprime. Nao decide nada.

Proporcao importante vem com intervalo de Wilson 95%. Celula com 0, 1 ou 2
ocorrencias e reportada com o denominador ao lado e NUNCA lida como padrao.
"""

import glob
import json
import math
import sys
from collections import Counter, defaultdict

CLASSES = ("warrior", "mage", "rogue")
BANDAS = ("ABAIXO", "CLOSE_ENOUGH", "META_BATIDA", "HARD_STOP", "NAO_MEDIDO")
ESTADOS = ("SAUDAVEL", "CURTO", "ESGOTADO", "SEM_EVIDENCIA")
FAIXAS = ((3, 6), (7, 10), (11, 14), (15, 20))


def wilson(k: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    z = 1.959963985
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, centro - meia), min(1.0, centro + meia))


def pct(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    return f"{100 * p:5.1f}% [{100 * lo:4.1f};{100 * hi:4.1f}]  {k}/{n}"


def perc(xs, q):
    if not xs:
        return None
    ys = sorted(xs)
    i = (len(ys) - 1) * q
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return ys[lo] if lo == hi else ys[lo] + (ys[hi] - ys[lo]) * (i - lo)


def linha_perc(rotulo, xs, fmt="{:.2f}"):
    if not xs:
        print(f"  {rotulo:<22} n=0")
        return
    vals = [perc(xs, q) for q in (0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0)]
    print(f"  {rotulo:<22} n={len(xs):<6} " + "  ".join(fmt.format(v) for v in vals))


def faixa_de(andar: int) -> str | None:
    for a, b in FAIXAS:
        if a <= andar <= b:
            return f"{a}-{b}"
    return None


def titulo(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def sub(t):
    print()
    print(f"-- {t} " + "-" * max(0, 74 - len(t)))


def main():
    padrao = sys.argv[1] if len(sys.argv) > 1 else "bl_*.jsonl"
    runs, oport, avals = [], [], []
    for caminho in sorted(glob.glob(padrao)):
        with open(caminho) as f:
            for linha in f:
                try:
                    r = json.loads(linha)
                except json.JSONDecodeError:
                    continue  # ultima linha truncada de um shard vivo
                {"run": runs, "oportunidade": oport, "avaliacao": avals}.get(r["tipo"], []).append(
                    r
                )

    titulo(f"BASELINE — {len(runs)} runs, {len(oport)} oportunidades, {len(avals)} avaliacoes")
    seeds = {r["seed"] for r in runs}
    print(f"seeds distintas: {len(seeds)}  ({min(seeds)}..{max(seeds)})")
    por_classe = {c: [r for r in runs if r["classe"] == c] for c in CLASSES}
    print("runs por classe: " + "  ".join(f"{c}={len(v)}" for c, v in por_classe.items()))
    erros = [r for r in runs if r["desfecho"].startswith("ERRO")]
    if erros:
        print(f"!! runs com excecao: {len(erros)}")
        for e in Counter(r["desfecho"] for r in erros).most_common(5):
            print(f"   {e[1]:4d}x {e[0][:90]}")

    # ------------------------------------------------------------------ 1
    titulo("1. DESFECHO POR CLASSE")
    print(f"{'':<9}{'MORREU':<28}{'EXTRAIU':<28}{'CHEGOU AO 20':<28}")
    for c in CLASSES + ("TODAS",):
        rs = runs if c == "TODAS" else por_classe[c]
        n = len(rs)
        m = sum(1 for r in rs if r["desfecho"] == "MORREU")
        e = sum(1 for r in rs if r["desfecho"] == "EXTRAIU")
        v = sum(1 for r in rs if r["chegou_ao_20"])
        print(f"{c:<9}{pct(m, n):<28}{pct(e, n):<28}{pct(v, n):<28}")
    print()
    print(
        "desfechos crus: "
        + "  ".join(f"{k}={v}" for k, v in Counter(r["desfecho"] for r in runs).most_common())
    )

    sub("sobrevivencia: quem termina a run vivo (extraiu OU chegou ao 20)")
    for c in CLASSES + ("TODAS",):
        rs = runs if c == "TODAS" else por_classe[c]
        viv = sum(1 for r in rs if r["desfecho"] != "MORREU")
        print(f"  {c:<9}{pct(viv, len(rs))}")

    # ------------------------------------------------------------------ 2
    titulo("2. ANDAR FINAL E NIVEL")
    print(f"  {'':<22}{'n':<8}{'min':<8}{'p10':<8}{'p25':<8}{'p50':<8}{'p75':<8}{'p90':<8}{'max'}")
    for c in CLASSES + ("TODAS",):
        rs = runs if c == "TODAS" else por_classe[c]
        linha_perc(f"andar final {c}", [r["andar_final"] for r in rs], "{:6.1f}")
    print()
    for c in CLASSES + ("TODAS",):
        rs = runs if c == "TODAS" else por_classe[c]
        linha_perc(f"nivel final {c}", [r["build"]["nivel"] for r in rs], "{:6.1f}")
    print()
    for c in CLASSES + ("TODAS",):
        rs = runs if c == "TODAS" else por_classe[c]
        linha_perc(f"combates {c}", [r["combates"] for r in rs], "{:6.1f}")

    sub("onde a run morre: histograma do andar final (todas as classes)")
    hist = Counter(r["andar_final"] for r in runs)
    total = len(runs)
    acum = 0
    for andar in sorted(hist):
        acum += hist[andar]
        barra = "#" * int(60 * hist[andar] / max(hist.values()))
        print(
            f"  andar {andar:>2}  {hist[andar]:>5}  {100 * hist[andar] / total:5.1f}%  "
            f"acum {100 * acum / total:5.1f}%  {barra}"
        )

    sub("mortalidade condicional: entrou no andar e morreu nele")
    entrou = {a: sum(1 for r in runs if r["andar_final"] >= a) for a in range(1, 21)}
    morreu = {
        a: sum(1 for r in runs if r["andar_final"] == a and r["desfecho"] == "MORREU")
        for a in range(1, 21)
    }
    for a in range(1, 21):
        if entrou[a]:
            print(f"  andar {a:>2}  {pct(morreu[a], entrou[a])}")

    # ------------------------------------------------------------------ 3
    titulo("3. MATRIZ 4x3 DE EXTRACAO")
    for rotulo, fonte, kb, ke, kd in (
        (
            "PRIMEIRA avaliacao de cada oportunidade unica",
            oport,
            "banda_ini",
            "estado_ini",
            "decisao_ini",
        ),
        ("TODAS as avaliacoes", avals, "banda", "estado", None),
    ):
        sub(rotulo)
        grade = defaultdict(lambda: [0, 0])  # [n, preservou]
        for x in fonte:
            b, e = x[kb], x[ke]
            pres = (x[kd] == "EXTRAI") if kd else bool(x["preservou"])
            g = grade[(b, e)]
            g[0] += 1
            g[1] += int(pres)
        print(f"  {'':<14}" + "".join(f"{e:<20}" for e in ESTADOS))
        for b in BANDAS:
            celulas = []
            for e in ESTADOS:
                n, k = grade[(b, e)]
                celulas.append(
                    "-"
                    if n == 0
                    else f"{k}/{n} {'PRES' if k == n else ('cont' if k == 0 else 'MISTO')}"
                )
            print(f"  {b:<14}" + "".join(f"{c:<20}" for c in celulas))
        n_tot = sum(v[0] for v in grade.values())
        ocupadas = sum(1 for v in grade.values() if v[0])
        print(f"  total {n_tot}   celulas ocupadas {ocupadas}/{len(BANDAS) * len(ESTADOS)}")
        print(
            "  bandas:  "
            + "  ".join(f"{b}={sum(grade[(b, e)][0] for e in ESTADOS)}" for b in BANDAS)
        )
        print(
            "  estados: "
            + "  ".join(f"{e}={sum(grade[(b, e)][0] for b in BANDAS)}" for e in ESTADOS)
        )

    sub("snapshot INICIAL x snapshot DA EXTRACAO (oportunidades que extrairam)")
    venceu = [o for o in oport if o["banda_na_extracao"]]
    print(f"  oportunidades em que a extracao venceu: {len(venceu)} de {len(oport)}")
    mudou_banda = [o for o in venceu if o["banda_na_extracao"] != o["banda_ini"]]
    print(
        "  banda mudou entre a primeira avaliacao e a vencedora: "
        + pct(len(mudou_banda), len(venceu))
    )
    for o in mudou_banda[:10]:
        print(
            f"    {o['classe']:<8} seed {o['seed']} andar {o['andar']:>2}: "
            f"{o['banda_ini']}/{o['estado_ini']} -> "
            f"{o['banda_na_extracao']}/{o['estado_na_extracao']}"
        )

    # ------------------------------------------------------------------ 4
    titulo("4. DISTRIBUICAO DE PODER E RUNWAY")
    print(f"  {'':<22}{'n':<8}{'min':<8}{'p10':<8}{'p25':<8}{'p50':<8}{'p75':<8}{'p90':<8}{'max'}")
    sub("poder relativo (so onde foi medido naturalmente)")
    linha_perc("todas as avaliacoes", [a["poder"] for a in avals if a["poder"] > 0], "{:6.3f}")
    for c in CLASSES:
        linha_perc(
            f"  {c}", [a["poder"] for a in avals if a["classe"] == c and a["poder"] > 0], "{:6.3f}"
        )
    linha_perc(
        "ultimo poder da run",
        [r["poder_relativo_ultimo"] for r in runs if r["poder_relativo_ultimo"]],
        "{:6.3f}",
    )
    linha_perc(
        "poder ABSOLUTO (cache)",
        [r["poder_absoluto_build_final"] for r in runs if r["poder_absoluto_build_final"]],
        "{:6.2f}",
    )
    medido = sum(1 for r in runs if r["poder_relativo_ultimo"])
    print(f"  runs com poder medido de graca: {pct(medido, len(runs))}")

    sub("runway em andares")
    linha_perc(
        "todas as avaliacoes", [a["runway"] for a in avals if a["runway"] is not None], "{:6.2f}"
    )
    for c in CLASSES:
        linha_perc(
            f"  {c}",
            [a["runway"] for a in avals if a["classe"] == c and a["runway"] is not None],
            "{:6.2f}",
        )
    sub("runway por faixa de andar")
    for a, b in FAIXAS:
        linha_perc(
            f"andares {a}-{b}",
            [x["runway"] for x in avals if x["runway"] is not None and a <= x["andar"] <= b],
            "{:6.2f}",
        )

    # ------------------------------------------------------------------ 5
    titulo("5. COMPORTAMENTO POR FAIXA DE ANDAR")
    print(f"  {'faixa':<10}{'oport':<8}{'aval':<8}{'PRES':<26}{'bandas'}")
    for a, b in FAIXAS:
        ops = [o for o in oport if a <= o["andar"] <= b]
        avs = [x for x in avals if a <= x["andar"] <= b]
        pres = sum(1 for o in ops if o["decisao_ini"] == "EXTRAI")
        bd = Counter(o["banda_ini"] for o in ops)
        print(
            f"  {f'{a}-{b}':<10}{len(ops):<8}{len(avs):<8}{pct(pres, len(ops)):<26}"
            + " ".join(f"{k}={v}" for k, v in bd.most_common())
        )
    print()
    print(f"  {'faixa':<10}{'estados do runway'}")
    for a, b in FAIXAS:
        ops = [o for o in oport if a <= o["andar"] <= b]
        st = Counter(o["estado_ini"] for o in ops)
        print(
            f"  {f'{a}-{b}':<10}"
            + " ".join(f"{k}={v} ({100 * v / max(1, len(ops)):.0f}%)" for k, v in st.most_common())
        )

    sub("oportunidades por andar e o que aconteceu depois")
    print(f"  {'andar':<7}{'oport':<8}{'extraiu aqui':<16}{'abandonou':<12}{'morreu no andar'}")
    for andar in range(1, 21):
        ops = [o for o in oport if o["andar"] == andar]
        if not ops:
            continue
        d = Counter(o["desfecho"] for o in ops)
        print(
            f"  {andar:<7}{len(ops):<8}{d['extraiu_aqui']:<16}"
            f"{d['abandonou_andar']:<12}{d['morreu_no_andar']}"
        )

    # ------------------------------------------------------------------ 6
    titulo("6. SKILLS, PASSIVAS E EQUIPAMENTO")

    sub("SKILLS: oferecida x escolhida (taxa de captura)")
    ofer, esco = Counter(), Counter()
    for r in runs:
        for o in r["ofertas_skill"]:
            for s in o["oferecidas"]:
                ofer[s] += 1
            if o["escolhida"]:
                esco[o["escolhida"]] += 1
    recusas = sum(1 for r in runs for o in r["ofertas_skill"] if o["escolhida"] is None)
    total_ofertas = sum(len(r["ofertas_skill"]) for r in runs)
    print(
        f"  ofertas de skill: {total_ofertas}   "
        f"recusadas por completo: {pct(recusas, total_ofertas)}"
    )
    print(f"  {'skill':<26}{'oferecida':<12}{'escolhida':<12}{'captura'}")
    for s, n in ofer.most_common():
        print(f"  {s:<26}{n:<12}{esco[s]:<12}{pct(esco[s], n)}")

    sub("SKILLS: uso real (no deck final x turnos gastos)")
    no_deck, usos, dano, mp = Counter(), Counter(), Counter(), Counter()
    for r in runs:
        for s in r["build"]["skills"]:
            no_deck[s] += 1
        for s, v in r["skill_usos"].items():
            usos[s] += v
        for s, v in r["skill_dano"].items():
            dano[s] += v
        for s, v in r["skill_mp"].items():
            mp[s] += v
    print(
        f"  {'skill':<26}{'no deck':<10}{'usos':<10}{'usos/deck':<12}"
        f"{'dano':<12}{'mp':<10}{'dano/mp'}"
    )
    for s, n in no_deck.most_common():
        u = usos[s]
        dpm = dano[s] / mp[s] if mp[s] else 0.0
        print(f"  {s:<26}{n:<10}{u:<10}{u / n:<12.1f}{dano[s]:<12}{mp[s]:<10}{dpm:.1f}")
    mortas = [s for s in no_deck if usos[s] == 0]
    if mortas:
        print(
            f"  ** no deck e NUNCA usadas: {len(mortas)} -> "
            + ", ".join(f"{s} ({no_deck[s]}x)" for s in mortas)
        )

    sub("PASSIVAS: oferecida x escolhida (taxa de captura)")
    pofer, pesco = Counter(), Counter()
    for r in runs:
        for o in r["ofertas_passiva"]:
            for p in o["oferecidas"]:
                pofer[p] += 1
            if o["escolhida"]:
                pesco[o["escolhida"]] += 1
    print(f"  {'passiva':<26}{'oferecida':<12}{'escolhida':<12}{'captura'}")
    for p, n in pofer.most_common():
        print(f"  {p:<26}{n:<12}{pesco[p]:<12}{pct(pesco[p], n)}")

    sub("EQUIPAMENTO: ocupacao do slot na build final")
    print(f"  {'slot':<12}{'preenchido':<28}{'pecas distintas':<18}{'mais frequente'}")
    slots = [s for s in (runs[0]["build"]["equipamento"] if runs else {})]
    for slot in slots:
        pecas = [r["build"]["equipamento"][slot] for r in runs]
        cheio = [p for p in pecas if p]
        nomes = Counter(p["nome"] for p in cheio)
        top = nomes.most_common(1)
        print(
            f"  {slot:<12}{pct(len(cheio), len(pecas)):<28}{len(nomes):<18}"
            + (f"{top[0][0]} ({top[0][1]})" if top else "-")
        )

    sub("EQUIPAMENTO: as 25 pecas mais equipadas (qualquer slot)")
    todas = Counter()
    rar = Counter()
    for r in runs:
        for p in r["build"]["equipamento"].values():
            if p:
                todas[p["nome"]] += 1
                rar[p["raridade"]] += 1
    for nome, n in todas.most_common(25):
        print(f"  {nome:<34}{n:>6}  {100 * n / len(runs):5.1f}% das runs")
    print("  raridades equipadas: " + "  ".join(f"{k}={v}" for k, v in rar.most_common()))

    sub("upgrades: +N, gemas, encantos (build final)")
    for rot, key in (
        ("+N somado", "mais_n_total"),
        ("gemas cravadas", "gemas_cravadas"),
        ("encantos", "encantos_totais"),
        ("sockets", "sockets_totais"),
        ("pecas equipadas", "pecas_equipadas"),
    ):
        linha_perc(rot, [r["build"][key] for r in runs], "{:6.1f}")
    for rot, key in (
        ("+N somado", "mais_n_total"),
        ("gemas cravadas", "gemas_cravadas"),
        ("encantos", "encantos_totais"),
    ):
        zero = sum(1 for r in runs if r["build"][key] == 0)
        print(f"  runs com {rot} == 0: {pct(zero, len(runs))}")
    sub("sobreviventes (nao morreram): upgrades")
    vivos = [r for r in runs if r["desfecho"] != "MORREU"]
    for rot, key in (
        ("+N somado", "mais_n_total"),
        ("gemas cravadas", "gemas_cravadas"),
        ("encantos", "encantos_totais"),
        ("pecas equipadas", "pecas_equipadas"),
    ):
        linha_perc(f"vivos: {rot}", [r["build"][key] for r in vivos], "{:6.1f}")

    # ------------------------------------------------------------------ 7
    titulo("7. WARRIOR x MAGE x ROGUE")
    campos = [
        ("andar final", lambda r: r["andar_final"]),
        ("nivel final", lambda r: r["build"]["nivel"]),
        ("combates", lambda r: r["combates"]),
        ("fugas na ficha", lambda r: r["fugas_na_ficha"]),
        ("hp max", lambda r: r["build"]["hp_max"]),
        ("mp max", lambda r: r["build"]["mp_max"]),
        ("dano medio", lambda r: r["build"]["dano_medio"]),
        ("ouro final", lambda r: r["build"]["ouro"]),
        ("pocoes bebidas", lambda r: r["pocoes_bebidas"]),
        ("passivas", lambda r: len(r["build"]["passivas"])),
        ("skills no deck", lambda r: len(r["build"]["skills"])),
        ("pecas equipadas", lambda r: r["build"]["pecas_equipadas"]),
        ("dano dado", lambda r: r["dano_dado_total"]),
        ("dano recebido", lambda r: r["dano_recebido_total"]),
        ("dano recebido frac", lambda r: r["dano_recebido_frac"]),
        ("egide absorvida", lambda r: r["egide_absorvida"]),
        ("mp gasto", lambda r: r["mp_gasto"]),
    ]
    print(f"  {'metrica (MEDIANA)':<24}" + "".join(f"{c:<14}" for c in CLASSES))
    for rot, f in campos:
        vals = [perc([f(r) for r in por_classe[c]], 0.5) for c in CLASSES]
        print(f"  {rot:<24}" + "".join(f"{(v if v is not None else 0):<14.1f}" for v in vals))
    print()
    print(f"  {'metrica (MEDIA)':<24}" + "".join(f"{c:<14}" for c in CLASSES))
    for rot, f in campos:
        vals = [sum(f(r) for r in por_classe[c]) / max(1, len(por_classe[c])) for c in CLASSES]
        print(f"  {rot:<24}" + "".join(f"{v:<14.1f}" for v in vals))

    sub("verbos de combate por classe (fracao dos turnos)")
    for c in CLASSES:
        ac = Counter()
        for r in por_classe[c]:
            ac.update(r["acoes_de_combate"])
        t = sum(ac.values()) or 1
        print(f"  {c:<9}" + "  ".join(f"{k}={100 * v / t:.1f}%" for k, v in ac.most_common()))

    sub("skills mais usadas por classe")
    for c in CLASSES:
        u = Counter()
        for r in por_classe[c]:
            u.update(r["skill_usos"])
        t = sum(u.values()) or 1
        print(f"  {c}:")
        for s, n in u.most_common(8):
            print(f"    {s:<26}{n:>8}  {100 * n / t:5.1f}%")

    sub("passivas mais frequentes na build final por classe")
    for c in CLASSES:
        p = Counter()
        for r in por_classe[c]:
            p.update(r["build"]["passivas"])
        print(f"  {c}:")
        for s, n in p.most_common(8):
            print(f"    {s:<26}{n:>8}  {100 * n / len(por_classe[c]):5.1f}% das runs")

    sub("causa da morte: monstro e gap de nivel")
    for c in CLASSES:
        fat = [r["fatal"] for r in por_classe[c] if r["fatal"]]
        gaps = Counter(f["gap"] for f in fat)
        mons = Counter(f["monstro"].rsplit(" Nv.", 1)[0] for f in fat)
        print(
            f"  {c} (n={len(fat)})  gap: "
            + " ".join(f"{g:+d}={n}" for g, n in sorted(gaps.items()))
        )
        print("    top monstros: " + ", ".join(f"{m} ({n})" for m, n in mons.most_common(6)))
        print(
            f"    hp_frac ao aceitar a luta fatal: "
            f"mediana {perc([f['hp_frac'] for f in fat], 0.5) or 0:.2f}"
            f"  p10 {perc([f['hp_frac'] for f in fat], 0.10) or 0:.2f}"
        )

    # ------------------------------------------------------------------ 8
    titulo("8. OUTLIERS E BUILDS INTERESSANTES")
    sub("as 12 runs de maior poder medido")
    com_poder = sorted(
        (r for r in runs if r["poder_relativo_ultimo"]), key=lambda r: -r["poder_relativo_ultimo"]
    )
    for r in com_poder[:12]:
        b = r["build"]
        print(
            f"  {r['classe']:<8} seed {r['seed']}  andar {r['andar_final']:>2} nv {b['nivel']:>2}  "
            f"poder {r['poder_relativo_ultimo']:.3f} "
            f"(abs {r['poder_absoluto_ultimo']:.1f})  {r['desfecho']}"
        )
        print(
            f"    {b['pecas_equipadas']} pecas, +{b['mais_n_total']}, {b['gemas_cravadas']} gemas, "
            f"{b['encantos_totais']} encantos | {len(b['passivas'])} passivas | ouro {b['ouro']}"
        )
        print(f"    deck: {', '.join(b['skills'])}")
    sub("as 8 runs mais profundas")
    for r in sorted(runs, key=lambda r: (-r["andar_final"], -r["build"]["nivel"]))[:8]:
        b = r["build"]
        print(
            f"  {r['classe']:<8} seed {r['seed']}  andar {r['andar_final']:>2} "
            f"nv {b['nivel']:>2} {r['desfecho']:<9}"
            f" hp {b['hp_max']} dano {b['dano_medio']:.0f} ouro {b['ouro']}  "
            f"deck: {', '.join(b['skills'])}"
        )
    sub("extremos de economia e nivel")
    for rot, key, f in (
        ("mais ouro", "ouro", lambda r: r["build"]["ouro"]),
        ("maior nivel", "nivel", lambda r: r["build"]["nivel"]),
        ("mais combates", "combates", lambda r: r["combates"]),
        ("mais +N", "mais_n", lambda r: r["build"]["mais_n_total"]),
        ("mais gemas", "gemas", lambda r: r["build"]["gemas_cravadas"]),
    ):
        top = sorted(runs, key=lambda r: -f(r))[:3]
        print(
            f"  {rot:<14}"
            + "   ".join(
                f"{r['classe']}/{r['seed']} = {f(r)} (andar {r['andar_final']})" for r in top
            )
        )

    # ------------------------------------------------------------------ 9
    titulo("9. SINAIS DE CONTEUDO DOMINANTE OU MORTO")
    sub("skills: captura >=80% (dominante) ou <=5% com n>=30 (morta)")
    for s, n in ofer.most_common():
        if n < 30:
            continue
        p, lo, hi = wilson(esco[s], n)
        if hi <= 0.05:
            print(f"  MORTA       {s:<26}{pct(esco[s], n)}")
    for s, n in ofer.most_common():
        if n < 30:
            continue
        p, lo, hi = wilson(esco[s], n)
        if lo >= 0.80:
            print(f"  DOMINANTE   {s:<26}{pct(esco[s], n)}")
    sub("passivas: captura >=80% (dominante) ou <=5% com n>=30 (morta)")
    for p_, n in pofer.most_common():
        if n < 30:
            continue
        p, lo, hi = wilson(pesco[p_], n)
        if hi <= 0.05:
            print(f"  MORTA       {p_:<26}{pct(pesco[p_], n)}")
    for p_, n in pofer.most_common():
        if n < 30:
            continue
        p, lo, hi = wilson(pesco[p_], n)
        if lo >= 0.80:
            print(f"  DOMINANTE   {p_:<26}{pct(pesco[p_], n)}")
    sub("servicos e eventos: quantas runs USARAM")
    serv = Counter()
    for r in runs:
        for k in r["servicos"]:
            serv[k] += 1
    for k, n in serv.most_common():
        print(f"  {k:<24}{pct(n, len(runs))}")
    sub("consumiveis: pocoes bebidas e estoque final")
    zero = sum(1 for r in runs if r["pocoes_bebidas"] == 0)
    print(f"  runs que NAO beberam nenhuma pocao: {pct(zero, len(runs))}")
    linha_perc("pocoes bebidas", [r["pocoes_bebidas"] for r in runs], "{:6.1f}")
    est = Counter()
    for r in runs:
        for k, v in r["build"]["pocoes"].items():
            est[k] += v
    print(
        "  estoque final somado: "
        + ("  ".join(f"{k}={v}" for k, v in est.most_common(8)) or "vazio")
    )
    outros = Counter()
    for r in runs:
        for k, v in r["build"]["outros_consumiveis"].items():
            outros[k] += v
    print(
        "  outros consumiveis: "
        + ("  ".join(f"{k}={v}" for k, v in outros.most_common(8)) or "vazio")
    )
    sub("dot sofrido e egide")
    dots = Counter()
    for r in runs:
        for k, v in r["dot_sofrido"].items():
            dots[k] += v
    print(
        "  dano total por DoT: "
        + ("  ".join(f"{k}={v}" for k, v in dots.most_common()) or "nenhum")
    )
    com_egide = sum(1 for r in runs if r["egide_absorvida"] > 0)
    print(f"  runs com Egide absorvendo algo: {pct(com_egide, len(runs))}")
    sub("chaves de extracao")
    linha_perc("chaves na build final", [r["build"]["chaves"] for r in runs], "{:6.2f}")
    com_chave = sum(1 for r in runs if r["build"]["chaves"] > 0)
    print(f"  runs terminando com chave no bolso: {pct(com_chave, len(runs))}")
    com_oport = sum(1 for r in runs if r["oportunidades"] > 0)
    print(f"  runs que TIVERAM alguma oportunidade de extrair: {pct(com_oport, len(runs))}")


if __name__ == "__main__":
    main()
