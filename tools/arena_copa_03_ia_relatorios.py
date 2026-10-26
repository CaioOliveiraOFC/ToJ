"""Relatórios da Copa Arena 03 v2 — Inteligência Estratégica.

Lê a Copa nova (IA estratégica nos dois lados), a original reproduzida
(`PoliticaCopa`), as verificações da reprodução e os confrontos controlados, e
escreve em `reports/pvp/copa_03_ia/`:

- `relatorio.md`: a comparação obrigatória, os confrontos controlados, a
  economia de recursos, as builds e três lutas em detalhe;
- `decisoes.md`: onde a IA divergiu da `PoliticaCopa`, e por quê, com o que
  estava na tela no momento;
- `final_detalhada.md` e `final_trace.json`: a final, auditada, com as
  avaliações da IA a cada rodada;
- `dashboard.html` e `relatorio_visual.pdf`.

As duas Copas passam pelos MESMOS agregados (`arena_copa_03_relatorios.modelo`
e `arena_metricas_combate`): a comparação é feita com a mesma régua.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from src.mechanics.pvp_duel import SIDES
from tools import arena_copa_02_relatorios as c2
from tools import arena_copa_03_relatorios as c3r
from tools import arena_ia_estrategica as ia
from tools.arena_copa_02 import FASES
from tools.arena_copa_03 import PASTA as PASTA_ORIGINAL
from tools.arena_copa_03 import SEMENTE_PRINCIPAL, ler_gladiadores, todas
from tools.arena_copa_03_ia import COPA_IA, PASTA_IA
from tools.arena_copa_teste import relatorio_final, trace_json
from tools.arena_metricas_combate import MOTIVOS, ROTULO_DO_MOTIVO, metricas_da_partida, somar

ARQUIVO_RELATORIO = "relatorio.md"
ARQUIVO_DECISOES = "decisoes.md"
ARQUIVO_FINAL = "final_detalhada.md"
ARQUIVO_TRACE = "final_trace.json"
ARQUIVO_DASHBOARD = "dashboard.html"
ARQUIVO_PDF = "relatorio_visual.pdf"
ARQUIVO_CONFRONTOS = "confrontos.json"
ASSETS = Path(__file__).resolve().parent / "arena_copa_03_ia_assets"
NOME_DA_FASE = {f: nome for f, _, nome in FASES}
ARQUETIPOS = ("controle", "crítico", "defesa", "sustento")
POLITICAS_PT = {"offense": "ofensiva", "survival": "sobrevivência", "economy": "economia"}
MOTIVO_CURTO = {
    "mp": "MP insuficiente",
    "recarga": "recarga",
    "requisito": "requisito",
    "preferencia": "escolha",
}
TIPO_PT = {
    "damage": "dano",
    "heal": "cura",
    "buff": "buff",
    "status": "status",
    "damage_reduction": "redução de dano",
}
COR_ORIGINAL = "var(--c-neutra)"
COR_IA = "var(--c-serie)"
# Ranking Bradley-Terry da Copa 03 (todos contra todos com a `PoliticaCopa`).
ARQUIVO_RODIZIO = PASTA_ORIGINAL / "round_robin.json"


# --- números ----------------------------------------------------------------------


def _media(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def _pct(a: float, b: float) -> str:
    return f"{100 * a / b:.1f}%".replace(".", ",") if b else "—"


def _num(v, casas: int = 2) -> str:
    if isinstance(v, int):
        return f"{v:,}".replace(",", ".")
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _sinal(v: float) -> str:
    return ("+" if v >= 0 else "−") + _num(abs(v))


def _wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return 0.0, 0.0
    z, p = 1.96, k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centro - meia), min(1.0, centro + meia)


def _taxa(k: int, n: int) -> str:
    lo, hi = _wilson(k, n)
    return f"{_pct(k, n)} (IC 95% {_pct(lo, 1)}–{_pct(hi, 1)})"


# --- o modelo de dados ---------------------------------------------------------------


def _metricas(copa, herois: dict) -> dict:
    return {f"{p.fase}-{p.indice}": metricas_da_partida(p, herois) for p in todas(copa)}


def conducao(dados: dict, metricas: dict) -> dict:
    """Os totais de condução de uma Copa: o turno, o MP e o desperdício."""
    lados = [m for por_lado in metricas.values() for m in por_lado.values()]
    t = somar(lados)
    acoes = t["basicos"] + t["skills"]
    maiores = [m["max_basicos_seguidos"] for m in lados]
    jogos = dados["partidas"]
    golpes = [g for j in jogos for g in j["golpes"]]
    conectados = [g for g in golpes if not g["errou"]]
    return {
        "lados": len(lados),
        "acoes": acoes,
        "basicos": t["basicos"],
        "skills": t["skills"],
        "skills_por_tipo": t.get("skills_por_tipo", {}),
        "fracao_basicos": t["basicos"] / acoes if acoes else 0.0,
        "basicos_por_motivo": {m: t.get("basicos_por_motivo", {}).get(m, 0) for m in MOTIVOS},
        "max_basicos_seguidos": max(maiores, default=0),
        "media_max_basicos": _media(maiores),
        "sequencias_5": t["sequencias_5_ou_mais"],
        "rodadas_sem_skill": t["rodadas_sem_skill"],
        "max_rodadas_sem_skill": t["max_rodadas_sem_skill"],
        "perdidas_por_controle": t["perdidas_por_controle"],
        "mp_gasto": t["mp_gasto"],
        "mp_disponivel": t["mp_inicial"] + t["mp_regenerado"],
        "mp_final": t["mp_final"],
        "mp_em_dano": t["mp_em_dano"],
        "dano_de_skill": t["dano_de_skill"],
        "dano_por_100mp": 100 * t["dano_de_skill"] / t["mp_em_dano"] if t["mp_em_dano"] else 0.0,
        "dano_basico_medio": t["dano_basico"] / t["basicos_executados"]
        if t["basicos_executados"]
        else 0.0,
        "rodadas_no_teto": t["rodadas_no_teto_sem_gastar"],
        "regen_perdida": t["regen_perdida_no_teto"],
        "cura_lancada": t["cura_lancada"],
        "cura_excedente": t["cura_excedente"],
        "controle_redundante": t["controle_redundante"],
        "status_redundante": t["status_redundante"],
        "buff_redundante": t["buff_redundante"],
        "golpes": len(golpes),
        "conectados": len(conectados),
        "criticos": sum(1 for g in conectados if g["critico"]),
        "rodadas": [j["rodadas"] for j in jogos],
    }


def _por_build(dados: dict) -> dict:
    """Vitórias por partida disputada, por arquétipo e por política de geração."""
    part = {p["id"]: p for p in dados["participantes"]}
    saida: dict = {"arquetipo": {}, "politica": {}}
    for chave, valores, nomes in (
        ("arquetipo", ARQUETIPOS, lambda p: p["arquetipos"]),
        ("politica", tuple(POLITICAS_PT), lambda p: [p["politica"]]),
    ):
        for v in valores:
            ids = {pid for pid, p in part.items() if v in nomes(p)}
            jogos = [j for j in dados["partidas"] if j["p1"] in ids or j["p2"] in ids]
            vitorias = sum(1 for j in dados["partidas"] if j["vencedor"] in ids)
            disputas = sum((j["p1"] in ids) + (j["p2"] in ids) for j in jogos)
            alcance = _media(
                [
                    FASES_ORDEM.index(part[pid]["fase"]) + (1 if part[pid]["campeao"] else 0)
                    for pid in ids
                ]
            )
            saida[chave][v] = {
                "gladiadores": len(ids),
                "vitorias": vitorias,
                "disputas": disputas,
                "taxa": vitorias / disputas if disputas else 0.0,
                "alcance": alcance,
            }
    return saida


FASES_ORDEM = ["fase64"] + [f for f, _, _ in FASES]


def comparacao(do: dict, dv: dict, co: dict, cv: dict) -> list[list]:
    """A tabela obrigatória: rótulo, Copa original, Copa v2."""
    part = {p["id"]: p for p in dv["participantes"]}

    def campeao(d):
        c = part[d["campeao"]]
        return f"{c['nome']} ({c['id']}, OP {_num(c['op'])})"

    def tipos(c):
        return ", ".join(
            f"{TIPO_PT.get(k, k)} {v}" for k, v in sorted(c["skills_por_tipo"].items())
        )

    def motivos(c):
        return "; ".join(
            f"{ROTULO_DO_MOTIVO[m]} {_pct(c['basicos_por_motivo'][m], c['basicos'])}"
            for m in MOTIVOS
            if c["basicos_por_motivo"][m]
        )

    linhas = [
        ["Campeão", campeao(do), campeao(dv)],
        ["Rodadas por partida (média)", _num(_media(co["rodadas"])), _num(_media(cv["rodadas"]))],
        ["Rodadas (máximo)", max(co["rodadas"]), max(cv["rodadas"])],
        ["Rodadas (mínimo)", min(co["rodadas"]), min(cv["rodadas"])],
        [
            "Golpes conectados / tentados",
            f"{co['conectados']} / {co['golpes']} ({_pct(co['conectados'], co['golpes'])})",
            f"{cv['conectados']} / {cv['golpes']} ({_pct(cv['conectados'], cv['golpes'])})",
        ],
        [
            "Críticos (por golpe conectado)",
            f"{co['criticos']} ({_pct(co['criticos'], co['conectados'])})",
            f"{cv['criticos']} ({_pct(cv['criticos'], cv['conectados'])})",
        ],
        [
            "Ações que foram ataque básico",
            f"{co['basicos']} de {co['acoes']} ({_pct(co['basicos'], co['acoes'])})",
            f"{cv['basicos']} de {cv['acoes']} ({_pct(cv['basicos'], cv['acoes'])})",
        ],
        [
            "Maior sequência de básicos (um lado)",
            co["max_basicos_seguidos"],
            cv["max_basicos_seguidos"],
        ],
        [
            "Maior sequência por lado (média)",
            _num(co["media_max_basicos"]),
            _num(cv["media_max_basicos"]),
        ],
        ["Sequências de 5+ básicos", co["sequencias_5"], cv["sequencias_5"]],
        ["Motivo dos básicos", motivos(co), motivos(cv)],
        [
            "Rodadas sem skill (lado) / maior trecho",
            f"{co['rodadas_sem_skill']} / {co['max_rodadas_sem_skill']}",
            f"{cv['rodadas_sem_skill']} / {cv['max_rodadas_sem_skill']}",
        ],
        ["Skills usadas (total)", co["skills"], cv["skills"]],
        ["Skills por tipo", tipos(co), tipos(cv)],
        [
            "MP gasto / disponível",
            f"{_num(co['mp_gasto'])} / {_num(co['mp_disponivel'])} "
            f"({_pct(co['mp_gasto'], co['mp_disponivel'])})",
            f"{_num(cv['mp_gasto'])} / {_num(cv['mp_disponivel'])} "
            f"({_pct(cv['mp_gasto'], cv['mp_disponivel'])})",
        ],
        [
            "MP no fim do duelo (média por lado)",
            _num(co["mp_final"] / co["lados"]),
            _num(cv["mp_final"] / cv["lados"]),
        ],
        [
            "Regeneração perdida no teto de MP",
            f"{_num(co['regen_perdida'])} MP em {co['rodadas_no_teto']} rodadas",
            f"{_num(cv['regen_perdida'])} MP em {cv['rodadas_no_teto']} rodadas",
        ],
        ["Dano de skill por 100 MP", _num(co["dano_por_100mp"], 1), _num(cv["dano_por_100mp"], 1)],
        [
            "Cura além do HP que faltava",
            f"{_num(co['cura_excedente'])} de {_num(co['cura_lancada'])} "
            f"({_pct(co['cura_excedente'], co['cura_lancada'])})",
            f"{_num(cv['cura_excedente'])} de {_num(cv['cura_lancada'])} "
            f"({_pct(cv['cura_excedente'], cv['cura_lancada'])})",
        ],
        [
            "Controle em alvo já controlado / status repetido / buff ativo relançado",
            f"{co['controle_redundante']} / {co['status_redundante']} / {co['buff_redundante']}",
            f"{cv['controle_redundante']} / {cv['status_redundante']} / {cv['buff_redundante']}",
        ],
        ["Ações perdidas por controle", co["perdidas_por_controle"], cv["perdidas_por_controle"]],
        [
            "Zebras por OP (venceu o OP menor)",
            len(do["agregados"]["zebras"]),
            len(dv["agregados"]["zebras"]),
        ],
    ]
    return linhas


def _primeira_fase_comparada(do: dict, dv: dict) -> dict:
    """Os 32 pares da primeira fase são os mesmos nas duas Copas: o que mudou."""
    velho = {j["chave"]: j for j in do["partidas"] if j["fase"] == "fase64"}
    novo = {j["chave"]: j for j in dv["partidas"] if j["fase"] == "fase64"}
    viradas = [
        {
            "chave": k,
            "antes": velho[k]["vencedor"],
            "agora": novo[k]["vencedor"],
            "rodadas_antes": velho[k]["rodadas"],
            "rodadas_agora": novo[k]["rodadas"],
        }
        for k in sorted(novo, key=lambda c: int(c.split("-")[1]))
        if novo[k]["vencedor"] != velho[k]["vencedor"]
    ]
    return {"pares": len(novo), "viradas": viradas}


def resumo_controlados(controlados: list[dict], part: dict) -> dict:
    """IA × `PoliticaCopa` nos espelhos e nos cruzados, com a mesma régua de condução."""
    saida: dict = {}
    for tipo in ("espelho", "cruzado"):
        lista = [r for r in controlados if r["tipo"] == tipo and r["ia_venceu"] is not None]
        vitorias = sum(r["ia_venceu"] for r in lista)
        lado_ia = [r["metricas"][r["lado_ia"]] for r in lista]
        lado_pc = [r["metricas"]["p2" if r["lado_ia"] == "p1" else "p1"] for r in lista]
        por_arquetipo = {}
        for arq in ARQUETIPOS:
            sub = [r for r in lista if arq in part[r["ids"][r["lado_ia"]]]["arquetipos"]]
            por_arquetipo[arq] = (sum(r["ia_venceu"] for r in sub), len(sub))
        sem = [r for r in lista if not part[r["ids"][r["lado_ia"]]]["arquetipos"]]
        por_arquetipo["sem canal"] = (sum(r["ia_venceu"] for r in sem), len(sem))
        por_lado = {
            lado: (
                sum(r["ia_venceu"] for r in lista if r["lado_ia"] == lado),
                sum(1 for r in lista if r["lado_ia"] == lado),
            )
            for lado in SIDES
        }
        saida[tipo] = {
            "n": len(lista),
            "inconclusivos": sum(
                1 for r in controlados if r["tipo"] == tipo and r["ia_venceu"] is None
            ),
            "vitorias": vitorias,
            "por_lado": por_lado,
            "por_arquetipo": por_arquetipo,
            "rodadas": _media(r["rodadas"] for r in lista),
            "ia": conducao_lados(lado_ia),
            "pc": conducao_lados(lado_pc),
            "concordancia": (
                sum(r["concorda_com_politica"] for r in lista),
                sum(r["decisoes"] for r in lista),
            ),
        }
    cruzados = [r for r in controlados if r["tipo"] == "cruzado" and r["ia_venceu"] is not None]
    pares: dict = {}
    for r in cruzados:
        a, b = r["a"], r["b"]
        quem = a if r["ia"] == "A" else b
        venceu = r["ids"][r["vencedor"]]
        d = pares.setdefault((a, b), {"a": a, "b": b, "a_com_ia": [0, 0], "a_com_pc": [0, 0]})
        chave = "a_com_ia" if quem == a else "a_com_pc"
        d[chave][0] += venceu == a
        d[chave][1] += 1
    saida["pares"] = list(pares.values())
    saida["previsoes"] = [
        (p, r["ia_venceu"], rodada)
        for r in controlados
        if r["ia_venceu"] is not None
        for rodada, p in r["previsoes"]
        if p is not None
    ]
    return saida


def conducao_lados(lados: list[dict]) -> dict:
    t = somar(lados)
    acoes = t["basicos"] + t["skills"]
    return {
        "lados": len(lados),
        "fracao_basicos": t["basicos"] / acoes if acoes else 0.0,
        "media_max_basicos": _media(m["max_basicos_seguidos"] for m in lados),
        "skills_por_lado": t["skills"] / max(1, len(lados)),
        "mp_gasto_por_lado": t["mp_gasto"] / max(1, len(lados)),
        "fracao_mp_gasto": t["mp_gasto"] / max(1, t["mp_inicial"] + t["mp_regenerado"]),
        "mp_final_por_lado": t["mp_final"] / max(1, len(lados)),
        "regen_perdida_por_lado": t["regen_perdida_no_teto"] / max(1, len(lados)),
        "dano_por_100mp": 100 * t["dano_de_skill"] / t["mp_em_dano"] if t["mp_em_dano"] else 0.0,
        "cura_excedente": t["cura_excedente"] / max(1, t["cura_lancada"]),
        "redundantes": t["controle_redundante"] + t["status_redundante"] + t["buff_redundante"],
        "perdidas_por_controle": t["perdidas_por_controle"] / max(1, len(lados)),
        "basicos_por_motivo": {m: t.get("basicos_por_motivo", {}).get(m, 0) for m in MOTIVOS},
        "basicos": t["basicos"],
    }


def _calibracao(previsoes: list) -> dict:
    """Brier e confiabilidade das P(vitória) que a IA estimou nas próprias escolhas."""
    if not previsoes:
        return {"n": 0}
    brier = _media((p - g) ** 2 for p, g, _ in previsoes)
    faixas = []
    for lo in (0.0, 0.2, 0.4, 0.6, 0.8):
        sub = [(p, g) for p, g, _ in previsoes if lo <= p < lo + 0.2 or (lo == 0.8 and p == 1.0)]
        if sub:
            faixas.append(
                [lo, lo + 0.2, len(sub), _media(p for p, _ in sub), _media(g for _, g in sub)]
            )
    return {"n": len(previsoes), "brier": brier, "faixas": faixas}


# --- as decisões da IA ------------------------------------------------------------------


def _tipo_da_acao(rotulo: str, deck: dict) -> str:
    if rotulo == "ataque básico":
        return "básico"
    carta = next((s for s in deck.values() if s.name == rotulo), None)
    if carta is None:
        return "?"
    return {
        "damage": "dano",
        "heal": "cura",
        "buff": "buff",
        "status": "status",
        "damage_reduction": "redução de dano",
    }[carta.effect_type]


def resumo_decisoes(decisoes: dict, copa) -> dict:
    """Concordância com a `PoliticaCopa` e as divergências, por categoria."""
    por_chave = {f"{p.fase}-{p.indice}": p for p in todas(copa)}
    total = escolha_real = concordou = 0
    categorias: Counter = Counter()
    exemplos: dict = {}
    basicos: Counter = Counter()
    preferido_a: Counter = Counter()
    for chave, lados in decisoes.items():
        partida = por_chave[chave]
        for lado, lista in lados.items():
            deck = {s.id: s for s in partida.lados[lado].heroi.skills.values()}
            curas = {s.name for s in deck.values() if s.effect_type == "heal"}
            for i, d in enumerate(lista):
                total += 1
                if len(d["avaliacoes"]) < 2:
                    continue
                escolha_real += 1
                if d["acao"] == "ataque básico":
                    motivo = _por_que_basico(d, lista[i + 1 : i + 6], curas)
                    basicos[motivo] += 1
                    if motivo == "preferencia":
                        outras = [a for a in d["avaliacoes"] if a["acao"] != "ataque básico"]
                        melhor = max(outras, key=lambda a: a["utilidade"] or 0)["acao"]
                        preferido_a[_tipo_da_acao(melhor, deck)] += 1
                if d["acao"] == d["politica_copa"]:
                    concordou += 1
                    continue
                cat = (_tipo_da_acao(d["politica_copa"], deck), _tipo_da_acao(d["acao"], deck))
                categorias[cat] += 1
                exemplos.setdefault(cat, []).append(
                    {
                        "chave": chave,
                        "titulo": partida.titulo,
                        "lado": lado,
                        "nome": partida.lados[lado].nome,
                        **d,
                    }
                )
    # Os exemplos de cada categoria: o de maior diferença estimada entre a escolha
    # da IA e a da política, para mostrar o caso mais nítido.
    for cat, lista in exemplos.items():

        def ganho(d):
            p = {a["acao"]: a["utilidade"] for a in d["avaliacoes"]}
            return (p.get(d["acao"]) or 0) - (p.get(d["politica_copa"]) or 0)

        ordenados = sorted(lista, key=lambda d: -ganho(d))
        # O caso mais nítido e um típico (o da diferença mediana).
        exemplos[cat] = [ordenados[0]] + (
            [ordenados[len(ordenados) // 2]] if len(ordenados) > 2 else []
        )
    return {
        "total": total,
        "com_escolha": escolha_real,
        "concordou": concordou,
        "categorias": categorias.most_common(),
        "exemplos": exemplos,
        "basicos_por_escolha": dict(basicos),
        "basico_preferido_a": preferido_a.most_common(),
    }


EMPATE_TECNICO = 0.002
POR_QUE_BASICO = {
    "empate": "as opções valiam o mesmo (diferença de utilidade abaixo de 0,002)",
    "cura": "guardou MP e curou nas 5 rodadas seguintes",
    "preferencia": "o básico valia mais que qualquer carta legal",
}


def _por_que_basico(d: dict, seguintes: list[dict], curas: set) -> str:
    """Por que a IA atacou no básico com carta legal na mão, pelos números dela."""
    u = {a["acao"]: a["utilidade"] for a in d["avaliacoes"] if a["utilidade"] is not None}
    melhor_carta = max((v for k, v in u.items() if k != "ataque básico"), default=None)
    if melhor_carta is not None and u.get("ataque básico", 0) - melhor_carta < EMPATE_TECNICO:
        return "empate"
    if curas and any(x["acao"] in curas for x in seguintes):
        return "cura"
    return "preferencia"


# --- três lutas em detalhe -----------------------------------------------------------------


def escolher_lutas(dv: dict, do: dict) -> list[str]:
    """A final; a virada de maior ΔOP na primeira fase; a partida mais longa."""
    escolhidas = ["final-1"]
    viradas = _primeira_fase_comparada(do, dv)["viradas"]
    jogos = {j["chave"]: j for j in dv["partidas"]}
    if viradas:
        escolhidas.append(max(viradas, key=lambda v: abs(jogos[v["chave"]]["delta_op"]))["chave"])
    for j in sorted(dv["partidas"], key=lambda j: (-j["rodadas"], j["chave"])):
        if j["chave"] not in escolhidas:
            escolhidas.append(j["chave"])
        if len(escolhidas) >= 3:
            break
    return escolhidas


def _iniciativa(partida) -> dict:
    """O Initiative Score de cada lado, rodada a rodada, lido do trace."""
    saida: dict = {lado: {} for lado in SIDES}
    for r in partida.auditado.trace.de("iniciativa"):
        saida[r["lado"]][r["rodada"]] = r.get("score")
    return saida


def luta(partida, jogo: dict, decisoes: dict, part: dict, velho: dict | None) -> dict:
    ini = _iniciativa(partida)
    por_rodada = {lado: {d["rodada"]: d for d in decisoes.get(lado, [])} for lado in SIDES}
    linhas = []
    for r in jogo["rodadas_detalhe"]:
        n = r["n"]
        linha = {"n": n, "primeiro": r["ordem"][0], "hp": r["hp"], "mp": r["mp"], "lados": {}}
        for lado in SIDES:
            d = por_rodada[lado].get(n)
            p = None
            if d is not None:
                p = next((a["p"] for a in d["avaliacoes"] if a["acao"] == d["acao"]), None)
            linha["lados"][lado] = {
                **r["acoes"][lado],
                "p": p,
                "iniciativa": ini[lado].get(n),
                "politica_copa": d["politica_copa"] if d else None,
                "impasse": d["modelo"]["impasse"] if d else 0,
            }
        linhas.append(linha)
    curas = {
        s.name
        for lado in SIDES
        for s in partida.lados[lado].heroi.skills.values()
        if s.effect_type == "heal"
    }
    momentos = _momentos(jogo, linhas, part, curas)
    return {
        "chave": jogo["chave"],
        "titulo": jogo["titulo"],
        "nome_fase": jogo["nome_fase"],
        "seed": jogo["seed"],
        "jogo": jogo,
        "linhas": linhas,
        "momentos": momentos,
        "decisoes": decisoes,
        "original": velho,
    }


def _momentos(jogo: dict, linhas: list[dict], part: dict, curas: set) -> list[str]:
    """Os momentos decisivos, lidos dos números da própria luta."""
    frases = []
    nomes = {lado: part[jogo[lado]]["nome"] for lado in SIDES}
    venc = jogo["lado_vencedor"]
    # A maior virada na estimativa do vencedor.
    serie = [
        (x_["n"], x_["lados"][venc]["p"]) for x_ in linhas if x_["lados"][venc]["p"] is not None
    ]
    if len(serie) > 1:
        saltos = [(b[1] - a[1], b[0]) for a, b in zip(serie, serie[1:])]
        antes = {b[0]: a[1] for a, b in zip(serie, serie[1:])}
        delta, rodada = max(saltos, key=lambda x: abs(x[0]))
        frases.append(
            f"Maior mudança na estimativa de {nomes[venc]}: {_sinal(delta)} na rodada {rodada} "
            f"(P(vitória) {_num(antes[rodada]) if rodada in antes else '—'} → "
            f"{_num(dict(serie)[rodada])})."
        )
    criticos = [g for g in jogo["golpes"] if g["critico"] and not g["errou"]]
    if criticos:
        maior = max(criticos, key=lambda g: g["dano"])
        frases.append(
            f"Maior crítico: {part[maior['atacante']]['nome']}, {maior['dano']} de dano com "
            f"{maior['acao']} na rodada {maior['rodada']}."
        )
    ultimo = next((g for g in reversed(jogo["golpes"]) if g["matou"]), None)
    if ultimo:
        frases.append(
            f"Golpe final: {part[ultimo['atacante']]['nome']}, {ultimo['acao']}, "
            f"{ultimo['dano']} de dano na rodada {ultimo['rodada']}"
            f"{' (crítico)' if ultimo['critico'] else ''}."
        )
    feitas = [
        (x_["n"], lado)
        for x_ in linhas
        for lado in SIDES
        if x_["lados"][lado]["desfecho"] == "executed" and x_["lados"][lado]["acao"] in curas
    ]
    if feitas:
        por_lado = Counter(lado for _, lado in feitas)
        frases.append(
            "Curas: " + ", ".join(f"{nomes[lado]} {n}" for lado, n in por_lado.items()) + "."
        )
    trocas = sum(1 for a, b in zip(linhas, linhas[1:]) if a["primeiro"] != b["primeiro"])
    frases.append(f"A iniciativa trocou de mãos {trocas} vez(es).")
    impasse = [x_["n"] for x_ in linhas if max(x_["lados"][s]["impasse"] for s in SIDES) > 0]
    if impasse:
        frases.append(f"A urgência de impasse entrou na rodada {impasse[0]}: a luta já não andava.")
    return frases


# --- o modelo inteiro ----------------------------------------------------------------------


def modelo(nova, decisoes, original, verificacoes, controlados, variantes=None) -> dict:
    gladiadores = ler_gladiadores(PASTA_ORIGINAL)
    geracao = c3r.modelo_geracao(PASTA_ORIGINAL)
    dv = c3r.modelo(nova, [], geracao, gladiadores)
    do = c3r.modelo(original, [], geracao, gladiadores)
    herois = {p.id: p.heroi for p in nova.participantes}
    mv, mo = _metricas(nova, herois), _metricas(original, herois)
    cv, co = conducao(dv, mv), conducao(do, mo)
    part = {p["id"]: p for p in dv["participantes"]}
    por_chave = {f"{p.fase}-{p.indice}": p for p in todas(nova)}
    jogos_v = {j["chave"]: j for j in dv["partidas"]}
    jogos_o = {j["chave"]: j for j in do["partidas"]}
    lutas = [
        luta(por_chave[k], jogos_v[k], decisoes.get(k, {}), part, jogos_o.get(k))
        for k in escolher_lutas(dv, do)
    ]
    controle = resumo_controlados(controlados, part)
    rodizio = (
        json.loads(ARQUIVO_RODIZIO.read_text(encoding="utf-8"))
        if ARQUIVO_RODIZIO.exists()
        else None
    )
    return {
        "copa": COPA_IA,
        "semente_principal": SEMENTE_PRINCIPAL,
        "verificacoes": verificacoes,
        "dados": dv,
        "dados_original": do,
        "conducao": cv,
        "conducao_original": co,
        "metricas": mv,
        "metricas_original": mo,
        "comparacao": comparacao(do, dv, co, cv),
        "primeira_fase": _primeira_fase_comparada(do, dv),
        "por_build": _por_build(dv),
        "por_build_original": _por_build(do),
        "controlados": controle,
        "calibracao": _calibracao(controle["previsoes"]),
        "decisoes": resumo_decisoes(decisoes, nova),
        "lutas": lutas,
        "rodizio": rodizio,
        "economia": economia(nova),
        "config": ia.Configuracao(),
        "variantes": variantes or {},
    }


def economia(copa) -> dict:
    """A economia de MP dos 64, em números do motor: regeneração contra custo."""
    from src.content.gladiator import prepare_gladiator
    from src.mechanics import combat
    from tools.arena_ia_estrategica import cura_esperada, regeneracao

    linhas = []
    for p in copa.participantes:
        h = prepare_gladiator(p.heroi).hero
        custos = [combat.skill_mana_cost(h, s) for s in h.skills.values()]
        curas = [cura_esperada(h, s) for s in h.skills.values() if s.effect_type == "heal"]
        linhas.append(
            {
                "id": p.id,
                "mp": h.base_mp,
                "regen": regeneracao(h),
                "custo_medio": _media(custos),
                "rodadas_por_skill": _media(custos) / max(1, regeneracao(h)),
                "skills_no_caixa": h.base_mp / max(1, _media(custos)),
                "cura": max(curas, default=0),
            }
        )
    return {
        "regen_media": _media(x["regen"] for x in linhas),
        "custo_medio": _media(x["custo_medio"] for x in linhas),
        "rodadas_por_skill": _media(x["rodadas_por_skill"] for x in linhas),
        "skills_no_caixa": _media(x["skills_no_caixa"] for x in linhas),
        "mp_medio": _media(x["mp"] for x in linhas),
    }


# --- Markdown ---------------------------------------------------------------------------


def _tabela(cabecalho: list[str], linhas: list[list]) -> list[str]:
    saida = ["| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
    saida += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return saida


def _nome(pid: str, part: dict) -> str:
    return f"{part[pid]['nome']} ({pid})"


def _metodo_md(m: dict) -> list[str]:
    cfg = m["config"]
    return [
        "## A IA, em uma página",
        "",
        "`tools/arena_ia_estrategica.py` implementa `DuelController.choose(view)`. Não é lista de "
        "prioridade: para cada ação legal ela joga continuações curtas NO PRÓPRIO MOTOR "
        "(`Duel.play_round` sobre cópias) e avalia onde cada uma para.",
        "",
        f"- **Horizonte e orçamento:** {cfg.horizonte} rodadas, {cfg.rollouts} continuações por "
        "ação "
        f"({cfg.rollouts_criticos} quando alguém está ao alcance de um golpe letal). As sementes "
        "são "
        "as mesmas para todas as candidatas, e cada sorteio vem de um fluxo próprio por origem "
        "(função do motor, lado, rodada): o golpe do adversário na rodada 1 é o mesmo número em "
        "todas as candidatas, e a diferença entre elas não é sorte.",
        "- **Dentro do horizonte** é o motor de verdade: acerto, crítico, status, DoT, controle, "
        "buffs, recargas, reserva de MP e iniciativa. A primeira ação é a candidata; depois, uma "
        "política base barata (cura quando aperta, senão o maior dano esperado, com o bônus "
        "situacional conferido no estado simulado).",
        '- **Depois do horizonte**, uma corrida "quem derruba quem primeiro" com as fórmulas '
        "canônicas (`hit_chance`, `crit_chance`, `damage_modifiers`, `_calculate_damage`, "
        "`skill_damage_base`, `basic_attack_power`): taxa de dano por oportunidade, DoT e controle "
        "dos procs do acerto, roubo de vida, o MP que ainda compra dano ou cura até o fim previsto "
        "da luta (ponto fixo por bisseção), temporários pelo que ainda duram e bônus situacional "
        "pela fração da luta em que vale. Vira P(vitória) pela normal, com a incerteza do dado e a "
        f"do modelo (κ de {cfg.incerteza_inicial} a {cfg.incerteza_final}, ajustado por log-loss "
        "em "
        "duelos IA × IA).",
        "- **Utilidade:** P(vitória) menos um custo pequeno do tempo que ainda falta para vencer — "
        "que só desempata quando a vitória já está decidida. Num impasse (20 rodadas sem que "
        "ninguém bata o próprio recorde de HP baixo, ou mais de 60 rodadas) o custo do tempo passa "
        "a ser linear e cresce até dominar: a IA larga a cura que só mantém tudo onde está.",
        "- **O que ela sabe:** de si, a própria ficha e o próprio estado (só leitura); do "
        "adversário, só a `FighterView` — classe, nível, HP/MP atuais e máximos, nomes de efeitos "
        "e buffs — e a história dessas leituras. O adversário é modelado: o herói canônico da "
        "classe "
        "e do nível com o loadout esperado, os tetos de HP/MP da tela, ofensa e defesa ajustadas "
        "pelo dano observado, cartas reveladas pelo custo de MP gasto (catálogo público) e pelos "
        "buffs que aparecem pelo nome, e roubo de vida, regeneração e procs inferidos do que a "
        "tela "
        "mostra. Antes de aparecerem, as cartas dele são supostas iguais às dela (mesma classe).",
        "- **Simultaneidade:** o adversário das simulações escolhe a primeira ação do estado "
        "anterior à rodada, igual para todas as candidatas — sem ver a ação candidata.",
        "",
    ] + _orcamento_md(m)


def _orcamento_md(m: dict) -> list[str]:
    if not m["variantes"]:
        return []
    linhas = [
        "**O orçamento basta?** Cada variante contra a configuração da Copa, IA × IA em espelho "
        "(os 64, lados e duas seeds alternados):",
        "",
    ]
    for nome, v in m["variantes"].items():
        inconclusivos = f"; {v['inconclusivos']} inconclusivos" if v["inconclusivos"] else ""
        linhas.append(
            f"- {nome}: venceu {_taxa(v['vitorias_da_variante'], v['n'])}{inconclusivos}."
        )
    linhas += [
        "",
        "Um intervalo que contém 50% quer dizer que a variante não joga melhor: o orçamento da "
        "Copa não é o que limita a IA.",
        "",
    ]
    return linhas


def _integridade_md(m: dict) -> list[str]:
    linhas = [
        "## Integridade",
        "",
        "- Os mesmos 64 gladiadores publicados em `reports/pvp/copa_03/` — snapshots conferidos "
        "pelo `sha256` de `gladiadores.json` antes de cada reconstrução —, com os mesmos IDs, "
        "nomes, builds e OP. Nenhuma run PvE, nenhuma extração, nenhum arquivo de `src/` alterado.",
        '- O mesmo sorteio da chave (`sha256("20261025:chave")`) e as mesmas seeds oficiais por '
        'posição (`sha256("20261025:fase:índice")`). Só o controlador dos dois lados muda. Da '
        "segunda fase em diante os pares dependem de quem venceu, então não são os mesmos.",
        "- Antes da v2, a Copa original foi reproduzida com a `PoliticaCopa` e conferida contra o "
        "que está publicado:",
        "",
    ]
    linhas += [f"  - {nome}: {'ok' if ok else 'FALHOU'}" for nome, ok in m["verificacoes"]]
    total = sum(len(p) for p in m["metricas"].values())
    fiel = all(j["fidelidade"] and j["coerencia"] for j in m["dados"]["partidas"])
    linhas += [
        "",
        f"- As 63 partidas da v2 jogadas duas vezes (sem e com auditoria): fidelidade e coerência "
        f"{'ok em todas' if fiel else 'COM FALHA'}; {total} lados medidos. O que a IA simula ao "
        "decidir não entra no trace: `ControladorAuditado` devolve as funções canônicas originais "
        "enquanto o controlador pensa (`arena_auditoria.fora_do_duelo`).",
        "",
    ]
    return linhas


def _comparacao_md(m: dict) -> list[str]:
    linhas = [
        "## A comparação obrigatória",
        "",
        "Original = Copa Arena 03 (`PoliticaCopa`), reproduzida bit a bit; v2 = IA estratégica. "
        "As duas medidas pelas mesmas funções.",
        "",
    ]
    linhas += _tabela(["", "Original (PoliticaCopa)", "v2 (IA estratégica)"], m["comparacao"])
    pf = m["primeira_fase"]
    part = {p["id"]: p for p in m["dados"]["participantes"]}
    linhas += [
        "",
        f"**Primeira fase, os mesmos 32 pares e as mesmas seeds:** {len(pf['viradas'])} dos "
        f"{pf['pares']} resultados mudaram com a troca de controlador.",
        "",
    ]
    if pf["viradas"]:
        linhas += _tabela(
            ["Partida", "Vencia com a PoliticaCopa", "Vence com a IA", "Rodadas (antes → agora)"],
            [
                [
                    v["chave"],
                    _nome(v["antes"], part),
                    _nome(v["agora"], part),
                    f"{v['rodadas_antes']} → {v['rodadas_agora']}",
                ]
                for v in pf["viradas"]
            ],
        )
        linhas.append("")
    return linhas


def _builds_md(m: dict) -> list[str]:
    linhas = [
        "## Desempenho por tipo de build",
        "",
        "Na Copa: vitórias sobre partidas disputadas. Num mata-mata cada derrota elimina, então os "
        "números são pequenos e dependem da chave — por isso a coluna dos confrontos controlados, "
        "que mede o quanto a MESMA build rende a mais com a IA do que com a `PoliticaCopa`, lado e "
        "seed alternados.",
        "",
    ]
    ctrl = m["controlados"]
    rotulos = {
        "controle": "controle",
        "crítico": "crítico",
        "defesa": "defesa",
        "sustento": "sustento",
    }
    tabela = []
    for arq in ARQUETIPOS:
        a, b = m["por_build_original"]["arquetipo"][arq], m["por_build"]["arquetipo"][arq]
        k, n = ctrl["espelho"]["por_arquetipo"][arq]
        tabela.append(
            [
                rotulos[arq],
                a["gladiadores"],
                f"{a['vitorias']}/{a['disputas']} ({_pct(a['vitorias'], a['disputas'])})",
                f"{b['vitorias']}/{b['disputas']} ({_pct(b['vitorias'], b['disputas'])})",
                f"{_num(a['alcance'], 2)} → {_num(b['alcance'], 2)}",
                _taxa(k, n),
            ]
        )
    for pol, pt in POLITICAS_PT.items():
        a, b = m["por_build_original"]["politica"][pol], m["por_build"]["politica"][pol]
        tabela.append(
            [
                f"política {pt}",
                a["gladiadores"],
                f"{a['vitorias']}/{a['disputas']} ({_pct(a['vitorias'], a['disputas'])})",
                f"{b['vitorias']}/{b['disputas']} ({_pct(b['vitorias'], b['disputas'])})",
                f"{_num(a['alcance'], 2)} → {_num(b['alcance'], 2)}",
                "—",
            ]
        )
    linhas += _tabela(
        [
            "Build",
            "Gladiadores",
            "Copa original",
            "Copa v2",
            "Fase média alcançada",
            "Espelho: IA vence a PoliticaCopa",
        ],
        tabela,
    )
    linhas += [
        "",
        "Fase média alcançada: 0 = caiu na fase de 64, 6 = campeão.",
        "",
    ]
    return linhas + _leitura_das_builds(m)


def _leitura_das_builds(m: dict) -> list[str]:
    """Controle, crítico e política ofensiva: o que mudou, e o que dá para dizer."""
    e, c = m["controlados"]["espelho"], m["controlados"]["cruzado"]
    geral = e["vitorias"] / e["n"] if e["n"] else 0.0
    rr = m["rodizio"] or {}
    canais = rr.get("canais", {})
    ofensiva = rr.get("grupos", {}).get("politica", {}).get("offense", {})
    linhas = ["**Controle, crítico e política ofensiva.**", ""]
    for arq in ("controle", "crítico"):
        a, b = m["por_build_original"]["arquetipo"][arq], m["por_build"]["arquetipo"][arq]
        k, n = e["por_arquetipo"][arq]
        kc, nc = c["por_arquetipo"][arq]
        residuo = canais.get(arq, {}).get("residuo_com")
        contexto = (
            f" No todos contra todos com a `PoliticaCopa`, essas builds rendiam "
            f"{_num(100 * abs(residuo), 1)} pontos percentuais "
            f"{'abaixo' if residuo < 0 else 'acima'} do que o OP previa."
            if residuo is not None
            else ""
        )
        ganho = (
            "maior"
            if k / max(1, n) > geral + 0.03
            else "menor"
            if k / max(1, n) < geral - 0.03
            else "igual"
        )
        linhas.append(
            f"- **{arq.capitalize()}** ({a['gladiadores']} builds):{contexto} Na Copa v2 venceram "
            f"{b['vitorias']} de {b['disputas']} partidas ({_pct(b['vitorias'], b['disputas'])}; "
            f"eram {_pct(a['vitorias'], a['disputas'])}) e a fase média foi de "
            f"{_num(a['alcance'])} para {_num(b['alcance'])}. Com a build fixa, a IA vence a "
            f"`PoliticaCopa` em {_pct(k, n)} dos espelhos dessas builds ({_pct(geral, 1)} no "
            "geral) "
            f"e em {_pct(kc, nc)} dos cruzados: o ganho do controlador nelas é {ganho} ao geral."
        )
    a, b = m["por_build_original"]["politica"]["offense"], m["por_build"]["politica"]["offense"]
    residuo = ofensiva.get("residuo")
    contexto = (
        f" No todos contra todos, {_num(100 * abs(residuo), 1)} pontos "
        f"{'abaixo' if residuo < 0 else 'acima'} do previsto pelo OP."
        if residuo is not None
        else ""
    )
    linhas += [
        f"- **Política ofensiva** ({a['gladiadores']} builds geradas com a agenda de risco "
        f"ofensiva):{contexto} Na Copa v2, {b['vitorias']} de {b['disputas']} "
        f"({_pct(b['vitorias'], b['disputas'])}; eram {_pct(a['vitorias'], a['disputas'])}), fase "
        f"média {_num(a['alcance'])} → {_num(b['alcance'])}.",
        "",
        "Uma parte do resíduo negativo de controle e de política ofensiva no todos contra todos "
        "vinha da `PoliticaCopa`, que lança todo status antes do dano. Os espelhos isolam o "
        "controlador e mostram quanto a mesma build ganha com a IA; a Copa, sozinha, não separa "
        "isso da chave. Para afirmar que essas builds ficaram mais fortes, seria preciso um novo "
        "todos contra todos com a IA — que não foi feito aqui.",
        "",
    ]
    return linhas


def _controlados_md(m: dict) -> list[str]:
    ctrl = m["controlados"]
    e, c = ctrl["espelho"], ctrl["cruzado"]
    linhas = [
        "## IA × PoliticaCopa em confrontos controlados",
        "",
        f"- **Espelho** (cada um dos 64 contra si mesmo, IA de um lado e `PoliticaCopa` do outro, "
        f"lados e duas seeds alternados): a IA venceu {_taxa(e['vitorias'], e['n'])} — como p1 "
        f"{e['por_lado']['p1'][0]}/{e['por_lado']['p1'][1]}, como p2 {e['por_lado']['p2'][0]}/"
        f"{e['por_lado']['p2'][1]}. Duração média {_num(e['rodadas'], 1)} rodadas.",
        f"- **Cruzado** (os 32 pares da primeira fase, cada gladiador uma vez com a IA e uma vez "
        f"com a `PoliticaCopa`, lados e seeds alternados): o lado da IA venceu "
        f"{_taxa(c['vitorias'], c['n'])}.",
        f"- Inconclusivos no limite técnico: {e['inconclusivos'] + c['inconclusivos']}.",
        "",
        "Com a build fixa, o controlador é a única diferença. A IA não foi ajustada para vencer a "
        "`PoliticaCopa`: nada nela conhece a política antiga (que ela só consulta para registrar o "
        "que a política teria feito), e o único parâmetro ajustado com dados — a incerteza do "
        "modelo — foi calibrado em duelos IA × IA.",
        "",
        "### Competência medida nos mesmos duelos (espelho)",
        "",
    ]
    a, b = e["ia"], e["pc"]
    linhas += _tabela(
        ["Por lado", "IA", "PoliticaCopa"],
        [
            ["Ações que foram básico", _pct(a["fracao_basicos"], 1), _pct(b["fracao_basicos"], 1)],
            [
                "Maior sequência de básicos (média)",
                _num(a["media_max_basicos"]),
                _num(b["media_max_basicos"]),
            ],
            ["Skills por duelo", _num(a["skills_por_lado"], 1), _num(b["skills_por_lado"], 1)],
            ["MP gasto / disponível", _pct(a["fracao_mp_gasto"], 1), _pct(b["fracao_mp_gasto"], 1)],
            [
                "MP no fim do duelo",
                _num(a["mp_final_por_lado"], 0),
                _num(b["mp_final_por_lado"], 0),
            ],
            [
                "Regeneração perdida no teto",
                _num(a["regen_perdida_por_lado"], 1),
                _num(b["regen_perdida_por_lado"], 1),
            ],
            [
                "Dano de skill por 100 MP",
                _num(a["dano_por_100mp"], 1),
                _num(b["dano_por_100mp"], 1),
            ],
            [
                "Cura além do HP que faltava",
                _pct(a["cura_excedente"], 1),
                _pct(b["cura_excedente"], 1),
            ],
            ["Controle/status/buff redundantes (total)", a["redundantes"], b["redundantes"]],
            [
                "Ações perdidas por controle (sofridas)",
                _num(a["perdidas_por_controle"], 2),
                _num(b["perdidas_por_controle"], 2),
            ],
        ],
    )
    k, n = e["concordancia"]
    linhas += [
        "",
        f"Nas {n} decisões da IA nesses duelos, ela escolheu o mesmo que a `PoliticaCopa` "
        f"escolheria na mesma visão em {_pct(k, n)} delas (contando as rodadas em que só o "
        "básico era legal).",
        "",
    ]
    cal = m["calibracao"]
    if cal["n"]:
        linhas += [
            "### As estimativas da IA batem com o que acontece?",
            "",
            f"Brier {_num(cal['brier'], 3)} em {cal['n']} estimativas de P(vitória) da ação "
            "escolhida (0,25 é o chute de 50%).",
            "",
        ]
        linhas += _tabela(
            ["P estimada", "Decisões", "P média estimada", "Vitórias de fato"],
            [
                [f"{_num(lo, 1)}–{_num(hi, 1)}", n_, _num(pm, 2), _pct(g, 1)]
                for lo, hi, n_, pm, g in cal["faixas"]
            ],
        )
        linhas += [
            "",
            "A estimativa ordena bem — quanto maior a P que ela dá, mais ela vence —, mas contra a "
            "`PoliticaCopa` ela é pessimista: a IA modela o adversário como alguém que gasta o MP "
            "tão bem quanto ela e tem um deck como o dela, e a política antiga não joga assim. A "
            "incerteza do modelo foi calibrada em duelos IA × IA, onde esse viés é menor.",
            "",
        ]
    return linhas


def _economia_md(m: dict) -> list[str]:
    ec = m["economia"]
    cv, co = m["conducao"], m["conducao_original"]
    linhas = [
        "## A economia de recursos (§2): por que ainda há tanto básico",
        "",
        f"Nos 64, o MP máximo médio é {_num(ec['mp_medio'], 0)}, a regeneração média "
        f"{_num(ec['regen_media'], 1)} por turno (2% do teto mais passivas e equipamento) e o "
        "custo "
        f"médio de uma carta {_num(ec['custo_medio'], 1)}. O caixa inicial paga cerca de "
        f"{_num(ec['skills_no_caixa'], 1)} cartas; depois dele, a regeneração paga uma carta a "
        f"cada {_num(ec['rodadas_por_skill'], 1)} rodadas. Numa luta de 30 rodadas isso dá, no "
        f"máximo, perto de {_num(ec['skills_no_caixa'] + 30 / ec['rodadas_por_skill'], 0)} cartas "
        "por lado — o resto é básico, faça o controlador o que fizer. Nenhum custo, regeneração ou "
        "regra foi mudado.",
        "",
        "Motivo de cada ataque básico, lido da visão e da ficha de quem atacou:",
        "",
    ]
    linhas += _tabela(
        ["Motivo", "Original (PoliticaCopa)", "v2 (IA)"],
        [
            [
                ROTULO_DO_MOTIVO[mot],
                f"{co['basicos_por_motivo'][mot]} "
                f"({_pct(co['basicos_por_motivo'][mot], co['basicos'])})",
                f"{cv['basicos_por_motivo'][mot]} "
                f"({_pct(cv['basicos_por_motivo'][mot], cv['basicos'])})",
            ]
            for mot in MOTIVOS
        ],
    )
    linhas += [
        "",
        '"Havia skill legal" é a escolha do controlador: na `PoliticaCopa`, nenhuma regra dela '
        "pedia carta (buff ativo, status já no alvo, nenhuma carta de dano legal); na IA, a "
        "avaliação preferiu o básico. Os básicos da IA com carta legal na mão, pelos números "
        "dela no momento:",
        "",
    ]
    escolha = m["decisoes"]["basicos_por_escolha"]
    total = sum(escolha.values())
    linhas += _tabela(
        ["Por quê", "Básicos"],
        [
            [POR_QUE_BASICO[k], f"{escolha.get(k, 0)} ({_pct(escolha.get(k, 0), total)})"]
            for k in ("empate", "cura", "preferencia")
        ],
    )
    preferido = m["decisoes"]["basico_preferido_a"]
    if preferido:
        linhas += [
            "",
            "Quando o básico valia mais, a melhor carta legal que ficou na mão era: "
            + ", ".join(f"{tipo} ({n})" for tipo, n in preferido)
            + ". Com carta de dano, é o MP guardado para algo que rende mais depois — a cura, a "
            "carta condicional, a recarga da melhor carta —, ou o alvo que o básico já derruba.",
        ]
    linhas += [
        "",
        "No empate as opções valiam o mesmo para o modelo — o MP guardado compra a mesma coisa "
        "depois —, e o básico vem primeiro na lista de ações legais. Um desempate a favor de "
        "gastar mudaria o número de básicos sem mudar o valor das decisões; ele não foi feito, "
        "para não otimizar a métrica no lugar da luta.",
        "",
        "**Impasse entre builds de sustento.** Entre builds com cura de 10–12% do HP, roubo de "
        "vida "
        "e redução de dano, a cura por MP rende cerca de quatro vezes o dano por MP (no espelho de "
        "W05: 852 de HP por 74 MP contra cerca de 2,8 de dano extra por MP nas cartas de dano), e "
        "a recarga da cura sustenta mais HP por rodada do que o básico do outro tira. Com as duas "
        "IAs curando bem, os espelhos de W05 e W23 chegavam a 500 rodadas — o limite técnico, "
        "sem vencedor. É uma propriedade da economia, não da IA, e a regra não foi tocada: a IA "
        "ganhou a urgência de impasse descrita acima, e esses espelhos passaram a terminar.",
        "",
    ]
    return linhas


def _rodizio_md(m: dict) -> list[str]:
    rr = m["rodizio"]
    if not rr:
        return []
    pos = {x["id"]: x["posicao"] for x in rr["ranking"]}
    part = {p["id"]: p for p in m["dados"]["participantes"]}
    linhas = [
        "## O ranking Bradley-Terry original, como referência histórica",
        "",
        "O todos contra todos da Copa 03 (`round_robin.json`, `PoliticaCopa` nos dois lados) segue "
        "sendo a medida de força das builds. Uma eliminatória de 63 partidas, uma seed cada, não "
        "mede força: aqui ela só mostra onde a troca de controlador mudou caminhos.",
        "",
    ]
    for rotulo, d in (("original", m["dados_original"]), ("v2", m["dados"])):
        campeao = d["campeao"]
        quartas = [
            p["id"] for p in d["participantes"] if FASES_ORDEM.index(p["fase"]) >= 3 or p["campeao"]
        ]
        linhas.append(
            f"- Copa {rotulo}: campeão {_nome(campeao, part)}, {pos.get(campeao, '—')}º no "
            f"Bradley-Terry; posição média dos que chegaram às quartas: "
            f"{_num(_media(pos[i] for i in quartas if i in pos), 1)}."
        )
    linhas.append("")
    return linhas


def _luta_md(lt: dict, part: dict) -> list[str]:
    j = lt["jogo"]
    nomes = {lado: part[j[lado]]["nome"] for lado in SIDES}
    linhas = [
        f"### {lt['titulo']}",
        "",
        f"{_nome(j['p1'], part)}, OP {_num(j['op']['p1'])}, contra {_nome(j['p2'], part)}, OP "
        f"{_num(j['op']['p2'])}. Seed {lt['seed']}. Venceu {_nome(j['vencedor'], part)} em "
        f"{j['rodadas']} rodadas, com {j['hp_vencedor']} de {j['hp_max_vencedor']} de HP.",
    ]
    if lt["original"]:
        o = lt["original"]
        linhas.append(
            f"Na Copa original, a mesma posição era {_nome(o['p1'], part)} × "
            f"{_nome(o['p2'], part)}: "
            f"venceu {_nome(o['vencedor'], part)} em {o['rodadas']} rodadas."
        )
    linhas += ["", "**Momentos decisivos**", ""]
    linhas += [f"- {f}" for f in lt["momentos"]]
    linhas += [
        "",
        "**Rodada a rodada** (P = a estimativa de vitória da IA para a ação que ela escolheu; "
        "Init = Initiative Score lido no início da rodada):",
        "",
    ]
    tabela = []
    for r in lt["linhas"]:
        celulas = [r["n"], nomes[r["primeiro"]]]
        for lado in SIDES:
            x = r["lados"][lado]
            desfecho = "" if x["desfecho"] == "executed" else f" ({x['desfecho']})"
            p = "—" if x["p"] is None else _num(x["p"], 2)
            ini = "—" if x["iniciativa"] is None else _num(x["iniciativa"], 3)
            celulas.append(f"{x['acao']}{desfecho} · {x['dano']} dano · P {p} · Init {ini}")
            celulas.append(f"{r['hp'][lado]} / {r['mp'][lado]}")
        tabela.append(celulas)
    linhas += _tabela(
        [
            "Rod.",
            "Age primeiro",
            f"{nomes['p1']}: ação",
            "HP / MP",
            f"{nomes['p2']}: ação",
            "HP / MP",
        ],
        tabela,
    )
    linhas += ["", "**Avaliação das escolhas**", ""]
    linhas += _avaliacao_das_escolhas_md(lt, nomes)
    linhas.append("")
    return linhas


def _avaliacao_das_escolhas_md(lt: dict, nomes: dict) -> list[str]:
    """As decisões em que havia mais em jogo: maior diferença entre a melhor e a pior ação."""
    candidatas = []
    for lado in SIDES:
        for d in lt["decisoes"].get(lado, []):
            us = [a["utilidade"] for a in d["avaliacoes"] if a["utilidade"] is not None]
            if len(us) > 1:
                candidatas.append((max(us) - min(us), lado, d))
    linhas = []
    for _, lado, d in sorted(candidatas, key=lambda x: -x[0])[:4]:
        opcoes = "; ".join(
            f"{a['acao']} P {_num(a['p'], 3)}" + (f", {a['custo']} MP" if a["custo"] else "")
            for a in sorted(d["avaliacoes"], key=lambda a: -(a["utilidade"] or 0))
        )
        linhas.append(
            f"- Rodada {d['rodada']}, {nomes[lado]} (HP {d['hp'][0]}/{d['hp'][1]}, MP "
            f"{d['mp'][0]}; o outro com HP {d['hp_dele'][0]}/{d['hp_dele'][1]}): escolheu "
            f"**{d['acao']}**. Opções: {opcoes}. A `PoliticaCopa` faria {d['politica_copa']} "
            f"({d['motivo_politica_copa']})."
        )
    return linhas or ["- Só uma ação legal na maior parte das rodadas."]


def relatorio_md(m: dict) -> str:
    dv = m["dados"]
    part = {p["id"]: p for p in dv["participantes"]}
    campeao = part[dv["campeao"]]
    final = next(j for j in dv["partidas"] if j["fase"] == "final")
    linhas = [
        f"# {m['copa']}",
        "",
        f"Campeão: **{campeao['nome']} ({campeao['id']})**, OP {_num(campeao['op'])}, "
        f"{campeao['perfil_pt']} · política "
        f"{POLITICAS_PT.get(campeao['politica'], campeao['politica'])}. "
        f"Final: {final['titulo']} — {final['rodadas']} rodadas. Na Copa original o campeão foi "
        f"{_nome(m['dados_original']['campeao'], part)}.",
        "",
        "Os mesmos 64 Guerreiros extraídos do PvE real da Copa Arena 03, a mesma chave e as mesmas "
        "seeds; os dois lados de cada partida conduzidos pela IA estratégica em vez da "
        "`PoliticaCopa`. Este relatório compara as duas Copas com a mesma régua e não declara "
        "mudança de força real das builds a partir de uma eliminatória — o ranking Bradley-Terry "
        "da Copa 03 continua sendo a referência.",
        "",
    ]
    linhas += _integridade_md(m)
    linhas += _metodo_md(m)
    linhas += _comparacao_md(m)
    linhas += _controlados_md(m)
    linhas += _economia_md(m)
    linhas += _builds_md(m)
    linhas += _rodizio_md(m)
    linhas += ["## Três lutas em detalhe", ""]
    for luta_ in m["lutas"]:
        linhas += _luta_md(luta_, part)
    linhas += _resultados_md(m)
    linhas += [
        "## Limitações",
        "",
        "- O adversário é modelado: até as cartas dele aparecerem, a IA supõe um deck como o "
        "dela; até a tela revelar procs e roubo de vida, supõe metade dos dela. Contra uma build "
        "muito diferente, as primeiras rodadas são decididas com um modelo errado.",
        "- A corrida depois do horizonte é uma estimativa: ela supõe o MP gasto da melhor forma e "
        "não conta cartas de buff e de status depois do horizonte. As estimativas de P(vitória) "
        "ordenam bem, mas não são probabilidades calibradas no começo da luta.",
        "- Uma Copa eliminatória com uma seed por partida não mede força de build. Os confrontos "
        "controlados medem o controlador; o Bradley-Terry da Copa 03, as builds.",
        "",
    ]
    return "\n".join(linhas)


def _resultados_md(m: dict) -> list[str]:
    dv = m["dados"]
    part = {p["id"]: p for p in dv["participantes"]}
    linhas = ["## As 63 partidas da v2", ""]
    tabela = []
    for j in dv["partidas"]:
        tabela.append(
            [
                j["chave"],
                _nome(j["p1"], part),
                _nome(j["p2"], part),
                _nome(j["vencedor"], part),
                j["rodadas"],
                f"{j['hp_vencedor']}/{j['hp_max_vencedor']}",
                _sinal(j["delta_op"]) + (" (zebra)" if j["zebra"] else ""),
            ]
        )
    linhas += _tabela(
        ["Partida", "Lado 1", "Lado 2", "Vencedor", "Rod.", "HP final", "ΔOP"], tabela
    )
    linhas.append("")
    return linhas


def decisoes_md(m: dict) -> str:
    dec = m["decisoes"]
    linhas = [
        f"# {m['copa']} — as decisões da IA",
        "",
        f"A IA tomou {dec['total']} decisões nas 63 partidas auditadas; em {dec['com_escolha']} "
        f"havia mais de uma ação legal (sem contar a rendição). Nessas, ela escolheu o mesmo que a "
        f"`PoliticaCopa` escolheria NA MESMA VISÃO em {dec['concordou']} "
        f"({_pct(dec['concordou'], dec['com_escolha'])}) e divergiu em "
        f"{dec['com_escolha'] - dec['concordou']}.",
        "",
        "A `PoliticaCopa` é consultada em cada visão só para registro — ela não influencia a "
        "escolha. As explicações abaixo usam apenas o que estava disponível no momento: a visão "
        "(HP/MP dos dois, efeitos e buffs visíveis, ações legais, recargas) e as estimativas que a "
        "IA calculou com o modelo dela do adversário.",
        "",
        "## Onde divergiram",
        "",
    ]
    linhas += _tabela(
        ["A PoliticaCopa faria", "A IA fez", "Vezes"],
        [[pc, ia_, n] for (pc, ia_), n in dec["categorias"]],
    )
    linhas += [
        "",
        "## Por quê, caso a caso",
        "",
        "Em cada categoria, o caso em que a IA via mais diferença entre a escolha dela e a da "
        "política:",
        "",
    ]
    explicacao = {
        ("buff", "dano"): "a política lança todo buff que não está ativo; a IA compara o buff "
        "com o golpe que ele substitui, e o buff só vence quando ainda há oportunidades "
        "suficientes "
        "para ele render",
        ("status", "dano"): "a política aplica todo status que o alvo não carrega; a IA mede o que "
        "o status muda nas próximas rodadas contra o dano que se perde nesta",
        ("dano", "básico"): "a política gasta a primeira carta de dano legal; a IA guarda o MP "
        "quando ele compra mais depois — uma cura que vai ser necessária, a carta condicional que "
        "vai valer mais, ou simplesmente quando o básico já resolve",
        ("básico", "dano"): "nenhuma regra da política pedia carta; a IA viu dano que compensava "
        "o MP",
        ("redução de dano", "dano"): "a política ergue toda redução de dano inativa; a IA só a "
        "ergue quando o dano que ela evita no tempo que dura passa o golpe que se perde",
        ("dano", "dano"): "a política pega a primeira carta de dano na ordem do deck; a IA pega a "
        "de maior valor esperado no estado — bônus situacional, chance de derrubar, recarga",
        ("cura", "dano"): "a política cura com HP até a metade; a IA corre quando o golpe dela "
        "chega antes do dele",
        ("dano", "cura"): "a IA curou antes da metade do HP, quando o próximo golpe do outro já "
        "derrubaria e ela age primeiro",
        ("buff", "básico"): "a política lança todo buff que não está ativo; a IA não lança buff "
        "quando ele não tem rodadas suficientes para render mais que o golpe que custa — no fim "
        "da luta, ou com o MP guardado para uma carta que vale mais",
        ("status", "básico"): "a política aplica todo status que o alvo não carrega; a IA só o "
        "aplica quando o que ele muda nas próximas rodadas passa o golpe desta e o MP",
        ("redução de dano", "básico"): "a política ergue toda redução de dano inativa; a IA "
        "guarda o MP quando o dano que a redução evitaria no tempo que dura é pequeno",
        ("buff", "status"): "a política prefere o buff ao status pela ordem das regras; a IA "
        "comparou os dois no motor",
        ("dano", "buff"): "a política gasta a carta de dano; a IA viu o buff render mais nas "
        "rodadas seguintes do que o golpe agora",
        ("cura", "básico"): "a política cura com HP até a metade; a IA não curou porque o dano "
        "do outro até o fim previsto não justificava a cura agora",
        ("redução de dano", "cura"): "a IA preferiu devolver HP a reduzir o dano que viria",
        ("status", "cura"): "a IA curou antes de aplicar status: sobreviver valia mais",
        ("buff", "cura"): "a IA curou antes de buffar: sobreviver valia mais",
    }
    for (pc, ia_), _ in dec["categorias"]:
        casos = dec["exemplos"].get((pc, ia_), [])[:2]
        linhas += [
            f"### A política: {pc} → a IA: {ia_}",
            "",
            "- Leitura: "
            f"{explicacao.get((pc, ia_), 'a avaliação no motor preferiu a outra ação')}.",
            "",
        ]
        for rotulo, d in zip(("O caso mais nítido", "Um caso típico"), casos):
            opcoes = "; ".join(
                f"{a['acao']} P {_num(a['p'], 3)}"
                + (f", {a['custo']} MP" if a["custo"] else "")
                + (
                    f", chance de derrubar {_pct(a['chance_letal'], 1)}"
                    if a["chance_letal"]
                    else ""
                )
                for a in sorted(d["avaliacoes"], key=lambda a: -(a["utilidade"] or 0))
            )
            linhas += [
                f"**{rotulo}.** {d['titulo']}, rodada {d['rodada']}, {d['nome']}. Na tela: HP "
                f"{d['hp'][0]}/"
                f"{d['hp'][1]}, MP {d['mp'][0]}/{d['mp'][1]}; o adversário com HP "
                f"{d['hp_dele'][0]}/{d['hp_dele'][1]}, MP {d['mp_dele'][0]}/{d['mp_dele'][1]}, "
                f"efeitos {', '.join(d['efeitos_dele']) or 'nenhum'}; buffs próprios "
                f"{', '.join(d['buffs']) or 'nenhum'}.",
                "",
                f"- A `PoliticaCopa` faria **{d['politica_copa']}**: {d['motivo_politica_copa']}.",
                f"- A IA fez **{d['acao']}** (justificativa registrada por ela): {d['motivo']}.",
                f"- Todas as opções avaliadas: {opcoes}.",
                "- Modelo do adversário naquele momento: ofensa "
                f"×{_num(d['modelo']['fator_ofensa'], 2)}, "
                f"defesa ×{_num(d['modelo']['fator_defesa'], 2)} sobre a priori; cartas reveladas: "
                f"{', '.join(d['modelo']['cartas_reveladas']) or 'nenhuma'}.",
                "",
            ]
    cv = m["conducao"]
    linhas += [
        "## Os ataques básicos da IA",
        "",
        f"{cv['basicos']} básicos em {cv['acoes']} ações ({_pct(cv['basicos'], cv['acoes'])}). "
        "Motivo de cada um:",
        "",
    ]
    linhas += _tabela(
        ["Motivo", "Básicos"],
        [
            [
                ROTULO_DO_MOTIVO[mot],
                f"{cv['basicos_por_motivo'][mot]} "
                f"({_pct(cv['basicos_por_motivo'][mot], cv['basicos'])})",
            ]
            for mot in MOTIVOS
        ],
    )
    linhas.append("")
    return "\n".join(linhas)


def final_md(m: dict, final) -> str:
    """A auditoria integral da final, como nas Copas anteriores, e as avaliações da IA."""
    texto = relatorio_final(final, copa=COPA_IA)
    lt = next(x for x in m["lutas"] if x["chave"] == "final-1")
    part = {p["id"]: p for p in m["dados"]["participantes"]}
    nomes = {lado: part[lt["jogo"][lado]]["nome"] for lado in SIDES}
    extra = ["", "## As decisões da IA na final, rodada a rodada", ""]
    for lado in SIDES:
        extra += [f"### {nomes[lado]} ({lt['jogo'][lado]})", ""]
        for d in lt["decisoes"].get(lado, []):
            opcoes = "; ".join(
                f"{a['acao']} {_num(a['p'], 3) if a['p'] is not None else '—'}"
                for a in sorted(d["avaliacoes"], key=lambda a: -(a["utilidade"] or 0))
            )
            extra.append(
                f"- R{d['rodada']}: **{d['acao']}** — {d['motivo']}. Opções: {opcoes}. "
                f"PoliticaCopa: {d['politica_copa']}."
            )
        extra.append("")
    return texto + "\n" + "\n".join(extra)


def trace_da_final(m: dict, final) -> dict:
    trace = trace_json(final, copa=COPA_IA, semente_principal=SEMENTE_PRINCIPAL)
    lt = next(x for x in m["lutas"] if x["chave"] == "final-1")
    trace["decisoes_ia"] = lt["decisoes"]
    return trace


# --- HTML ----------------------------------------------------------------------------------


def _e(texto) -> str:
    return c2._e(texto)


def _html_texto(frase: str) -> str:
    return c2._texto(frase.replace("**", ""))


def _kpi(rotulo: str, valor: str, nota: str = "") -> str:
    return (
        f'<div class="kpi"><div class="kl">{_e(rotulo)}</div><div class="kv">{_e(valor)}</div>'
        f'<div class="kl">{_e(nota)}</div></div>'
    )


def _barras_pareadas(itens: list[tuple[str, float, float]], fmt: str) -> str:
    """Original e v2 lado a lado, uma barra de cada por rótulo."""
    barras = []
    for rotulo, a, b in itens:
        barras.append(
            (f"{rotulo} · original", a, COR_ORIGINAL, f"{rotulo}, original: {fmt.format(a)}")
        )
        barras.append((f"{rotulo} · v2", b, COR_IA, f"{rotulo}, v2: {fmt.format(b)}"))
    return c2.svg_barras(barras, rotulo_w=230, fmt=fmt)


def _graficos(m: dict) -> dict:
    co, cv = m["conducao_original"], m["conducao"]
    tipos = sorted(set(co["skills_por_tipo"]) | set(cv["skills_por_tipo"]))
    nomes_tipo = {
        "damage": "dano",
        "heal": "cura",
        "buff": "buff",
        "status": "status",
        "damage_reduction": "redução de dano",
    }
    e = m["controlados"]["espelho"]["por_arquetipo"]
    return {
        "rodadas_original": c2.svg_colunas(Counter(co["rodadas"]), titulo="Rodadas por partida"),
        "rodadas_ia": c2.svg_colunas(Counter(cv["rodadas"]), titulo="Rodadas por partida"),
        "motivos": _barras_pareadas(
            [
                (
                    MOTIVO_CURTO[mot],
                    100 * co["basicos_por_motivo"][mot] / max(1, co["basicos"]),
                    100 * cv["basicos_por_motivo"][mot] / max(1, cv["basicos"]),
                )
                for mot in MOTIVOS
            ],
            "{:.1f}%",
        ),
        "tipos": _barras_pareadas(
            [
                (
                    nomes_tipo.get(t, t),
                    co["skills_por_tipo"].get(t, 0),
                    cv["skills_por_tipo"].get(t, 0),
                )
                for t in tipos
            ],
            "{:.0f}",
        ),
        "arquetipos": c2.svg_barras(
            [
                (arq, 100 * k / n if n else 0.0, COR_IA, f"{arq}: a IA venceu {k} de {n}")
                for arq, (k, n) in e.items()
            ],
            rotulo_w=110,
            fmt="{:.1f}%",
        ),
        "chave": c2.svg_chave(m["dados"]),
    }


def _linhas(tabela: list[list]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{_html_texto(str(c))}</td>" for c in linha) + "</tr>"
        for linha in tabela
    )


def _valores_comuns(m: dict) -> dict:
    dv, do = m["dados"], m["dados_original"]
    part = {p["id"]: p for p in dv["participantes"]}
    co, cv = m["conducao_original"], m["conducao"]
    ctrl = m["controlados"]
    esp, cru = ctrl["espelho"], ctrl["cruzado"]
    campeao, antigo = part[dv["campeao"]], part[do["campeao"]]
    svgs = _graficos(m)
    kpis = "".join(
        [
            _kpi("Campeão v2", campeao["nome"], f"{campeao['id']} · OP {_num(campeao['op'])}"),
            _kpi("Campeão original", antigo["nome"], f"{antigo['id']} · OP {_num(antigo['op'])}"),
            _kpi(
                "Rodadas por partida",
                f"{_num(_media(cv['rodadas']), 1)}",
                f"original {_num(_media(co['rodadas']), 1)} · máx {max(cv['rodadas'])} (era "
                f"{max(co['rodadas'])})",
            ),
            _kpi(
                "Ações que foram básico",
                _pct(cv["basicos"], cv["acoes"]),
                f"original {_pct(co['basicos'], co['acoes'])}",
            ),
            _kpi(
                "Maior sequência de básicos",
                str(cv["max_basicos_seguidos"]),
                f"original {co['max_basicos_seguidos']}",
            ),
            _kpi(
                "Zebras por OP",
                str(len(dv["agregados"]["zebras"])),
                f"original {len(do['agregados']['zebras'])}",
            ),
        ]
    )
    kpis_ctrl = "".join(
        [
            _kpi(
                "Espelho: IA vence",
                _pct(esp["vitorias"], esp["n"]),
                f"{esp['vitorias']} de {esp['n']} duelos",
            ),
            _kpi(
                "Cruzado: IA vence",
                _pct(cru["vitorias"], cru["n"]),
                f"{cru['vitorias']} de {cru['n']} duelos",
            ),
            _kpi(
                "Concordância com a política",
                _pct(*esp["concordancia"]),
                "decisões da IA nos espelhos",
            ),
            _kpi(
                "Inconclusivos",
                str(esp["inconclusivos"] + cru["inconclusivos"]),
                "limite técnico de 500 rodadas",
            ),
        ]
    )
    a, b = esp["ia"], esp["pc"]
    competencia = [
        ["Ações que foram básico", _pct(a["fracao_basicos"], 1), _pct(b["fracao_basicos"], 1)],
        [
            "Maior sequência de básicos (média)",
            _num(a["media_max_basicos"]),
            _num(b["media_max_basicos"]),
        ],
        ["Skills por duelo", _num(a["skills_por_lado"], 1), _num(b["skills_por_lado"], 1)],
        ["MP gasto / disponível", _pct(a["fracao_mp_gasto"], 1), _pct(b["fracao_mp_gasto"], 1)],
        ["MP no fim do duelo", _num(a["mp_final_por_lado"], 0), _num(b["mp_final_por_lado"], 0)],
        [
            "Regeneração perdida no teto",
            _num(a["regen_perdida_por_lado"], 1),
            _num(b["regen_perdida_por_lado"], 1),
        ],
        ["Dano de skill por 100 MP", _num(a["dano_por_100mp"], 1), _num(b["dano_por_100mp"], 1)],
        ["Cura além do HP que faltava", _pct(a["cura_excedente"], 1), _pct(b["cura_excedente"], 1)],
        ["Controle/status/buff redundantes", a["redundantes"], b["redundantes"]],
    ]
    cal = m["calibracao"]
    pf = m["primeira_fase"]
    builds = []
    for arq in ARQUETIPOS:
        x, y = m["por_build_original"]["arquetipo"][arq], m["por_build"]["arquetipo"][arq]
        k, n = esp["por_arquetipo"][arq]
        builds.append(
            [
                arq,
                x["gladiadores"],
                f"{x['vitorias']}/{x['disputas']}",
                f"{y['vitorias']}/{y['disputas']}",
                f"{_num(x['alcance'])} → {_num(y['alcance'])}",
                f"{k}/{n} ({_pct(k, n)})",
            ]
        )
    for pol, pt in POLITICAS_PT.items():
        x, y = m["por_build_original"]["politica"][pol], m["por_build"]["politica"][pol]
        builds.append(
            [
                f"política {pt}",
                x["gladiadores"],
                f"{x['vitorias']}/{x['disputas']}",
                f"{y['vitorias']}/{y['disputas']}",
                f"{_num(x['alcance'])} → {_num(y['alcance'])}",
                "—",
            ]
        )
    dec = m["decisoes"]
    exemplos = []
    for (pc, ia_), _ in dec["categorias"][:6]:
        for d in dec["exemplos"].get((pc, ia_), [])[:1]:
            opcoes = "; ".join(
                f"{x['acao']} {_num(x['p'], 3)}"
                for x in sorted(d["avaliacoes"], key=lambda x: -(x["utilidade"] or 0))
            )
            exemplos.append(
                f'<div class="card"><h3>A política: {_e(pc)} → a IA: {_e(ia_)}</h3>'
                f"<p>{_e(d['titulo'])}, rodada {d['rodada']}, {_e(d['nome'])}: HP "
                f"{d['hp'][0]}/{d['hp'][1]}, "
                f"MP {d['mp'][0]}; o adversário com HP {d['hp_dele'][0]}/{d['hp_dele'][1]}.</p>"
                f"<p><b>PoliticaCopa:</b> {_e(d['politica_copa'])} — "
                f"{_e(d['motivo_politica_copa'])}</p>"
                f"<p><b>IA:</b> {_e(d['acao'])} — {_e(d['motivo'])}</p>"
                f'<p class="muted">P(vitória) por opção: {_e(opcoes)}</p></div>'
            )
    partidas = "".join(
        f"<tr><td>{_e(j['chave'])}</td><td>{_e(part[j['p1']]['nome'])}</td><td>{_e(part[j['p2']]['nome'])}</td>"
        f"<td><b>{_e(part[j['vencedor']]['nome'])}</b></td><td class=n>{j['rodadas']}</td>"
        f"<td class=n>{j['hp_vencedor']}/{j['hp_max_vencedor']}</td>"
        f"<td class=n>{_sinal(j['delta_op'])}{' zebra' if j['zebra'] else ''}</td></tr>"
        for j in dv["partidas"]
    )
    return {
        "estilo": c3r._recurso("estilo.css"),
        "subtitulo": _e(
            "Os mesmos 64 da Copa Arena 03, a mesma chave e as mesmas seeds; só o controlador "
            "mudou "
            f"(IA estratégica nos dois lados). Semente principal {SEMENTE_PRINCIPAL}."
        ),
        "kpis": kpis,
        "kpis_controlados": kpis_ctrl,
        "svg_rodadas_original": svgs["rodadas_original"],
        "svg_rodadas_ia": svgs["rodadas_ia"],
        "svg_motivos": svgs["motivos"],
        "svg_tipos": svgs["tipos"],
        "svg_arquetipos": svgs["arquetipos"],
        "svg_chave": svgs["chave"],
        "integridade": "".join(
            f"<li>{_e(nome)}: {'ok' if ok else 'FALHOU'}</li>" for nome, ok in m["verificacoes"]
        ),
        "linhas_comparacao": "".join(
            f"<tr><th>{_e(a)}</th><td>{_e(b)}</td><td>{_e(c)}</td></tr>"
            for a, b, c in m["comparacao"]
        ),
        "texto_viradas": _e(
            f"{len(pf['viradas'])} dos {pf['pares']} resultados da primeira fase mudaram com a "
            "troca de controlador."
        ),
        "linhas_viradas": "".join(
            f"<tr><td>{_e(v['chave'])}</td><td>{_e(part[v['antes']]['nome'])}</td>"
            f"<td><b>{_e(part[v['agora']]['nome'])}</b></td><td class=n>{v['rodadas_antes']} → "
            f"{v['rodadas_agora']}</td></tr>"
            for v in pf["viradas"]
        ),
        "linhas_builds": _linhas(builds),
        "linhas_competencia": "".join(
            f"<tr><td>{_e(a)}</td><td class=n>{_e(b)}</td><td class=n>{_e(c)}</td></tr>"
            for a, b, c in competencia
        ),
        "texto_calibracao": _e(
            f"Brier {_num(cal.get('brier', 0), 3)} em {cal['n']} estimativas de P(vitória) da "
            "ação escolhida, "
            "nos confrontos controlados (0,25 é o chute de 50%)."
        ),
        "linhas_calibracao": "".join(
            f"<tr><td>{_num(lo, 1)}–{_num(hi, 1)}</td><td class=n>{n_}</td><td "
            f"class=n>{_num(pm, 2)}</td>"
            f"<td class=n>{_pct(g, 1)}</td></tr>"
            for lo, hi, n_, pm, g in cal.get("faixas", [])
        ),
        "texto_decisoes": _e(
            f"{dec['com_escolha']} decisões com mais de uma ação legal; a IA fez o mesmo que a "
            "PoliticaCopa "
            f"faria na mesma visão em {_pct(dec['concordou'], dec['com_escolha'])} delas."
        ),
        "linhas_divergencias": "".join(
            f"<tr><td>{_e(pc)}</td><td>{_e(ia_)}</td><td class=n>{n}</td></tr>"
            for (pc, ia_), n in dec["categorias"]
        ),
        "exemplos": "".join(exemplos),
        "linhas_partidas": partidas,
        "aviso_economia": _e(
            f"Economia de MP: regeneração média {_num(m['economia']['regen_media'], 1)} por turno "
            "contra custo "
            f"médio de carta {_num(m['economia']['custo_medio'], 1)} — depois do caixa inicial, "
            "uma carta a cada "
            f"{_num(m['economia']['rodadas_por_skill'], 1)} rodadas. Nenhuma regra foi mudada."
        ),
    }


def _luta_html(lt: dict, part: dict, *, pagina: bool) -> str:
    j = lt["jogo"]
    nomes = {lado: part[j[lado]]["nome"] for lado in SIDES}
    rotulos = [str(x["n"]) for x in lt["linhas"]]
    hp = c3r.svg_linhas_n(
        [
            (nomes[lado], [max(0, x["hp"][lado]) for x in lt["linhas"]], cor)
            for lado, cor in (("p1", "var(--c-serie)"), ("p2", "var(--c-hard)"))
        ],
        rotulos,
        titulo="HP ao fim de cada rodada",
        fmt="{:.0f}",
    )
    mp = c3r.svg_linhas_n(
        [
            (nomes[lado], [x["mp"][lado] for x in lt["linhas"]], cor)
            for lado, cor in (("p1", "var(--c-serie)"), ("p2", "var(--c-hard)"))
        ],
        rotulos,
        titulo="MP ao fim de cada rodada",
        fmt="{:.0f}",
    )
    ps = [
        (
            nomes[lado],
            [
                x["lados"][lado]["p"] if x["lados"][lado]["p"] is not None else float("nan")
                for x in lt["linhas"]
            ],
            cor,
        )
        for lado, cor in (("p1", "var(--c-serie)"), ("p2", "var(--c-hard)"))
    ]
    ps = [
        (n, [v if v == v else (vs[i - 1] if i else 0.5) for i, v in enumerate(vs)], c)
        for n, vs, c in ps
    ]
    for _, vs, _ in ps:
        for i in range(1, len(vs)):
            if vs[i] != vs[i]:
                vs[i] = vs[i - 1]
    estimativas = c3r.svg_linhas_n(ps, rotulos, titulo="P(vitória) estimada pela IA", fmt="{:.2f}")

    def celulas(x: dict, lado: str) -> str:
        acao = x["lados"][lado]
        desfecho = "" if acao["desfecho"] == "executed" else f" ({_e(acao['desfecho'])})"
        p = "—" if acao["p"] is None else _num(acao["p"], 2)
        return (
            f"<td>{_e(acao['acao'])}{desfecho}</td><td class=n>{acao['dano']}</td>"
            f"<td class=n>{x['hp'][lado]}</td><td class=n>{x['mp'][lado]}</td><td class=n>{p}</td>"
        )

    linhas = "".join(
        f"<tr><td class=n>{x['n']}</td><td>{_e(nomes[x['primeiro']])}</td>"
        + "".join(celulas(x, lado) for lado in SIDES)
        + "</tr>"
        for x in lt["linhas"]
    )
    cabecalho = (
        "<thead><tr><th class=n>Rod.</th><th>Primeiro</th>"
        + "".join(
            f"<th>{_e(nomes[lado])}</th><th class=n>Dano</th><th class=n>HP</th><th "
            "class=n>MP</th><th class=n>P</th>"
            for lado in SIDES
        )
        + "</tr></thead>"
    )
    momentos = "".join(f"<li>{_html_texto(f)}</li>" for f in lt["momentos"])
    resumo = (
        f"{_e(part[j['p1']]['nome'])} (OP {_num(j['op']['p1'])}) × {_e(part[j['p2']]['nome'])} "
        f"(OP {_num(j['op']['p2'])}) · seed {_e(lt['seed'])} · venceu "
        f"<b>{_e(part[j['vencedor']]['nome'])}</b> "
        f"em {j['rodadas']} rodadas"
    )
    if lt["original"]:
        o = lt["original"]
        resumo += (
            f" · na Copa original, nesta posição: {_e(part[o['p1']]['nome'])} × "
            f"{_e(part[o['p2']]['nome'])}, "
            f"venceu {_e(part[o['vencedor']]['nome'])} em {o['rodadas']}"
        )
    if pagina:
        return (
            f'<div class="pagina"><h2>{_e(lt["titulo"])}</h2><p class="aviso">{resumo}</p>'
            f'<div class="duas"><div><h3>HP</h3>{hp}</div><div><h3>P(vitória) '
            f"estimada</h3>{estimativas}</div></div>"
            f"<h3>Momentos decisivos</h3><ul>{momentos}</ul></div>"
        )
    return (
        f'<div class="card"><h3>{_e(lt["titulo"])}</h3><p>{resumo}</p>'
        '<div class="grid2">'
        f"<div><h4>HP ao fim de cada rodada</h4>{hp}</div>"
        f"<div><h4>P(vitória) estimada pela IA</h4>{estimativas}</div></div>"
        f'<div class="grid2"><div><h4>MP ao fim de cada rodada</h4>{mp}</div>'
        f"<div><h4>Momentos decisivos</h4><ul>{momentos}</ul></div></div>"
        "<details><summary>Rodada a rodada</summary><div "
        f'class="rolagem"><table>{cabecalho}<tbody>{linhas}'
        "</tbody></table></div></details></div>"
    )


def dashboard_html(m: dict) -> str:
    valores = _valores_comuns(m)
    part = {p["id"]: p for p in m["dados"]["participantes"]}
    valores["lutas"] = "".join(_luta_html(lt, part, pagina=False) for lt in m["lutas"])
    return c2._preencher((ASSETS / "dashboard.html").read_text(encoding="utf-8"), valores)


def visual_html(m: dict) -> str:
    valores = _valores_comuns(m)
    part = {p["id"]: p for p in m["dados"]["participantes"]}
    valores["lutas"] = "".join(_luta_html(lt, part, pagina=True) for lt in m["lutas"])
    return c2._preencher((ASSETS / "visual.html").read_text(encoding="utf-8"), valores)


# --- escrever ------------------------------------------------------------------------------


def confrontos_json(controlados: list[dict], variantes: dict | None) -> dict:
    """Os confrontos controlados, um por linha, e o teste de orçamento: o dado bruto."""
    campos = (
        "tipo",
        "a",
        "b",
        "ia",
        "lado_a",
        "lado_ia",
        "seed",
        "vencedor",
        "ia_venceu",
        "rodadas",
    )
    return {
        "campos": list(campos),
        "confrontos": [[r[c] for c in campos] for r in controlados],
        "orcamento": variantes or {},
    }


def escrever_tudo(
    nova,
    decisoes,
    original,
    verificacoes,
    controlados,
    variantes=None,
    pasta: Path = PASTA_IA,
    *,
    pdf: bool = True,
) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    m = modelo(nova, decisoes, original, verificacoes, controlados, variantes)
    final = nova.fases["final"][0]
    saidas = {
        ARQUIVO_RELATORIO: relatorio_md(m) + "\n",
        ARQUIVO_DECISOES: decisoes_md(m) + "\n",
        ARQUIVO_FINAL: final_md(m, final) + "\n",
        ARQUIVO_TRACE: json.dumps(trace_da_final(m, final), ensure_ascii=False, indent=1) + "\n",
        ARQUIVO_DASHBOARD: dashboard_html(m),
        ARQUIVO_CONFRONTOS: json.dumps(confrontos_json(controlados, variantes), ensure_ascii=False)
        + "\n",
    }
    caminhos = []
    for nome, texto in saidas.items():
        (pasta / nome).write_text(texto, encoding="utf-8")
        caminhos.append(pasta / nome)
    if pdf:
        motivo = c2.imprimir_pdf(visual_html(m), pasta / ARQUIVO_PDF)
        if motivo is None:
            caminhos.append(pasta / ARQUIVO_PDF)
        else:
            print(motivo)
    return caminhos
