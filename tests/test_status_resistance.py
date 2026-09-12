"""Resistência a status: dano resolve dano, status resolve status.

Um golpe pode tirar a vida inteira e mesmo assim não congelar. Um alvo imune a
`frozen` leva o dano normalmente. São dois sistemas vizinhos, e a implementação
não pode confundi-los — resistência a status não entra na mitigação de dano.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.items import Item  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effects as fx  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from tests.test_damage_pipeline import ACERTA_SEM_CRIT, RngRoteirizado  # noqa: E402


def _proporcao_que_pegou(alvo_fabrica, status, chance, tentativas=2000):
    """Fração das tentativas em que o status pegou, com rolagem uniforme."""
    pegou = 0
    for i in range(tentativas):
        alvo = alvo_fabrica()
        # Rolagem determinística varrendo 1..100: mede a chance efetiva exata.
        r = RngRoteirizado((i % 100) + 1)
        if cmb.try_apply_status(alvo, status, chance, 3, r):
            pegou += 1
    return pegou / tentativas


def _heroi():
    return make_hero("Warrior", 8, "expected")


class TestFormula:
    """`base × (1 − resistência/100)`, com as duas pontas em 0..100."""

    @pytest.mark.parametrize(
        "base,resist,esperado",
        [(40, 0, 40), (40, 25, 30), (40, 50, 20), (40, 100, 0), (100, 50, 50), (100, 100, 0)],
    )
    def test_a_chance_efetiva(self, base, resist, esperado):
        assert fx.effective_status_chance(base, resist) == pytest.approx(esperado)

    def test_as_pontas_ficam_presas(self):
        assert fx.effective_status_chance(300, 0) == 100
        assert fx.effective_status_chance(-10, 0) == 0
        assert fx.effective_status_chance(50, 300) == 0
        assert fx.effective_status_chance(50, -50) == 50


class TestResistenciaNaRolagem:
    def test_sem_resistencia_a_chance_e_a_declarada(self):
        """Resistência zero preserva o jogo que existe hoje."""
        assert _proporcao_que_pegou(_heroi, "stun", 40) == pytest.approx(0.40, abs=0.01)

    def test_metade_reduz_pela_metade(self):
        def alvo():
            h = _heroi()
            h.resistances["stun"] = 50
            return h

        assert _proporcao_que_pegou(alvo, "stun", 40) == pytest.approx(0.20, abs=0.01)

    def test_cem_por_cento_e_imunidade_de_verdade(self):
        """Sem piso. Se o jogador pagou pela imunidade, ela é real."""

        def alvo():
            h = _heroi()
            h.resistances["frozen"] = 100
            return h

        assert _proporcao_que_pegou(alvo, "frozen", 100) == 0.0

    def test_resistir_a_um_status_nao_protege_de_outro(self):
        def alvo():
            h = _heroi()
            h.resistances["stun"] = 100
            return h

        assert _proporcao_que_pegou(alvo, "stun", 100) == 0.0
        assert _proporcao_que_pegou(alvo, "poison", 100) == 1.0

    def test_heroi_e_monstro_resolvem_igual(self):
        def monstro():
            m = spawn_by_role("bruiser", 8)
            m.resistances["fear"] = 50
            return m

        def heroi():
            h = _heroi()
            h.resistances["fear"] = 50
            return h

        assert _proporcao_que_pegou(monstro, "fear", 60) == _proporcao_que_pegou(heroi, "fear", 60)


class TestDanoEStatusSaoSeparados:
    def test_o_golpe_machuca_mesmo_com_o_status_resistido(self):
        """O exemplo obrigatório: imune a frozen, mas o dano acontece igual."""
        atacante = make_hero("Warrior", 8, "expected")
        normal = spawn_by_role("bruiser", 8)
        imune = spawn_by_role("bruiser", 8)
        imune.resistances["frozen"] = 100

        danos = []
        for alvo in (normal, imune):
            hp = alvo.get_hp()
            cmb.resolve_physical_attack(
                atacante,
                alvo,
                cmb.basic_attack_power(atacante),
                "",
                rng=RngRoteirizado(*ACERTA_SEM_CRIT),
            )
            danos.append(hp - alvo.get_hp())
            # 30% de chance de congelar, com uma rolagem que sempre passaria
            cmb.try_apply_status(alvo, "frozen", 30, 3, RngRoteirizado(1))

        assert danos[0] == danos[1], "a resistência a status mexeu no dano"
        assert "frozen" in normal.active_effects
        assert "frozen" not in imune.active_effects


class TestOsCaminhosDeAplicacao:
    def test_o_stun_extra_da_skill_passa_pelo_resolvedor(self):
        """`investida` e `esmagar` carregam `stun_chance` no JSON."""
        alvo = spawn_by_role("bruiser", 8)
        alvo.resistances["stun"] = 100
        assert cmb._try_apply_stun(alvo, 100, RngRoteirizado(1), None) is False
        assert "stun" not in alvo.active_effects

    def test_a_skill_de_status_passa_pelo_resolvedor(self):
        caster = make_hero("Mage", 8, "expected")
        alvo = spawn_by_role("bruiser", 8)
        skill = next(
            s for s in load_skills() if s.effect_type == "status" and s.effect_value == "frozen"
        )
        alvo.resistances["frozen"] = 100
        resultado = cmb.apply_skill(caster, alvo, skill, rng=RngRoteirizado(1))
        assert resultado.status_success is False
        assert "frozen" not in alvo.active_effects


def test_o_vocabulario_e_o_do_motor():
    """A lista de resistíveis é montada das famílias, não escrita à mão."""
    canonicos = set(fx.negative_statuses())
    assert canonicos == {
        "frozen",
        "stun",
        "sleep",
        "poison",
        "bleed",
        "weakened",
        "fear",
        "mana_burn",
    }
    assert "invisible" not in canonicos, "estado benéfico não é resistível"
    assert "damage_reduction" not in canonicos, "buff que o lançador põe em si mesmo"


# --- equipamento como fonte de resistência -----------------------------------


def _item(slot: str, **resistencias) -> Item:
    """Item de prova. Não entra no catálogo: existe só para exercitar o caminho."""
    return Item(
        item_id=f"prova_{slot.lower()}",
        name=f"Prova {slot}",
        description="",
        slot=slot,
        status_resistances=resistencias,
    )


def _com(heroi, *itens):
    for item in itens:
        heroi.inventory.append(item)
        heroi.equip(item)
    return heroi


class TestEquipamentoContribui:
    def test_um_item_soma(self):
        h = _com(make_hero("Warrior", 8, "naked"), _item("Ring", frozen=50))
        assert h.get_status_resistance("frozen") == 50

    def test_varios_itens_somam(self):
        h = _com(
            make_hero("Warrior", 8, "naked"),
            _item("Ring", frozen=40),
            _item("Amulet", frozen=35),
            _item("Body", frozen=25),
        )
        assert h.get_status_resistance("frozen") == 100

    def test_a_soma_e_capada_em_cem(self):
        """Sem overflow, sem conversão em outro bônus, sem retorno decrescente."""
        h = _com(
            make_hero("Warrior", 8, "naked"),
            _item("Ring", frozen=70),
            _item("Amulet", frozen=60),
        )
        assert h.get_status_resistance("frozen") == 100

    def test_resistencias_nao_vazam_entre_status(self):
        h = _com(make_hero("Warrior", 8, "naked"), _item("Ring", frozen=100))
        assert h.get_status_resistance("frozen") == 100
        for outro in fx.negative_statuses():
            if outro != "frozen":
                assert h.get_status_resistance(outro) == 0, outro

    def test_um_item_pode_dar_mais_de_uma_resistencia(self):
        h = _com(make_hero("Warrior", 8, "naked"), _item("Amulet", frozen=25, stun=15))
        assert h.get_status_resistance("frozen") == 25
        assert h.get_status_resistance("stun") == 15

    def test_desequipar_nao_deixa_residuo(self):
        """A resistência é derivada do equipamento atual, nunca copiada."""
        h = make_hero("Warrior", 8, "naked")
        h.resistances["frozen"] = 10
        anel = _item("Ring", frozen=90)
        _com(h, anel)
        assert h.get_status_resistance("frozen") == 100
        h.unequip("Ring")
        assert h.get_status_resistance("frozen") == 10

    def test_a_resistencia_propria_soma_com_a_do_item(self):
        h = make_hero("Warrior", 8, "naked")
        h.resistances["stun"] = 20
        _com(h, _item("Ring", stun=30))
        assert h.get_status_resistance("stun") == 50


class TestDePontaAPonta:
    def test_anel_de_imunidade_impede_o_status_e_nao_o_dano(self):
        """O caso C: 100% de Frozen no ataque contra 100% de resistência.

        O golpe machuca igual; o congelamento não acontece. É o teste que prova
        que dano e status são resolvidos por caminhos separados.
        """
        atacante = spawn_by_role("bruiser", 8)
        nu = make_hero("Warrior", 8, "naked")
        protegido = _com(make_hero("Warrior", 8, "naked"), _item("Ring", frozen=100))

        danos = []
        for alvo in (nu, protegido):
            hp = alvo.get_hp()
            cmb.resolve_physical_attack(
                atacante,
                alvo,
                cmb.basic_attack_power(atacante),
                "",
                rng=RngRoteirizado(*ACERTA_SEM_CRIT),
            )
            danos.append(hp - alvo.get_hp())
            cmb.try_apply_status(alvo, "frozen", 100, 3, RngRoteirizado(1))

        assert danos[0] == danos[1], "o anel de resistência mexeu no dano"
        assert "frozen" in nu.active_effects
        assert "frozen" not in protegido.active_effects
