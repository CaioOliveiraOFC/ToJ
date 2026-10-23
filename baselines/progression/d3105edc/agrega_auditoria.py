"""Auditoria do primeiro nível — o agregador: "antes" (4d0a9a0a) contra "depois".

    python baselines/progression/<dir>/agrega_auditoria.py [antes.jsonl depois.jsonl]

Percentil por interpolação linear (tipo 7). "Chegou ao andar N" = entrou no
andar N. "Nível ao entrar no andar N" = `nivel_por_andar[N - 1]`. As runs são
ordenadas por classe e seed antes de qualquer conta. Só biblioteca padrão.
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import Counter
from pathlib import Path

CLASSES = ("warrior", "mage", "rogue")
SEEDS = range(1, 101)
AQUI = Path(__file__).parent
# As seis runs que morriam na primeira luta do andar 1 com HP cheio (0ab837b9).
PRIMEIRA_LUTA = (
    ("mage", 16), ("mage", 62), ("mage", 93), ("rogue", 4), ("rogue", 16), ("rogue", 98),
)  # fmt: skip
CASOS = (("warrior", 24), ("mage", 59), ("warrior", 2))


def carregar(caminho: Path) -> list[dict]:
    runs = [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines()]
    chaves = Counter((r["classe"], r["seed"]) for r in runs)
    esperado = {(c, s) for c in CLASSES for s in SEEDS}
    if set(chaves) != esperado or any(n > 1 for n in chaves.values()):
        raise SystemExit(f"{caminho}: amostra incompleta ou duplicada")
    for r in runs:
        coerente = r["fim"].startswith({"morreu": "MORREU", "extraiu": "EXTRAIU"}[r["desfecho"]])
        starter = sum(1 for s in r["starter"] if s["origin"] == "starter") == 1
        if not (coerente and starter and r["andar"] < r["teto"]):
            raise SystemExit(f"{caminho}: registro incoerente em {r['classe']} seed {r['seed']}")
    return sorted(runs, key=lambda r: (CLASSES.index(r["classe"]), r["seed"]))


def pct(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def _f(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",") if not float(x).is_integer() else str(int(x))


def _atrasos(r: dict) -> list[int]:
    """Andar menos nível, ao entrar em cada andar."""
    return [andar - nivel for andar, nivel in enumerate(r["nivel_por_andar"], start=1)]


def _recuperou(r: dict, k: int = 3) -> bool | None:
    """Ficou `k` ou mais níveis atrás e depois voltou a no máximo 1. None: nunca caiu."""
    lag = _atrasos(r)
    i = next((j for j, x in enumerate(lag) if x >= k), None)
    if i is None:
        return None
    return any(x <= 1 for x in lag[i + 1 :])


def _pocoes_obtidas(r: dict) -> int:
    return r["pocoes_compradas"] + r.get("pocoes_do_loot", 0) + r.get("pocoes_da_fonte", 0)


def _mergulhou(r: dict) -> bool:
    return len(r["nivel_por_andar"]) >= 10 and r["nivel_por_andar"][9] <= 5


def _fatal_sublevel_abaixo_da_aposta(r: dict) -> bool:
    return r["desfecho"] == "morreu" and r["fatal"]["hp_frac"] < 0.35 and r["nivel"] < r["andar"]


def _primeira_fatal(r: dict) -> bool:
    return (
        r["desfecho"] == "morreu"
        and r["andar"] == 1
        and r["combates"] == 1
        and r["fatal"]["hp_frac"] >= 0.999
    )


def metricas(rs: list[dict]) -> dict[str, str]:
    n = len(rs)
    andar = [r["andar"] for r in rs]
    nivel = [r["nivel"] for r in rs]
    mortes = [r for r in rs if r["desfecho"] == "morreu"]
    extr = [r for r in rs if r["desfecho"] == "extraiu"]
    hp_fatal = [r["fatal"]["hp_frac"] for r in mortes if r.get("fatal")]
    lojas = sum(r["lojas"] for r in rs)
    inuteis = sum(r["lojas_inuteis"] for r in rs)
    mergulho = [r for r in rs if _mergulhou(r)]
    streak = [r["max_streak_nao_pagas"] for r in rs]
    itens = sum(r["acoes"].get("item", 0) for r in rs)
    com_pocao = [r for r in mortes if r["pocoes_na_mochila_ao_fim"] > 0]
    return {
        "mortes / extrações": f"{len(mortes)} / {len(extr)}",
        "andar médio": _f(st.mean(andar), 2),
        "andar mediana · P25 · P75 · P90 · máx": " · ".join(
            _f(pct(andar, p)) for p in (0.5, 0.25, 0.75, 0.9)
        )
        + f" · {max(andar)}",
        "nível final médio · mediana · P90 · máx": f"{_f(st.mean(nivel))} · "
        + " · ".join(_f(pct(nivel, p)) for p in (0.5, 0.9))
        + f" · {max(nivel)}",
        "morte no andar 1 / até 3 / até 5": " / ".join(
            str(sum(1 for r in mortes if r["andar"] <= k)) for k in (1, 3, 5)
        ),
        "chegou ao 10 / ao 20": f"{sum(a >= 10 for a in andar)} / {sum(a >= 20 for a in andar)}",
        "morte na 1ª luta do andar 1, com HP cheio": str(sum(_primeira_fatal(r) for r in rs)),
        "das mortes, fração até o andar 5": (
            f"{sum(r['andar'] <= 5 for r in mortes) / max(1, len(mortes)):.0%}"
        ),
        "nível 1 ao entrar no andar 2": (
            f"{sum(r['nivel_por_andar'][1] == 1 for r in rs if len(r['nivel_por_andar']) >= 2)}"
            f"/{sum(len(r['nivel_por_andar']) >= 2 for r in rs)}"
        ),
        "HP de entrada no combate fatal (mediana)": _f(st.median(hp_fatal), 2) if hp_fatal else "-",
        "combate fatal por HP de entrada: <35% · 35–55% · >=55%": (
            f"{sum(h < 0.35 for h in hp_fatal)} · "
            f"{sum(0.35 <= h < 0.55 for h in hp_fatal)} · {sum(h >= 0.55 for h in hp_fatal)}"
        ),
        "  dos <35%, sublevel (nível < andar)": str(
            sum(_fatal_sublevel_abaixo_da_aposta(r) for r in rs)
        ),
        "mortes com combate fatal abaixo de 55%": (
            f"{sum(h < 0.55 for h in hp_fatal)}/{len(hp_fatal)} "
            f"({sum(h < 0.55 for h in hp_fatal) / max(1, len(hp_fatal)):.0%})"
        ),
        "poções bebidas no mapa (total · runs sem nenhuma)": (
            f"{sum(r['pocoes'] for r in rs)} · {sum(r['pocoes'] == 0 for r in rs)}/{n}"
        ),
        "itens usados em combate (total)": str(itens),
        "mortes com poção de cura na mochila (poções levadas)": (
            f"{len(com_pocao)} ({sum(r['pocoes_na_mochila_ao_fim'] for r in com_pocao)})"
        ),
        "  dessas, com combate fatal abaixo de 55%": str(
            sum(r["fatal"]["hp_frac"] < 0.55 for r in com_pocao)
        ),
        "extrações com poção de cura na mochila": (
            f"{sum(r['pocoes_na_mochila_ao_fim'] > 0 for r in extr)}/{len(extr)}"
        ),
        "Loja: visitas · que curaram · poções compradas": (
            f"{lojas} · {sum(r['lojas_que_curaram'] for r in rs)} · "
            f"{sum(r['pocoes_compradas'] for r in rs)}"
        ),
        "Loja: visitas sem efeito nenhum": f"{inuteis} ({inuteis / max(1, lojas):.0%})",
        "saídas não pagas por run (média)": _f(st.mean(r["saidas_nao_pagas"] for r in rs), 2),
        "maior streak de não pagas (média · P90 · máx)": (
            f"{_f(st.mean(streak), 2)} · {_f(pct(streak, 0.9))} · {max(streak)}"
        ),
        "chegou ao 10 com nível <= 5 (extraíram)": (
            f"{len(mergulho)} ({sum(r['desfecho'] == 'extraiu' for r in mergulho)})"
        ),
        "combates por run (média)": _f(st.mean(r["combates"] for r in rs), 1),
        "mortes sublevel (nível < andar)": f"{sum(r['nivel'] < r['andar'] for r in mortes)}",
        "atraso ao entrar no andar 5 · 10 · 15 (média)": " · ".join(
            _f(st.mean(_atrasos(r)[k - 1] for r in rs if len(r["nivel_por_andar"]) >= k), 2)
            if any(len(r["nivel_por_andar"]) >= k for r in rs)
            else "-"
            for k in (5, 10, 15)
        ),
        "maior atraso da run (mediana · P90 · máx)": (
            f"{_f(pct([max(_atrasos(r)) for r in rs], 0.5))} · "
            f"{_f(pct([max(_atrasos(r)) for r in rs], 0.9))} · {max(max(_atrasos(r)) for r in rs)}"
        ),
        "caíram 3+ atrás · voltaram a <= 1": (
            f"{sum(_recuperou(r) is not None for r in rs)} · {sum(bool(_recuperou(r)) for r in rs)}"
        ),
        "caíram 2+ atrás · voltaram a <= 1": (
            f"{sum(_recuperou(r, 2) is not None for r in rs)} · "
            f"{sum(bool(_recuperou(r, 2)) for r in rs)}"
        ),
        "Essência efetiva média por andar": (
            _f(st.mean(e for r in rs for e in r["essencia_efetiva"]), 2)
            if all("essencia_efetiva" in r for r in rs)
            else "-"
        ),
        "andares na Essência do piso (0,5)": (
            str(sum(e <= 0.5 for r in rs for e in r["essencia_efetiva"]))
            if all("essencia_efetiva" in r for r in rs)
            else "-"
        ),
        "ouro ganho por run (média · por andar)": (
            f"{_f(st.mean(r['ouro_ganho'] for r in rs), 0)} · "
            f"{_f(sum(r['ouro_ganho'] for r in rs) / sum(r['andar'] for r in rs), 1)}"
        ),
        "poções obtidas: compradas · loot · Fonte": (
            f"{sum(r['pocoes_compradas'] for r in rs)} · "
            f"{sum(r.get('pocoes_do_loot', 0) for r in rs)} · "
            f"{sum(r.get('pocoes_da_fonte', 0) for r in rs)}"
        ),
        "runs sem acesso a cura (nenhuma poção, nenhuma cura paga)": str(
            sum(_pocoes_obtidas(r) == 0 and r["lojas_que_curaram"] == 0 for r in rs)
        ),
        "runs que nunca tiveram poção": str(sum(_pocoes_obtidas(r) == 0 for r in rs)),
    }


def familias(rs: list[dict]) -> Counter:
    return Counter(f for r in rs for f in r["familias_passivas"])


def main() -> None:
    antes_p = Path(sys.argv[1]) if len(sys.argv) > 2 else AQUI / "antes.jsonl"
    depois_p = Path(sys.argv[2]) if len(sys.argv) > 2 else AQUI / "depois.jsonl"
    antes, depois = carregar(antes_p), carregar(depois_p)

    for titulo, filtro in [("TODAS AS CLASSES", None), *[(c.upper(), c) for c in CLASSES]]:
        a = [r for r in antes if filtro is None or r["classe"] == filtro]
        d = [r for r in depois if filtro is None or r["classe"] == filtro]
        ma, md = metricas(a), metricas(d)
        print(f"== {titulo} (n={len(a)}) ==")
        print("| Métrica | antes (4d0a9a0a) | depois |\n|---|---:|---:|")
        for k in ma:
            print(f"| {k} | {ma[k]} | {md[k]} |")
        print()

    print("== NÍVEL AO ENTRAR NO ANDAR (quem entrou: n · P25 · mediana · P75) ==")
    for andar in (2, 3, 4, 5, 6, 8, 10, 15, 20):
        linha = []
        for rs in (antes, depois):
            niveis = [
                r["nivel_por_andar"][andar - 1] for r in rs if len(r["nivel_por_andar"]) >= andar
            ]
            linha.append(
                f"{len(niveis):3d} · {_f(pct(niveis, 0.25))} · {_f(pct(niveis, 0.5))} · "
                f"{_f(pct(niveis, 0.75))}"
                if niveis
                else "  0"
            )
        print(f"  andar {andar:2d}: antes {linha[0]:22s} depois {linha[1]}")
    print()

    print("== EXTRAÇÕES (andares; níveis) ==")
    for nome, rs in (("antes", antes), ("depois", depois)):
        for c in CLASSES:
            ex = [r for r in rs if r["classe"] == c and r["desfecho"] == "extraiu"]
            if ex:
                a = sorted(r["andar"] for r in ex)
                n = sorted(r["nivel"] for r in ex)
                print(
                    f"  {nome:6s} {c:8s} {len(ex):2d}: andares {a[0]}–{a[-1]}, "
                    f"níveis {n[0]}–{n[-1]}"
                )
            else:
                print(f"  {nome:6s} {c:8s}  0")
    print()

    print("== FAMÍLIAS DE PASSIVA ESCOLHIDAS ==")
    fa, fd = familias(antes), familias(depois)
    total_a, total_d = sum(fa.values()), sum(fd.values())
    for fam in sorted(set(fa) | set(fd), key=lambda f: (-fd[f], -fa[f], f)):
        print(f"  {fam:20s} antes {fa[fam]:4d}   depois {fd[fam]:4d}")
    print(f"  total: antes {total_a}, depois {total_d}")
    print()

    ia = {(r["classe"], r["seed"]): r for r in antes}
    idp = {(r["classe"], r["seed"]): r for r in depois}
    if any(ia[k]["starter"] != idp[k]["starter"] for k in ia):
        raise SystemExit("antes e depois não nasceram com o mesmo starter: outro protocolo")

    print("== SEED A SEED (mesma classe, mesma seed, mesmo starter) ==")
    ea = {k for k, r in ia.items() if r["desfecho"] == "extraiu"}
    ed = {k for k, r in idp.items() if r["desfecho"] == "extraiu"}
    print(f"  extrações: mantidas {len(ea & ed)}, perdidas {len(ea - ed)}, novas {len(ed - ea)}")
    da, dd = ({k for k, r in x.items() if _mergulhou(r)} for x in (ia, idp))
    print(
        f"  mergulhos (andar 10 com nível <= 5): mantidos {len(da & dd)}, "
        f"saíram {len(da - dd)}, novos {len(dd - da)}"
    )
    baixo = [k for k, r in idp.items() if _fatal_sublevel_abaixo_da_aposta(r)]
    if baixo:
        rasos = sum(idp[k]["andar"] < ia[k]["andar"] for k in baixo)
        fundos = sum(idp[k]["andar"] > ia[k]["andar"] for k in baixo)
        print(
            f"  mortes de depois com combate fatal < 35% e sublevel: {len(baixo)}; no antes "
            f"{Counter(ia[k]['desfecho'] for k in baixo).most_common()}; andar médio "
            f"{_f(st.mean(ia[k]['andar'] for k in baixo), 2)} -> "
            f"{_f(st.mean(idp[k]['andar'] for k in baixo), 2)} "
            f"(mais raso {rasos}, igual {len(baixo) - rasos - fundos}, mais fundo {fundos})"
        )
    print()

    print("== AS SEIS RUNS DA PRIMEIRA LUTA (fixtures do KI-002) ==")
    for chave in PRIMEIRA_LUTA:
        a, d = ia[chave], idp[chave]
        print(
            f"  {chave[0]} seed {chave[1]}: antes {a['fim']} | depois {d['fim']} "
            f"(1ª luta fatal: {_primeira_fatal(d)})"
        )
    print()

    print("== CASOS HISTÓRICOS (traces de regressão, não critério) ==")
    for chave in CASOS:
        a, d = ia[chave], idp[chave]
        print(
            f"  {chave[0]} seed {chave[1]}: antes {a['fim']} (Nv{a['nivel']}, "
            f"{a['saidas_nao_pagas']} não pagas) | depois {d['fim']} (Nv{d['nivel']}, "
            f"{d['saidas_nao_pagas']} não pagas, lojas {d['lojas']}/{d['lojas_inuteis']} inúteis)"
        )


if __name__ == "__main__":
    main()
