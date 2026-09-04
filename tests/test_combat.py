"""Testes unitários de src/mechanics/combat.py — determinísticos (rng injetado/seed fixa)."""

import random
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

from src.mechanics import combat as cmb  # noqa: E402
from src.shared.constants import (  # noqa: E402
    BASE_HIT_CHANCE,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_DAMAGE_BASE,
    DEFENSE_K,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
    POISON_DAMAGE_PER_TICK,
    XMULT_CAP,
)

# ------------------------------------------------------------------ stubs


class StubEntity:
    """Entidade mínima: só o que combat.py toca."""

    def __init__(self, name="A", ag=10, df=20, hp=999, mp=100, classname="Guerreiro"):
        self._name = name
        self._ag = ag
        self._df = df
        self._hp = hp
        self._mp = mp
        self._alive = True
        self._classname = classname
        self.level = 1
        self.active_effects = {}
        self.active_buffs = {}
        self.passive_bonus = {}

    def get_nick_name(self):
        return self._name

    def get_ag(self):
        return self._ag

    def get_df(self):
        return self._df

    def get_hp(self):
        return self._hp

    def get_mp(self):
        return self._mp

    def reduce_mp(self, cost):
        self._mp -= cost

    def heal(self, amount):
        self._hp += amount

    def take_damage(self, amount):
        self._hp -= amount

    def set_isalive(self, state):
        self._alive = state

    def get_isalive(self):
        return self._alive

    def get_classname(self):
        return self._classname

    def get_avg_damage(self):
        return 40

    def get_passive_bonus(self, effect_type):
        return self.passive_bonus.get(effect_type, 0)


class EventRecorder:
    def __init__(self):
        self.events = []

    def __call__(self, topic, event):
        self.events.append((topic, event.type, event.payload))


# ------------------------------------------------------- helpers


def expected_damage(base_power, *, flat=None, mult=None, xmult=None, defense=0):
    """Réplica literal do pipeline de combat.py p/ calcular o valor esperado."""
    flat_total = sum(flat) if flat else 0
    mult_total = 1.0 + sum(mult) if mult else 1.0
    xraw = 1.0
    for v in xmult or []:
        xraw *= v
    xcap = min(xraw, XMULT_CAP)
    dmod = DEFENSE_K / (DEFENSE_K + max(0, defense))
    return max(1, int((base_power + flat_total) * mult_total * xcap * dmod))


def predict_attack_rolls(seed, hit_chance, crit_chance):
    """Replica a sequência de randrange de resolve_physical_attack."""
    r = random.Random(seed)
    roll_hit = r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX)
    roll_crit = r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX)
    return roll_hit <= hit_chance, roll_crit <= crit_chance


# ------------------------------------------- curva hiperbólica de defesa


class TestHyperbolicDefenseMitigation:
    """DEFENSE_MODIFIER = k/(k+defense) — COMBAT_DESIGN.md §5."""

    @pytest.mark.parametrize(
        "defense,expected_mod",
        [
            (0, 1.0),
            (30, 100 / 130),
            (100, 0.5),
            (200, 1 / 3),
            (300, 0.25),
            (500, 100 / 600),
            (1000, 100 / 1100),
        ],
    )
    def test_curva_hiperbolica_valores_da_tabela_do_design(self, defense, expected_mod):
        assert cmb._defense_modifier(defense) == pytest.approx(expected_mod)

    def test_defesa_negativa_e_truncada_para_zero(self):
        # SUSPEITO (decisão defensiva ok, mas não está documentada no design)
        assert cmb._defense_modifier(-50) == 1.0

    def test_dano_nunca_chega_a_zero_mitigacao_via_pipeline_publico(self):
        dmg = cmb._calculate_damage(1000, defense_target=1000)
        assert dmg == int(1000 * (100 / 1100))


# ------------------------------------------------------ teto de XMULT


