"""Iniciativa da Arena: a fórmula aprovada, o desempate e o que fica injetado.

A estrutura é contrato: seis atributos efetivos, peso igual, raiz da razão
contra a referência do nível, modificador de nível limitado. Aqui a fórmula é
testada com tabelas injetadas, para que cada conta seja conferível à mão; as
referências canônicas da fundação estão em `test_pvp_references.py`.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mechanics.pvp_initiative import (  # noqa: E402
    InitiativeReading,
    InitiativeReference,
    MissingInitiativeReferenceError,
    ReferenceTable,
    SeededCoinTieBreak,
    build_initiative,
    level_modifier,
    order_by_initiative,
    read_initiative,
)
from src.shared import effect_core as core  # noqa: E402
from src.shared.constants import (  # noqa: E402
    PVP_INITIATIVE_LEVEL_CAP,
    PVP_INITIATIVE_LEVEL_STEP,
)
from src.sim.harness import make_hero  # noqa: E402

REF = InitiativeReference(hp=1000, mp=500, st=50, mg=50, ag=50, df=50)
TABELA = ReferenceTable({nivel: REF for nivel in range(1, 41)})


def _leitura(side, score, relative_ag=1.0) -> InitiativeReading:
    return InitiativeReading(side, 10, score, 1.0, score, relative_ag)


class _PoliticaEspia:
    """Desempate que registra se foi consultado."""

    def __init__(self, lado):
        self.lado = lado
        self.chamadas = 0

    def first(self, a, b, rng):
        self.chamadas += 1
        return self.lado


class TestFormula:
    def test_build_e_a_media_das_raizes_dos_seis_atributos_efetivos(self):
        heroi = make_hero("Warrior", 10, "naked")
        esperado = (
            math.sqrt(heroi.base_hp / REF.hp)
            + math.sqrt(heroi.base_mp / REF.mp)
            + math.sqrt(heroi.get_st() / REF.st)
            + math.sqrt(heroi.get_mg() / REF.mg)
            + math.sqrt(heroi.get_ag() / REF.ag)
            + math.sqrt(heroi.get_df() / REF.df)
        ) / 6
        assert build_initiative(heroi, REF) == pytest.approx(esperado, rel=1e-12)

    def test_hp_e_mp_atuais_nao_entram(self):
        heroi = make_hero("Mage", 10, "naked")
        cheio = build_initiative(heroi, REF)
        heroi._hp = 1
        heroi._mp = 0
        assert build_initiative(heroi, REF) == cheio

    def test_buff_e_efeito_de_atributo_entram_pelo_atributo_efetivo(self):
        heroi = make_hero("Rogue", 10, "naked")
        antes = build_initiative(heroi, REF)
        heroi.active_buffs["Sombra"] = {"stat": "ag", "value": 20, "duration": 2}
        com_buff = build_initiative(heroi, REF)
        core.apply_effect(heroi, "slowed", source_id="teste")
        assert com_buff > antes
        assert build_initiative(heroi, REF) < com_buff

    def test_score_e_build_vezes_modificador_de_nivel(self):
        alto = make_hero("Warrior", 12, "naked")
        baixo = make_hero("Warrior", 10, "naked")
        leitura = read_initiative("p1", alto, baixo, TABELA)
        assert leitura.level_modifier == pytest.approx(1 + 2 * PVP_INITIATIVE_LEVEL_STEP)
        assert leitura.score == leitura.build * leitura.level_modifier
        assert leitura.relative_ag == alto.get_ag() / REF.ag


class TestModificadorDeNivel:
    @pytest.mark.parametrize(
        ("proprio", "adversario", "esperado"),
        [
            (10, 10, 1.0),
            (12, 10, 1.01),
            (10, 12, 0.99),
            (30, 10, 1.10),
            (60, 10, 1.10),
            (10, 60, 0.90),
        ],
    )
    def test_valores_e_teto(self, proprio, adversario, esperado):
        assert level_modifier(proprio, adversario) == pytest.approx(esperado)

    def test_teto_vem_da_constante(self):
        assert level_modifier(100, 1) == pytest.approx(1 + PVP_INITIATIVE_LEVEL_CAP)
        assert level_modifier(1, 100) == pytest.approx(1 - PVP_INITIATIVE_LEVEL_CAP)


class TestOrdem:
    def test_maior_score_primeiro_sem_olhar_o_resto(self):
        politica = _PoliticaEspia("p1")
        ordem = order_by_initiative(
            _leitura("p1", 1.0, relative_ag=9.0),
            _leitura("p2", 1.1, relative_ag=0.1),
            politica,
            random.Random(0),
        )
        assert (ordem.first, ordem.second, ordem.decided_by) == ("p2", "p1", "score")
        assert politica.chamadas == 0

    def test_diferenca_minima_decide_sem_arredondar(self):
        """Arredondar a 6 casas empataria os dois e mandaria para a AG."""
        a = _leitura("p1", 1.000000000001, relative_ag=0.5)
        b = _leitura("p2", 1.000000000000, relative_ag=2.0)
        assert round(a.score, 6) == round(b.score, 6)
        ordem = order_by_initiative(a, b, _PoliticaEspia("p2"), random.Random(0))
        assert (ordem.first, ordem.decided_by) == ("p1", "score")

    def test_score_igual_desempata_pela_ag_relativa(self):
        politica = _PoliticaEspia("p1")
        ordem = order_by_initiative(
            _leitura("p1", 1.2, relative_ag=1.0),
            _leitura("p2", 1.2, relative_ag=1.0 + 1e-12),
            politica,
            random.Random(0),
        )
        assert (ordem.first, ordem.decided_by) == ("p2", "relative_ag")
        assert politica.chamadas == 0

    def test_empate_absoluto_vai_para_a_politica_injetada(self):
        politica = _PoliticaEspia("p2")
        ordem = order_by_initiative(
            _leitura("p1", 1.2), _leitura("p2", 1.2), politica, random.Random(0)
        )
        assert (ordem.first, ordem.second, ordem.decided_by) == ("p2", "p1", "fallback")
        assert politica.chamadas == 1

    def test_politica_que_inventa_lado_e_recusada(self):
        with pytest.raises(ValueError):
            order_by_initiative(
                _leitura("p1", 1.0), _leitura("p2", 1.0), _PoliticaEspia("p3"), random.Random(0)
            )

    def test_moeda_tecnica_e_reproduzivel_pela_semente(self):
        a, b = _leitura("p1", 1.0), _leitura("p2", 1.0)
        moeda = SeededCoinTieBreak()
        primeiras = [moeda.first(a, b, random.Random(s)) for s in range(20)]
        segundas = [moeda.first(a, b, random.Random(s)) for s in range(20)]
        assert primeiras == segundas
        assert set(primeiras) == {"p1", "p2"}


class TestReferenciasInjetadas:
    def test_nivel_fora_da_tabela_e_erro_e_nao_valor_inventado(self):
        tabela = ReferenceTable({10: REF})
        with pytest.raises(MissingInitiativeReferenceError):
            tabela.at_level(11)

    @pytest.mark.parametrize("ruim", [0, -1, float("nan"), float("inf")])
    def test_referencia_precisa_ser_positiva_e_finita(self, ruim):
        with pytest.raises(ValueError):
            InitiativeReference(hp=ruim, mp=1, st=1, mg=1, ag=1, df=1)

    def test_a_referencia_e_a_do_nivel_do_proprio_gladiador(self):
        """Cada lado é normalizado pela referência do PRÓPRIO nível."""
        dobro = InitiativeReference(hp=2000, mp=1000, st=100, mg=100, ag=100, df=100)
        tabela = ReferenceTable({10: REF, 12: dobro})
        heroi = make_hero("Warrior", 12, "naked")
        leitura = read_initiative("p1", heroi, make_hero("Warrior", 10, "naked"), tabela)
        assert leitura.build == build_initiative(heroi, dobro)
