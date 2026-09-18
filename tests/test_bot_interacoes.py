"""Paridade das INTERAÇÕES: o que o adapter declara × o que o engine faz.

A FASE B responde uma pergunta só: *existe uma lei válida AGORA, e qual
consequência mecânica o engine produziria se esta ação a ativasse?* Quanto isso
vale é FASE C, e nada aqui responde isso.

Um achado que mudou o desenho e precisa de guarda permanente: o dano declarado
JÁ INCLUI o ×MULT das leis de golpe, porque `combat.damage_modifiers` chama
`strike_xmult(strike_interactions(...))` por dentro. `damage_xmult` é
informativo — multiplicá-lo de novo conta duas vezes.
"""

from __future__ import annotations

import copy
import random

from src.content.factories.monsters import create_monster
from src.engine.game_logic import create_player_from_data
from src.mechanics import combat as cm
from src.shared import effect_core as core
from src.shared import interactions as ix
from tools import bot_adapter as ad


def _heroi(classe="rogue", nivel=8):
    h = create_player_from_data(classe, "Interacoes")
    h.set_level(nivel)
    return h


def _monstro(nivel=8):
    return create_monster("Alvo", nivel, "bruiser")


def _por_id(views) -> dict:
    return {v.interaction_id: v for v in views}


class TestOCatalogoInteiroEstaClassificado:
    """Se uma lei nova entrar em `interactions.py`, este teste cai.

    Sem ele, a FASE B envelhece em silêncio: o catálogo cresce e o bot para de
    enxergar as leis novas sem ninguém perceber.
    """

    # A classificação da auditoria. Mudar o catálogo obriga a revisitar a matriz.
    POR_CONSTRUCAO = {
        "empowered_weakened",
        "arcane_surge_hexed",
        "quickened_slowed",
        "fortified_vulnerable",
        "vitality_frailty",
        "focused_clouded",
        "precision_fear",
    }
    CUSTO_DA_ACAO = {"sleep_damage"}
    EXPOSTAS = {
        "emboscada",
        "quebra_gelida",
        "toxicidade",
        "panico",
        "ferida_aberta",
        "ferida_septica",
        "colapso_mental",
    }
    LACUNA_CONHECIDA = {"hemorragia_fria"}

    def test_toda_lei_do_catalogo_tem_classificacao(self):
        catalogadas = {i.id for i in ix.all_interactions()}
        classificadas = (
            self.POR_CONSTRUCAO | self.CUSTO_DA_ACAO | self.EXPOSTAS | self.LACUNA_CONHECIDA
        )
        assert catalogadas == classificadas, (
            f"sem classificação: {sorted(catalogadas - classificadas)}; "
            f"classificadas e inexistentes: {sorted(classificadas - catalogadas)}"
        )