class TestXmultCap:
    """XMULT Cap 5.0 — COMBAT_DESIGN.md §3.3."""

    def test_produtorio_abaixo_do_teto_passa_intacto(self):
        assert cmb._apply_xmult_cap(1.8) == 1.8

    def test_produtorio_acima_do_teto_e_saturado_em_5(self):
        assert cmb._apply_xmult_cap(6.0) == XMULT_CAP

    def test_full_house_execute_glass_soul_critic_exemplo_do_design(self):
        # 3.0 * 2.0 * 1.8 * 1.5 = 16.2 -> cap 5.0 (exemplo numérico do §3.3)
        raw = cmb._calculate_damage(10, xmult_mods=[3.0, 2.0, 1.8, 1.5])
        assert raw == 10 * 5

    def test_cap_aplicado_antes_da_defesa(self):
        # 100 * (6 -> 5) * 0.5 = 250; sem cap seria 300
        assert cmb._calculate_damage(100, xmult_mods=[3.0, 2.0], defense_target=100) == 250


# -------------------------------------------------- cálculo básico de dano


class TestCalculateDamageBasico:
    def test_atk_def_conhecidos_sem_random(self):
        # 100 ATK vs DEF 0 => 100
        assert cmb._calculate_damage(100) == 100

    def test_pipeline_completo_flat_mult_xmult_defesa(self):
        # (50+25)*(1.5)*(1.0)*(0.5) = 56.25 -> 56
        got = cmb._calculate_damage(
            50, flat_mods=[10, 15], mult_mods=[0.5], xmult_mods=[1.0], defense_target=100
        )
        assert got == 56

    def test_esperado_bate_com_replica_manual(self):
        got = cmb._calculate_damage(
            80, flat_mods=[7], mult_mods=[0.2, -0.1], xmult_mods=[1.3], defense_target=30
        )
        assert got == expected_damage(80, flat=[7], mult=[0.2, -0.1], xmult=[1.3], defense=30)

    def test_atk_zero_produz_dano_minimo_1(self):
        assert cmb._calculate_damage(0) == 1

    def test_def_muito_alta_produz_dano_minimo_1(self):
        assert cmb._calculate_damage(50, defense_target=10**9) == 1

    def test_resultado_e_inteiro_truncado(self):
        # 41.66... -> 41 (trunca, nao arredonda)
        assert cmb._calculate_damage(50, defense_target=20) == 41


# ------------------------------------------------ acerto crítico / resolve


