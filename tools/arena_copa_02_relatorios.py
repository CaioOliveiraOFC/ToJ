"""Relatórios da Copa Arena 02: Markdown, trace, dashboard HTML e PDF.

Tudo sai de um MODELO único (`modelo(copa)`), em dado puro, montado a partir das
partidas reais e do trace da auditoria. O Markdown, o dashboard e o PDF leem o
mesmo modelo; a chave de 64 e os gráficos são SVG gerados aqui, iguais nas duas
saídas visuais. Nenhum número é estimado fora do motor: o que não está no
histórico ou no trace não aparece.

Os modelos de página, o CSS e o JavaScript do dashboard ficam em
`tools/arena_copa_02_assets/`; aqui só se preenchem os marcadores `@@nome@@`.

O PDF é impresso pelo Chromium em modo headless a partir da página `visual.html`
(A4 paisagem, com a chave numa página A2 paisagem). Sem Chromium, o PDF é
pulado e o motivo é informado; o resto dos relatórios não depende dele.
"""

from __future__ import annotations

import html
import json
import math
import os
import shutil
import statistics
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from src.content.gladiator import prepare_gladiator
from src.mechanics.pvp_duel import SIDES, opponent_of
from tools.arena_copa_02 import (
    ARQUIVO_CALIBRACAO,
    COPA,
    FAIXAS,
    FASES,
    MAX_TENTATIVAS,
    NOME_DA_FASE,
    PASTA_DE_SAIDA,
    REALOCACOES,
    SEMENTE_PRINCIPAL,
    faixa_de,
    todas,
)
from tools.arena_copa_teste import (
    CLASSE,
    LIMITE_TECNICO,
    _bloco_da_partida,
    _diagnostico_final,
    _nome_da_carta,
    cura_total,
    dano_total,
    estatisticas,
    nome_da_acao,
    relatorio_final,
    trace_json,
)

ARQUIVO_RELATORIO = "relatorio.md"
ARQUIVO_FINAL = "final_detalhada.md"
ARQUIVO_TRACE = "final_trace.json"
ARQUIVO_DASHBOARD = "dashboard.html"
ARQUIVO_PDF = "relatorio_visual.pdf"
RECURSOS = Path(__file__).resolve().parent / "arena_copa_02_assets"
CLASSES = ("Warrior", "Mage", "Rogue")
CONTROLES = ("stun", "sleep", "frozen")
AVISO_NOMES = (
    "Os nomes são apenas identificadores de personagens simulados, tirados de canais da "
    "Twitch. Não existe participação, autorização ou endosso dessas pessoas. Classe, build, "
    "força e posição na chave foram atribuídas por sorteio e não têm relação com a pessoa "
    "real nem com o desempenho dela."
)
AVISO_ESTATISTICA = (
    "Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por "
    "confronto. Ela aponta casos para investigar; não prova balanceamento entre classes."
)


# --- o modelo ------------------------------------------------------------------


def _ficha(participante) -> dict:
    heroi = prepare_gladiator(participante.heroi).hero
    espec = participante.espec
    return {
        "id": espec.id,
        "nome": espec.nome,
        "grupo": espec.grupo,
        "rotulo": espec.rotulo,
        "classe": espec.classe,
        "classe_pt": CLASSE[espec.classe],
        "nivel": espec.nivel,
        "faixa": espec.faixa,
        "faixa_medida": faixa_de(participante.poder),
        "op": participante.poder,
        "hp": heroi.base_hp,
        "mp": heroi.base_mp,
        "st": heroi.get_st(),
        "mg": heroi.get_mg(),
        "ag": heroi.get_ag(),
        "df": heroi.get_df(),
        "equipamento": {p: i.display_name for p, i in heroi.equipment.items() if i is not None},
        "deck": [heroi.skills[k].name for k in sorted(heroi.skills)],
        "passivas": [[nome, n] for nome, n in Counter(p.name for p in heroi.passives).items()],
        "trocas": [list(t) for t in espec.trocas],
        "foco": espec.foco,
        "tentativas": list(espec.tentativas),
    }


def _lado_de(st: dict) -> dict:
    """Os totais de um lado, em dado puro."""
    return {
        "dano": dano_total(st),
        "dano_golpes": st["dano_golpes"],
        "dano_dot": st["dano_dot"],
        "cura": cura_total(st),
        "cura_skill": st["cura_skill"],
        "roubo_de_vida": st["roubo_de_vida"],
        "mp": st["mp_gasto"],
        "skills": st["skills"],
        "basicos": st["basicos"],
        "acertos": st["acertos"],
        "erros": st["erros"],
        "criticos": st["criticos"],
        "dano_critico": st["dano_critico"],
        "status_aplicados": list(st["status_aplicados"]),
        "status_falhos": list(st["status_falharam_na_rolagem"])
        + list(st["status_anulados"])
        + list(st["status_recusados_pelo_nucleo"]),
        "perdidas_controle": st["perdidas_controle"],
        "egide": st["egide_absorvido"],
        "egide_mp": st["egide_mp"],
        "buffs": list(st["buffs"]),
        "leis": list(st["leis"]),
        "skills_usadas": {_nome_da_carta(k): n for k, n in st["skills_usadas"].items()},
        "primeiro": st["primeiro"],
    }


def _rodadas(duelo) -> tuple[list[dict], int]:
    rodadas = []
    anterior = None
    viradas = 0
    for registro in duelo.history:
        passos = {p.side: p for p in registro.steps}
        if anterior is not None and registro.order.first != anterior:
            viradas += 1
        anterior = registro.order.first
        rodadas.append(
            {
                "n": registro.number,
                "ordem": [registro.order.first, registro.order.second],
                "criterio": registro.order.decided_by,
                "acoes": {
                    lado: {
                        "acao": nome_da_acao(passos[lado].action),
                        "desfecho": passos[lado].outcome,
                        "dano": passos[lado].damage_to_opponent,
                        "mp": passos[lado].mp_spent,
                    }
                    for lado in SIDES
                },
                "hp": dict(registro.hp_end),
                "mp": dict(registro.mp_end),
            }
        )
    return rodadas, viradas


def _golpes(trace, ids: dict) -> list[dict]:
    inicio = {g["golpe"]: g for g in trace.de("golpe_inicio")}
    golpes = []
    for g in trace.de("golpe_fim"):
        skill = inicio[g["golpe"]]["skill"]
        golpes.append(
            {
                "atacante": ids[g["atacante"]],
                "defensor": ids[g["defensor"]],
                "dano": g["resultado"]["damage"],
                "critico": g["resultado"]["was_critical"],
                "errou": g["resultado"]["was_evaded"],
                "rodada": g["rodada"],
                "acao": _nome_da_carta(skill) if skill else "Ataque básico",
                "matou": g["defensor_morreu"],
                "death_ignore": g["death_ignore_disparou"],
            }
        )
    return golpes


def _jogo(partida) -> dict:
    st = estatisticas(partida)
    duelo = partida.auditado.duelo
    trace = partida.auditado.trace
    resultado = duelo.result
    ids = {lado: partida.lados[lado].id for lado in SIDES}
    rodadas, viradas = _rodadas(duelo)
    status = [
        {
            "status": s["status"],
            "autor": ids.get(s["atacante"]),
            "alvo": ids[s["alvo"]],
            "pegou": s["pegou"],
            "rolou": s["rolou"],
            "rodada": s["rodada"],
        }
        for s in trace.de("status")
    ]
    leis = [lei["nome"] for i in trace.de("interacoes") for lei in i["leis"]]
    egide = [
        e["dano_entrada"] - e["dano_saida"] for e in trace.de("egide") if not e.get("inaplicavel")
    ]
    venc, perd = resultado.winner, resultado.loser
    heroi = duelo.hero(venc)
    op = {lado: partida.lados[lado].poder for lado in SIDES}
    # O teto de HP de referência é o do início da luta: um efeito de recurso
    # (`frailty`) corta o teto durante o duelo sem cortar o HP atual.
    teto_inicial = trace.de("rodada_inicio")[0]["estado"][venc]["hp_max"]
    return {
        "chave": f"{partida.fase}-{partida.indice}",
        "fase": partida.fase,
        "nome_fase": NOME_DA_FASE[partida.fase],
        "indice": partida.indice,
        "titulo": partida.titulo,
        "seed": str(partida.semente),
        "p1": ids["p1"],
        "p2": ids["p2"],
        "op": op,
        "vencedor": ids[venc],
        "perdedor": ids[perd],
        "lado_vencedor": venc,
        "motivo": resultado.reason,
        "rodadas": len(duelo.history),
        "hp_vencedor": heroi.get_hp(),
        "hp_max_vencedor": teto_inicial,
        "hp_teto_final_vencedor": heroi.base_hp,
        "hp_final_perdedor": duelo.hero(perd).get_hp(),
        "delta_op": op[venc] - op[perd],
        "zebra": op[venc] < op[perd],
        "lados": {lado: _lado_de(st[lado]) for lado in SIDES},
        "rodadas_detalhe": rodadas,
        "golpes": _golpes(trace, ids),
        "status": status,
        "leis": leis,
        "egide": egide,
        "viradas": viradas,
        "criterios": dict(Counter(r["criterio"] for r in rodadas)),
        "fidelidade": all(ok for _, ok in partida.fidelidade),
        "coerencia": all(ok for _, ok in partida.coerencia),
        "verificacoes": len(partida.fidelidade) + len(partida.coerencia),
        "sorteios": partida.auditado.rng.chamadas,
    }


def modelo(copa) -> dict:
    participantes = [_ficha(p) for p in copa.participantes]
    partidas = [_jogo(p) for p in todas(copa)]
    destino = {
        p["id"]: {"fase": "fase64", "eliminado_por": None, "vitorias": 0} for p in participantes
    }
    for jogo in partidas:
        destino[jogo["vencedor"]]["vitorias"] += 1
        destino[jogo["vencedor"]]["fase"] = jogo["fase"]
        destino[jogo["perdedor"]]["fase"] = jogo["fase"]
        destino[jogo["perdedor"]]["eliminado_por"] = jogo["vencedor"]
    campeao = copa.campeao.id if copa.campeao else None
    for p in participantes:
        p.update(destino[p["id"]])
        p["campeao"] = p["id"] == campeao
    dados = {
        "copa": COPA,
        "semente_principal": SEMENTE_PRINCIPAL,
        "limite_tecnico": LIMITE_TECNICO,
        "faixas": [list(f) for f in FAIXAS],
        "fases": [[f, n, nome] for f, n, nome in FASES],
        "chave": list(copa.chave),
        "campeao": campeao,
        "interrompida": copa.interrompida,
        "participantes": participantes,
        "partidas": partidas,
    }
    dados["agregados"] = agregados(dados)
    dados["final"] = None
    if "final" in copa.fases:
        final = copa.fases["final"][0]
        dados["final"] = _final(final)
        dados["final"]["diagnostico"] = [
            [len(linha) - len(linha.lstrip(" ")), linha.strip()[2:].replace("**", "")]
            for linha in _diagnostico_final(final)
            if linha.strip().startswith("- ")
        ]
    return dados