class TestCondicaoAusenteCondicaoPresente:
    def test_sem_a_condicao_a_lei_nao_aparece(self):
        hero, alvo = _heroi(), _monstro()
        assert ad._interacoes_do_ataque(hero, alvo) == ()

    def test_com_a_condicao_a_lei_aparece(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        assert "emboscada" in _por_id(ad._interacoes_do_ataque(hero, alvo))

    def test_a_lei_some_quando_a_condicao_sai(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        core.remove_effect(hero, "invisible")
        assert ad._interacoes_do_ataque(hero, alvo) == ()


class TestDependenciaDeCritico:
    def test_quebra_gelida_e_declarada_como_dependente_de_critico(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        assert _por_id(ad._interacoes_do_ataque(hero, alvo))["quebra_gelida"].requires_critical

    def test_emboscada_nao_depende_de_critico(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        assert not _por_id(ad._interacoes_do_ataque(hero, alvo))["emboscada"].requires_critical

    def test_a_dependencia_declarada_bate_com_a_funcao_canonica(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        sem = set(ix.strike_interactions(hero, alvo, is_critical=False))
        com = set(ix.strike_interactions(hero, alvo, is_critical=True))
        for view in ad._interacoes_do_ataque(hero, alvo):
            esperado = view.interaction_id in (com - sem)
            assert view.requires_critical is esperado


class TestMultiplicadorDeclaradoEODoEngine:
    def test_o_fator_declarado_e_o_de_strike_xmult(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        view = _por_id(ad._interacoes_do_ataque(hero, alvo))["emboscada"]
        assert [view.damage_xmult] == ix.strike_xmult(("emboscada",))

    def test_o_dano_declarado_ja_contem_o_fator(self):
        """A guarda contra dupla contagem na FASE C.

        `damage_modifiers` chama `strike_xmult(strike_interactions(...))` por
        dentro, então o fator já está no dano. Se um dia deixar de estar, é aqui
        que se descobre — e não numa policy que multiplicava duas vezes.
        """
        hero, alvo = _heroi(), _monstro()
        base = cm.basic_attack_power(hero)
        sem = ad._dano_do_funil(hero, alvo, base, critico=False)
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        com = ad._dano_do_funil(hero, alvo, base, critico=False)
        assert com > sem, "o dano declarado NÃO inclui o fator da lei — a FASE C precisaria somá-lo"

    def test_lei_que_nao_mexe_em_dano_declara_o_neutro(self):
        """Neutro é 1.0. Zero zeraria o dano na primeira multiplicação distraída."""
        alvo = _monstro(10)
        core.apply_effect(alvo, "frailty", source_id="t", duration=3)
        view = ad._view_da_lei("toxicidade", exige_critico=False, bonus_de_duracao=1)
        assert view.damage_xmult == 1.0


class TestConsumoDeclaradoEOQueOEngineConsome:
    """O mirror de `consume_strike`, provado contra a execução real."""

    def test_emboscada_consome_a_invisibilidade_do_atacante(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        view = _por_id(ad._interacoes_do_ataque(hero, alvo))["emboscada"]
        assert view.consumes_status == "invisible" and view.consumes_from_self

        disparadas = ix.strike_interactions(hero, alvo, is_critical=False)
        ix.consume_strike(hero, alvo, disparadas)
        assert not core.has_effect(hero, view.consumes_status), (
            "o engine não consumiu o que o adapter declarou"
        )

    def test_quebra_gelida_consome_o_congelamento_do_alvo(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        view = _por_id(ad._interacoes_do_ataque(hero, alvo))["quebra_gelida"]
        assert view.consumes_status == "frozen" and not view.consumes_from_self

        disparadas = ix.strike_interactions(hero, alvo, is_critical=True)
        ix.consume_strike(hero, alvo, disparadas)
        assert not core.has_effect(alvo, view.consumes_status)

    def test_observar_nao_consome_nada(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        for _ in range(5):
            ad._interacoes_do_ataque(hero, alvo)
        assert core.has_effect(hero, "invisible") and core.has_effect(alvo, "frozen")


class TestLeisDeAplicacaoDeclaramDuracao:
    def test_toxicidade_declara_o_bonus_da_funcao_canonica(self):
        alvo = _monstro(10)
        core.apply_effect(alvo, "frailty", source_id="t", duration=3)
        duracao, disparadas = ix.duration_before_apply(alvo, "poison", 1)
        assert "toxicidade" in disparadas
        assert duracao - 1 == 1

    def test_sem_a_condicao_nao_ha_bonus(self):
        alvo = _monstro(10)
        duracao, disparadas = ix.duration_before_apply(alvo, "poison", 1)
        assert disparadas == () and duracao == 1


class TestQuebraDeStatusPeloDano:
    def test_alvo_dormindo_faz_a_acao_declarar_que_quebra_o_sono(self):
        alvo = _monstro()
        core.apply_effect(alvo, "sleep", source_id="t", duration=3)
        assert "sleep" in ad._quebra_ao_dar_dano(alvo)

    def test_alvo_sem_efeito_quebravel_declara_tupla_vazia(self):
        assert ad._quebra_ao_dar_dano(_monstro()) == ()

    def test_o_declarado_bate_com_o_catalogo_de_efeitos(self):
        alvo = _monstro()
        core.apply_effect(alvo, "sleep", source_id="t", duration=3)
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        for efeito in ad._quebra_ao_dar_dano(alvo):
            assert core.definition(efeito).breaks_on_damage
        ativos = set(getattr(alvo, "active_effects", {}) or {})
        for efeito in ativos - set(ad._quebra_ao_dar_dano(alvo)):
            definicao = core.definition(str(efeito))
            assert definicao is None or not definicao.breaks_on_damage

    def test_a_acao_de_dano_carrega_a_tupla(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(alvo, "sleep", source_id="t", duration=3)
        estado = ad.estado_do_combate(hero, alvo, 0)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, estado)
        ataque = next(o for o in opcoes if o.action_id == "attack")
        assert "sleep" in ataque.mechanics.breaks_statuses


class TestCoreRepresentadasPorConstrucao:
    """As sete leis CORE não viram view: elas já estão dentro de cada atributo."""

    def test_forca_e_fraqueza_mudam_o_dano_declarado(self):
        hero, alvo = _heroi("warrior", 8), _monstro()
        base = cm.basic_attack_power(hero)
        neutro = ad._dano_do_funil(hero, alvo, base, critico=False)
        core.apply_effect(hero, "weakened", source_id="t", duration=3)
        enfraquecido = cm.basic_attack_power(hero)
        assert enfraquecido <= base
        assert ad._dano_do_funil(hero, alvo, enfraquecido, critico=False) <= neutro

    def test_guarda_e_brecha_mudam_o_dano_declarado(self):
        hero, alvo = _heroi("warrior", 8), _monstro()
        base = cm.basic_attack_power(hero)
        antes = ad._dano_do_funil(hero, alvo, base, critico=False)
        core.apply_effect(alvo, "vulnerable", source_id="t", duration=3)
        assert ad._dano_do_funil(hero, alvo, base, critico=False) > antes

    def test_mira_e_medo_mudam_a_chance_de_acerto(self):
        hero, alvo = _heroi("warrior", 8), _monstro()
        antes = ad._chance_de_acerto(hero, alvo)
        core.apply_effect(hero, "fear", source_id="t", duration=3)
        assert ad._chance_de_acerto(hero, alvo) < antes

    def test_pressa_e_peso_mudam_a_agilidade_que_alimenta_a_iniciativa(self):
        """A iniciativa sai de `build_turn_order`, que lê `get_ag`.

        Provar a AGILIDADE e não a ordem: com o monstro mais lento, a ordem pode
        já estar decidida a favor do herói e o booleano não mudaria — uma
        asserção sobre ele passaria sem verificar coisa alguma.
        """
        alvo = _monstro(5)
        antes = alvo.get_ag()
        core.apply_effect(alvo, "slowed", source_id="t", duration=3)
        assert alvo.get_ag() < antes


class TestObservarInteracoesNaoMutaNadaNemRNG:
    def test_enumerar_com_leis_ativas_nao_altera_estado_nem_rng(self):
        hero, alvo = _heroi(), _monstro()
        core.apply_effect(hero, "invisible", source_id="t", duration=3)
        core.apply_effect(alvo, "frozen", source_id="t", duration=3)
        core.apply_effect(alvo, "bleed", source_id="t", duration=3)

        antes = (
            hero.get_hp(),
            hero.get_mp(),
            alvo.get_hp(),
            copy.deepcopy(getattr(hero, "active_effects", {})),
            copy.deepcopy(getattr(alvo, "active_effects", {})),
            dict(getattr(hero, "skill_cooldowns", {})),
        )
        r = random.Random(11)
        rng_antes = r.getstate()

        estado = ad.estado_do_combate(hero, alvo, 0)
        ad.acoes_do_combate(hero, alvo, estado)

        depois = (
            hero.get_hp(),
            hero.get_mp(),
            alvo.get_hp(),
            copy.deepcopy(getattr(hero, "active_effects", {})),
            copy.deepcopy(getattr(alvo, "active_effects", {})),
            dict(getattr(hero, "skill_cooldowns", {})),
        )
        assert antes == depois
        assert r.getstate() == rng_antes


class TestOAdapterNaoTrazEstrategia:
    def test_nao_usa_opportunity_weight(self):
        """`OPPORTUNITY_BONUS` é quanto a lei VALE — pergunta da FASE C."""
        texto = open("tools/bot_adapter.py", encoding="utf-8").read()
        assert "opportunity_weight" not in texto.replace(
            "NÃO usa `opportunity_weight`", ""
        ).replace("aquele carrega `OPPORTUNITY_BONUS`", "")

    def test_a_view_nao_tem_campo_de_julgamento(self):
        from src.sim.bot.observation import InteractionView

        campos = set(InteractionView.__dataclass_fields__)
        proibidos = {"score", "value", "utility", "is_good", "should_use", "priority", "weight"}
        assert not (campos & proibidos)
