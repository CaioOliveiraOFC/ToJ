"""O ARENA BENCHMARK V1: um personagem que existiu, congelado.

Ele não foi montado. É o snapshot de uma run real do `BotPadrao`, capturado na
entrada do andar 20 e escolhido por estar mais próximo da mediana de
`overall_power` de 54 sobreviventes em 900 runs. A mediana escolheu QUAL
snapshot representa a população; ela nunca montou um. Um "personagem médio" com
o elmo de um e a arma de outro não atravessou 19 andares.

O que estes testes fixam:

1. o congelamento é FIEL — o que foi salvo é o que volta, peça por peça;
2. o alvo não se move — `overall_power` dele continua onde foi medido;
3. quem carrega usa o caminho CANÔNICO do save, não uma reconstrução paralela;
4. `NAO_CONFIAVEL` existe e não se disfarça de veredito.
"""

from __future__ import annotations

import json

import pytest

from src.sim.arena import (
    ABAIXO,
    EQUIVALENTE,
    NAO_CONFIAVEL,
    SUPEROU,
    assinatura_de_build,
    limpar_cache,
)
from src.sim.harness import make_hero
from tools.arena_alvo import (
    ARQUIVO,
    PODER_ESPERADO,
    benchmark,
    comparar_com_benchmark,
    poder_do_benchmark,
    procedencia,
)

POUCOS_DUELOS = 6


@pytest.fixture(autouse=True)
def _cache_limpo():
    limpar_cache()
    yield
    limpar_cache()


# --- 1. O congelamento é fiel ---------------------------------------------


def test_o_snapshot_veio_de_uma_run_real():
    """Procedência declarada no próprio arquivo, não em comentário."""
    origem = procedencia()
    assert origem["classe"] == "Rogue"
    assert origem["seed"] == 20261007
    assert origem["andar_de_captura"] == 20
    assert "run real" in origem["origem"]


def test_o_benchmark_volta_inteiro_do_arquivo():
    """Equipamento, `+N`, sockets, gemas, encantamentos, deck, passivas, bolso."""
    h = benchmark()
    assert h.get_classname() == "Rogue"
    assert h.get_level() == 22
    assert len(h.skills) == 4
    assert len(h.passives) == 21
    assert sum(1 for i in h.equipment.values() if i) == 10
    assert any(getattr(i, "enhancement_level", 0) > 0 for i in h.equipment.values() if i)
    assert any(g for i in h.equipment.values() if i for g in getattr(i, "gems", []))
    assert [i for i in h.inventory if getattr(i, "consumable", False)]


def test_o_arquivo_guarda_o_estado_por_peca_e_nao_so_o_nome():
    """`+N`, socket e gema precisam sobreviver ao disco.

    O formato "só o nome" perdia as três em silêncio: duas Espadas de Ferro +3 e
    +17 têm a mesma chave de catálogo.
    """
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    pecas = [p for p in dados["equipment"].values() if p]
    assert any(p.get("enhancement_level", 0) > 0 for p in pecas)
    assert any(p.get("socket_count", 0) > 0 for p in pecas)
    assert any(p.get("gems") for p in pecas)


def test_carregar_duas_vezes_da_o_mesmo_personagem():
    assert assinatura_de_build(benchmark()) == assinatura_de_build(benchmark())


def test_o_benchmark_e_um_exemplar_proprio_e_nao_a_definicao_do_catalogo():
    """Aprimorar a arma do benchmark não pode aprimorar a do catálogo."""
    from src.content.items import get_all_items

    arma = benchmark().equipment.get("Weapon1")
    assert arma is not None
    catalogo = get_all_items().get(arma.name)
    assert catalogo is not None
    assert arma is not catalogo


# --- 2. O alvo não se move -------------------------------------------------


@pytest.mark.balance
def test_o_poder_do_benchmark_continua_onde_foi_medido():
    """Um alvo que se desloca em silêncio recalibra a extração sem avisar.

    Se este teste falhar, alguma coisa mudou — régua, conteúdo ou balanceamento
    — e a decisão é REMEDIR e congelar de novo, de propósito, nunca ajustar o
    número para o teste passar.
    """
    medido = poder_do_benchmark()
    assert abs(medido - PODER_ESPERADO) < 0.05, f"{medido:.2f} != {PODER_ESPERADO}"


@pytest.mark.balance
def test_o_benchmark_comparado_consigo_mesmo_da_equivalente():
    resultado = comparar_com_benchmark(benchmark())
    assert resultado.relativo == pytest.approx(1.0)
    assert resultado.veredito == EQUIVALENTE
    assert resultado.confiavel


# --- 3. O caminho canônico -------------------------------------------------


def test_quem_carrega_usa_a_reidratacao_do_save_do_jogo():
    """Reconstruir campo a campo perderia o próximo campo que o save aprender.

    Foi o que aconteceu com `+N`, socket e encantamento quando o formato era só
    o nome. Uma segunda reidratação em paralelo repete o erro na próxima vez.
    """
    import ast
    from pathlib import Path

    arvore = ast.parse(Path("tools/arena_alvo.py").read_text(encoding="utf-8"))
    importados = {
        f"{no.module}.{alias.name}"
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module
        for alias in no.names
    }
    assert "src.storage.save_manager.player_from_save_data" in importados


def test_o_jogo_nao_depende_do_benchmark():
    """A Arena ainda não é feature: nada em `src/` consulta o alvo."""
    from pathlib import Path

    for arquivo in Path("src").rglob("*.py"):
        assert "arena_alvo" not in arquivo.read_text(encoding="utf-8"), arquivo


# --- 4. NAO_CONFIAVEL não se disfarça --------------------------------------


def test_kit_incompativel_nao_vira_veredito():
    """O número continua saindo; o que muda é a promessa sobre ele."""
    resultado = comparar_com_benchmark(make_hero("Warrior", 12, "expected"), duelos=POUCOS_DUELOS)
    assert resultado.veredito == NAO_CONFIAVEL
    assert resultado.veredito not in (ABAIXO, EQUIVALENTE, SUPEROU)
    assert not resultado.confiavel
    assert resultado.motivo


def test_a_observacao_do_bot_carrega_o_fato_sem_pre_digerir():
    """O cérebro recebe MAGNITUDE e confiabilidade, não um veredito pronto.

    Classificar é política, e política mora no evaluator. Entregar a etiqueta
    pronta pela porta da observação repetiria o modelo de votos que a rodada da
    razão de runway derrubou.
    """
    from src.sim.bot.observation import ProgressionState

    campos = ProgressionState.__dataclass_fields__
    assert "poder_relativo" in campos
    assert "poder_confiavel" in campos
    assert campos["poder_relativo"].type == "float"
    assert campos["poder_confiavel"].type == "bool"
    # zero significa NÃO MEDIDO: a medição custa centenas de duelos e só é paga
    # quando extrair é possível.
    assert (
        ProgressionState(
            nivel=1, hp=1, hp_max=1, mp=0, mp_max=0, ouro=0, taxa_de_saida=0
        ).poder_relativo
        == 0.0
    )
