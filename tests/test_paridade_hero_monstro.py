"""Herói e monstro obedecem ao MESMO núcleo de efeitos.

O monstro é outra entidade jogável, controlada por IA. O que muda é a origem do
poder e quem decide — não a gramática. Estes testes percorrem o caminho real
(`apply_skill` / `resolve_physical_attack`) nos dois sentidos, e não chamam o
núcleo na mão: uma paridade que só existe quando o teste aplica o efeito
diretamente não é paridade, é coincidência.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import _skill_from_json, spawn_by_role  # noqa: E402
from src.content.items import Item  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effect_core as core  # noqa: E402


class _Rng:
    """RNG roteirizado: a rolagem 1 passa em qualquer chance maior que zero."""

    def __init__(self, *valores: int) -> None:
        self._v = list(valores) or [1]
        self._i = 0

    def randrange(self, a: int, b: int) -> int:
        v = self._v[min(self._i, len(self._v) - 1)]
        self._i += 1
        return v

    def random(self) -> float:
        return 0.5


def _heroi(nivel: int = 8) -> Warrior:
    h = Warrior("Herói")
    h.level = nivel
    h._hp, h._mp = h.base_hp, h.base_mp
    return h


def _skill_de_heroi(efeito: str):
    """A primeira skill de herói que aplica `efeito`, do catálogo real."""
    return next(s for s in load_skills() if s.effect_type == "status" and s.effect_value == efeito)


def _skill_de_monstro(papel: str, skill_id: str):
    monstro = spawn_by_role(papel, 8)
    return monstro, next(s for s in monstro.skills if s.id == skill_id)


# Skills de status que os arquétipos realmente têm. Veneno não existe como carta
# de monstro no conteúdo de hoje, e é construído pela MESMA fábrica dos
# arquétipos — o caminho é o real, só a carta é que ainda não foi escrita.
SKILLS_REAIS = [
    ("skirmisher", "mob_ferida", "bleed"),
    ("controller", "mob_torpor", "stun"),
    ("controller", "mob_medo", "fear"),
    ("controller", "mob_queima_mana", "mana_burn"),
    ("support", "mob_maldicao", "weakened"),
]


class TestMonstroAplicaNoHeroi:
    @pytest.mark.parametrize("papel,skill_id,efeito", SKILLS_REAIS)
    def test_skill_real_de_monstro_chega_ao_nucleo(self, papel, skill_id, efeito):
        monstro, skill = _skill_de_monstro(papel, skill_id)
        heroi = _heroi()
        cmb.apply_skill(monstro, heroi, skill, rng=_Rng(1))

        instancia = next(i for i in core.instances(heroi) if i.effect == efeito)
        assert isinstance(instancia, core.EffectInstance)
        assert instancia.definition is core.CATALOG[efeito], "outra definição que não a global"
        assert instancia.duration == int(skill.duration)

    def test_poison_pela_mesma_fabrica_de_skill_de_arquetipo(self):
        monstro = spawn_by_role("skirmisher", 8)
        skill = _skill_from_json(
            {
                "id": "mob_veneno",
                "name": "Presas Peçonhentas",
                "effect_type": "status",
                "effect_value": "poison",
                "chance": 100,
                "duration": 4,
                "mana_cost": 10,
                "cooldown": 2,
            }
        )
        heroi = _heroi()
        cmb.apply_skill(monstro, heroi, skill, rng=_Rng(1))
        assert core.has_effect(heroi, "poison")


class TestHeroiAplicaNoMonstro:
    def test_skill_do_heroi_chega_ao_nucleo(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        skill = _skill_de_heroi("poison")
        cmb.apply_skill(heroi, monstro, skill, rng=_Rng(1))
        instancia = next(i for i in core.instances(monstro) if i.effect == "poison")
        assert instancia.definition is core.CATALOG["poison"]

    def test_item_do_heroi_chega_pelo_mesmo_caminho(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        heroi.equip(
            Item(
                item_id="adaga",
                name="Adaga",
                description="prova",
                slot="Weapon",
                damage_bonus=10,
                effect_type="poison",
                effect_value=100,
            )
        )
        cmb.resolve_physical_attack(
            heroi, monstro, cmb.basic_attack_power(heroi), "", rng=_Rng(1, 100)
        )
        assert core.has_effect(monstro, "poison")


class TestMesmaDefinicao:
    def test_o_mesmo_efeito_pelos_dois_lados_e_a_mesma_coisa(self):
        """`weakened` é o único status que o conteúdo tem nos DOIS lados hoje."""
        monstro, skill_monstro = _skill_de_monstro("support", "mob_maldicao")
        heroi = _heroi()
        alvo_monstro = spawn_by_role("bruiser", 8)

        cmb.apply_skill(monstro, heroi, skill_monstro, rng=_Rng(1))
        cmb.apply_skill(heroi, alvo_monstro, _skill_de_heroi("weakened"), rng=_Rng(1))

        no_heroi = next(i for i in core.instances(heroi) if i.effect == "weakened")
        no_monstro = next(i for i in core.instances(alvo_monstro) if i.effect == "weakened")

        assert no_heroi.definition is no_monstro.definition
        assert no_heroi.intensity == no_monstro.intensity
        assert no_heroi.stacks == no_monstro.stacks == 1
        # A única diferença permitida: quem aplicou.
        assert no_heroi.source_id != no_monstro.source_id

    @pytest.mark.parametrize("efeito", ["bleed", "poison"])
    def test_teto_de_stacks_e_o_mesmo_nos_dois(self, efeito):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        for alvo in (heroi, monstro):
            for _ in range(9):
                cmb.try_apply_status(alvo, efeito, 100, 3, _Rng(1), source_id="fonte")
        assert core.stacks_of(heroi, efeito) == core.stacks_of(monstro, efeito) == 5

    def test_tick_e_o_mesmo_nos_dois(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        for alvo in (heroi, monstro):
            core.apply_effect(alvo, "bleed", source_id="fonte", duration=2)
        perdido = {}
        for alvo in (heroi, monstro):
            antes = alvo.get_hp()
            cmb.process_turn_start_effects(alvo)
            perdido[alvo] = (antes - alvo.get_hp()) / alvo.base_hp
        assert perdido[heroi] == pytest.approx(perdido[monstro], abs=0.005)


class TestAtributosNosDois:
    ALVOS = ["heroi", "monstro"]

    def _entidade(self, qual):
        return _heroi() if qual == "heroi" else spawn_by_role("bruiser", 8)

    @pytest.mark.parametrize("quem", ALVOS)
    @pytest.mark.parametrize(
        "positivo,negativo,stat",
        [
            ("empowered", "weakened", "st"),
            ("arcane_surge", "hexed", "mg"),
            ("quickened", "slowed", "ag"),
            ("fortified", "vulnerable", "df"),
        ],
    )
    def test_buff_e_debuff_de_atributo(self, quem, positivo, negativo, stat):
        e = self._entidade(quem)
        base = e.get_stat(stat)
        core.apply_effect(e, positivo, source_id="a", intensity=20)
        assert e.get_stat(stat) > base
        core.apply_effect(e, negativo, source_id="b", intensity=40)
        assert e.get_stat(stat) < base

    @pytest.mark.parametrize("quem", ALVOS)
    def test_piso_de_atributo(self, quem):
        e = self._entidade(quem)
        base = e.get_stat("st")
        core.apply_effect(e, "weakened", source_id="maldição", intensity=300)
        assert e.get_stat("st") == max(1, int(base * core.MIN_ATTRIBUTE_RATIO))

    @pytest.mark.parametrize("quem", ALVOS)
    @pytest.mark.parametrize("efeito,sobe", [("vitality", True), ("frailty", False)])
    def test_teto_de_vida_temporario_e_reversivel(self, quem, efeito, sobe):
        e = self._entidade(quem)
        base = e.base_hp
        core.apply_effect(e, efeito, source_id="fonte", intensity=25, duration=1)
        assert (e.base_hp > base) is sobe
        cmb.process_turn_start_effects(e)
        assert e.base_hp == base, "o teto não voltou"

    @pytest.mark.parametrize("quem", ALVOS)
    def test_teto_de_mana_temporario(self, quem):
        e = self._entidade(quem)
        base = e.base_mp
        core.apply_effect(e, "focused", source_id="fonte", intensity=30)
        assert e.base_mp > base
        core.remove_effect(e, "focused")
        assert e.base_mp == base


class TestMedoNosDois:
    def test_reduz_o_acerto_do_heroi_e_do_monstro(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        antes = {"heroi": cmb.hit_chance(heroi, monstro), "monstro": cmb.hit_chance(monstro, heroi)}
        for atacante in (heroi, monstro):
            core.apply_effect(atacante, "fear", source_id="fonte")
        assert cmb.hit_chance(heroi, monstro) == antes["heroi"] - core.FEAR_ACCURACY_PENALTY
        assert cmb.hit_chance(monstro, heroi) == antes["monstro"] - core.FEAR_ACCURACY_PENALTY

    def test_monstro_amedrontado_erra_mais(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        limite = cmb.hit_chance(monstro, heroi)

        def acertou():
            alvo = _heroi()
            hp = alvo.get_hp()
            cmb.resolve_physical_attack(
                monstro, alvo, cmb.basic_attack_power(monstro), "", rng=_Rng(limite, 100)
            )
            return alvo.get_hp() < hp

        assert acertou(), "premissa: a rolagem no limite acerta sem medo"
        core.apply_effect(monstro, "fear", source_id="heroi")
        assert not acertou()


class TestResistenciaNosDoisSentidos:
    def test_heroi_resistente_bloqueia_a_skill_do_monstro(self):
        monstro, skill = _skill_de_monstro("skirmisher", "mob_ferida")
        heroi = _heroi()
        heroi.resistances = {"bleed": 100}
        cmb.apply_skill(monstro, heroi, skill, rng=_Rng(1))
        assert not core.has_effect(heroi, "bleed")

    def test_monstro_resistente_bloqueia_a_skill_do_heroi(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        monstro.resistances = {"poison": 100}
        cmb.apply_skill(heroi, monstro, _skill_de_heroi("poison"), rng=_Rng(1))
        assert not core.has_effect(monstro, "poison")

    def test_a_formula_e_a_mesma(self):
        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        for e in (heroi, monstro):
            e.resistances = {"poison": 60}
        from src.shared import effects as fx

        assert fx.status_resistance(heroi, "poison") == fx.status_resistance(monstro, "poison")
        assert fx.effective_status_chance(50, 60) == pytest.approx(20.0)


class TestDamageReductionSemCaminhoExclusivo:
    """A última mecânica com representação só-de-monstro."""

    def test_skill_de_monstro_escreve_onde_o_buff_do_heroi_escreve(self):
        monstro, skill = _skill_de_monstro("tank", "mob_carapaca")
        cmb.apply_skill(monstro, monstro, skill, rng=random.Random(0))
        assert skill.name in monstro.active_buffs
        assert "damage_reduction" not in monstro.active_effects

    def test_heroi_e_monstro_reduzem_dano_pela_mesma_leitura(self):
        from src.shared import effects as fx

        heroi, monstro = _heroi(), spawn_by_role("bruiser", 8)
        for e in (heroi, monstro):
            e.active_buffs["Guarda"] = {
                "stat": "damage_reduction",
                "value": 30,
                "duration": 3,
            }
        assert fx.incoming_damage_multiplier(heroi) == fx.incoming_damage_multiplier(monstro)
        assert fx.incoming_damage_multiplier(heroi) == pytest.approx(0.7)

    def test_expira_pelo_mesmo_ciclo_de_buff(self):
        monstro, skill = _skill_de_monstro("tank", "mob_carapaca")
        cmb.apply_skill(monstro, monstro, skill, rng=random.Random(0))
        for _ in range(int(skill.duration) + 1):
            cmb.process_turn_start_effects(monstro)
        assert skill.name not in monstro.active_buffs
