"""Quanto o RNG compartilhado custa ao pareamento entre versões. Só mede.

O jogo sorteia por duas fontes: o gerador da run (`BotPadrao.rng`: combate e
decisões) e o `random` global (mapa, vitrine da Loja, loot, gema, chave,
encanto, nomes de monstro). Uma mudança de código que consome UM sorteio a mais
em qualquer uma delas desloca tudo o que vem depois na mesma fonte. Este
experimento mede quanto: o protocolo histórico de progressão
(`baselines/progression/d3105edc/run_auditoria.py`), em três braços que só
diferem num sorteio a mais no início do andar `--andar`:

    controle          nada muda (e tem de reproduzir a baseline publicada);
    global            um `random.random()` a mais no gerador global, ANTES de
                      gerar o mapa do andar;
    global_pos_mapa   o mesmo sorteio, logo DEPOIS de gerar o mapa: é onde cai
                      uma mudança típica de versão (um sorteio a mais no loot, na
                      Loja, num evento);
    run               um `self.rng.random()` a mais no gerador da run.

Os dois braços globais existem porque o gerador do mapa é uma caminhada
aleatória com rejeição na borda: dois trajetos deslocados tendem a se acoplar
ao bater nas mesmas paredes, e o mapa pode sair idêntico — com o gerador global
no mesmo estado — apesar do sorteio a mais. Perturbar antes do mapa mede essa
absorção; perturbar depois mede o caso comum.

Cada braço registra, andar a andar, a assinatura do mapa recém-gerado e o
estado do herói ao fim do andar. Nada em `src/` ou em `tools/bot_padrao.py`
muda: as sondas embrulham funções, chamam a original e só leem estado; a
perturbação é o único sorteio a mais, e só nos braços que a pedem.

Uso, a partir da raiz do repositório:

    python tools/rng_pareamento.py rodar --braco controle --saida controle.jsonl
    python tools/rng_pareamento.py rodar --braco global --saida global.jsonl
    python tools/rng_pareamento.py rodar --braco run --saida run.jsonl
    python tools/rng_pareamento.py analisar controle.jsonl global.jsonl run.jsonl \\
        --baseline baselines/progression/d3105edc/depois.jsonl
"""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import os
import pathlib
import statistics as st
import sys

RAIZ = str(pathlib.Path(__file__).resolve().parents[1])
COLETOR = pathlib.Path(RAIZ) / "baselines" / "progression" / "d3105edc" / "run_auditoria.py"
BRACOS = ("controle", "global", "global_pos_mapa", "run")
CAMPOS_VOLATEIS = ("segundos", "rng")


