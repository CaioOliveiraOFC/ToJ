"""Ranked offline: amostra real, comparação Glicko-2 × TrueSkill, calibração e grind.

Uso:
    python tools/ranked_experimentos.py amostra [--trabalhadores 4]
    python tools/ranked_experimentos.py comparar

Todo confronto daqui é uma partida REAL do motor PvP entre dois gladiadores da
população (`src/engine/ranked_partidas.jogar`): a IA estratégica dos dois lados,
o gerador semeado. Nenhum resultado é sorteado por fórmula.

## A amostra (`amostra`)

Pequena e conectada, desenhada para informação e não para volume. A população
é ordenada pela força de referência (o OP da geração):

- `proximo`: cada gladiador contra o vizinho de OP — a corrente que conecta os
  186;
- `distante`: um terço de baixo contra um terço de cima, ao acaso;
- `classes`: Warrior × Mage, Mage × Rogue e Rogue × Warrior com OP parecido;
- `estilos`: mesma classe, perfis de run diferentes;
- `repeticao`: duplas de `proximo` outra vez, com duas seeds novas — mede o
  quanto o resultado depende da sorte;
- `holdout`: duplas que não aparecem no treino, nos mesmos estratos, para
  medir previsão de confronto não visto.

Os confrontos vão para `reports/ranked/_trabalho/amostra.jsonl` (checkpoint:
uma linha por partida, e quem retoma não repete nenhuma) e, no fim, para
`reports/ranked/amostra.jsonl`.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import multiprocessing as mp
import os
import random
import sys
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.engine.arena_populacao import Populacao  # noqa: E402
from src.engine.ranked_partidas import jogar  # noqa: E402

PASTA = RAIZ / "reports" / "ranked"
TRABALHO = PASTA / "_trabalho"
SEMENTE = 20261027


def semente(*partes) -> int:
    texto = ":".join(str(p) for p in (SEMENTE, *partes))
    return int.from_bytes(hashlib.sha256(texto.encode()).digest()[:8], "big")


# --- o desenho da amostra ---------------------------------------------------------


def desenho(populacao: Populacao) -> list[dict]:
    """As partidas da amostra, em ordem fixa. Determinístico pela `SEMENTE`."""
    rng = random.Random(semente("desenho"))
    ordem = populacao.oponentes()
    n = len(ordem)
    vistos: set[frozenset] = set()
    partidas: list[dict] = []

    def incluir(a, b, estrato: str, k: int = 0) -> bool:
        par = frozenset((a.id, b.id))
        if a.id == b.id or (k == 0 and par in vistos):
            return False
        vistos.add(par)
        partidas.append(
            {"a": a.id, "b": b.id, "estrato": estrato, "semente": semente(a.id, b.id, k)}
        )
        return True

    for i in range(n - 1):
        incluir(ordem[i], ordem[i + 1], "proximo")
    terco = n // 3
    baixo, cima = ordem[:terco], ordem[-terco:]
    for a in baixo:
        while not incluir(a, rng.choice(cima), "distante"):
            pass
    pares_de_classe = (("warrior", "mage"), ("mage", "rogue"), ("rogue", "warrior"))
    for ca, cb in pares_de_classe:
        feitos = 0
        while feitos < 20:
            a = rng.choice(populacao.oponentes(ca))
            perto = [o for o in populacao.oponentes(cb) if abs(o.op - a.op) <= 1.5]
            if perto and incluir(a, rng.choice(perto), "classes"):
                feitos += 1
    feitos = 0
    while feitos < 30:
        a = rng.choice(ordem)
        outros = [o for o in populacao.oponentes(a.classe) if o.perfil != a.perfil]
        if incluir(a, rng.choice(outros), "estilos"):
            feitos += 1
    proximos = [p for p in partidas if p["estrato"] == "proximo"]
    for p in rng.sample(proximos, 30):
        a, b = populacao.get(p["a"]), populacao.get(p["b"])
        for k in (1, 2):
            incluir(a, b, "repeticao", k)
    # O holdout: duplas novas nos mesmos estratos.
    feitos = 0
    while feitos < 40:
        i = rng.randrange(n - 3)
        if incluir(ordem[i], ordem[i + rng.choice((2, 3))], "holdout_proximo"):
            feitos += 1
    feitos = 0
    while feitos < 40:
        a, b = rng.sample(ordem, 2)
        if incluir(a, b, "holdout_aleatorio"):
            feitos += 1
    feitos = 0
    while feitos < 40:
        ca, cb = rng.choice(pares_de_classe)
        a = rng.choice(populacao.oponentes(ca))
        perto = [o for o in populacao.oponentes(cb) if abs(o.op - a.op) <= 1.5]
        if perto and incluir(a, rng.choice(perto), "holdout_classes"):
            feitos += 1
    return partidas


def _jogar(partida: dict) -> dict:
    confronto = jogar(Populacao(), partida["a"], partida["b"], partida["semente"])
    if confronto is None:
        return {**partida, "vencedor": None, "motivo": "limite"}
    return {**partida, **confronto.para_dict()}


def rodar(partidas: list[dict], arquivo: Path, trabalhadores: int = 4) -> list[dict]:
    """Joga o que falta, com checkpoint por partida concluída."""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    feitas = {}
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(linha)
            except json.JSONDecodeError:
                break
            feitas[(r["a"], r["b"], r["semente"])] = r
    pendentes = [p for p in partidas if (p["a"], p["b"], p["semente"]) not in feitas]
    contexto = mp.get_context("spawn")
    with ProcessPoolExecutor(trabalhadores, mp_context=contexto) as pool:
        futuros = {pool.submit(_jogar, p): p for p in pendentes}
        with open(arquivo, "a", encoding="utf-8") as saida:
            feitos = 0
            while futuros:
                prontos, _ = wait(futuros, return_when=FIRST_COMPLETED)
                for futuro in prontos:
                    futuros.pop(futuro)
                    r = futuro.result()
                    saida.write(json.dumps(r, ensure_ascii=False) + "\n")
                    saida.flush()
                    os.fsync(saida.fileno())
                    feitas[(r["a"], r["b"], r["semente"])] = r
                    feitos += 1
                    if feitos % 50 == 0:
                        print(f"{feitos}/{len(pendentes)} partidas", flush=True)
    return [feitas[(p["a"], p["b"], p["semente"])] for p in partidas]


def amostra(trabalhadores: int = 4) -> list[dict]:
    partidas = desenho(Populacao())
    resultados = rodar(partidas, TRABALHO / "amostra.jsonl", trabalhadores)
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "amostra.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in resultados), encoding="utf-8"
    )
    return resultados


# --- a comparação (`comparar`) -------------------------------------------------------

TREINO = ("proximo", "distante", "classes", "estilos", "repeticao")
PERMUTACOES = 30


def _ler_amostra() -> list[dict]:
    linhas = (PASTA / "amostra.jsonl").read_text(encoding="utf-8").splitlines()
    return [r for r in map(json.loads, linhas) if r.get("vencedor")]


def _logistica_do_op(treino: list[dict], op: dict) -> float:
    """O k de P(a vence) = σ(k·(OP_a − OP_b)), por máxima verossimilhança (Newton)."""
    k = 0.1
    for _ in range(50):
        g = h = 0.0
        for r in treino:
            d = op[r["a"]] - op[r["b"]]
            y = 1.0 if r["vencedor"] == r["a"] else 0.0
            p = 1.0 / (1.0 + math.exp(-k * d))
            g += (y - p) * d
            h -= p * (1.0 - p) * d * d
        passo = g / h
        k -= passo
        if abs(passo) < 1e-10:
            break
    return k


def _bradley_terry(treino: list[dict], ids: list[str], prior: float = 0.5) -> dict:
    """Forças em lote (logit), com priori gaussiana leve para dar conta de quem nunca perdeu."""
    s = dict.fromkeys(ids, 0.0)
    for _ in range(300):
        grad = {i: -s[i] * prior for i in ids}
        hess = dict.fromkeys(ids, prior)
        for r in treino:
            a, b = r["a"], r["b"]
            p = 1.0 / (1.0 + math.exp(-(s[a] - s[b])))
            y = 1.0 if r["vencedor"] == a else 0.0
            grad[a] += y - p
            grad[b] -= y - p
            hess[a] += p * (1 - p)
            hess[b] += p * (1 - p)
        maior = 0.0
        for i in ids:
            passo = grad[i] / hess[i]
            s[i] += passo
            maior = max(maior, abs(passo))
        if maior < 1e-8:
            break
    return s


class _Sistema:
    """Um sistema com priori: plano, ou o OP como estimativa inicial fraca."""

    def __init__(self, nome, sistema, inicial):
        self.nome, self.s, self.inicial = nome, sistema, inicial

    def rodar(self, partidas, ids):
        r = {i: self.inicial(i) for i in ids}
        perdas = []
        for p in partidas:
            a, b = p["a"], p["b"]
            prob = self.s.esperado(r[a], r[b])
            venceu = p["vencedor"] == a
            perdas.append(-math.log(max(1e-12, prob if venceu else 1.0 - prob)))
            r[a], r[b] = self.s.partida(r[a], r[b], venceu)
        return r, perdas


def _sistemas(op: dict, k_op: float):
    from src.ranked.glicko2 import ESCALA, Glicko2
    from src.ranked.trueskill import TrueSkill

    centro = sorted(op.values())[len(op) // 2]
    fraco = 0.5  # o OP entra pela metade: estimativa fraca

    def logit(i):
        # O mesmo teto da priori do jogo (`sistema.LOGIT_MAXIMO`).
        return max(-3.0, min(3.0, k_op * fraco * (op[i] - centro)))

    lista = []
    for tau in (0.3, 0.6, 1.0):
        g = Glicko2(tau=tau)
        lista.append(_Sistema(f"Glicko-2 τ={tau} plano", g, lambda i, g=g: g.novo()))
        lista.append(
            _Sistema(
                f"Glicko-2 τ={tau} OP",
                g,
                lambda i, g=g: g.novo(1500.0 + ESCALA * logit(i)),
            )
        )
    for divisor in (2.0, 4.0, 8.0):
        ts = TrueSkill(beta=25.0 / 3.0 / divisor)
        escala = math.sqrt(2.0) * ts.beta / 1.702
        lista.append(_Sistema(f"TrueSkill β=σ/{divisor:g} plano", ts, lambda i, t=ts: t.novo()))
        lista.append(
            _Sistema(
                f"TrueSkill β=σ/{divisor:g} OP",
                ts,
                lambda i, t=ts, e=escala: t.novo(25.0 + e * logit(i)),
            )
        )
    return lista


def _metricas(probs: list[float], ganhou: list[bool]) -> dict:
    n = len(probs)
    perda = sum(-math.log(max(1e-12, p if y else 1 - p)) for p, y in zip(probs, ganhou)) / n
    brier = sum((p - (1.0 if y else 0.0)) ** 2 for p, y in zip(probs, ganhou)) / n
    acerto = sum((p > 0.5) == y for p, y in zip(probs, ganhou) if p != 0.5) / max(
        1, sum(p != 0.5 for p in probs)
    )
    caixas = [[] for _ in range(5)]
    for p, y in zip(probs, ganhou):
        # Calibração simétrica: a probabilidade do lado favorito.
        q, z = (p, y) if p >= 0.5 else (1 - p, not y)
        caixas[min(4, int((q - 0.5) / 0.1))].append((q, z))
    ece = (
        sum(
            len(c) * abs(sum(q for q, _ in c) / len(c) - sum(z for _, z in c) / len(c))
            for c in caixas
            if c
        )
        / n
    )
    return {"log_loss": perda, "brier": brier, "acerto": acerto, "ece": ece}


def _spearman(x: list[float], y: list[float]) -> float:
    def postos(v):
        ordem = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(ordem):
            r[i] = pos
        return r

    rx, ry = postos(x), postos(y)
    n = len(x)
    mx = (n - 1) / 2
    num = sum((a - mx) * (b - mx) for a, b in zip(rx, ry))
    den = sum((a - mx) ** 2 for a in rx)
    return num / den


def _sequencias(sistema: _Sistema, finais: dict, ids: list[str]) -> dict:
    """Sensibilidade a sequências: resultados INJETADOS sobre o estado calibrado.

    Não é previsão: é a sonda de quanto cada sistema mexe no rating e na posição
    de um gladiador mediano com cinco vitórias seguidas contra iguais, contra
    muito mais fracos, e com resultados alternados.
    """
    s = sistema.s
    ordem = sorted(ids, key=lambda i: s.exibicao(finais[i]))
    valores = [s.exibicao(finais[i]) for i in ordem]
    media = sum(valores) / len(valores)
    dp = math.sqrt(sum((v - media) ** 2 for v in valores) / len(valores))
    alvo = ordem[len(ordem) // 2]
    iguais = sorted(
        (i for i in ids if i != alvo),
        key=lambda i: abs(s.exibicao(finais[i]) - s.exibicao(finais[alvo])),
    )[:5]
    fracos = ordem[: max(5, len(ordem) // 10)][:5]

    def jogar(sequencia):
        r = finais[alvo]
        for oponente, venceu in sequencia:
            r = s.partida(r, finais[oponente], venceu)[0]
        delta = (s.exibicao(r) - s.exibicao(finais[alvo])) / dp
        posicao = sum(v > s.exibicao(r) for i, v in zip(ordem, valores) if i != alvo) + 1
        return {"delta_em_dp": round(delta, 3), "posicao": posicao}

    antes = sum(v > s.exibicao(finais[alvo]) for i, v in zip(ordem, valores) if i != alvo) + 1
    return {
        "posicao_inicial": antes,
        "cinco_vitorias_contra_iguais": jogar([(o, True) for o in iguais]),
        "cinco_vitorias_contra_fracos": jogar([(o, True) for o in fracos]),
        "alternado_seis": jogar([(iguais[i % 5], i % 2 == 0) for i in range(6)]),
        "cinco_derrotas_e_cinco_vitorias": jogar(
            [(o, False) for o in iguais] + [(o, True) for o in iguais]
        ),
    }


def _avaliar_sistemas(treino, teste, op, k_op, ids, cronologica: bool) -> dict:
    """Cada sistema sobre o treino, em ordens permutadas (e na cronológica, se houver)."""
    rng = random.Random(semente("permutacoes"))
    ordens = [list(treino)] if cronologica else []
    while len(ordens) < PERMUTACOES:
        ordem = list(treino)
        rng.shuffle(ordem)
        ordens.append(ordem)
    estratos = sorted({r["estrato"] for r in teste})
    resultado = {}
    for sistema in _sistemas(op, k_op):
        holdout, preq, rankings, finais0 = [], [], [], None
        for n, ordem in enumerate(ordens):
            finais, perdas = sistema.rodar(ordem, ids)
            if n == 0:
                finais0 = finais
            preq.append(perdas)
            probs = [sistema.s.esperado(finais[r["a"]], finais[r["b"]]) for r in teste]
            holdout.append(_metricas(probs, [r["vencedor"] == r["a"] for r in teste]))
            rankings.append([sistema.s.exibicao(finais[i]) for i in ids])
        media = {k: sum(h[k] for h in holdout) / len(holdout) for k in holdout[0]}
        passo = max(100, len(treino) // 8)
        janelas = [
            round(sum(sum(p[j : j + passo]) / len(p[j : j + passo]) for p in preq) / len(preq), 4)
            for j in range(0, len(treino), passo)
        ]
        pares = [
            _spearman(rankings[i], rankings[j])
            for i in range(len(rankings))
            for j in range(i + 1, min(len(rankings), i + 6))
        ]
        frequencia: dict = {}
        for valores in rankings:
            for k in sorted(range(len(ids)), key=lambda i: -valores[i])[:5]:
                frequencia[ids[k]] = frequencia.get(ids[k], 0) + 1
        jogos = {i: 0 for i in ids}
        for r in treino:
            jogos[r["a"]] += 1
            jogos[r["b"]] += 1
        por_estrato = {}
        for estrato in estratos:
            sub = [r for r in teste if r["estrato"] == estrato]
            probs = [sistema.s.esperado(finais0[r["a"]], finais0[r["b"]]) for r in sub]
            por_estrato[estrato] = round(
                _metricas(probs, [r["vencedor"] == r["a"] for r in sub])["log_loss"], 4
            )
        resultado[sistema.nome] = {
            "holdout": {k: round(v, 4) for k, v in media.items()},
            "holdout_dp_log_loss": round(
                math.sqrt(
                    sum((h["log_loss"] - media["log_loss"]) ** 2 for h in holdout) / len(holdout)
                ),
                4,
            ),
            "holdout_por_estrato": por_estrato,
            "prequencial_por_janela": janelas,
            "janela": passo,
            "estabilidade_spearman": round(sum(pares) / len(pares), 4),
            "top5_mais_frequentes": sorted(frequencia.items(), key=lambda x: -x[1])[:8],
            "incerteza_x_jogos_spearman": round(
                _spearman([sistema.s.incerteza(finais0[i]) for i in ids], [-jogos[i] for i in ids]),
                4,
            ),
            "sequencias": _sequencias(sistema, finais0, ids),
        }
    return resultado


def _linhas_de_base(treino, teste, op, k_op, ids) -> dict:
    base = {
        "moeda": _metricas([0.5] * len(teste), [True] * len(teste)),
        "OP logístico": _metricas(
            [1 / (1 + math.exp(-k_op * (op[r["a"]] - op[r["b"]]))) for r in teste],
            [r["vencedor"] == r["a"] for r in teste],
        ),
    }
    bt = _bradley_terry(treino, ids)
    base["Bradley-Terry em lote"] = _metricas(
        [1 / (1 + math.exp(-(bt[r["a"]] - bt[r["b"]]))) for r in teste],
        [r["vencedor"] == r["a"] for r in teste],
    )
    return {k: {m: round(v, 4) for m, v in d.items()} for k, d in base.items()}


def comparar() -> dict:
    populacao = Populacao()
    op = {o.id: o.op for o in populacao}
    ids = sorted(op)
    amostra_ = _ler_amostra()
    treino = [r for r in amostra_ if r["estrato"] in TREINO]
    teste = [r for r in amostra_ if r["estrato"].startswith("holdout")]
    k_op = _logistica_do_op(treino, op)

    # O teto da sorte: as duplas repetidas com seeds diferentes.
    grupos: dict = {}
    for r in amostra_:
        if r["estrato"] in ("proximo", "repeticao"):
            grupos.setdefault(frozenset((r["a"], r["b"])), []).append(r["vencedor"])
    trios = [v for v in grupos.values() if len(v) == 3]
    unanimes = sum(len(set(v)) == 1 for v in trios)

    resultado = _avaliar_sistemas(treino, teste, op, k_op, ids, cronologica=False)

    relatorio = {
        "partidas": {"treino": len(treino), "holdout": len(teste)},
        "k_op_logit_por_ponto": round(k_op, 4),
        "repeticoes": {"trios": len(trios), "vencedor_unanime": unanimes},
        "custo_medio_s": round(sum(r["segundos"] for r in amostra_) / len(amostra_), 3),
        "rodadas_medias": round(sum(r["rodadas"] for r in amostra_) / len(amostra_), 1),
        "linhas_de_base": _linhas_de_base(treino, teste, op, k_op, ids),
        "sistemas": resultado,
    }
    (PASTA / "comparacao.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=1, default=list), encoding="utf-8"
    )
    return relatorio


# --- a calibração dos 186 (`calibrar`) ------------------------------------------------

RODADAS = 12
RECENTES_NA_CALIBRACAO = 8
# A cada `EXPLORAR` rodadas, a vizinhança cresce: o grafo de confrontos continua
# ligando níveis diferentes, e não só vizinhos de rating.
EXPLORAR = 3


def ladder_inicial(sistema, populacao: Populacao):
    """Os 186 com a priori fraca do OP e nenhuma partida."""
    from src.ranked.ladder import Ladder, Registro
    from src.ranked.sistema import inicial

    return Ladder(
        sistema,
        [
            Registro(
                identidade=o.id,
                nome=o.apelido,
                classe=o.classe,
                npc=True,
                rating=inicial(sistema, o.op),
                forca_de_referencia=o.op,
            )
            for o in populacao.oponentes()
        ],
    )


def _aplicar(ladder, partidas: list[dict], origem: str) -> int:
    aplicadas = 0
    for r in partidas:
        if r.get("vencedor"):
            ladder.registrar(r["a"], r["b"], r["vencedor"], origem=origem)
            aplicadas += 1
    return aplicadas


def _ranking(ladder) -> list[str]:
    return [r.identidade for r in ladder.classificacao()]


def partidas_da_rodada(ladder, rodada: int) -> list[dict]:
    """As duplas de uma rodada suíça, pelo estado da Ladder no começo dela."""
    from src.ranked import matchmaking as mm

    rng = random.Random(semente("calibracao", rodada))
    vizinhos = 8 if rodada % EXPLORAR == 0 else 4
    pares = mm.rodada_suica(ladder, rng, vizinhos, RECENTES_NA_CALIBRACAO)
    return [
        {
            "a": a,
            "b": b,
            "estrato": f"calibracao_{rodada:02d}",
            "semente": semente("calibracao", rodada, a, b),
        }
        for a, b in pares
    ]


def calibrar(trabalhadores: int = 4, rodadas: int = RODADAS) -> dict:
    """A amostra real e depois `rodadas` rodadas suíças. Retomável pelo checkpoint."""
    from src.ranked import sistema as sis

    populacao = Populacao()
    sistema = sis.criar()
    ladder = ladder_inicial(sistema, populacao)
    _aplicar(ladder, _ler_amostra(), "amostra")
    trajetoria = []
    anterior = _ranking(ladder)
    for rodada in range(1, rodadas + 1):
        partidas = partidas_da_rodada(ladder, rodada)
        resultados = rodar(partidas, TRABALHO / "calibracao.jsonl", trabalhadores)
        _aplicar(ladder, resultados, "calibracao")
        atual = _ranking(ladder)
        posicao = {i: k for k, i in enumerate(atual)}
        rds = [ladder.incerteza(i) for i in atual]
        trajetoria.append(
            {
                "rodada": rodada,
                "partidas": len(resultados),
                "sem_resultado": sum(1 for r in resultados if not r.get("vencedor")),
                "rd_medio": round(sum(rds) / len(rds), 1),
                "spearman_com_a_anterior": round(
                    _spearman(list(range(len(anterior))), [posicao[i] for i in anterior]), 4
                ),
                "top5": atual[:5],
            }
        )
        print(json.dumps(trajetoria[-1], ensure_ascii=False), flush=True)
        anterior = atual
    estado = {
        "algoritmo": sis.ALGORITMO,
        "parametros": sis.PARAMETROS,
        "rodadas": rodadas,
        "trajetoria": trajetoria,
        "ladder": ladder.para_dict(),
    }
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "calibracao.json").write_text(
        json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    linhas = (TRABALHO / "calibracao.jsonl").read_text(encoding="utf-8")
    (PASTA / "calibracao.jsonl").write_text(linhas, encoding="utf-8")
    return estado


# --- a comparação ampliada (`holdout2` e `comparar --ampliada`) ---------------------


def desenho_holdout2(ladder, populacao: Populacao) -> list[dict]:
    """150 duplas que nunca jogaram, sobre a classificação calibrada."""
    rng = random.Random(semente("holdout2"))
    jogados = set()
    for arquivo in ("amostra.jsonl", "calibracao.jsonl"):
        for linha in (PASTA / arquivo).read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            jogados.add(frozenset((r["a"], r["b"])))
    ordem = _ranking(ladder)
    partidas: list[dict] = []

    def incluir(a: str, b: str, estrato: str) -> bool:
        par = frozenset((a, b))
        if a == b or par in jogados:
            return False
        jogados.add(par)
        partidas.append({"a": a, "b": b, "estrato": estrato, "semente": semente("h2", a, b)})
        return True

    feitos = 0
    while feitos < 50:
        i = rng.randrange(len(ordem) - 4)
        feitos += incluir(ordem[i], ordem[i + rng.randint(1, 4)], "h2_vizinhos")
    feitos = 0
    while feitos < 50:
        a, b = rng.sample(ordem, 2)
        feitos += incluir(a, b, "h2_aleatorio")
    classe = {o.id: o.classe for o in populacao}
    feitos = 0
    while feitos < 50:
        i = rng.randrange(len(ordem))
        perto = [
            ordem[j]
            for j in range(max(0, i - 8), min(len(ordem), i + 9))
            if classe[ordem[j]] != classe[ordem[i]]
        ]
        if perto:
            feitos += incluir(ordem[i], rng.choice(perto), "h2_classes")
    return partidas


def holdout2(trabalhadores: int = 4) -> list[dict]:
    from src.ranked import sistema as sis
    from src.ranked.ladder import Ladder

    estado = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    ladder = Ladder.de_dict(sis.criar(), estado["ladder"])
    partidas = desenho_holdout2(ladder, Populacao())
    resultados = rodar(partidas, TRABALHO / "holdout2.jsonl", trabalhadores)
    (PASTA / "holdout2.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in resultados), encoding="utf-8"
    )
    return resultados


def comparar_ampliada() -> dict:
    populacao = Populacao()
    op = {o.id: o.op for o in populacao}
    ids = sorted(op)

    def ler(nome):
        linhas = (PASTA / nome).read_text(encoding="utf-8").splitlines()
        return [r for r in map(json.loads, linhas) if r.get("vencedor")]

    treino = ler("amostra.jsonl") + ler("calibracao.jsonl")
    teste = ler("holdout2.jsonl")
    k_op = _logistica_do_op([r for r in treino if r["estrato"] in TREINO], op)
    relatorio = {
        "partidas": {"treino": len(treino), "holdout": len(teste)},
        "k_op_logit_por_ponto": round(k_op, 4),
        "linhas_de_base": _linhas_de_base(treino, teste, op, k_op, ids),
        "sistemas": _avaliar_sistemas(treino, teste, op, k_op, ids, cronologica=True),
    }
    (PASTA / "comparacao_ampliada.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=1, default=list), encoding="utf-8"
    )
    return relatorio


# --- o jogador artificial (`grind`) -------------------------------------------------

# Hipótese explícita de tempo humano: uma partida ranqueada leva 3 minutos de
# jogo (≈ 23 rodadas medidas na amostra, ~6 s por decisão, mais o resumo de cada
# rodada e as telas). É só a régua das horas equivalentes; o custo real é o de
# CPU, medido à parte.
MINUTOS_POR_PARTIDA = 3.0
HORAS = (2, 5, 10, 20)


def _jogador(id_gemeo: str) -> str:
    return f"jogador:{id_gemeo}"


def _grind_um(id_gemeo: str, partidas: int, mundo_por_partida: int, arquivo: str) -> str:
    """A carreira de um jogador artificial, com checkpoint por partida."""
    from src.ranked import matchmaking as mm
    from src.ranked import sistema as sis
    from src.ranked.ladder import Ladder, Registro

    populacao = Populacao()
    estado = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    sistema = sis.criar()
    ladder = Ladder.de_dict(sistema, estado["ladder"])
    gemeo = populacao.get(id_gemeo)
    eu = _jogador(id_gemeo)
    ladder.adicionar(Registro(eu, gemeo.apelido, gemeo.classe, False, sis.inicial(sistema)))
    caminho = Path(arquivo)
    feitas = []
    if caminho.exists():
        feitas = [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines()]
    with open(caminho, "a", encoding="utf-8") as saida:
        for n in range(1, partidas + 1):
            if n <= len(feitas):
                registro = feitas[n - 1]
            else:
                registro = _uma_partida(ladder, populacao, eu, id_gemeo, n, mundo_por_partida, mm)
                saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
                saida.flush()
                os.fsync(saida.fileno())
                continue
            # Retomada: reaplica o que já foi jogado, na mesma ordem.
            ladder.registrar(eu, registro["oponente"], registro["vencedor_id"], origem="ranqueada")
            for m in registro["mundo"]:
                ladder.registrar(m["a"], m["b"], m["vencedor"], origem="mundo")
    return arquivo


def _uma_partida(ladder, populacao, eu, id_gemeo, n, mundo_por_partida, mm) -> dict:
    rng = random.Random(semente("grind", eu, n))
    escolha = mm.escolher_oponente(ladder, eu, rng, excluir={id_gemeo})
    oponente = escolha.oponente
    prob = ladder.esperado(eu, oponente)
    oponente_antes = ladder.valor(oponente)
    confronto = None
    tentativa = 0
    while confronto is None:
        confronto = jogar(populacao, id_gemeo, oponente, semente("grind", eu, n, tentativa))
        tentativa += 1
    venceu = confronto.vencedor == id_gemeo
    vencedor_id = eu if venceu else oponente
    ladder.registrar(eu, oponente, vencedor_id, origem="ranqueada")
    mundo = []
    pares = mm.parear_npcs(ladder, random.Random(semente("grind-mundo", eu, n)), mundo_por_partida)
    for a, b in pares:
        c = jogar(populacao, a, b, semente("grind-mundo", eu, n, a, b))
        if c is not None:
            ladder.registrar(a, b, c.vencedor, origem="mundo")
            mundo.append({"a": a, "b": b, "vencedor": c.vencedor, "segundos": c.segundos})
    return {
        "n": n,
        "fase": escolha.fase,
        "oponente": oponente,
        "oponente_rating": round(oponente_antes, 1),
        "oponente_posicao": ladder.posicao(oponente),
        "probabilidade": round(prob, 4),
        "venceu": venceu,
        "vencedor_id": vencedor_id,
        "rating": round(ladder.valor(eu), 1),
        "rd": round(ladder.incerteza(eu), 1),
        "posicao": ladder.posicao(eu),
        "percentil": ladder.percentil(eu),
        "rank": ladder.rank(eu),
        "competitivos": ladder.competitivos(),
        "segundos": confronto.segundos,
        "mundo": mundo,
    }


def analisar_carreira(linhas: list[dict]) -> dict:
    """As medidas de uma carreira: marcos de horas, dificuldade, repetição, estabilidade."""
    n = len(linhas)
    marcos = {}
    for horas in HORAS:
        k = int(horas * 60 / MINUTOS_POR_PARTIDA)
        if k <= n:
            r = linhas[k - 1]
            marcos[f"{horas}h"] = {
                "partidas": k,
                "rating": r["rating"],
                "rd": r["rd"],
                "percentil": None if r["percentil"] is None else round(r["percentil"], 1),
                "rank": r["rank"],
                "vitorias": sum(x["venceu"] for x in linhas[:k]),
            }
    posicionamento = linhas[min(9, n - 1)]
    oponentes = [x["oponente"] for x in linhas]
    repetidas_em_10 = sum(1 for i, o in enumerate(oponentes) if o in oponentes[max(0, i - 10) : i])
    ranks_depois = [x["rank"] for x in linhas[10:] if x["rank"]]
    mudancas = sum(1 for a, b in zip(ranks_depois, ranks_depois[1:]) if a != b)
    from src.ranked.ranks import RANKS

    nivel = {nome: i for i, nome in enumerate(RANKS)}
    subidas = sum(1 for a, b in zip(ranks_depois, ranks_depois[1:]) if nivel[b] > nivel[a])
    metade = [x["rating"] for x in linhas[n // 2 :]]
    media = sum(metade) / len(metade)
    final = [x["percentil"] for x in linhas[-max(1, n // 4) :] if x["percentil"] is not None]
    faixa = None
    if final and n > 10:
        alvo = sum(final) / len(final)
        for k in range(10, n):
            resto = [x["percentil"] for x in linhas[k:] if x["percentil"] is not None]
            if resto and all(abs(v - alvo) <= 15 for v in resto):
                faixa = k + 1
                break
    return {
        "partidas": n,
        "horas_equivalentes": round(n * MINUTOS_POR_PARTIDA / 60, 1),
        "cpu_s": round(
            sum(x["segundos"] + sum(m["segundos"] for m in x["mundo"]) for x in linhas), 1
        ),
        "vitorias": sum(x["venceu"] for x in linhas),
        "derrotas": sum(not x["venceu"] for x in linhas),
        "posicionamento": {
            "vitorias": sum(x["venceu"] for x in linhas[:10]),
            "rank": posicionamento["rank"],
            "percentil": posicionamento["percentil"],
            "rating": posicionamento["rating"],
            "rd": posicionamento["rd"],
            "fases": [x["fase"] for x in linhas[:10]],
            "probabilidades": [x["probabilidade"] for x in linhas[:10]],
        },
        "marcos": marcos,
        "final": {
            "rating": linhas[-1]["rating"],
            "rd": linhas[-1]["rd"],
            "percentil": linhas[-1]["percentil"],
            "rank": linhas[-1]["rank"],
            "posicao": linhas[-1]["posicao"],
        },
        "probabilidade_media_depois_do_posicionamento": round(
            sum(x["probabilidade"] for x in linhas[10:]) / max(1, n - 10), 3
        ),
        "oponentes_distintos": len(set(oponentes)),
        "repetidos_nas_ultimas_10": repetidas_em_10,
        "mudancas_de_rank": mudancas,
        "subidas_de_rank": subidas,
        "descidas_de_rank": mudancas - subidas,
        "rating_dp_na_segunda_metade": round(
            math.sqrt(sum((v - media) ** 2 for v in metade) / len(metade)), 1
        ),
        "partidas_ate_a_faixa": faixa,
    }


def grind(jogadores: list[str], partidas: int, mundo_por_partida: int = 1, nome: str = "grind"):
    """Vários jogadores artificiais em paralelo, cada um com o próprio mundo."""
    TRABALHO.mkdir(parents=True, exist_ok=True)
    contexto = mp.get_context("spawn")
    arquivos = {j: str(TRABALHO / f"{nome}_{j}.jsonl") for j in jogadores}
    with ProcessPoolExecutor(len(jogadores), mp_context=contexto) as pool:
        futuros = [
            pool.submit(_grind_um, j, partidas, mundo_por_partida, arquivos[j]) for j in jogadores
        ]
        for f in futuros:
            f.result()
    return arquivos


def resumir_grind(nomes: list[str]) -> dict:
    """Copia as carreiras para `reports/ranked/grind/` e escreve o resumo."""
    from src.ranked import sistema as sis
    from src.ranked.ladder import Ladder

    pasta = PASTA / "grind"
    pasta.mkdir(parents=True, exist_ok=True)
    populacao = Populacao()
    calibrada = Ladder.de_dict(
        sis.criar(),
        json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))["ladder"],
    )
    resumo = {}
    for arquivo in sorted(p for nome in nomes for p in TRABALHO.glob(f"{nome}_*.jsonl")):
        linhas = [json.loads(x) for x in arquivo.read_text(encoding="utf-8").splitlines()]
        if not linhas:
            continue
        (pasta / arquivo.name).write_text(arquivo.read_text(encoding="utf-8"), encoding="utf-8")
        gemeo = arquivo.stem.split("_", 1)[1]
        o = populacao.get(gemeo)
        resumo[arquivo.stem] = {
            "gladiador": {"id": o.id, "classe": o.classe, "nivel": o.nivel, "op": o.op},
            "gemeo_calibrado": {
                "rating": round(calibrada.valor(gemeo), 1),
                "rd": round(calibrada.incerteza(gemeo), 1),
                "percentil": round(calibrada.percentil(gemeo), 1),
                "rank": calibrada.rank(gemeo),
            },
            **analisar_carreira(linhas),
        }
    (pasta / "resumo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    md = [
        "## 5. Jogadores artificiais",
        "",
        f"Hipótese de tempo humano: {_n(MINUTOS_POR_PARTIDA, 0)} minutos por partida ranqueada "
        "(o CPU real está na coluna própria). Cada jogador pega um gladiador legítimo da "
        "população (o gêmeo NPC fica fora do matchmaking), começa do centro sem priori e joga "
        "com a IA estratégica; entre as partidas dele, o mundo joga NPC × NPC.",
        "",
        "| carreira | gladiador | partidas (h) | V-D | posicionamento | 2h | 5h | 10h | 20h "
        "| final | CPU |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for nome, r in resumo.items():
        g = r["gladiador"]
        pos = r["posicionamento"]

        def marco(h, r=r):
            m = r["marcos"].get(f"{h}h")
            return f"{m['rank']} ({_n(m['percentil'], 0)})" if m else "—"

        md.append(
            f"| {nome} | {g['id']} {g['classe']} nv {g['nivel']} OP {_n(g['op'], 1)} | "
            f"{r['partidas']} ({_n(r['horas_equivalentes'], 1)}) | "
            f"{r['vitorias']}-{r['derrotas']} | "
            f"{pos['vitorias']}V → {pos['rank']} ({_n(pos['percentil'], 0)}) | "
            + " | ".join(marco(h) for h in HORAS)
            + f" | {r['final']['rank']} ({_n(r['final']['percentil'], 0)}), "
            f"{_n(r['final']['rating'], 0)} ± {_n(2 * r['final']['rd'], 0)} | "
            f"{_n(r['cpu_s'] / 60, 0)} min |"
        )
    md += [
        "",
        "| carreira | gêmeo NPC calibrado | P(vitória) média depois do posicionamento | "
        "oponentes distintos | repetidos nas últimas 10 | subidas / descidas de rank | "
        "DP do rating na 2ª metade | partidas até a faixa |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for nome, r in resumo.items():
        gemeo = r["gemeo_calibrado"]
        md.append(
            f"| {nome} | {gemeo['rank']} ({_n(gemeo['percentil'], 0)}), "
            f"{_n(gemeo['rating'], 0)} ± {_n(2 * gemeo['rd'], 0)} | "
            f"{_n(r['probabilidade_media_depois_do_posicionamento'])} | "
            f"{r['oponentes_distintos']} | {r['repetidos_nas_ultimas_10']} | "
            f"{r['subidas_de_rank']} / {r['descidas_de_rank']} | "
            f"{_n(r['rating_dp_na_segunda_metade'], 1)} | {r['partidas_ate_a_faixa'] or '—'} |"
        )
    (pasta / "resumo.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return resumo


# --- o estado inicial do jogo (`publicar`) ---------------------------------------------

DESTINO_DO_JOGO = RAIZ / "src" / "data" / "arena_ranked" / "ladder_inicial.json"
HISTORICO_PUBLICADO = 10


def publicar() -> dict:
    """A Ladder calibrada como o mundo inicial de toda instalação."""
    from src.engine.ranked_mundo import VERSAO

    estado = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    ladder = estado["ladder"]
    for registro in ladder["registros"]:
        registro["historico"] = registro["historico"][-HISTORICO_PUBLICADO:]
        registro["rating"] = {k: round(v, 6) for k, v in registro["rating"].items()}
    dados = {
        "versao": VERSAO,
        "aviso": (
            "Gerado por tools/ranked_experimentos.py publicar, a partir da calibração "
            "(reports/ranked/calibracao.json). Não edite à mão."
        ),
        "algoritmo": estado["algoritmo"],
        "parametros": estado["parametros"],
        "semente": SEMENTE,
        "relogio": 0,
        "fila": 0,
        "ultima_sessao": None,
        "reservas": {},
        "ladder": ladder,
    }
    DESTINO_DO_JOGO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO_DO_JOGO.write_text(
        json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return dados


# --- o relatório (`relatorio`) ---------------------------------------------------------


def _n(valor, casas: int = 3) -> str:
    if valor is None:
        return "—"
    return f"{valor:.{casas}f}".replace(".", ",")


def _tabela_de_sistemas(dados: dict, nomes: list[str]) -> list[str]:
    linhas = [
        "| sistema | log-loss holdout | Brier | acerto | ECE | estabilidade (Spearman) |",
        "|---|---|---|---|---|---|",
    ]
    for nome, base in dados["linhas_de_base"].items():
        linhas.append(
            f"| *{nome}* | {_n(base['log_loss'])} | {_n(base['brier'])} | "
            f"{_n(base['acerto'])} | {_n(base['ece'])} | — |"
        )
    for nome in nomes:
        s = dados["sistemas"][nome]
        h = s["holdout"]
        linhas.append(
            f"| {nome} | {_n(h['log_loss'])} ± {_n(s['holdout_dp_log_loss'])} | "
            f"{_n(h['brier'])} | {_n(h['acerto'])} | {_n(h['ece'])} | "
            f"{_n(s['estabilidade_spearman'])} |"
        )
    return linhas


def _tabela_de_sequencias(dados: dict, nomes: list[str]) -> list[str]:
    linhas = [
        "| sistema | 5 vitórias contra iguais | 5 contra muito mais fracos | "
        "6 alternados | 5 derrotas e 5 vitórias |",
        "|---|---|---|---|---|",
    ]
    for nome in nomes:
        q = dados["sistemas"][nome]["sequencias"]
        celulas = [
            f"{_n(q[k]['delta_em_dp'], 2)} dp ({q['posicao_inicial']}º → {q[k]['posicao']}º)"
            for k in (
                "cinco_vitorias_contra_iguais",
                "cinco_vitorias_contra_fracos",
                "alternado_seis",
                "cinco_derrotas_e_cinco_vitorias",
            )
        ]
        linhas.append(f"| {nome} | " + " | ".join(celulas) + " |")
    return linhas


def relatorio() -> str:
    from src.ranked import ranks as rk
    from src.ranked import sistema as sis
    from src.ranked.ladder import Ladder

    populacao = Populacao()
    pequena = json.loads((PASTA / "comparacao.json").read_text(encoding="utf-8"))
    ampliada = json.loads((PASTA / "comparacao_ampliada.json").read_text(encoding="utf-8"))
    calibracao = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    principais = [
        "Glicko-2 τ=0.6 plano",
        "Glicko-2 τ=0.6 OP",
        "TrueSkill β=σ/2 plano",
        "TrueSkill β=σ/2 OP",
    ]
    todos = list(pequena["sistemas"])
    ladder = Ladder.de_dict(sis.criar(), calibracao["ladder"])
    ordem = ladder.classificacao()
    oponente = {o.id: o for o in populacao}
    out = [
        "# Ranked offline — Fase 6",
        "",
        "Gerado por `python tools/ranked_experimentos.py relatorio` a partir dos JSON desta "
        "pasta. Todo confronto é uma partida real do motor PvP (IA estratégica dos dois lados, "
        "gerador semeado).",
        "",
        "## 1. Custo",
        "",
        f"- Um confronto NPC × NPC custa em média {_n(pequena['custo_medio_s'], 2)} s de CPU "
        f"e dura {_n(pequena['rodadas_medias'], 1)} rodadas (amostra de "
        f"{pequena['partidas']['treino'] + pequena['partidas']['holdout']} partidas).",
        "- Com 4 processos, ~1 partida por segundo de relógio.",
        "",
        "## 2. Glicko-2 × TrueSkill na amostra pequena",
        "",
        f"{pequena['partidas']['treino']} partidas de treino e {pequena['partidas']['holdout']} "
        "de holdout, estratificadas (OP próximo e distante, classes, estilos, repetições). "
        f"{PERMUTACOES} ordens diferentes do treino; média do holdout.",
        "",
        *_tabela_de_sistemas(pequena, todos),
        "",
        "- O OP prevê bem quando a diferença é grande: k = "
        f"{_n(pequena['k_op_logit_por_ponto'], 2)} logit por ponto de OP.",
        f"- Nas {pequena['repeticoes']['trios']} duplas repetidas com três seeds, só "
        f"{pequena['repeticoes']['vencedor_unanime']} tiveram o mesmo vencedor nas três: entre "
        "builds parecidas, a sorte pesa muito.",
        "",
        "## 3. Calibração dos 186",
        "",
        f"A amostra e depois {calibracao['rodadas']} rodadas suíças com {sis.ALGORITMO} "
        "(cada NPC contra um vizinho de rating que ele não enfrentou nas últimas 8; a cada 3 "
        "rodadas, a vizinhança dobra).",
        "",
        "| rodada | RD médio | Spearman com a anterior | Top 5 |",
        "|---|---|---|---|",
    ]
    for t in calibracao["trajetoria"]:
        out.append(
            f"| {t['rodada']} | {_n(t['rd_medio'], 1)} | {_n(t['spearman_com_a_anterior'], 4)} | "
            + ", ".join(t["top5"])
            + " |"
        )
    out += [
        "",
        "### A classificação calibrada",
        "",
        "| # | id | nome | classe | nível | OP | rating ± 2RD | V-D | rank |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for posicao, r in enumerate(ordem, start=1):
        if posicao > 20 and posicao < len(ordem) - 9 and posicao % 20:
            continue
        o = oponente[r.identidade]
        titulo = " ★" if posicao <= rk.DEFINITIVE_MASTERS else ""
        out.append(
            f"| {posicao} | {o.id} | {o.apelido} | {o.nome_da_classe} | {o.nivel} | "
            f"{_n(o.op, 1)} | "
            f"{_n(ladder.valor(r.identidade), 0)} ± {_n(2 * ladder.incerteza(r.identidade), 0)} | "
            f"{r.vitorias}-{r.derrotas} | {ladder.rank(r.identidade)}{titulo} |"
        )
    out += [
        "",
        "(Top 20, uma a cada 20 posições e os 10 últimos. ★ = Definitive Master.)",
        "",
        "### Proposta de limites percentuais",
        "",
        "| rank | percentil mínimo | gladiadores com 186 | classes |",
        "|---|---|---|---|",
    ]
    for nome, minimo in zip(rk.RANKS, rk.LIMITES):
        membros = [r for r in ordem if ladder.rank(r.identidade) == nome]
        classes = collections.Counter(oponente[r.identidade].classe[0].upper() for r in membros)
        out.append(
            f"| {nome} | {_n(minimo, 1)} | {len(membros)} | "
            + " ".join(f"{c}{n}" for c, n in sorted(classes.items()))
            + " |"
        )
    out += [
        "",
        "## 4. Comparação ampliada (holdout novo)",
        "",
        f"Treino: as {ampliada['partidas']['treino']} partidas da amostra e da calibração, na "
        f"ordem em que aconteceram (e em {PERMUTACOES - 1} ordens embaralhadas). Holdout: "
        f"{ampliada['partidas']['holdout']} duplas que nunca tinham jogado.",
        "",
        *_tabela_de_sistemas(ampliada, todos),
        "",
        "### Log-loss do holdout por estrato (ordem cronológica)",
        "",
        "| sistema | "
        + " | ".join(sorted(ampliada["sistemas"][principais[0]]["holdout_por_estrato"]))
        + " |",
        "|---|" + "---|" * len(ampliada["sistemas"][principais[0]]["holdout_por_estrato"]),
    ]
    for nome in principais:
        estratos = ampliada["sistemas"][nome]["holdout_por_estrato"]
        out.append(f"| {nome} | " + " | ".join(_n(estratos[k]) for k in sorted(estratos)) + " |")
    out += [
        "",
        "### Convergência (log-loss prequencial por janela de partidas, ordem cronológica)",
        "",
    ]
    for nome in principais:
        s = ampliada["sistemas"][nome]
        out.append(
            f"- {nome} (janelas de {s['janela']}): "
            + " → ".join(_n(v) for v in s["prequencial_por_janela"])
        )
    out += [
        "",
        "### Sensibilidade a sequências (resultados injetados sobre o estado calibrado)",
        "",
        *_tabela_de_sequencias(ampliada, principais),
        "",
        "### Incerteza",
        "",
    ]
    for nome in principais:
        s = ampliada["sistemas"][nome]
        out.append(
            f"- {nome}: Spearman entre incerteza final e menos partidas jogadas = "
            f"{_n(s['incerteza_x_jogos_spearman'], 3)}; ECE do holdout {_n(s['holdout']['ece'])}."
        )
    grind_md = PASTA / "grind" / "resumo.md"
    if grind_md.exists():
        out += ["", grind_md.read_text(encoding="utf-8")]
    texto = "\n".join(out) + "\n"
    (PASTA / "relatorio.md").write_text(texto, encoding="utf-8")
    return texto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    a = sub.add_parser("amostra")
    a.add_argument("--trabalhadores", type=int, default=4)
    comp = sub.add_parser("comparar")
    comp.add_argument("--ampliada", action="store_true")
    g = sub.add_parser("grind")
    g.add_argument("--jogadores", required=True, help="ids da população, separados por vírgula")
    g.add_argument("--partidas", type=int, default=20)
    g.add_argument("--mundo", type=int, default=1)
    g.add_argument("--nome", default="grind")
    sub.add_parser("publicar")
    sub.add_parser("relatorio")
    r = sub.add_parser("resumir-grind")
    r.add_argument("--nomes", default="curto,longo")
    h = sub.add_parser("holdout2")
    h.add_argument("--trabalhadores", type=int, default=4)
    c = sub.add_parser("calibrar")
    c.add_argument("--trabalhadores", type=int, default=4)
    c.add_argument("--rodadas", type=int, default=RODADAS)
    args = parser.parse_args()
    if args.comando == "amostra":
        resultados = amostra(args.trabalhadores)
        print(f"{len(resultados)} partidas")
    elif args.comando == "calibrar":
        calibrar(args.trabalhadores, args.rodadas)
    elif args.comando == "grind":
        grind(args.jogadores.split(","), args.partidas, args.mundo, args.nome)
    elif args.comando == "resumir-grind":
        resumir_grind(args.nomes.split(","))
    elif args.comando == "relatorio":
        relatorio()
        print(f"{PASTA / 'relatorio.md'}")
    elif args.comando == "publicar":
        dados = publicar()
        print(
            f"{len(dados['ladder']['registros'])} registros em {DESTINO_DO_JOGO.relative_to(RAIZ)}"
        )
    elif args.comando == "holdout2":
        print(f"{len(holdout2(args.trabalhadores))} partidas")
    elif args.comando == "comparar":
        dados = comparar_ampliada() if args.ampliada else comparar()
        print(json.dumps(dados, ensure_ascii=False, indent=1, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
