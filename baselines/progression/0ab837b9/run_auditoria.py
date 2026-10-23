"""Auditoria do instrumento — o coletor.

Mesmo protocolo da baseline de progressão `fb321d4e` — BotPadrão no perfil
conservador, nova jornada real com Starter Kit, seeds 1-100 para warrior, mage e
rogue, teto técnico de 200 andares, um processo por run — e os MESMOS campos de
registro, mais sondas PASSIVAS para o que a auditoria precisa medir:

    lojas, lojas_inuteis      visitas à Loja, e as que não mudaram nada
                              (nem ouro, nem HP, nem poção na mochila)
    lojas_que_curaram         visitas que compraram recuperação de HP
    pocoes_na_mochila_ao_fim  poções de cura que sobraram na mochila quando a run
                              acabou (numa morte: as que ele levou para o túmulo)
    pocoes_compradas          poções de cura que entraram na mochila na Loja
    max_streak_nao_pagas      maior sequência de saídas não pagas da run
    familias_passivas         o `effect_type` de cada passiva escolhida
    acoes                     quantas vezes cada verbo de combate foi escolhido

As sondas embrulham métodos do driver e só leem estado: nenhuma consulta RNG.
Roda contra qualquer árvore do jogo (`--raiz`), para medir o "antes" e o
"depois" com a mesma régua.

Uso, a partir da raiz do repositório:

    python baselines/progression/<dir>/run_auditoria.py --saida depois.jsonl
    python baselines/progression/<dir>/run_auditoria.py --saida antes.jsonl \\
        --raiz /caminho/para/uma/exportacao/do/fb321d4e
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

CLASSES = ("warrior", "mage", "rogue")
SEEDS = range(1, 101)
TETO = 200
PERFIL = "conservador"


def _pocoes_na_mochila(hero) -> int:
    return sum(
        1
        for i in hero.inventory
        if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
    )


def uma_run(tarefa: tuple[str, str, int, int]) -> dict:
    raiz, classe, seed, teto = tarefa
    # A árvore medida entra ANTES de qualquer import do jogo.
    sys.path.insert(0, raiz)
    import tools.bot_padrao as bp

    lojas = {"lojas": 0, "lojas_inuteis": 0, "lojas_que_curaram": 0, "pocoes_compradas": 0}
    comprar = bp.BotPadrao._comprar_com_orcamento

    def comprar_espiao(self, rotulo):
        hero = self.hero
        antes = (hero.coins, hero.get_hp(), _pocoes_na_mochila(hero))
        comprar(self, rotulo)
        depois = (hero.coins, hero.get_hp(), _pocoes_na_mochila(hero))
        lojas["lojas"] += 1
        lojas["lojas_inuteis"] += antes == depois
        lojas["lojas_que_curaram"] += depois[1] > antes[1]
        lojas["pocoes_compradas"] += max(0, depois[2] - antes[2])

    bp.BotPadrao._comprar_com_orcamento = comprar_espiao

    t0 = time.time()
    bot = bp.BotPadrao(classe, seed, teto, bp.PERFIS[PERFIL])
    starter = [
        dict(posicao=p, id=i.id, nome=i.name, categoria=i.slot, origin=i.origin)
        for p, i in bot.hero.equipment.items()
        if i
    ]
    with contextlib.redirect_stdout(io.StringIO()):
        bot.jogar()
    hero = bot.hero
    fim = bot.fim
    if fim.startswith("MORREU"):
        desfecho = "morreu"
    elif fim.startswith("EXTRAIU"):
        desfecho = "extraiu"
    else:
        desfecho = "teto"
    led = hero.ledger
    return dict(
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
        max_streak_nao_pagas=led.get("max_unpaid_exit_streak", 0),
        familias_passivas=[p.effect_type for p in hero.passives],
        acoes=dict(bot.acoes),
        pocoes_na_mochila_ao_fim=_pocoes_na_mochila(hero),
        **lojas,
        segundos=round(time.time() - t0, 2),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    args = parser.parse_args()
    raiz = str(args.raiz.resolve())
    tarefas = [(raiz, c, s, TETO) for c in CLASSES for s in SEEDS]
    with mp.get_context("spawn").Pool(args.workers, maxtasksperchild=1) as pool:
        with args.saida.open("w", encoding="utf-8") as f:
            for registro in pool.imap(uma_run, tarefas):
                f.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")
                f.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
