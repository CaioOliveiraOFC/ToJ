"""Copa Arena 03 v2 — Inteligência Estratégica: os mesmos 64, outra cabeça.

Uso:
    python tools/arena_copa_03_ia.py              # tudo, e os relatórios
    python tools/arena_copa_03_ia.py sem-pdf      # idem, sem o PDF

A Copa 03 de novo, com EXATAMENTE os 64 gladiadores publicados em
`reports/pvp/copa_03/` — mesmos IDs, nomes, builds e OP, conferidos pelo
`sha256` de cada snapshot —, o mesmo sorteio da chave e as mesmas seeds
oficiais por posição. Muda uma coisa: os dois lados de cada partida são
conduzidos pela IA estratégica (`tools/arena_ia_estrategica.py`) em vez da
`PoliticaCopa`. Nenhuma run PvE, nenhuma extração, nenhuma regra do motor.

Antes da Copa nova:

1. a Copa original é reproduzida com a `PoliticaCopa` e conferida, partida a
   partida, contra os resultados publicados e contra `final_trace.json`. É
   desses traces reproduzidos que saem as métricas que a Copa original não
   publicou (sequências de básicos e o motivo de cada uma);
2. confrontos controlados IA × `PoliticaCopa`: cada gladiador contra si mesmo
   (espelho) e os 32 pares da primeira fase com o controlador trocado, lados
   e seeds alternados. A seed de cada um é derivada (`semente_derivada`) e
   não toca as seeds oficiais.

Saída em `reports/pvp/copa_03_ia/`. A Copa 03 original fica como está.
"""

from __future__ import annotations

import json
import multiprocessing
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.gladiator import prepare_gladiator  # noqa: E402
from src.mechanics.pvp_duel import SIDES  # noqa: E402
from tools.arena_auditoria import disputar as duelo_auditavel  # noqa: E402
from tools.arena_copa_02 import FASES  # noqa: E402
from tools.arena_copa_03 import (  # noqa: E402
    COPA,
    PASTA,
    SEMENTE_PRINCIPAL,
    formar_participantes,
    semente_derivada,
    todas,
)
from tools.arena_copa_teste import (  # noqa: E402
    LIMITE_TECNICO,
    Copa,
    PoliticaCopa,
    jogar_partida,
    sortear_chave,
    trace_json,
)
from tools.arena_ia_estrategica import IAEstrategica  # noqa: E402
from tools.arena_metricas_combate import RegistroDeEscolhas, metricas_do_lado  # noqa: E402

COPA_IA = "Copa Arena 03 v2 — Inteligência Estratégica"
PASTA_ORIGINAL = PASTA
PASTA_IA = PASTA.parent / "copa_03_ia"
CONTROLADORES = {"ia": IAEstrategica, "politica_copa": PoliticaCopa}
PROCESSOS = 4
# Confrontos controlados: seeds por combinação de lado.
SEEDS_POR_LADO = 2


# --- o trabalho de cada processo -------------------------------------------------

_POR_ID: dict = {}


def _participantes() -> dict:
    """Os 64, reconstruídos uma vez por processo, dos snapshots publicados."""
    if not _POR_ID:
        _POR_ID.update({p.id: p for p in formar_participantes(PASTA_ORIGINAL)})
    return _POR_ID


def _destacar(partida) -> None:
    """Tira do duelo auditado os embrulhos locais, para a partida atravessar processos.

    `disputar` troca `_event` e `_clamp_free_mp` da instância por funções locais
    durante o duelo; depois que ele termina, elas não servem a nada e não são
    serializáveis. Sem elas, a instância volta aos métodos da classe.
    """
    for nome in ("_event", "_clamp_free_mp"):
        partida.auditado.duelo.__dict__.pop(nome, None)


def _jogar(tarefa: tuple) -> tuple:
    """Uma partida oficial: (fase, índice, id p1, id p2, nome da fase, controlador)."""
    fase, indice, id1, id2, nome_da_fase, controlador = tarefa
    por_id = _participantes()
    instancias: list = []

    def fabrica(heroi):
        instancias.append(CONTROLADORES[controlador](heroi))
        return instancias[-1]

    partida = jogar_partida(
        fase,
        indice,
        por_id[id1],
        por_id[id2],
        semente_principal=SEMENTE_PRINCIPAL,
        nome_da_fase=nome_da_fase,
        controlador=fabrica,
    )
    _destacar(partida)
    # `jogar_partida` joga o duelo puro e depois o auditado; cada um cria p1 e p2.
    auditados = dict(zip(SIDES, instancias[2:4], strict=True))
    decisoes = {lado: getattr(c, "decisoes", []) for lado, c in auditados.items()}
    return partida, decisoes


