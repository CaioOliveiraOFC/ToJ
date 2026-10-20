"""Baseline de progressão real (Run/Progression Balance): o agregador.

Lê `baseline.jsonl` (o deste diretório, ou o caminho passado), confere a
integridade da amostra e imprime as métricas consolidadas do README.

    python baselines/progression/fb321d4e/agrega.py [baseline.jsonl]

Convenções, fixas para o resultado ser reproduzível:

- percentil por interpolação linear (tipo 7, o padrão do numpy);
- IC95 da média por bootstrap: 4.000 reamostras, `random.Random(7)`;
- efeito do starter por Kruskal-Wallis com permutação: 5.000 permutações,
  `random.Random(11)`, unidade = seed (o starter é sorteado por seed e é o mesmo
  nas três classes);
- "chegou ao andar N" = a run entrou no andar N (`andar >= N`);
- "nível ao entrar no andar N" = `nivel_por_andar[N - 1]`.

A ordem das linhas do arquivo é irrelevante: as runs são ordenadas por classe e
seed antes de qualquer conta.

Só biblioteca padrão.
"""

from __future__ import annotations

import json
import math
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

CLASSES = ("warrior", "mage", "rogue")
SEEDS = range(1, 101)
ARQUIVO = Path(__file__).with_name("baseline.jsonl")


# -- leitura e integridade ---------------------------------------------------


def carregar(caminho: Path) -> list[dict]:
    runs = [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines()]
    return sorted(runs, key=lambda r: (CLASSES.index(r["classe"]), r["seed"]))


def validar(runs: list[dict]) -> None:
    """Recusa amostra incompleta em vez de agregar o que sobrou."""
    problemas = []
    chaves = Counter((r["classe"], r["seed"]) for r in runs)
    esperado = {(c, s) for c in CLASSES for s in SEEDS}
    if len(runs) != len(esperado):
        problemas.append(f"{len(runs)} registros, esperado {len(esperado)}")
    if duplicadas := sorted(k for k, n in chaves.items() if n > 1):
        problemas.append(f"duplicadas: {duplicadas}")
    if faltando := sorted(esperado - set(chaves)):
        problemas.append(f"faltando: {faltando}")
    if sobrando := sorted(set(chaves) - esperado):
        problemas.append(f"fora do protocolo: {sobrando}")
    if no_teto := [(r["classe"], r["seed"]) for r in runs if r["desfecho"] == "teto"]:
        problemas.append(f"runs que bateram no teto: {no_teto}")
    prefixo = {"morreu": "MORREU", "extraiu": "EXTRAIU", "teto": "CHEGOU"}
    if incoerentes := [
        (r["classe"], r["seed"]) for r in runs if not r["fim"].startswith(prefixo[r["desfecho"]])
    ]:
        problemas.append(f"desfecho incoerente com o fim: {incoerentes}")
    if sem_um_starter := [
        (r["classe"], r["seed"])
        for r in runs
        if len(r["starter"]) != 1 or r["starter"][0]["origin"] != "starter"
    ]:
        problemas.append(f"sem exatamente um starter: {sem_um_starter}")
    por_seed = defaultdict(set)
    for r in runs:
        por_seed[r["seed"]].add(r["starter"][0]["id"] if r["starter"] else None)
    if starter_variando := sorted(s for s, ids in por_seed.items() if len(ids) != 1):
        problemas.append(f"seed com starter diferente entre classes: {starter_variando}")
    if problemas:
        raise SystemExit("amostra inválida:\n  " + "\n  ".join(problemas))


# -- estatística --------------------------------------------------------------


def pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def ic95_media(xs: list[float], n: int = 4000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    medias = sorted(st.mean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return medias[int(0.025 * n)], medias[int(0.975 * n)]


def p_sinal(a_vence: int, b_vence: int) -> float:
    """Teste do sinal bilateral, exato; empates descartados."""
    n, k = a_vence + b_vence, min(a_vence, b_vence)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def _postos(valores: list[float]) -> list[float]:
    ordem = sorted(range(len(valores)), key=lambda i: valores[i])
    postos = [0.0] * len(valores)
    i = 0
    while i < len(valores):
        j = i
        while j + 1 < len(valores) and valores[ordem[j + 1]] == valores[ordem[i]]:
            j += 1
        for k in range(i, j + 1):
            postos[ordem[k]] = (i + j) / 2 + 1
        i = j + 1
    return postos


def _h(valores: list[float], grupos: list[str]) -> float:
    postos, n = _postos(valores), len(valores)
    por_grupo = defaultdict(list)
    for posto, grupo in zip(postos, grupos):
        por_grupo[grupo].append(posto)
    soma = sum(len(v) * st.mean(v) ** 2 for v in por_grupo.values())
    return 12 / (n * (n + 1)) * soma - 3 * (n + 1)


def kruskal_permutacao(
    valores: list[float], grupos: list[str], n: int = 5000, seed: int = 11
) -> tuple[float, float]:
    h0 = _h(valores, grupos)
    rng, embaralhados, extremos = random.Random(seed), list(grupos), 0
    for _ in range(n):
        rng.shuffle(embaralhados)
        extremos += _h(valores, embaralhados) >= h0 - 1e-12
    return h0, (extremos + 1) / (n + 1)


# -- formatação ---------------------------------------------------------------


def br(x: float, casas: int = 1) -> str:
    """Número no formato do README: vírgula decimal, inteiro sem casas."""
    if float(x).is_integer() and casas <= 1:
        return str(int(x))
    return f"{x:.{casas}f}".replace(".", ",")


def _morreu_ate(rs: list[dict], andar: int) -> int:
    return sum(1 for r in rs if r["desfecho"] == "morreu" and r["andar"] <= andar)


def _nivel_ao_entrar(r: dict, andar: int) -> int | None:
    return r["nivel_por_andar"][andar - 1] if len(r["nivel_por_andar"]) >= andar else None


# -- relatório ----------------------------------------------------------------


def tabela_consolidada(por_classe: dict[str, list[dict]]) -> None:
    linhas: list[tuple[str, list[str]]] = []

    def linha(rotulo, f):
        linhas.append((rotulo, [f(por_classe[c]) for c in CLASSES]))

    def andares(rs):
        return [r["andar"] for r in rs]

    def niveis(rs):
        return [r["nivel"] for r in rs]

    def desfechos(rs):
        d = Counter(r["desfecho"] for r in rs)
        return f"{d['morreu']} / {d['extraiu']}"

    def media_ic(rs):
        lo, hi = (f"{x:.1f}".replace(".", ",") for x in ic95_media(andares(rs)))
        return f"{br(st.mean(andares(rs)), 2)} [{lo}–{hi}]"

    linha("Mortes / extrações", desfechos)
    linha("Andar médio [IC95]", media_ic)
    linha("Mediana", lambda rs: br(pct(andares(rs), 0.5)))
    linha("P25", lambda rs: br(pct(andares(rs), 0.25)))
    linha("P75", lambda rs: br(pct(andares(rs), 0.75)))
    linha("P90", lambda rs: br(pct(andares(rs), 0.9)))
    linha("Máximo", lambda rs: br(max(andares(rs))))
    linha("Nível final médio", lambda rs: f"{st.mean(niveis(rs)):.1f}".replace(".", ","))
    linha("Nível final mediano", lambda rs: br(pct(niveis(rs), 0.5)))
    linha("Nível final P90", lambda rs: br(pct(niveis(rs), 0.9)))
    linha("Nível final máximo", lambda rs: br(max(niveis(rs))))
    linha("Morte no andar 1", lambda rs: str(_morreu_ate(rs, 1)))
    linha("Morte até andar 3", lambda rs: str(_morreu_ate(rs, 3)))
    linha("Morte até andar 5", lambda rs: str(_morreu_ate(rs, 5)))
    linha("Chegou ao andar 10", lambda rs: str(sum(a >= 10 for a in andares(rs))))
    linha("Chegou ao andar 20", lambda rs: str(sum(a >= 20 for a in andares(rs))))

    print("| Métrica | Warrior | Mage | Rogue |")
    print("|---|---:|---:|---:|")
    for rotulo, valores in linhas:
        print(f"| {rotulo} | " + " | ".join(valores) + " |")

    print("\nExtrações:")
    for c in CLASSES:
        ex = [r for r in por_classe[c] if r["desfecho"] == "extraiu"]
        a, n = [r["andar"] for r in ex], [r["nivel"] for r in ex]
        print(f"- {c.capitalize()}: andares {min(a)}–{max(a)}, níveis {min(n)}–{max(n)}")


def early_game(runs: list[dict]) -> None:
    total = len(runs)
    mortes = [r for r in runs if r["desfecho"] == "morreu"]
    a1, a5 = _morreu_ate(runs, 1), _morreu_ate(runs, 5)
    print(f"morte no andar 1: {a1}/{total} ({a1 / total:.1%})")
    print(f"morte até o andar 5: {a5}/{total} ({a5 / total:.1%})")
    baixo = sum(1 for r in mortes if r["fatal"]["hp_frac"] < 0.55)
    print(
        f"mortes que entraram no combate fatal abaixo de 55% de HP: {baixo}/{len(mortes)} "
        f"({baixo / len(mortes):.0%}); mediana do HP de entrada "
        f"{st.median(r['fatal']['hp_frac'] for r in mortes):.2f}"
    )
    primeira = [
        (r["classe"], r["seed"], r["fatal"]["monstro"])
        for r in mortes
        if r["andar"] == 1 and r["combates"] == 1 and r["fatal"]["hp_frac"] >= 0.999
    ]
    print(f"morte na PRIMEIRA luta do andar 1, com HP cheio: {len(primeira)} {primeira}")


def mergulho(por_classe: dict[str, list[dict]]) -> None:
    print("Quem chegou ao andar 10, pelo nível ao entrar nele:")
    total_mergulho = total_extraiu = 0
    for c in CLASSES:
        chegou = [r for r in por_classe[c] if _nivel_ao_entrar(r, 10) is not None]
        baixo = [r for r in chegou if _nivel_ao_entrar(r, 10) <= 5]
        alto = [r for r in chegou if _nivel_ao_entrar(r, 10) >= 8]
        ex_baixo = sum(r["desfecho"] == "extraiu" for r in baixo)
        ex_alto = sum(r["desfecho"] == "extraiu" for r in alto)
        total_mergulho += len(baixo)
        total_extraiu += ex_baixo
        print(
            f"  {c:8s} chegou {len(chegou):2d} | nível <= 5: {len(baixo):2d} "
            f"(extraíram {ex_baixo}, andar da morte {min(r['andar'] for r in baixo)}–"
            f"{max(r['andar'] for r in baixo)}) | nível >= 8: {ex_alto}/{len(alto)} extraem"
        )
    print(f"  mergulho (nível <= 5 no andar 10): {total_mergulho} runs, {total_extraiu} extraíram")


def pareado(por_classe: dict[str, list[dict]]) -> None:
    print("Mesma seed (mesmo starter), andar final:")
    andar = {c: {r["seed"]: r["andar"] for r in por_classe[c]} for c in CLASSES}
    for a, b in (("warrior", "mage"), ("warrior", "rogue"), ("mage", "rogue")):
        va = sum(andar[a][s] > andar[b][s] for s in SEEDS)
        vb = sum(andar[a][s] < andar[b][s] for s in SEEDS)
        print(
            f"  {a} vs {b}: {a} mais fundo {va}, empate {len(SEEDS) - va - vb}, "
            f"{b} mais fundo {vb}; teste do sinal p = {p_sinal(va, vb):.4f}"
        )


def starter(runs: list[dict]) -> None:
    por = {(r["classe"], r["seed"]): r for r in runs}
    seeds = list(SEEDS)
    categoria = {s: por[("warrior", s)]["starter"][0]["categoria"] for s in seeds}
    item = {s: por[("warrior", s)]["starter"][0]["id"] for s in seeds}
    andar_medio = [st.mean(por[(c, s)]["andar"] for c in CLASSES) for s in seeds]
    mortes_cedo = [
        sum(por[(c, s)]["desfecho"] == "morreu" and por[(c, s)]["andar"] <= 3 for c in CLASSES)
        for s in seeds
    ]
    print("Kruskal-Wallis por permutação (unidade = seed, n = 100):")
    for rotulo, valores, grupos in (
        ("categoria × andar médio", andar_medio, [categoria[s] for s in seeds]),
        ("categoria × morte até andar 3", mortes_cedo, [categoria[s] for s in seeds]),
        ("item × andar médio", andar_medio, [item[s] for s in seeds]),
    ):
        h, p = kruskal_permutacao(valores, grupos)
        print(f"  {rotulo}: H = {h:.2f}, p = {p:.3f}")

    geral = st.mean(r["andar"] for r in runs)
    print(f"\nPor categoria (as 3 classes juntas; média geral {geral:.2f}):")
    grupos = defaultdict(list)
    for r in runs:
        grupos[r["starter"][0]["categoria"]].append(r)
    for cat, rs in sorted(grupos.items(), key=lambda kv: -st.mean(r["andar"] for r in kv[1])):
        a = [r["andar"] for r in rs]
        lo, hi = ic95_media(a)
        cedo = _morreu_ate(rs, 3) / len(rs)
        print(
            f"  {cat:10s} seeds {len(rs) // 3:2d}  média {st.mean(a):5.2f} "
            f"[{lo:.2f}–{hi:.2f}]  mediana {pct(a, 0.5):4.1f}  morte <=3 {cedo:.0%}"
        )
    print("\nPor item (amostras pequenas: inconclusivo por construção):")
    por_item = defaultdict(list)
    for r in runs:
        por_item[(r["starter"][0]["categoria"], r["starter"][0]["id"])].append(r["andar"])
    for (cat, iid), a in sorted(por_item.items(), key=lambda kv: -st.mean(kv[1])):
        print(f"  {cat:9s} {iid:18s} seeds {len(a) // 3:2d}  média {st.mean(a):5.2f}")


def pocoes(por_classe: dict[str, list[dict]]) -> None:
    sem = {c: sum(r["pocoes"] == 0 for r in por_classe[c]) for c in CLASSES}
    total = sum(len(rs) for rs in por_classe.values())
    print(
        "runs sem nenhuma poção bebida: "
        + ", ".join(f"{c} {n}" for c, n in sem.items())
        + f"; total {sum(sem.values())}/{total} ({sum(sem.values()) / total:.0%})"
    )


def histograma(por_classe: dict[str, list[dict]]) -> None:
    faixas = ((1, "1"), (3, "2-3"), (5, "4-5"), (9, "6-9"), (14, "10-14"), (19, "15-19"),
              (29, "20-29"), (10**9, "30+"))  # fmt: skip

    def faixa(a):
        return next(rot for lim, rot in faixas if a <= lim)

    print("Andar final por faixa:")
    for c in CLASSES:
        h = Counter(faixa(r["andar"]) for r in por_classe[c])
        print(f"  {c:8s} " + "  ".join(f"{rot}:{h[rot]}" for _, rot in faixas))


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else ARQUIVO
    runs = carregar(caminho)
    validar(runs)
    por_classe = {c: [r for r in runs if r["classe"] == c] for c in CLASSES}
    print(f"{caminho}: {len(runs)} runs íntegras, 100 por classe, seeds 1–100\n")
    for titulo, secao in (
        ("RESULTADO CONSOLIDADO", lambda: tabela_consolidada(por_classe)),
        ("EARLY GAME", lambda: early_game(runs)),
        ("ESPIRAL DE MERGULHO", lambda: mergulho(por_classe)),
        ("CLASSES PAREADAS POR SEED", lambda: pareado(por_classe)),
        ("STARTER KIT", lambda: starter(runs)),
        ("POÇÕES", lambda: pocoes(por_classe)),
        ("DISTRIBUIÇÃO", lambda: histograma(por_classe)),
    ):
        print(f"== {titulo} ==")
        secao()
        print()


if __name__ == "__main__":
    main()
