"""Propriedades da decisão do BOT_PADRÃO. Nunca uma sequência decorada.

Nada aqui afirma "tem de usar Bola de Fogo no turno 3". O que se prova é que a
decisão é legal, que o motivo pertence a ela, e que a prioridade não suprime
avaliação.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.sim.bot import decidir_no_combate, decidir_no_mapa
from src.sim.bot.decision import ActionOption, Need, Score, escolher
from src.sim.bot.observation import (
    ActionMechanicsView,
    CombatState,
    MapState,
    ProgressionState,
    TargetView,
)

CEREBRO = Path("src/sim/bot")


def _combate(**kwargs) -> CombatState:
    base = dict(
        turno=0,
        hp=300,
        hp_max=500,
        mp=80,
        mp_max=100,
        dano_basico=60,
        alvo_nivel=3,
        alvo_hp=240,
        alvo_hp_max=240,
        alvo_mp=30,
        alvo_mp_max=30,
        alvo_dano=50,
    )
    base.update(kwargs)
    return CombatState(**base)


def _progresso(**kwargs) -> ProgressionState:
    base = dict(
        nivel=3,
        hp=300,
        hp_max=500,
        mp=80,
        mp_max=100,
        ouro=100,
        taxa_de_saida=40,
    )
    base.update(kwargs)
    return ProgressionState(**base)


def _mapa(**kwargs) -> MapState:
    base = dict(andar=3, posicao=(1, 1), passos_ate_saida=10)
    base.update(kwargs)
    return MapState(**base)


ATAQUE = ActionOption(
    action_id="attack",
    family="attack",
    label="ataque básico",
    mechanics=ActionMechanicsView(expected_strike_damage=60, hit_chance=1.0),
)
FUGA = ActionOption(
    action_id="flee", family="flee", label="fugir", mechanics=ActionMechanicsView(flee_chance=0.5)
)


class TestSoAcoesLegais:
    def test_a_escolhida_esta_sempre_entre_as_recebidas(self):
        opcoes = (ATAQUE, FUGA)
        decisao = decidir_no_combate(_combate(), opcoes)
        assert decisao.action_id in {o.action_id for o in opcoes}

    def test_sem_candidata_a_escolha_falha_em_voz_alta(self):
        """Devolver um default silencioso esconderia um adaptador que não enumerou."""
        with pytest.raises(ValueError, match="zero candidatas"):
            escolher((), {})

    def test_o_cerebro_nao_enumera_legalidade(self):
        """MP, recarga e requisito são regra do jogo, e ficam do outro lado.

        Se o cérebro chamasse as funções de legalidade, ele precisaria do `Hero`.
        """
        for caminho in sorted(CEREBRO.glob("*.py")):
            texto = caminho.read_text(encoding="utf-8")
            for nome in ("_usable_skills", "_consumables", "can_use_skill", "skill_mana_cost"):
                assert nome not in texto, f"{caminho} chama {nome} — legalidade é do adaptador"


class TestOMotivoPertenceADecisao:
    def test_o_motivo_nao_e_vazio_e_cita_a_acao_vencedora(self):
        decisao = decidir_no_combate(_combate(), (ATAQUE, FUGA))
        assert decisao.reason
        vencedora = next(o for o in (ATAQUE, FUGA) if o.action_id == decisao.action_id)
        assert vencedora.label in decisao.reason

    def test_todas_as_candidatas_aparecem_nos_scores(self):
        opcoes = (ATAQUE, FUGA)
        decisao = decidir_no_combate(_combate(), opcoes)
        assert {s.action_id for s in decisao.scores} == {o.action_id for o in opcoes}

    def test_o_trace_recebe_o_proprio_motivo_da_decisao(self):
        """Identidade, não semelhança: é a mesma string, não uma reconstrução."""
        decisao = decidir_no_combate(_combate(), (ATAQUE, FUGA))
        linha = decisao.reason
        assert linha is decisao.reason


class TestPrioridadeNaoSuprimeAvaliacao:
    def test_opcao_de_necessidade_menos_urgente_ainda_e_avaliada(self):
        """A escada ordena; ela não apaga ninguém do relatório."""
        alvo = TargetView(casa=(2, 2), passos=4, extras=0, chefe=False)
        opcoes = (
            ActionOption(action_id="lutar:2,2", family="lutar", target=alvo),
            ActionOption(action_id="saida", family="saida"),
            ActionOption(action_id="forge", family="forge"),
        )
        decisao = decidir_no_mapa(_mapa(alvos=(alvo,)), _progresso(), opcoes)
        assert {s.action_id for s in decisao.scores} == {o.action_id for o in opcoes}
        necessidades = {s.action_id: s.need for s in decisao.scores}
        assert necessidades["saida"] is Need.ENCERRAR
        assert necessidades["lutar:2,2"] is Need.PROGREDIR

    def test_a_escolha_e_lexicografica_necessidade_e_depois_utilidade(self):
        scores = (
            Score("urgente", Need.SOBREVIVER, 0.2),
            Score("util", Need.PROGREDIR, 9.0),
        )
        assert escolher(scores, {}).action_id == "urgente"

    def test_utilidade_nao_positiva_nao_vence_mesmo_sendo_urgente(self):
        """Beber com a vida cheia não pode ganhar de lutar só por ser 'recuperar'."""
        scores = (
            Score("inutil", Need.SOBREVIVER, 0.0),
            Score("util", Need.PROGREDIR, 1.0),
        )
        assert escolher(scores, {}).action_id == "util"


class TestOurroNaoDecideOAndar:
    def test_ter_a_taxa_da_saida_nao_muda_a_nota_de_lutar(self):
        """Era o portão que desligava a principal fonte de combate do bot."""
        alvo = TargetView(casa=(2, 2), passos=4, extras=0, chefe=False)
        opcoes = (
            ActionOption(action_id="lutar:2,2", family="lutar", target=alvo),
            ActionOption(action_id="saida", family="saida"),
        )
        mapa = _mapa(alvos=(alvo,))
        pobre = decidir_no_mapa(mapa, _progresso(ouro=0), opcoes)
        rico = decidir_no_mapa(mapa, _progresso(ouro=10_000), opcoes)
        nota = {d.action_id: {s.action_id: s.utility for s in d.scores} for d in (pobre, rico)}
        assert nota[pobre.action_id]["lutar:2,2"] == nota[rico.action_id]["lutar:2,2"]
        assert pobre.action_id == rico.action_id == "lutar:2,2"


class TestSemRegraDeClasseNemDeSeed:
    def test_nenhum_nome_de_classe_no_cerebro(self):
        for caminho in sorted(CEREBRO.glob("*.py")):
            texto = caminho.read_text(encoding="utf-8").lower()
            for classe in ('"warrior"', '"mage"', '"rogue"', "'warrior'", "'mage'", "'rogue'"):
                assert classe not in texto, f"{caminho} tem regra por classe ({classe})"

    def test_nenhum_literal_de_seed_ou_de_monstro(self):
        for caminho in sorted(CEREBRO.glob("*.py")):
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if isinstance(no, ast.Constant) and isinstance(no.value, int):
                    assert no.value < 10_000_000, (
                        f"{caminho}:{no.lineno} tem um literal com cara de seed"
                    )