def _executor(processos: int):
    # `spawn`: cada processo importa o jogo do zero. `fork` herdaria o estado do
    # gerador global e o que mais o processo principal tivesse mexido.
    return ProcessPoolExecutor(processos, mp_context=multiprocessing.get_context("spawn"))


def tarefas_da_fase(fase: str, quantas: int, nome: str, vivos: list, controlador: str) -> list:
    """As partidas de uma fase: os vivos em pares, na ordem da chave."""
    return [
        (fase, i + 1, vivos[2 * i].id, vivos[2 * i + 1].id, nome, controlador)
        for i in range(quantas)
    ]


def disputar_copa(participantes: list, controlador: str, processos: int = PROCESSOS) -> tuple:
    """A chave da Copa 03 — mesmo sorteio, mesmas seeds — com `controlador`.

    É `tools/arena_copa_03.disputar_copa` com o controlador como parâmetro e as
    partidas de cada fase em paralelo: elas não dependem umas das outras, só da
    fase anterior. Devolve a Copa e as decisões registradas pela IA (vazias para
    a `PoliticaCopa`), por partida e lado.
    """
    por_id = {p.id: p for p in participantes}
    chave = sortear_chave([p.id for p in participantes], semente_derivada("chave"))
    vivos = [por_id[i] for i in chave]
    copa = Copa(participantes, chave, {})
    decisoes: dict = {}
    with _executor(processos) as executor:
        for fase, quantas, nome in FASES:
            tarefas = tarefas_da_fase(fase, quantas, nome, vivos, controlador)
            partidas = []
            for partida, registro in executor.map(_jogar, tarefas):
                # Os participantes do processo principal, não as cópias do filho.
                partida.lados = {lado: por_id[partida.lados[lado].id] for lado in SIDES}
                partidas.append(partida)
                decisoes[f"{fase}-{partida.indice}"] = registro
            copa.fases[fase] = partidas
            if any(p.inconclusiva for p in partidas):
                copa.interrompida = (
                    f"{nome}: confronto inconclusivo no limite técnico; a chave parou."
                )
                return copa, decisoes
            vivos = [p.vencedor for p in partidas]
    return copa, decisoes


# --- a Copa original, reproduzida -------------------------------------------------


def dados_publicados(pasta: Path = PASTA_ORIGINAL) -> dict:
    """O modelo de dados que o `dashboard.html` da Copa 03 publicou."""
    texto = (pasta / "dashboard.html").read_text(encoding="utf-8")
    achado = re.search(r'<script id="dados" type="application/json">(.*?)</script>', texto, re.S)
    if achado is None:
        raise RuntimeError("dashboard.html da Copa 03 sem o bloco de dados")
    return json.loads(achado.group(1))


def conferir_reproducao(copa: Copa, publicados: dict, pasta: Path = PASTA_ORIGINAL) -> list:
    """A Copa reproduzida contra a publicada: partida a partida e o trace da final."""
    from tools.arena_copa_02_relatorios import _jogo

    jogos = {j["chave"]: j for j in publicados["partidas"]}
    campos = ("seed", "p1", "p2", "vencedor", "perdedor", "rodadas", "hp_vencedor", "golpes")
    verificacoes = [("63 partidas", len(todas(copa)) == len(jogos) == 63)]
    divergentes = []
    for partida in todas(copa):
        novo = _jogo(partida)
        velho = jogos.get(novo["chave"])
        if velho is None or any(novo[c] != velho[c] for c in campos):
            divergentes.append(novo["chave"])
    verificacoes.append(
        ("semente, lados, vencedor, rodadas, HP e golpes de cada partida", not divergentes)
    )
    verificacoes.append(("campeão", copa.campeao.id == publicados["campeao"]))
    verificacoes.append(("chave sorteada", list(copa.chave) == publicados["chave"]))
    publicado = json.loads((pasta / "final_trace.json").read_text(encoding="utf-8"))
    final = copa.fases["final"][0]
    refeito = json.loads(
        json.dumps(trace_json(final, copa=COPA, semente_principal=SEMENTE_PRINCIPAL))
    )
    verificacoes.append(("final_trace.json registro a registro", refeito == publicado))
    verificacoes.append(
        (
            "fidelidade e coerência de todas as partidas",
            all(ok for p in todas(copa) for _, ok in p.fidelidade + p.coerencia),
        )
    )
    return verificacoes


