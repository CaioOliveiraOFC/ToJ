"""Monta amostras reproduzíveis a partir dos logs reais de geração."""
import json
import pathlib, random, sys
FONTES = [
    ("warrior", "reports/pvp/copa_03/_trabalho/tentativas.jsonl"),
    ("warrior", "reports/pvp/copa_03/_trabalho/preenchimento.jsonl"),
    ("mage", "reports/pvp/arena_offline/_trabalho/mage/tentativas.jsonl"),
    ("rogue", "reports/pvp/arena_offline/_trabalho/rogue/tentativas.jsonl"),
]
def ler():
    vistos = set()
    for classe, f in FONTES:
        for l in open(str(pathlib.Path(__file__).resolve().parents[3]) + "/" + f):
            if not l.strip(): continue
            r = json.loads(l)
            k = (classe, r["perfil"], r["politica"], r["tentativa"])
            if k in vistos: continue
            vistos.add(k)
            yield classe, f, r
def tarefa(classe, f, r, estrato):
    return {"classe": classe, "perfil": r["perfil"], "politica": r["politica"],
            "tentativa": r["tentativa"], "fonte": f, "estrato": estrato, "log": r}
todas = list(ler())
modo = sys.argv[1]
if modo == "piloto":
    out = []
    for cl in ("warrior", "mage", "rogue"):
        mortes = [x for x in todas if x[0] == cl and x[2]["desfecho"] == "morreu" and x[2]["andar"] >= 4]
        ext = sorted([x for x in todas if x[0] == cl and x[2]["desfecho"] == "extraiu"], key=lambda x: x[2].get("tempo_s", 0))
        out.append(tarefa(*mortes[0], "piloto_morte"))
        out.append(tarefa(*ext[len(ext)//2], "piloto_extracao"))
elif modo == "principal":
    rng = random.Random(20261028)
    out, chaves = [], set()
    cotas_completas = {"warrior": 40, "mage": 30, "rogue": 30}
    cotas_extraidas = {"warrior": 20, "mage": 20, "rogue": 20}
    for cl in ("warrior", "mage", "rogue"):
        pool = [x for x in todas if x[0] == cl]
        for x in rng.sample(pool, cotas_completas[cl]):
            out.append(tarefa(*x, "run_completa")); chaves.add((cl, x[2]["perfil"], x[2]["politica"], x[2]["tentativa"]))
        ext = [x for x in pool if x[2]["desfecho"] == "extraiu"]
        for x in rng.sample(ext, cotas_extraidas[cl]):
            k = (cl, x[2]["perfil"], x[2]["politica"], x[2]["tentativa"])
            if k in chaves:
                for t in out:
                    if (t["classe"], t["perfil"], t["politica"], t["tentativa"]) == k:
                        t["estrato"] = "run_completa+extraida"
                continue
            out.append(tarefa(*x, "extraida")); chaves.add(k)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False)
print(len(out), "tarefas")
import collections
print(collections.Counter((t["classe"], t["estrato"], t["log"]["desfecho"]) for t in out))
