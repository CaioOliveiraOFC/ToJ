"""Matriz de cobertura PvE: por sistema, runs com oportunidade, com uso e com efeito.

Lê a saída de `tools/cobertura_pve.py rodar` (o registro do coletor histórico de
progressão mais a chave `cobertura`). Porto do agregador da auditoria de
cobertura PvE (`reports/auditoria_pve/`, branch `phase/pvp-arena`, commit
`5b99109`), sem merge. As regras de cada sistema são as mesmas; só a leitura do
registro mudou, numa camada que o normaliza para o formato da auditoria.

Dois universos, sempre separados:
- COMPLETAS: todas as runs do protocolo (morte e extração juntas);
- EXTRAIDAS: só as runs que extraíram.

Uso:
    python tools/cobertura_pve_matriz.py cobertura.jsonl [matriz.json] > matriz.md
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

ENTRADA = sys.argv[1]
SAIDA_JSON = sys.argv[2] if len(sys.argv) > 2 else None


def _normalizar(bruto: dict) -> dict:
    """O registro do coletor histórico, no formato que as regras da auditoria leem."""
    cob = bruto["cobertura"]
    return {
        "tarefa": {"classe": bruto["classe"], "seed": bruto["seed"], "estrato": "run_completa"},
        "reproduziu": True,
        "divergencias_do_log": {},
        "registro": {
            "desfecho": bruto["desfecho"],
            "andar": bruto["andar"],
            "pocoes_bebidas": bruto["pocoes"],
            # O protocolo histórico não mede o OP final nem registra a decisão de
            # extração andar a andar; as medições DURANTE a run estão nas sondas.
            "op": None,
            "extracao": None,
        },
        "n": cob["n"],
        "listas": cob["listas"],
        "skills_disponiveis": cob["skills_disponiveis"],
        "starter": cob["starter"],
        "final": cob["final"],
    }


runs = [
    _normalizar(json.loads(linha)) for linha in open(ENTRADA, encoding="utf-8") if linha.strip()
]
erros: list = []
COMPLETAS = runs
EXTRAIDAS = [r for r in runs if r["registro"]["desfecho"] == "extraiu"]


def conta(r, chave):
    return r["n"].get(chave, 0)


def soma(r, prefixo):
    return sum(v for k, v in r["n"].items() if k.startswith(prefixo))


def andares(r):
    return r["listas"].get("andares", [])


def final(r):
    return r.get("final") or {}


def equipado(r):
    return list((final(r).get("equipado") or {}).values())


SISTEMAS = []


def sistema(nome, grupo, opp, uso, efeito=None, nota=""):
    SISTEMAS.append((nome, grupo, opp, uso, efeito, nota))


# --- Itens e progressão ------------------------------------------------------
sistema(
    "Loot de equipamento (drop)",
    "itens",
    lambda r: conta(r, "loot.drop_equipamento"),
    lambda r: conta(r, "loot.drop_equipado"),
    lambda r: conta(r, "loot.drop_equipado"),
    "uso = equipou um drop",
)
sistema(
    "Raridade Epic/Legendary no drop",
    "itens",
    lambda r: conta(r, "loot.drop_raridade:Epic") + conta(r, "loot.drop_raridade:Legendary"),
    lambda r: (
        conta(r, "loot.drop_equipado_raridade:Epic")
        + conta(r, "loot.drop_equipado_raridade:Legendary")
    ),
    lambda r: sum(1 for i in equipado(r) if i["raridade"] in ("Epic", "Legendary")),
    "efeito = Epic/Legendary na build final",
)
sistema(
    "Starter Kit",
    "itens",
    lambda r: 1,
    lambda r: 1 if r.get("starter") else 0,
    lambda r: 1 if final(r).get("starter_ainda_equipado") else 0,
    "efeito = o starter ainda está equipado no fim",
)
sistema(
    "Evolução (level-up)",
    "progressão",
    lambda r: 1,
    lambda r: conta(r, "nivel.ganhos"),
    lambda r: conta(r, "nivel.ganhos"),
)
sistema(
    "Passivas (oferta 1 de 3)",
    "progressão",
    lambda r: conta(r, "nivel.ofertas_passiva"),
    lambda r: conta(r, "passiva.escolhida"),
    None,
    "efeito por carta: NÃO MENSURADO",
)
sistema(
    "Skills: oferta a cada 3 níveis",
    "progressão",
    lambda r: conta(r, "skill.ofertas"),
    lambda r: conta(r, "skill.aprendida"),
    lambda r: sum(
        1
        for s in r["listas"].get("skills_aprendidas", [])
        if conta(r, f"skill_heroi_escolhida:{s}") > 0
    ),
    "efeito = a carta aprendida foi lançada em combate",
)
sistema(
    "Skills em combate",
    "combate",
    lambda r: soma(r, "heroi.acao:"),
    lambda r: conta(r, "heroi.acao:skill"),
    lambda r: soma(r, "skill_heroi_resultado:"),
)
sistema(
    "Reroll da Loja",
    "economia",
    lambda r: conta(r, "loja.vitrines"),
    lambda r: conta(r, "loja.reroll_pago"),
    None,
    "só rerrola com vitrine sem nada útil (gatilho do bot); efeito: NÃO MENSURADO",
)
sistema(
    "Reroll de oferta de skill/passiva",
    "progressão",
    lambda r: conta(r, "nivel.ofertas_passiva") + conta(r, "skill.ofertas"),
    lambda r: 0,
    None,
    "o driver do bot não tem caminho para pagar",
)

# --- Serviços ------------------------------------------------------------------
sistema(
    "Loja (casa no mapa)",
    "serviços",
    lambda r: sum(a["loja"] for a in andares(r)),
    lambda r: sum(a["loja_usada"] for a in andares(r)),
    lambda r: conta(r, "loja.comprou_equipamento") + soma(r, "loja.comprou_consumivel"),
)
sistema(
    "Ferreiro (casa no mapa)",
    "serviços",
    lambda r: sum(a["ferreiro"] for a in andares(r)),
    lambda r: sum(a["ferreiro_usado"] for a in andares(r)),
    lambda r: (
        conta(r, "ferreiro.enhance") + conta(r, "ferreiro.socket") + conta(r, "ferreiro.enchant")
    ),
)
sistema(
    "+N (aprimorar)",
    "ferreiro",
    lambda r: conta(r, "ferreiro.oportunidade_aprimorar_sem_teto_do_bot"),
    lambda r: conta(r, "ferreiro.enhance"),
    lambda r: sum(1 for i in equipado(r) if i["mais"] > 0),
    "oportunidade = visita em que o ouro pagava o +N mais barato; efeito = peça +N equipada no fim",
)
sistema(
    "+N na arma",
    "ferreiro",
    lambda r: conta(r, "ferreiro.oportunidade_aprimorar_sem_teto_do_bot"),
    lambda r: conta(r, "ferreiro.enhance_slot:Weapon"),
    lambda r: sum(1 for i in equipado(r) if i["slot"] == "Weapon" and i["mais"] > 0),
)
sistema(
    "Gemas (engastar)",
    "ferreiro",
    lambda r: conta(r, "ferreiro.oportunidade_engastar"),
    lambda r: conta(r, "ferreiro.socket"),
    lambda r: sum(i["gemas"] for i in equipado(r)),
    "oportunidade = visita com gema na bolsa e socket vazio",
)
sistema(
    "Retirar gema",
    "ferreiro",
    lambda r: conta(r, "ferreiro.visitas"),
    lambda r: conta(r, "ferreiro.unsocket"),
)
sistema(
    "Encantar",
    "ferreiro",
    lambda r: conta(r, "ferreiro.visitas"),
    lambda r: conta(r, "ferreiro.enchant"),
    lambda r: sum(1 for i in equipado(r) if i["encantos"] > 0),
)
sistema(
    "Reencantar",
    "ferreiro",
    lambda r: conta(r, "ferreiro.visitas"),
    lambda r: conta(r, "ferreiro.reenchant"),
)
sistema(
    "Recuperação paga (HP)",
    "serviços",
    lambda r: conta(r, "loja.vitrines"),
    lambda r: conta(r, "recuperacao.comprou:hp"),
    lambda r: conta(r, "recuperacao.comprou:hp"),
)
sistema(
    "Recuperação paga (MP)",
    "serviços",
    lambda r: conta(r, "loja.vitrines"),
    lambda r: conta(r, "recuperacao.comprou:mp"),
)
sistema(
    "Venda de itens",
    "economia",
    lambda r: conta(r, "loja.vitrines"),
    lambda r: conta(r, "venda.itens"),
    lambda r: conta(r, "venda.itens"),
)

# --- Eventos -------------------------------------------------------------------
for tipo, rot in (
    ("fountain", "Evento Fonte"),
    ("altar", "Evento Altar"),
    ("merchant", "Evento Mercador"),
):
    efeito = {
        "fountain": lambda r: conta(r, "evento.fonte_curou"),
        "altar": lambda r: 0,
        "merchant": lambda r: conta(r, "evento.mercador_gastou"),
    }[tipo]
    uso = (
        (lambda r: conta(r, "evento.altar_aceito"))
        if tipo == "altar"
        else (lambda r, t=tipo: conta(r, f"evento.pisou:{t}"))
    )
    sistema(
        rot,
        "eventos",
        lambda r, t=tipo: sum(1 for a in andares(r) if a["evento"] == t),
        uso,
        efeito,
        {
            "altar": "efeito ZERO medido (A/B 60/60): bug mecânico",
            "merchant": "o bot abre a Loja inteira, não a oferta do Mercador",
            "fountain": "",
        }[tipo],
    )

# --- Consumíveis -----------------------------------------------------------------
sistema(
    "Poção de cura (mapa + combate)",
    "consumíveis",
    lambda r: (
        conta(r, "item_disponivel_turno:max_hp") + (1 if r["registro"]["pocoes_bebidas"] else 0)
    ),
    lambda r: conta(r, "item_usado_combate:max_hp") + r["registro"]["pocoes_bebidas"],
    lambda r: conta(r, "item_usado_combate:max_hp") + r["registro"]["pocoes_bebidas"],
)
sistema(
    "Poção de mana",
    "consumíveis",
    lambda r: conta(r, "item_disponivel_turno:max_mp"),
    lambda r: conta(r, "item_usado_combate:max_mp"),
    lambda r: conta(r, "item_usado_combate:max_mp"),
)
ELIX = (
    "strength",
    "defense",
    "agility",
    "crit_chance",
    "damage_reduction",
    "life_steal",
    "evasion",
)
sistema(
    "Elixires (7 tipos no cardápio)",
    "consumíveis",
    lambda r: sum(conta(r, f"item_disponivel_turno:{e}") for e in ELIX),
    lambda r: sum(conta(r, f"item_usado_combate:{e}") for e in ELIX),
    lambda r: sum(conta(r, f"item_usado_combate:{e}") for e in ELIX),
)
sistema(
    "Elixir de mana_regen",
    "consumíveis",
    lambda r: conta(r, "loot.drop_consumivel:mana_regen"),
    lambda r: 0,
    None,
    "fora do cardápio do adaptador",
)
sistema(
    "Compra de poção de mana/elixir na Loja",
    "consumíveis",
    lambda r: conta(r, "loja.vitrines"),
    lambda r: sum(
        v
        for k, v in r["n"].items()
        if k.startswith("loja.comprou_consumivel:") and not k.endswith(":max_hp")
    ),
)

# --- Monstros ----------------------------------------------------------------------
PAPEIS = (
    "trash",
    "bruiser",
    "tank",
    "glass_cannon",
    "skirmisher",
    "controller",
    "support",
    "elite",
    "boss",
)
for p in PAPEIS:
    sistema(
        f"Arquétipo {p}",
        "monstros",
        lambda r, p=p: sum(a["papeis"].get(p, 0) for a in andares(r)),
        lambda r, p=p: conta(r, f"encontro.papel:{p}"),
        lambda r, p=p: soma(r, f"skill_monstro:{p}:"),
        "oportunidade = no mapa; uso = enfrentado; efeito = lançou skill",
    )
for m in ("execucao", "sobrevivencia", "desespero", "abertura"):
    sistema(
        f"IA do monstro: {m}",
        "monstros",
        lambda r, m=m: soma(r, f"ia.{m}.oportunidade"),
        lambda r, m=m: soma(r, f"ia.{m}.usou"),
        lambda r, m=m: soma(r, f"ia.{m}.usou"),
    )
sistema(
    "Chefe",
    "monstros",
    lambda r: sum(a["chefes"] for a in andares(r)),
    lambda r: conta(r, "encontro.chefe"),
    lambda r: conta(r, "encontro.chefe_derrotado"),
    "D4: o chefe é contornável; ver chefes deixados para trás",
)

# --- Status e leis ------------------------------------------------------------------
sistema(
    "Status aplicados pelo herói",
    "combate",
    lambda r: conta(r, "heroi.acao:skill"),
    lambda r: soma(r, "skill_heroi_status:"),
    lambda r: sum(
        v
        for k, v in r["n"].items()
        if k.startswith("status_aplicado:") and k.endswith(":em_monstro")
    ),
)
sistema(
    "Status aplicados pelos monstros",
    "combate",
    lambda r: soma(r, "ia.turnos:"),
    lambda r: soma(r, "skill_monstro:"),
    lambda r: sum(
        v for k, v in r["n"].items() if k.startswith("status_aplicado:") and k.endswith(":em_heroi")
    ),
)
sistema(
    "16 leis (qualquer disparo)",
    "combate",
    lambda r: soma(r, "encontro.papel:"),
    lambda r: soma(r, "lei:") + soma(r, "lei_core:"),
    lambda r: soma(r, "lei:") + soma(r, "lei_core:"),
)
sistema(
    "Herói escolheu ação que destrava lei",
    "combate",
    lambda r: conta(r, "heroi.turno_com_lei_disponivel"),
    lambda r: conta(r, "heroi.escolheu_acao_com_lei"),
    lambda r: soma(r, "lei:"),
)

# --- Economia, fuga, extração ------------------------------------------------------
sistema(
    "Taxa de saída paga",
    "economia",
    lambda r: len(andares(r)),
    lambda r: sum(1 for a in andares(r) if a["saida_paga"]),
    None,
)
sistema(
    "Juros",
    "economia",
    lambda r: len(andares(r)),
    lambda r: sum(1 for a in andares(r) if (a.get("juros") or 0) > 0),
    lambda r: sum(1 for a in andares(r) if (a.get("juros") or 0) > 0),
)
sistema(
    "Fuga",
    "combate",
    lambda r: soma(r, "encontro.papel:"),
    lambda r: conta(r, "fuga.decidida"),
    lambda r: conta(r, "fuga.sucesso"),
)
sistema(
    "Extração",
    "extração",
    lambda r: sum(
        1 for a in andares(r) if a["extracao"] and (a["chave_no_inicio"] or a["chave_no_fim"])
    ),
    lambda r: 1 if r["registro"]["desfecho"] == "extraiu" else 0,
    lambda r: 1 if r["registro"]["desfecho"] == "extraiu" else 0,
    "oportunidade = andar com casa E e chave no bolso",
)
sistema(
    "Medição de OP na run",
    "extração",
    lambda r: conta(r, "op.medicoes_na_run"),
    lambda r: conta(r, "op.medicoes_na_run"),
    lambda r: 1 if r["registro"].get("op") is not None else 0,
)
sistema(
    "DEFEITO: troca na posição errada",
    "itens",
    lambda r: (
        conta(r, "loot.drop_equipado")
        + conta(r, "loja.comprou_equipamento")
        + conta(r, "mercador.comprou_equipamento")
    ),
    lambda r: conta(r, "equip.trocou_a_peca_errada"),
    lambda r: conta(r, "equip.troca_errada_com_perda_liquida"),
    "uso = trocas que tiraram peça melhor que o pior ocupante; "
    "efeito = a peça nova era pior que a que saiu",
)


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "—"


def tabela(universo, rotulo):
    linhas = []
    total = len(universo)
    for nome, grupo, opp, uso, efeito, nota in SISTEMAS:
        r_opp = sum(1 for r in universo if opp(r) > 0)
        r_uso = sum(1 for r in universo if uso(r) > 0)
        r_ef = None if efeito is None else sum(1 for r in universo if efeito(r) > 0)
        e_opp = sum(opp(r) for r in universo)
        e_uso = sum(uso(r) for r in universo)
        linhas.append(
            {
                "sistema": nome,
                "grupo": grupo,
                "runs": total,
                "runs_com_oportunidade": r_opp,
                "runs_com_uso": r_uso,
                "runs_com_efeito": r_ef,
                "pct_uso_todas": pct(r_uso, total),
                "pct_uso_elegiveis": pct(r_uso, r_opp),
                "eventos_oportunidade": e_opp,
                "eventos_uso": e_uso,
                "nota": nota,
            }
        )
    print(f"\n### {rotulo} (n = {total})\n")
    print(
        "| sistema | runs c/ oportunidade | runs c/ uso | runs c/ efeito "
        "| % uso (todas) | % uso (elegíveis) | eventos opp → uso | nota |"
    )
    print("|---|---:|---:|---:|---:|---:|---|---|")
    for x in linhas:
        ef = "—" if x["runs_com_efeito"] is None else x["runs_com_efeito"]
        print(
            f"| {x['sistema']} | {x['runs_com_oportunidade']} | {x['runs_com_uso']} | {ef} | "
            f"{x['pct_uso_todas']} | {x['pct_uso_elegiveis']} | "
            f"{x['eventos_oportunidade']} → {x['eventos_uso']} | {x['nota']} |"
        )
    return linhas


print(
    f"runs: {len(runs)} (erros {len(erros)}); reproduziram o log: "
    f"{sum(r['reproduziu'] for r in runs)}/{len(runs)}"
)
print("divergências:", [r["divergencias_do_log"] for r in runs if not r["reproduziu"]][:5])
saida = {
    "completas": tabela(COMPLETAS, "Runs completas"),
    "extraidas": tabela(EXTRAIDAS, "Builds extraídas"),
}


# --- Detalhes: leis, status, skills, papéis --------------------------------------
def contagem(universo, prefixo):
    c = collections.Counter()
    runs_c = collections.Counter()
    for r in universo:
        for k, v in r["n"].items():
            if k.startswith(prefixo):
                c[k[len(prefixo) :]] += v
                runs_c[k[len(prefixo) :]] += 1
    return c, runs_c


from src.shared import effect_core as core  # noqa: E402
from src.shared import interactions as ix  # noqa: E402

for rot, uni in (("COMPLETAS", COMPLETAS), ("EXTRAIDAS", EXTRAIDAS)):
    print(f"\n#### Leis — {rot}")
    c1, rc1 = contagem(uni, "lei:")
    c2, rc2 = contagem(uni, "lei_core:")
    por_lei = collections.Counter()
    runs_lei = collections.Counter()
    for k, v in list(c1.items()) + list(c2.items()):
        lei = k.split(":")[0]
        if "+" in lei:
            a, b = lei.split("+")
            cand = [
                i.id
                for i in ix.all_interactions()
                if set(i.id.split("_")) >= {a, b} or i.id in (f"{a}_{b}", f"{b}_{a}")
            ]
            lei = cand[0] if cand else lei
        por_lei[lei] += v
    for r in uni:
        vistos = set()
        for k in r["n"]:
            if k.startswith("lei:") or k.startswith("lei_core:"):
                lei = k.split(":")[1]
                if "+" in lei:
                    a, b = lei.split("+")
                    cand = [i.id for i in ix.all_interactions() if i.id in (f"{a}_{b}", f"{b}_{a}")]
                    lei = cand[0] if cand else lei
                vistos.add(lei)
        for lei in vistos:
            runs_lei[lei] += 1
    for i in ix.all_interactions():
        print(
            f"  {i.id:22s} [{i.kind:6s}] disparos={por_lei.get(i.id, 0):5d}  "
            f"runs={runs_lei.get(i.id, 0)}"
        )
    print("  por ator:", dict(c1), dict(c2))
    print(f"\n#### Status — {rot}")
    c, rc = contagem(uni, "status_aplicado:")
    for e in sorted(core.CATALOG):
        h = c.get(f"{e}:em_heroi", 0)
        m = c.get(f"{e}:em_monstro", 0)
        print(
            f"  {e:13s} no herói={h:5d} (runs {rc.get(f'{e}:em_heroi', 0)})  "
            f"no monstro={m:5d} (runs {rc.get(f'{e}:em_monstro', 0)})"
        )
    print(f"\n#### Passivas escolhidas por família — {rot}")
    c, rc = contagem(uni, "passiva.familia:")
    print("  ", dict(c.most_common()))
    print(f"\n#### Encontros por papel — {rot}")
    c, rc = contagem(uni, "encontro.papel:")
    print("  ", {p: (c.get(p, 0), rc.get(p, 0)) for p in PAPEIS})

if SAIDA_JSON:
    json.dump(saida, open(SAIDA_JSON, "w"), ensure_ascii=False, indent=1)


# --- Detalhes complementares ---------------------------------------------------
SK = {
    s["id"]: s
    for s in json.load(
        open(str(pathlib.Path(__file__).resolve().parents[1]) + "/src/data/skills.json")
    )["skills"]
}
import statistics as st  # noqa: E402

for rot, uni in (("COMPLETAS", COMPLETAS), ("EXTRAIDAS", EXTRAIDAS)):
    print(f"\n#### Complementos — {rot} (n={len(uni)})")
    deixados = sum(a["chefes_restantes"] for r in uni for a in andares(r) if a["desfecho"] == "")
    com_chefe = sum(1 for r in uni for a in andares(r) if a["chefes"])
    print(
        f"  chefes: andares com chefe {com_chefe}; "
        f"chefes deixados vivos em andar concluído {deixados}"
    )
    esc = collections.Counter()
    disp = collections.Counter()
    for r in uni:
        for k, v in r["n"].items():
            if k.startswith("skill_heroi_escolhida:"):
                esc[SK.get(k.split(":", 1)[1], {}).get("effect_type", "?")] += v
        for sid, v in (r.get("skills_disponiveis") or {}).items():
            disp[SK.get(sid, {}).get("effect_type", "?")] += v
    print("  skills do herói: turnos disponíveis por tipo", dict(disp), "| escolhidas", dict(esc))
    nunca = collections.Counter()
    for r in uni:
        for sid, v in (r.get("skills_disponiveis") or {}).items():
            if conta(r, f"skill_heroi_escolhida:{sid}") == 0 and v >= 20:
                nunca[SK.get(sid, {}).get("effect_type", "?")] += 1
    print("  (run, skill) disponível em 20+ turnos e nunca escolhida, por tipo:", dict(nunca))
    deck = collections.Counter(
        SK.get(s, {}).get("effect_type", "?") for r in uni for s in (final(r).get("skills") or [])
    )
    print("  deck final por tipo:", dict(deck))
    fim_g = [
        (
            final(r).get("gemas_na_bolsa", 0),
            sum(1 for i in equipado(r) for _ in range(max(0, i["sockets"] - i["gemas"]))),
        )
        for r in uni
    ]
    print(
        f"  gemas: runs com gema na bolsa no fim {sum(1 for g, v in fim_g if g)}; "
        f"com gema na bolsa E socket vazio equipado {sum(1 for g, v in fim_g if g and v)}"
    )
    ouro = [final(r).get("ouro", 0) for r in uni]
    ganho = [max(1, (final(r).get("ledger") or {}).get("gold_earned", 1)) for r in uni]
    if ouro:
        print(
            f"  ouro no fim: mediana {st.median(ouro):.0f}; fração do ganho parada: "
            f"mediana {st.median([o / g for o, g in zip(ouro, ganho)]):.1%}"
        )
    mochila = collections.Counter()
    for r in uni:
        for cat in final(r).get("melhor_na_mochila_que_o_pior_equipado") or {}:
            mochila[cat] += 1
    print("  runs com peça melhor na mochila que o pior ocupante, por categoria:", dict(mochila))
    errada = collections.Counter()
    for r in uni:
        for k, v in r["n"].items():
            if k.startswith("equip.trocou_a_peca_errada:"):
                errada[k.split(":")[1]] += v
    print(
        "  trocas na posição errada por categoria:",
        dict(errada),
        "| runs:",
        sum(1 for r in uni if conta(r, "equip.trocou_a_peca_errada")),
        "| com perda líquida:",
        sum(1 for r in uni if conta(r, "equip.troca_errada_com_perda_liquida")),
    )
    mais = collections.Counter((i["slot"] == "Weapon", i["mais"]) for r in uni for i in equipado(r))
    print("  +N no fim (arma?, nível): ", dict(sorted(mais.items())))
    pen = sum(
        1
        for r in uni
        for a in andares(r)
        if (a.get("essencia_efetiva") or 0) < (a.get("essencia_sorteada") or 0) - 1e-9
    )
    print(
        f"  Essência: andares com penalidade de saída não paga {pen} "
        f"de {sum(len(andares(r)) for r in uni)}"
    )
    print(
        f"  Égide (absorções): runs {sum(1 for r in uni if conta(r, 'egide.absorveu'))}; "
        f"críticos do herói em {sum(1 for r in uni if conta(r, 'critico:heroi'))} runs"
    )
    porcl = collections.defaultdict(list)
    for r in uni:
        porcl[r["tarefa"]["classe"]].append(r)
    for cl, rs in sorted(porcl.items()):
        print(
            f"  [{cl}] n={len(rs)} "
            f"extraiu={sum(r['registro']['desfecho'] == 'extraiu' for r in rs)} "
            f"andar mediano={st.median([r['registro']['andar'] for r in rs])} "
            f"+N={sum(1 for r in rs if conta(r, 'ferreiro.enhance'))} "
            f"gemas={sum(1 for r in rs if conta(r, 'ferreiro.socket'))} "
            f"encanto={sum(1 for r in rs if conta(r, 'ferreiro.enchant'))} "
            f"altar={sum(1 for r in rs if conta(r, 'evento.altar_aceito'))} "
            f"troca_errada={sum(1 for r in rs if conta(r, 'equip.trocou_a_peca_errada'))} "
            f"leis={sum(1 for r in rs if soma(r, 'lei:') + soma(r, 'lei_core:'))}"
        )
