"""As leis globais que ligam um efeito ao outro.

Testam a LEI, não a carta. Se a Quebra Gélida só funcionasse na skill que
congelou, ela não seria uma lei do jogo — seria uma regra daquela carta, e a
próxima carta de gelo precisaria reimplementá-la. Por isso quase todo teste aqui
monta o estado à mão e resolve o golpe pelo motor: a origem da peça não entra na
pergunta.

Também por isso existe o teste de paridade. Não há `hero_shatter` e
`monster_shatter`: existe UMA Quebra Gélida, e quem a ativa pode ser qualquer
entidade.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.mechanics import combat  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.shared import interactions as ix  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402


def _heroi(nivel: int = 20):
    return make_hero("Warrior", nivel, "naked")


def _alvo(nivel: int = 20):
    """Um monstro que não morre no meio da amostra."""
    m = spawn_by_role("trash", nivel)
    m._hp = 10**9
    m.base_hp = 10**6
    return m


def _golpe(atacante, alvo, base=300, semente=1):
    return combat.resolve_physical_attack(
        atacante, alvo, base, "", rng=random.Random(semente), publish=None
    )


class TestCatalogoDeLeis:
    """A pergunta "quais interações existem no jogo?" tem UMA resposta."""

    def test_as_dezesseis_leis_estao_declaradas(self):
        assert len(ix.all_interactions()) == 16

    def test_oito_ja_eram_resolvidas_pelo_nucleo(self):
        antigas = [i for i in ix.all_interactions() if i.kind == ix.KIND_CORE]
        assert len(antigas) == 8
        # Declaradas, e não reimplementadas: cada uma aponta onde já acontece.
        assert all(i.resolved_by for i in antigas)

    def test_os_sete_pares_opostos_continuam_valendo(self):
        pares = {frozenset(p) for p in core.OPPOSING_PAIRS.items()}
        assert len(pares) == 7

    def test_o_sono_continua_quebrando_com_dano(self):
        alvo = _alvo()
        core.apply_effect(alvo, "sleep")
        _golpe(_heroi(), alvo)
        assert not core.has_effect(alvo, "sleep")


class TestQuebraGelida:
    def test_congelado_mais_critico_dispara(self):
        alvo = _alvo()
        core.apply_effect(alvo, "frozen")
        assert ix.strike_interactions(_heroi(), alvo, is_critical=True) == ("quebra_gelida",)

    def test_sem_gelo_ou_sem_critico_nao_dispara(self):
        alvo = _alvo()
        assert ix.strike_interactions(_heroi(), alvo, is_critical=True) == ()
        core.apply_effect(alvo, "frozen")
        assert ix.strike_interactions(_heroi(), alvo, is_critical=False) == ()

    def test_entra_no_bucket_xmult_e_em_nenhum_outro(self):
        alvo = _alvo()
        heroi = _heroi()
        sem = combat.damage_modifiers(heroi, alvo, is_critical=True)
        core.apply_effect(alvo, "frozen")
        com = combat.damage_modifiers(heroi, alvo, is_critical=True)
        assert com.xmult == [*sem.xmult, ix.SHATTER_XMULT]
        assert (com.flat, com.mult, com.mitigation) == (sem.flat, sem.mult, sem.mitigation)

    def test_o_golpe_sai_maior_pelo_funil(self):
        alvo = _alvo()
        heroi = _heroi()
        sem = combat._calculate_damage(
            300, **_baldes(combat.damage_modifiers(heroi, alvo, is_critical=True)), defense_target=0
        )
        core.apply_effect(alvo, "frozen")
        com = combat._calculate_damage(
            300, **_baldes(combat.damage_modifiers(heroi, alvo, is_critical=True)), defense_target=0
        )
        assert com > sem

    def test_consome_o_gelo_depois_do_golpe(self):
        """A troca: ganha dano, abre mão do controle."""
        alvo = _alvo()
        core.apply_effect(alvo, "frozen")
        ix.consume_strike(_heroi(), alvo, ("quebra_gelida",))
        assert not core.has_effect(alvo, "frozen")

    def test_respeita_o_teto_de_xmult(self):
        from src.shared.constants import XMULT_CAP

        assert combat._apply_xmult_cap(ix.SHATTER_XMULT * 10) <= XMULT_CAP


class TestHemorragiaFria:
    def test_quebra_gelida_em_alvo_que_sangra_da_stack(self):
        alvo = _alvo()
        core.apply_effect(alvo, "frozen")
        core.apply_effect(alvo, "bleed")
        antes = core.stacks_of(alvo, "bleed")
        disparadas = ix.consume_strike(_heroi(), alvo, ("quebra_gelida",))
        assert "hemorragia_fria" in disparadas
        assert core.stacks_of(alvo, "bleed") == antes + 1

    def test_sem_sangramento_nao_dispara(self):
        alvo = _alvo()
        core.apply_effect(alvo, "frozen")
        assert ix.consume_strike(_heroi(), alvo, ("quebra_gelida",)) == ("quebra_gelida",)


class TestFeridaAberta:
    def test_bleed_em_alvo_vulneravel_entra_com_stack_extra(self):
        alvo = _alvo()
        core.apply_effect(alvo, "vulnerable")
        combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        assert core.stacks_of(alvo, "bleed") == 2

    def test_sem_vulneravel_entra_normal(self):
        alvo = _alvo()
        combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        assert core.stacks_of(alvo, "bleed") == 1

    def test_o_teto_de_stacks_continua_valendo(self):
        alvo = _alvo()
        core.apply_effect(alvo, "vulnerable")
        for _ in range(6):
            combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        assert core.stacks_of(alvo, "bleed") == core.definition("bleed").max_stacks

    def test_a_lei_nao_aumenta_a_chance_de_aplicar(self):
        """O primeiro sangramento passa pela resistência sozinho."""
        alvo = _alvo()
        core.apply_effect(alvo, "vulnerable")
        alvo.resistances = {"bleed": 100}
        assert not combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        assert not core.has_effect(alvo, "bleed")


class TestToxicidade:
    def test_poison_em_alvo_fragil_dura_um_turno_a_mais(self):
        normal, _ = ix.duration_before_apply(_alvo(), "poison", 5)
        fragil = _alvo()
        core.apply_effect(fragil, "frailty")
        com_lei, leis = ix.duration_before_apply(fragil, "poison", 5)
        assert normal == 5
        assert com_lei == 6
        assert leis == ("toxicidade",)

    def test_nao_muda_intensidade_nem_stacks(self):
        alvo = _alvo()
        core.apply_effect(alvo, "frailty")
        combat.try_apply_status(alvo, "poison", 100, 5, random.Random(1), None)
        [instancia] = [i for i in core.instances(alvo) if i.effect == "poison"]
        assert instancia.stacks == 1
        assert instancia.intensity == core.definition("poison").default_intensity


class TestPanico:
    def test_fear_em_alvo_que_sangra_dura_um_turno_a_mais(self):
        alvo = _alvo()
        core.apply_effect(alvo, "bleed")
        duracao, leis = ix.duration_before_apply(alvo, "fear", 3)
        assert duracao == 4
        assert leis == ("panico",)

    def test_a_forca_do_medo_e_a_mesma(self):
        alvo = _alvo()
        core.apply_effect(alvo, "bleed")
        combat.try_apply_status(alvo, "fear", 100, 3, random.Random(1), None)
        [instancia] = [i for i in core.instances(alvo) if i.effect == "fear"]
        assert instancia.intensity == core.definition("fear").default_intensity


class TestFeridaSeptica:
    def test_bleed_renova_o_poison(self):
        alvo = _alvo()
        core.apply_effect(alvo, "poison", duration=1)
        combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        [veneno] = [i for i in core.instances(alvo) if i.effect == "poison"]
        assert veneno.duration == core.definition("poison").default_duration

    def test_poison_renova_o_bleed(self):
        alvo = _alvo()
        core.apply_effect(alvo, "bleed", duration=1)
        combat.try_apply_status(alvo, "poison", 100, 5, random.Random(1), None)
        [sangue] = [i for i in core.instances(alvo) if i.effect == "bleed"]
        assert sangue.duration == core.definition("bleed").default_duration

    def test_nao_da_stack_extra(self):
        alvo = _alvo()
        core.apply_effect(alvo, "poison", duration=1)
        antes = core.stacks_of(alvo, "poison")
        combat.try_apply_status(alvo, "bleed", 100, 2, random.Random(1), None)
        assert core.stacks_of(alvo, "poison") == antes


class TestColapsoMental:
    def test_mana_burn_drena_cinquenta_por_cento_a_mais(self):
        def mp_perdido(com_clouded: bool) -> int:
            alvo = _heroi()
            alvo._mp = alvo.base_mp
            core.apply_effect(alvo, "mana_burn")
            if com_clouded:
                core.apply_effect(alvo, "clouded")
            relatorio = core.tick_effects(alvo, drain_scale=ix.drain_scale)
            return relatorio["drain"].get("mana_burn", 0)

        normal = mp_perdido(False)
        turvo = mp_perdido(True)
        assert turvo == int(normal * ix.MENTAL_COLLAPSE_DRAIN)

    def test_nao_e_dano(self):
        alvo = _heroi()
        core.apply_effect(alvo, "mana_burn")
        core.apply_effect(alvo, "clouded")
        hp = alvo.get_hp()
        core.tick_effects(alvo, drain_scale=ix.drain_scale)
        assert alvo.get_hp() == hp


class TestEmboscada:
    def test_invisivel_atacando_dispara(self):
        heroi = _heroi()
        core.apply_effect(heroi, "invisible")
        assert ix.strike_interactions(heroi, _alvo(), is_critical=False) == ("emboscada",)

    def test_entra_no_bucket_xmult(self):
        heroi = _heroi()
        alvo = _alvo()
        sem = combat.damage_modifiers(heroi, alvo, is_critical=False)
        core.apply_effect(heroi, "invisible")
        com = combat.damage_modifiers(heroi, alvo, is_critical=False)
        assert com.xmult == [*sem.xmult, ix.AMBUSH_XMULT]
        assert (com.flat, com.mult, com.mitigation) == (sem.flat, sem.mult, sem.mitigation)

    def test_a_invisibilidade_sai_no_golpe_que_acerta(self):
        heroi = _heroi()
        core.apply_effect(heroi, "invisible")
        golpe = _golpe(heroi, _alvo(), semente=3)
        assert not golpe.was_evaded
        assert not core.has_effect(heroi, "invisible")

    def test_a_invisibilidade_sai_mesmo_errando(self):
        """Atacou, revelou a posição. Não dá para guardar o bônus até acertar."""

        class SempreErra(random.Random):
            def randrange(self, *args, **kwargs):  # a primeira rolagem é o acerto
                return 100

        heroi = _heroi()
        core.apply_effect(heroi, "invisible")
        golpe = combat.resolve_physical_attack(
            heroi, _alvo(), 300, "", rng=SempreErra(0), publish=None
        )
        assert golpe.was_evaded
        assert not core.has_effect(heroi, "invisible")


class TestParidadeHeroiEMonstro:
    """Existe UMA lei. O ator pode ser qualquer entidade."""

    @pytest.mark.parametrize("invertido", [False, True])
    def test_a_mesma_quebra_gelida_para_os_dois_lados(self, invertido):
        heroi, monstro = _heroi(), _alvo()
        atacante, defensor = (monstro, heroi) if invertido else (heroi, monstro)
        core.apply_effect(defensor, "frozen")
        assert ix.strike_interactions(atacante, defensor, is_critical=True) == ("quebra_gelida",)
        ix.consume_strike(atacante, defensor, ("quebra_gelida",))
        assert not core.has_effect(defensor, "frozen")

    @pytest.mark.parametrize("invertido", [False, True])
    def test_a_mesma_ferida_aberta_para_os_dois_lados(self, invertido):
        heroi, monstro = _heroi(), _alvo()
        defensor = heroi if invertido else monstro
        core.apply_effect(defensor, "vulnerable")
        combat.try_apply_status(defensor, "bleed", 100, 2, random.Random(1), None)
        assert core.stacks_of(defensor, "bleed") == 2

    @pytest.mark.parametrize("invertido", [False, True])
    def test_o_mesmo_colapso_mental_para_os_dois_lados(self, invertido):
        alvo = _alvo() if invertido else _heroi()
        core.apply_effect(alvo, "clouded")
        fator, leis = ix.drain_scale(alvo, "mana_burn")
        assert fator == ix.MENTAL_COLLAPSE_DRAIN
        assert leis == ("colapso_mental",)


class TestOMonstroPercebeAOportunidade:
    @staticmethod
    def _queima_de_mana(monstro):
        return [s for s in monstro.skills if "mana_burn" in ix.applicable_effects(s)]

    def test_a_lei_so_conta_com_o_estado_realmente_no_alvo(self):
        """Nada de conhecimento mágico: sem Mente Turva, queima é só queima."""
        monstro = spawn_by_role("controller", 12)
        [carta, *_] = self._queima_de_mana(monstro)

        assert ix.opportunities(monstro, _heroi(), carta) == ()

        turvo = _heroi()
        core.apply_effect(turvo, "clouded")
        assert ix.opportunities(monstro, turvo, carta) == ("colapso_mental",)

    def test_sem_oportunidade_o_peso_nao_muda_nada(self):
        monstro = spawn_by_role("controller", 12)
        [carta, *_] = self._queima_de_mana(monstro)
        assert ix.opportunity_weight(monstro, _heroi(), carta) == 1.0

    @staticmethod
    def _carta(monstro, nome):
        return next(s for s in monstro.skills if s.name == nome)

    def test_a_lei_desempata_entre_cartas_comparaveis(self):
        """O par é real: Presságio vale 2,10 e Queima de Mana 1,50.

        Com o alvo de Mente Turva, a Queima destrava Colapso Mental e passa à
        frente. É desempate, e não ordem: as cartas que ROUBAM O TURNO — Letargia
        e Teia de Gelo — continuam acima das duas, e é assim que deve ser. Uma IA
        que largasse o controle para perseguir um combo estaria jogando pior.
        """
        from src.mechanics import monster_ai

        monstro = spawn_by_role("controller", 12)
        par = [self._carta(monstro, "Presságio"), self._carta(monstro, "Queima de Mana")]

        assert monster_ai._maior(par, monstro, _heroi()).name == "Presságio"

        turvo = _heroi()
        core.apply_effect(turvo, "clouded")
        assert monster_ai._maior(par, monstro, turvo).name == "Queima de Mana"

    def test_a_rotina_leva_o_estado_do_alvo_para_a_escolha(self):
        """Sem execução, sobrevivência ou desespero acima dela."""
        from src.mechanics import monster_ai

        monstro = spawn_by_role("controller", 12)
        monstro._mp = monstro.base_mp
        par = [self._carta(monstro, "Presságio"), self._carta(monstro, "Queima de Mana")]

        limpo, _ = monster_ai._pick_skill(monstro, _heroi(), par, random.Random(0))
        turvo = _heroi()
        core.apply_effect(turvo, "clouded")
        com_lei, _ = monster_ai._pick_skill(monstro, turvo, par, random.Random(0))

        assert limpo.name == "Presságio"
        assert com_lei.name == "Queima de Mana", "A oportunidade não chegou à rotina."

    def test_a_execucao_continua_acima_da_oportunidade(self):
        """Perseguir combo com o herói a um golpe da morte é jogar pior."""
        from src.mechanics import monster_ai

        monstro = spawn_by_role("controller", 12)
        monstro._mp = monstro.base_mp
        alvo = _heroi()
        core.apply_effect(alvo, "clouded")
        alvo._hp = 1
        usaveis = monster_ai._usable_skills(monstro, alvo)
        assert [s for s in usaveis if s.effect_type == "damage"], "Cenário sem dano não prova nada."
        escolha, decisiva = monster_ai._pick_skill(monstro, alvo, usaveis, random.Random(0))
        assert escolha.effect_type == "damage"
        assert decisiva


def _baldes(mods) -> dict:
    return {
        "flat_mods": mods.flat,
        "mult_mods": mods.mult,
        "xmult_mods": mods.xmult,
        "mitigation": mods.mitigation,
    }


class TestCoberturaDeMonstro:
    """Toda lei nova precisa de um caminho real para o monstro no 1x1.

    No duelo não existe aliado para preparar a jogada: o mesmo monstro tem de
    colocar as DUAS peças com as próprias cartas, ao longo dos próprios turnos.
    Estes testes provam o patch de conteúdo que fechou isso, e não o motor —
    o motor já estava certo, faltavam as peças.
    """

    @staticmethod
    def _mob(role, nivel=20):
        mob = spawn_by_role(role, nivel)
        mob._mp = 10**6
        return mob

    @staticmethod
    def _carta(mob, sid):
        return next(s for s in mob.skills if s.id == sid)

    def _lancar(self, mob, alvo, sid):
        carta = self._carta(mob, sid)
        destino = mob if getattr(carta, "target", "enemy") == "self" else alvo
        combat.apply_skill(mob, destino, carta, rng=_Sempre(0), publish=None)

    def test_status_de_alvo_self_cai_no_proprio_monstro(self):
        """`Esquiva Felina` virou status: quem recebe é o lançador, não o herói."""
        mob, heroi = self._mob("skirmisher"), _heroi()
        self._lancar(mob, heroi, "mob_evasao_mob")
        assert core.has_effect(mob, "invisible")
        assert not core.has_effect(heroi, "invisible")

    def test_a_ia_nao_reaplica_invisibilidade_ja_ativa(self):
        """Perguntar ao herói faria o monstro pagar MP por um turno em branco."""
        from src.mechanics import monster_ai

        mob, heroi = self._mob("skirmisher"), _heroi()
        assert any(s.id == "mob_evasao_mob" for s in monster_ai._usable_skills(mob, heroi))

        core.apply_effect(mob, "invisible")
        assert not any(s.id == "mob_evasao_mob" for s in monster_ai._usable_skills(mob, heroi))

    def test_praga_lenta_dispara_toxicidade_na_ordem_nova(self):
        """Fragilidade primeiro, veneno depois: a lei precisa da peça já posta."""
        mob, heroi = self._mob("support"), _heroi()
        vistos: list[str] = []

        def publicar(_topico, evento):
            if evento.payload.get("kind") == "interaction":
                vistos.append(evento.payload["label"])

        carta = self._carta(mob, "mob_praga_lenta")
        assert carta.effect_value == "frailty"
        assert carta.secondary.effect == "poison"
        combat.apply_skill(mob, heroi, carta, rng=_Sempre(0), publish=publicar)
        assert "TOXICIDADE" in vistos

    def test_toda_lei_nova_tem_pelo_menos_um_arquetipo(self):
        """A auditoria, reduzida à pergunta que importa: sobrou alguma sem dono?"""
        from tools.audit_interactions import PECAS, ROLES, fontes_do_monstro

        fontes = fontes_do_monstro()
        sem_dono = [
            lei
            for lei, pecas in PECAS.items()
            if not any(all(fontes[p].get(r) for p in pecas) for r in ROLES)
        ]
        assert not sem_dono, f"Leis sem nenhum monstro capaz de montá-las: {sem_dono}"


class _Sempre(random.Random):
    """Toda rolagem passa. A chance é a do jogo; aqui ela é fixada."""

    def randrange(self, *args, **kwargs):
        return 1
