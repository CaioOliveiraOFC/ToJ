"""Tabela de status por efeito, pelos dois caminhos de aplicação, e a conferência das duas passadas.

Uso:
    python status.py <resultados.jsonl> [<primeira_passada.jsonl>] > status.md

`*_applied` cobre stun, secundário de carta e proc de passiva. O status PRINCIPAL
de uma carta de status só aparece no resultado da skill (`status_principal:`).
"""

import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from src.shared import effect_core as core  # noqa: E402

runs = [json.loads(linha) for linha in open(sys.argv[1]) if linha.strip()]
COMPLETAS = [r for r in runs if "run_completa" in r["tarefa"]["estrato"]]
EXTRAIDAS = [r for r in runs if r["registro"]["desfecho"] == "extraiu"]

if len(sys.argv) > 2:
    antes = {}
    for linha in open(sys.argv[2]):
        if linha.strip():
            r = json.loads(linha)
            t = r["tarefa"]
            antes[(t["classe"], t["perfil"], t["politica"], t["tentativa"])] = r
    iguais = 0
    for r in runs:
        t = r["tarefa"]
        a = antes.get((t["classe"], t["perfil"], t["politica"], t["tentativa"]))
        novo = {k: v for k, v in r["n"].items() if not k.startswith("status_principal:")}
        iguais += a is not None and a["n"] == novo and a["final"] == r["final"]
    print(f"<!-- conferência: {iguais}/{len(runs)} runs com todos os contadores e a ficha final "
          f"idênticos à primeira passada (fora a sonda nova) -->\n")


def tabela(uni, rotulo):
    print(f"### {rotulo} (n = {len(uni)})\n")
    print("| efeito | no herói: por `*_applied` | no herói: principal de carta (pegou/tentou) | "
          "runs | no monstro: por `*_applied` | no monstro: principal de carta (pegou/tentou) | runs |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for e in sorted(core.CATALOG):
        linha = [e]
        for alvo in ("heroi", "monstro"):
            ap = sum(r["n"].get(f"status_aplicado:{e}:em_{alvo}", 0) for r in uni)
            ok = sum(r["n"].get(f"status_principal:{e}:sucesso:em_{alvo}", 0) for r in uni)
            falhou = sum(r["n"].get(f"status_principal:{e}:falhou:em_{alvo}", 0) for r in uni)
            nr = sum(
                1 for r in uni
                if r["n"].get(f"status_aplicado:{e}:em_{alvo}", 0)
                or r["n"].get(f"status_principal:{e}:sucesso:em_{alvo}", 0)
            )
            linha += [str(ap), f"{ok}/{ok + falhou}", str(nr)]
        print("| " + " | ".join(linha) + " |")
    print()


print("# Status por efeito\n")
print("Contagem dos dois caminhos de aplicação, na amostra reproduzível. Efeito "
      "com zero nos dois caminhos e nos dois alvos não foi aplicado por nada na amostra.\n")
tabela(COMPLETAS, "Runs completas")
tabela(EXTRAIDAS, "Builds extraídas")