class TestResolvePhysicalAttack:
    BASE, DF = 50, 20

    def _pair(self, ag_a=10, ag_d=10):
        return StubEntity("Atk", ag=ag_a), StubEntity("Def", ag=ag_d, df=self.DF, hp=999)

    def test_miss_seed_fixa_19(self):
        a, d = self._pair()
        res = cmb.resolve_physical_attack(a, d, self.BASE, rng=random.Random(19))
        assert res.was_evaded is True
        assert res.damage == 0
        assert d.get_hp() == 999  # miss não aplica dano

    def test_hit_sem_critico_seed_3_valor_pinned(self):
        a, d = self._pair()
        res = cmb.resolve_physical_attack(a, d, self.BASE, rng=random.Random(3))
        assert res.was_evaded is False
        assert res.was_critical is False
        assert res.damage == 41  # int(50 * 100/120)

    def test_critico_seed_10_valor_pinned(self):
        a, d = self._pair()
        res = cmb.resolve_physical_attack(a, d, self.BASE, rng=random.Random(10))
        assert res.was_critical is True
        assert res.damage == 62  # int(50 * 1.5 * 100/120)

    def test_morte_do_defensor_marca_isalive_false(self):
        a, d = self._pair()
        d._hp = 30
        res = cmb.resolve_physical_attack(a, d, 100, rng=random.Random(3))
        assert res.did_defender_die is True
        assert d.get_isalive() is False

    @pytest.mark.parametrize("seed", range(12))
    def test_consistencia_com_replica_de_rolls_parametrizada(self, seed):
        a, d = self._pair()
        hit, crit = predict_attack_rolls(seed, BASE_HIT_CHANCE, CRIT_CHANCE_DEFAULT)
        res = cmb.resolve_physical_attack(a, d, self.BASE, rng=random.Random(seed))
        assert res.was_evaded is (not hit)
        if hit:
            exp = expected_damage(
                self.BASE, xmult=[CRIT_DAMAGE_BASE] if crit else None, defense=self.DF
            )
            assert (res.damage, res.was_critical) == (exp, crit)

    def test_agility_altera_chance_de_acerto(self):
        # A chance de acerto usa a diferença RELATIVA de agilidade, limitada
        # entre HIT_CHANCE_FLOOR e HIT_CHANCE_CEIL. Ninguém fica imune nem
        # infalível, por maior que seja a diferença de agilidade.
        a_hi, d_low = StubEntity(ag=90), StubEntity(df=20, ag=10)
        a_low, d_hi = StubEntity(ag=10), StubEntity(df=20, ag=95)
        assert cmb.hit_chance(a_hi, d_low) > cmb.hit_chance(a_low, d_hi)
        assert cmb.hit_chance(a_low, d_hi) >= cmb.HIT_CHANCE_FLOOR
        assert cmb.hit_chance(a_hi, d_low) <= cmb.HIT_CHANCE_CEIL

    def test_acerto_e_escala_livre(self):
        # Dois combatentes cujas agilidades crescem juntas mantêm a mesma
        # chance de acerto. É o que impede a classe ágil de virar imune.
        baixo = cmb.hit_chance(StubEntity(ag=8), StubEntity(ag=31))
        alto = cmb.hit_chance(StubEntity(ag=80), StubEntity(ag=310))
        assert baixo == alto

    def test_nenhum_defensor_fica_imune(self):
        # O bug original: AG do monstro fixa em 3 contra AG do Ladino sem teto
        # zerava a chance de acerto a partir do nível 13.
        assert cmb.hit_chance(StubEntity(ag=3), StubEntity(ag=1000)) >= cmb.HIT_CHANCE_FLOOR

    @pytest.mark.parametrize("seed", range(12))
    def test_rogue_ataque_furtivo_usa_crit_chance_high_e_cap_75(self, seed):
        # cc efetivo = min(25 + 200 passivas, 75) = CAP
        rogue = StubEntity("Rog", classname="Rogue")
        rogue.passive_bonus["crit_chance"] = 200
        target = StubEntity(df=0)
        _, crit = predict_attack_rolls(seed, BASE_HIT_CHANCE, CRIT_CHANCE_CAP)
        res = cmb.resolve_physical_attack(
            rogue, target, 40, "Ataque Furtivo", rng=random.Random(seed)
        )
        assert res.was_critical is crit

    def test_evento_publicado_quando_publish_fornecido(self):
        rec = EventRecorder()
        a, d = self._pair()
        cmb.resolve_physical_attack(a, d, self.BASE, rng=random.Random(3), publish=rec)
        assert len(rec.events) == 1
        topic, etype, payload = rec.events[0]
        assert etype == "physical_strike"
        assert payload["strike"].damage == 41

    def test_global_random_seed_tambem_funciona(self):
        random.seed(3)  # sem rng injetado, usa o módulo global
        a, d = self._pair()
        res = cmb.resolve_physical_attack(a, d, self.BASE)
        assert res.damage == 41


# ------------------------------------------------------------ apply_skill


