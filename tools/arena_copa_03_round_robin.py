"""Copa Arena 03: todos contra todos, para separar potência bruta de sinergia.

Uso:
    python tools/arena_copa_03_round_robin.py [--seeds 40] [--trabalhadores 4]

Os 64 gladiadores da Copa 03 (os snapshots publicados, reconstruídos pelo
caminho da Arena) se enfrentam em todos os 2016 pares, cada par `--seeds` vezes,
metade com os lados trocados. Mesma `PoliticaCopa`, mesmo motor e mesmo limite
técnico da Copa; duelos sem auditoria, como o `disputar` puro da Copa. A seed de
cada duelo é `sha256("20261025:rr:{id_a}:{id_b}:{r}")`, e o resultado não
depende de quantos processos rodaram.

A Copa MD1 é uma amostra de 63 duelos; aqui cada gladiador joga 63 adversários
× seeds. Disso saem:

- a taxa de vitória e a força Bradley-Terry de cada um (o ranking robusto);
- quanto o OP explica dessa força, e o RESÍDUO: o que a build rende acima ou
  abaixo do que o OP dela prevê. É a parte que o OP, medido contra um boneco
  fixo, não vê — a candidata a "sinergia";
- o que, na build, acompanha esse resíduo (atributos, famílias de passiva,
  tipos de carta, canais);
- confrontos: quantos são decididos pela build, quantos são moeda, e quantos
  ciclos pedra-papel-tesoura existem.

Nada aqui muda a Copa oficial, os snapshots ou o motor. Correlação não é causa:
perfil, política, RNG da jornada e build vêm juntos em cada gladiador.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import statistics
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.gladiator import prepare_gladiator  # noqa: E402
from src.content.skills_loader import get_skill_by_id  # noqa: E402
from tools.arena_auditoria import disputar  # noqa: E402
from tools.arena_copa_03 import (  # noqa: E402
    PERFIL_PT,
    disputar_copa,
    formar_participantes,
    ler_gladiadores,
    todas,
)
from tools.arena_copa_03_geracao import PASTA, PERFIS, POLITICAS, SEMENTE_PRINCIPAL  # noqa: E402
from tools.arena_copa_teste import LIMITE_TECNICO, PoliticaCopa  # noqa: E402

SEEDS = 40
ARQUIVO_JSON = "round_robin.json"
ARQUIVO_MD = "round_robin.md"
# Um confronto "decidido pela build": um lado vence pelo menos esta fração.
DECISIVO = 0.8
# Um elo de ciclo pedra-papel-tesoura: vitória em pelo menos esta fração.
ELO_DE_CICLO = 0.6


def semente(a: str, b: str, r: int) -> int:
    digest = hashlib.sha256(f"{SEMENTE_PRINCIPAL}:rr:{a}:{b}:{r}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def confronto(a, b, seeds: int) -> dict:
    """`a` contra `b`, `seeds` vezes; nas repetições ímpares `b` é o p1."""
    vitorias_a = vitorias_b = inconclusivos = rodadas = 0
    for r in range(seeds):
        p1, p2 = (a, b) if r % 2 == 0 else (b, a)
        duelo = disputar(
            prepare_gladiator(p1.heroi),
            prepare_gladiator(p2.heroi),
            semente(a.id, b.id, r),
            PoliticaCopa,
            auditar=False,
            limite=LIMITE_TECNICO,
        )
        rodadas += len(duelo.duelo.history)
        if duelo.inconclusivo:
            inconclusivos += 1
            continue
        vencedor = p1 if duelo.duelo.result.winner == "p1" else p2
        if vencedor is a:
            vitorias_a += 1
        else:
            vitorias_b += 1
    return {"a": vitorias_a, "b": vitorias_b, "inconclusivos": inconclusivos, "rodadas": rodadas}


_PARTICIPANTES: dict = {}


def _iniciar(pasta: str) -> None:
    _PARTICIPANTES.update({p.id: p for p in formar_participantes(Path(pasta))})


def _lote(pares: list[tuple[str, str]], seeds: int) -> list[tuple[str, str, dict]]:
    return [(a, b, confronto(_PARTICIPANTES[a], _PARTICIPANTES[b], seeds)) for a, b in pares]


def jogar_rodizio(participantes: list, seeds: int = SEEDS, trabalhadores: int = 1, pasta=PASTA):
    """Todos os pares. Devolve `{(a, b): resultado}` com `a < b` na ordem dos IDs."""
    ids = sorted(p.id for p in participantes)
    pares = list(combinations(ids, 2))
    if trabalhadores <= 1:
        por_id = {p.id: p for p in participantes}
        return {(a, b): confronto(por_id[a], por_id[b], seeds) for a, b in pares}
    lotes = [pares[i : i + 24] for i in range(0, len(pares), 24)]
    resultados = {}
    with ProcessPoolExecutor(
        max_workers=trabalhadores,
        mp_context=mp.get_context("spawn"),
        initializer=_iniciar,
        initargs=(str(pasta),),
    ) as pool:
        for lote in pool.map(_lote, lotes, [seeds] * len(lotes)):
            for a, b, resultado in lote:
                resultados[(a, b)] = resultado
    return resultados


# --- estatística ---------------------------------------------------------------


def bradley_terry(ids: list[str], vitorias: dict, iteracoes: int = 5000) -> dict[str, float]:
    """Força de Bradley-Terry (log, média zero) pelo algoritmo MM de Hunter (2004).

    `vitorias[(i, j)]` é quantas vezes `i` venceu `j`. Um meio-ponto de vitória
    contra cada adversário evita força infinita para quem nunca perdeu.
    """
    w = {i: sum(vitorias.get((i, j), 0) for j in ids if j != i) + 0.5 * (len(ids) - 1) for i in ids}
    n = {
        (i, j): vitorias.get((i, j), 0) + vitorias.get((j, i), 0) + 1.0
        for i in ids
        for j in ids
        if i != j
    }
    p = dict.fromkeys(ids, 1.0)
    for _ in range(iteracoes):
        novo = {i: w[i] / sum(n[(i, j)] / (p[i] + p[j]) for j in ids if j != i) for i in ids}
        media = math.exp(statistics.mean(math.log(v) for v in novo.values()))
        novo = {i: v / media for i, v in novo.items()}
        convergiu = max(abs(novo[i] - p[i]) for i in ids) < 1e-12
        p = novo
        if convergiu:
            break
    return {i: math.log(v) for i, v in p.items()}


def _postos(v: list[float]) -> list[float]:
    ordem = sorted(range(len(v)), key=lambda k: v[k])
    r = [0.0] * len(v)
    k = 0
    while k < len(ordem):
        j = k
        while j + 1 < len(ordem) and v[ordem[j + 1]] == v[ordem[k]]:
            j += 1
        for t in range(k, j + 1):
            r[ordem[t]] = (k + j) / 2 + 1
        k = j + 1
    return r


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else 0.0


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(_postos(x), _postos(y))


def _ajuste(x: list[float], y: list[float]) -> tuple[float, float]:
    mx, my = statistics.mean(x), statistics.mean(y)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return my - b * mx, b


# --- análise --------------------------------------------------------------------


def _atributos(participantes: list, gladiadores: dict) -> dict[str, dict]:
    """O que se pode ler de cada build, para cruzar com o resíduo."""
    saida = {}
    for p in participantes:
        h = prepare_gladiator(p.heroi).hero
        g = gladiadores[p.id]
        fam = Counter(g["familias"])
        tipos = Counter(get_skill_by_id(s).effect_type for s in g["deck"])
        saida[p.id] = {
            "HP máximo": h.base_hp,
            "MP máximo": h.base_mp,
            "ST": h.get_st(),
            "MG": h.get_mg(),
            "AG": h.get_ag(),
            "DF": h.get_df(),
            "Nível": g["nivel"],
            "Passivas de vida": fam["max_hp"],
            "Passivas de roubo de vida": fam["life_steal"],
            "Passivas de crítico": fam["crit_chance"] + fam["crit_damage"],
            "Passivas de defesa e redução": fam["defense"] + fam["damage_reduction"],
            "Passivas de força": fam["strength"],
            "Passivas de mana": fam["max_mp"] + fam["mana_regen"],
            "Passivas de agilidade e esquiva": fam["agility"] + fam["evasion"],
            "Passivas sem efeito no duelo": fam["essence_bonus"]
            + fam["gold_drop_bonus"]
            + fam["potion_heal_bonus"],
            "Cartas de dano": tipos["damage"],
            "Cartas de buff": tipos["buff"],
            "Cartas de status": tipos["status"],
            "Cartas de cura": tipos["heal"],
            "Cartas de redução de dano": tipos["damage_reduction"],
        }
    return saida


def _ciclos(ids: list[str], taxa_par: dict) -> list[tuple[str, str, str]]:
    """Triplas A > B > C > A, cada elo com pelo menos `ELO_DE_CICLO`."""

    def vence(x, y):
        return taxa_par.get((x, y), 0.0) >= ELO_DE_CICLO

    ciclos = []
    for a, b, c in combinations(ids, 3):
        if vence(a, b) and vence(b, c) and vence(c, a):
            ciclos.append((a, b, c))
        elif vence(a, c) and vence(c, b) and vence(b, a):
            ciclos.append((a, c, b))
    return ciclos


def analisar(participantes: list, resultados: dict, seeds: int, copa=None) -> dict:
    gladiadores = {g["id"]: g for g in ler_gladiadores()}
    por_id = {p.id: p for p in participantes}
    ids = sorted(por_id)
    vitorias, taxa_par = {}, {}
    inconclusivos = rodadas = 0
    for (a, b), r in resultados.items():
        vitorias[(a, b)], vitorias[(b, a)] = r["a"], r["b"]
        validos = r["a"] + r["b"]
        if validos:
            taxa_par[(a, b)], taxa_par[(b, a)] = r["a"] / validos, r["b"] / validos
        inconclusivos += r["inconclusivos"]
        rodadas += r["rodadas"]
    jogos = {i: sum(vitorias[(i, j)] + vitorias[(j, i)] for j in ids if j != i) for i in ids}
    taxa = {i: sum(vitorias[(i, j)] for j in ids if j != i) / jogos[i] for i in ids}
    forca = bradley_terry(ids, vitorias)
    ranking = sorted(ids, key=lambda i: -forca[i])
    op = {i: por_id[i].poder for i in ids}
    a0, b0 = _ajuste([op[i] for i in ids], [taxa[i] for i in ids])
    previsto = {i: a0 + b0 * op[i] for i in ids}
    residuo = {i: taxa[i] - previsto[i] for i in ids}
    r_op = pearson([op[i] for i in ids], [taxa[i] for i in ids])
    atributos = _atributos(participantes, gladiadores)
    correlacoes = []
    for nome in next(iter(atributos.values())):
        xs = [atributos[i][nome] for i in ids]
        if len(set(xs)) < 2:
            continue
        correlacoes.append(
            {
                "atributo": nome,
                "com_taxa": spearman(xs, [taxa[i] for i in ids]),
                "com_residuo": spearman(xs, [residuo[i] for i in ids]),
                "com_op": spearman(xs, [op[i] for i in ids]),
            }
        )
    correlacoes.sort(key=lambda c: -abs(c["com_residuo"]))
    canais = {}
    for canal in ("crítico", "defesa", "controle", "sustento"):
        com = [i for i in ids if canal in gladiadores[i]["arquetipos"]]
        sem = [i for i in ids if canal not in gladiadores[i]["arquetipos"]]
        canais[canal] = {
            "com": len(com),
            "taxa_com": statistics.mean(taxa[i] for i in com) if com else 0.0,
            "taxa_sem": statistics.mean(taxa[i] for i in sem) if sem else 0.0,
            "residuo_com": statistics.mean(residuo[i] for i in com) if com else 0.0,
            "residuo_sem": statistics.mean(residuo[i] for i in sem) if sem else 0.0,
        }
    grupos = {}
    for chave, valores in (("perfil", PERFIS), ("politica", POLITICAS)):
        grupos[chave] = {}
        for v in valores:
            membros = [i for i in ids if gladiadores[i][chave] == v]
            grupos[chave][v] = {
                "n": len(membros),
                "op": statistics.mean(op[i] for i in membros),
                "taxa": statistics.mean(taxa[i] for i in membros),
                "residuo": statistics.mean(residuo[i] for i in membros),
            }
    pares = list(combinations(ids, 2))
    decididos = sum(1 for a, b in pares if max(taxa_par[(a, b)], taxa_par[(b, a)]) >= DECISIVO)
    moeda = sum(1 for a, b in pares if abs(taxa_par[(a, b)] - 0.5) <= 0.1)
    contra_op = sorted(
        (
            (x, y, taxa_par[(x, y)])
            for a, b in pares
            for x, y in ((a, b), (b, a))
            if op[x] < op[y] and taxa_par[(x, y)] >= 0.7
        ),
        key=lambda t: (-(op[t[1]] - op[t[0]]), -t[2]),
    )
    favorito = [
        taxa_par[(a, b)] if op[a] > op[b] else taxa_par[(b, a)] for a, b in pares if op[a] != op[b]
    ]
    ciclos = _ciclos(ids, taxa_par)
    copa_md1 = None
    if copa is not None:
        venceu = Counter(p.vencedor.id for p in todas(copa))
        chegou = {}
        for partida in todas(copa):
            for lado in ("p1", "p2"):
                chegou[partida.lados[lado].id] = partida.fase
        copa_md1 = {
            "vitorias": {i: venceu[i] for i in ids},
            "campeao": copa.campeao.id,
            "spearman_vitorias_md1_taxa": spearman(
                [venceu[i] for i in ids], [taxa[i] for i in ids]
            ),
            "posicao_do_campeao": ranking.index(copa.campeao.id) + 1,
            "top8_nas_quartas": sum(
                1 for i in ranking[:8] if chegou[i] in ("quartas", "semifinal", "final")
            ),
        }
    return {
        "seeds": seeds,
        "duelos": sum(r["a"] + r["b"] + r["inconclusivos"] for r in resultados.values()),
        "inconclusivos": inconclusivos,
        "rodadas_media": rodadas / max(1, len(pares) * seeds),
        "ranking": [
            {
                "posicao": k + 1,
                "id": i,
                "nome": por_id[i].nome,
                "perfil": gladiadores[i]["perfil"],
                "politica": gladiadores[i]["politica"],
                "origem": gladiadores[i].get("origem", "original"),
                "op": op[i],
                "taxa": taxa[i],
                "forca": forca[i],
                "previsto": previsto[i],
                "residuo": residuo[i],
                "canais": gladiadores[i]["arquetipos"],
                "deck": [get_skill_by_id(s).name for s in gladiadores[i]["deck"]],
                "atributos": atributos[i],
            }
            for k, i in enumerate(ranking)
        ],
        "op_explica": {
            "spearman": spearman([op[i] for i in ids], [taxa[i] for i in ids]),
            "pearson": r_op,
            "r2": r_op**2,
            "inclinacao_por_ponto_de_op": b0,
        },
        "favorito_por_op": statistics.mean(favorito),
        "correlacoes": correlacoes,
        "canais": canais,
        "grupos": grupos,
        "pares": len(pares),
        "pares_decididos": decididos,
        "pares_moeda": moeda,
        "contra_op": [
            {"vencedor": x, "perdedor": y, "taxa": t, "delta_op": op[y] - op[x]}
            for x, y, t in contra_op
        ],
        "ciclos": len(ciclos),
        "exemplos_de_ciclo": [list(c) for c in ciclos[:5]],
        "copa_md1": copa_md1,
        "matriz": {f"{a}|{b}": r for (a, b), r in resultados.items()},
    }


# --- relatório ------------------------------------------------------------------


def _pct(v: float) -> str:
    return f"{v:.1%}"


def _linha_de_build(r: dict) -> str:
    a = r["atributos"]
    return (
        f"- **{r['nome']} ({r['id']})**, OP {r['op']:.2f}: taxa {_pct(r['taxa'])} contra "
        f"{_pct(r['previsto'])} previstos ({r['residuo']:+.1%}). HP {a['HP máximo']}, MP "
        f"{a['MP máximo']}, ST {a['ST']}, DF {a['DF']}, AG {a['AG']}; "
        f"{', '.join(r['canais']) or 'sem canal'}; {', '.join(r['deck'])}."
    )


def relatorio_md(d: dict) -> str:
    rk = d["ranking"]
    por_id = {r["id"]: r for r in rk}
    oe = d["op_explica"]
    md1 = d["copa_md1"]

    def quem(i):
        return f"{por_id[i]['nome']} ({i})"

    linhas = [
        "# Copa Arena 03 — todos contra todos",
        "",
        "Gerado por `tools/arena_copa_03_round_robin.py`. Os 64 gladiadores da Copa 03, "
        f"reconstruídos dos snapshots, em todos os {d['pares']} pares, {d['seeds']} duelos por "
        "par (metade com os lados trocados), com a mesma `PoliticaCopa` e o mesmo motor da "
        f"Copa. {d['duelos']} duelos, {d['inconclusivos']} inconclusivos no limite técnico, "
        f"{d['rodadas_media']:.1f} rodadas por duelo em média.",
        "",
        "> Correlação não é causa: perfil, política, RNG da jornada e build vêm juntos em cada "
        "gladiador. O OP é o medido na geração, contra o boneco fixo da Arena.",
        "",
        "## Resumo",
        "",
        f"- **O OP explica {oe['r2']:.0%} da variação da força real** (R² linear da taxa de "
        f"vitória contra o OP; Spearman {oe['spearman']:.2f}). Cada ponto de OP vale "
        f"{oe['inclinacao_por_ponto_de_op']:+.1%} de taxa de vitória.",
        f"- O de OP maior vence {_pct(d['favorito_por_op'])} dos duelos, em média, nos pares "
        "de OP diferente.",
        f"- {d['pares_decididos']} dos {d['pares']} pares "
        f"({d['pares_decididos'] / d['pares']:.0%}) são decididos pela build (um lado vence "
        f"{DECISIVO:.0%} ou mais); {d['pares_moeda']} ({d['pares_moeda'] / d['pares']:.0%}) são "
        "moeda (40–60%).",
        f"- {len(d['contra_op'])} confrontos têm o OP menor vencendo 70% ou mais; "
        f"{d['ciclos']} ciclos pedra-papel-tesoura (A vence B, B vence C, C vence A, cada um "
        f"com {ELO_DE_CICLO:.0%} ou mais).",
    ]
    if md1:
        linhas.append(
            f"- A Copa MD1 e o todos-contra-todos concordam em parte: Spearman "
            f"{md1['spearman_vitorias_md1_taxa']:.2f} entre vitórias na Copa e taxa aqui. O "
            f"campeão, {quem(md1['campeao'])}, é o {md1['posicao_do_campeao']}º mais forte; "
            f"{md1['top8_nas_quartas']} dos 8 mais fortes chegaram às quartas."
        )
    linhas += [
        "",
        "## O ranking robusto",
        "",
        "Força de Bradley-Terry (log, média zero) e taxa de vitória contra os outros 63. "
        '"Previsto" é a taxa que o OP prevê pelo ajuste linear; "resíduo" é o que a build '
        "rende acima (+) ou abaixo (−) disso.",
        "",
        "| # | Gladiador | Perfil/política | OP | Taxa | Previsto | Resíduo | Força BT | Canais "
        "| Deck |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rk:
        linhas.append(
            f"| {r['posicao']} | {r['nome']} ({r['id']}) | {PERFIL_PT[r['perfil']]}/"
            f"{r['politica']}{' · preench.' if r['origem'] != 'original' else ''} | {r['op']:.2f} "
            f"| {_pct(r['taxa'])} | {_pct(r['previsto'])} | {r['residuo']:+.1%} "
            f"| {r['forca']:+.2f} | {', '.join(r['canais']) or '—'} | {', '.join(r['deck'])} |"
        )
    linhas += ["", "## A sinergia: quem rende acima e abaixo do próprio OP", ""]
    linhas += ["### Mais acima do OP", ""]
    linhas += [_linha_de_build(r) for r in sorted(rk, key=lambda r: -r["residuo"])[:8]]
    linhas += ["", "### Mais abaixo do OP", ""]
    linhas += [_linha_de_build(r) for r in sorted(rk, key=lambda r: r["residuo"])[:8]]
    linhas += [
        "",
        "### O que acompanha o resíduo",
        "",
        "Spearman de cada característica da build com a taxa de vitória, com o resíduo (o que "
        "sobra depois do OP) e com o próprio OP. Ordenado pelo peso no resíduo.",
        "",
        "| Característica | Com a taxa | Com o resíduo | Com o OP |",
        "|---|---|---|---|",
    ]
    for c in d["correlacoes"]:
        linhas.append(
            f"| {c['atributo']} | {c['com_taxa']:+.2f} | {c['com_residuo']:+.2f} "
            f"| {c['com_op']:+.2f} |"
        )
    linhas += [
        "",
        "### Canais da build",
        "",
        "| Canal | Builds | Taxa com | Taxa sem | Resíduo com | Resíduo sem |",
        "|---|---|---|---|---|---|",
    ]
    for canal, v in d["canais"].items():
        linhas.append(
            f"| {canal} | {v['com']} | {_pct(v['taxa_com'])} | {_pct(v['taxa_sem'])} "
            f"| {v['residuo_com']:+.1%} | {v['residuo_sem']:+.1%} |"
        )
    linhas += ["", "### Perfil e política", "", "| Grupo | n | OP médio | Taxa | Resíduo |"]
    linhas.append("|---|---|---|---|---|")
    for chave, nomes in (("perfil", PERFIL_PT), ("politica", {p: p for p in POLITICAS})):
        for v, x in d["grupos"][chave].items():
            linhas.append(
                f"| {nomes[v]} | {x['n']} | {x['op']:.2f} | {_pct(x['taxa'])} "
                f"| {x['residuo']:+.1%} |"
            )
    linhas += [
        "",
        "## Confrontos",
        "",
        f"Os 10 confrontos em que o OP menor vence com mais folga ({len(d['contra_op'])} no "
        "total com 70% ou mais):",
        "",
        "| Vencedor (OP) | Perdedor (OP) | ΔOP contra | Taxa |",
        "|---|---|---|---|",
    ]
    for c in d["contra_op"][:10]:
        v, p = por_id[c["vencedor"]], por_id[c["perdedor"]]
        linhas.append(
            f"| {v['nome']} ({v['op']:.2f}) | {p['nome']} ({p['op']:.2f}) "
            f"| {c['delta_op']:.2f} | {_pct(c['taxa'])} |"
        )
    if d["exemplos_de_ciclo"]:
        linhas += ["", "Exemplos de ciclo:", ""]
        for a, b, c in d["exemplos_de_ciclo"]:
            linhas.append(f"- {quem(a)} > {quem(b)} > {quem(c)} > {quem(a)}")
    return "\n".join(linhas) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=SEEDS)
    parser.add_argument("--trabalhadores", type=int, default=os.cpu_count() or 2)
    args = parser.parse_args(argv)
    participantes = formar_participantes()
    resultados = jogar_rodizio(participantes, args.seeds, args.trabalhadores)
    dados = analisar(participantes, resultados, args.seeds, copa=disputar_copa(participantes))
    (PASTA / ARQUIVO_JSON).write_text(
        json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (PASTA / ARQUIVO_MD).write_text(relatorio_md(dados), encoding="utf-8")
    oe = dados["op_explica"]
    print(f"duelos {dados['duelos']} | OP explica R² {oe['r2']:.2f} | ciclos {dados['ciclos']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
