"""Baseline de progressão real (Run/Progression Balance): o coletor.

Reproduz o protocolo que gerou `baseline.jsonl` neste diretório:

    BotPadrao atual, perfil conservador
    criação real de nova jornada (`create_player_for_new_run`, dentro do bot),
    com o Starter Kit sorteado pelo gerador da run
    seeds 1-100 para warrior, mage e rogue
    teto técnico de 200 andares

Sem expected loadout, sem injeção de equipamento, sem tocar regra do jogo: o
coletor só instancia o bot, deixa a run acabar e lê o estado final.

Cada run roda num processo próprio (`spawn`, um processo por tarefa). Estado de
módulo de uma run não vaza para a seguinte, e o resultado depende só de
`(classe, seed)`.

O teto não entra em decisão nenhuma: `max_andar` é só o limite do laço de andares
de `BotPadrao.jogar`. Cortar estes dados no andar 20 dá o mesmo que rodar com
`--max-floor 20`.

Uso, a partir da raiz do repositório:

    # coletar de novo (nunca sobre o arquivo versionado)
    python baselines/progression/fb321d4e/run_baseline.py --saida /caminho/nova.jsonl

    # conferir: reexecuta runs do arquivo e compara registro a registro
    python baselines/progression/fb321d4e/run_baseline.py \
        --conferir baselines/progression/fb321d4e/baseline.jsonl --runs extracoes

`segundos` é tempo de parede: fica no registro e fica fora da comparação.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
# Em nível de módulo: o `spawn` reimporta este arquivo em cada processo filho.
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CLASSES = ("warrior", "mage", "rogue")
SEEDS = range(1, 101)
TETO = 200
PERFIL = "conservador"
# Campo que não é resultado da run, e por isso não entra na conferência.
FORA_DA_COMPARACAO = {"segundos"}


def _instalar_sondas(bot, sonda: dict) -> None:
    """Sondas PASSIVAS da conferência: leem a chave, não mudam nada.

    Uma em `extraction.finish_run`, que o bot chama pelo módulo no momento de
    extrair; outra no fim de cada andar. Nenhuma consulta RNG nem altera estado.
    """
    from src.content import extraction

    original = extraction.finish_run

    def finish_run(player, dungeon_level, gravar):
        sonda["chaves_na_extracao"] = extraction.keys_of(player)
        return original(player, dungeon_level, gravar)

    extraction.finish_run = finish_run

    andar_original = bot._jogar_andar

    def jogar_andar(andar):
        desfecho = andar_original(andar)
        sonda["max_chaves_visto"] = max(sonda["max_chaves_visto"], extraction.keys_of(bot.hero))
        return desfecho

    bot._jogar_andar = jogar_andar


def uma_run(tarefa: tuple[str, int, int, bool]) -> tuple[dict, dict | None]:
    classe, seed, teto, sondar = tarefa
    from tools.bot_padrao import PERFIS, BotPadrao

    t0 = time.time()
    bot = BotPadrao(classe, seed, teto, PERFIS[PERFIL])
    starter = [
        dict(posicao=p, id=i.id, nome=i.name, categoria=i.slot, origin=i.origin)
        for p, i in bot.hero.equipment.items()
        if i
    ]
    sonda = {"chaves_na_extracao": None, "max_chaves_visto": 0} if sondar else None
    if sondar:
        _instalar_sondas(bot, sonda)
    with contextlib.redirect_stdout(io.StringIO()):
        bot.jogar()
    hero = bot.hero
    if sondar:
        from src.content import extraction

        sonda["max_chaves_visto"] = max(sonda["max_chaves_visto"], extraction.keys_of(hero))
    fim = bot.fim
    if fim.startswith("MORREU"):
        desfecho = "morreu"
    elif fim.startswith("EXTRAIU"):
        desfecho = "extraiu"
    else:
        desfecho = "teto"
    led = hero.ledger
    registro = dict(
        classe=classe,
        seed=seed,
        teto=teto,
        starter=starter,
        desfecho=desfecho,
        fim=fim,
        andar=bot.andar,
        andares_concluidos=bot.andares_concluidos,
        nivel=hero.get_level(),
        nivel_por_andar=[r["nivel"] for r in bot.por_andar],
        combates=bot.combates_na_run,
        fugas=bot.fugas_na_run,
        pocoes=bot.pocoes_bebidas,
        passivas=len(hero.passives),
        skills=len(hero.skills),
        equipado=sum(1 for i in hero.equipment.values() if i),
        starter_ainda_equipado=any(
            i is not None and getattr(i, "origin", None) == "starter"
            for i in hero.equipment.values()
        ),
        ouro_ganho=led.get("gold_earned", 0),
        saidas_pagas=led.get("paid_exits", 0),
        saidas_nao_pagas=led.get("unpaid_exits", 0),
        fatal=bot.fatal,
        segundos=round(time.time() - t0, 2),
    )
    return registro, sonda


def _pool(workers: int):
    return mp.get_context("spawn").Pool(workers, maxtasksperchild=1)


def coletar(saida: Path, workers: int) -> None:
    tarefas = [(c, s, TETO, False) for c in CLASSES for s in SEEDS]
    with _pool(workers) as pool, saida.open("w", encoding="utf-8") as f:
        # `imap` mantém a ordem das tarefas no arquivo; cada linha é gravada
        # assim que chega, e o que já foi medido sobrevive a uma interrupção.
        for registro, _ in pool.imap(uma_run, tarefas):
            f.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")
            f.flush()


def _selecionar(guardados: dict, runs: str) -> list[tuple[str, int]]:
    if runs == "todas":
        return sorted(guardados)
    if runs == "extracoes":
        return sorted(k for k, r in guardados.items() if r["desfecho"] == "extraiu")
    escolhidas = []
    for item in runs.split(","):
        classe, seed = item.split(":")
        escolhidas.append((classe, int(seed)))
    return escolhidas


def conferir(arquivo: Path, runs: str, workers: int) -> int:
    guardados = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        guardados[(r["classe"], r["seed"])] = r
    alvo = _selecionar(guardados, runs)
    tarefas = [(c, s, guardados[(c, s)]["teto"], True) for c, s in alvo]
    falhas = 0
    with _pool(workers) as pool:
        for registro, sonda in pool.imap(uma_run, tarefas):
            chave = (registro["classe"], registro["seed"])
            # Ida e volta por JSON: o guardado passou por `json.dumps(default=str)`.
            novo = json.loads(json.dumps(registro, ensure_ascii=False, default=str))
            antigo = guardados[chave]
            diverge = sorted(
                c
                for c in set(novo) | set(antigo)
                if c not in FORA_DA_COMPARACAO and novo.get(c) != antigo.get(c)
            )
            extra = ""
            if novo["desfecho"] == "extraiu":
                ok_chave = (sonda["chaves_na_extracao"] or 0) >= 1
                extra = f"chave na extração: {sonda['chaves_na_extracao']}"
                if not ok_chave:
                    falhas += 1
                    extra += "  <- EXTRAIU SEM CHAVE"
            else:
                extra = f"maior número de chaves visto: {sonda['max_chaves_visto']}"
            if diverge:
                falhas += 1
            estado = "idêntico" if not diverge else f"DIVERGE em {diverge}"
            print(f"{chave[0]:7s} seed {chave[1]:3d}  {novo['fim']:22s}  {estado}  | {extra}")
    print(f"\n{len(tarefas)} run(s) conferida(s), {falhas} falha(s).")
    return 1 if falhas else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--saida", type=Path, help="JSONL novo para uma coleta completa")
    modo.add_argument("--conferir", type=Path, help="JSONL a reexecutar e comparar")
    parser.add_argument(
        "--runs",
        default="extracoes",
        help="na conferência: 'extracoes', 'todas' ou 'classe:seed,classe:seed'",
    )
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    args = parser.parse_args()
    if args.saida is not None:
        if args.saida.resolve() == (Path(__file__).parent / "baseline.jsonl").resolve():
            parser.error("a coleta não sobrescreve a amostra versionada")
        coletar(args.saida, args.workers)
        return 0
    return conferir(args.conferir, args.runs, args.workers)


if __name__ == "__main__":
    sys.exit(main())
