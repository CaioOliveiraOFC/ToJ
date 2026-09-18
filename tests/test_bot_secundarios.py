"""Efeito principal e `secondary` são a MESMA peça do jogo.

`combat.apply_skill` passa os dois pelo mesmo `apply_effect`, com a mesma
resistência e as mesmas leis de interação. O bot não pode valorar `vulnerable`
de um jeito quando ele é o efeito da carta e de outro quando vem no campo
`secondary` — seriam duas notas para a mesma coisa.

Varredura no catálogo REAL: 66 das 150 cartas têm `secondary`, e 24 delas são
skills de status que aplicam DOIS efeitos. Antes desta rodada o secundário
chegava com nome e chance e sem consequência nenhuma, e o segundo efeito de uma
carta de status simplesmente não existia para o bot.
"""

from __future__ import annotations

import json

from src.content.factories.monsters import create_monster
from src.content.skills_loader import get_skill_by_id
from src.engine.game_logic import create_player_from_data
from src.shared import effect_core as core
from src.sim.bot.decision import ActionOption
from src.sim.bot.evaluators import avaliar_combate
from src.sim.bot.observation import ActionMechanicsView, CombatState, StatusView
from tools import bot_adapter as ad


def _heroi(classe="warrior", nivel=10):
    h = create_player_from_data(classe, "Secundario")
    h.set_level(nivel)
    return h


def _monstro(nivel=10, papel="bruiser"):
    return create_monster("Alvo", nivel, papel)


def _cartas_com_secundario() -> list[dict]:
    dados = json.load(open("src/data/skills.json", encoding="utf-8"))
    itens = dados["skills"] if isinstance(dados, dict) and "skills" in dados else dados
    lista = list(itens.values()) if isinstance(itens, dict) else itens
    return [s for s in lista if s.get("secondary")]


def _estado(**kwargs) -> CombatState:
    base = dict(
        turno=1,
        hp=400,
        hp_max=500,
        mp=100,
        mp_max=100,
        dano_basico=50,
        alvo_nivel=5,
        alvo_hp=600,
        alvo_hp_max=600,
        alvo_mp=40,
        alvo_mp_max=40,
        alvo_dano=40,
    )
    base.update(kwargs)
    return CombatState(**base)


class TestVarreduraDoCatalogo:
    def test_o_catalogo_tem_cartas_com_secundario(self):
        """Sem isto, toda a varredura abaixo ficaria verde sem verificar nada."""
        assert len(_cartas_com_secundario()) >= 60

    def test_toda_carta_com_secundario_declara_o_secundario(self):
        hero = _heroi("warrior", 12)
        faltando = []
        for dados in _cartas_com_secundario():
            skill = get_skill_by_id(dados["id"])
            if skill is None:
                continue
            m = ad._mecanica_de_skill(hero, _monstro(12), skill)
            efeitos = {st.effect for st in m.statuses}
            if str(dados["secondary"]["effect"]) not in efeitos:
                faltando.append(dados["name"])
        assert not faltando, f"secundário sem representação: {faltando}"

    def test_carta_de_status_com_secundario_declara_os_dois_efeitos(self):
        hero = _heroi("warrior", 12)
        vistos = 0
        for dados in _cartas_com_secundario():
            if dados["effect_type"] != "status":
                continue
            skill = get_skill_by_id(dados["id"])
            if skill is None:
                continue
            m = ad._mecanica_de_skill(hero, _monstro(12), skill)
            efeitos = [st.effect for st in m.statuses]
            assert str(dados["effect_value"]) in efeitos, dados["name"]
            assert str(dados["secondary"]["effect"]) in efeitos, dados["name"]
            vistos += 1
        assert vistos >= 20, "a varredura não alcançou as cartas de status com secundário"

    def test_o_secundario_sai_do_mesmo_construtor_do_principal(self):
        """A propriedade central: mesma peça, mesma consequência, mesmos campos."""
        hero = _heroi("warrior", 12)
        for dados in _cartas_com_secundario():
            skill = get_skill_by_id(dados["id"])
            if skill is None:
                continue
            alvo = _monstro(12)
            m = ad._mecanica_de_skill(hero, alvo, skill)
            sec = dados["secondary"]
            declarado = next(st for st in m.statuses if st.effect == str(sec["effect"]))
            direto = ad._status_declarado(
                hero, alvo, str(sec["effect"]), float(sec["chance"]), int(sec["duration"] or 0)
            )
            assert declarado == direto, dados["name"]