def _final(partida) -> dict:
    """O que o dashboard mostra da final: iniciativa e HP por rodada, e o golpe decisivo."""
    trace = partida.auditado.trace
    duelo = partida.auditado.duelo
    ids = {lado: partida.lados[lado].id for lado in SIDES}
    iniciativa: dict[int, dict] = {}
    for x in trace.de("iniciativa"):
        iniciativa.setdefault(x["rodada"], {})[x["lado"]] = {
            "score": x["score"],
            "build": x["build"],
            "modificador": x["modificador"],
            "parcelas": {p["stat"]: [p["valor"], p["ref"], p["raiz"]] for p in x["parcelas"]},
        }
    hp = [{lado: r["estado"][lado]["hp"] for lado in SIDES} for r in trace.de("rodada_inicio")]
    hp.append({lado: duelo.hero(lado).get_hp() for lado in SIDES})
    decisivo = next((g for g in reversed(trace.de("golpe_fim")) if g["defensor_morreu"]), None)
    funil = None
    if decisivo is not None:
        funil = next(
            (r for r in trace.records if r["kind"] == "funil" and r["golpe"] == decisivo["golpe"]),
            None,
        )
    rolagens = Counter(r["mecanica"].split(" (")[0] for r in trace.de("rolagem"))
    return {
        "chave": f"final-{partida.indice}",
        "ids": ids,
        "iniciativa": [[n, iniciativa[n]] for n in sorted(iniciativa)],
        "hp": hp,
        "hp_max": {lado: duelo.hero(lado).base_hp for lado in SIDES},
        "decisivo": None
        if decisivo is None
        else {
            "rodada": decisivo["rodada"],
            "atacante": ids[decisivo["atacante"]],
            "dano": decisivo["resultado"]["damage"],
            "critico": decisivo["resultado"]["was_critical"],
            "hp_antes": decisivo["hp_defensor"][0],
            "hp_depois": decisivo["hp_defensor"][1],
            "funil_final": funil["final"] if funil else None,
            "base": funil["base"] if funil else None,
            "fator_defesa": funil["fator_defesa"] if funil else None,
        },
        "rolagens": dict(rolagens),
        "sorteios": partida.auditado.rng.chamadas,
        "fidelidade": [[n, ok] for n, ok in partida.fidelidade],
        "coerencia": [[n, ok] for n, ok in partida.coerencia],
    }


def _media(xs) -> float:
    return statistics.mean(xs) if xs else 0.0


def _por_classe(dados: dict, ordem_das_fases: list[str]) -> dict:
    jogos = dados["partidas"]
    saida = {}
    for classe in CLASSES:
        membros = [p for p in dados["participantes"] if p["classe"] == classe]
        ids = {p["id"] for p in membros}
        lados = [(j, lado) for j in jogos for lado in SIDES if j[lado] in ids]
        vitorias = sum(1 for j, lado in lados if j["vencedor"] == j[lado])
        golpes = [g for j in jogos for g in j["golpes"] if g["atacante"] in ids]
        conectados = [g for g in golpes if not g["errou"]]
        criticos = sum(1 for g in conectados if g["critico"])
        saida[classe] = {
            "participantes": len(membros),
            "op_medio": _media([p["op"] for p in membros]),
            "partidas": len(lados),
            "vitorias": vitorias,
            "derrotas": len(lados) - vitorias,
            "taxa": vitorias / len(lados) if lados else 0.0,
            "alcancou": {
                fase: sum(
                    1
                    for p in membros
                    if ordem_das_fases.index(p["fase"]) >= ordem_das_fases.index(fase)
                )
                for fase in ordem_das_fases
            },
            "dano_por_partida": _media([j["lados"][lado]["dano"] for j, lado in lados]),
            "acerto": len(conectados) / len(golpes) if golpes else 0.0,
            "criticos": criticos,
            "taxa_critico": criticos / len(conectados) if conectados else 0.0,
            "cura": sum(j["lados"][lado]["cura"] for j, lado in lados),
            "perdidas_controle": sum(j["lados"][lado]["perdidas_controle"] for j, lado in lados),
            "campeao": any(p["campeao"] for p in membros),
        }
    return saida


def _op_por_fase(dados: dict, part: dict, ordem_das_fases: list[str]) -> list[dict]:
    saida = []
    for fase in ordem_das_fases:
        da_fase = [j for j in dados["partidas"] if j["fase"] == fase]
        if not da_fase:
            continue
        vencedores = [part[j["vencedor"]]["op"] for j in da_fase]
        perdedores = [part[j["perdedor"]]["op"] for j in da_fase]
        entrando = vencedores + perdedores
        saida.append(
            {
                "fase": fase,
                "nome": NOME_DA_FASE[fase],
                "partidas": len(da_fase),
                "vencedores": [_media(vencedores), min(vencedores), max(vencedores)],
                "perdedores": [_media(perdedores), min(perdedores), max(perdedores)],
                "entrando": [_media(entrando), min(entrando), max(entrando)],
                "favorito_venceu": sum(1 for j in da_fase if not j["zebra"]),
            }
        )
    return saida


def _resumo(j: dict) -> dict:
    return {
        "chave": j["chave"],
        "titulo": j["titulo"],
        "vencedor": j["vencedor"],
        "perdedor": j["perdedor"],
        "delta_op": j["delta_op"],
        "rodadas": j["rodadas"],
        "nome_fase": j["nome_fase"],
    }


def agregados(dados: dict) -> dict:
    part = {p["id"]: p for p in dados["participantes"]}
    jogos = dados["partidas"]
    ordem_das_fases = [f for f, _, _ in dados["fases"]]
    matriz = {c: {d: 0 for d in CLASSES} for c in CLASSES}
    for j in jogos:
        matriz[part[j["vencedor"]]["classe"]][part[j["perdedor"]]["classe"]] += 1
    zebras = sorted((j for j in jogos if j["zebra"]), key=lambda j: j["delta_op"])
    golpes = [dict(g, chave=j["chave"]) for j in jogos for g in j["golpes"] if not g["errou"]]
    criticos = [g for g in golpes if g["critico"]]
    skills, buffs, aplicados, falhos, leis, curas, criterios = (Counter() for _ in range(7))
    for j in jogos:
        for lado in SIDES:
            skills.update(j["lados"][lado]["skills_usadas"])
            buffs.update(j["lados"][lado]["buffs"])
            curas[j[lado]] += j["lados"][lado]["cura"]
        for s in j["status"]:
            (aplicados if s["pegou"] else falhos)[s["status"]] += 1
        leis.update(j["leis"])
        criterios.update(j["criterios"])

    def dano_de(pid):
        return sum(j["lados"][lado]["dano"] for j in jogos for lado in SIDES if j[lado] == pid)

    eliminacoes = sorted(dados["participantes"], key=lambda p: (-p["vitorias"], -dano_de(p["id"])))
    faixa_contra_faixa = Counter(
        (part[j["vencedor"]]["faixa_medida"], part[j["perdedor"]]["faixa_medida"]) for j in jogos
    )
    ops = [p["op"] for p in dados["participantes"]]
    por_rodadas = sorted(jogos, key=lambda j: (-j["rodadas"], j["chave"]))
    return {
        "por_classe": _por_classe(dados, ordem_das_fases),
        "matriz": matriz,
        "op_por_fase": _op_por_fase(dados, part, ordem_das_fases),
        "op_medio": _media(ops),
        "op_min": min(ops),
        "op_max": max(ops),
        "por_faixa": dict(Counter(p["faixa_medida"] for p in dados["participantes"])),
        "favoritos": sum(1 for j in jogos if not j["zebra"]),
        "zebras": [_resumo(j) for j in zebras],
        "maiores_diferencas": [
            _resumo(j) for j in sorted(jogos, key=lambda j: -abs(j["delta_op"]))[:10]
        ],
        "maiores_golpes": sorted(golpes, key=lambda g: (-g["dano"], g["chave"]))[:10],
        "criticos_total": len(criticos),
        "maior_critico": max(criticos, key=lambda g: g["dano"]) if criticos else None,
        "golpes_total": sum(len(j["golpes"]) for j in jogos),
        "golpes_conectados": len(golpes),
        "longas": [_resumo(j) for j in por_rodadas[:5]],
        "curtas": [_resumo(j) for j in sorted(jogos, key=lambda j: (j["rodadas"], j["chave"]))[:5]],
        "rodadas_total": sum(j["rodadas"] for j in jogos),
        "rodadas_hist": dict(sorted(Counter(j["rodadas"] for j in jogos).items())),
        "skills": skills.most_common(),
        "buffs": buffs.most_common(),
        "status_aplicados": aplicados.most_common(),
        "status_falhos": falhos.most_common(),
        "controles": {c: aplicados.get(c, 0) for c in CONTROLES},
        "perdidas_controle": sum(
            j["lados"][lado]["perdidas_controle"] for j in jogos for lado in SIDES
        ),
        "curas": curas.most_common(5),
        "cura_total": sum(curas.values()),
        "leis": leis.most_common(),
        "criterios": dict(criterios),
        "eliminacoes": [[p["id"], p["vitorias"]] for p in eliminacoes[:10]],
        "faixa_contra_faixa": [[v, p, n] for (v, p), n in sorted(faixa_contra_faixa.items())],
        "campeao": dados["campeao"],
        "curiosidades": curiosidades(dados),
    }


