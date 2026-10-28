"""Teste: gladiadores extraídos de runs reais com OP entre 40 e 70 (no máximo 10).

Uso:
    python tools/arena_teste_op_alto.py

Saída em `reports/pvp/teste_op_alto/`: `tentativas.jsonl` (uma linha por run) e
`gladiadores/` (os snapshots aceitos). NÃO entra no catálogo da Arena.

Mesmo caminho da população da Arena (`tools/arena_copa_03_geracao.executar`): o
BotExperimental joga a run desde a criação canônica até a Extração, e o
snapshot sai da serialização canônica do save. A ÚNICA diferença é o alvo da
decisão de extrair: o bot compara a build com o benchmark da Arena (OP 29,17) e
sai perto dele. Aqui, dentro de cada processo de teste, a comparação usa um
alvo maior (`ALVOS`), e o bot segue descendo até chegar perto dele. Nada em
`src/` muda; o catálogo da Arena não é tocado.
"""

from __future__ import annotations

import itertools
import json
import multiprocessing as mp
import os
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
AQUI = RAIZ / "reports" / "pvp" / "teste_op_alto"

FAIXA = (40.0, 70.0)
MAXIMO = 10
POR_CLASSE = 4
ALVOS = (45.0, 55.0, 65.0)
CLASSES = ("warrior", "mage", "rogue")
PERFIS = ("conservador", "moderado")
POLITICAS = ("survival", "offense", "economy")
BASE = 900_000
LIMITE_DE_TENTATIVAS = 600
TRABALHADORES = 4


def tentar(tarefa: tuple) -> dict:
    import tools.arena_copa_03_geracao as ger
    import tools.bot_adapter as adapter
    from src.sim.arena import Comparacao, classificar, overall_power

    classe, perfil, politica, alvo, k = tarefa

    def comparar(heroi, **kwargs):
        relativo = overall_power(heroi, **kwargs).nivel_equivalente / alvo
        return Comparacao(relativo, classificar(relativo))

    adapter.comparar_com_benchmark = comparar
    inicio = time.time()
    registro = ger.executar(perfil, politica, BASE + k, classe=classe, faixa=FAIXA)
    registro.update(classe=classe, alvo=alvo, k=k, relogio_s=round(time.time() - inicio, 1))
    return registro


def tarefas():
    combinacoes = list(itertools.product(ALVOS, PERFIS, POLITICAS, CLASSES))
    for k in itertools.count():
        alvo, perfil, politica, classe = combinacoes[k % len(combinacoes)]
        yield (classe, perfil, politica, alvo, k)


def main() -> int:
    log = AQUI / "tentativas.jsonl"
    pasta = AQUI / "gladiadores"
    pasta.mkdir(exist_ok=True)
    feitas = {}
    if log.exists():
        for linha in log.read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            feitas[r["k"]] = r
    aceitos = [r for r in feitas.values() if r.get("qualificada")]
    por_classe = {c: sum(1 for r in aceitos if r["classe"] == c) for c in CLASSES}
    fila = (t for t in tarefas() if t[4] not in feitas)
    with (
        ProcessPoolExecutor(TRABALHADORES, mp_context=mp.get_context("spawn")) as pool,
        open(log, "a", encoding="utf-8") as saida,
    ):
        voando = {}

        def despachar():
            while len(voando) < TRABALHADORES and len(feitas) + len(voando) < LIMITE_DE_TENTATIVAS:
                tarefa = next(fila)
                if por_classe[tarefa[0]] >= POR_CLASSE:
                    continue
                voando[pool.submit(tentar, tarefa)] = tarefa

        despachar()
        while voando and len(aceitos) < MAXIMO:
            prontos, _ = wait(voando, return_when=FIRST_COMPLETED)
            for futuro in prontos:
                tarefa = voando.pop(futuro)
                try:
                    r = futuro.result()
                except Exception as erro:  # noqa: BLE001
                    r = {
                        "classe": tarefa[0],
                        "k": tarefa[4],
                        "desfecho": "erro",
                        "motivo": repr(erro),
                    }
                snapshot = r.pop("_snapshot", None)
                aceito = (
                    bool(snapshot)
                    and len(aceitos) < MAXIMO
                    and por_classe[r["classe"]] < POR_CLASSE
                )
                r["aceito"] = aceito
                if aceito:
                    nome = f"{r['classe'][0].upper()}{len(aceitos) + 1:02d}_op{r['op']:.1f}.json"
                    (pasta / nome).write_text(
                        json.dumps(snapshot, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    r["arquivo"] = nome
                    aceitos.append(r)
                    por_classe[r["classe"]] += 1
                saida.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
                saida.flush()
                os.fsync(saida.fileno())
                feitas[r["k"]] = r
                print(
                    f"k={r['k']} {r['classe']} {r.get('perfil')}/{r.get('politica')} "
                    f"alvo {r.get('alvo')}: "
                    f"{r.get('desfecho')} andar {r.get('andar')} nível {r.get('nivel')} "
                    f"OP {r.get('op')} {'ACEITO' if aceito else ''} ({r.get('relogio_s')} s) "
                    f"— aceitos {len(aceitos)}/{MAXIMO}",
                    flush=True,
                )
            if len(aceitos) < MAXIMO:
                despachar()
        for futuro in voando:
            futuro.cancel()
    print(f"FIM: {len(aceitos)} aceitos em {len(feitas)} tentativas", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