class TestConsequenciaDoSecundario:
    """As mesmas consequências que o principal ganhou na FASE C."""

    def _view(self, skill_id: str, efeito: str) -> StatusView:
        hero, alvo = _heroi("warrior", 12), _monstro(12)
        skill = get_skill_by_id(skill_id)
        assert skill is not None, skill_id
        m = ad._mecanica_de_skill(hero, alvo, skill)
        return next(st for st in m.statuses if st.effect == efeito)

    def test_quebra_guarda_declara_o_golpe_que_passa_a_sair_maior(self):
        """damage + vulnerable: baixa a Defesa do alvo, então meu golpe cresce."""
        assert self._view("quebra_guarda", "vulnerable").outgoing_damage_after > 0

    def test_danca_das_laminas_declara_o_golpe_que_passa_a_entrar_menor(self):
        """damage + weakened: baixa a Força do alvo, então o golpe dele encolhe."""
        assert self._view("danca_laminas", "weakened").incoming_damage_after > 0

    def test_pisada_de_ferro_declara_as_duas_pontas(self):
        """damage + slowed: Agilidade mexe no acerto dos DOIS lados."""
        st = self._view("pisada_de_ferro", "slowed")
        assert st.incoming_damage_after > 0
        assert st.outgoing_damage_after > 0

    def test_lasca_de_gelo_declara_o_mesmo_que_pisada_de_ferro(self):
        """O mesmo efeito, em cartas de classes diferentes, tem a mesma mecânica."""
        gelo = self._view("lasca_de_gelo", "slowed")
        ferro = self._view("pisada_de_ferro", "slowed")
        assert gelo.incoming_damage_after == ferro.incoming_damage_after
        assert gelo.outgoing_damage_after == ferro.outgoing_damage_after

    def test_dividendo_de_mana_declara_o_dreno(self):
        """damage + mana_burn: recurso negado é consequência, não enfeite."""
        assert self._view("dividendo_de_mana", "mana_burn").target_mp_drained > 0

    def test_secundario_de_dot_declara_dano_por_turno(self):
        st = self._view("sangue_nos_olhos", "bleed")
        assert st.dot_damage_per_turn > 0
        assert st.dot_duration > 0

    def test_secundario_de_controle_declara_que_rouba_turno(self):
        assert self._view("golpe_baixo", "stun").skips_turn


class TestOEvaluatorNaoDistingue:
    """O cérebro não sabe o que é principal e o que é secundário — nem deve."""

    def _opcao(self, family: str, statuses: tuple[StatusView, ...]) -> ActionOption:
        return ActionOption(
            action_id=f"skill:{family}",
            family=family,
            label=family,
            mechanics=ActionMechanicsView(statuses=statuses, duration=3, mana_cost=10),
        )

    def test_mesmo_efeito_pela_carta_de_dano_e_pela_de_status_vale_o_mesmo(self):
        efeito = (StatusView(effect="weakened", chance=0.6, duration=3, incoming_damage_after=25),)
        state = _estado(hp=120, alvo_dano=60)
        por_status = avaliar_combate(self._opcao("status", efeito), state)
        por_dano = avaliar_combate(self._opcao("damage", efeito), state)
        assert por_status.components == por_dano.components

    def test_dois_efeitos_somam_as_duas_consequencias(self):
        state = _estado(hp=120, alvo_dano=60)
        um = (StatusView(effect="weakened", chance=1.0, duration=3, incoming_damage_after=30),)
        dois = um + (StatusView(effect="stun", chance=1.0, duration=2, skips_turn=True),)
        assert (
            avaliar_combate(self._opcao("status", dois), state).utility
            > avaliar_combate(self._opcao("status", um), state).utility
        )

    def test_efeito_ja_no_ar_nao_conta_duas_vezes(self):
        state = _estado(hp=120, alvo_dano=60)
        no_ar = (
            StatusView(
                effect="weakened",
                chance=1.0,
                duration=3,
                incoming_damage_after=30,
                already_active=True,
            ),
        )
        score = avaliar_combate(self._opcao("status", no_ar), state)
        assert score.note.startswith("o efeito desta ação já está ativo")


class TestLacunaRegistradaDeRecurso:
    """`frailty` e `clouded` no alvo mexem no TETO, e a luta corre pelo ATUAL.

    Os dois são LIVE (2 e 3 cartas como secundário), mas hoje não mudam decisão
    nenhuma: baixam `base_hp`/`base_mp` do monstro sem tocar o HP e o MP atuais,
    e nada no motor re-limita o atual ao novo teto. Este teste é a evidência da
    lacuna E o alarme: no dia em que o motor passar a limitar, ele cai e a
    consequência precisa ser representada.
    """

    def test_frailty_no_alvo_nao_muda_o_hp_que_decide_a_corrida(self):
        alvo = _monstro(12)
        antes = alvo.get_hp()
        definicao = core.definition("frailty")
        core.apply_effect(
            alvo, "frailty", intensity=definicao.default_intensity, duration=3, source_id="teste"
        )
        assert alvo.base_hp < antes, "frailty deveria baixar o teto"
        assert alvo.get_hp() == antes, "se o atual passar a ser limitado, isto vira consequência"
        alvo.take_damage(1)
        assert alvo.get_hp() == antes - 1

    def test_clouded_no_alvo_nao_muda_o_mp_que_o_dreno_consome(self):
        alvo = _monstro(12)
        antes = alvo.get_mp()
        definicao = core.definition("clouded")
        core.apply_effect(
            alvo, "clouded", intensity=definicao.default_intensity, duration=3, source_id="teste"
        )
        assert alvo.base_mp < antes
        assert alvo.get_mp() == antes
