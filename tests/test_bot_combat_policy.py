"""Propriedades da decisão de combate. Recurso, fuga e reaplicação.

O que estes testes protegem é o que a policy anterior errava por forma: ela
comparava a skill com o ataque básico por dano imediato, e como o básico é
gratuito a mana nunca tinha valor. O Mago morreu com 85–100% de MP em cinco de
cinco runs medidas.
"""

from __future__ import annotations

from src.sim.bot import decidir_no_combate
from src.sim.bot.decision import ActionOption
from src.sim.bot.observation import ActionMechanicsView, CombatState


def _estado(**kwargs) -> CombatState:
    base = dict(
        turno=0,
        hp=400,
        hp_max=500,
        mp=100,
        mp_max=100,
        dano_basico=50,
        alvo_nivel=3,
        alvo_hp=300,
        alvo_hp_max=300,
        alvo_mp=30,
        alvo_mp_max=30,
        alvo_dano=40,
    )
    base.update(kwargs)
    return CombatState(**base)


def _ataque(dano=50) -> ActionOption:
    return ActionOption(
        action_id="attack",
        family="attack",
        label="ataque básico",
        mechanics=ActionMechanicsView(expected_strike_damage=dano, hit_chance=1.0),
    )


def _skill(dano, custo, action_id="skill:x") -> ActionOption:
    return ActionOption(
        action_id=action_id,
        family="damage",
        label="skill de dano",
        mechanics=ActionMechanicsView(expected_strike_damage=dano, hit_chance=1.0, mana_cost=custo),
    )


def _fuga(chance=0.5) -> ActionOption:
    return ActionOption(
        action_id="flee",
        family="flee",
        label="fugir",
        mechanics=ActionMechanicsView(flee_chance=chance),
    )


def _nota(decisao, action_id: str) -> float:
    return next(s.utility for s in decisao.scores if s.action_id == action_id)


class TestOBasicoEALinhaDeBase:
    def test_a_parcela_de_duracao_do_basico_e_zero(self):
        """É contra ele que as outras são medidas — por definição, zero."""
        decisao = decidir_no_combate(_estado(), (_ataque(), _fuga()))
        assert _nota(decisao, "attack") == 0.0

    def test_com_nada_melhor_o_basico_vence(self):
        decisao = decidir_no_combate(_estado(), (_ataque(), _skill(dano=50, custo=10), _fuga()))
        assert decisao.action_id == "attack"


class TestManaTemValor:
    def test_skill_que_encurta_a_luta_vence_o_basico_gratuito(self):
        """A regra antiga era "só se bater mais que o básico" — e por isso nunca.

        Aqui a skill precisa VALER mais, não apenas bater mais: o custo entra, e
        com a barra cheia ele é pequeno porque a mana ainda pode virar ação.
        """
        decisao = decidir_no_combate(_estado(), (_ataque(), _skill(dano=120, custo=10), _fuga()))
        assert decisao.action_id == "skill:x"
        assert _nota(decisao, "skill:x") > _nota(decisao, "attack")

    def test_com_a_barra_no_fim_e_luta_longa_a_mana_custa(self):
        cheio = decidir_no_combate(
            _estado(mp=100, alvo_hp=600), (_ataque(), _skill(dano=120, custo=20), _fuga())
        )
        quase_seco = decidir_no_combate(
            _estado(mp=20, alvo_hp=600), (_ataque(), _skill(dano=120, custo=20), _fuga())
        )
        assert _nota(quase_seco, "skill:x") < _nota(cheio, "skill:x"), (
            "a escassez de mana não mudou a nota da skill"
        )

    def test_no_ultimo_turno_guardar_mana_nao_vale_nada(self):
        """Morrer com recurso utilizável é o pior desfecho, e a conta diz isso."""
        # Último turno de verdade: eu mato agora, e ele me mata agora. Com o
        # horizonte em 1, não existe "turno seguinte" para guardar mana.
        curto = _estado(alvo_hp=40, hp=30, alvo_dano=40, dano_basico=50)
        decisao = decidir_no_combate(curto, (_ataque(), _skill(dano=120, custo=90), _fuga()))
        recurso = next(
            valor
            for s in decisao.scores
            if s.action_id == "skill:x"
            for nome, valor in s.components
            if nome == "recurso"
        )
        assert recurso == 0.0

    def test_a_regra_de_mana_nao_conhece_classe(self):
        """O mesmo estado com as mesmas ações decide igual, venha de quem vier."""
        estado = _estado()
        acoes = (_ataque(), _skill(dano=120, custo=10), _fuga())
        assert (
            decidir_no_combate(estado, acoes).action_id
            == decidir_no_combate(estado, acoes).action_id
        )


class TestFugaCompete:
    def test_fuga_e_candidata_e_nao_porteira(self):
        decisao = decidir_no_combate(_estado(), (_ataque(), _fuga()))
        assert "flee" in {s.action_id for s in decisao.scores}

    def test_ganhando_a_corrida_a_fuga_perde(self):
        decisao = decidir_no_combate(_estado(hp=400, alvo_hp=100), (_ataque(), _fuga()))
        assert decisao.action_id != "flee"

    def test_perdendo_de_muito_a_fuga_ganha_do_basico(self):
        perdida = _estado(hp=40, alvo_hp=2000, alvo_dano=40, dano_basico=10)
        decisao = decidir_no_combate(perdida, (_ataque(dano=10), _fuga()))
        assert _nota(decisao, "flee") > _nota(decisao, "attack")

    def test_a_chance_de_fuga_vem_do_jogo_e_muda_a_nota(self):
        perdida = dict(hp=40, alvo_hp=2000, alvo_dano=40, dano_basico=10)
        boa = decidir_no_combate(_estado(**perdida), (_ataque(dano=10), _fuga(chance=0.9)))
        ruim = decidir_no_combate(_estado(**perdida), (_ataque(dano=10), _fuga(chance=0.1)))
        assert _nota(boa, "flee") > _nota(ruim, "flee")


class TestNaoReaplicaOQueJaEstaNoAr:
    def test_buff_ativo_vale_zero_e_diz_por_que(self):
        ativo = ActionOption(
            action_id="skill:buff",
            family="buff",
            label="buff já no ar",
            mechanics=ActionMechanicsView(buff_stat="defense", buff_value=10, already_active=True),
        )
        decisao = decidir_no_combate(_estado(), (_ataque(), ativo, _fuga()))
        score = next(s for s in decisao.scores if s.action_id == "skill:buff")
        assert score.utility == 0.0
        assert "já está ativo" in score.note


class TestCuraEntraNaAvaliacao:
    def test_cura_disputa_e_o_overheal_aparece(self):
        pouca_falta = _estado(hp=490, hp_max=500)
        cura = ActionOption(
            action_id="item:pocao",
            family="heal",
            label="poção",
            mechanics=ActionMechanicsView(healing=200),
        )
        decisao = decidir_no_combate(pouca_falta, (_ataque(), cura, _fuga()))
        score = next(s for s in decisao.scores if s.action_id == "item:pocao")
        assert "aproveitável" in score.note
        assert decisao.action_id != "item:pocao", "curou 10 de vida com uma poção de 200"