def curiosidades(dados: dict) -> list[str]:
    """Situações incomuns, lidas dos dados. Cada frase cita a partida de onde sai."""
    part = {p["id"]: p for p in dados["participantes"]}
    jogos = dados["partidas"]
    frases = []

    def nome(pid):
        return f"{part[pid]['nome']} ({pid})"

    zebras = [j for j in jogos if j["zebra"]]
    if zebras:
        z = min(zebras, key=lambda j: j["delta_op"])
        frases.append(
            f"Maior zebra: {nome(z['vencedor'])}, OP {part[z['vencedor']]['op']:.2f}, eliminou "
            f"{nome(z['perdedor'])}, OP {part[z['perdedor']]['op']:.2f} ({z['nome_fase']}, "
            f"diferença de {abs(z['delta_op']):.2f})."
        )
    apertada = min(jogos, key=lambda j: j["hp_vencedor"] / j["hp_max_vencedor"])
    frases.append(
        f"Vitória mais apertada: {nome(apertada['vencedor'])} terminou com "
        f"{apertada['hp_vencedor']}/{apertada['hp_max_vencedor']} de HP contra "
        f"{nome(apertada['perdedor'])} ({apertada['nome_fase']})."
    )
    sobra = min(jogos, key=lambda j: j["hp_final_perdedor"])
    frases.append(
        f"Golpe que mais passou do necessário: {nome(sobra['perdedor'])} terminou com "
        f"{sobra['hp_final_perdedor']} de HP ({sobra['titulo']})."
    )
    ignorados = [(j, g) for j in jogos for g in j["golpes"] if g["death_ignore"]]
    if ignorados:
        frases.append(
            f"`death_ignore` salvou um golpe letal {len(ignorados)} vez(es): "
            + "; ".join(f"{nome(g['defensor'])} em {j['titulo']}" for j, g in ignorados[:5])
            + "."
        )
    else:
        frases.append("Nenhum `death_ignore` disparou: nenhum dos 64 tem essa fonte.")
    letais = [g for j in jogos for g in j["golpes"] if g["critico"] and g["matou"]]
    if letais:
        frases.append(
            f"{len(letais)} partida(s) terminaram num golpe crítico; o maior deles tirou "
            f"{max(g['dano'] for g in letais)} de HP."
        )
    sem_vez = [
        j for j in jogos if all(r["ordem"][0] != j["lado_vencedor"] for r in j["rodadas_detalhe"])
    ]
    if sem_vez:
        frases.append(
            f"{len(sem_vez)} partida(s) foram vencidas por quem NUNCA agiu primeiro, como "
            f"{nome(sem_vez[0]['vencedor'])} em {sem_vez[0]['titulo']}."
        )
    viradas = [j for j in jogos if j["viradas"]]
    if viradas:
        mais = max(viradas, key=lambda j: j["viradas"])
        frases.append(
            f"A ordem de iniciativa mudou dentro de {len(viradas)} partida(s); o recorde foi "
            f"{mais['viradas']} virada(s) em {mais['titulo']}."
        )
    criterios = Counter()
    for j in jogos:
        criterios.update(j["criterios"])
    desempates = criterios.get("relative_ag", 0) + criterios.get("fallback", 0)
    frases.append(
        f"De {sum(criterios.values())} rodadas, {criterios.get('score', 0)} tiveram a ordem "
        f"decidida pelo score; {desempates} precisaram de desempate."
    )
    controle = max(jogos, key=lambda j: sum(j["lados"][x]["perdidas_controle"] for x in SIDES))
    perdidas = sum(controle["lados"][x]["perdidas_controle"] for x in SIDES)
    if perdidas:
        frases.append(
            f"Partida com mais ações perdidas por controle: {controle['titulo']}, com {perdidas}."
        )
    egide = [(j, a) for j in jogos for a in j["egide"]]
    if egide:
        j, a = max(egide, key=lambda x: x[1])
        frases.append(f"Maior absorção da Égide de Mana num golpe: {a} de dano, em {j['titulo']}.")
    leis = Counter(lei for j in jogos for lei in j["leis"])
    if leis:
        frases.append(
            "Leis de interação disparadas: "
            + ", ".join(f"{lei} ×{n}" for lei, n in leis.most_common())
            + "."
        )
    sem_critico = [
        j
        for j in jogos
        if not any(g["critico"] for g in j["golpes"] if g["atacante"] == j["vencedor"])
    ]
    frases.append(
        f"{len(sem_critico)} das {len(jogos)} vitórias saíram sem nenhum crítico do vencedor."
    )
    acima = [j for j in jogos if j["hp_vencedor"] > j["hp_teto_final_vencedor"]]
    if acima:
        j = acima[0]
        frases.append(
            f"Em {len(acima)} partida(s) o vencedor terminou com HP atual acima do teto do fim "
            f"da luta, como {nome(j['vencedor'])} em {j['titulo']} ({j['hp_vencedor']} de HP com "
            f"teto {j['hp_teto_final_vencedor']}, contra {j['hp_max_vencedor']} no início): "
            "`frailty` corta o HP máximo e o motor não corta o HP atual."
        )
    um_turno = [j for j in jogos if j["rodadas"] == 1]
    if um_turno:
        frases.append(f"{len(um_turno)} partida(s) acabaram na primeira rodada.")
    de_baixo = [
        j
        for j in jogos
        if part[j["vencedor"]]["faixa_medida"] == 1 and part[j["perdedor"]]["faixa_medida"] == 4
    ]
    if de_baixo:
        frases.append(
            f"{len(de_baixo)} vez(es) alguém da faixa 20–22,5 eliminou alguém da faixa 27,5–30."
        )
    return frases


# --- Markdown ------------------------------------------------------------------


def _n(pid: str, part: dict) -> str:
    return f"{part[pid]['nome']} ({pid})"


def _tentativas(lista: list[dict]) -> str:
    return "; ".join(
        f"L{t['nivel']}→{t['op']:.2f}" if "op" in t else f"L{t['nivel']} ilegal" for t in lista
    )


def _passivas_txt(passivas) -> str:
    return ", ".join(f"{nome} ×{n}" if n > 1 else nome for nome, n in passivas)


def _montagem_md() -> list[str]:
    return [
        "## Como a Copa foi montada",
        "",
        "- **Builds legais.** Classe e nível por `make_hero`; deck de até 4 cartas da oferta da "
        "classe (classe + Neutral), cada carta além da inicial com uma oferta própria (níveis 3, "
        "6, 9, …) de nível ≥ `level_required`, e requisito de equipamento atendido; `nível − 1` "
        "passivas, sem Lendária, no máximo uma Épica e duas cópias por Rara; equipamento do "
        "`expected loadout` do nível, com trocas só por peças que caem de loot, servem à classe "
        "e à posição e não superam em dano+defesa a melhor peça da mesma categoria do loadout.",
        "- **Poder.** `overall_power` canônico, sem cache, medido de novo nesta execução.",
        f"- **Calibração.** Só o nível muda; no máximo {MAX_TENTATIVAS} medições por "
        "participante, a partir de um palpite por classe e faixa (tabela abaixo).",
        f"- **Chave.** Seed principal `{SEMENTE_PRINCIPAL}`; `random.Random(seed).shuffle` dos "
        "64 IDs, pares em ordem, sem cabeças de chave. Seed de cada partida: os 8 primeiros bytes "
        '(big-endian) de `sha256(f"{seed}:{fase}:{índice}")`, o mesmo esquema da Copa 01.',
        "- **Nomes.** Sorteados para os IDs com uma seed derivada própria "
        '(`sha256(f"{seed}:nomes")`), independente das builds e da chave.',
        "- **Política.** `PoliticaCopa` da Copa 01, igual para os 64: cura com HP ≤ 50%; senão "
        "buff ou redução ainda não ativos; senão status que o adversário não carrega; senão a "
        "primeira skill de dano legal; senão ataque básico. Lê só a `DuelView` e o próprio deck.",
        "- **Partida.** Preparação nova a cada duelo (HP e MP cheios, sem recarga nem efeito). "
        f"Limite técnico do laço: {LIMITE_TECNICO} rodadas (inconclusivo, nunca empate); não foi "
        "atingido.",
        "- **Isolamento.** Bonecos só em memória; nenhum save, slot ou coleção de gladiadores.",
        "- **Fora do catálogo desta Copa.** A carta `fantasma` (status `invisible` com alvo "
        "próprio): `apply_skill` aplica todo status no adversário, então ela tornaria o RIVAL "
        "invisível. É uma peculiaridade do motor, também no PvE, registrada aqui e não corrigida: "
        "`src/` não muda nesta Copa.",
        "",
    ]


