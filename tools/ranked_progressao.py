"""Ranked offline, Fase 6.1: impasses, progressão por divisões e a elite.

Uso:
    python tools/ranked_progressao.py trajetorias [--trabalhadores 4]
    python tools/ranked_progressao.py impasse
    python tools/ranked_progressao.py formula
    python tools/ranked_progressao.py repeticao
    python tools/ranked_progressao.py carreiras --partidas 200 [--nome carreira]
    python tools/ranked_progressao.py progressao
    python tools/ranked_progressao.py relatorio

Reaproveita os confrontos reais da Fase 6 (`reports/ranked/`). Tudo é
reprodutível pela semente: um confronto refeito com a mesma semente é o mesmo.

## As trajetórias (`trajetorias`)

Para decidir o critério de impasse com dados, e não no chute, refaz pelo motor
de verdade os confrontos que importam, guardando o HP e o MP dos dois lados ao
fim de cada rodada:

- todos os que bateram o limite técnico na Fase 6 (amostra, calibração e as
  carreiras dos jogadores artificiais);
- todos os que terminaram em KO depois de `LONGOS` rodadas — as partidas
  longas e legítimas que o critério NÃO pode encerrar;
- uma amostra fixa das partidas comuns.

Saída: `reports/ranked/fase61/trajetorias.jsonl`.

## As carreiras (`carreiras`)

Cinco jogadores artificiais, um por faixa da Ladder calibrada (baixa,
intermediária, alta, a fronteira Obsidian/Master e a elite). Cada um joga com
o gladiador de um NPC (o gêmeo fica fora do matchmaking dele), começa do
centro sem priori, e o mundo joga NPC × NPC entre as partidas dele — pelo
caminho do jogo: `MundoRanqueado`, matchmaking, árbitro de impasse, leaderboard.

O relógio é injetado: o jogador joga `SESSAO` partidas por dia, uma a cada
`MINUTOS_POR_PARTIDA` minutos, começando às `HORA_DA_SESSAO` (UTC), e fecha o
jogo até o dia seguinte. Cada linha registra a partida dele e as do mundo, com
seed e desfecho, e é o que basta para refazer a carreira inteira sem o motor
(`progressao`), com outro ciclo de leaderboard.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

from ranked_experimentos import semente  # noqa: E402

from src.engine.arena_populacao import Populacao  # noqa: E402

FASE6 = RAIZ / "reports" / "ranked"
PASTA = FASE6 / "fase61"
TRABALHO = FASE6 / "_trabalho"

MINUTOS_POR_PARTIDA = 3.0
SESSAO = 40
HORA_DA_SESSAO = 19
INICIO = 1_798_761_600  # 2027-01-01 00:00 UTC: só a origem do relógio injetado
MUNDO_POR_PARTIDA = 3
FAIXAS = {"baixo": 10.0, "intermediario": 50.0, "alto": 78.0, "fronteira": 90.0, "elite": 98.0}

LONGOS = 100
COMUNS = 200
TETO_DA_TRAJETORIA = 1500


# --- as trajetórias -----------------------------------------------------------------


def _ler(nome: str) -> list[dict]:
    return [json.loads(x) for x in (FASE6 / nome).read_text(encoding="utf-8").splitlines()]


def desenho_das_trajetorias() -> list[dict]:
    """Os confrontos a refazer, em ordem fixa."""
    partidas: list[dict] = []
    comuns: list[dict] = []
    for nome in ("amostra.jsonl", "calibracao.jsonl", "holdout2.jsonl"):
        for r in _ler(nome):
            base = {"a": r["a"], "b": r["b"], "semente": r["semente"], "origem": nome}
            if not r.get("vencedor"):
                partidas.append({**base, "grupo": "impasse_fase6"})
            elif r["rodadas"] >= LONGOS:
                partidas.append({**base, "grupo": "longo"})
            else:
                comuns.append({**base, "grupo": "comum"})
    for arquivo in sorted((FASE6 / "grind").glob("carreira_*.jsonl")):
        gemeo = arquivo.stem.split("_", 1)[1]
        eu = f"jogador:{gemeo}"
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            if r["venceu"] is None:
                partidas.append(
                    {
                        "a": gemeo,
                        "b": r["oponente"],
                        "semente": semente("grind", eu, r["n"], 0),
                        "origem": arquivo.name,
                        "grupo": "impasse_fase6",
                    }
                )
    rng = random.Random(semente("fase61", "comuns"))
    partidas += rng.sample(comuns, COMUNS)
    return partidas


def trajetoria(partida: dict) -> dict:
    """O confronto refeito, sem limite de rodada abaixo do teto, com HP/MP por rodada."""
    from src.engine import ranked_partidas
    from src.ranked.impasse import Observador

    observador = Observador(TETO_DA_TRAJETORIA)
    inicio = time.perf_counter()
    confronto = ranked_partidas.jogar(
        Populacao(), partida["a"], partida["b"], partida["semente"], arbitro=observador
    )
    return {
        **partida,
        "vencedor": confronto.vencedor,
        "motivo": confronto.motivo,
        "rodadas": confronto.rodadas,
        "segundos": round(time.perf_counter() - inicio, 2),
        "maximos": observador.maximos,
        "hp": observador.hp,
        "mp": observador.mp,
    }


def trajetorias(trabalhadores: int = 4) -> list[dict]:
    partidas = desenho_das_trajetorias()
    arquivo = TRABALHO / "trajetorias.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    feitas = {}
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            feitas[(r["a"], r["b"], r["semente"])] = r
    pendentes = [p for p in partidas if (p["a"], p["b"], p["semente"]) not in feitas]
    print(f"{len(partidas)} confrontos, {len(pendentes)} pendentes", flush=True)
    with ProcessPoolExecutor(trabalhadores, mp_context=mp.get_context("spawn")) as pool:
        futuros = {pool.submit(trajetoria, p): p for p in pendentes}
        with open(arquivo, "a", encoding="utf-8") as saida:
            while futuros:
                prontos, _ = wait(futuros, return_when=FIRST_COMPLETED)
                for futuro in prontos:
                    futuros.pop(futuro)
                    r = futuro.result()
                    saida.write(json.dumps(r, ensure_ascii=False) + "\n")
                    saida.flush()
                    os.fsync(saida.fileno())
                    feitas[(r["a"], r["b"], r["semente"])] = r
    resultado = [feitas[(p["a"], p["b"], p["semente"])] for p in partidas]
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "trajetorias.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in resultado), encoding="utf-8"
    )
    return resultado


# --- a análise do impasse (`impasse`) ------------------------------------------------

JANELAS = (100, 150, 200, 250)


def _arbitrar(r: dict, janela: int):
    """O árbitro de verdade sobre uma trajetória gravada: a rodada do veredito, ou `None`."""
    from src.ranked.impasse import ArbitroDeImpasse

    if not r["maximos"]:
        return None
    arbitro = ArbitroDeImpasse(janela=janela, teto=10**9)
    for rodada, (hp, mana) in enumerate(zip(r["hp"], r["mp"]), start=1):
        veredito = arbitro.observar(rodada, hp, mana, r["maximos"])
        if veredito is not None:
            return veredito.rodada
    return None


def _maior_espera(r: dict) -> int:
    """A maior sequência de rodadas sem mínimo novo de HP ou MP numa trajetória."""
    from src.ranked.impasse import ArbitroDeImpasse

    if not r["maximos"]:
        return 0
    arbitro = ArbitroDeImpasse(janela=10**9, teto=10**9)
    maior = 0
    for rodada, (hp, mana) in enumerate(zip(r["hp"], r["mp"]), start=1):
        arbitro.observar(rodada, hp, mana, r["maximos"])
        maior = max(maior, arbitro.sem_desgaste)
    return maior


def impasse() -> dict:
    """O critério de impasse contra as trajetórias reais: o que ele encerra, e quando."""
    from src.ranked.impasse import JANELA, MARGEM, TETO

    trajetorias = [
        json.loads(x)
        for x in (PASTA / "trajetorias.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    gravadas = []
    for nome in ("amostra.jsonl", "calibracao.jsonl", "holdout2.jsonl"):
        gravadas += _ler(nome)
    rodadas = sorted(r["rodadas"] for r in gravadas if r.get("vencedor"))

    def quantil(q):
        return rodadas[min(len(rodadas) - 1, int(q * len(rodadas)))]

    terminadas = [r for r in trajetorias if r["vencedor"]]
    sem_fim = [r for r in trajetorias if not r["vencedor"]]
    esperas = sorted(
        ((_maior_espera(r), r["rodadas"], f"{r['a']}×{r['b']}") for r in terminadas),
        reverse=True,
    )
    janelas = {}
    for janela in JANELAS:
        convertidas = []
        for r in terminadas:
            rodada = _arbitrar(r, janela)
            if rodada is not None:
                convertidas.append(
                    {
                        "dupla": f"{r['a']}×{r['b']}",
                        "ko_na_rodada": r["rodadas"],
                        "empate_na": rodada,
                    }
                )
        encerradas = [_arbitrar(r, janela) for r in sem_fim]
        janelas[janela] = {
            "ko_que_viram_empate": convertidas,
            "sem_fim_encerradas_em": encerradas,
        }
    resultado = {
        "parametros": {"janela": JANELA, "margem": MARGEM, "teto": TETO},
        "partidas_gravadas_da_fase6": {
            "com_vencedor": len(rodadas),
            "sem_vencedor_em_500": sum(1 for r in gravadas if not r.get("vencedor")),
            "rodadas_p50_p90_p99_max": [quantil(0.5), quantil(0.9), quantil(0.99), rodadas[-1]],
        },
        "trajetorias": {
            "total": len(trajetorias),
            "por_grupo": {
                g: sum(1 for r in trajetorias if r["grupo"] == g)
                for g in ("impasse_fase6", "longo", "comum")
            },
            "impasses_da_fase6_que_terminaram_ate_1500": sum(
                1 for r in trajetorias if r["grupo"] == "impasse_fase6" and r["vencedor"]
            ),
            "sem_fim_em_1500": [f"{r['a']}×{r['b']}" for r in sem_fim],
        },
        "maiores_esperas_em_partidas_terminadas": [
            {"espera": e, "rodadas": n, "dupla": d} for e, n, d in esperas[:12]
        ],
        "janelas": janelas,
    }
    (PASTA / "impasse.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return resultado


# --- a fórmula de PR sobre as carreiras da Fase 6 (`formula`) ------------------------

_BASE = {
    "K": 40.0,
    "BETA": 0.20,
    "MULTIPLICADOR_MAXIMO": 3.0,
    "ESCUDO": 3,
    "PR_APOS_REBAIXAMENTO": 75,
}
VARIANTES = [
    {"nome": "proposta", **_BASE},
    {"nome": "K 30", **_BASE, "K": 30.0},
    {"nome": "K 50", **_BASE, "K": 50.0},
    {"nome": "β 0,12", **_BASE, "BETA": 0.12},
    {"nome": "β 0,30", **_BASE, "BETA": 0.30},
    {"nome": "sem escudo", **_BASE, "ESCUDO": 0},
    {"nome": "rebaixa contínuo", **_BASE, "PR_APOS_REBAIXAMENTO": 100},
    {
        "nome": "sem puxar para o alvo",
        **_BASE,
        "BETA": 0.0,
        "MULTIPLICADOR_MAXIMO": 1.0,
        "ESCUDO": 0,
        "PR_APOS_REBAIXAMENTO": 100,
    },
]


def _pr_numa_carreira_da_fase6(linhas: list[dict]) -> dict:
    """A fórmula reaplicada a uma carreira gravada da Fase 6 (resultado, chance e percentil)."""
    from src.ranked import progressao as pg

    prog = None
    passos = []
    for i, r in enumerate(linhas):
        if i < 9:
            continue
        if i == 9:
            prog = pg.posicionar(pg.alvo(r["percentil"]))
            passos.append(
                {
                    "eventos": ["posicionamento"],
                    "coordenada": prog.coordenada,
                    "divisao": prog.divisao,
                    "alvo": pg.alvo(r["percentil"]),
                    "pr": None,
                    "resultado": None,
                    "rank_do_percentil": r["rank"],
                }
            )
            continue
        if r["venceu"] is None:
            continue
        meta = pg.alvo(linhas[i - 1]["percentil"])
        pontos = 1.0 if r["venceu"] else 0.0
        delta = pg.variacao(pontos, r["probabilidade"], prog.coordenada, meta)
        eventos = [e["evento"] for e in pg.aplicar(prog, delta, meta)]
        passos.append(
            {
                "eventos": eventos,
                "coordenada": prog.coordenada,
                "divisao": prog.divisao,
                "alvo": pg.alvo(r["percentil"]),
                "pr": delta,
                "resultado": "vitoria" if pontos else "derrota",
                "rank_do_percentil": r["rank"],
            }
        )
    regulares = [p for p in passos if p["alvo"] < pg.TOPO]
    ranks_vis = [pg.rank_da_divisao(p["divisao"]) for p in passos]
    distancias = [abs(p["alvo"] - p["coordenada"]) for p in regulares]
    return {
        "ganho": round(
            sum(p["pr"] for p in passos if p["resultado"] == "vitoria")
            / max(1, sum(p["resultado"] == "vitoria" for p in passos)),
            1,
        ),
        "perda": round(
            sum(p["pr"] for p in passos if p["resultado"] == "derrota")
            / max(1, sum(p["resultado"] == "derrota" for p in passos)),
            1,
        ),
        "promocoes": sum("promocao" in p["eventos"] for p in passos),
        "rebaixamentos": sum("rebaixamento" in p["eventos"] for p in passos),
        "oscilacoes": _oscilacoes(passos),
        "trocas_de_rank": sum(1 for a, b in zip(ranks_vis, ranks_vis[1:]) if a != b),
        "trocas_de_rank_por_percentil": sum(
            1
            for a, b in zip(passos, passos[1:])
            if a["rank_do_percentil"] != b["rank_do_percentil"]
        ),
        "distancia_media": round(sum(distancias) / len(distancias)) if distancias else None,
        "final": f"{pg.nome_da_divisao(passos[-1]['divisao'])} {prog.pr} PR",
    }


def formula() -> dict:
    """As variantes da fórmula sobre as 4 carreiras reais da Fase 6, sem jogar nada."""
    from src.ranked import progressao as pg

    carreiras_ = {
        p.stem.split("_")[1]: [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()]
        for p in sorted((FASE6 / "grind").glob("carreira_*.jsonl"))
    }
    originais = {k: getattr(pg, k) for k in _BASE}
    resultado = []
    try:
        for variante in VARIANTES:
            for k in _BASE:
                setattr(pg, k, variante[k])
            resultado.append(
                {
                    "variante": variante,
                    "carreiras": {
                        nome: _pr_numa_carreira_da_fase6(linhas)
                        for nome, linhas in carreiras_.items()
                    },
                }
            )
    finally:
        for k, v in originais.items():
            setattr(pg, k, v)
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / "formula.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return resultado


# --- a repetição de adversário, por modelo (`repeticao`) -------------------------------

PARTIDAS_DO_MODELO = 300


def _escolher_fase6(ladder, identidade: str, rng, *, excluir=()):
    """A política da Fase 6, para comparação: janela, exclusão das 3 últimas, k mais perto."""
    from src.ranked import matchmaking as mm

    proibidos = {identidade, *excluir}
    candidatos = [r.identidade for r in ladder.npcs() if r.identidade not in proibidos]
    etapa = mm.fase(ladder[identidade].partidas)
    desvio = mm.desvio_da_populacao(ladder, candidatos)
    alvo = ladder.valor(identidade) + mm.empurrao_da_sequencia(ladder, identidade, desvio)
    if etapa == mm.DESCOBERTA:
        alvo += rng.uniform(-1.0, 1.0) * mm.JANELA[mm.DESCOBERTA] * desvio
    recentes = {e["oponente"] for e in ladder[identidade].historico[-3:]}
    janela = mm.JANELA[etapa] * desvio
    escolhidos: list[str] = []
    for _ in range(8):
        escolhidos = [
            c for c in candidatos if c not in recentes and abs(ladder.valor(c) - alvo) <= janela
        ]
        if escolhidos:
            break
        janela *= 2
    if not escolhidos:
        escolhidos = candidatos
    escolhidos.sort(key=lambda c: (abs(ladder.valor(c) - alvo), c))
    return mm.Escolha(rng.choice(escolhidos[: mm.MAIS_PROXIMOS[etapa]]), etapa, alvo, desvio)


def _modelo(ladder, verdade: dict, eu: str, gemeo: str, escolher, rng, partidas: int) -> dict:
    """Uma carreira em que o resultado sai da chance do Glicko-2 entre as forças VERDADEIRAS."""
    from src.ranked.glicko2 import Glicko2, RatingGlicko2

    g = Glicko2()
    oponentes, desequilibrio = [], []
    for _ in range(partidas):
        escolha = escolher(ladder, eu, rng, excluir={gemeo})
        o = escolha.oponente
        desequilibrio.append(abs(ladder.esperado(eu, o) - 0.5))
        chance = g.esperado(RatingGlicko2(verdade[gemeo], 60), RatingGlicko2(verdade[o], 60))
        vencedor = eu if rng.random() < chance else o
        ladder.registrar(eu, o, vencedor, origem="modelo")
        oponentes.append(o)
    repetidos = sum(1 for i, o in enumerate(oponentes) if o in oponentes[max(0, i - 10) : i])
    depois = oponentes[10:]
    repetidos_depois = sum(
        1 for i, o in enumerate(depois, start=10) if o in oponentes[max(0, i - 10) : i]
    )
    return {
        "repeticao": round(repetidos / partidas, 3),
        "repeticao_depois_do_posicionamento": round(repetidos_depois / max(1, len(depois)), 3),
        "distintos": len(set(oponentes)),
        "desequilibrio_medio": round(sum(desequilibrio) / partidas, 3),
    }


def _populacao_sintetica(base, tamanho: int, rng):
    """`tamanho` NPCs com ratings tirados da Ladder calibrada (com ruído), para medir escala."""
    from src.ranked.ladder import Ladder, Registro

    valores = [base.valor(r.identidade) for r in base.npcs()]
    sistema = base.sistema
    registros = [
        Registro(
            f"S{i:04d}",
            f"S{i}",
            "warrior",
            True,
            sistema.novo(rng.choice(valores) + rng.gauss(0, 25), 70),
        )
        for i in range(tamanho)
    ]
    return Ladder(sistema, registros)


def repeticao() -> dict:
    """A política nova contra a da Fase 6, com 186 (os calibrados) e com 5.000 (sintéticos)."""
    import tempfile
    import time as relogio_

    from src.ranked import matchmaking as mm
    from src.ranked.ladder import Registro

    base = mundo_inicial(3600, os.path.join(tempfile.mkdtemp(prefix="rep-"), "r.json")).ladder
    escolhidos = gemeos(type("M", (), {"ladder": base})())
    resultado: dict = {"186": {}, "5000": {}}
    for nome, escolher in (("fase6", _escolher_fase6), ("nova", mm.escolher_oponente)):
        for faixa, gemeo in escolhidos.items():
            ladder = type(base).de_dict(base.sistema, base.para_dict())
            verdade = {r.identidade: ladder.valor(r.identidade) for r in ladder.npcs()}
            eu = f"jogador:{gemeo}"
            ladder.adicionar(Registro(eu, "Eu", "warrior", False, ladder.sistema.novo()))
            rng = random.Random(semente("repeticao", nome, faixa))
            resultado["186"].setdefault(faixa, {})[nome] = _modelo(
                ladder, verdade, eu, gemeo, escolher, rng, PARTIDAS_DO_MODELO
            )
    rng = random.Random(semente("repeticao", "5000"))
    grande = _populacao_sintetica(base, 5000, rng)
    ordem = sorted(grande.npcs(), key=lambda r: -grande.valor(r.identidade))
    for nome, escolher in (("fase6", _escolher_fase6), ("nova", mm.escolher_oponente)):
        for faixa, alvo in FAIXAS.items():
            ladder = type(grande).de_dict(grande.sistema, grande.para_dict())
            gemeo = ordem[int((100 - alvo) / 100 * (len(ordem) - 1))].identidade
            verdade = {r.identidade: ladder.valor(r.identidade) for r in ladder.npcs()}
            eu = f"jogador:{gemeo}"
            ladder.adicionar(Registro(eu, "Eu", "warrior", False, ladder.sistema.novo()))
            inicio = relogio_.perf_counter()
            medida = _modelo(
                ladder, verdade, eu, gemeo, escolher, random.Random(semente(nome, faixa)), 100
            )
            medida["ms_por_escolha"] = round((relogio_.perf_counter() - inicio) * 10, 1)
            resultado["5000"].setdefault(faixa, {})[nome] = medida
    (PASTA / "repeticao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return resultado


# --- as carreiras ------------------------------------------------------------------


def gemeos(mundo) -> dict[str, str]:
    """O NPC de cada faixa: o mais perto do percentil da faixa na Ladder calibrada."""
    escolhidos: dict[str, str] = {}
    for faixa, alvo in FAIXAS.items():
        escolhidos[faixa] = min(
            (r.identidade for r in mundo.ladder.npcs()),
            key=lambda i: (abs(mundo.ladder.percentil(i) - alvo), i),
        )
    return escolhidos


def relogio(n: int) -> float:
    """O instante da partida `n` (1, 2, ...) do jogador artificial."""
    dia, k = divmod(n - 1, SESSAO)
    return INICIO + dia * 86_400 + HORA_DA_SESSAO * 3600 + k * MINUTOS_POR_PARTIDA * 60


def mundo_inicial(periodo: int, caminho: str):
    from src.engine.ranked_mundo import MundoRanqueado

    mundo = MundoRanqueado.carregar(Populacao(), caminho)
    mundo.leaderboard.periodo = periodo
    return mundo


def _confronto_do_registro(m: dict):
    from src.engine.ranked_mundo import Anulada
    from src.engine.ranked_partidas import Confronto

    if m["resultado"] == "anulada":
        return Anulada(m["a"], m["b"], m["motivo"])
    return Confronto(
        m["a"], m["b"], m["semente"], m["vencedor"], m["motivo"], m["rodadas"], m["segundos"]
    )


def _retrato(mundo, n: int, agora: float, resumo: dict) -> dict:
    """O que guardar de uma atualização: o resumo, os Definitive Masters e o tamanho da elite."""
    linhas = mundo.leaderboard.linhas
    return {
        "n": n,
        "agora": agora,
        **resumo,
        "top5": [x["identidade"] for x in linhas if x["titulo"]],
        "elite": sum(1 for x in linhas if x["elite"]),
    }


def _aplicar_linha(mundo, eu: str, linha: dict, eventos_da_leaderboard: list):
    """Uma linha da carreira no mundo: a sessão, a partida do jogador, as do mundo."""
    if linha.get("sessao"):
        resumo = mundo.atualizar_leaderboard(linha["agora"])
        if resumo:
            eventos_da_leaderboard.append(_retrato(mundo, linha["n"], linha["agora"], resumo))
        mundo.ao_retornar(linha["agora"])
    atualizacao = mundo.registrar_do_jogador(
        eu, linha["oponente"], linha["resultado"], motivo=linha["motivo"]
    )
    for m in linha["mundo"]:
        mundo.aplicar_do_mundo(_confronto_do_registro(m))
    depois = linha["agora"] + MINUTOS_POR_PARTIDA * 60
    resumo = mundo.atualizar_leaderboard(depois)
    if resumo:
        eventos_da_leaderboard.append(_retrato(mundo, linha["n"], depois, resumo))
    return atualizacao


def _carreira(faixa: str, gemeo: str, partidas: int, arquivo: str) -> str:
    """A carreira de um jogador artificial, com checkpoint por partida."""
    import tempfile

    from src.engine import ranked_partidas
    from src.ranked import matchmaking as mm

    populacao = Populacao()
    pasta = tempfile.mkdtemp(prefix="carreira-")
    mundo = mundo_inicial(3600, os.path.join(pasta, "ranked.json"))
    mundo.salvar = lambda: None  # a carreira não precisa de disco a cada partida
    o = populacao.get(gemeo)
    eu = f"jogador:{gemeo}"
    mundo.inscrever(eu, o.apelido, o.classe)
    caminho = Path(arquivo)
    feitas = []
    if caminho.exists():
        feitas = [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines()]
    descartar: list = []
    for linha in feitas:
        _aplicar_linha(mundo, eu, linha, descartar)
    with open(caminho, "a", encoding="utf-8") as saida:
        for n in range(len(feitas) + 1, partidas + 1):
            agora = relogio(n)
            sessao = n == 1 or (n - 1) % SESSAO == 0
            retorno = None
            if sessao:
                mundo.atualizar_leaderboard(agora)
                retorno = mundo.ao_retornar(agora)
            registro = mundo.ladder[eu]
            rng = random.Random(semente("fase61", "carreira", eu, n))
            escolha = mm.escolher_oponente(mundo.ladder, eu, rng, excluir={gemeo})
            oponente = escolha.oponente
            prob = mundo.ladder.esperado(eu, oponente)
            semente_da_partida = semente("fase61", "partida", eu, n)
            confronto = ranked_partidas.jogar(populacao, gemeo, oponente, semente_da_partida)
            if confronto.vencedor is None:
                resultado = "empate"
            else:
                resultado = "vitoria" if confronto.vencedor == gemeo else "derrota"
            linha = {
                "n": n,
                "agora": agora,
                "sessao": sessao,
                "retorno": retorno,
                "fase": escolha.fase,
                "partidas_antes": registro.partidas,
                "oponente": oponente,
                "probabilidade": round(prob, 4),
                "resultado": resultado,
                "motivo": confronto.motivo,
                "rodadas": confronto.rodadas,
                "segundos": confronto.segundos,
                "semente": semente_da_partida,
            }
            mundo.registrar_do_jogador(eu, oponente, resultado, motivo=confronto.motivo)
            linha["mundo"] = []
            for a, b, s_ in mundo.planejar(min(mundo.fila, MUNDO_POR_PARTIDA)):
                c = ranked_partidas.jogar(populacao, a, b, s_)
                mundo.aplicar_do_mundo(c)
                linha["mundo"].append({**c.para_dict()})
            mundo.atualizar_leaderboard(agora + MINUTOS_POR_PARTIDA * 60)
            linha["rating"] = round(mundo.ladder.valor(eu), 2)
            linha["rd"] = round(mundo.ladder.incerteza(eu), 2)
            saida.write(json.dumps(linha, ensure_ascii=False) + "\n")
            saida.flush()
            os.fsync(saida.fileno())
    return arquivo


def carreiras(partidas: int, nome: str = "carreira", faixas: list[str] | None = None) -> dict:
    """As cinco carreiras em paralelo, cada uma com o próprio mundo. Retomável."""
    import tempfile

    pasta = tempfile.mkdtemp(prefix="gemeos-")
    escolhidos = gemeos(mundo_inicial(3600, os.path.join(pasta, "ranked.json")))
    faixas = faixas or list(FAIXAS)
    TRABALHO.mkdir(parents=True, exist_ok=True)
    arquivos = {f: str(TRABALHO / f"{nome}_{f}_{escolhidos[f]}.jsonl") for f in faixas}
    with ProcessPoolExecutor(len(faixas), mp_context=mp.get_context("spawn")) as pool:
        futuros = [pool.submit(_carreira, f, escolhidos[f], partidas, arquivos[f]) for f in faixas]
        for f in futuros:
            f.result()
    return arquivos


# --- a progressão refeita sem o motor (`progressao`) ----------------------------------

PERIODOS = {"1h": 3600, "24h": 86_400}
OSCILACAO = 3


def _arquivos_de_carreira(nome: str = "carreira") -> list[Path]:
    ordem = {f: i for i, f in enumerate(FAIXAS)}
    arquivos = [p for p in TRABALHO.glob(f"{nome}_*_*.jsonl") if p.stem.split("_")[1] in FAIXAS]
    return sorted(arquivos, key=lambda p: ordem[p.stem.split("_")[1]])


def _coordenada(progresso) -> int | None:
    from src.ranked import progressao as pg

    if progresso.elite is not None:
        return pg.TOPO + pg.POR_RANK * (pg.ELITE.index(progresso.elite) + 1) - 1
    return progresso.coordenada


def refazer(arquivo: Path, periodo: int) -> dict:
    """Uma carreira refeita pelo caminho do jogo, com o ciclo de leaderboard pedido."""
    import tempfile

    linhas = [json.loads(x) for x in arquivo.read_text(encoding="utf-8").splitlines()]
    faixa, gemeo = arquivo.stem.split("_")[1:3]
    mundo = mundo_inicial(periodo, os.path.join(tempfile.mkdtemp(prefix="refazer-"), "r.json"))
    mundo.salvar = lambda: None
    o = Populacao().get(gemeo)
    eu = f"jogador:{gemeo}"
    mundo.inscrever(eu, o.apelido, o.classe)
    ladder = mundo.ladder
    eventos_lb: list[dict] = []
    passos = []
    divergencias = 0
    for linha in linhas:
        meta_antes = ladder.alvo(eu)
        atualizacao = _aplicar_linha(mundo, eu, linha, eventos_lb)
        if abs(ladder.valor(eu) - linha["rating"]) > 0.01:
            divergencias += 1
        p = ladder[eu].progresso
        pct = ladder.percentil(eu)
        passos.append(
            {
                "n": linha["n"],
                "resultado": linha["resultado"],
                "motivo": linha["motivo"],
                "pr": atualizacao.pr.get(eu) if atualizacao else None,
                "eventos": [e["evento"] for e in atualizacao.eventos.get(eu, [])]
                if atualizacao
                else [],
                "divisao": p.divisao,
                "pr_atual": p.pr,
                "elite": p.elite,
                "candidato": p.candidato,
                "titulo": p.titulo,
                "coordenada": _coordenada(p),
                "alvo": ladder.alvo(eu),
                "alvo_antes": meta_antes,
                "percentil": pct,
                "rank_do_percentil": ladder.rank(eu),
                "rating": ladder.valor(eu),
                "rd": ladder.incerteza(eu),
                "oponente": linha["oponente"],
                "probabilidade": linha["probabilidade"],
            }
        )
    meus_eventos = [
        {"n": e["n"], "agora": e["agora"], **ev}
        for e in eventos_lb
        for ev in e.get("eventos", [])
        if ev.get("identidade") == eu
    ]
    return {
        "faixa": faixa,
        "gemeo": gemeo,
        "periodo": periodo,
        "passos": passos,
        "divergencias_de_mmr": divergencias,
        "eventos_da_elite": meus_eventos,
        "atualizacoes": len(eventos_lb),
        "elite_por_atualizacao": [
            {
                "n": e["n"],
                "promocoes": sum(x["evento"] == "promocao_a_elite" for x in e["eventos"]),
                "rebaixamentos": sum(x["evento"] == "rebaixamento_da_elite" for x in e["eventos"]),
                "em_risco": sum(x["evento"] == "em_risco" for x in e["eventos"]),
            }
            for e in eventos_lb
        ],
        "top5": [e["top5"] for e in eventos_lb],
        "tamanho_da_elite": [e["elite"] for e in eventos_lb],
    }


def _oscilacoes(passos: list[dict]) -> int:
    """Promoções desfeitas (ou rebaixamentos desfeitos) em até `OSCILACAO` partidas."""
    mudancas = [
        (i, +1 if "promocao" in p["eventos"] else -1)
        for i, p in enumerate(passos)
        if "promocao" in p["eventos"] or "rebaixamento" in p["eventos"]
    ]
    return sum(1 for (i, a), (j, b) in zip(mudancas, mudancas[1:]) if a != b and j - i <= OSCILACAO)


def medir(carreira: dict) -> dict:
    """As medidas de uma carreira refeita."""
    from src.ranked import progressao as pg

    passos = carreira["passos"]
    n = len(passos)
    disputadas = [p for p in passos if p["resultado"] != "anulada"]
    posicionado = next((i for i, p in enumerate(passos) if p["divisao"] is not None), None)
    depois = passos[posicionado:] if posicionado is not None else []
    regulares = [p for p in depois if p["elite"] is None]
    ganhos = [p["pr"] for p in regulares if p["pr"] is not None and p["resultado"] == "vitoria"]
    perdas = [p["pr"] for p in regulares if p["pr"] is not None and p["resultado"] == "derrota"]
    empates_pr = [p["pr"] for p in regulares if p["pr"] is not None and p["resultado"] == "empate"]
    promocoes = sum("promocao" in p["eventos"] for p in passos)
    rebaixamentos = sum("rebaixamento" in p["eventos"] for p in passos)
    escudos = sum("escudo" in p["eventos"] for p in passos)
    ranks_vis = [
        (pg.rank_da_divisao(p["divisao"]) if p["elite"] is None else p["elite"]) for p in depois
    ]
    trocas_de_rank = sum(1 for a, b in zip(ranks_vis, ranks_vis[1:]) if a != b)
    alinhados = [
        abs(p["alvo"] - p["coordenada"])
        for p in regulares
        if p["alvo"] is not None and p["alvo"] < pg.TOPO
    ]
    mesmo_rank = sum(
        1 for p in regulares if p["rank_do_percentil"] == pg.rank_da_divisao(p["divisao"])
    )
    candidato = [p for p in passos if p["candidato"]]
    primeira_candidatura = next((p["n"] for p in passos if p["candidato"]), None)
    entrada_na_elite = next((p["n"] for p in passos if p["elite"]), None)
    oponentes = [p["oponente"] for p in passos]
    repetidos = sum(1 for i, o in enumerate(oponentes) if o in oponentes[max(0, i - 10) : i])

    def media(xs):
        return round(sum(xs) / len(xs), 1) if xs else None

    def marco(horas):
        k = int(horas * 60 / MINUTOS_POR_PARTIDA)
        if k > n:
            return None
        p = passos[k - 1]
        return {
            "exibicao": _exibicao(p),
            "percentil": None if p["percentil"] is None else round(p["percentil"], 1),
        }

    subidas = [
        p["n"] for p in passos if "promocao" in p["eventos"] or "posicionamento" in p["eventos"]
    ]
    return {
        "faixa": carreira["faixa"],
        "gemeo": carreira["gemeo"],
        "partidas": n,
        "horas": round(n * MINUTOS_POR_PARTIDA / 60, 1),
        "vitorias": sum(p["resultado"] == "vitoria" for p in passos),
        "derrotas": sum(p["resultado"] == "derrota" for p in passos),
        "empates": sum(p["resultado"] == "empate" for p in passos),
        "anuladas": n - len(disputadas),
        "posicionamento": None
        if posicionado is None
        else {
            "na_partida": passos[posicionado]["n"],
            "exibicao": _exibicao(passos[posicionado]),
            "percentil": round(passos[posicionado]["percentil"], 1),
        },
        "pr_medio": {
            "vitoria": media(ganhos),
            "derrota": media(perdas),
            "empate": media(empates_pr),
        },
        "pr_extremos": [min(perdas, default=None), max(ganhos, default=None)],
        "promocoes": promocoes,
        "rebaixamentos": rebaixamentos,
        "escudo_segurou": escudos,
        "oscilacoes": _oscilacoes(passos),
        "trocas_de_rank_visivel": trocas_de_rank,
        "partidas_por_promocao": round(len(regulares) / promocoes, 1) if promocoes else None,
        "distancia_media_ao_alvo": media(alinhados),
        "distancia_p90_ao_alvo": sorted(alinhados)[int(0.9 * len(alinhados))]
        if alinhados
        else None,
        "rank_visivel_igual_ao_do_percentil": round(mesmo_rank / len(regulares), 3)
        if regulares
        else None,
        "candidato": {
            "primeira_vez_na_partida": primeira_candidatura,
            "partidas_como_candidato": len(candidato),
            "horas_de_jogo_como_candidato": round(len(candidato) * MINUTOS_POR_PARTIDA / 60, 1),
        },
        "elite": {
            "entrada_na_partida": entrada_na_elite,
            "avaliacoes": [
                {k: e[k] for k in ("n", "evento") if k in e}
                | ({"motivos": e["motivos"]} if e.get("motivos") else {})
                | ({"para": e["para"]} if e.get("para") is not None else {})
                for e in carreira["eventos_da_elite"]
            ],
        },
        "marcos": {f"{h}h": marco(h) for h in (2, 5, 10)},
        "final": {
            "exibicao": _exibicao(passos[-1]),
            "titulo": passos[-1]["titulo"],
            "mmr": round(passos[-1]["rating"], 1),
            "rd": round(passos[-1]["rd"], 1),
            "percentil": None
            if passos[-1]["percentil"] is None
            else round(passos[-1]["percentil"], 1),
            "rank_do_percentil": passos[-1]["rank_do_percentil"],
        },
        "matchmaking": {
            "oponentes_distintos": len(set(oponentes)),
            "repetidos_nas_ultimas_10": repetidos,
            "taxa_de_repeticao": round(repetidos / n, 3),
            "chance_media": round(sum(p["probabilidade"] for p in passos) / n, 3),
            "desequilibrio_medio": round(sum(abs(p["probabilidade"] - 0.5) for p in passos) / n, 3),
        },
        "subidas_nas_partidas": subidas[:60],
        "divergencias_de_mmr": carreira["divergencias_de_mmr"],
    }


def _estabilidade_do_top5(tops: list[list[str]]) -> dict:
    """Quantas atualizações mudaram os Definitive Masters, e em quantos nomes."""
    trocas = [len(set(a) - set(b)) for a, b in zip(tops, tops[1:])]
    return {
        "atualizacoes": len(tops),
        "mudaram": sum(1 for t in trocas if t),
        "nomes_trocados": sum(trocas),
        "conjuntos_distintos": len({tuple(sorted(t)) for t in tops}),
    }


def _empates_do_mundo(arquivo: Path) -> dict:
    linhas = [json.loads(x) for x in arquivo.read_text(encoding="utf-8").splitlines()]
    mundo = [m for x in linhas for m in x["mundo"]]
    return {
        "partidas": len(mundo),
        "empates": sum(1 for m in mundo if m["vencedor"] is None),
        "rodadas_dos_empates": [m["rodadas"] for m in mundo if m["vencedor"] is None],
        "cpu_s_do_jogador": round(sum(x["segundos"] for x in linhas), 1),
        "cpu_s_do_mundo": round(sum(m["segundos"] for m in mundo), 1),
    }


def progressao(nome: str = "carreira") -> dict:
    """As carreiras refeitas com ciclo de 1 h e de 24 h, e as medidas de cada uma."""
    resultado: dict = {"periodos": {}, "mundo": {}}
    PASTA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / "carreiras"
    destino.mkdir(parents=True, exist_ok=True)
    for arquivo in _arquivos_de_carreira(nome):
        (destino / arquivo.name).write_text(arquivo.read_text(encoding="utf-8"), encoding="utf-8")
        faixa = arquivo.stem.split("_")[1]
        resultado["mundo"][faixa] = _empates_do_mundo(arquivo)
        for rotulo, periodo in PERIODOS.items():
            carreira = refazer(arquivo, periodo)
            medidas = medir(carreira)
            medidas["top5"] = _estabilidade_do_top5(carreira["top5"])
            medidas["elite_por_atualizacao"] = {
                "promocoes": sum(e["promocoes"] for e in carreira["elite_por_atualizacao"]),
                "rebaixamentos": sum(e["rebaixamentos"] for e in carreira["elite_por_atualizacao"]),
                "em_risco": sum(e["em_risco"] for e in carreira["elite_por_atualizacao"]),
                "tamanho_da_elite": [
                    min(carreira["tamanho_da_elite"], default=None),
                    max(carreira["tamanho_da_elite"], default=None),
                ],
            }
            resultado["periodos"].setdefault(rotulo, {})[faixa] = medidas
    (PASTA / "progressao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return resultado


def _exibicao(p: dict) -> str | None:
    from src.ranked import progressao as pg

    if p["elite"]:
        return p["elite"] + (" ★" if p["titulo"] else "")
    if p["divisao"] is None:
        return None
    sufixo = " (candidato)" if p["candidato"] else ""
    return f"{pg.nome_da_divisao(p['divisao'])} {p['pr_atual']} PR{sufixo}"


# --- o relatório (`relatorio`) ---------------------------------------------------------


def _n(valor, casas: int = 0) -> str:
    if valor is None:
        return "—"
    return f"{valor:.{casas}f}".replace(".", ",")


PROBLEMAS = [
    '**O "impasse" da Fase 6 não era um só fenômeno.** Refeitos até 1.500 rodadas, 8 dos '
    "15 confrontos que bateram o limite de 500 terminaram em KO (entre as rodadas 509 e "
    "1.002) e 7 — todos R31 × M33 — não terminaram nunca. Os dois casos são o mesmo "
    "equilíbrio: o MP dos dois zera por volta da rodada 100 e o HP passa a oscilar numa "
    "faixa estável; o KO, quando vem, é sorte. Por isso o critério é de desgaste (mínimo "
    "novo de HP ou MP) e não de duração.",
    "**Rebaixamento contínuo fazia pisca-pisca.** Com o PR do rebaixamento contínuo (100 − o "
    "que faltou), um gladiador na fronteira descia e subia na partida seguinte: 30 "
    "oscilações em 390 partidas na carreira W26 da Fase 6. Pousar em no máximo 75 PR e o "
    "escudo de 3 partidas derrubaram isso para 4, sem piorar a distância ao alvo.",
    "**Sem puxar para o alvo, o PR se descola do MMR.** A variante sem o multiplicador (PR "
    "puro por resultado contra expectativa) termina a carreira M11 em Diamond V com o MMR "
    "de Diamond II, e a W26 três divisões acima do alvo: distância média de 93 a 227 PR, "
    "contra 25 a 76 com β = 0,20.",
    "**Posicionar em 0 PR rebaixava na primeira derrota.** A primeira versão punha o "
    "gladiador no começo da divisão do alvo; qualquer derrota logo depois do posicionamento "
    "descia uma divisão. O posicionamento agora nasce no PR do alvo e com escudo.",
    "**Repetição no topo é estrutural com 186.** O custo de repetição zera a repetição nas "
    "faixas baixa, média, alta e na fronteira, mas no topo há poucos rivais: o peso 4 "
    "deixava 34% de repetição no modelo; o peso 8 deixa 16%, ao custo de partidas um pouco "
    "menos equilibradas. Com 5.000, a repetição some nas duas políticas.",
    "**Títulos com população pequena.** Os Definitive Masters são os cinco primeiros DA "
    "ELITE; com menos de ~60 gladiadores competitivos, a elite (percentil ≥ 92) tem menos "
    "de cinco membros e sobra título. Com 186 a elite tem 15.",
]


def relatorio() -> str:
    """O relatório da Fase 6.1, a partir dos JSONs de `reports/ranked/fase61/`."""
    from src.ranked import impasse as imp
    from src.ranked import leaderboard as lbm
    from src.ranked import matchmaking as mm
    from src.ranked import progressao as pg

    ler = lambda nome: json.loads((PASTA / nome).read_text(encoding="utf-8"))  # noqa: E731
    impasse_ = ler("impasse.json")
    formula_ = ler("formula.json")
    repeticao_ = ler("repeticao.json")
    prog = ler("progressao.json")
    md: list[str] = [
        "# Ranked offline — Fase 6.1: progressão competitiva, elite e correções",
        "",
        "Gerado por `python tools/ranked_progressao.py relatorio`, a partir dos JSONs "
        "desta pasta. Todo confronto é uma partida real do motor PvP com seed; as "
        "carreiras se refazem sem o motor (`progressao`) com qualquer ciclo de "
        "leaderboard. O contrato está em `GAMEPLAY_CONTRACTS.md`.",
        "",
        "## 1. Empate técnico por impasse",
        "",
    ]
    fase6 = impasse_["partidas_gravadas_da_fase6"]
    p50, p90, p99, maximo = fase6["rodadas_p50_p90_p99_max"]
    traj = impasse_["trajetorias"]
    md += [
        f"Nos {fase6['com_vencedor']} confrontos com vencedor da Fase 6 (amostra, calibração e "
        f"holdout), a duração foi de {p50} rodadas na mediana, {p90} no p90, {p99} no p99 e "
        f"{maximo} no máximo; {fase6['sem_vencedor_em_500']} bateram o limite de 500.",
        "",
        f"Refiz {traj['total']} duelos rodada a rodada, guardando HP e MP dos dois lados "
        f"(`trajetorias.jsonl`): os {traj['por_grupo']['impasse_fase6']} que bateram o limite "
        f"na Fase 6 (amostra, calibração e as carreiras), os {traj['por_grupo']['longo']} que "
        f"terminaram em KO depois de {LONGOS} rodadas e {traj['por_grupo']['comum']} comuns, "
        "até 1.500 rodadas. Todos os refeitos com vencedor repetiram o vencedor e o número "
        "de rodadas gravados.",
        "",
        f'- Dos {traj["por_grupo"]["impasse_fase6"]} "sem resultado" da Fase 6, '
        f"{traj['impasses_da_fase6_que_terminaram_ate_1500']} terminaram em KO depois da rodada "
        f"500; {len(traj['sem_fim_em_1500'])} (todos R31 × M33) não terminaram em 1.500.",
        "- A maior espera por um mínimo novo de HP ou MP (folga de 1%), por partida que "
        "terminou em KO:",
        "",
        "| dupla | rodadas até o KO | maior espera |",
        "|---|---|---|",
    ]
    for e in impasse_["maiores_esperas_em_partidas_terminadas"]:
        md.append(f"| {e['dupla']} | {e['rodadas']} | {e['espera']} |")
    md += [
        "",
        "Há um vão limpo: as partidas que andam até o fim (desgaste contínuo) esperam no "
        "máximo 50 rodadas por um mínimo novo; as duplas de sustain em equilíbrio, de 134 "
        "a 826. A janela escolhida é o triplo de 50:",
        "",
        "| janela | KOs que virariam empate | rodada em que as duplas sem fim empatam |",
        "|---|---|---|",
    ]
    for janela, v in impasse_["janelas"].items():
        md.append(
            f"| {janela}{' (escolhida)' if int(janela) == imp.JANELA else ''} | "
            f"{len(v['ko_que_viram_empate'])} | "
            f"{', '.join(str(x) for x in v['sem_fim_encerradas_em'])} |"
        )
    md += [
        "",
        f"**Regra:** empate técnico depois de {imp.JANELA} rodadas sem nenhum mínimo novo "
        f"(folga de {_n(100 * imp.MARGEM)}% do máximo), ou no teto de {imp.TETO} rodadas. "
        "Os KOs que viram empate com a janela de 150 são todos de duplas que passaram pelo "
        "menos 150 rodadas sem que ninguém fosse desgastado — R31, M27, M32, M33 e M20 × "
        "W77 —, e nenhuma partida que terminou com desgaste contínuo é encerrada.",
        "",
        "## 2. A fórmula de PR",
        "",
        "Antes de jogar qualquer partida nova, a fórmula foi reaplicada às 4 carreiras reais "
        "da Fase 6 (resultado, chance do Glicko-2 e percentil de cada partida gravados): "
        "`formula.json`. Oscilação = promoção desfeita em até 3 partidas (ou rebaixamento "
        "desfeito); distância = |alvo − coordenada visível| média, em PR.",
        "",
        "| variante | M03 osc. / trocas de rank / dist. | M11 | W26 | R31 ganho / perda |",
        "|---|---|---|---|---|",
    ]
    for v in formula_:
        c = v["carreiras"]

        def celula(nome, c=c):
            r = c[nome]
            return f"{r['oscilacoes']} / {r['trocas_de_rank']} / {_n(r['distancia_media'])}"

        md.append(
            f"| {v['variante']['nome']} | {celula('M03')} | {celula('M11')} | {celula('W26')} | "
            f"{_n(c['R31']['ganho'], 1)} / {_n(c['R31']['perda'], 1)} |"
        )
    w26 = formula_[0]["carreiras"]["W26"]
    md += [
        "",
        f"Na W26, o rank por percentil da Fase 6 trocava {w26['trocas_de_rank_por_percentil']} "
        f"vezes; o rank visível com a proposta, {w26['trocas_de_rank']}. Escolhidos: K = "
        f"{_n(pg.K)}, β = {_n(pg.BETA, 2)}, multiplicador até {_n(pg.MULTIPLICADOR_MAXIMO)}, "
        f"escudo de {pg.ESCUDO} partidas, rebaixamento pousando em no máximo "
        f"{pg.PR_APOS_REBAIXAMENTO} PR. Ganho ~18 e perda ~18 por partida equilibrada no "
        "lugar certo; o R31, de elite e posicionado no teto (Obsidian I), ganha ~38 e perde "
        "~4 até virar candidato.",
        "",
        "## 3. Repetição de adversário",
        "",
        "Por modelo (`repeticao.json`): o resultado sai da chance do Glicko-2 entre as "
        "forças VERDADEIRAS (as da calibração) e o MMR do jogador artificial começa do "
        "centro. 300 partidas por jogador com os 186; 100 com uma população sintética de "
        "5.000 (ratings sorteados da calibrada, com ruído). Repetição = adversário que já "
        "apareceu nas 10 partidas anteriores; desequilíbrio = |chance − ½| médio.",
        "",
        "| população | faixa | Fase 6: repetição / distintos / deseq. | 6.1 |",
        "|---|---|---|---|",
    ]
    for populacao_, faixas in repeticao_.items():
        for faixa, d in faixas.items():
            a, b = d["fase6"], d["nova"]
            md.append(
                f"| {populacao_} | {faixa} | {_n(100 * a['repeticao'])}% / {a['distintos']} / "
                f"{_n(a['desequilibrio_medio'], 3)} | {_n(100 * b['repeticao'])}% / "
                f"{b['distintos']} / {_n(b['desequilibrio_medio'], 3)} |"
            )
    ms = [d["nova"]["ms_por_escolha"] for d in repeticao_["5000"].values()]
    md += [
        "",
        f"Custo por escolha com 5.000 NPCs: {_n(min(ms), 1)}–{_n(max(ms), 1)} ms. Parâmetros: "
        f"peso {_n(mm.PESO_DA_REPETICAO)}, meia-vida {_n(mm.MEIA_VIDA)} partidas, memória "
        f"{mm.MEMORIA}. **Para 5.000:** a mesma regra serve sem mudança; o que muda é a "
        "densidade — a janela da etapa passa a ter dezenas de candidatos, e o custo de "
        "repetição quase nunca decide. A memória de 20 partidas por gladiador já está no "
        "histórico guardado (50).",
        "",
        "## 4. Os jogadores artificiais",
        "",
        f"Cinco carreiras reais (`carreiras/`), uma por faixa da Ladder calibrada, com o "
        f"caminho do jogo: matchmaking 6.1, árbitro de impasse, mundo NPC × NPC "
        f"(2 confrontos por partida do jogador, mais a fila do retorno) e a leaderboard. "
        f"Relógio injetado: {SESSAO} partidas por dia (hipótese de "
        f"{_n(MINUTOS_POR_PARTIDA)} min por partida, {_n(SESSAO * MINUTOS_POR_PARTIDA / 60)} h "
        f"de jogo), a partir das {HORA_DA_SESSAO}h UTC, e o jogo fechado até o dia "
        "seguinte. A mesma carreira foi refeita sem o motor com o ciclo de 1 h e com o de "
        "24 h: o MMR é idêntico nas duas (divergência zero em todas), e muda só o que a "
        "leaderboard decide.",
        "",
    ]
    um = prog["periodos"]["1h"]
    md += [
        "| faixa (gêmeo) | partidas (h) | V-E-D | posicionado em | 2h | 5h | 10h | final "
        "| MMR final (percentil) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for faixa, m in um.items():
        pos = m["posicionamento"] or {}
        marcos = [m["marcos"].get(f"{h}h") for h in (2, 5, 10)]
        md.append(
            f"| {faixa} ({m['gemeo']}) | {m['partidas']} ({_n(m['horas'], 1)}) | "
            f"{m['vitorias']}-{m['empates']}-{m['derrotas']} | "
            f"{pos.get('exibicao', '—')} (p {_n(pos.get('percentil'), 1)}) | "
            + " | ".join(x["exibicao"] if x else "—" for x in marcos)
            + f" | {m['final']['exibicao']} | {_n(m['final']['mmr'])} "
            f"({_n(m['final']['percentil'], 1)}) |"
        )
    md += [
        "",
        "| faixa | PR médio vitória / derrota / empate | promoções / rebaixamentos | "
        "escudo segurou | oscilações | partidas por promoção | distância média (p90) ao alvo "
        "| rank visível = rank do percentil |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for faixa, m in um.items():
        pr = m["pr_medio"]
        igual = m["rank_visivel_igual_ao_do_percentil"]
        md.append(
            f"| {faixa} | {_n(pr['vitoria'], 1)} / {_n(pr['derrota'], 1)} / "
            f"{_n(pr['empate'], 1)} | {m['promocoes']} / {m['rebaixamentos']} | "
            f"{m['escudo_segurou']} | {m['oscilacoes']} | {_n(m['partidas_por_promocao'], 1)} | "
            f"{_n(m['distancia_media_ao_alvo'])} ({_n(m['distancia_p90_ao_alvo'])}) | "
            f"{_n(None if igual is None else 100 * igual)}% |"
        )
    md += [
        "",
        "**Matchmaking real:**",
        "",
        "| faixa | oponentes distintos | repetidos nas últimas 10 | chance média | desequilíbrio |",
        "|---|---|---|---|---|",
    ]
    for faixa, m in um.items():
        mm_ = m["matchmaking"]
        md.append(
            f"| {faixa} | {mm_['oponentes_distintos']} | {mm_['repetidos_nas_ultimas_10']} "
            f"({_n(100 * mm_['taxa_de_repeticao'], 1)}%) | {_n(mm_['chance_media'], 3)} | "
            f"{_n(mm_['desequilibrio_medio'], 3)} |"
        )
    md += [
        "",
        "## 5. Candidatura, elite e a leaderboard: 1 h × 24 h",
        "",
        "| ciclo | faixa | 1ª vez candidato | partidas como candidato (h de jogo) | "
        "avaliações na atualização | entrou na elite | final |",
        "|---|---|---|---|---|---|---|",
    ]
    for rotulo, faixas in prog["periodos"].items():
        for faixa, m in faixas.items():
            cand = m["candidato"]
            horas = _n(cand["horas_de_jogo_como_candidato"], 1)
            avaliacoes = ", ".join(
                f"{a['evento'].replace('_', ' ')} (n {a['n']})" for a in m["elite"]["avaliacoes"]
            )
            md.append(
                f"| {rotulo} | {faixa} | {cand['primeira_vez_na_partida'] or '—'} | "
                f"{cand['partidas_como_candidato']} ({horas}) "
                f"| {avaliacoes or '—'} | {m['elite']['entrada_na_partida'] or '—'} | "
                f"{m['final']['exibicao']} |"
            )
    md += [
        "",
        "**A leaderboard inteira** (cada carreira tem o próprio mundo; números somados das 5):",
        "",
        "| ciclo | atualizações | Top 5 mudou em | nomes trocados no Top 5 | promoções à elite | "
        "rebaixamentos da elite | avisos de risco | tamanho da elite |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for rotulo, faixas in prog["periodos"].items():
        soma = lambda chave, sub: sum(m[sub][chave] for m in faixas.values())  # noqa: E731
        tamanhos = [
            t
            for m in faixas.values()
            for t in m["elite_por_atualizacao"]["tamanho_da_elite"]
            if t is not None
        ]
        md.append(
            f"| {rotulo} | {soma('atualizacoes', 'top5')} | {soma('mudaram', 'top5')} | "
            f"{soma('nomes_trocados', 'top5')} | "
            f"{soma('promocoes', 'elite_por_atualizacao')} | "
            f"{soma('rebaixamentos', 'elite_por_atualizacao')} | "
            f"{soma('em_risco', 'elite_por_atualizacao')} | "
            f"{min(tamanhos, default='—')}–{max(tamanhos, default='—')} |"
        )
    md += [
        "",
        f"Regras: promoção com percentil ≥ {_n(lbm.MINIMO_DA_ELITE)} e RD ≤ "
        f"{_n(lbm.RD_MAXIMO_PARA_PROMOVER)}; risco a menos de {_n(lbm.FAIXA_DE_RISCO)} pontos "
        "abaixo; rebaixamento no segundo retrato abaixo ou de uma vez além da faixa.",
        "",
        "## 6. Empates e custo",
        "",
        "| faixa | partidas do mundo | empates do mundo (rodada) | empates do jogador | "
        "CPU do jogador | CPU do mundo |",
        "|---|---|---|---|---|---|",
    ]
    for faixa, w in prog["mundo"].items():
        m = um[faixa]
        md.append(
            f"| {faixa} | {w['partidas']} | {w['empates']} "
            f"({', '.join(str(r) for r in w['rodadas_dos_empates']) or '—'}) | "
            f"{m['empates']} | {_n(w['cpu_s_do_jogador'] / 60, 1)} min | "
            f"{_n(w['cpu_s_do_mundo'] / 60, 1)} min |"
        )
    md += ["", "## 7. Problemas encontrados e correções", ""]
    md += [f"- {p}" for p in PROBLEMAS]
    texto = "\n".join(md) + "\n"
    (PASTA / "relatorio.md").write_text(texto, encoding="utf-8")
    return texto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("trajetorias")
    p.add_argument("--trabalhadores", type=int, default=4)
    sub.add_parser("impasse")
    sub.add_parser("formula")
    sub.add_parser("repeticao")
    p = sub.add_parser("progressao")
    p.add_argument("--nome", default="carreira")
    sub.add_parser("relatorio")
    p = sub.add_parser("carreiras")
    p.add_argument("--partidas", type=int, required=True)
    p.add_argument("--nome", default="carreira")
    p.add_argument("--faixas", nargs="*")
    args = parser.parse_args()
    if args.comando == "trajetorias":
        r = trajetorias(args.trabalhadores)
        print(f"{len(r)} trajetórias")
    elif args.comando == "impasse":
        print(json.dumps(impasse(), ensure_ascii=False, indent=1)[:3000])
    elif args.comando == "formula":
        for v in formula():
            print(v["variante"])
            for nome, r in v["carreiras"].items():
                print("  ", nome, r)
    elif args.comando == "repeticao":
        print(json.dumps(repeticao(), ensure_ascii=False, indent=1))
    elif args.comando == "progressao":
        r = progressao(args.nome)
        for rotulo, faixas in r["periodos"].items():
            for faixa, m in faixas.items():
                print(rotulo, faixa, m["partidas"], m["final"], m["elite"], m["top5"])
    elif args.comando == "relatorio":
        print(relatorio())
    elif args.comando == "carreiras":
        for faixa, arquivo in carreiras(args.partidas, args.nome, args.faixas).items():
            print(faixa, arquivo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