# --- confrontos controlados ---------------------------------------------------------


def _duelo_controlado(tarefa: tuple) -> dict:
    """Um duelo sem auditoria: (rótulo, id A, id B, quem é IA, lado de A, seed).

    `quem é IA` é "A" ou "B". No espelho A e B são o mesmo gladiador, em duas
    instâncias preparadas: o lado B leva um apóstrofo no nome só para os dois
    nomes não colidirem na tela.
    """
    rotulo, id_a, id_b, quem_ia, lado_a, seed = tarefa
    por_id = _participantes()
    ga, gb = prepare_gladiator(por_id[id_a].heroi), prepare_gladiator(por_id[id_b].heroi)
    if id_a == id_b:
        gb.hero.nick_name = gb.hero.nick_name + "'"
    lado_b = "p2" if lado_a == "p1" else "p1"
    g = {lado_a: ga, lado_b: gb}
    lado_ia = lado_a if quem_ia == "A" else lado_b
    herois = {id(g[lado].hero): lado for lado in SIDES}
    registros: list = []
    envoltos: dict = {}

    def fabrica(heroi):
        lado = herois[id(heroi)]
        interno = IAEstrategica(heroi) if lado == lado_ia else PoliticaCopa(heroi)
        envoltos[lado] = RegistroDeEscolhas(interno, lado, registros, heroi)
        return envoltos[lado]

    duelo = duelo_auditavel(g["p1"], g["p2"], seed, fabrica, auditar=False, limite=LIMITE_TECNICO)
    resultado = duelo.duelo.result
    historico = duelo.duelo.history
    ids = {lado_a: id_a, lado_b: id_b}
    metricas = {
        lado: metricas_do_lado(registros, historico, lado, por_id[ids[lado]].heroi)
        for lado in SIDES
    }
    ia = envoltos[lado_ia].interno
    return {
        "tipo": rotulo,
        "a": id_a,
        "b": id_b,
        "ia": quem_ia,
        "lado_a": lado_a,
        "lado_ia": lado_ia,
        "seed": seed,
        "ids": ids,
        "vencedor": None if resultado is None else resultado.winner,
        "ia_venceu": None if resultado is None else resultado.winner == lado_ia,
        "rodadas": None if resultado is None else resultado.rounds,
        "metricas": metricas,
        "previsoes": [
            [d["rodada"], next((a["p"] for a in d["avaliacoes"] if a["acao"] == d["acao"]), None)]
            for d in ia.decisoes
        ],
        "concorda_com_politica": sum(1 for d in ia.decisoes if d["acao"] == d["politica_copa"]),
        "decisoes": len(ia.decisoes),
    }


def tarefas_controladas(participantes: list) -> list[tuple]:
    """Espelhos (os 64) e cruzados (os 32 pares da primeira fase), lados e seeds alternados."""
    ids = [p.id for p in participantes]
    chave = sortear_chave(ids, semente_derivada("chave"))
    tarefas = []
    for gid in ids:
        for lado in SIDES:
            for k in range(SEEDS_POR_LADO):
                seed = semente_derivada(f"ia:espelho:{gid}:{lado}:{k}")
                tarefas.append(("espelho", gid, gid, "A", lado, seed))
    for i in range(0, len(chave), 2):
        a, b = chave[i], chave[i + 1]
        for quem in ("A", "B"):
            for lado in SIDES:
                for k in range(SEEDS_POR_LADO):
                    seed = semente_derivada(f"ia:cruzado:{a}:{b}:{quem}:{lado}:{k}")
                    tarefas.append(("cruzado", a, b, quem, lado, seed))
    return tarefas