def _calibracao_md(dados: dict) -> list[str]:
    ag = dados["agregados"]
    linhas = [
        "## Calibração",
        "",
        "| ID | Gladiador | Build | Classe | Faixa pedida | Nível | OP medido | Faixa medida "
        "| Tentativas (nível→OP) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for p in dados["participantes"]:
        linhas.append(
            f"| {p['id']} | {p['nome']} | {p['rotulo']} | {p['classe_pt']} | {p['faixa']} "
            f"| {p['nivel']} | {p['op']:.2f} | {p['faixa_medida']} "
            f"| {_tentativas(p['tentativas'])} |"
        )
    fora = [p["id"] for p in dados["participantes"] if p["faixa_medida"] != p["faixa"]]
    linhas += [
        "",
        f"Por faixa medida: {dict(sorted(ag['por_faixa'].items()))}. "
        + (f"Fora da faixa pedida: {fora}." if fora else "Nenhum fora da faixa pedida."),
        "",
    ]
    if REALOCACOES:
        linhas += ["Faixas inviáveis registradas na calibração:", ""]
        linhas += [f"- **{r}**: faixa {de} → {para}. {m}" for r, de, para, m in REALOCACOES]
        linhas.append("")
    return linhas


def _participantes_md(dados: dict) -> list[str]:
    linhas = [
        "## Participantes",
        "",
        "| ID | Gladiador | Grupo | Classe | Nível | OP | HP | MP | ST | MG | AG | DF | Build "
        "| Skills | Passivas | Equipamento |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in sorted(dados["participantes"], key=lambda p: -p["op"]):
        equipamento = "; ".join(f"{pos}: {nome}" for pos, nome in p["equipamento"].items())
        linhas.append(
            f"| {p['id']} | {p['nome']} | {p['grupo']} | {p['classe_pt']} | {p['nivel']} "
            f"| {p['op']:.2f} | {p['hp']} | {p['mp']} | {p['st']} | {p['mg']} | {p['ag']} "
            f"| {p['df']} | {p['rotulo']}: {p['foco']} | {', '.join(p['deck'])} "
            f"| {_passivas_txt(p['passivas'])} | {equipamento} |"
        )
    return linhas + [""]


def _resultados_md(dados: dict, part: dict) -> list[str]:
    linhas = ["## Resultados por fase", ""]
    for fase, _, nome in FASES:
        da_fase = [j for j in dados["partidas"] if j["fase"] == fase]
        if not da_fase:
            continue
        linhas += [
            f"### {nome}",
            "",
            "| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for j in da_fase:
            p1, p2 = part[j["p1"]], part[j["p2"]]
            linhas.append(
                f"| {j['indice']} | {p1['nome']} ({p1['op']:.2f}) | {p2['nome']} "
                f"({p2['op']:.2f}) | **{part[j['vencedor']]['nome']}** | {j['rodadas']} "
                f"| {j['hp_vencedor']}/{j['hp_max_vencedor']} | {j['delta_op']:+.2f} "
                f"| {'sim' if j['zebra'] else ''} |"
            )
        linhas.append("")
    return linhas


def relatorio_md(dados: dict, copa) -> str:
    ag = dados["agregados"]
    part = {p["id"]: p for p in dados["participantes"]}
    campeao = part.get(dados["campeao"])
    final = next((j for j in dados["partidas"] if j["fase"] == "final"), None)
    linhas = [
        f"# {COPA} — 64 gladiadores",
        "",
        "Campeonato técnico da Arena PvP, gerado por `tools/arena_copa_02.py`. Experimento de "
        "diagnóstico do duelo sob uma política fixa.",
        "",
        f"> {AVISO_NOMES}",
        ">",
        f"> {AVISO_ESTATISTICA}",
        "",
        "## Resumo",
        "",
    ]
    if campeao and final:
        vice = part[final["perdedor"]]
        linhas += [
            f"- **Campeão: {campeao['nome']} ({campeao['id']})**, {campeao['classe_pt']} nível "
            f"{campeao['nivel']}, OP {campeao['op']:.2f}, build *{campeao['rotulo']}* "
            f"({campeao['foco']}).",
            f"- Vice: {vice['nome']} ({vice['id']}), {vice['classe_pt']} nível {vice['nivel']}, "
            f"OP {vice['op']:.2f}, build *{vice['rotulo']}*.",
        ]
    linhas += [
        f"- 64 participantes (22 Guerreiros, 21 Magos, 21 Ladinos); OP médio "
        f"{ag['op_medio']:.2f} (mínimo {ag['op_min']:.2f}, máximo {ag['op_max']:.2f}).",
        f"- 63 partidas, {ag['rodadas_total']} rodadas, {ag['golpes_total']} golpes "
        f"({ag['golpes_conectados']} conectados), {ag['criticos_total']} críticos.",
        f"- O favorito (OP maior) venceu {ag['favoritos']} das 63 partidas; houve "
        f"{len(ag['zebras'])} zebras.",
        "- As 63 partidas rodaram duas vezes, sem e com auditoria, e coincidiram em todas as "
        "verificações (tabela de auditoria resumida).",
        "",
        "Arquivos desta Copa: [`final_detalhada.md`](final_detalhada.md) (auditoria integral da "
        "final), [`final_trace.json`](final_trace.json), [`dashboard.html`](dashboard.html), "
        "[`relatorio_visual.pdf`](relatorio_visual.pdf) e [`calibracao.json`](calibracao.json).",
        "",
    ]
    linhas += _montagem_md()
    linhas += _calibracao_md(dados)
    linhas += _participantes_md(dados)
    linhas += ["## Chave", "", *_chave_md(dados, part), ""]
    linhas += _resultados_md(dados, part)
    linhas += _agregados_md(dados, part)
    linhas += [
        "## Auditoria resumida das 63 partidas",
        "",
        "Cada partida rodou sem instrumentação e auditada, com a mesma seed. As verificações são "
        "as da Copa 01: ações, ordem, leituras de iniciativa, passos, HP/MP por rodada, estado "
        "completo por rodada, eventos do motor, resultado, conclusividade e posição final do "
        "gerador; e a coerência do trace com o motor (sorteios classificados, contagem igual à "
        "do gerador, dano e MP por passo, ações executadas).",
        "",
        "| Partida | Seed | Rodadas | Sorteios | Fidelidade | Coerência |",
        "|---|---|---|---|---|---|",
    ]
    for j in dados["partidas"]:
        linhas.append(
            f"| {j['titulo']} | `{j['seed']}` | {j['rodadas']} | {j['sorteios']} "
            f"| {'idêntica' if j['fidelidade'] else 'DIVERGENTE'} "
            f"| {'ok' if j['coerencia'] else 'FALHOU'} |"
        )
    linhas += ["", "## As 63 partidas em detalhe", ""]
    for fase, _, nome in FASES:
        partidas = copa.fases.get(fase, ())
        if partidas:
            linhas += [f"### {nome}: detalhes", ""]
            for partida in partidas:
                bloco = _bloco_da_partida(partida)
                bloco[0] = "#" + bloco[0]
                linhas += bloco
    return "\n".join(linhas)


def _chave_md(dados: dict, part: dict) -> list[str]:
    linhas = ["```"]
    for fase, _, nome in FASES:
        da_fase = [j for j in dados["partidas"] if j["fase"] == fase]
        if not da_fase:
            continue
        linhas.append(nome)
        for j in da_fase:
            p1, p2 = part[j["p1"]], part[j["p2"]]
            linhas.append(
                f"  {j['indice']:>2}. {p1['nome']} ({p1['op']:.1f}) × {p2['nome']} "
                f"({p2['op']:.1f})  →  {part[j['vencedor']]['nome']}"
            )
    if dados["campeao"]:
        linhas.append(f"Campeão: {part[dados['campeao']]['nome']} ({dados['campeao']})")
    linhas.append("```")
    return linhas


def _classes_md(ag: dict) -> list[str]:
    linhas = [
        "### Desempenho por classe",
        "",
        "| Classe | Participantes | OP médio | Vitórias | Derrotas | Taxa | Dano por partida "
        "| Acerto | Críticos (taxa) | Cura total | Ações perdidas por controle |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for classe, c in ag["por_classe"].items():
        linhas.append(
            f"| {CLASSE[classe]} | {c['participantes']} | {c['op_medio']:.2f} | {c['vitorias']} "
            f"| {c['derrotas']} | {c['taxa']:.1%} | {c['dano_por_partida']:.0f} "
            f"| {c['acerto']:.1%} | {c['criticos']} ({c['taxa_critico']:.1%}) | {c['cura']} "
            f"| {c['perdidas_controle']} |"
        )
    linhas += [
        "",
        "Quantos de cada classe chegaram a cada fase:",
        "",
        "| Classe | " + " | ".join(nome for _, _, nome in FASES) + " | Campeão |",
        "|---|" + "---|" * (len(FASES) + 1),
    ]
    for classe, c in ag["por_classe"].items():
        linhas.append(
            f"| {CLASSE[classe]} | "
            + " | ".join(str(c["alcancou"][f]) for f, _, _ in FASES)
            + f" | {'sim' if c['campeao'] else ''} |"
        )
    linhas += [
        "",
        "Vitórias da classe da linha sobre a da coluna:",
        "",
        "| Vencedor \\ Perdedor | " + " | ".join(CLASSE[c] for c in CLASSES) + " |",
        "|---|---|---|---|",
    ]
    for c in CLASSES:
        linhas.append(
            f"| {CLASSE[c]} | " + " | ".join(str(ag["matriz"][c][d]) for d in CLASSES) + " |"
        )
    return linhas + [""]


def _op_md(ag: dict, part: dict) -> list[str]:
    linhas = [
        "### Overall Power dos vencedores por fase",
        "",
        "| Fase | Partidas | OP médio de quem entrou (mín–máx) | OP médio dos vencedores "
        "(mín–máx) | OP médio dos perdedores | Favorito venceu |",
        "|---|---|---|---|---|---|",
    ]
    for f in ag["op_por_fase"]:
        e, v, p = f["entrando"], f["vencedores"], f["perdedores"]
        linhas.append(
            f"| {f['nome']} | {f['partidas']} | {e[0]:.2f} ({e[1]:.2f}–{e[2]:.2f}) "
            f"| {v[0]:.2f} ({v[1]:.2f}–{v[2]:.2f}) | {p[0]:.2f} "
            f"| {f['favorito_venceu']}/{f['partidas']} |"
        )
    linhas += ["", "### Confrontos com as maiores diferenças de OP", ""]
    linhas += _tabela_resumos(ag["maiores_diferencas"], part)
    linhas += ["", f"### Vitórias de quem tinha o OP menor ({len(ag['zebras'])} zebras)", ""]
    linhas += _tabela_resumos(ag["zebras"], part) if ag["zebras"] else ["Nenhuma."]
    linhas += [
        "",
        "Vencedor × perdedor por faixa medida (1 = 20–22,5 … 4 = 27,5–30): "
        + ", ".join(f"{v}→{p}: {n}" for v, p, n in ag["faixa_contra_faixa"]),
        "",
    ]
    return linhas


def _golpes_md(dados: dict, ag: dict, part: dict) -> list[str]:
    jogos = {j["chave"]: j for j in dados["partidas"]}
    linhas = [
        "### Maiores golpes",
        "",
        "| Dano | Crítico | Atacante | Alvo | Ação | Partida | Rodada |",
        "|---|---|---|---|---|---|---|",
    ]
    for g in ag["maiores_golpes"]:
        linhas.append(
            f"| {g['dano']} | {'sim' if g['critico'] else ''} | {_n(g['atacante'], part)} "
            f"| {_n(g['defensor'], part)} | {g['acao']} | {jogos[g['chave']]['titulo']} "
            f"| {g['rodada']} |"
        )
    mc = ag["maior_critico"]
    maior = (
        f"; o maior, {mc['dano']} de dano de {_n(mc['atacante'], part)} ({mc['acao']})"
        if mc
        else ""
    )
    linhas += [
        "",
        f"Críticos: {ag['criticos_total']} em {ag['golpes_conectados']} golpes conectados{maior}.",
        "",
        "### Partidas mais longas e mais curtas",
        "",
        "Mais longas: "
        + "; ".join(f"{r['titulo']} ({r['rodadas']} rodadas)" for r in ag["longas"]),
        "",
        "Mais curtas: "
        + "; ".join(f"{r['titulo']} ({r['rodadas']} rodadas)" for r in ag["curtas"]),
        "",
        "Rodadas por partida: "
        + ", ".join(f"{k}: {v}" for k, v in ag["rodadas_hist"].items())
        + ".",
        "",
    ]
    return linhas


def _efeitos_md(ag: dict, part: dict) -> list[str]:
    def lista(pares):
        return ", ".join(f"{s} ×{n}" for s, n in pares) or "nenhum"

    return [
        "### Uso de skills, buffs, controles e curas",
        "",
        f"Skills mais usadas: {lista(ag['skills'][:15])}.",
        "",
        f"Buffs ativados: {lista(ag['buffs'])}.",
        "",
        f"Status aplicados: {lista(ag['status_aplicados'])}. Tentativas que não pegaram: "
        f"{lista(ag['status_falhos'])}.",
        "",
        "Controles que tiram a vez (atordoar, sono, congelar) aplicados: "
        f"{lista(ag['controles'].items())}; ações perdidas por controle no total: "
        f"{ag['perdidas_controle']}.",
        "",
        f"Cura total (skill + roubo de vida): {ag['cura_total']}. Quem mais curou: "
        + ", ".join(f"{_n(pid, part)} {n}" for pid, n in ag["curas"])
        + ".",
        "",
        "Critério que decidiu a ordem, por rodada: "
        + ", ".join(f"{k} ×{v}" for k, v in ag["criterios"].items())
        + ".",
        "",
    ]


def _agregados_md(dados: dict, part: dict) -> list[str]:
    ag = dados["agregados"]
    linhas = ["## Estatísticas agregadas", "", f"> {AVISO_ESTATISTICA}", ""]
    linhas += _classes_md(ag)
    linhas += _op_md(ag, part)
    linhas += _golpes_md(dados, ag, part)
    linhas += _efeitos_md(ag, part)
    linhas += [
        "### Quem mais eliminou",
        "",
        "| Gladiador | Classe | OP | Vitórias | Fase alcançada |",
        "|---|---|---|---|---|",
    ]
    for pid, vitorias in ag["eliminacoes"]:
        p = part[pid]
        alcance = "Campeão" if p["campeao"] else NOME_DA_FASE[p["fase"]]
        linhas.append(
            f"| {p['nome']} ({pid}) | {p['classe_pt']} | {p['op']:.2f} | {vitorias} | {alcance} |"
        )
    linhas += ["", *_campeao_md(dados, part), "", "## Curiosidades", ""]
    linhas += [f"- {frase}" for frase in ag["curiosidades"]]
    return linhas + [""]


def _tabela_resumos(resumos: list[dict], part: dict) -> list[str]:
    linhas = [
        "| Partida | Vencedor (OP) | Perdedor (OP) | ΔOP | Rodadas |",
        "|---|---|---|---|---|",
    ]
    for r in resumos:
        v, p = part[r["vencedor"]], part[r["perdedor"]]
        linhas.append(
            f"| {r['titulo']} | {v['nome']} ({v['op']:.2f}) | {p['nome']} ({p['op']:.2f}) "
            f"| {r['delta_op']:+.2f} | {r['rodadas']} |"
        )
    return linhas


def _trajetoria(dados: dict) -> list[tuple[dict, str]]:
    campeao = dados["campeao"]
    return [
        (j, "p1" if j["p1"] == campeao else "p2")
        for j in dados["partidas"]
        if campeao in (j["p1"], j["p2"])
    ]


def _campeao_md(dados: dict, part: dict) -> list[str]:
    campeao = part.get(dados["campeao"])
    if campeao is None:
        return ["## O campeão", "", "Sem campeão: a Copa foi interrompida."]
    linhas = [
        "## O campeão",
        "",
        f"**{campeao['nome']} ({campeao['id']})**, {campeao['classe_pt']} nível "
        f"{campeao['nivel']}, OP {campeao['op']:.2f} (faixa {campeao['faixa_medida']}), build "
        f"*{campeao['rotulo']}*: {campeao['foco']}.",
        "",
        f"- Skills: {', '.join(campeao['deck'])}",
        f"- Passivas: {_passivas_txt(campeao['passivas'])}",
        "- Equipamento: " + "; ".join(f"{p}: {n}" for p, n in campeao["equipamento"].items()),
        f"- HP {campeao['hp']}, MP {campeao['mp']}, ST {campeao['st']}, MG {campeao['mg']}, "
        f"AG {campeao['ag']}, DF {campeao['df']}",
        "",
        "| Fase | Adversário (OP) | Rodadas | Dano causado | Dano recebido | Cura | MP "
        "| Acertos/erros | Críticos | HP final |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    total = Counter()
    for j, lado in _trajetoria(dados):
        e, o = j["lados"][lado], j["lados"][opponent_of(lado)]
        rival = part[j[opponent_of(lado)]]
        for k in ("dano", "cura", "mp", "acertos", "erros", "criticos", "skills", "basicos"):
            total[k] += e[k]
        total["recebido"] += o["dano"]
        total["rodadas"] += j["rodadas"]
        linhas.append(
            f"| {j['nome_fase']} | {rival['nome']} ({rival['op']:.2f}) | {j['rodadas']} "
            f"| {e['dano']} | {o['dano']} | {e['cura']} | {e['mp']} | {e['acertos']}/{e['erros']} "
            f"| {e['criticos']} | {j['hp_vencedor']}/{j['hp_max_vencedor']} |"
        )
    linhas += [
        "",
        f"Totais: {total['rodadas']} rodadas, {total['dano']} de dano causado, "
        f"{total['recebido']} recebido, {total['cura']} de cura, {total['mp']} de MP, "
        f"{total['skills']} skills e {total['basicos']} ataques básicos, {total['acertos']} "
        f"acertos, {total['erros']} erros, {total['criticos']} críticos.",
    ]
    return linhas


# --- SVG -----------------------------------------------------------------------

COR = {"Warrior": "var(--c-warrior)", "Mage": "var(--c-mage)", "Rogue": "var(--c-rogue)"}
FONTE = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'


def _e(texto) -> str:
    return html.escape(str(texto), quote=True)


def _caixa_da_chave(jogo: dict, part: dict, x: float, cy: float, largura: int, alto: int) -> str:
    y = cy - alto / 2
    dica = f"{jogo['titulo']} · {jogo['rodadas']} rodadas · vence {part[jogo['vencedor']]['nome']}"
    if jogo["zebra"]:
        dica += " (zebra)"
    classe_caixa = "caixa zebra" if jogo["zebra"] else "caixa"
    s = [
        f'<g class="jogo" data-jogo="{jogo["chave"]}" data-tip="{_e(dica)}" tabindex="0" '
        f'transform="translate({x:.1f},{y:.1f})">',
        f'<rect class="{classe_caixa}" width="{largura}" height="{alto}" rx="4"/>',
    ]
    for i, lado in enumerate(SIDES):
        p = part[jogo[lado]]
        ganhou = jogo["vencedor"] == p["id"]
        ty = 15 + i * 16
        tom = "t-primary" if ganhou else "t-muted"
        peso = 600 if ganhou else 400
        s.append(f'<circle cx="9" cy="{ty - 4}" r="4" fill="{COR[p["classe"]]}"/>')
        s.append(
            f'<text x="18" y="{ty}" class="{tom}" font-weight="{peso}">{_e(p["nome"][:18])}</text>'
        )
        s.append(
            f'<text x="{largura - 6}" y="{ty}" text-anchor="end" class="t-secondary" '
            f'font-variant-numeric="tabular-nums">{p["op"]:.1f}</text>'
        )
    s.append("</g>")
    return "".join(s)


def svg_chave(dados: dict) -> str:
    """A chave de 64 em duas metades espelhadas, com a final no centro."""
    part = {p["id"]: p for p in dados["participantes"]}
    jogos = {(j["fase"], j["indice"]): j for j in dados["partidas"]}
    fases = [f for f, _, _ in FASES]
    largura, alto, folga, passo, topo = 172, 38, 22, 46, 34
    altura = topo + 16 * passo + 20
    coluna = largura + folga
    total = coluna * 11 - folga
    centros = [[k * passo + passo / 2 + topo for k in range(16)]]
    for _ in range(4):
        ant = centros[-1]
        centros.append([(ant[2 * k] + ant[2 * k + 1]) / 2 for k in range(len(ant) // 2)])

    def x_de(c: int, lado: str) -> float:
        return c * coluna if lado == "esq" else total - largura - c * coluna

    s = [
        f'<svg class="chave" viewBox="0 0 {total} {altura}" width="{total}" height="{altura}" '
        f'role="img" aria-label="Chave eliminatória completa" {FONTE} font-size="11">'
    ]
    for c, fase in enumerate(fases[:5]):
        for lado in ("esq", "dir"):
            s.append(
                f'<text x="{x_de(c, lado) + largura / 2}" y="16" text-anchor="middle" '
                f'class="t-muted" font-weight="600">{_e(NOME_DA_FASE[fase])}</text>'
            )
    s.append(
        f'<text x="{total / 2}" y="16" text-anchor="middle" class="t-muted" '
        'font-weight="600">Final</text>'
    )
    for c, fase in enumerate(fases[:5]):
        n = len(centros[c]) * 2
        for i in range(n):
            lado = "esq" if i < n // 2 else "dir"
            k = i if lado == "esq" else i - n // 2
            jogo = jogos.get((fase, i + 1))
            if jogo is None:
                continue
            cy = centros[c][k]
            x = x_de(c, lado)
            if c > 0:
                a, b = centros[c - 1][2 * k], centros[c - 1][2 * k + 1]
                if lado == "esq":
                    xa = x_de(c - 1, lado) + largura
                    xm, xb = xa + folga / 2, x
                else:
                    xa = x_de(c - 1, lado)
                    xm, xb = xa - folga / 2, x + largura
                s.append(
                    f'<path class="ligacao" fill="none" '
                    f'd="M{xa},{a}H{xm}V{b}H{xa}M{xm},{cy}H{xb}"/>'
                )
            s.append(_caixa_da_chave(jogo, part, x, cy, largura, alto))
    final = jogos.get(("final", 1))
    if final is not None:
        cy = centros[4][0]
        xf = (total - largura) / 2
        s.append(
            f'<path class="ligacao" fill="none" d="M{x_de(4, "esq") + largura},{cy}H{xf}'
            f'M{xf + largura},{cy}H{x_de(4, "dir")}"/>'
        )
        s.append(_caixa_da_chave(final, part, xf, cy, largura, alto))
        campeao = part[final["vencedor"]]
        s.append(
            f'<text x="{total / 2}" y="{cy - 34}" text-anchor="middle" class="t-primary" '
            f'font-size="13" font-weight="700">Campeão: {_e(campeao["nome"])}</text>'
        )
        s.append(
            f'<text x="{total / 2}" y="{cy + 38}" text-anchor="middle" class="t-secondary">'
            f"{_e(campeao['classe_pt'])} · OP {campeao['op']:.2f} · {_e(campeao['rotulo'])}"
            "</text>"
        )
    s.append("</svg>")
    return "".join(s)


def _escala(lo: float, hi: float, marcas: int = 4) -> tuple[float, float, float, str]:
    """Uma escala de valores redondos (passos 1, 2, 2,5 ou 5 × 10^k) que cobre [lo, hi]."""
    bruto = (hi - lo) / marcas if hi > lo else 1.0
    potencia = 10 ** math.floor(math.log10(bruto))
    passo = next(m * potencia for m in (1, 2, 2.5, 5, 10) if m * potencia >= bruto)
    inicio = math.floor(lo / passo) * passo
    fim = math.ceil(hi / passo) * passo
    casas = max(0, -math.floor(math.log10(passo)) + (1 if passo / potencia == 2.5 else 0))
    return inicio, fim, passo, "{:." + str(casas) + "f}"


def _grade_y(x0, base, topo, inicio, fim, passo, largura, fmt) -> list[str]:
    s = []
    n = round((fim - inicio) / passo)
    for i in range(n + 1):
        v = inicio + i * passo
        y = base - (base - topo) * i / n
        s.append(f'<line class="grade" x1="{x0}" x2="{x0 + largura}" y1="{y:.1f}" y2="{y:.1f}"/>')
        s.append(
            f'<text x="{x0 - 6}" y="{y + 4:.1f}" text-anchor="end" class="t-muted" '
            f'font-variant-numeric="tabular-nums">{fmt.format(v)}</text>'
        )
    return s


def svg_dispersao_op(dados: dict) -> str:
    """OP do vencedor × OP do perdedor: acima da diagonal, a zebra."""
    part = {p["id"]: p for p in dados["participantes"]}
    w, h, m = 520, 400, 52
    lo, hi = 19.5, 30.5

    def px(v):
        return m + (v - lo) / (hi - lo) * (w - m - 16)

    def py(v):
        return h - m - (v - lo) / (hi - lo) * (h - m - 16)

    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="OP do vencedor contra OP do perdedor em cada partida" {FONTE} '
        'font-size="11">'
    ]
    for v in range(20, 31, 2):
        s.append(f'<line class="grade" x1="{px(v):.1f}" x2="{px(v):.1f}" y1="16" y2="{h - m}"/>')
        s.append(f'<line class="grade" x1="{m}" x2="{w - 16}" y1="{py(v):.1f}" y2="{py(v):.1f}"/>')
        s.append(
            f'<text x="{px(v):.1f}" y="{h - m + 16}" text-anchor="middle" '
            f'class="t-muted">{v}</text>'
        )
        s.append(
            f'<text x="{m - 8}" y="{py(v) + 4:.1f}" text-anchor="end" class="t-muted">{v}</text>'
        )
    s.append(
        f'<line class="eixo" x1="{px(lo):.1f}" y1="{py(lo):.1f}" '
        f'x2="{px(hi):.1f}" y2="{py(hi):.1f}"/>'
    )
    s.append(
        f'<text x="{px(20.2):.1f}" y="{py(29.6):.1f}" class="t-secondary">acima da diagonal: '
        "venceu o OP menor</text>"
    )
    s.append(
        f'<text x="{(w + m) / 2:.1f}" y="{h - 12}" text-anchor="middle" class="t-secondary">'
        "OP do vencedor</text>"
    )
    s.append(
        f'<text transform="translate(14,{(h - m) / 2:.1f}) rotate(-90)" text-anchor="middle" '
        'class="t-secondary">OP do perdedor</text>'
    )
    for j in dados["partidas"]:
        v, p = part[j["vencedor"]], part[j["perdedor"]]
        dica = f"{j['titulo']}: {v['nome']} {v['op']:.2f} venceu {p['nome']} {p['op']:.2f}"
        s.append(
            f'<circle class="ponto" data-jogo="{j["chave"]}" data-tip="{_e(dica)}" '
            f'cx="{px(v["op"]):.1f}" cy="{py(p["op"]):.1f}" r="5" fill="{COR[v["classe"]]}"/>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_op_por_fase(dados: dict) -> str:
    """OP médio de quem entrou em cada fase, com o mínimo e o máximo."""
    pontos = [(f["nome"], f["entrando"]) for f in dados["agregados"]["op_por_fase"]]
    campeao = next((p for p in dados["participantes"] if p["campeao"]), None)
    if campeao:
        pontos.append(("Campeão", [campeao["op"]] * 3))
    w, h, m = 560, 300, 48
    lo, hi = 20, 30

    def py(v):
        return h - 40 - (v - lo) / (hi - lo) * (h - 60)

    passo = (w - m - 70) / max(1, len(pontos) - 1)
    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="OP de quem entrou em cada fase" {FONTE} font-size="11">'
    ]
    s += _grade_y(m, h - 40, 20, lo, hi, 2, w - m - 10, "{:.0f}")
    caminho = []
    for i, (nome, (media, minimo, maximo)) in enumerate(pontos):
        x = m + 14 + i * passo
        s.append(
            f'<line class="faixa-linha" x1="{x:.1f}" x2="{x:.1f}" '
            f'y1="{py(minimo):.1f}" y2="{py(maximo):.1f}"/>'
        )
        caminho.append(f"{'M' if i == 0 else 'L'}{x:.1f},{py(media):.1f}")
        s.append(
            f'<text x="{x:.1f}" y="{h - 22}" text-anchor="middle" class="t-muted">{_e(nome)}</text>'
        )
    s.append(f'<path class="linha-1" d="{"".join(caminho)}" fill="none"/>')
    for i, (nome, (media, minimo, maximo)) in enumerate(pontos):
        x = m + 14 + i * passo
        dica = f"{nome}: média {media:.2f}, mínimo {minimo:.2f}, máximo {maximo:.2f}"
        s.append(
            f'<circle class="ponto-1" data-tip="{_e(dica)}" cx="{x:.1f}" '
            f'cy="{py(media):.1f}" r="5"/>'
        )
        s.append(
            f'<text x="{x + 8:.1f}" y="{py(media) - 8:.1f}" class="t-secondary">{media:.1f}</text>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_barras(itens: list[tuple], *, largura=560, rotulo_w=180, fmt="{:.0f}") -> str:
    """Barras horizontais: (rótulo, valor, cor, dica). Valor na ponta."""
    alto = 18
    h = len(itens) * (alto + 8) + 8
    maximo = max((v for _, v, _, _ in itens), default=1) or 1
    util = largura - rotulo_w - 60
    s = [f'<svg viewBox="0 0 {largura} {h}" width="100%" role="img" {FONTE} font-size="11">']
    for i, (rotulo, valor, cor, dica) in enumerate(itens):
        y = 4 + i * (alto + 8)
        comp = max(6.0, valor / maximo * util)
        s.append(
            f'<text x="{rotulo_w - 8}" y="{y + 13}" text-anchor="end" class="t-secondary">'
            f"{_e(rotulo)}</text>"
        )
        s.append(
            f'<path data-tip="{_e(dica)}" class="barra" fill="{cor}" '
            f'd="M{rotulo_w},{y}h{comp - 4:.1f}a4,4 0 0 1 4,4v{alto - 8}a4,4 0 0 1 -4,4'
            f'h-{comp - 4:.1f}z"/>'
        )
        s.append(
            f'<text x="{rotulo_w + comp + 6:.1f}" y="{y + 13}" class="t-primary" '
            f'font-variant-numeric="tabular-nums">{fmt.format(valor)}</text>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_linhas(series: list[tuple], rotulos_x: list[str], *, titulo: str, fmt="{:.0f}") -> str:
    """Duas séries numa escala só, com legenda e rótulo no fim de cada linha."""
    largura, altura, m, direita = 560, 280, 64, 120
    valores = [v for _, vs, _ in series for v in vs]
    lo, hi, marca, fmt_eixo = _escala(min(valores), max(valores))
    util_w = largura - m - direita
    passo = util_w / max(1, len(rotulos_x) - 1)

    def py(v):
        return altura - 40 - (v - lo) / (hi - lo) * (altura - 74)

    s = [
        f'<svg viewBox="0 0 {largura} {altura}" width="100%" role="img" '
        f'aria-label="{_e(titulo)}" {FONTE} font-size="11">'
    ]
    s += _grade_y(m, altura - 40, 34, lo, hi, marca, util_w, fmt_eixo)
    pula = max(1, round(len(rotulos_x) / 12))
    for i, r in enumerate(rotulos_x):
        if i % pula and i != len(rotulos_x) - 1:
            continue
        s.append(
            f'<text x="{m + i * passo:.1f}" y="{altura - 22}" text-anchor="middle" '
            f'class="t-muted">{_e(r)}</text>'
        )
    fins = [py(vs[-1]) for _, vs, _ in series]
    juntos = len(fins) > 1 and abs(fins[0] - fins[-1]) < 14
    for k, (nome, vs, cor) in enumerate(series):
        d = "".join(
            f"{'M' if i == 0 else 'L'}{m + i * passo:.1f},{py(v):.1f}" for i, v in enumerate(vs)
        )
        s.append(
            f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i, v in enumerate(vs):
            dica = f"{nome}, {rotulos_x[i]}: {fmt.format(v)}"
            s.append(
                f'<circle class="marcador" data-tip="{_e(dica)}" cx="{m + i * passo:.1f}" '
                f'cy="{py(v):.1f}" r="4" fill="{cor}"/>'
            )
        deslocamento = (k * 2 - 1) * 8 if juntos else 0
        s.append(
            f'<text x="{m + (len(vs) - 1) * passo + 10:.1f}" '
            f'y="{py(vs[-1]) + 4 + deslocamento:.1f}" class="t-secondary">{_e(nome)}</text>'
        )
    x = m
    for nome, _, cor in series:
        s.append(f'<rect x="{x}" y="8" width="14" height="4" rx="2" fill="{cor}"/>')
        s.append(f'<text x="{x + 20}" y="14" class="t-secondary">{_e(nome)}</text>')
        x += 36 + len(nome) * 7
    s.append("</svg>")
    return "".join(s)


def svg_colunas(contagem: dict, *, titulo: str) -> str:
    """Colunas de uma série só: rodadas por partida."""
    largura, altura, m = 560, 220, 40
    chaves = sorted(int(k) for k in contagem)
    valores = [contagem.get(k, contagem.get(str(k), 0)) for k in chaves]
    _, maximo, marca, fmt_eixo = _escala(0, max(valores) or 1)
    marca = max(1, marca)
    util = largura - m - 10
    banda = util / len(chaves)
    barra = min(24.0, banda - 4)
    base = altura - 30
    s = [
        f'<svg viewBox="0 0 {largura} {altura}" width="100%" role="img" '
        f'aria-label="{_e(titulo)}" {FONTE} font-size="11">'
    ]
    s += _grade_y(m, base, 16, 0, maximo, marca, util, "{:.0f}")
    for i, (k, v) in enumerate(zip(chaves, valores)):
        x = m + i * banda + (banda - barra) / 2
        alt = v / maximo * (base - 16)
        if v:
            s.append(
                f'<path data-tip="{k} rodadas: {v} partida(s)" class="barra" '
                f'fill="var(--c-serie)" d="M{x:.1f},{base}v-{max(0.0, alt - 4):.1f}'
                f'a4,4 0 0 1 4,-4h{barra - 8:.1f}a4,4 0 0 1 4,4v{max(0.0, alt - 4):.1f}z"/>'
            )
            s.append(
                f'<text x="{x + barra / 2:.1f}" y="{base - alt - 4:.1f}" text-anchor="middle" '
                f'class="t-secondary">{v}</text>'
            )
        s.append(
            f'<text x="{x + barra / 2:.1f}" y="{altura - 14}" text-anchor="middle" '
            f'class="t-muted">{k}</text>'
        )
    s.append("</svg>")
    return "".join(s)


def graficos(dados: dict) -> dict:
    ag = dados["agregados"]
    part = {p["id"]: p for p in dados["participantes"]}
    classes = []
    for c in CLASSES:
        v = ag["por_classe"][c]
        dica = f"{CLASSE[c]}: {v['vitorias']} vitórias em {v['partidas']} partidas"
        classes.append((CLASSE[c], v["vitorias"], COR[c], dica))
    golpes = []
    for g in ag["maiores_golpes"]:
        atacante = part[g["atacante"]]
        dica = f"{g['dano']} de dano em {part[g['defensor']]['nome']}"
        if g["critico"]:
            dica += " (crítico)"
        rotulo = f"{atacante['nome']} · {g['acao']}"[:34] + (" · crítico" if g["critico"] else "")
        golpes.append((rotulo, g["dano"], COR[atacante["classe"]], dica))
    skills = [(nome, n, "var(--c-serie)", f"{nome}: {n} usos") for nome, n in ag["skills"][:12]]
    saida = {
        "chave": svg_chave(dados),
        "dispersao": svg_dispersao_op(dados),
        "op_por_fase": svg_op_por_fase(dados),
        "classes": svg_barras(classes, rotulo_w=110),
        "golpes": svg_barras(golpes, rotulo_w=250),
        "skills": svg_barras(skills, rotulo_w=190),
        "rodadas": svg_colunas(ag["rodadas_hist"], titulo="Rodadas por partida"),
        "final_iniciativa": "",
        "final_hp": "",
    }
    final = dados.get("final")
    if final:
        nomes = {lado: part[final["ids"][lado]]["nome"] for lado in SIDES}
        cores = {lado: COR[part[final["ids"][lado]]["classe"]] for lado in SIDES}
        if cores["p1"] == cores["p2"]:
            cores["p2"] = "var(--c-neutra)"
        scores = [
            (nomes[lado], [leit[lado]["score"] for _, leit in final["iniciativa"]], cores[lado])
            for lado in SIDES
        ]
        saida["final_iniciativa"] = svg_linhas(
            scores,
            [str(n) for n, _ in final["iniciativa"]],
            titulo="Initiative Score por rodada",
            fmt="{:.4f}",
        )
        hp = [(nomes[lado], [r[lado] for r in final["hp"]], cores[lado]) for lado in SIDES]
        saida["final_hp"] = svg_linhas(
            hp,
            [str(i) for i in range(len(final["hp"]))],
            titulo="HP ao fim de cada rodada (0 = início)",
        )
    return saida


# --- HTML ----------------------------------------------------------------------


def _recurso(nome: str) -> str:
    return (RECURSOS / nome).read_text(encoding="utf-8")


def _preencher(modelo_html: str, valores: dict) -> str:
    saida = modelo_html
    for chave, valor in valores.items():
        saida = saida.replace(f"@@{chave}@@", valor)
    restantes = [p for p in saida.split("@@")[1::2] if p.isidentifier()]
    reservados = {"js", "dados"}
    if set(restantes) - reservados:
        raise KeyError(f"marcadores sem valor: {sorted(set(restantes) - reservados)}")
    return saida


def _texto(frase: str) -> str:
    """Escapa e transforma `trecho` em <code>trecho</code>."""
    partes = _e(frase).split("`")
    return "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(partes))


def _lista_diagnostico(itens) -> str:
    saida = []
    for nivel, texto in itens:
        estilo = ' style="margin-left:1.4em;list-style:circle"' if nivel else ""
        saida.append(f"<li{estilo}>{_texto(texto)}</li>")
    return "".join(saida)


def _dot(classe: str) -> str:
    return f'<span class="dot" style="background:{COR[classe]}"></span>'


def _kpis(ag: dict, campeao: dict | None) -> str:
    itens = [
        (
            "Campeão",
            campeao["nome"] if campeao else "—",
            f"{campeao['classe_pt']} · OP {campeao['op']:.2f}" if campeao else "",
        ),
        ("OP médio", f"{ag['op_medio']:.2f}", f"de {ag['op_min']:.2f} a {ag['op_max']:.2f}"),
        ("Partidas", "63", f"{ag['rodadas_total']} rodadas"),
        ("Zebras", str(len(ag["zebras"])), f"favorito venceu {ag['favoritos']}"),
        ("Golpes conectados", str(ag["golpes_conectados"]), f"de {ag['golpes_total']} tentados"),
        ("Críticos", str(ag["criticos_total"]), "em golpes conectados"),
    ]
    return "".join(
        f'<div class="card kpi"><div class="sec">{_e(r)}</div><div class="kv">{_e(v)}</div>'
        f'<div class="muted">{_e(d)}</div></div>'
        for r, v, d in itens
    )


def _linhas_classe(ag: dict, *, com_fases: bool) -> str:
    linhas = []
    for c, v in ag["por_classe"].items():
        celulas = [
            f"<td>{_dot(c)}{CLASSE[c]}</td>",
            f"<td class=n>{v['participantes']}</td>",
            f"<td class=n>{v['op_medio']:.2f}</td>",
            f"<td class=n>{v['vitorias']}</td>",
            f"<td class=n>{v['derrotas']}</td>",
            f"<td class=n>{v['taxa']:.1%}</td>",
            f"<td class=n>{v['dano_por_partida']:.0f}</td>",
            f"<td class=n>{v['acerto']:.1%}</td>",
            f"<td class=n>{v['criticos']}</td>",
        ]
        if com_fases:
            celulas.append(f"<td class=n>{v['alcancou']['oitavas']}</td>")
            celulas.append(f"<td class=n>{v['alcancou']['quartas']}</td>")
        linhas.append("<tr>" + "".join(celulas) + "</tr>")
    return "".join(linhas)


def _legenda() -> str:
    return " ".join(f"{_dot(c)}{CLASSE[c]}" for c in CLASSES)


def _final_html(dados: dict, svgs: dict, part: dict) -> str:
    final = dados.get("final")
    if not final:
        return "<p>Sem final: a Copa foi interrompida.</p>"
    d = final["decisivo"]
    nomes = {lado: _e(part[final["ids"][lado]]["nome"]) for lado in SIDES}
    if d:
        decisivo = (
            f"Rodada {d['rodada']}: {_e(part[d['atacante']]['nome'])} causou "
            f"<b>{d['dano']}</b> de dano{' (crítico)' if d['critico'] else ''}, levando o alvo "
            f"de {d['hp_antes']} a {d['hp_depois']} de HP. BASE {d['base']}, fator de defesa "
            f"{d['fator_defesa']:.6f}, funil {d['funil_final']}."
        )
    else:
        decisivo = "Sem golpe letal registrado."
    n_fid = len(final["fidelidade"])
    fid = all(ok for _, ok in final["fidelidade"])
    fidelidade = f"idêntica nas {n_fid} verificações" if fid else "DIVERGENTE"
    rolagens = ", ".join(f"{k} ×{v}" for k, v in final["rolagens"].items())
    diagnostico = _lista_diagnostico(final["diagnostico"])
    return f"""
<div class="grid2">
 <div class="card"><h3>Initiative Score por rodada</h3>{svgs["final_iniciativa"]}
  <p class="muted">A ordem de cada rodada sai da comparação destes floats crus; as seis
  parcelas estão na tabela abaixo e na transcrição.</p></div>
 <div class="card"><h3>HP ao fim de cada rodada (0 = início)</h3>{svgs["final_hp"]}</div>
</div>
<div class="card"><h3>Golpe decisivo</h3><p>{decisivo}</p>
 <p class="sec">Sorteios da final: {final["sorteios"]} ({_e(rolagens)}). Execução com × sem
 auditoria: {fidelidade}.</p>
 <p><a href="final_detalhada.md">Auditoria integral da final (final_detalhada.md)</a> ·
 <a href="final_trace.json">trace estruturado (final_trace.json)</a></p></div>
<div class="card"><h3>Diagnóstico (interpretação, separada dos fatos)</h3>
 <ul>{diagnostico}</ul></div>
<div class="card"><h3>Parcelas da iniciativa por rodada</h3>
 <div class="rolagem" id="tabela-iniciativa"></div></div>
<div class="card" id="final-partida"></div>
<p class="muted">Lados da final: p1 = {nomes["p1"]}, p2 = {nomes["p2"]}.</p>
"""


def dashboard_html(dados: dict, svgs: dict) -> str:
    part = {p["id"]: p for p in dados["participantes"]}
    ag = dados["agregados"]
    eliminacoes = []
    for pid, v in ag["eliminacoes"]:
        p = part[pid]
        alcance = "Campeão" if p["campeao"] else _e(NOME_DA_FASE[p["fase"]])
        eliminacoes.append(
            f"<tr><td>{_dot(p['classe'])}{_e(p['nome'])} <span class=muted>{pid}</span></td>"
            f"<td class=n>{p['op']:.2f}</td><td class=n>{v}</td><td>{alcance}</td></tr>"
        )
    matriz = "".join(
        f"<tr><th>{_dot(c)}{CLASSE[c]}</th>"
        + "".join(f"<td class=n>{ag['matriz'][c][d]}</td>" for d in CLASSES)
        + "</tr>"
        for c in CLASSES
    )

    def lista(pares):
        return _e(", ".join(f"{s} ×{n}" for s, n in pares) or "nenhum")

    efeitos = (
        f"<p><b>Status aplicados:</b> {lista(ag['status_aplicados'])}</p>"
        f"<p><b>Tentativas de status que não pegaram:</b> {lista(ag['status_falhos'])}</p>"
        f"<p><b>Buffs ativados:</b> {lista(ag['buffs'][:14])}</p>"
        f"<p><b>Controles que tiram a vez:</b> {lista(ag['controles'].items())}; "
        f"ações perdidas por controle: {ag['perdidas_controle']}.</p>"
        f"<p><b>Cura total:</b> {ag['cura_total']}. <b>Critério da ordem por rodada:</b> "
        f"{lista(ag['criterios'].items())}.</p>"
    )
    valores = {
        "estilo": _recurso("estilo.css"),
        "aviso": _e(AVISO_NOMES),
        "aviso_estatistica": _e(AVISO_ESTATISTICA),
        "kpis": _kpis(ag, part.get(dados["campeao"])),
        "svg_dispersao": svgs["dispersao"],
        "svg_op_por_fase": svgs["op_por_fase"],
        "svg_classes": svgs["classes"],
        "svg_chave": svgs["chave"],
        "svg_golpes": svgs["golpes"],
        "svg_skills": svgs["skills"],
        "svg_rodadas": svgs["rodadas"],
        "legenda_classes": _legenda(),
        "curiosidades": "".join(f"<li>{_texto(f)}</li>" for f in ag["curiosidades"]),
        "opcoes_fase": "".join(f'<option value="{f}">{_e(n)}</option>' for f, _, n in FASES),
        "opcoes_classe": "".join(f'<option value="{c}">{CLASSE[c]}</option>' for c in CLASSES),
        "linhas_classe": _linhas_classe(ag, com_fases=True),
        "cabecalho_matriz": "".join(f"<th class=n>{CLASSE[c]}</th>" for c in CLASSES),
        "linhas_matriz": matriz,
        "linhas_eliminacoes": "".join(eliminacoes),
        "resumo_efeitos": efeitos,
        "final": _final_html(dados, svgs, part),
    }
    pagina = _preencher(_recurso("dashboard.html"), valores)
    # O script e os dados entram por último: nenhum marcador é procurado dentro deles.
    payload = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pagina = pagina.replace("@@js@@", _recurso("dashboard.js"))
    return pagina.replace("@@dados@@", payload)


def _linhas_participantes(lista: list[dict]) -> str:
    linhas = []
    for p in lista:
        resultado = "Campeão" if p["campeao"] else _e(NOME_DA_FASE[p["fase"]])
        linhas.append(
            f"<tr><td>{p['id']}</td><td>{_dot(p['classe'])}{_e(p['nome'])}</td>"
            f"<td>{p['classe_pt']}</td><td class=n>{p['nivel']}</td><td class=n>{p['op']:.2f}</td>"
            f"<td class=n>{p['hp']}</td><td class=n>{p['mp']}</td><td class=n>{p['st']}</td>"
            f"<td class=n>{p['mg']}</td><td class=n>{p['ag']}</td><td class=n>{p['df']}</td>"
            f"<td>{_e(p['rotulo'])}</td><td>{_e(', '.join(p['deck']))}</td>"
            f"<td class=n>{p['vitorias']}</td><td>{resultado}</td></tr>"
        )
    return "".join(linhas)


def _gladiador_html(p: dict) -> str:
    return f"{_dot(p['classe'])}{_e(p['nome'])} <span class=muted>{p['op']:.2f}</span>"


def _linhas_resultados(dados: dict, part: dict) -> list[str]:
    blocos = []
    for fase, _, nome in FASES:
        jogos = [j for j in dados["partidas"] if j["fase"] == fase]
        linhas = [f"<tr><th colspan=7>{_e(nome)}</th></tr>"]
        for j in jogos:
            zebra = ' <span class="tag z">zebra</span>' if j["zebra"] else ""
            linhas.append(
                f"<tr><td>{j['indice']}</td><td>{_gladiador_html(part[j['p1']])}</td>"
                f"<td>{_gladiador_html(part[j['p2']])}</td>"
                f"<td><b>{_e(part[j['vencedor']]['nome'])}</b>{zebra}</td>"
                f"<td class=n>{j['rodadas']}</td>"
                f"<td class=n>{j['hp_vencedor']}/{j['hp_max_vencedor']}</td>"
                f"<td class=n>{j['delta_op']:+.2f}</td></tr>"
            )
        blocos.append("".join(linhas))
    return blocos


def _trajetoria_html(dados: dict, part: dict) -> str:
    linhas = []
    for j, lado in _trajetoria(dados):
        e = j["lados"][lado]
        recebido = j["lados"][opponent_of(lado)]["dano"]
        linhas.append(
            f"<tr><td>{_e(j['nome_fase'])}</td>"
            f"<td>{_gladiador_html(part[j[opponent_of(lado)]])}</td>"
            f"<td class=n>{j['rodadas']}</td><td class=n>{e['dano']}</td>"
            f"<td class=n>{recebido}</td>"
            f"<td class=n>{e['cura']}</td><td class=n>{e['acertos']}/{e['erros']}</td>"
            f"<td class=n>{e['criticos']}</td>"
            f"<td class=n>{j['hp_vencedor']}/{j['hp_max_vencedor']}</td></tr>"
        )
    return "".join(linhas)


def visual_html(dados: dict, svgs: dict) -> str:
    """A página que o Chromium imprime: A4 paisagem, com a chave em A2 paisagem."""
    part = {p["id"]: p for p in dados["participantes"]}
    ag = dados["agregados"]
    ordenados = sorted(dados["participantes"], key=lambda p: -p["op"])
    resultados = _linhas_resultados(dados, part)
    zebras = "".join(
        f"<tr><td>{_e(r['nome_fase'])}</td><td>{_gladiador_html(part[r['vencedor']])}</td>"
        f"<td>{_gladiador_html(part[r['perdedor']])}</td>"
        f"<td class=n>{r['delta_op']:.2f}</td><td class=n>{r['rodadas']}</td></tr>"
        for r in ag["zebras"][:16]
    )
    final = dados.get("final") or {}
    d = final.get("decisivo")
    decisivo = "—"
    if d:
        decisivo = (
            f"Rodada {d['rodada']}: {_e(part[d['atacante']]['nome'])} causou {d['dano']} de dano"
            f"{' (crítico)' if d['critico'] else ''}, levando o alvo de {d['hp_antes']} a "
            f"{d['hp_depois']} de HP (BASE {d['base']}, fator de defesa {d['fator_defesa']:.6f}, "
            f"funil {d['funil_final']})."
        )
    cab_participantes = (
        "<thead><tr><th>ID</th><th>Gladiador</th><th>Classe</th><th class=n>Nv</th>"
        "<th class=n>OP</th><th class=n>HP</th><th class=n>MP</th><th class=n>ST</th>"
        "<th class=n>MG</th><th class=n>AG</th><th class=n>DF</th><th>Build</th><th>Skills</th>"
        "<th class=n>V</th><th>Resultado</th></tr></thead>"
    )
    cab_resultados = (
        "<thead><tr><th>#</th><th>Lado 1</th><th>Lado 2</th><th>Vencedor</th>"
        "<th class=n>Rod.</th><th class=n>HP</th><th class=n>ΔOP</th></tr></thead>"
    )
    subtitulo = (
        f"Mata-mata MD1 de 64 gladiadores de OP 20 a 30 na Arena PvP do ToJ · seed "
        f"{SEMENTE_PRINCIPAL} · 63 partidas reais do motor, cada uma repetida sem e com auditoria."
    )
    valores = {
        "estilo": _recurso("estilo.css"),
        "subtitulo": _e(subtitulo),
        "kpis": _kpis(ag, part.get(dados["campeao"])),
        "svg_dispersao": svgs["dispersao"],
        "svg_op_por_fase": svgs["op_por_fase"],
        "legenda_classes": _legenda(),
        "linhas_classe": _linhas_classe(ag, com_fases=False),
        "aviso": _e(f"{AVISO_NOMES} {AVISO_ESTATISTICA}"),
        "svg_chave": svgs["chave"],
        "cabecalho_participantes": cab_participantes,
        "participantes_1": _linhas_participantes(ordenados[:32]),
        "participantes_2": _linhas_participantes(ordenados[32:]),
        "cabecalho_resultados": cab_resultados,
        "resultados_1": "".join(resultados[:1]),
        "resultados_2": "".join(resultados[1:]),
        "svg_golpes": svgs["golpes"],
        "svg_rodadas": svgs["rodadas"],
        "zebras": zebras,
        "svg_skills": svgs["skills"],
        "curiosidades": "".join(f"<li>{_texto(f)}</li>" for f in ag["curiosidades"]),
        "trajetoria": _trajetoria_html(dados, part),
        "svg_final_iniciativa": svgs["final_iniciativa"],
        "svg_final_hp": svgs["final_hp"],
        "decisivo": decisivo,
        "diagnostico": _lista_diagnostico(final.get("diagnostico", ())),
    }
    return _preencher(_recurso("visual.html"), valores)


def localizar_chromium() -> str | None:
    binario = os.environ.get("CHROMIUM") or shutil.which("chromium")
    if binario:
        return binario
    candidato = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")) / "chromium"
    return str(candidato) if candidato.exists() else None


def imprimir_pdf(pagina_html: str, destino: Path) -> str | None:
    """Imprime pelo Chromium headless. Devolve o motivo, se não der para imprimir."""
    binario = localizar_chromium()
    if not binario:
        return "Chromium não encontrado (defina CHROMIUM); PDF não gerado."
    with tempfile.TemporaryDirectory() as pasta:
        origem = Path(pasta) / "relatorio_visual.html"
        origem.write_text(pagina_html, encoding="utf-8")
        comando = [
            binario,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={destino}",
            origem.as_uri(),
        ]
        subprocess.run(comando, check=True, capture_output=True, timeout=240)
    return None


def escrever_tudo(copa, pasta: Path = PASTA_DE_SAIDA, *, pdf: bool = True) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    dados = modelo(copa)
    caminhos = [pasta / ARQUIVO_RELATORIO]
    caminhos[0].write_text(relatorio_md(dados, copa) + "\n", encoding="utf-8")
    if "final" in copa.fases:
        final = copa.fases["final"][0]
        caminhos.append(pasta / ARQUIVO_FINAL)
        caminhos[-1].write_text(relatorio_final(final, copa=COPA) + "\n", encoding="utf-8")
        caminhos.append(pasta / ARQUIVO_TRACE)
        trace = trace_json(final, copa=COPA, semente_principal=SEMENTE_PRINCIPAL)
        caminhos[-1].write_text(
            json.dumps(trace, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    svgs = graficos(dados)
    caminhos.append(pasta / ARQUIVO_DASHBOARD)
    caminhos[-1].write_text(dashboard_html(dados, svgs), encoding="utf-8")
    if pdf:
        motivo = imprimir_pdf(visual_html(dados, svgs), pasta / ARQUIVO_PDF)
        if motivo is None:
            caminhos.append(pasta / ARQUIVO_PDF)
        else:
            print(motivo)
    if (pasta / ARQUIVO_CALIBRACAO).exists():
        caminhos.append(pasta / ARQUIVO_CALIBRACAO)
    return caminhos
