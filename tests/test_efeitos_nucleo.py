"""Os contratos do núcleo de efeitos.

A fonte declara intenção; o catálogo diz o que o efeito é; o núcleo decide se
entra, como empilha, quanto dura e como termina. Estes testes travam as regras
que nenhuma fonte pode reimplementar por conta própria.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.enchantments import create_enchantment  # noqa: E402
from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.items import Item  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effect_core as core  # noqa: E402


class _Rng:
    """RNG roteirizado: devolve a sequência dada, repetindo o último valor."""

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
    h = Warrior("Prova")
    h.level = nivel
    h._hp = h.base_hp
    h._mp = h.base_mp
    return h


class TestCatalogo:
    def test_todo_efeito_tem_familia_e_regra(self):
        for d in core.CATALOG.values():
            assert d.family and d.stack_rule, d.effect_id
            assert d.default_duration >= 1, d.effect_id

    def test_pares_opostos_apontam_um_para_o_outro(self):
        for a, b in core.OPPOSING_PAIRS.items():
            assert core.OPPOSING_PAIRS[b] == a
            assert core.CATALOG[a].stat == core.CATALOG[b].stat
            assert core.CATALOG[a].positive is not core.CATALOG[b].positive

    def test_o_catalogo_cobre_ataque_e_defesa(self):
        """A filosofia em dados: para cada amplificação, a redução oposta."""
        for stat in ("st", "mg", "ag", "df", "hp", "mp"):
            do_atributo = [
                d for d in core.CATALOG.values() if d.stat == stat and d.family != "drain"
            ]
            assert any(d.positive for d in do_atributo), stat
            assert any(not d.positive for d in do_atributo), stat


class TestAtributos:
    def test_buff_e_debuff_opostos_se_compensam(self):
        h = _heroi()
        base = h.base_st
        core.apply_effect(h, "empowered", source_id="skill", intensity=20)
        core.apply_effect(h, "weakened", source_id="monstro", intensity=15)
        assert core.attribute_percent(h, "st") == pytest.approx(5.0)
        assert h.base_st == int(base * 1.05)

    def test_fontes_diferentes_acumulam(self):
        h = _heroi()
        core.apply_effect(h, "empowered", source_id="skill", intensity=10)
        core.apply_effect(h, "empowered", source_id="equipamento", intensity=15)
        core.apply_effect(h, "empowered", source_id="passiva", intensity=5)
        assert core.attribute_percent(h, "st") == pytest.approx(30.0)

    def test_a_mesma_fonte_nao_stacka_infinitamente(self):
        """Reaplicar a mesma skill renova a contribuição dela, não empilha."""
        h = _heroi()
        for _ in range(6):
            core.apply_effect(h, "empowered", source_id="Grito de Guerra", intensity=10)
        assert core.attribute_percent(h, "st") == pytest.approx(10.0)

    def test_reaplicar_renova_a_duracao(self):
        h = _heroi()
        core.apply_effect(h, "empowered", source_id="skill", intensity=10, duration=1)
        core.apply_effect(h, "empowered", source_id="skill", intensity=10, duration=4)
        assert core.instances(h, core.FAMILY_ATTRIBUTE)[0].duration == 4

    @pytest.mark.parametrize(
        "efeito,stat", [("weakened", "st"), ("hexed", "mg"), ("slowed", "ag"), ("vulnerable", "df")]
    )
    def test_piso_de_dez_por_cento(self, efeito, stat):
        h = _heroi()
        base = getattr(h, f"base_{stat}")
        core.apply_effect(h, efeito, source_id="maldição", intensity=150)
        resolvido = getattr(h, f"base_{stat}")
        assert resolvido == max(1, int(base * core.MIN_ATTRIBUTE_RATIO))
        assert resolvido > 0, "nenhum debuff pode zerar um atributo"

    def test_o_piso_vale_para_o_monstro_tambem(self):
        m = spawn_by_role("bruiser", 8)
        base = m.get_st()
        core.apply_effect(m, "weakened", source_id="heroi", intensity=200)
        assert m.get_st() == max(1, int(base * core.MIN_ATTRIBUTE_RATIO))


class TestRecursoTemporario:
    """Teto de HP/MP sobe e desce, e volta exatamente ao normal."""

    def test_vitality_sobe_e_devolve_o_teto(self):
        h = _heroi()
        base = h.base_hp
        core.apply_effect(h, "vitality", source_id="poção", intensity=20, duration=1)
        assert h.base_hp == int(base * 1.2)
        cmb.process_turn_start_effects(h)
        assert h.base_hp == base, "o teto não voltou"

    def test_frailty_desce_e_devolve_o_teto(self):
        h = _heroi()
        base = h.base_hp
        core.apply_effect(h, "frailty", source_id="maldição", intensity=25, duration=1)
        assert h.base_hp < base
        cmb.process_turn_start_effects(h)
        assert h.base_hp == base

    def test_frailty_nao_deixa_perda_permanente_de_vida_atual(self):
        """Sair do efeito não cura, e entrar nele não mata.

        A regra: o HP ATUAL nunca é tocado pelo teto. Encolher o teto abaixo do
        atual apenas prende o atual no teto novo (o herói não morre de susto), e
        voltar não devolve vida — se devolvesse, aplicar e remover fragilidade em
        laço seria uma poção infinita.
        """
        h = _heroi()
        base = h.base_hp
        core.apply_effect(h, "frailty", source_id="maldição", intensity=50, duration=1)
        h._hp = min(h._hp, h.base_hp)
        durante = h.get_hp()
        cmb.process_turn_start_effects(h)
        assert h.base_hp == base
        assert h.get_hp() == durante, "sair do efeito curou de graça"

    def test_focused_e_clouded_mexem_no_teto_de_mana(self):
        h = _heroi()
        base = h.base_mp
        core.apply_effect(h, "focused", source_id="poção", intensity=30)
        assert h.base_mp > base
        core.remove_effect(h, "focused")
        assert h.base_mp == base
        core.apply_effect(h, "clouded", source_id="maldição", intensity=30)
        assert h.base_mp < base


class TestDoT:
    @pytest.mark.parametrize("efeito", ["bleed", "poison"])
    def test_stacka_ate_cinco(self, efeito):
        h = _heroi()
        for _ in range(9):
            core.apply_effect(h, efeito, source_id="arma")
        assert core.stacks_of(h, efeito) == 5

    def test_bleed_e_poison_tem_identidades_diferentes(self):
        """Não podem ser 'X dano por turno' com nomes diferentes."""
        sangue, veneno = core.definition("bleed"), core.definition("poison")
        assert sangue.default_intensity > veneno.default_intensity, "sangramento é o forte"
        assert sangue.default_duration < veneno.default_duration, "veneno é o longo"

    def test_nova_aplicacao_tambem_renova_a_duracao(self):
        h = _heroi()
        core.apply_effect(h, "bleed", source_id="arma", duration=1)
        core.apply_effect(h, "bleed", source_id="arma", duration=3)
        instancia = core.instances(h, core.FAMILY_DOT)[0]
        assert (instancia.stacks, instancia.duration) == (2, 3)

    def test_dano_escala_com_os_stacks(self):
        h = _heroi()
        core.apply_effect(h, "bleed", source_id="arma")
        um = core.dot_damage(h, "bleed", h.base_hp)
        core.apply_effect(h, "bleed", source_id="arma")
        assert core.dot_damage(h, "bleed", h.base_hp) == pytest.approx(um * 2, abs=1)


class TestControle:
    @pytest.mark.parametrize("efeito", ["stun", "frozen", "sleep"])
    def test_renova_e_nao_stacka(self, efeito):
        h = _heroi()
        for _ in range(5):
            core.apply_effect(h, efeito, source_id="skill", duration=2)
        assert core.stacks_of(h, efeito) == 1
        assert core.instances(h, core.FAMILY_CONTROL)[0].duration == 2

    def test_sleep_continua_quebrando_ao_levar_dano(self):
        h = _heroi()
        core.apply_effect(h, "sleep", source_id="skill")
        core.apply_effect(h, "stun", source_id="skill")
        assert core.break_on_damage(h) == ["sleep"]
        assert core.has_effect(h, "stun"), "atordoamento não quebra com dano"

    def test_varios_status_convivem(self):
        h = _heroi()
        for efeito in ("bleed", "poison", "fear", "weakened", "stun"):
            core.apply_effect(h, efeito, source_id="monstro")
        assert all(core.has_effect(h, e) for e in ("bleed", "poison", "fear", "weakened", "stun"))


class TestMedo:
    """Medo não reduz Agilidade nem dano: reduz a confiabilidade ofensiva."""

    def test_afeta_o_ataque_basico(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        antes = cmb.hit_chance(h, m)
        core.apply_effect(h, "fear", source_id="monstro")
        assert cmb.hit_chance(h, m) == antes - core.FEAR_ACCURACY_PENALTY

    def test_nao_mexe_na_agilidade_nem_no_dano(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        ag, poder = h.get_ag(), cmb.basic_attack_power(h)
        core.apply_effect(h, "fear", source_id="monstro")
        assert h.get_ag() == ag
        assert cmb.basic_attack_power(h) == poder
        mods = cmb.damage_modifiers(h, m, is_critical=False)
        assert all(v == 1.0 for v in mods.mitigation)

    def test_afeta_a_skill_ofensiva(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        skill = next(s for s in load_skills() if s.effect_type == "damage")

        def acertou(rolagem):
            alvo = spawn_by_role("bruiser", 8)
            hp = alvo.get_hp()
            cmb.resolve_physical_attack(
                h, alvo, cmb.skill_damage_base(h, skill, alvo), skill.name, rng=_Rng(rolagem, 100)
            )
            return alvo.get_hp() < hp

        limite = cmb.hit_chance(h, m)
        assert acertou(limite), "premissa: a rolagem no limite acerta sem medo"
        core.apply_effect(h, "fear", source_id="monstro")
        assert not acertou(limite), "com medo, a mesma rolagem devia errar"

    def test_nao_afeta_buff_nem_cura(self):
        """Buff e cura não passam por `hit_chance`, então o medo não os alcança."""
        h = _heroi()
        core.apply_effect(h, "fear", source_id="monstro")
        h._hp = h.base_hp // 2
        cura = next(s for s in load_skills() if s.effect_type == "heal")
        antes = h.get_hp()
        cmb.apply_skill(h, h, cura, rng=random.Random(0))
        assert h.get_hp() > antes

        buff = next(s for s in load_skills() if s.effect_type == "buff")
        res = cmb.apply_skill(h, h, buff, rng=random.Random(0))
        assert res.buff_name == buff.name


class TestResistencia:
    def test_cem_por_cento_bloqueia(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.resistances = {"bleed": 100}
        assert (
            cmb.try_apply_status(h, "bleed", 100, 3, _Rng(1), source_id=m.get_nick_name()) is False
        )
        assert not core.has_effect(h, "bleed")

    def test_resistencia_nao_reduz_a_intensidade(self):
        """Ela age na CHANCE de entrar, nunca no tamanho do que entrou."""
        h = _heroi()
        h.resistances = {"bleed": 50}
        cmb.try_apply_status(h, "bleed", 100, 3, _Rng(1))
        assert core.has_effect(h, "bleed")
        instancia = core.instances(h, core.FAMILY_DOT)[0]
        assert instancia.intensity == core.definition("bleed").default_intensity


class TestFontesDiferentesMesmoResolver:
    """Item, encantamento e skill aplicam o MESMO bleed global."""

    def _arma(self, effect_type: str, valor: int) -> Item:
        return Item(
            item_id="arma",
            name="Arma",
            description="prova",
            slot="Weapon",
            damage_bonus=10,
            effect_type=effect_type,
            effect_value=valor,
        )

    def test_item_aplica_pelo_catalogo(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equip(self._arma("bleed", 100))
        cmb.resolve_physical_attack(h, m, cmb.basic_attack_power(h), "", rng=_Rng(1, 100))
        instancia = core.instances(m, core.FAMILY_DOT)[0]
        assert instancia.effect == "bleed"
        assert instancia.duration == core.definition("bleed").default_duration

    def test_encantamento_aplica_pelo_mesmo_caminho(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        arma = self._arma(None, 0)
        arma.enchant(create_enchantment("poison_chance", 100))
        h.equip(arma)
        cmb.resolve_physical_attack(h, m, cmb.basic_attack_power(h), "", rng=_Rng(1, 100))
        assert core.has_effect(m, "poison")

    def test_item_e_skill_produzem_a_mesma_instancia(self):
        por_item, por_skill = spawn_by_role("bruiser", 8), spawn_by_role("bruiser", 8)
        h = _heroi()
        h.equip(self._arma("bleed", 100))
        cmb.resolve_physical_attack(h, por_item, cmb.basic_attack_power(h), "", rng=_Rng(1, 100))
        cmb.try_apply_status(por_skill, "bleed", 100, 2, _Rng(1), source_id="skill_corte")

        a = core.instances(por_item, core.FAMILY_DOT)[0]
        b = core.instances(por_skill, core.FAMILY_DOT)[0]
        assert a.effect == b.effect == "bleed"
        assert a.intensity == b.intensity, "a mecânica é do catálogo, não da fonte"
        assert a.source_id != b.source_id, "mas a origem continua registrada"

    def test_a_fonte_pode_escolher_duracao_e_intensidade(self):
        h = _heroi()
        core.apply_effect(h, "bleed", source_id="chefe", intensity=12, duration=6)
        instancia = core.instances(h, core.FAMILY_DOT)[0]
        assert (instancia.intensity, instancia.duration) == (12.0, 6)