class TestApplySkill:
    def _caster_target(self):
        caster = StubEntity("Caster", mp=100)
        caster.level = 10
        return caster, StubEntity("Target", df=0, hp=500)

    def _skill(self, effect_type, value=30, chance=50, duration=3, mana=20):
        return SimpleNamespace(
            name="Bola de Fogo",
            mana_cost=mana,
            effect_type=effect_type,
            effect_value=value,
            chance=chance,
            duration=duration,
        )

    def test_skill_de_dano_e_percentual_do_poder_base(self):
        caster, target = self._caster_target()
        # effect_value 30 = +30% sobre o poder base 40 -> 52.
        skill = self._skill("damage")
        assert cmb.skill_damage_base(caster, skill) == 52
        res = cmb.apply_skill(caster, target, skill, rng=random.Random(7))
        assert res.kind == "damage"
        assert res.mp_spent == 20
        assert caster.get_mp() == 80

    def test_skill_de_dano_mantem_peso_relativo_entre_niveis(self):
        # Como percentual, a skill vale o mesmo no nível 1 e no nível 20. Como
        # soma fixa, ela anti-escalava e virava ruído no fim do jogo.
        baixo, _ = self._caster_target()
        alto, _ = self._caster_target()
        alto.level = 20
        skill = self._skill("damage")
        assert cmb.skill_damage_base(baixo, skill) == cmb.skill_damage_base(alto, skill)

    def test_skill_de_cura(self):
        caster, target = self._caster_target()
        caster._hp = 100
        res = cmb.apply_skill(caster, target, self._skill("heal", value=45), rng=random.Random(0))
        assert (res.kind, res.heal_amount) == ("heal", 45)
        assert caster.get_hp() == 145

    def test_status_sucesso_aplica_efeito_no_alvo(self):
        caster, target = self._caster_target()
        roll = random.Random(0).randrange(1, 101)
        res = cmb.apply_skill(caster, target, self._skill("status"), rng=random.Random(0))
        sucesso = roll <= 50
        assert res.status_success is sucesso
        if sucesso:
            assert target.active_effects["30"] == {"duration": 3}
        else:
            assert target.active_effects == {}

    def test_buff_registra_no_caster(self):
        caster, target = self._caster_target()
        res = cmb.apply_skill(
            caster, target, self._skill("buff", value=8, duration=2), rng=random.Random(0)
        )
        assert res.kind == "buff"
        assert caster.active_buffs["Bola de Fogo"] == {"stat": "", "value": 8, "duration": 2}
        assert caster.get_mp() == 80

    def test_effect_type_desconhecido_levanta_valueerror(self):
        caster, target = self._caster_target()
        with pytest.raises(ValueError, match="Unknown skill.effect_type"):
            cmb.apply_skill(caster, target, self._skill("teleporte"), rng=random.Random(0))

    def test_eventos_cast_e_outcome_publicados(self):
        rec = EventRecorder()
        caster, target = self._caster_target()
        cmb.apply_skill(caster, target, self._skill("buff"), rng=random.Random(0), publish=rec)
        assert [e[1] for e in rec.events] == ["skill_cast", "skill_outcome"]


# ------------------------------------------------ process_turn_start_effects


class TestProcessTurnStartEffects:
    def test_poison_tick_dano_por_ag_e_duracao(self):
        e = StubEntity(ag=20, hp=100)
        e.active_effects["poison"] = {"duration": 2}
        cmb.process_turn_start_effects(e)
        # POISON_DAMAGE_PER_TICK + ag//5 = 5 + 4 = 9
        assert e.get_hp() == 91
        assert e.active_effects["poison"]["duration"] == 1

    def test_poison_expira_e_remove(self):
        e = StubEntity(ag=0, hp=100)
        e.active_effects["poison"] = {"duration": 1}
        cmb.process_turn_start_effects(e)
        assert "poison" not in e.active_effects
        assert e.get_hp() == 100 - POISON_DAMAGE_PER_TICK

    def test_frozen_pula_turno(self):
        e = StubEntity()
        e.active_effects["frozen"] = {"duration": 1}
        assert cmb.process_turn_start_effects(e) is True

    def test_sem_frozen_retorna_false(self):
        assert cmb.process_turn_start_effects(StubEntity()) is False

    def test_buff_expira(self):
        e = StubEntity()
        e.active_buffs["fúria"] = {"value": 5, "duration": 1}
        cmb.process_turn_start_effects(e)
        assert "fúria" not in e.active_buffs

    def test_entidade_morta_por_tick_marca_isalive_false(self):
        e = StubEntity(hp=3)
        e.active_effects["poison"] = {"duration": 2}
        cmb.process_turn_start_effects(e)
        assert e.get_isalive() is False


# -------------------------------------------------------- roll_flee_success


class TestRollFleeSuccess:
    def test_seeds_pinned(self):
        # FLEE_RANGE_MAX=2 -> sucesso iff randrange(0,2)==0
        assert cmb.roll_flee_success(rng=random.Random(0)) is False
        for s in (1, 2, 3, 4):
            assert cmb.roll_flee_success(rng=random.Random(s)) is True

    def test_com_random_seed_global(self):
        random.seed(1)
        assert cmb.roll_flee_success() is True
