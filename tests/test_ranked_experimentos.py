"""Os experimentos da Ranked são reprodutíveis a partir do que está no repositório.

- o desenho da amostra é determinístico e tem os estratos pedidos;
- confrontos registrados (da amostra e da calibração) se repetem pela seed;
- a Ladder calibrada publicada é exatamente a reaplicação dos confrontos
  guardados, na ordem em que aconteceram;
- o estado inicial do jogo é a calibração, com o histórico aparado.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tools.ranked_experimentos as x  # noqa: E402
from src.engine import ranked_mundo  # noqa: E402
from src.engine.arena_populacao import Populacao  # noqa: E402
from src.engine.ranked_partidas import jogar  # noqa: E402
from src.ranked import sistema  # noqa: E402
from src.ranked.ladder import Ladder  # noqa: E402

PASTA = ROOT / "reports" / "ranked"


def _jsonl(nome: str) -> list[dict]:
    return [json.loads(linha) for linha in (PASTA / nome).read_text(encoding="utf-8").splitlines()]


@pytest.fixture(scope="module")
def populacao():
    return Populacao()


def test_o_desenho_da_amostra_e_deterministico_e_estratificado(populacao):
    desenho = x.desenho(populacao)
    assert desenho == x.desenho(populacao)
    estratos = collections.Counter(p["estrato"] for p in desenho)
    assert estratos["proximo"] == len(populacao) - 1
    for estrato in ("distante", "classes", "estilos", "repeticao", "holdout_proximo"):
        assert estratos[estrato] > 0
    publicados = _jsonl("amostra.jsonl")
    assert [(p["a"], p["b"], p["semente"]) for p in desenho] == [
        (r["a"], r["b"], r["semente"]) for r in publicados
    ]


@pytest.mark.parametrize("arquivo, indice", [("amostra.jsonl", 3), ("calibracao.jsonl", 41)])
def test_um_confronto_registrado_se_repete_pela_seed(populacao, arquivo, indice):
    registro = [r for r in _jsonl(arquivo) if r.get("vencedor")][indice]
    confronto = jogar(populacao, registro["a"], registro["b"], registro["semente"])
    assert (confronto.vencedor, confronto.rodadas, confronto.motivo) == (
        registro["vencedor"],
        registro["rodadas"],
        registro["motivo"],
    )


def test_a_calibracao_publicada_e_a_reaplicacao_dos_confrontos(populacao):
    estado = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    sis = sistema.criar(estado["algoritmo"], estado["parametros"])
    ladder = x.ladder_inicial(sis, populacao)
    x._aplicar(ladder, _jsonl("amostra.jsonl"), "amostra")
    feitas = {(r["a"], r["b"], r["semente"]): r for r in _jsonl("calibracao.jsonl")}
    for rodada in range(1, estado["rodadas"] + 1):
        # O pareamento suíço refeito a partir do estado: a mesma rodada sai igual.
        pares = x.partidas_da_rodada(ladder, rodada)
        x._aplicar(ladder, [feitas[(p["a"], p["b"], p["semente"])] for p in pares], "calibracao")
    assert ladder.para_dict() == estado["ladder"]


def test_o_estado_inicial_do_jogo_e_a_calibracao(populacao):
    estado = json.loads((PASTA / "calibracao.json").read_text(encoding="utf-8"))
    inicial = json.loads(ranked_mundo.INICIAL.read_text(encoding="utf-8"))
    assert inicial["versao"] == ranked_mundo.VERSAO
    assert (inicial["algoritmo"], inicial["parametros"]) == (
        estado["algoritmo"],
        estado["parametros"],
    )
    calibrada = {r["identidade"]: r for r in estado["ladder"]["registros"]}
    for r in inicial["ladder"]["registros"]:
        origem = calibrada[r["identidade"]]
        assert (r["vitorias"], r["derrotas"]) == (origem["vitorias"], origem["derrotas"])
        assert r["rating"] == pytest.approx(origem["rating"], abs=1e-5)
        assert len(r["historico"]) <= x.HISTORICO_PUBLICADO
    assert {r["identidade"] for r in inicial["ladder"]["registros"]} == {o.id for o in populacao}
    mundo = ranked_mundo.MundoRanqueado.carregar(populacao, caminho="/nao/existe/ranked.json")
    assert mundo.ladder.competitivos() == len(populacao)
    assert isinstance(Ladder.de_dict(sistema.criar(), inicial["ladder"]), Ladder)


def test_a_analise_de_carreira_com_dados_sinteticos():
    linhas = []
    for n in range(1, 61):
        linhas.append(
            {
                "n": n,
                "fase": "ranqueada" if n > 10 else "descoberta",
                "oponente": f"W{n % 7:02d}",
                "probabilidade": 0.5,
                "venceu": n % 3 != 0,
                "rating": 1500.0 + n,
                "rd": 100.0,
                "posicao": None if n < 10 else 50,
                "percentil": None if n < 10 else 70.0,
                "rank": None if n < 10 else ("Gold" if n < 30 else "Platinum"),
                "segundos": 1.0,
                "mundo": [],
            }
        )
    medidas = x.analisar_carreira(linhas)
    assert medidas["partidas"] == 60 and medidas["horas_equivalentes"] == 3.0
    assert medidas["marcos"]["2h"]["partidas"] == 40
    assert (medidas["vitorias"], medidas["derrotas"]) == (40, 20)
    assert medidas["subidas_de_rank"] == 1 and medidas["descidas_de_rank"] == 0
    assert medidas["oponentes_distintos"] == 7
    assert medidas["partidas_ate_a_faixa"] == 11