def confrontos_controlados(participantes: list, processos: int = PROCESSOS) -> list[dict]:
    tarefas = tarefas_controladas(participantes)
    with _executor(processos) as executor:
        return list(executor.map(_duelo_controlado, tarefas, chunksize=4))


# --- o orçamento -----------------------------------------------------------------------

# Variantes medidas contra a configuração da Copa, em espelho IA × IA: o dobro de
# continuações e um horizonte menor. Se o dobro não rende, o orçamento basta.
VARIANTES = {
    "o dobro de continuações (20 por ação, 40 nos momentos críticos)": {
        "rollouts": 20,
        "rollouts_criticos": 40,
    },
    "horizonte de 2 rodadas": {"horizonte": 2},
}


def _duelo_de_variantes(tarefa: tuple) -> tuple:
    """Espelho IA × IA: o lado A com a variante, o B com a configuração da Copa."""
    from tools.arena_ia_estrategica import Configuracao

    nome, gid, lado_a, seed = tarefa
    por_id = _participantes()
    ga, gb = prepare_gladiator(por_id[gid].heroi), prepare_gladiator(por_id[gid].heroi)
    gb.hero.nick_name = gb.hero.nick_name + "'"
    lado_b = "p2" if lado_a == "p1" else "p1"
    g = {lado_a: ga, lado_b: gb}
    configuracao = {lado_a: Configuracao(**VARIANTES[nome]), lado_b: Configuracao()}
    herois = {id(g[lado].hero): lado for lado in SIDES}

    def fabrica(heroi):
        return IAEstrategica(heroi, configuracao[herois[id(heroi)]])

    duelo = duelo_auditavel(g["p1"], g["p2"], seed, fabrica, auditar=False, limite=LIMITE_TECNICO)
    resultado = duelo.duelo.result
    return nome, None if resultado is None else resultado.winner == lado_a


def orcamento(participantes: list, processos: int = PROCESSOS) -> dict:
    """Cada variante contra a da Copa: os 64 em espelho, lados e duas seeds alternados."""
    tarefas = [
        (nome, p.id, lado, semente_derivada(f"ia:orcamento:{nome}:{p.id}:{lado}:{k}"))
        for nome in VARIANTES
        for p in participantes
        for lado in SIDES
        for k in range(SEEDS_POR_LADO)
    ]
    with _executor(processos) as executor:
        resultados = list(executor.map(_duelo_de_variantes, tarefas, chunksize=2))
    saida = {}
    for nome in VARIANTES:
        lista = [r for n, r in resultados if n == nome]
        saida[nome] = {
            "n": sum(1 for r in lista if r is not None),
            "vitorias_da_variante": sum(1 for r in lista if r),
            "inconclusivos": sum(1 for r in lista if r is None),
        }
    return saida


# --- o programa ----------------------------------------------------------------------


def main(argv: list[str]) -> int:
    from tools.arena_copa_03_ia_relatorios import escrever_tudo

    PASTA_IA.mkdir(parents=True, exist_ok=True)
    participantes = formar_participantes(PASTA_ORIGINAL)
    original, _ = disputar_copa(participantes, "politica_copa")
    verificacoes = conferir_reproducao(original, dados_publicados())
    for nome, ok in verificacoes:
        print(f"reprodução da Copa 03 — {nome}: {'ok' if ok else 'FALHOU'}")
    if not all(ok for _, ok in verificacoes):
        return 1
    controlados = confrontos_controlados(participantes)
    print(f"confrontos controlados: {len(controlados)}")
    nova, decisoes = disputar_copa(participantes, "ia")
    campeao = nova.campeao
    print(f"Campeão da v2: {campeao.nome} ({campeao.id})" if campeao else nova.interrompida)
    variantes = orcamento(participantes)
    caminhos = escrever_tudo(
        nova,
        decisoes,
        original,
        verificacoes,
        controlados,
        variantes,
        pdf="sem-pdf" not in argv,
    )
    for caminho in caminhos:
        print(f"escrito: {caminho.relative_to(RAIZ)}")
    falhas = [p for p in todas(nova) if not all(ok for _, ok in p.fidelidade + p.coerencia)]
    return 1 if falhas or nova.interrompida else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