def _coletor():
    import importlib.util

    spec = importlib.util.spec_from_file_location("coletor_d3105edc", COLETOR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _assinatura_do_mapa(mapa) -> str:
    """O mapa como saiu do gerador: paredes, saída, monstros, evento e casas
    especiais. Os nomes dos monstros ficam de fora — o tipo e o nível bastam."""
    inimigos = sorted(
        (y, x, type(m).__name__, getattr(m, "level", None), getattr(m, "role", None))
        for (y, x), m in mapa.enemies_pos.items()
    )
    partes = (
        "".join("".join(linha) for linha in mapa.grid),
        repr(sorted(mapa.exit_pos.items())),
        repr(sorted(mapa.player_pos.items())),
        repr(inimigos),
        repr((mapa.event_pos, mapa.event_type)),
        repr(sorted(mapa.features.items())),
    )
    return hashlib.sha256("|".join(partes).encode()).hexdigest()[:16]


def _instalar(braco: str, andar_perturbado: int, por_andar: list) -> None:
    import random

    import tools.bot_padrao as bp

    gerar = bp._setup_dungeon_map

    def gerar_espiao(*args, **kwargs):
        mapa = gerar(*args, **kwargs)
        por_andar.append({"andar": args[0], "mapa": _assinatura_do_mapa(mapa)})
        if braco == "global_pos_mapa" and args[0] == andar_perturbado:
            random.random()
        return mapa

    bp._setup_dungeon_map = gerar_espiao
    jogar_andar = bp.BotPadrao._jogar_andar

    def jogar_andar_espiao(self, andar):
        if andar == andar_perturbado:
            if braco == "global":
                random.random()
            elif braco == "run":
                self.rng.random()
        desfecho = jogar_andar(self, andar)
        h = self.hero
        por_andar[-1]["estado"] = [
            h.get_level(),
            h.get_hp(),
            h.get_mp(),
            h.coins,
            len(h.inventory),
            self.combates,
            desfecho,
        ]
        return desfecho

    bp.BotPadrao._jogar_andar = jogar_andar_espiao


def uma_run(tarefa) -> dict:
    raiz, classe, seed, teto, braco, andar_perturbado = tarefa
    sys.path.insert(0, raiz)
    por_andar: list = []
    _instalar(braco, andar_perturbado, por_andar)
    registro = _coletor().uma_run((raiz, classe, seed, teto))
    registro["rng"] = {"braco": braco, "andar_perturbado": andar_perturbado, "por_andar": por_andar}
    return registro


def rodar(saida, braco, workers, classes, seeds, teto, andar_perturbado) -> None:
    coletor = _coletor()
    tarefas = [
        (RAIZ, c, s, teto or coletor.TETO, braco, andar_perturbado)
        for c in (classes or coletor.CLASSES)
        for s in seeds
    ]
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        with saida.open("w", encoding="utf-8") as f:
            for i, r in enumerate(pool.imap(uma_run, tarefas), 1):
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
                f.flush()
                print(f"[{braco} {i}/{len(tarefas)}] {r['classe']} seed {r['seed']}", flush=True)


# --------------------------------------------------------------------------- #
# Análise                                                                     #
# --------------------------------------------------------------------------- #


def _ler(caminho) -> dict:
    linhas = pathlib.Path(caminho).read_text(encoding="utf-8").splitlines()
    return {(r["classe"], r["seed"]): r for r in (json.loads(x) for x in linhas if x.strip())}


def _primeira_divergencia(a: list, b: list, campo: str):
    """Primeiro andar em que o campo difere. `None`: idênticos até onde os dois
    foram. Se um acabou antes do outro sem diferir, a divergência é o fim."""
    for x, y in zip(a, b):
        if x.get(campo) != y.get(campo):
            return x["andar"]
    if len(a) != len(b):
        return min(len(a), len(b)) + 1
    return None


def _pearson(xs, ys) -> float:
    if len(xs) < 3 or st.pstdev(xs) == 0 or st.pstdev(ys) == 0:
        return float("nan")
    mx, my = st.fmean(xs), st.fmean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
    return cov / (st.pstdev(xs) * st.pstdev(ys))


# Poder 80%, alfa 5% bicaudal.
Z = 1.959964 + 0.841621


def _n_nao_pareado(sigma: float, delta: float) -> int:
    return math.ceil(2 * (Z * sigma / delta) ** 2)


def _n_pareado(sigma: float, rho: float, delta: float) -> int:
    var_dif = 2 * sigma**2 * (1 - rho)
    return math.ceil(Z**2 * var_dif / delta**2)


def _n_proporcao(p: float, delta: float) -> int:
    p2 = min(0.999, p + delta)
    pm = (p + p2) / 2
    return math.ceil(Z**2 * 2 * pm * (1 - pm) / delta**2)


def analisar(controle, perturbados, baseline) -> int:
    ctl = _ler(controle)
    linhas = []
    falhou = 0
    if baseline:
        ref = _ler(baseline)
        diverge = [
            k
            for k in ctl
            if {c: v for c, v in ctl[k].items() if c not in CAMPOS_VOLATEIS}
            != {c: v for c, v in ref[k].items() if c not in CAMPOS_VOLATEIS}
        ]
        linhas.append(
            f"controle × baseline publicada: {len(ctl) - len(diverge)}/{len(ctl)} idênticas"
        )
        falhou |= bool(diverge)
    for caminho in perturbados:
        pert = _ler(caminho)
        chaves = sorted(set(ctl) & set(pert))
        braco = next(iter(pert.values()))["rng"]["braco"]
        k_and = next(iter(pert.values()))["rng"]["andar_perturbado"]
        div_mapa, div_estado, iguais, d_andar = [], [], 0, []
        ctl_and, pert_and = [], []
        for k in chaves:
            a, b = ctl[k]["rng"]["por_andar"], pert[k]["rng"]["por_andar"]
            div_mapa.append(_primeira_divergencia(a, b, "mapa"))
            div_estado.append(_primeira_divergencia(a, b, "estado"))
            fim_a = (ctl[k]["desfecho"], ctl[k]["andar"])
            fim_b = (pert[k]["desfecho"], pert[k]["andar"])
            iguais += fim_a == fim_b
            d_andar.append(pert[k]["andar"] - ctl[k]["andar"])
            ctl_and.append(ctl[k]["andar"])
            pert_and.append(pert[k]["andar"])
        alcancaram = [k for k in chaves if ctl[k]["andar"] >= k_and]
        n_alc = len(alcancaram)
        mapa_no_k = sum(
            1 for k, d in zip(chaves, div_mapa) if k in alcancaram and d is not None and d <= k_and
        )
        mapa_depois = sum(1 for k, d in zip(chaves, div_mapa) if k in alcancaram and d is not None)
        estado_div = [d for k, d in zip(chaves, div_estado) if k in alcancaram and d is not None]
        rho = _pearson(ctl_and, pert_and)
        linhas += [
            "",
            f"braço {braco} (um sorteio a mais no andar {k_and}), {len(chaves)} pares",
            f"  runs que chegaram ao andar {k_and}: {n_alc}",
            f"  mapa diferente já no andar {k_and}: {mapa_no_k}/{n_alc}",
            f"  mapa diferente em algum andar: {mapa_depois}/{n_alc}",
            f"  estado diferente em algum andar: {len(estado_div)}/{n_alc}"
            + (f" (mediana do 1º andar: {st.median(estado_div)})" if estado_div else ""),
            f"  desfecho final igual (desfecho, andar): {iguais}/{len(chaves)}",
            f"  Δandar final: média {st.fmean(d_andar):+.2f}, |Δ| médio "
            f"{st.fmean(abs(x) for x in d_andar):.2f}, desvio {st.pstdev(d_andar):.2f}",
            f"  correlação do andar final, controle × {braco}: ρ = {rho:.2f}",
        ]
    # Quanto custa medir uma diferença entre versões, com a variância da baseline.
    if baseline:
        ref = list(_ler(baseline).values())
        linhas += ["", "tamanho de amostra por braço (poder 80%, α 5%), variância da baseline:"]
        for classe in sorted({r["classe"] for r in ref}):
            rs = [r for r in ref if r["classe"] == classe]
            sigma = st.pstdev(r["andar"] for r in rs)
            p_ext = sum(r["desfecho"] == "extraiu" for r in rs) / len(rs)
            linhas.append(
                f"  {classe}: σ(andar) = {sigma:.2f}; Δ1 andar: não pareado "
                f"{_n_nao_pareado(sigma, 1)}, pareado ideal (ρ=0,9) "
                f"{_n_pareado(sigma, 0.9, 1)}; extração {p_ext:.0%}, Δ10 p.p.: "
                f"{_n_proporcao(p_ext, 0.10)}"
            )
    print("\n".join(linhas))
    return 1 if falhou else 0


def _intervalo(texto: str) -> range:
    ini, _, fim = texto.partition("-")
    return range(int(ini), int(fim or ini) + 1)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("rodar")
    p.add_argument("--braco", choices=BRACOS, required=True)
    p.add_argument("--saida", type=pathlib.Path, required=True)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    p.add_argument("--classes", nargs="*")
    p.add_argument("--seeds", default="1-20")
    p.add_argument("--teto", type=int, default=0)
    p.add_argument("--andar", type=int, default=2)
    p = sub.add_parser("analisar")
    p.add_argument("controle", type=pathlib.Path)
    p.add_argument("perturbados", type=pathlib.Path, nargs="+")
    p.add_argument("--baseline", type=pathlib.Path)
    args = parser.parse_args()
    if args.comando == "rodar":
        rodar(
            args.saida,
            args.braco,
            args.workers,
            args.classes,
            _intervalo(args.seeds),
            args.teto,
            args.andar,
        )
        return 0
    return analisar(args.controle, args.perturbados, args.baseline)


if __name__ == "__main__":
    sys.exit(main())
