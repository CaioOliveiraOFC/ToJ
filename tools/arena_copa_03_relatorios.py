"""Relatórios da Copa Arena 03: a geração PvE, o campeonato, o dashboard e o PDF.

Dois modelos em dado puro, e tudo sai deles:

- `modelo_geracao(pasta)` lê `runs.jsonl` e `gladiadores.json`: mortes,
  extrações, OP, andares, builds, o efeito medido da agenda de risco;
- `modelo(copa, diagnostico, geracao)` lê as partidas reais e o trace da
  auditoria, como na Copa 02, mais o diagnóstico de RNG do duelo.

O Markdown, o dashboard e o PDF leem esses modelos. A partida, a final e os
gráficos genéricos vêm da Copa 02 (`tools/arena_copa_02_relatorios.py`); aqui
fica o que é próprio desta Copa: perfis e políticas no lugar de classes, a
geração e o diagnóstico de RNG. Os modelos de página ficam em
`tools/arena_copa_03_assets/`.

Nenhum número é estimado fora do motor ou do registro das runs.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

from src.content.gladiator import prepare_gladiator
from src.content.passives import get_passive_by_id
from src.content.skills_loader import get_skill_by_id
from src.mechanics.pvp_duel import SIDES, opponent_of
from tools import arena_copa_02_relatorios as c2
from tools.arena_copa_02 import FASES, NOME_DA_FASE, faixa_de
from tools.arena_copa_02_relatorios import (
    FONTE,
    _e,
    _escala,
    _grade_y,
    _lista_diagnostico,
    _preencher,
    _texto,
    svg_barras,
)
from tools.arena_copa_03 import (
    ARQUIVO_DIAGNOSTICO,
    ARQUIVO_GLADIADORES,
    ARQUIVO_PILOTO,
    ARQUIVO_PLANO,
    ARQUIVO_RUNS,
    ARQUIVO_RUNS_PREENCHIMENTO,
    COPA,
    PERFIL_PT,
    REPETICOES,
    todas,
)
from tools.arena_copa_03 import arquetipos as ler_arquetipos
from tools.arena_copa_03_geracao import (
    FAIXA,
    FAIXA_DE_OP,
    GRUPOS,
    LINHA_CANONICA,
    PASSO,
    PERFIS,
    PISO,
    POLITICAS,
    PRESERVA_DESDE,
    QUOTAS,
    SEMENTE_PRINCIPAL,
    TETO,
    agenda,
    linha_base,
)
from tools.arena_copa_teste import (
    LIMITE_TECNICO,
    _bloco_da_partida,
    _diagnostico_final,
    relatorio_final,
    trace_json,
)

ARQUIVO_GERACAO = "geracao.md"
ARQUIVO_RELATORIO = "relatorio.md"
ARQUIVO_FINAL = "final_detalhada.md"
ARQUIVO_TRACE = "final_trace.json"
ARQUIVO_DASHBOARD = "dashboard.html"
ARQUIVO_PDF = "relatorio_visual.pdf"
RECURSOS = Path(__file__).resolve().parent / "arena_copa_03_assets"
COPA_02 = Path(__file__).resolve().parents[1] / "reports" / "pvp" / "copa_02" / "dashboard.html"
COR_PERFIL = {
    "conservador": "var(--c-con)",
    "moderado": "var(--c-mod)",
    "hardcore": "var(--c-hard)",
}
ARQUETIPOS = ("crítico", "defesa", "controle", "sustento")
ORIGEM_PT = {
    "original": "seleção original",
    "hardcore_adicional": "hardcore adicional do checkpoint",
    "preenchimento_checkpoint": "preenchimento (qualificada do checkpoint)",
    "preenchimento_novo": "preenchimento (run nova)",
}
RARIDADES = ("Common", "Rare", "Epic", "Legendary")
RARIDADE_PT = {"Common": "Comum", "Rare": "Rara", "Epic": "Épica", "Legendary": "Lendária"}
AVISO_NOMES = (
    "Os nomes são apenas identificadores fictícios de personagens simulados, tirados de canais "
    "da Twitch. Não existe participação, autorização ou endosso dessas pessoas. Os nicknames "
    "foram sorteados independentemente das builds, dos perfis e da chave."
)
AVISO_ESTATISTICA = (
    "Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por "
    "confronto. Ela aponta casos para investigar; não prova balanceamento."
)
AVISO_CAUSAL = (
    "Perfil, política, RNG da jornada e RNG do duelo atuam juntos em cada gladiador. As "
    "tabelas mostram associações observadas nesta amostra, não efeitos causais isolados."
)


def _media(xs) -> float:
    xs = list(xs)
    return statistics.mean(xs) if xs else 0.0


def _mediana(xs) -> float:
    xs = list(xs)
    return statistics.median(xs) if xs else 0.0


def _pct(a: float, b: float) -> str:
    return f"{a / b:.1%}" if b else "—"


def _num(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}"


def _nome_carta(sid: str) -> str:
    return get_skill_by_id(sid).name


def _nome_passiva(pid: str) -> str:
    return get_passive_by_id(pid).name


# --- modelo da geração --------------------------------------------------------


def ler_runs(pasta: Path) -> list[dict]:
    texto = (pasta / ARQUIVO_RUNS).read_text(encoding="utf-8")
    return [json.loads(linha) for linha in texto.splitlines() if linha.strip()]


def _sobrevivencia(runs: list[dict], ate: int) -> list[float]:
    """Fração das runs que ENTROU viva em cada andar, de 1 a `ate`."""
    n = len(runs) or 1
    return [sum(1 for r in runs if r.get("andar", 0) >= f) / n for f in range(1, ate + 1)]


def _faixas_de_andar(ate: int) -> list[str]:
    return [f"{i * FAIXA + 1}-{(i + 1) * FAIXA}" for i in range((ate - 1) // FAIXA + 1)]


def _resumo_de(runs: list[dict]) -> dict:
    """Desfechos e telemetria de um conjunto de tentativas."""
    n = len(runs)
    mortes = [r for r in runs if r["desfecho"] == "morreu"]
    extracoes = [r for r in runs if r["desfecho"] == "extraiu"]
    medidas = [r for r in extracoes if r.get("op") is not None]
    qualificadas = [r for r in runs if r.get("qualificada")]
    decisoes = sum(r.get("decisoes", 0) for r in runs)
    divergentes = sum(r.get("divergencias", {}).get("total", 0) for r in runs)
    fatais = [r["fatal"] for r in mortes if r.get("fatal")]
    return {
        "tentativas": n,
        "mortes": len(mortes),
        "extracoes": len(extracoes),
        "teto": sum(1 for r in runs if r["desfecho"] == "teto"),
        "erros": sum(1 for r in runs if r["desfecho"] == "erro"),
        "qualificadas": len(qualificadas),
        "aceitas": sum(1 for r in runs if r.get("situacao") == "aceita"),
        "sem_vaga": sum(1 for r in runs if r.get("situacao") == "qualificada_sem_vaga"),
        "acima": sum(1 for r in medidas if r["op"] > FAIXA_DE_OP[1]),
        "abaixo": sum(1 for r in medidas if r["op"] < FAIXA_DE_OP[0]),
        "invalidas": sum(1 for r in runs if r.get("situacao") == "rejeitada_snapshot"),
        "taxa_morte": len(mortes) / n if n else 0.0,
        "taxa_extracao": len(extracoes) / n if n else 0.0,
        "taxa_aprovacao": len(qualificadas) / len(extracoes) if extracoes else 0.0,
        "andar_medio_morte": _media(r["andar"] for r in mortes),
        "andar_mediano_morte": _mediana(r["andar"] for r in mortes),
        "mortes_ate_5": sum(1 for r in mortes if r["andar"] <= 5),
        "op_medio_extracao": _media(r["op"] for r in medidas),
        "op_extracoes": [r["op"] for r in medidas],
        "andar_medio_extracao": _media(r["andar"] for r in extracoes),
        "nivel_medio_extracao": _media(r["nivel"] for r in extracoes),
        "combates_por_run": _media(r.get("combates", 0) for r in runs),
        "fugas_por_run": _media(r.get("acoes", {}).get("flee", 0) for r in runs),
        "pocoes_por_run": _media(r.get("pocoes_bebidas", 0) for r in runs),
        "decisoes": decisoes,
        "divergentes": divergentes,
        "taxa_divergencia": divergentes / decisoes if decisoes else 0.0,
        "orcamentos": sum(r.get("divergencias", {}).get("orcamentos", 0) for r in runs),
        "orcamentos_divergentes": sum(
            r.get("divergencias", {}).get("orcamentos_divergentes", 0) for r in runs
        ),
        "hp_entrada_fatal": _mediana(f["hp_frac"] for f in fatais),
        "fatal_abaixo_de_55": sum(1 for f in fatais if f["hp_frac"] < 0.55),
        "ilegais": sum(r.get("ilegais", 0) for r in runs),
        "tempo_s": sum(r.get("tempo_s", 0) for r in runs),
    }


def _divergencia_por_faixa(runs: list[dict], faixas: list[str]) -> list[float]:
    """Decisões divergentes por 100 decisões de mapa, por faixa de andares."""
    saida = []
    for faixa in faixas:
        dec = sum(
            r.get("divergencias", {}).get("decisoes_por_faixa", {}).get(faixa, 0) for r in runs
        )
        div = sum(r.get("divergencias", {}).get("por_faixa", {}).get(faixa, 0) for r in runs)
        saida.append(100 * div / dec if dec else 0.0)
    return saida


def _banda_da_extracao(r: dict) -> str | None:
    preservadas = [e for e in r.get("extracao", ()) if e.get("preservar")]
    return preservadas[-1]["banda"] if preservadas else None


def _estatisticas_de_build(lista: list[dict]) -> dict:
    """Equipamento, cartas e passivas de um conjunto de builds (dicionários `build`)."""
    pecas = [peca for b in lista for peca in b["equipamento"].values()]
    familias, raridades_passiva, cartas, passivas = Counter(), Counter(), Counter(), Counter()
    arquetipos = Counter()
    for b in lista:
        familias.update(b["familias"])
        raridades_passiva.update(b["raridades"])
        cartas.update(_nome_carta(s) for s in b["deck"])
        passivas.update(_nome_passiva(p) for p in b["passivas"])
        arquetipos.update(ler_arquetipos(b) or ["sem canal dominante"])
    return {
        "builds": len(lista),
        "pecas": len(pecas),
        "pecas_por_build": len(pecas) / len(lista) if lista else 0.0,
        "raridade_pecas": dict(Counter(p["raridade"] for p in pecas)),
        "aprimoradas": sum(1 for p in pecas if p["mais"]),
        "mais_total": sum(p["mais"] for p in pecas),
        "mais_max": max((p["mais"] for p in pecas), default=0),
        "com_gema": sum(1 for p in pecas if p["gemas"]),
        "gemas": sum(p["gemas"] for p in pecas),
        "com_encanto": sum(1 for p in pecas if p["encantos"]),
        "encantos": sum(p["encantos"] for p in pecas),
        "starter": sum(1 for p in pecas if p.get("origem") == "starter"),
        "itens": Counter(p["nome"] for p in pecas).most_common(12),
        "familias": familias.most_common(),
        "raridade_passivas": dict(raridades_passiva),
        "cartas": cartas.most_common(),
        "passivas": passivas.most_common(15),
        "decks_distintos": len({tuple(sorted(b["deck"])) for b in lista}),
        "passivas_distintas": len({tuple(sorted(b["passivas"])) for b in lista}),
        "equipamentos_distintos": len(
            {tuple(sorted((k, v["nome"]) for k, v in b["equipamento"].items())) for b in lista}
        ),
        "arquetipos": arquetipos.most_common(),
    }


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def _piloto(pasta: Path) -> dict | None:
    """O piloto v1: a mesma geração com a matriz de extração canônica nos três perfis."""
    arquivo = pasta / ARQUIVO_PILOTO
    if not arquivo.exists():
        return None
    runs = [
        json.loads(linha) for linha in arquivo.read_text(encoding="utf-8").splitlines() if linha
    ]
    extracoes = [r for r in runs if r["desfecho"] == "extraiu" and r.get("op") is not None]
    janela = [
        e
        for r in runs
        for e in r.get("extracao", ())
        if e.get("banda") in ("CLOSE_ENOUGH", "META_BATIDA")
    ]
    return {
        "resumo": _resumo_de(runs),
        "por_perfil": {p: _resumo_de([r for r in runs if r["perfil"] == p]) for p in PERFIS},
        "bandas": dict(Counter(_banda_da_extracao(r) for r in extracoes)),
        "op_extracoes": sorted(r["op"] for r in extracoes),
        "janela": len(janela),
        "janela_continuou": sum(1 for e in janela if not e["preservar"]),
    }


def _marcantes(gladiadores: list[dict]) -> list[str]:
    """Builds que se destacam, apontadas DEPOIS da geração e só para o relatório."""
    if not gladiadores:
        return []

    def quem(g):
        return f"{g['nick']} ({g['id']}, {PERFIL_PT[g['perfil']]}/{g['politica']})"

    def mais(g):
        return sum(p["mais"] for p in g["equipamento"].values())

    def gemas(g):
        return sum(p["gemas"] for p in g["equipamento"].values())

    def criticas(g):
        return g["familias"].get("crit_chance", 0) + g["familias"].get("crit_damage", 0)

    def raras(g):
        return g["raridades"].get("Epic", 0) + g["raridades"].get("Legendary", 0)

    frases = []
    g = max(gladiadores, key=mais)
    frases.append(f"Mais trabalho de Ferreiro: {quem(g)}, `+{mais(g)}` somados nas peças.")
    g = max(gladiadores, key=gemas)
    frases.append(f"Mais gemas encaixadas: {quem(g)}, {gemas(g)}.")
    g = max(gladiadores, key=raras)
    frases.append(
        f"Mais passivas Épicas ou Lendárias: {quem(g)}, {raras(g)} "
        f"({g['raridades'].get('Legendary', 0)} Lendária(s))."
    )
    g = max(gladiadores, key=criticas)
    frases.append(f"Mais passivas de crítico: {quem(g)}, {criticas(g)}.")
    cartas = Counter(c for g in gladiadores for c in set(g["deck"]))
    unicas = [(c, g) for g in gladiadores for c in g["deck"] if cartas[c] == 1]
    if unicas:
        frases.append(
            "Cartas que só um dos 64 levou: "
            + "; ".join(f"{_nome_carta(c)} ({quem(g)})" for c, g in unicas[:8])
            + "."
        )
    fundo = max(gladiadores, key=lambda g: (g["andar_de_extracao"], g["op"]))
    raso = min(gladiadores, key=lambda g: (g["andar_de_extracao"], g["op"]))
    frases.append(
        f"Extração mais funda: {quem(fundo)}, andar {fundo['andar_de_extracao']}, nível "
        f"{fundo['nivel']}; mais rasa: {quem(raso)}, andar {raso['andar_de_extracao']}, nível "
        f"{raso['nivel']}."
    )
    forte = max(gladiadores, key=lambda g: g["op"])
    fraco = min(gladiadores, key=lambda g: g["op"])
    frases.append(
        f"Maior OP: {quem(forte)}, {forte['op']:.2f}; menor: {quem(fraco)}, {fraco['op']:.2f}."
    )
    return frases


def modelo_geracao(pasta: Path) -> dict:
    runs = ler_runs(pasta)
    gladiadores = json.loads((pasta / ARQUIVO_GLADIADORES).read_text(encoding="utf-8"))[
        "gladiadores"
    ]
    ate = max(r.get("andar", 1) for r in runs)
    faixas = _faixas_de_andar(min(ate, 30))
    por_grupo = {}
    for perfil, politica in GRUPOS:
        rs = [r for r in runs if (r["perfil"], r["politica"]) == (perfil, politica)]
        aceitas = sorted(r["tentativa"] for r in rs if r["situacao"] == "aceita")
        por_grupo[f"{perfil}/{politica}"] = dict(
            _resumo_de(rs),
            perfil=perfil,
            politica=politica,
            quota=QUOTAS[(perfil, politica)],
            ultima_aceita=max(aceitas),
            apos_a_quota=sum(1 for r in rs if r.get("apos_a_quota")),
        )
    por_perfil = {}
    for perfil in PERFIS:
        rs = [r for r in runs if r["perfil"] == perfil]
        pares = Counter()
        for r in rs:
            pares.update(r.get("divergencias", {}).get("pares", {}))
        bandas = Counter(_banda_da_extracao(r) for r in rs if r["desfecho"] == "extraiu")
        mortes_por_faixa = Counter(
            faixas[min(len(faixas) - 1, (r["andar"] - 1) // FAIXA)]
            for r in rs
            if r["desfecho"] == "morreu"
        )
        por_perfil[perfil] = dict(
            _resumo_de(rs),
            agenda=agenda(perfil, ate=min(ate, 30)),
            sobrevivencia=_sobrevivencia(rs, min(ate, 30)),
            divergencia_por_faixa=_divergencia_por_faixa(rs, faixas),
            pares=pares.most_common(8),
            trocas=sum(pares.values()),
            trocas_para_lutar=sum(n for par, n in pares.items() if par.endswith("→lutar")),
            bandas_na_extracao={str(k): v for k, v in bandas.items()},
            mortes_por_faixa={f: mortes_por_faixa.get(f, 0) for f in faixas},
        )
    por_politica = {
        politica: _resumo_de([r for r in runs if r["politica"] == politica])
        for politica in POLITICAS
    }
    extracoes = [r for r in runs if r["desfecho"] == "extraiu" and r.get("op") is not None]
    aceitos = gladiadores
    builds_aceitas = [
        {k: g[k] for k in ("deck", "passivas", "familias", "raridades", "equipamento")}
        for g in aceitos
    ]
    builds_extraidas = [r["build"] for r in runs if r["desfecho"] == "extraiu" and "build" in r]
    decks = {g["id"]: set(g["deck"]) for g in aceitos}
    jaccard_dentro, jaccard_fora = [], []
    for i, a in enumerate(aceitos):
        for b in aceitos[i + 1 :]:
            mesmo = (a["perfil"], a["politica"]) == (b["perfil"], b["politica"])
            (jaccard_dentro if mesmo else jaccard_fora).append(
                _jaccard(decks[a["id"]], decks[b["id"]])
            )
    diversidade = {}
    for perfil, politica in GRUPOS:
        membros = [g for g in aceitos if (g["perfil"], g["politica"]) == (perfil, politica)]
        familias = Counter()
        for g in membros:
            familias.update(g["familias"])
        diversidade[f"{perfil}/{politica}"] = {
            "n": len(membros),
            "op_medio": _media(g["op"] for g in membros),
            "nivel_medio": _media(g["nivel"] for g in membros),
            "andar_medio": _media(g["andar_de_extracao"] for g in membros),
            "familias": familias.most_common(3),
            "decks_distintos": len({tuple(sorted(g["deck"])) for g in membros}),
            "arquetipos": Counter(a for g in membros for a in g["arquetipos"]).most_common(),
        }
    op_aceitos = [g["op"] for g in aceitos]
    return {
        "semente_principal": SEMENTE_PRINCIPAL,
        "teto": TETO,
        "andar_maximo": ate,
        "faixas": faixas,
        "linha_canonica": LINHA_CANONICA,
        "passo": PASSO,
        "faixa": FAIXA,
        "piso": PISO,
        "linha_base": {p: linha_base(p) for p in PERFIS},
        "total": _resumo_de(runs),
        "por_grupo": por_grupo,
        "por_perfil": por_perfil,
        "por_politica": por_politica,
        "extracoes": [
            {
                "op": r["op"],
                "perfil": r["perfil"],
                "politica": r["politica"],
                "andar": r["andar"],
                "nivel": r["nivel"],
                "qualificada": bool(r.get("qualificada")),
                "situacao": r["situacao"],
                "banda": _banda_da_extracao(r),
            }
            for r in extracoes
        ],
        "aceitos": [
            {
                "id": g["id"],
                "nick": g["nick"],
                "perfil": g["perfil"],
                "politica": g["politica"],
                "op": g["op"],
                "nivel": g["nivel"],
                "andar": g["andar_de_extracao"],
                "tentativa": g["tentativa"],
                "seed": g["seed"],
                "arquetipos": g["arquetipos"],
                "origem": g.get("origem", "original"),
            }
            for g in aceitos
        ],
        "op_aceitos": {
            "media": _media(op_aceitos),
            "min": min(op_aceitos),
            "max": max(op_aceitos),
            "mediana": _mediana(op_aceitos),
        },
        "builds_aceitas": _estatisticas_de_build(builds_aceitas),
        "builds_extraidas": _estatisticas_de_build(builds_extraidas),
        "diversidade": diversidade,
        "jaccard": {"dentro": _media(jaccard_dentro), "entre": _media(jaccard_fora)},
        "piloto": _piloto(pasta),
        "marcantes": _marcantes(gladiadores),
        "preenchimento": _preenchimento(pasta),
        "distribuicao": {
            p: {
                pol: sum(1 for x in aceitos if (x["perfil"], x["politica"]) == (p, pol))
                for pol in POLITICAS
            }
            for p in PERFIS
        },
        "origens": dict(Counter(x.get("origem", "original") for x in aceitos)),
    }


# --- markdown da geração -----------------------------------------------------


def _tabela(cabecalho: list[str], linhas: list[list]) -> list[str]:
    saida = ["| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
    saida += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return saida + [""]


def _lista(pares, n: int = 99) -> str:
    return ", ".join(f"{k} ×{v}" for k, v in list(pares)[:n]) or "nenhum"


def geracao_md(g: dict) -> str:
    t = g["total"]
    b = g["builds_aceitas"]
    linhas = [
        f"# {COPA} — a geração: 64 Guerreiros extraídos do PvE real",
        "",
        "Gerado por `tools/arena_copa_03_geracao.py` e `tools/arena_copa_03.py`. Cada gladiador "
        "é um personagem que começou no nível 1 pela criação canônica de uma nova jornada, "
        "atravessou a dungeon jogado pelo BotPadrão (numa variante experimental de perfil e "
        "política) e saiu vivo pela Extração, com a Chave e o mecanismo do jogo.",
        "",
        f"> {AVISO_CAUSAL}",
        "",
        "## Resumo",
        "",
        f"- **Geração original: {t['tentativas']} runs**, {t['mortes']} mortes "
        f"({t['taxa_morte']:.1%}), {t['extracoes']} extrações ({t['taxa_extracao']:.1%}), "
        f"{t['teto']} chegaram ao teto técnico vivas e {t['erros']} erros técnicos.",
        *_resumo_do_preenchimento(g),
        f"- Das {t['extracoes']} extrações, {t['qualificadas']} ficaram na faixa de OP 20–30 "
        f"({_pct(t['qualificadas'], t['extracoes'])}); {t['acima']} passaram de 30 e "
        f"{t['abaixo']} ficaram abaixo de 20. {t['sem_vaga']} qualificada(s) chegaram depois de a "
        "quota do grupo fechar e ficaram de fora.",
        f"- OP dos 64 aceitos: média {g['op_aceitos']['media']:.2f}, mediana "
        f"{g['op_aceitos']['mediana']:.2f}, mínimo {g['op_aceitos']['min']:.2f}, máximo "
        f"{g['op_aceitos']['max']:.2f}.",
        f"- Nenhuma decisão de mapa fora das opções legais ({t['ilegais']} ilegais em "
        f"{t['decisoes']} decisões). A agenda de risco mudou {t['divergentes']} decisões "
        f"({t['taxa_divergencia']:.1%}) em relação ao que o cérebro canônico faria no mesmo "
        "estado.",
        f"- Horizonte técnico: {g['teto']} andares; o andar mais fundo alcançado foi "
        f"{g['andar_maximo']}. Tempo de CPU somado das runs: {t['tempo_s'] / 3600:.1f} h.",
        "",
    ]
    linhas += _protocolo_md(g)
    linhas += _alavancas_md(g)
    linhas += _piloto_md(g)
    linhas += _runs_md(g)
    linhas += _preenchimento_md(g)
    linhas += _perfis_md(g)
    linhas += _op_md(g)
    linhas += _andares_md(g)
    linhas += _builds_md(b, g["builds_extraidas"])
    linhas += _diversidade_md(g)
    linhas += ["## Builds marcantes", "", "Apontadas depois da geração, só para descrever.", ""]
    linhas += [f"- {frase}" for frase in g["marcantes"]] + [""]
    linhas += _risco_md(g)
    linhas += _aceitos_md(g)
    return "\n".join(linhas)


def _protocolo_md(g: dict) -> list[str]:
    linhas = [
        "## Protocolo",
        "",
        f"- **Seed.** Principal `{g['semente_principal']}`. Cada tentativa: os 8 primeiros "
        'bytes (big-endian) de `sha256(f"{seed}:v2:{perfil}:{politica}:{k}")` (o piloto v1 usou '
        '`sha256(f"{seed}:{perfil}:{politica}:{k}")`). Nenhuma seed foi '
        "repetida, e o checkpoint recusa seed ou tentativa duplicada.",
        "- **Run.** `BotPadrao` do repositório, classe `warrior`, criação por "
        "`create_player_for_new_run` com o gerador da run (nível 1, uma skill, Starter Kit "
        f"sorteado). Teto técnico de {g['teto']} andares, o mesmo das auditorias de progressão. "
        "Nenhum item concedido, nenhuma oferta escolhida à mão, nenhum atributo mexido.",
        "- **Variante experimental.** `BotExperimental` (subclasse em `tools/`) troca a política "
        "de escolha pelo atributo `picker` que o driver já consulta e aplica a agenda de risco "
        "do perfil: a linha de aposta a cada andar e a matriz de extração do perfil. O "
        "BotPadrão oficial, `src/` e as baselines não mudaram.",
        "- **Aceite.** Guerreiro; run terminada pela Extração; vivo; Chave gasta e marca de "
        "extração no andar certo; snapshot pela serialização canônica do save "
        "(`to_save_data`), reconstruído por `player_from_save_data` (o caminho da Arena) com "
        "a mesma assinatura de build, o mesmo deck, passivas, equipamento, HP/MP máximos e "
        "nível, e a ida e volta reproduzindo o snapshot; `overall_power(...)` do reconstruído, "
        "sem cache, entre 20 e 30; vaga no grupo.",
        "- **Ordem de aceite.** Dentro de cada grupo, as primeiras qualificadas pela ordem da "
        "tentativa, sem lacuna. Assim o resultado não depende de quantos processos rodaram nem "
        "de qual terminou antes. Tentativas que estavam em voo quando a quota fechou foram "
        "executadas e registradas.",
        "- **Isolamento.** A Extração passa por `extraction.finish_run` com gravação em memória; "
        "nenhum slot, `saves/` ou `trophies.json` foi tocado.",
        "- **Checkpoint.** Cada tentativa concluída foi gravada e sincronizada em disco no "
        "momento em que terminou; snapshots e estado da fila com escrita atômica. Retomar não "
        "repete runs nem mede de novo aceitos.",
        "- **Quirk registrado.** A recarga canônica do save soma 1 a `ledger.items_equipped` "
        "por peça reequipada. É telemetria do livro-caixa, não build; a conferência de ida e "
        "volta ignora só esse contador.",
        "",
    ]
    return linhas


def _alavancas_md(g: dict) -> list[str]:
    linhas = [
        "## A escalada de risco: o que decide e o que foi medido",
        "",
        "### O que foi verificado no BotPadrão",
        "",
        "- `Perfil.hp_engajar` e `Perfil.mp_engajar` (55/15, 45/10, 38/5) **não são lidos por "
        "nenhuma decisão**. O docstring de `ProgressionState` diz que ficaram no driver por "
        "compatibilidade, e `tests/test_bot_observation.py` proíbe que voltem ao estado. Os três "
        "perfis oficiais jogam runs idênticas; baixar esses números não aumentaria risco.",
        "- `DESVIO_ACEITAVEL`, `HP_SAUDAVEL`, `FOLGA_PARA_COMPRAR`, `HP_PARA_ALTAR` e "
        "`POCOES_PARA_SUSTENTAR` também não decidem mais nada; `_sinais_de_risco` só escreve "
        "no trace.",
        f"- O que decide no mapa é **um limiar**: `evaluators.HP_DE_APOSTA` "
        f"({g['linha_canonica']}). Ele mede a capacidade de cada luta (`hp − aposta`), "
        "decide quando curar vira SOBREVIVER ou RECUPERAR e quando a saída do andar vira "
        f"descanso. Do lado do driver, `bot_padrao.HP_CRITICO` ({g['linha_canonica']}) é a "
        "mesma linha: abaixo dela a Loja pode gastar a reserva da saída em recuperação.",
        "- **Continuar ou extrair** é a matriz `evaluators._MATRIZ` (banda da build contra o "
        "benchmark da Arena × fôlego observado). Não tem parâmetro; é outra constante de "
        "módulo lida no momento da chamada.",
        "- **Sem alavanca externa, e por isso canônicos nos três perfis:** MP (o mapa não tem "
        "limiar de mana; ela só pesa dentro do duelo), desvio voluntário (o adaptador enumera "
        "todo serviço alcançável) e o combate (fuga, cura, buff e controle).",
        "",
        "### Como a agenda foi aplicada",
        "",
        "As duas linhas e a matriz são constantes de módulo lidas no momento da chamada. A "
        "variante as sobrescreve em tempo de execução, só dentro da run experimental, e as "
        "devolve ao valor canônico no fim (verificado em todas as runs). Não é um ponto de "
        "configuração que o projeto já declarava: é a menor intervenção que muda risco de "
        "verdade sem duplicar regra nem avaliador. Nenhum arquivo de `src/` ou de "
        "`tools/bot_padrao.py` mudou.",
        "",
        "A linha de base sai do próprio perfil oficial: o driver documenta que o piso de "
        "engajamento fica 0,20 acima da linha crítica, então a linha do perfil é "
        f"`hp_engajar − 0,20`. Com a profundidade ela desce {g['passo']:.2f} a cada "
        f"{g['faixa']} andares, até o piso.",
        "",
    ]
    cab = ["Perfil", "Base", "Piso"] + g["faixas"][:6]
    corpo = [
        [PERFIL_PT[p], g["linha_base"][p], g["piso"][p]]
        + [g["por_perfil"][p]["agenda"].get(f, "") for f in g["faixas"][:6]]
        for p in PERFIS
    ]
    linhas += _tabela(cab, corpo)
    linhas += [
        "### A decisão de extrair, por perfil (v2)",
        "",
        "A matriz do perfil só ACRESCENTA preservação à canônica: a partir da banda indicada, "
        "o perfil preserva a build com qualquer fôlego; abaixo dela, e no hardcore inteiro, vale "
        "a canônica, que só preserva entre 0,95 e 1,05 do benchmark com o fôlego curto e acima "
        "de 1,05 sempre. O conservador sai mais cedo; o hardcore aposta mais.",
        "",
    ]
    linhas += _tabela(
        ["Perfil", "Preserva com qualquer fôlego a partir de", "OP equivalente"],
        [
            [
                PERFIL_PT[p],
                PRESERVA_DESDE.get(p, "HARD_STOP (canônica)"),
                {"CLOSE_ENOUGH": "≥ 27,7", "META_BATIDA": "≥ 29,17"}.get(
                    PRESERVA_DESDE.get(p, ""), "> 30,6"
                ),
            ]
            for p in PERFIS
        ],
    )
    linhas += [
        "### O efeito medido: decisões que a agenda mudou",
        "",
        "Em cada decisão de mapa, o mesmo estado foi avaliado de novo com a linha e a matriz "
        "canônicas (a decisão-sombra, sem consumir RNG). Uma divergência é uma decisão de "
        "família diferente (lutar em vez de beber, extrair em vez de seguir) num estado que a "
        "run realmente alcançou. O conservador nos andares 1–5 usa a linha canônica, então "
        "ali só a extração pode divergir.",
        "",
    ]
    cab = ["Perfil", "Decisões", "Divergentes", "Taxa"] + [f"/100 em {f}" for f in g["faixas"][:6]]
    corpo = []
    for p in PERFIS:
        v = g["por_perfil"][p]
        corpo.append(
            [PERFIL_PT[p], v["decisoes"], v["divergentes"], f"{v['taxa_divergencia']:.1%}"]
            + [f"{x:.1f}" for x in v["divergencia_por_faixa"][:6]]
        )
    linhas += _tabela(cab, corpo)
    for p in PERFIS:
        v = g["por_perfil"][p]
        linhas.append(
            f"- {PERFIL_PT[p]}: trocas mais frequentes (canônica→experimental) "
            f"{_lista(v['pares'], 6)}; orçamento da Loja com a reserva tratada diferente em "
            f"{v['orcamentos_divergentes']} de {v['orcamentos']} visitas."
        )
    taxas = {p: g["por_perfil"][p]["taxa_divergencia"] for p in PERFIS}
    ordem = sorted(PERFIS, key=lambda p: -taxas[p])
    trocas = sum(g["por_perfil"][p]["trocas"] for p in PERFIS)
    viraram_luta = sum(g["por_perfil"][p]["trocas_para_lutar"] for p in PERFIS)
    linhas += [
        "",
        "Leitura: a agenda mudou escolhas em estados alcançáveis em todos os perfis com linha "
        "diferente da canônica. Taxa de decisões mudadas, da maior para a menor: "
        + ", ".join(f"{PERFIL_PT[p]} {taxas[p]:.1%}" for p in ordem)
        + f". {viraram_luta} das {trocas} trocas foram para `lutar` (no lugar de "
        "beber poção, comprar cura, ir a um serviço ou sair para descansar). A agenda não "
        "desliga proteção: abaixo da linha o cérebro continua mandando curar ou sair, e a fuga "
        "dentro do duelo é a canônica.",
        "",
    ]
    return linhas


def _piloto_md(g: dict) -> list[str]:
    v = g.get("piloto")
    if not v:
        return []
    r = v["resumo"]
    ops = v["op_extracoes"]
    projecao = f"{64 * r['tentativas'] / max(1, r['qualificadas']):,.0f}".replace(",", ".")
    linhas = [
        "## O piloto v1 e a decisão de extrair",
        "",
        "A primeira versão da variante mexia só na linha de aposta e deixava a matriz de "
        "extração canônica nos três perfis. Ela rodou como piloto, com as seeds "
        '`sha256(f"{seed}:{perfil}:{politica}:{k}")`, e foi interrompida por decisão do '
        "usuário diante do resultado abaixo. Nenhuma build dela entrou na Copa; as runs estão "
        "em `runs_piloto.jsonl`.",
        "",
        f"- {r['tentativas']} runs: {r['mortes']} mortes, {r['extracoes']} extrações, "
        f"{r['qualificadas']} na faixa de OP 20–30.",
        f"- OP das extrações: de {min(ops):.2f} a {max(ops):.2f} (mediana {_mediana(ops):.2f}).",
        "- Banda da build quando o bot decidiu preservar: "
        + ", ".join(f"{k} ×{n}" for k, n in sorted(v["bandas"].items(), key=str))
        + ".",
        f"- Em {v['janela_continuou']} de {v['janela']} oportunidades de extração com a build "
        "entre 0,95 e 1,05 do benchmark (OP 27,7–30,6), a matriz canônica mandou continuar: o "
        "fôlego estava saudável.",
        f"- Projeção daquele ritmo: cerca de {projecao} runs para as 64 vagas, com os grupos "
        "do conservador e do moderado sem nenhuma extração na faixa.",
        "",
        "Por isso a v2 pôs a decisão de continuar ou extrair na agenda do perfil (seção "
        "anterior). O que não mudou: a dungeon, o motor, o `overall_power`, a faixa de OP, a "
        "linha de aposta e o critério de aceite.",
        "",
    ]
    return linhas


def _preenchimento(pasta: Path) -> dict | None:
    """As runs e o plano do preenchimento, separados da geração original."""
    plano_arq, runs_arq = pasta / ARQUIVO_PLANO, pasta / ARQUIVO_RUNS_PREENCHIMENTO
    if not plano_arq.exists() or not runs_arq.exists():
        return None
    plano = json.loads(plano_arq.read_text(encoding="utf-8"))
    runs = [json.loads(x) for x in runs_arq.read_text(encoding="utf-8").splitlines() if x]
    return {
        "plano": plano,
        "resumo": _resumo_de(runs),
        "por_perfil": {
            p: _resumo_de([r for r in runs if r["perfil"] == p])
            for p in ("conservador", "moderado")
        },
        "por_grupo": plano.get("grupos_do_preenchimento", {}),
    }


def _resumo_do_preenchimento(g: dict) -> list[str]:
    pre = g.get("preenchimento")
    original = [a for a in g["aceitos"] if a["origem"] == "original"]
    por_perfil = Counter(a["perfil"] for a in original)
    linhas = [
        "- **Seleção original: "
        f"{len(original)} aceitos** (conservador {por_perfil['conservador']}/22, moderado "
        f"{por_perfil['moderado']}/21, hardcore {por_perfil['hardcore']}/21). As quotas "
        "22/21/21 NÃO foram cumpridas: o hardcore ficou em "
        f"{por_perfil['hardcore']}/21.",
    ]
    if pre:
        r = pre["resumo"]
        novos = sum(1 for a in g["aceitos"] if a["origem"].startswith("preenchimento"))
        linhas.append(
            f"- **Preenchimento: {novos} vagas**, por decisão do usuário, com {r['tentativas']} "
            f"runs novas de conservador e moderado ({r['mortes']} mortes, {r['extracoes']} "
            f"extrações, {r['qualificadas']} na faixa)."
        )
    final = Counter(a["perfil"] for a in g["aceitos"])
    linhas.append(
        f"- **Os 64 por perfil:** conservador {final['conservador']}, moderado "
        f"{final['moderado']}, hardcore {final['hardcore']}."
    )
    return linhas


def _preenchimento_md(g: dict) -> list[str]:
    pre = g.get("preenchimento")
    if not pre:
        return []
    plano, r = pre["plano"], pre["resumo"]
    linhas = [
        "## O preenchimento",
        "",
        plano["decisao"],
        "",
        f"- Seleção original mantida inteira: {len(plano['selecao_original'])} gladiadores, "
        "com snapshots, seeds e builds como estavam.",
        "- Qualificadas que sobraram no checkpoint: "
        f"{sum(1 for v in plano['preenchimento'] if v['origem'] == 'preenchimento_checkpoint')}"
        " (nenhuma extração com OP acima de 30 foi usada).",
        "- Tentativas interrompidas no encerramento da geração original (em voo, sem "
        "resultado registrado): "
        + (
            ", ".join(f"{k} #{', #'.join(map(str, v))}" for k, v in plano["interrompidas"].items())
            or "nenhuma"
        )
        + ".",
        "- Regra das vagas novas (determinística): a política com menos gladiadores nos 64 "
        "(empate: survival, offense, economy) e, dentro dela, o perfil com menos vagas novas "
        "nessa política (empate: menos vagas novas no total; depois conservador). Cada grupo "
        "continua a própria numeração de tentativas depois da última da geração original, com "
        "as seeds v2 e o mesmo BotExperimental (linha de aposta e matriz de extração do "
        "perfil).",
        f"- {r['tentativas']} runs no preenchimento: {r['mortes']} mortes, {r['extracoes']} "
        f"extrações ({r['taxa_extracao']:.1%}), {r['qualificadas']} na faixa "
        f"(aprovação por OP: {r['taxa_aprovacao']:.1%} das extrações).",
        "",
    ]
    cab = ["Grupo", "Vagas", "Primeira tentativa", "Runs", "Aceitas (tentativas)"]
    corpo = []
    for chave, v in pre["por_grupo"].items():
        perfil, politica = chave.split("-")
        corpo.append(
            [
                f"{PERFIL_PT[perfil]}/{politica}",
                v["quota"],
                f"#{v['primeira_tentativa']}",
                v["tentativas"],
                ", ".join(f"#{k}" for k in v["aceitas"]),
            ]
        )
    linhas += _tabela(cab, corpo)
    linhas += [
        "### Distribuição final dos 64",
        "",
        "Não é a distribuição das quotas originais: ela mistura a seleção original e o "
        "preenchimento.",
        "",
    ]
    cab = ["Perfil"] + list(POLITICAS) + ["Total", "Do preenchimento"]
    corpo = []
    for perfil in PERFIS:
        linha = g["distribuicao"][perfil]
        do_pre = sum(
            1
            for a in g["aceitos"]
            if a["perfil"] == perfil and a["origem"].startswith("preenchimento")
        )
        corpo.append(
            [PERFIL_PT[perfil]] + [linha[p] for p in POLITICAS] + [sum(linha.values()), do_pre]
        )
    total = [sum(g["distribuicao"][p][pol] for p in PERFIS) for pol in POLITICAS]
    corpo.append(["Total"] + total + [sum(total), sum(row[-1] for row in corpo)])
    linhas += _tabela(cab, corpo)
    return linhas


def _runs_md(g: dict) -> list[str]:
    linhas = [
        "## Runs necessárias, por grupo",
        "",
    ]
    cab = [
        "Grupo",
        "Quota",
        "Runs",
        "Última aceita",
        "Mortes",
        "Extrações",
        "Na faixa",
        "OP > 30",
        "OP < 20",
        "Sem vaga",
        "Após a quota",
    ]
    corpo = []
    for chave, v in g["por_grupo"].items():
        corpo.append(
            [
                f"{PERFIL_PT[v['perfil']]}/{v['politica']}",
                v["quota"],
                v["tentativas"],
                f"#{v['ultima_aceita']}",
                f"{v['mortes']} ({v['taxa_morte']:.0%})",
                f"{v['extracoes']} ({v['taxa_extracao']:.0%})",
                v["qualificadas"],
                v["acima"],
                v["abaixo"],
                v["sem_vaga"],
                v["apos_a_quota"],
            ]
        )
    linhas += _tabela(cab, corpo)
    linhas += [
        '"Última aceita" é o número da tentativa que fechou a quota; "após a quota" são as '
        "que já estavam em voo quando isso aconteceu e terminaram depois.",
        "",
    ]
    return linhas


def _perfis_md(g: dict) -> list[str]:
    linhas = ["## Morte e extração por perfil e por política", ""]
    cab = [
        "Perfil",
        "Runs",
        "Mortes",
        "Mortes até o andar 5",
        "Andar de morte (média · mediana)",
        "HP ao entrar na luta fatal (mediana)",
        "Extrações",
        "Aprovação por OP (na faixa / extrações)",
        "Na faixa / runs",
        "Combates por run",
        "Fugas por run",
        "Poções bebidas por run",
    ]
    corpo = []
    for p in PERFIS:
        v = g["por_perfil"][p]
        corpo.append(
            [
                PERFIL_PT[p],
                v["tentativas"],
                f"{v['mortes']} ({v['taxa_morte']:.1%})",
                v["mortes_ate_5"],
                f"{v['andar_medio_morte']:.1f} · {v['andar_mediano_morte']:.0f}",
                f"{v['hp_entrada_fatal']:.0%}",
                f"{v['extracoes']} ({v['taxa_extracao']:.1%})",
                f"{v['qualificadas']} ({v['taxa_aprovacao']:.1%})",
                _pct(v["qualificadas"], v["tentativas"]),
                f"{v['combates_por_run']:.1f}",
                f"{v['fugas_por_run']:.2f}",
                f"{v['pocoes_por_run']:.2f}",
            ]
        )
    linhas += _tabela(cab, corpo)
    cab = ["Política", "Runs", "Mortes", "Extrações", "Na faixa", "OP médio das extrações"]
    corpo = [
        [
            pol,
            v["tentativas"],
            f"{v['mortes']} ({v['taxa_morte']:.1%})",
            f"{v['extracoes']} ({v['taxa_extracao']:.1%})",
            v["qualificadas"],
            f"{v['op_medio_extracao']:.2f}",
        ]
        for pol, v in g["por_politica"].items()
    ]
    linhas += _tabela(cab, corpo)
    linhas += ["### Sobrevivência por andar", "", "Fração das runs que entrou viva no andar:", ""]
    marcos = [
        f
        for f in (1, 2, 3, 5, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30)
        if f <= len(g["por_perfil"]["conservador"]["sobrevivencia"])
    ]
    cab = ["Perfil"] + [f"Andar {f}" for f in marcos]
    corpo = [
        [PERFIL_PT[p]] + [f"{g['por_perfil'][p]['sobrevivencia'][f - 1]:.1%}" for f in marcos]
        for p in PERFIS
    ]
    linhas += _tabela(cab, corpo)
    cab = ["Perfil"] + [f"Mortes em {f}" for f in g["faixas"][:6]]
    corpo = [
        [PERFIL_PT[p]] + [g["por_perfil"][p]["mortes_por_faixa"].get(f, 0) for f in g["faixas"][:6]]
        for p in PERFIS
    ]
    linhas += _tabela(cab, corpo)
    return linhas


def _op_md(g: dict) -> list[str]:
    t = g["total"]
    ops = sorted(e["op"] for e in g["extracoes"])
    bins = Counter(int(op) for op in ops)
    linhas = [
        "## Overall Power das extrações",
        "",
        f"{len(ops)} extrações medidas. Distribuição por unidade de OP (o número é o piso do "
        "intervalo):",
        "",
    ]
    linhas += _tabela(
        ["OP"] + [str(k) for k in sorted(bins)], [["extrações"] + [bins[k] for k in sorted(bins)]]
    )
    linhas += [
        f"- Na faixa 20–30: {t['qualificadas']}; acima de 30: {t['acima']}; abaixo de 20: "
        f"{t['abaixo']}.",
        f"- OP médio de todas as extrações: {t['op_medio_extracao']:.2f}; dos aceitos: "
        f"{g['op_aceitos']['media']:.2f}.",
        "",
        "### A banda da build no momento da extração",
        "",
        "Extrair exige a Chave no bolso e a casa `E` alcançável no andar; a banda é a da build "
        "contra o benchmark da Arena (OP 29,17) quando o bot decidiu preservar. Uma extração "
        "acima de 30 é uma em que a primeira oportunidade depois de cruzar a banda do perfil "
        "já caiu acima de 30, ou, no hardcore, uma em que o fôlego seguiu saudável até 1,05:",
        "",
    ]
    cab = ["Perfil", "ABAIXO", "CLOSE_ENOUGH", "META_BATIDA", "HARD_STOP"]
    corpo = [
        [PERFIL_PT[p]] + [g["por_perfil"][p]["bandas_na_extracao"].get(b, 0) for b in cab[1:]]
        for p in PERFIS
    ]
    linhas += _tabela(cab, corpo)
    linhas += [
        "Nada aqui foi ajustado para caber na faixa: a extração fora dela foi registrada e "
        "descartada, e a geração continuou até as vagas fecharem.",
        "",
    ]
    return linhas


def _andares_md(g: dict) -> list[str]:
    aceitos = g["aceitos"]
    andares = Counter(a["andar"] for a in aceitos)
    niveis = Counter(a["nivel"] for a in aceitos)
    linhas = [
        "## Andares e níveis dos 64",
        "",
        f"Andar de extração: média {_media(a['andar'] for a in aceitos):.1f} (de "
        f"{min(andares)} a {max(andares)}). Nível: média {_media(a['nivel'] for a in aceitos):.1f} "
        f"(de {min(niveis)} a {max(niveis)}).",
        "",
    ]
    linhas += _tabela(
        ["Andar"] + [str(k) for k in sorted(andares)],
        [["gladiadores"] + [andares[k] for k in sorted(andares)]],
    )
    linhas += _tabela(
        ["Nível"] + [str(k) for k in sorted(niveis)],
        [["gladiadores"] + [niveis[k] for k in sorted(niveis)]],
    )
    return linhas


def _builds_md(b: dict, todas_ext: dict) -> list[str]:
    rp = b["raridade_pecas"]
    linhas = [
        "## Equipamento, aprimoramentos, gemas e encantos (os 64)",
        "",
        f"- {b['pecas']} peças equipadas ({b['pecas_por_build']:.1f} por gladiador). "
        "Raridade: "
        + ", ".join(f"{RARIDADE_PT.get(k, k)} {rp.get(k, 0)}" for k in RARIDADES if rp.get(k))
        + ".",
        f"- Ferreiro: {b['aprimoradas']} peças com `+N` (soma {b['mais_total']}, maior "
        f"+{b['mais_max']}); {b['com_gema']} peças com gema ({b['gemas']} gemas); "
        f"{b['com_encanto']} com encanto ({b['encantos']} encantos).",
        f"- Peças do Starter Kit ainda equipadas: {b['starter']}.",
        f"- Peças mais comuns: {_lista(b['itens'], 12)}.",
        "",
        "## Skills e passivas (os 64)",
        "",
        f"- Decks distintos: {b['decks_distintos']} de {b['builds']}. Conjuntos de passivas "
        f"distintos: {b['passivas_distintas']}. Equipamentos distintos: "
        f"{b['equipamentos_distintos']}.",
        f"- Cartas no deck: {_lista(b['cartas'], 20)}.",
        f"- Famílias de passiva: {_lista(b['familias'])}.",
        "- Raridade das passivas: "
        + ", ".join(
            f"{RARIDADE_PT.get(k, k)} {b['raridade_passivas'].get(k, 0)}" for k in RARIDADES
        )
        + ".",
        f"- Passivas mais repetidas: {_lista(b['passivas'], 15)}.",
        "",
        "## Builds de crítico, defesa, controle e sustento",
        "",
        "Leitura feita DEPOIS da geração, só para descrever; nenhuma build foi escolhida por "
        "isso. Regras: crítico = 3+ passivas de crítico; defesa = metade ou mais das passivas "
        "em vida/defesa/redução/esquiva/resistência, ou carta de redução no deck; controle = "
        "carta de atordoar/sono/congelar/medo ou passiva de chance de atordoar/medo; sustento "
        "= carta de cura ou 2+ passivas de roubo de vida/bônus de poção/ignorar a morte. Uma "
        "build pode ter vários canais.",
        "",
        f"- Nos 64 aceitos: {_lista(b['arquetipos'])}.",
        f"- Em todas as {todas_ext['builds']} extrações: {_lista(todas_ext['arquetipos'])}.",
        "",
    ]
    return linhas


def _diversidade_md(g: dict) -> list[str]:
    linhas = ["## Diversidade entre os nove grupos", ""]
    cab = [
        "Grupo",
        "n",
        "OP médio",
        "Nível médio",
        "Andar médio",
        "Decks distintos",
        "Famílias mais frequentes",
        "Canais",
    ]
    corpo = []
    for chave, v in g["diversidade"].items():
        perfil, politica = chave.split("/")
        corpo.append(
            [
                f"{PERFIL_PT[perfil]}/{politica}",
                v["n"],
                f"{v['op_medio']:.2f}",
                f"{v['nivel_medio']:.1f}",
                f"{v['andar_medio']:.1f}",
                v["decks_distintos"],
                _lista(v["familias"]),
                _lista(v["arquetipos"]),
            ]
        )
    linhas += _tabela(cab, corpo)
    linhas += [
        f"Semelhança média dos decks (Jaccard das cartas) entre dois gladiadores do mesmo "
        f"grupo: {g['jaccard']['dentro']:.2f}; de grupos diferentes: {g['jaccard']['entre']:.2f}.",
        "",
    ]
    return linhas


def _risco_md(g: dict) -> list[str]:
    linhas = [
        "## Risco, sobrevivência e poder extraído",
        "",
        f"> {AVISO_CAUSAL}",
        "",
    ]
    cab = [
        "Perfil",
        "Mortes",
        "Extrações",
        "OP médio das extrações",
        "OP médio dos aceitos",
        "Andar médio dos aceitos",
        "Runs por aceito na seleção original",
    ]
    corpo = []
    for p in PERFIS:
        v = g["por_perfil"][p]
        aceitos = [a for a in g["aceitos"] if a["perfil"] == p and a["origem"] == "original"]
        corpo.append(
            [
                PERFIL_PT[p],
                f"{v['taxa_morte']:.1%}",
                f"{v['taxa_extracao']:.1%}",
                f"{v['op_medio_extracao']:.2f}",
                f"{_media(a['op'] for a in aceitos):.2f}",
                f"{_media(a['andar'] for a in aceitos):.1f}",
                f"{v['tentativas'] / max(1, len(aceitos)):.1f}",
            ]
        )
    linhas += _tabela(cab, corpo)
    return linhas


def _aceitos_md(g: dict) -> list[str]:
    linhas = ["## Os 64, na ordem de aceite", ""]
    cab = [
        "ID",
        "Nick",
        "Perfil",
        "Política",
        "Tentativa",
        "Seed",
        "Andar",
        "Nível",
        "OP",
        "Canais",
        "Origem",
    ]
    corpo = [
        [
            a["id"],
            a["nick"],
            PERFIL_PT[a["perfil"]],
            a["politica"],
            a["tentativa"],
            f"`{a['seed']}`",
            a["andar"],
            a["nivel"],
            f"{a['op']:.2f}",
            ", ".join(a["arquetipos"]) or "—",
            ORIGEM_PT[a["origem"]],
        ]
        for a in g["aceitos"]
    ]
    linhas += _tabela(cab, corpo)
    linhas += [
        "Snapshots canônicos em `snapshots/`, metadados e assinatura de cada build em "
        "`gladiadores.json`, e cada tentativa em `runs.jsonl` (geração original) e "
        "`runs_preenchimento.jsonl` (preenchimento).",
        "",
    ]
    return linhas


# --- modelo do campeonato ----------------------------------------------------


def _ficha(participante, gladiador: dict) -> dict:
    heroi = prepare_gladiator(participante.heroi).hero
    espec = participante.espec
    return {
        "id": espec.id,
        "nome": espec.nome,
        "classe": "Warrior",
        "classe_pt": "Guerreiro",
        "perfil": espec.perfil,
        "perfil_pt": PERFIL_PT[espec.perfil],
        "politica": espec.politica,
        "grupo": espec.grupo,
        "rotulo": espec.rotulo,
        "foco": espec.foco,
        "arquetipos": gladiador["arquetipos"],
        "origem": gladiador.get("origem", "original"),
        "cor": COR_PERFIL[espec.perfil],
        "nivel": espec.nivel,
        "andar": espec.andar,
        "tentativa": espec.tentativa,
        "seed": str(espec.seed),
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
        "tentativas": [],
    }


def _por(dados: dict, chave: str, valores) -> dict:
    """Vitórias, dano e alcance agrupados por `chave` do participante."""
    jogos = dados["partidas"]
    ordem = [f for f, _, _ in FASES]
    saida = {}
    for valor in valores:
        membros = [
            p
            for p in dados["participantes"]
            if (valor in p[chave] if isinstance(p[chave], list) else p[chave] == valor)
        ]
        ids = {p["id"] for p in membros}
        lados = [(j, lado) for j in jogos for lado in SIDES if j[lado] in ids]
        vitorias = sum(1 for j, lado in lados if j["vencedor"] == j[lado])
        golpes = [g for j in jogos for g in j["golpes"] if g["atacante"] in ids]
        conectados = [g for g in golpes if not g["errou"]]
        criticos = sum(1 for g in conectados if g["critico"])
        saida[valor] = {
            "participantes": len(membros),
            "op_medio": _media(p["op"] for p in membros),
            "partidas": len(lados),
            "vitorias": vitorias,
            "derrotas": len(lados) - vitorias,
            "taxa": vitorias / len(lados) if lados else 0.0,
            "alcancou": {
                fase: sum(1 for p in membros if ordem.index(p["fase"]) >= ordem.index(fase))
                for fase in ordem
            },
            "dano_por_partida": _media(j["lados"][lado]["dano"] for j, lado in lados),
            "acerto": len(conectados) / len(golpes) if golpes else 0.0,
            "criticos": criticos,
            "taxa_critico": criticos / len(conectados) if conectados else 0.0,
            "campeao": any(p["campeao"] for p in membros),
        }
    return saida


def _spearman(xs: list[float], ys: list[float]) -> float:
    def postos(v):
        ordem = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(ordem):
            j = i
            while j + 1 < len(ordem) and v[ordem[j + 1]] == v[ordem[i]]:
                j += 1
            for k in range(i, j + 1):
                r[ordem[k]] = (i + j) / 2 + 1
            i = j + 1
        return r

    a, b = postos(xs), postos(ys)
    ma, mb = _media(a), _media(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else 0.0


def _copa_02() -> dict | None:
    """Os agregados comparáveis da Copa 02, lidos do dashboard publicado."""
    if not COPA_02.exists():
        return None
    pagina = COPA_02.read_text(encoding="utf-8")
    marca = '<script id="dados" type="application/json">'
    inicio = pagina.index(marca) + len(marca)
    dados = json.loads(pagina[inicio : pagina.index("</script>", inicio)])
    return {"agregados": dados["agregados"], "partidas": dados["partidas"]}


def _comparaveis(dados: dict) -> dict:
    ag = dados["agregados"]
    jogos = dados["partidas"]
    return {
        "favoritos": ag["favoritos"],
        "zebras": len(ag["zebras"]),
        "maior_zebra": max((abs(z["delta_op"]) for z in ag["zebras"]), default=0.0),
        "rodadas_media": ag["rodadas_total"] / len(jogos) if jogos else 0.0,
        "acerto": ag["golpes_conectados"] / ag["golpes_total"] if ag["golpes_total"] else 0.0,
        "criticos_por_golpe": ag["criticos_total"] / ag["golpes_conectados"]
        if ag["golpes_conectados"]
        else 0.0,
        "op_medio": ag["op_medio"],
        "amplitude_op": ag["op_max"] - ag["op_min"],
        "primeira_rodada": sum(1 for j in jogos if j["rodadas"] == 1),
    }


def agregados(dados: dict) -> dict:
    # Os agregados da Copa 02 valem como estão (classe é sempre Guerreiro aqui); o que
    # é desta Copa entra por cima: perfil, política, canal da build e a comparação.
    ag = c2.agregados(dados)
    part = {p["id"]: p for p in dados["participantes"]}
    jogos = dados["partidas"]
    matriz = {a: {b: 0 for b in PERFIS} for a in PERFIS}
    for j in jogos:
        matriz[part[j["vencedor"]]["perfil"]][part[j["perdedor"]]["perfil"]] += 1
    ag["por_perfil"] = _por(dados, "perfil", PERFIS)
    ag["por_politica"] = _por(dados, "politica", POLITICAS)
    ag["por_arquetipo"] = _por(dados, "arquetipos", ARQUETIPOS)
    ag["matriz_perfil"] = matriz
    ops = [p["op"] for p in dados["participantes"]]
    ag["spearman_op_vitorias"] = _spearman(ops, [p["vitorias"] for p in dados["participantes"]])
    ag["comparaveis"] = _comparaveis({"agregados": ag, "partidas": jogos})
    copa02 = _copa_02()
    ag["copa_02"] = _comparaveis(copa02) if copa02 else None
    ag["curiosidades"] = curiosidades(dados, ag)
    return ag


def curiosidades(dados: dict, ag: dict) -> list[str]:
    """Situações incomuns, lidas dos dados. Cada frase cita de onde sai."""
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
    ignorados = [(j, g) for j in jogos for g in j["golpes"] if g["death_ignore"]]
    if ignorados:
        frases.append(
            f"`death_ignore` salvou um golpe letal {len(ignorados)} vez(es): "
            + "; ".join(f"{nome(g['defensor'])} em {j['titulo']}" for j, g in ignorados[:4])
            + "."
        )
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
    acima = [j for j in jogos if j["hp_vencedor"] > j["hp_teto_final_vencedor"]]
    if acima:
        j = acima[0]
        frases.append(
            f"Em {len(acima)} partida(s) o vencedor terminou com HP atual acima do teto do fim "
            f"da luta, como {nome(j['vencedor'])} em {j['titulo']}: `frailty` corta o HP "
            "máximo e o motor não corta o HP atual (peculiaridade já registrada na Copa 02)."
        )
    fundo = max(dados["participantes"], key=lambda p: p["andar"])
    raso = min(dados["participantes"], key=lambda p: p["andar"])
    frases.append(
        f"O gladiador extraído mais fundo é {nome(fundo['id'])}, andar {fundo['andar']} "
        f"(nível {fundo['nivel']}, OP {fundo['op']:.2f}); o mais raso, {nome(raso['id'])}, "
        f"andar {raso['andar']} (nível {raso['nivel']}, OP {raso['op']:.2f})."
    )
    por_perfil = ag["por_perfil"]
    melhor = max(PERFIS, key=lambda p: por_perfil[p]["taxa"])
    frases.append(
        f"Na Arena, o perfil com a maior taxa de vitória foi o {PERFIL_PT[melhor]} "
        f"({por_perfil[melhor]['vitorias']}–{por_perfil[melhor]['derrotas']}); o perfil "
        "decide a jornada PvE, e no duelo todos usam a mesma `PoliticaCopa`."
    )
    frases.append(
        f"Correlação de postos (Spearman) entre OP e vitórias na Copa: "
        f"{ag['spearman_op_vitorias']:.2f}."
    )
    um_turno = [j for j in jogos if j["rodadas"] == 1]
    if um_turno:
        frases.append(f"{len(um_turno)} partida(s) acabaram na primeira rodada.")
    sem_critico = [
        j
        for j in jogos
        if not any(g["critico"] for g in j["golpes"] if g["atacante"] == j["vencedor"])
    ]
    frases.append(
        f"{len(sem_critico)} das {len(jogos)} vitórias saíram sem nenhum crítico do vencedor."
    )
    return frases


def modelo(copa, diagnostico: list[dict], geracao: dict, gladiadores: list[dict]) -> dict:
    por_id = {g["id"]: g for g in gladiadores}
    participantes = [_ficha(p, por_id[p.id]) for p in copa.participantes]
    partidas = [c2._jogo(p) for p in todas(copa)]
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
        "fases": [[f, n, nome] for f, n, nome in FASES],
        "perfis": [[p, PERFIL_PT[p]] for p in PERFIS],
        "politicas": list(POLITICAS),
        "chave": list(copa.chave),
        "campeao": campeao,
        "interrompida": copa.interrompida,
        "participantes": participantes,
        "partidas": partidas,
        "rng": diagnostico,
        "repeticoes": REPETICOES,
    }
    dados["agregados"] = agregados(dados)
    dados["geracao"] = _geracao_para_o_painel(geracao)
    dados["final"] = None
    if "final" in copa.fases:
        final = copa.fases["final"][0]
        dados["final"] = c2._final(final)
        dados["final"]["diagnostico"] = [
            [len(linha) - len(linha.lstrip(" ")), linha.strip()[2:].replace("**", "")]
            for linha in _diagnostico_final(final)
            if linha.strip().startswith("- ")
        ]
    return dados


def _geracao_para_o_painel(g: dict) -> dict:
    """O pedaço da geração que o dashboard mostra (sem as listas longas)."""
    return {
        "total": {k: v for k, v in g["total"].items() if k != "op_extracoes"},
        "por_grupo": {
            k: {c: x for c, x in v.items() if c != "op_extracoes"}
            for k, v in g["por_grupo"].items()
        },
        "por_perfil": {
            p: {c: x for c, x in v.items() if c != "op_extracoes"}
            for p, v in g["por_perfil"].items()
        },
        "faixas": g["faixas"],
        "op_aceitos": g["op_aceitos"],
        "andar_maximo": g["andar_maximo"],
        "builds": {k: v for k, v in g["builds_aceitas"].items()},
    }


# --- Markdown do campeonato ---------------------------------------------------


def _n(pid: str, part: dict) -> str:
    return f"{part[pid]['nome']} ({pid})"


def _participantes_md(dados: dict) -> list[str]:
    linhas = [
        "## Participantes",
        "",
        "| ID | Gladiador | Perfil | Política | Andar | Nível | OP | HP | MP | ST | MG | AG | DF "
        "| Canais | Skills | Passivas | Equipamento |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in sorted(dados["participantes"], key=lambda p: -p["op"]):
        equipamento = "; ".join(f"{pos}: {nome}" for pos, nome in p["equipamento"].items())
        linhas.append(
            f"| {p['id']} | {p['nome']} | {p['perfil_pt']} | {p['politica']} | {p['andar']} "
            f"| {p['nivel']} | {p['op']:.2f} | {p['hp']} | {p['mp']} | {p['st']} | {p['mg']} "
            f"| {p['ag']} | {p['df']} | {p['foco']} | {', '.join(p['deck'])} "
            f"| {c2._passivas_txt(p['passivas'])} | {equipamento} |"
        )
    return linhas + [""]


def _grupos_md(ag: dict) -> list[str]:
    linhas = ["### Perfis, políticas e canais na Arena", "", f"> {AVISO_CAUSAL}", ""]
    for titulo, chave, nomes in (
        ("Perfil", "por_perfil", PERFIL_PT),
        ("Política", "por_politica", {p: p for p in POLITICAS}),
        ("Canal da build", "por_arquetipo", {a: a for a in ARQUETIPOS}),
    ):
        cab = [
            titulo,
            "Participantes",
            "OP médio",
            "Vitórias",
            "Derrotas",
            "Taxa",
            "Dano por partida",
            "Acerto",
            "Críticos (taxa)",
            "Nas oitavas",
            "Nas quartas",
        ]
        corpo = [
            [
                nomes[k],
                v["participantes"],
                f"{v['op_medio']:.2f}",
                v["vitorias"],
                v["derrotas"],
                f"{v['taxa']:.1%}",
                f"{v['dano_por_partida']:.0f}",
                f"{v['acerto']:.1%}",
                f"{v['criticos']} ({v['taxa_critico']:.1%})",
                v["alcancou"]["oitavas"],
                v["alcancou"]["quartas"],
            ]
            for k, v in ag[chave].items()
            if v["participantes"]
        ]
        linhas += _tabela(cab, corpo)
    linhas += [
        "Vitórias do perfil da linha sobre o da coluna:",
        "",
    ]
    linhas += _tabela(
        ["Vencedor \\ Perdedor"] + [PERFIL_PT[p] for p in PERFIS],
        [[PERFIL_PT[a]] + [ag["matriz_perfil"][a][b] for b in PERFIS] for a in PERFIS],
    )
    linhas += [
        f"Correlação de postos (Spearman) entre OP e número de vitórias: "
        f"{ag['spearman_op_vitorias']:.2f}.",
        "",
    ]
    return linhas


def _comparacao_md(ag: dict) -> list[str]:
    a, b = ag["comparaveis"], ag["copa_02"]
    if not b:
        return []
    linhas = [
        "### Comparação com a Copa 02 (só o que é comparável)",
        "",
        "A Copa 02 tinha três classes e builds montadas à mão; esta, só Guerreiros que vieram "
        "de runs reais. Mesma `PoliticaCopa`, mesmo motor, mesmo esquema de seeds por partida. "
        "Classe, build e OP diferem, então a comparação descreve as duas amostras, não isola "
        "causa.",
        "",
    ]
    linhas += _tabela(
        ["Métrica", "Copa 02", "Copa 03"],
        [
            ["OP médio", f"{b['op_medio']:.2f}", f"{a['op_medio']:.2f}"],
            ["Amplitude de OP (máx − mín)", f"{b['amplitude_op']:.2f}", f"{a['amplitude_op']:.2f}"],
            ["Favorito venceu", f"{b['favoritos']}/63", f"{a['favoritos']}/63"],
            ["Zebras", b["zebras"], a["zebras"]],
            ["Maior ΔOP de uma zebra", f"{b['maior_zebra']:.2f}", f"{a['maior_zebra']:.2f}"],
            ["Rodadas por partida", f"{b['rodadas_media']:.2f}", f"{a['rodadas_media']:.2f}"],
            ["Golpes que conectaram", f"{b['acerto']:.1%}", f"{a['acerto']:.1%}"],
            [
                "Críticos por golpe conectado",
                f"{b['criticos_por_golpe']:.1%}",
                f"{a['criticos_por_golpe']:.1%}",
            ],
            ["Partidas de uma rodada", b["primeira_rodada"], a["primeira_rodada"]],
        ],
    )
    return linhas


def _rng_md(dados: dict, part: dict) -> list[str]:
    linhas = [
        "## Diagnóstico do RNG do duelo",
        "",
        f"Depois da Copa oficial, {len(dados['rng'])} confrontos foram repetidos "
        f"{dados['repeticoes']} vezes cada, com os mesmos dois gladiadores, a mesma "
        '`PoliticaCopa` e seeds novas (`sha256(f"{seed}:rng:{fase}:{índice}:{r}")`), metade '
        "com os lados trocados. Nada disso altera o resultado oficial. Foram escolhidos a "
        "final, as zebras de maior diferença e os confrontos mais parelhos em OP.",
        "",
        "| Confronto | Vencedor oficial (OP) | Perdedor oficial (OP) | Vitórias do vencedor "
        "oficial | IC 95% | Rodadas (média) |",
        "|---|---|---|---|---|---|",
    ]
    for r in dados["rng"]:
        v, p = part[r["vencedor_oficial"]], part[r["perdedor_oficial"]]
        validos = r["repeticoes"] - r["inconclusivos"]
        linhas.append(
            f"| {r['titulo']}{' (zebra)' if r['zebra_oficial'] else ''} | {v['nome']} "
            f"({v['op']:.2f}) | {p['nome']} ({p['op']:.2f}) | {r['vitorias_do_vencedor_oficial']}"
            f"/{validos} ({r['taxa']:.1%}) | {r['ic95'][0]:.1%}–{r['ic95'][1]:.1%} "
            f"| {r['rodadas_media']:.1f} |"
        )
    linhas += [
        "",
        "Como ler: os três componentes estão separados no experimento só até certo ponto. O "
        "RNG da jornada PvE e as decisões do perfil produziram a build (e o OP); aqui ela fica "
        "fixa, e só o RNG do duelo varia. Uma taxa perto de 50% diz que, entre esses dois, o "
        "duelo é decidido pelo sorteio; perto de 100%, pela build. O experimento não separa "
        "o que, dentro da build, veio do perfil e o que veio do RNG da jornada.",
        "",
    ]
    return linhas


def _composicao(dados: dict) -> str:
    perfis = Counter(p["perfil"] for p in dados["participantes"])
    preenchidos = sum(1 for p in dados["participantes"] if p["origem"].startswith("preenchimento"))
    texto = (
        f"- Os 64: conservador {perfis['conservador']}, moderado {perfis['moderado']}, hardcore "
        f"{perfis['hardcore']}"
    )
    if preenchidos:
        texto += (
            f"; {64 - preenchidos} da seleção original e {preenchidos} do preenchimento. As "
            "quotas originais 22/21/21 não foram cumpridas (o hardcore não fechou); a "
            "distribuição final está em [`geracao.md`](geracao.md)"
        )
    return texto + "."


def relatorio_md(dados: dict, copa) -> str:
    ag = dados["agregados"]
    part = {p["id"]: p for p in dados["participantes"]}
    campeao = part.get(dados["campeao"])
    final = next((j for j in dados["partidas"] if j["fase"] == "final"), None)
    linhas = [
        f"# {COPA} — 64 Guerreiros extraídos do PvE real",
        "",
        "Campeonato técnico da Arena PvP, gerado por `tools/arena_copa_03.py`. A geração dos "
        "64 está em [`geracao.md`](geracao.md).",
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
            f"- **Campeão: {campeao['nome']} ({campeao['id']})**, Guerreiro "
            f"{campeao['perfil_pt'].lower()}/{campeao['politica']}, extraído no andar "
            f"{campeao['andar']}, nível {campeao['nivel']}, OP {campeao['op']:.2f} "
            f"({campeao['foco']}).",
            f"- Vice: {vice['nome']} ({vice['id']}), {vice['perfil_pt'].lower()}/"
            f"{vice['politica']}, andar {vice['andar']}, nível {vice['nivel']}, OP "
            f"{vice['op']:.2f}.",
        ]
    linhas += [
        f"- OP médio {ag['op_medio']:.2f} (mínimo {ag['op_min']:.2f}, máximo {ag['op_max']:.2f}).",
        _composicao(dados),
        f"- 63 partidas, {ag['rodadas_total']} rodadas, {ag['golpes_total']} golpes "
        f"({ag['golpes_conectados']} conectados), {ag['criticos_total']} críticos.",
        f"- O favorito (OP maior) venceu {ag['favoritos']} das 63 partidas; houve "
        f"{len(ag['zebras'])} zebras.",
        "- As 63 partidas rodaram duas vezes, sem e com auditoria, com o resultado conferido "
        "na tabela de auditoria resumida.",
        "",
        "Arquivos: [`geracao.md`](geracao.md), [`final_detalhada.md`](final_detalhada.md), "
        "[`final_trace.json`](final_trace.json), [`dashboard.html`](dashboard.html), "
        "[`relatorio_visual.pdf`](relatorio_visual.pdf), [`gladiadores.json`](gladiadores.json), "
        "[`runs.jsonl`](runs.jsonl), [`runs_preenchimento.jsonl`](runs_preenchimento.jsonl), "
        "[`preenchimento.json`](preenchimento.json), [`runs_piloto.jsonl`](runs_piloto.jsonl), "
        "[`diagnostico_rng.json`](diagnostico_rng.json) e `snapshots/`.",
        "",
        "## Como a Copa foi disputada",
        "",
        "- **Gladiadores.** Os 64 snapshots canônicos, reconstruídos por "
        "`player_from_save_data` sobre cópia (o caminho da Arena) e preparados por "
        "`prepare_gladiator` a cada duelo: HP e MP cheios, efeitos, buffs e recargas limpos, "
        "consumíveis fora. O snapshot não muda; o nickname vai só na instância reconstruída.",
        f'- **Chave.** `random.Random(sha256("{SEMENTE_PRINCIPAL}:chave")).shuffle` dos 64 IDs, '
        "pares em ordem, sem cabeças de chave. Seed de cada partida: 8 bytes de "
        f'`sha256(f"{SEMENTE_PRINCIPAL}:{{fase}}:{{índice}}")`, o esquema das Copas 01 e 02.',
        "- **Política.** A `PoliticaCopa` das Copas anteriores, igual para os 64: cura com HP ≤ "
        "50%; senão buff ou redução ainda não ativos; senão status que o adversário não "
        "carrega; senão a primeira skill de dano legal; senão ataque básico.",
        f"- **Limite técnico** do laço: {LIMITE_TECNICO} rodadas (inconclusivo, nunca empate).",
        "",
    ]
    linhas += _participantes_md(dados)
    linhas += ["## Chave", "", *c2._chave_md(dados, part), ""]
    linhas += c2._resultados_md(dados, part)
    linhas += ["## Estatísticas agregadas", "", f"> {AVISO_ESTATISTICA}", ""]
    linhas += _grupos_md(ag)
    linhas += c2._op_md(ag, part)
    linhas += _comparacao_md(ag)
    linhas += c2._golpes_md(dados, ag, part)
    linhas += c2._efeitos_md(ag, part)
    linhas += _rng_md(dados, part)
    linhas += [*c2._campeao_md(dados, part), "", "## Curiosidades", ""]
    linhas += [f"- {frase}" for frase in ag["curiosidades"]]
    linhas += [
        "",
        "## Auditoria resumida das 63 partidas",
        "",
        "Cada partida rodou sem instrumentação e auditada, com a mesma seed; as verificações são "
        "as das Copas 01 e 02.",
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


# --- SVG próprios desta Copa --------------------------------------------------


def _legenda_svg(itens: list[tuple[str, str]], y: int = 12) -> list[str]:
    s, x = [], 8
    for nome, cor in itens:
        s.append(f'<rect x="{x}" y="{y - 8}" width="10" height="10" rx="2" fill="{cor}"/>')
        s.append(f'<text x="{x + 15}" y="{y + 1}" class="t-secondary">{_e(nome)}</text>')
        x += 30 + len(nome) * 6.6
    return s


def svg_desfechos(por_grupo: dict) -> str:
    """Barras empilhadas, uma por grupo: morte, extração fora da faixa, na faixa."""
    largura, rotulo_w, alto, folga = 620, 170, 18, 9
    segmentos = (
        ("Morreu", "mortes", "var(--c-neutra)"),
        ("Extraiu fora de 20–30", "fora", "var(--c-fora)"),
        ("Extraiu na faixa", "qualificadas", "var(--c-serie)"),
    )
    linhas = list(por_grupo.items())
    h = 26 + len(linhas) * (alto + folga)
    util = largura - rotulo_w - 70
    s = [
        f'<svg viewBox="0 0 {largura} {h}" width="100%" role="img" '
        f'aria-label="Desfecho das runs por grupo" {FONTE} font-size="11">'
    ]
    s += _legenda_svg([(n, c) for n, _, c in segmentos])
    for i, (chave, v) in enumerate(linhas):
        y = 24 + i * (alto + folga)
        perfil, politica = chave.split("/")
        valores = {
            "mortes": v["mortes"],
            "fora": v["extracoes"] - v["qualificadas"],
            "qualificadas": v["qualificadas"],
        }
        total = max(1, v["tentativas"])
        s.append(
            f'<text x="{rotulo_w - 8}" y="{y + 13}" text-anchor="end" class="t-secondary">'
            f"{_e(PERFIL_PT[perfil])}/{_e(politica)}</text>"
        )
        x = float(rotulo_w)
        for nome, k, cor in segmentos:
            w = valores[k] / total * util
            if w <= 0:
                continue
            dica = f"{PERFIL_PT[perfil]}/{politica}: {nome.lower()} {valores[k]} de {total}"
            s.append(
                f'<rect data-tip="{_e(dica)}" x="{x:.1f}" y="{y}" width="{max(1.0, w - 1):.1f}" '
                f'height="{alto}" fill="{cor}"/>'
            )
            x += w
        s.append(
            f'<text x="{rotulo_w + util + 6}" y="{y + 13}" class="t-primary" '
            f'font-variant-numeric="tabular-nums">{total} runs</text>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_histograma_op(extracoes: list[dict]) -> str:
    """Extrações por unidade de OP; as da faixa 20–30 em destaque."""
    largura, altura, m = 620, 240, 40
    ops = [e["op"] for e in extracoes]
    lo, hi = int(min(ops)), int(max(ops)) + 1
    chaves = list(range(lo, hi))
    contagem = Counter(int(op) for op in ops)
    dentro = Counter(int(e["op"]) for e in extracoes if FAIXA_DE_OP[0] <= e["op"] <= FAIXA_DE_OP[1])
    _, maximo, marca, _ = _escala(0, max(contagem.values()) or 1)
    marca = max(1, marca)
    util = largura - m - 10
    banda = util / len(chaves)
    barra = min(26.0, banda - 3)
    base = altura - 34
    s = [
        f'<svg viewBox="0 0 {largura} {altura}" width="100%" role="img" '
        f'aria-label="Overall Power das extrações" {FONTE} font-size="11">'
    ]
    s += _legenda_svg([("OP 20–30 (aceitável)", "var(--c-serie)"), ("fora", "var(--c-fora)")])
    s += _grade_y(m, base, 26, 0, maximo, marca, util, "{:.0f}")
    for i, k in enumerate(chaves):
        v = contagem.get(k, 0)
        x = m + i * banda + (banda - barra) / 2
        alt = v / maximo * (base - 26)
        cor = "var(--c-serie)" if dentro.get(k) == v and v else "var(--c-fora)"
        if v:
            s.append(
                f'<rect data-tip="OP {k} a {k + 1}: {v} extração(ões)" x="{x:.1f}" '
                f'y="{base - alt:.1f}" width="{barra:.1f}" height="{alt:.1f}" rx="2" fill="{cor}"/>'
            )
            s.append(
                f'<text x="{x + barra / 2:.1f}" y="{base - alt - 4:.1f}" text-anchor="middle" '
                f'class="t-secondary">{v}</text>'
            )
        s.append(
            f'<text x="{x + barra / 2:.1f}" y="{altura - 18}" text-anchor="middle" '
            f'class="t-muted">{k}</text>'
        )
    s.append(
        f'<text x="{largura / 2}" y="{altura - 3}" text-anchor="middle" class="t-secondary">'
        "OP (piso do intervalo de 1)</text>"
    )
    s.append("</svg>")
    return "".join(s)


def _escala_op(ops: list[float]) -> tuple[float, float, float, str]:
    """Escala redonda que cobre os OPs da Copa, sem passar de 30 (o teto da faixa).

    Os gráficos da Copa 02 fixavam 20–30; aqui os 64 ficam num intervalo estreito
    perto de 30, e o eixo fixo espremia tudo na borda de cima.
    """
    lo, hi, passo, fmt = _escala(min(ops) - 0.05, max(ops) + 0.05, marcas=5)
    return lo, hi, passo, fmt


def _marcas(lo: float, hi: float, passo: float) -> list[float]:
    return [lo + i * passo for i in range(round((hi - lo) / passo) + 1)]


def svg_dispersao_op3(dados: dict) -> str:
    """OP do vencedor × OP do perdedor, na escala dos 64: acima da diagonal, a zebra."""
    part = {p["id"]: p for p in dados["participantes"]}
    w, h, m = 520, 400, 52
    lo, hi, passo, fmt = _escala_op([p["op"] for p in dados["participantes"]])

    def px(v):
        return m + (v - lo) / (hi - lo) * (w - m - 16)

    def py(v):
        return h - m - (v - lo) / (hi - lo) * (h - m - 16)

    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="OP do vencedor contra OP do perdedor em cada partida" {FONTE} '
        'font-size="11">'
    ]
    for v in _marcas(lo, hi, passo):
        s.append(f'<line class="grade" x1="{px(v):.1f}" x2="{px(v):.1f}" y1="16" y2="{h - m}"/>')
        s.append(f'<line class="grade" x1="{m}" x2="{w - 16}" y1="{py(v):.1f}" y2="{py(v):.1f}"/>')
        s.append(
            f'<text x="{px(v):.1f}" y="{h - m + 16}" text-anchor="middle" '
            f'class="t-muted">{fmt.format(v)}</text>'
        )
        s.append(
            f'<text x="{m - 8}" y="{py(v) + 4:.1f}" text-anchor="end" '
            f'class="t-muted">{fmt.format(v)}</text>'
        )
    s.append(
        f'<line class="eixo" x1="{px(lo):.1f}" y1="{py(lo):.1f}" '
        f'x2="{px(hi):.1f}" y2="{py(hi):.1f}"/>'
    )
    s.append(
        f'<text x="{m + 8}" y="30" class="t-secondary">acima da diagonal: venceu o OP menor</text>'
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
            f'cx="{px(v["op"]):.1f}" cy="{py(p["op"]):.1f}" r="5" fill="{v["cor"]}"/>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_op_por_fase3(dados: dict) -> str:
    """OP médio de quem entrou em cada fase, com mínimo e máximo, na escala dos 64."""
    pontos = [(f["nome"], f["entrando"]) for f in dados["agregados"]["op_por_fase"]]
    campeao = next((p for p in dados["participantes"] if p["campeao"]), None)
    if campeao:
        pontos.append(("Campeão", [campeao["op"]] * 3))
    w, h, m = 560, 300, 48
    lo, hi, passo, fmt = _escala_op([p["op"] for p in dados["participantes"]])

    def py(v):
        return h - 40 - (v - lo) / (hi - lo) * (h - 60)

    largura = (w - m - 70) / max(1, len(pontos) - 1)
    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="OP de quem entrou em cada fase" {FONTE} font-size="11">'
    ]
    s += _grade_y(m, h - 40, 20, lo, hi, passo, w - m - 10, fmt)
    caminho = []
    for i, (nome, (media, minimo, maximo)) in enumerate(pontos):
        x = m + 14 + i * largura
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
        x = m + 14 + i * largura
        dica = f"{nome}: média {media:.2f}, mínimo {minimo:.2f}, máximo {maximo:.2f}"
        s.append(
            f'<circle class="ponto-1" data-tip="{_e(dica)}" cx="{x:.1f}" '
            f'cy="{py(media):.1f}" r="5"/>'
        )
        s.append(
            f'<text x="{x + 8:.1f}" y="{py(media) - 8:.1f}" class="t-secondary">{media:.2f}</text>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_aceitos(aceitos: list[dict]) -> str:
    """OP × andar de extração dos 64, cor por perfil."""
    w, h, m = 520, 340, 50
    andares = [a["andar"] for a in aceitos]
    a_lo, a_hi = min(andares) - 1, max(andares) + 1
    lo, hi, passo, fmt = _escala_op([a["op"] for a in aceitos])

    def px(v):
        return m + (v - a_lo) / (a_hi - a_lo) * (w - m - 16)

    def py(v):
        return h - m - (v - lo) / (hi - lo) * (h - m - 24)

    s = [
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
        f'aria-label="OP e andar de extração dos 64" {FONTE} font-size="11">'
    ]
    s += _legenda_svg([(PERFIL_PT[p], COR_PERFIL[p]) for p in PERFIS])
    for v in _marcas(lo, hi, passo):
        s.append(f'<line class="grade" x1="{m}" x2="{w - 16}" y1="{py(v):.1f}" y2="{py(v):.1f}"/>')
        s.append(
            f'<text x="{m - 8}" y="{py(v) + 4:.1f}" text-anchor="end" '
            f'class="t-muted">{fmt.format(v)}</text>'
        )
    for a in range(a_lo + 1, a_hi, 2):
        s.append(
            f'<text x="{px(a):.1f}" y="{h - m + 16}" text-anchor="middle" '
            f'class="t-muted">{a}</text>'
        )
    s.append(
        f'<text x="{(w + m) / 2:.1f}" y="{h - 12}" text-anchor="middle" class="t-secondary">'
        "andar de extração</text>"
    )
    s.append(
        f'<text transform="translate(14,{(h - m) / 2:.1f}) rotate(-90)" text-anchor="middle" '
        'class="t-secondary">OP</text>'
    )
    vistos = Counter()
    for a in aceitos:
        k = (a["andar"], round(a["op"], 1))
        deslocamento = (vistos[k] % 3 - 1) * 5
        vistos[k] += 1
        dica = (
            f"{a['nick']} ({a['id']}): {PERFIL_PT[a['perfil']]}/{a['politica']}, "
            f"andar {a['andar']}, OP {a['op']:.2f}"
        )
        s.append(
            f'<circle class="ponto" data-tip="{_e(dica)}" cx="{px(a["andar"]) + deslocamento:.1f}" '
            f'cy="{py(a["op"]):.1f}" r="5" fill="{COR_PERFIL[a["perfil"]]}"/>'
        )
    s.append("</svg>")
    return "".join(s)


def svg_linhas_n(series: list[tuple], rotulos_x: list[str], *, titulo: str, fmt="{:.0f}") -> str:
    """Várias séries numa escala só, com legenda no topo e sem rótulo na ponta.

    A versão da Copa 02 rotula o fim de cada linha e só afasta os rótulos de duas
    séries; com três perfis eles se sobrepunham.
    """
    largura, altura, m, direita = 560, 280, 48, 16
    valores = [v for _, vs, _ in series for v in vs]
    lo, hi, marca, fmt_eixo = _escala(min(0.0, min(valores)), max(valores))
    util_w = largura - m - direita
    passo = util_w / max(1, len(rotulos_x) - 1)

    def py(v):
        return altura - 40 - (v - lo) / (hi - lo) * (altura - 74)

    s = [
        f'<svg viewBox="0 0 {largura} {altura}" width="100%" role="img" '
        f'aria-label="{_e(titulo)}" {FONTE} font-size="11">'
    ]
    s += _legenda_svg([(nome, cor) for nome, _, cor in series])
    s += _grade_y(m, altura - 40, 34, lo, hi, marca, util_w, fmt_eixo)
    pula = max(1, round(len(rotulos_x) / 12))
    for i, r in enumerate(rotulos_x):
        if i % pula and i != len(rotulos_x) - 1:
            continue
        s.append(
            f'<text x="{m + i * passo:.1f}" y="{altura - 22}" text-anchor="middle" '
            f'class="t-muted">{_e(r)}</text>'
        )
    for nome, vs, cor in series:
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
                f'cy="{py(v):.1f}" r="3.5" fill="{cor}"/>'
            )
    s.append("</svg>")
    return "".join(s)


def graficos(dados: dict, g: dict) -> dict:
    ag = dados["agregados"]
    saida = c2.graficos(dados)
    saida["dispersao"] = svg_dispersao_op3(dados)
    saida["op_por_fase"] = svg_op_por_fase3(dados)
    marcos = list(range(1, len(g["por_perfil"]["conservador"]["sobrevivencia"]) + 1))
    saida["sobrevivencia"] = svg_linhas_n(
        [
            (PERFIL_PT[p], [100 * x for x in g["por_perfil"][p]["sobrevivencia"]], COR_PERFIL[p])
            for p in PERFIS
        ],
        [str(f) for f in marcos],
        titulo="Runs que entraram vivas em cada andar (%)",
        fmt="{:.0f}",
    )
    saida["divergencia"] = svg_linhas_n(
        [
            (PERFIL_PT[p], g["por_perfil"][p]["divergencia_por_faixa"], COR_PERFIL[p])
            for p in PERFIS
        ],
        g["faixas"],
        titulo="Decisões que a agenda mudou, por 100 decisões",
        fmt="{:.1f}",
    )
    saida["desfechos"] = svg_desfechos(g["por_grupo"])
    saida["histograma"] = svg_histograma_op(g["extracoes"])
    saida["aceitos"] = svg_aceitos(g["aceitos"])
    saida["perfis"] = svg_barras(
        [
            (
                PERFIL_PT[p],
                100 * v["taxa"],
                COR_PERFIL[p],
                f"{PERFIL_PT[p]}: {v['vitorias']} vitórias em {v['partidas']} partidas",
            )
            for p, v in ag["por_perfil"].items()
        ],
        rotulo_w=110,
        fmt="{:.1f}%",
    )
    saida["arquetipos"] = svg_barras(
        [
            (nome, n, "var(--c-serie)", f"{nome}: {n} dos 64")
            for nome, n in g["builds_aceitas"]["arquetipos"]
        ],
        rotulo_w=150,
    )
    saida["familias"] = svg_barras(
        [
            (fam, n, "var(--c-serie)", f"{fam}: {n} passivas nos 64")
            for fam, n in g["builds_aceitas"]["familias"][:12]
        ],
        rotulo_w=150,
    )
    saida["rng"] = svg_barras(
        [
            (
                f"{r['titulo'].split(' — ')[0]}{' · zebra' if r['zebra_oficial'] else ''}",
                100 * r["taxa"],
                "var(--zebra)" if r["zebra_oficial"] else "var(--c-serie)",
                f"{r['titulo']}: vencedor oficial ganhou {r['vitorias_do_vencedor_oficial']} de "
                f"{r['repeticoes'] - r['inconclusivos']} "
                f"(IC 95% {r['ic95'][0]:.0%}–{r['ic95'][1]:.0%})",
            )
            for r in dados["rng"]
        ],
        rotulo_w=170,
        fmt="{:.0f}%",
    )
    return saida


# --- HTML --------------------------------------------------------------------


def _recurso(nome: str) -> str:
    return (RECURSOS / nome).read_text(encoding="utf-8")


def _dot(perfil: str) -> str:
    return f'<span class="dot" style="background:{COR_PERFIL[perfil]}"></span>'


def _legenda() -> str:
    return " ".join(f"{_dot(p)}{PERFIL_PT[p]}" for p in PERFIS)


def _kpis(dados: dict, g: dict) -> str:
    ag = dados["agregados"]
    part = {p["id"]: p for p in dados["participantes"]}
    campeao = part.get(dados["campeao"])
    t = g["total"]
    itens = [
        (
            "Campeão",
            campeao["nome"] if campeao else "—",
            f"{campeao['perfil_pt']}/{campeao['politica']} · OP {campeao['op']:.2f}"
            if campeao
            else "",
        ),
        (
            "Runs PvE",
            str(
                t["tentativas"]
                + (g["preenchimento"]["resumo"]["tentativas"] if g.get("preenchimento") else 0)
            ),
            f"{t['tentativas']} na geração original"
            + (
                f" · {g['preenchimento']['resumo']['tentativas']} no preenchimento"
                if g.get("preenchimento")
                else ""
            ),
        ),
        (
            "Extrações na faixa",
            str(t["qualificadas"]),
            f"{t['acima']} acima de 30 · {t['abaixo']} abaixo de 20",
        ),
        ("OP médio", f"{ag['op_medio']:.2f}", f"de {ag['op_min']:.2f} a {ag['op_max']:.2f}"),
        ("Zebras", str(len(ag["zebras"])), f"favorito venceu {ag['favoritos']} de 63"),
        ("Críticos", str(ag["criticos_total"]), f"em {ag['golpes_conectados']} golpes conectados"),
    ]
    return "".join(
        f'<div class="card kpi"><div class="sec">{_e(r)}</div><div class="kv">{_e(v)}</div>'
        f'<div class="muted">{_e(d)}</div></div>'
        for r, v, d in itens
    )


def _linhas_grupo(ag_por: dict, nomes: dict, cores: dict | None, *, com_fases: bool) -> str:
    linhas = []
    for k, v in ag_por.items():
        if not v["participantes"]:
            continue
        dot = _dot(k) if cores else ""
        celulas = [
            f"<td>{dot}{_e(nomes[k])}</td>",
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


def _linhas_geracao_grupo(g: dict) -> str:
    linhas = []
    for chave, v in g["por_grupo"].items():
        perfil, politica = chave.split("/")
        linhas.append(
            f"<tr><td>{_dot(perfil)}{_e(PERFIL_PT[perfil])}/{_e(politica)}</td>"
            f"<td class=n>{v['tentativas']}</td><td class=n>{v['mortes']}</td>"
            f"<td class=n>{v['extracoes']}</td><td class=n>{v['qualificadas']}</td>"
            f"<td class=n>{v['acima']}</td><td class=n>{v['quota']}</td>"
            f"<td class=n>#{v['ultima_aceita']}</td></tr>"
        )
    return "".join(linhas)


def _linhas_geracao_perfil(g: dict) -> str:
    linhas = []
    for p in PERFIS:
        v = g["por_perfil"][p]
        linhas.append(
            f"<tr><td>{_dot(p)}{PERFIL_PT[p]}</td><td class=n>{v['tentativas']}</td>"
            f"<td class=n>{v['taxa_morte']:.1%}</td><td class=n>{v['mortes_ate_5']}</td>"
            f"<td class=n>{v['hp_entrada_fatal']:.0%}</td>"
            f"<td class=n>{v['taxa_extracao']:.1%}</td>"
            f"<td class=n>{v['op_medio_extracao']:.2f}</td>"
            f"<td class=n>{v['taxa_divergencia']:.1%}</td></tr>"
        )
    return "".join(linhas)


def _linhas_rng(dados: dict, part: dict) -> str:
    linhas = []
    for r in dados["rng"]:
        v, p = part[r["vencedor_oficial"]], part[r["perdedor_oficial"]]
        validos = r["repeticoes"] - r["inconclusivos"]
        zebra = ' <span class="tag z">zebra</span>' if r["zebra_oficial"] else ""
        linhas.append(
            f'<tr class="clicavel" data-jogo="{r["chave"]}"><td>{_e(r["titulo"])}{zebra}</td>'
            f"<td>{_dot(v['perfil'])}{_e(v['nome'])} <span class=muted>{v['op']:.2f}</span></td>"
            f"<td>{_dot(p['perfil'])}{_e(p['nome'])} <span class=muted>{p['op']:.2f}</span></td>"
            f"<td class=n>{r['vitorias_do_vencedor_oficial']}/{validos}</td>"
            f"<td class=n>{r['taxa']:.1%}</td>"
            f"<td class=n>{r['ic95'][0]:.0%}–{r['ic95'][1]:.0%}</td></tr>"
        )
    return "".join(linhas)


def _final_html(dados: dict, svgs: dict, part: dict) -> str:
    return c2._final_html(dados, svgs, part)


def dashboard_html(dados: dict, svgs: dict, g: dict) -> str:
    part = {p["id"]: p for p in dados["participantes"]}
    ag = dados["agregados"]
    matriz = "".join(
        f"<tr><th>{_dot(a)}{PERFIL_PT[a]}</th>"
        + "".join(f"<td class=n>{ag['matriz_perfil'][a][b]}</td>" for b in PERFIS)
        + "</tr>"
        for a in PERFIS
    )

    def lista(pares):
        return _e(", ".join(f"{s} ×{n}" for s, n in pares) or "nenhum")

    efeitos = (
        f"<p><b>Status aplicados:</b> {lista(ag['status_aplicados'])}</p>"
        f"<p><b>Tentativas de status que não pegaram:</b> {lista(ag['status_falhos'])}</p>"
        f"<p><b>Buffs ativados:</b> {lista(ag['buffs'][:14])}</p>"
        f"<p><b>Controles que tiram a vez:</b> {lista(ag['controles'].items())}; "
        f"ações perdidas por controle: {ag['perdidas_controle']}.</p>"
        f"<p><b>Cura total:</b> {ag['cura_total']}.</p>"
    )
    eliminacoes = []
    for pid, v in ag["eliminacoes"]:
        p = part[pid]
        alcance = "Campeão" if p["campeao"] else _e(NOME_DA_FASE[p["fase"]])
        eliminacoes.append(
            f"<tr><td>{_dot(p['perfil'])}{_e(p['nome'])} <span class=muted>{pid}</span></td>"
            f"<td class=n>{p['op']:.2f}</td><td class=n>{v}</td><td>{alcance}</td></tr>"
        )
    valores = {
        "estilo": _recurso("estilo.css"),
        "aviso": _e(AVISO_NOMES),
        "aviso_estatistica": _e(f"{AVISO_ESTATISTICA} {AVISO_CAUSAL}"),
        "kpis": _kpis(dados, g),
        "svg_dispersao": svgs["dispersao"],
        "svg_op_por_fase": svgs["op_por_fase"],
        "svg_perfis": svgs["perfis"],
        "svg_chave": svgs["chave"],
        "svg_golpes": svgs["golpes"],
        "svg_skills": svgs["skills"],
        "svg_rodadas": svgs["rodadas"],
        "svg_sobrevivencia": svgs["sobrevivencia"],
        "svg_divergencia": svgs["divergencia"],
        "svg_desfechos": svgs["desfechos"],
        "svg_histograma": svgs["histograma"],
        "svg_aceitos": svgs["aceitos"],
        "svg_arquetipos": svgs["arquetipos"],
        "svg_familias": svgs["familias"],
        "svg_rng": svgs["rng"],
        "legenda_perfis": _legenda(),
        "curiosidades": "".join(f"<li>{_texto(f)}</li>" for f in ag["curiosidades"]),
        "opcoes_fase": "".join(f'<option value="{f}">{_e(n)}</option>' for f, _, n in FASES),
        "opcoes_perfil": "".join(f'<option value="{p}">{PERFIL_PT[p]}</option>' for p in PERFIS),
        "opcoes_politica": "".join(f'<option value="{p}">{p}</option>' for p in POLITICAS),
        "linhas_perfil": _linhas_grupo(ag["por_perfil"], PERFIL_PT, COR_PERFIL, com_fases=True),
        "linhas_politica": _linhas_grupo(
            ag["por_politica"], {p: p for p in POLITICAS}, None, com_fases=True
        ),
        "linhas_arquetipo": _linhas_grupo(
            ag["por_arquetipo"], {a: a for a in ARQUETIPOS}, None, com_fases=True
        ),
        "cabecalho_matriz": "".join(f"<th class=n>{PERFIL_PT[p]}</th>" for p in PERFIS),
        "linhas_matriz": matriz,
        "linhas_eliminacoes": "".join(eliminacoes),
        "resumo_efeitos": efeitos,
        "linhas_geracao_grupo": _linhas_geracao_grupo(g),
        "linhas_geracao_perfil": _linhas_geracao_perfil(g),
        "resumo_geracao": _texto(_resumo_geracao(g)),
        "linhas_rng": _linhas_rng(dados, part),
        "texto_rng": _e(
            f"{len(dados['rng'])} confrontos repetidos {dados['repeticoes']} vezes cada com seeds "
            "novas, metade com os lados trocados, depois da Copa oficial. A build fica fixa; só o "
            "RNG do duelo varia."
        ),
        "final": _final_html(dados, svgs, part),
    }
    pagina = _preencher(_recurso("dashboard.html"), valores)
    payload = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pagina = pagina.replace("@@js@@", _recurso("dashboard.js"))
    return pagina.replace("@@dados@@", payload)


def _resumo_geracao(g: dict) -> str:
    t = g["total"]
    final = Counter(a["perfil"] for a in g["aceitos"])
    texto = (
        f"Geração original: {t['tentativas']} runs reais de Guerreiro, desde o nível 1: "
        f"{t['mortes']} mortes, {t['extracoes']} extrações, {t['qualificadas']} na faixa de OP "
        f"20–30. A agenda de risco mudou {t['taxa_divergencia']:.1%} das decisões de mapa em "
        "relação ao cérebro canônico. "
    )
    pre = g.get("preenchimento")
    if pre:
        r = pre["resumo"]
        novos = sum(1 for a in g["aceitos"] if a["origem"].startswith("preenchimento"))
        texto += (
            f"O hardcore não fechou a quota (ficou em {final['hardcore']}/21) e, por decisão do "
            f"usuário, {novos} vagas foram preenchidas com {r['tentativas']} runs novas de "
            "conservador e moderado. "
        )
    return texto + (
        f"Os 64: conservador {final['conservador']}, moderado {final['moderado']}, hardcore "
        f"{final['hardcore']}; OP de {g['op_aceitos']['min']:.2f} a {g['op_aceitos']['max']:.2f}."
    )


def _linhas_participantes(lista: list[dict]) -> str:
    linhas = []
    for p in lista:
        resultado = "Campeão" if p["campeao"] else _e(NOME_DA_FASE[p["fase"]])
        linhas.append(
            f"<tr><td>{p['id']}</td><td>{_dot(p['perfil'])}{_e(p['nome'])}</td>"
            f"<td>{_e(p['perfil_pt'])}/{_e(p['politica'])}{_marca_origem(p)}</td>"
            f"<td class=n>{p['andar']}</td>"
            f"<td class=n>{p['nivel']}</td><td class=n>{p['op']:.2f}</td>"
            f"<td class=n>{p['hp']}</td><td class=n>{p['mp']}</td><td class=n>{p['st']}</td>"
            f"<td class=n>{p['ag']}</td><td class=n>{p['df']}</td>"
            f"<td>{_e(p['foco'])}</td><td>{_e(', '.join(p['deck']))}</td>"
            f"<td class=n>{p['vitorias']}</td><td>{resultado}</td></tr>"
        )
    return "".join(linhas)


def _marca_origem(p: dict) -> str:
    return "" if p["origem"] == "original" else ' <span class="tag">preench.</span>'


def _gladiador_html(p: dict) -> str:
    return f"{_dot(p['perfil'])}{_e(p['nome'])} <span class=muted>{p['op']:.2f}</span>"


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
    for j, lado in c2._trajetoria(dados):
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


def visual_html(dados: dict, svgs: dict, g: dict) -> str:
    """A página que o Chromium imprime: A4 paisagem, com a chave em A2 paisagem."""
    part = {p["id"]: p for p in dados["participantes"]}
    ag = dados["agregados"]
    ordenados = sorted(dados["participantes"], key=lambda p: -p["op"])
    resultados = _linhas_resultados(dados, part)
    zebras = "".join(
        f"<tr><td>{_e(r['nome_fase'])}</td><td>{_gladiador_html(part[r['vencedor']])}</td>"
        f"<td>{_gladiador_html(part[r['perdedor']])}</td>"
        f"<td class=n>{r['delta_op']:.2f}</td><td class=n>{r['rodadas']}</td></tr>"
        for r in ag["zebras"][:14]
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
        "<thead><tr><th>ID</th><th>Gladiador</th><th>Perfil/política</th><th class=n>Andar</th>"
        "<th class=n>Nv</th><th class=n>OP</th><th class=n>HP</th><th class=n>MP</th>"
        "<th class=n>ST</th><th class=n>AG</th><th class=n>DF</th><th>Canais</th>"
        "<th>Skills</th><th class=n>V</th><th>Resultado</th></tr></thead>"
    )
    cab_resultados = (
        "<thead><tr><th>#</th><th>Lado 1</th><th>Lado 2</th><th>Vencedor</th>"
        "<th class=n>Rod.</th><th class=n>HP</th><th class=n>ΔOP</th></tr></thead>"
    )
    t = g["total"]
    subtitulo = (
        f"Mata-mata MD1 de 64 Guerreiros extraídos de {t['tentativas']} runs PvE reais · seed "
        f"{SEMENTE_PRINCIPAL} · 63 partidas reais do motor, cada uma repetida sem e com auditoria."
    )
    valores = {
        "estilo": _recurso("estilo.css"),
        "subtitulo": _e(subtitulo),
        "kpis": _kpis(dados, g),
        "svg_sobrevivencia": svgs["sobrevivencia"],
        "svg_desfechos": svgs["desfechos"],
        "svg_histograma": svgs["histograma"],
        "svg_divergencia": svgs["divergencia"],
        "svg_aceitos": svgs["aceitos"],
        "svg_arquetipos": svgs["arquetipos"],
        "svg_familias": svgs["familias"],
        "linhas_geracao_perfil": _linhas_geracao_perfil(g),
        "linhas_geracao_grupo": _linhas_geracao_grupo(g),
        "legenda_perfis": _legenda(),
        "aviso": _e(f"{AVISO_NOMES} {AVISO_ESTATISTICA}"),
        "aviso_causal": _e(AVISO_CAUSAL),
        "svg_chave": svgs["chave"],
        "cabecalho_participantes": cab_participantes,
        "participantes_1": _linhas_participantes(ordenados[:32]),
        "participantes_2": _linhas_participantes(ordenados[32:]),
        "cabecalho_resultados": cab_resultados,
        "resultados_1": "".join(resultados[:1]),
        "resultados_2": "".join(resultados[1:]),
        "svg_dispersao": svgs["dispersao"],
        "svg_op_por_fase": svgs["op_por_fase"],
        "svg_golpes": svgs["golpes"],
        "svg_rodadas": svgs["rodadas"],
        "zebras": zebras,
        "svg_skills": svgs["skills"],
        "svg_perfis": svgs["perfis"],
        "linhas_perfil": _linhas_grupo(ag["por_perfil"], PERFIL_PT, COR_PERFIL, com_fases=False),
        "linhas_politica": _linhas_grupo(
            ag["por_politica"], {p: p for p in POLITICAS}, None, com_fases=False
        ),
        "svg_rng": svgs["rng"],
        "linhas_rng": _linhas_rng(dados, part),
        "curiosidades": "".join(f"<li>{_texto(f)}</li>" for f in ag["curiosidades"]),
        "trajetoria": _trajetoria_html(dados, part),
        "svg_final_iniciativa": svgs["final_iniciativa"],
        "svg_final_hp": svgs["final_hp"],
        "decisivo": decisivo,
        "diagnostico": _lista_diagnostico(final.get("diagnostico", ())),
    }
    return _preencher(_recurso("visual.html"), valores)


def escrever_tudo(copa, diagnostico: list[dict], pasta: Path | None = None, *, pdf=True) -> list:
    from tools.arena_copa_03 import PASTA, ler_gladiadores

    pasta = pasta or PASTA
    pasta.mkdir(parents=True, exist_ok=True)
    g = modelo_geracao(pasta)
    dados = modelo(copa, diagnostico, g, ler_gladiadores(pasta))
    caminhos = [pasta / ARQUIVO_GERACAO, pasta / ARQUIVO_RELATORIO]
    caminhos[0].write_text(geracao_md(g) + "\n", encoding="utf-8")
    caminhos[1].write_text(relatorio_md(dados, copa) + "\n", encoding="utf-8")
    if "final" in copa.fases:
        final = copa.fases["final"][0]
        caminhos.append(pasta / ARQUIVO_FINAL)
        caminhos[-1].write_text(relatorio_final(final, copa=COPA) + "\n", encoding="utf-8")
        caminhos.append(pasta / ARQUIVO_TRACE)
        trace = trace_json(final, copa=COPA, semente_principal=SEMENTE_PRINCIPAL)
        caminhos[-1].write_text(
            json.dumps(trace, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    svgs = graficos(dados, g)
    caminhos.append(pasta / ARQUIVO_DASHBOARD)
    caminhos[-1].write_text(dashboard_html(dados, svgs, g), encoding="utf-8")
    if pdf:
        motivo = c2.imprimir_pdf(visual_html(dados, svgs, g), pasta / ARQUIVO_PDF)
        if motivo is None:
            caminhos.append(pasta / ARQUIVO_PDF)
        else:
            print(motivo)
    for nome in (
        ARQUIVO_GLADIADORES,
        ARQUIVO_RUNS,
        ARQUIVO_RUNS_PREENCHIMENTO,
        ARQUIVO_PLANO,
        ARQUIVO_PILOTO,
        ARQUIVO_DIAGNOSTICO,
    ):
        if (pasta / nome).exists():
            caminhos.append(pasta / nome)
    return caminhos
