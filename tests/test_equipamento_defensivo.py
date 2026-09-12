"""O primeiro canal defensivo de equipamento: `evasion` e `damage_reduction`.

O catálogo tem 58 itens de equipamento declarando um `effect_type` que nada lê
quando o item está equipado. Abrir um canal genérico acordaria os 58 de uma vez,
sem ninguém ter medido o que isso faz — que é exatamente como eles viraram
placebo. Então o canal nasce com lista de permissão, e esta suíte protege as
duas pontas: que os dois efeitos permitidos funcionam, e que os outros não.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.items import Item  # noqa: E402
from src.content.passives import PassiveCard  # noqa: E402
from src.entities.heroes import Player, Warrior  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effects as fx  # noqa: E402


class _RngRoteirizado:
    """RNG determinístico: devolve a sequência dada, repetindo o último valor."""

    def __init__(self, *valores: int) -> None:
        self._v = list(valores) or [1]
        self._i = 0

    def randrange(self, a: int, b: int) -> int:
        valor = self._v[min(self._i, len(self._v) - 1)]
        self._i += 1
        return valor

    def random(self) -> float:
        return 0.5


def _item(efeito: str, valor: int, slot: str = "Ring") -> Item:
    return Item(
        item_id=f"prova_{efeito}",
        name=f"Prova de {efeito}",
        description="item construído no teste",
        slot=slot,
        effect_type=efeito,
        effect_value=valor,
    )


def _passiva(efeito: str, valor: int) -> PassiveCard:
    return PassiveCard(
        id=f"prova_{efeito}",
        name=f"Passiva de {efeito}",
        category="Combate",
        rarity="Rare",
        description="passiva construída no teste",
        effect_type=efeito,
        effect_value=valor,
    )


def _heroi() -> Warrior:
    h = Warrior("Prova")
    h.level = 8
    h._hp = h.base_hp
    h._mp = h.base_mp
    return h


class TestEvasion:
    """Evasão de item entra na mesma subtração que buff e passiva já usavam."""

    def test_item_baixa_a_chance_de_acerto_e_devolve_ao_desequipar(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        antes = cmb.hit_chance(m, h)

        h.equip(_item("evasion", 8))
        assert h.get_equipment_bonus("evasion") == 8
        assert cmb.hit_chance(m, h) == antes - 8

        h.unequip("Ring")
        assert h.get_equipment_bonus("evasion") == 0
        assert cmb.hit_chance(m, h) == antes, "desequipar deixou resíduo"

    def test_evasao_e_derivada_nunca_copiada(self):
        """Trocar o item troca o valor: nada foi gravado no personagem."""
        h = _heroi()
        h.equip(_item("evasion", 8))
        h.unequip("Ring")
        h.equip(_item("evasion", 3))
        assert h.get_equipment_bonus("evasion") == 3

    def test_respeita_o_piso_que_ja_existia(self):
        """`HIT_CHANCE_FLOOR` já é o teto de evasão. Não criamos um segundo."""
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equipment["Ring"] = _item("evasion", 500)
        assert cmb.hit_chance(m, h) == cmb.HIT_CHANCE_FLOOR

    def test_varios_slots_somam(self):
        h = _heroi()
        h.equip(_item("evasion", 4, "Ring"))
        h.equip(_item("evasion", 6, "Helmet"))
        h.equip(_item("evasion", 2, "Shoes"))
        assert h.get_equipment_bonus("evasion") == 12


class TestDamageReduction:
    """Redução de item chega ao bucket `mitigation`, não a uma multiplicação nova."""

    def _dano(self, atacante, defensor) -> int:
        base = cmb.basic_attack_power(atacante)
        mods = cmb.damage_modifiers(atacante, defensor, is_critical=False)
        return cmb._calculate_damage(
            base_power=float(base),
            flat_mods=mods.flat,
            mult_mods=mods.mult,
            xmult_mods=mods.xmult,
            defense_target=defensor.get_df(),
            mitigation=mods.mitigation,
        )

    def test_item_reduz_o_dano_recebido(self):
        m = spawn_by_role("bruiser", 8)
        nu, protegido = _heroi(), _heroi()
        protegido.equip(_item("damage_reduction", 20, "Body"))
        assert self._dano(m, protegido) < self._dano(m, nu)

    def test_o_item_passa_pelo_mesmo_caminho_que_a_passiva(self):
        """Prova de que não há multiplicação paralela: mesmo valor, mesmo dano."""
        m = spawn_by_role("bruiser", 8)
        por_item, por_passiva = _heroi(), _heroi()
        por_item.equip(_item("damage_reduction", 20, "Body"))
        por_passiva.add_passive_load(_passiva("damage_reduction", 20))
        assert self._dano(m, por_item) == self._dano(m, por_passiva)

    def test_respeita_o_cap_de_80_que_ja_existia(self):
        h = _heroi()
        h.equip(_item("damage_reduction", 200, "Body"))
        assert fx.incoming_damage_multiplier(h) == pytest.approx(0.2)

    def test_desequipar_devolve_o_dano(self):
        m = spawn_by_role("bruiser", 8)
        h = _heroi()
        antes = self._dano(m, h)
        h.equip(_item("damage_reduction", 20, "Body"))
        h.unequip("Body")
        assert self._dano(m, h) == antes


class TestComposicao:
    """Buff, passiva e equipamento são fontes SEPARADAS que somam."""

    @pytest.mark.parametrize("efeito", ["evasion", "damage_reduction", "crit_chance", "life_steal"])
    def test_as_tres_fontes_somam(self, efeito):
        h = _heroi()
        h.active_buffs["Buff de Prova"] = {"stat": efeito, "value": 5, "duration": 3}
        h.add_passive_load(_passiva(efeito, 7))
        h.equip(_item(efeito, 9, "Body"))
        assert fx.combat_modifier(h, efeito) == 21.0

    def test_equipamento_nao_se_disfarca_de_passiva(self):
        """O item soma pelo canal dele. `get_passive_bonus` não sabe dele."""
        h = _heroi()
        h.equip(_item("evasion", 9))
        assert h.get_passive_bonus("evasion") == 0.0
        assert h.get_equipment_bonus("evasion") == 9.0


class TestCritico:
    """`crit_chance` e `crit_damage` chegam pelo canal, sem fórmula nova."""

    def test_item_aumenta_a_chance_real_de_critico(self):
        """Rolagem 30: fora do padrão (10), dentro do que o anel promete (10+50)."""
        rolagem = (1, 30)
        danos = []
        for h in (_heroi(), _heroi()):
            if danos:  # o segundo herói leva o anel
                h.equip(_item("crit_chance", 50))
            m = spawn_by_role("bruiser", 8)
            hp = m.get_hp()
            cmb.resolve_physical_attack(
                h, m, cmb.basic_attack_power(h), "", rng=_RngRoteirizado(*rolagem)
            )
            danos.append(hp - m.get_hp())
        assert danos[1] > danos[0], "o anel não converteu a rolagem 30 em crítico"

    def test_item_de_crit_damage_engorda_o_critico_pelo_xmult(self):
        nu, com_anel = _heroi(), _heroi()
        com_anel.equip(_item("crit_damage", 40))

        def golpe(h):
            m = spawn_by_role("bruiser", 8)
            hp = m.get_hp()
            cmb.resolve_physical_attack(
                h, m, cmb.basic_attack_power(h), "", rng=_RngRoteirizado(1, 1)
            )
            return hp - m.get_hp()

        assert golpe(com_anel) > golpe(nu)
        # E entra no bucket certo: `xmult`, não um multiplicador solto.
        m = spawn_by_role("bruiser", 8)
        mods = cmb.damage_modifiers(com_anel, m, is_critical=True)
        assert mods.xmult == [pytest.approx(cmb.CRIT_DAMAGE_BASE + 0.40)]
        assert mods.flat == [] and mods.mult == []

    def test_o_cap_de_chance_critica_continua_valendo(self):
        h = _heroi()
        h.equip(_item("crit_chance", 500))
        chance = min(
            cmb.CRIT_CHANCE_DEFAULT + int(fx.combat_modifier(h, "crit_chance")), cmb.CRIT_CHANCE_CAP
        )
        assert chance == cmb.CRIT_CHANCE_CAP


class TestLifeSteal:
    """Cura depois do dano causado, no ponto do combate que já existia."""

    def test_item_cura_o_atacante(self):
        nu, com_anel = _heroi(), _heroi()
        com_anel.equip(_item("life_steal", 25))
        for h in (nu, com_anel):
            h._hp = h.base_hp // 2
        antes = {id(h): h.get_hp() for h in (nu, com_anel)}
        for h in (nu, com_anel):
            m = spawn_by_role("bruiser", 8)
            cmb.resolve_physical_attack(
                h, m, cmb.basic_attack_power(h), "", rng=_RngRoteirizado(1, 100)
            )
        assert nu.get_hp() == antes[id(nu)], "sem item não devia curar"
        assert com_anel.get_hp() > antes[id(com_anel)]

    def test_nao_cura_quando_o_golpe_erra(self):
        """A cura depende do dano, e é isso que a ordem do combate já garantia."""
        h = _heroi()
        h.equip(_item("life_steal", 25))
        h._hp = h.base_hp // 2
        antes = h.get_hp()
        m = spawn_by_role("bruiser", 8)
        cmb.resolve_physical_attack(h, m, cmb.basic_attack_power(h), "", rng=_RngRoteirizado(100))
        assert h.get_hp() == antes


class TestManaRegen:
    """Mesmo consumidor que buff e poção já usavam: o início do turno."""

    def test_item_aumenta_o_mp_recuperado_no_turno(self):
        nu, com_cajado = _heroi(), _heroi()
        com_cajado.equip(_item("mana_regen", 20, "Weapon"))
        for h in (nu, com_cajado):
            h._mp = 0
            cmb.process_turn_start_effects(h)
        assert com_cajado.get_mp() == nu.get_mp() + 20

    def test_nao_passa_do_teto_de_mana(self):
        h = _heroi()
        h.equip(_item("mana_regen", 9999, "Weapon"))
        cmb.process_turn_start_effects(h)
        assert h.get_mp() == h.base_mp


class TestDeathIgnore:
    """Binário por combate, e agora a regra pergunta pela mecânica, não pela fonte."""

    def _golpe_letal(self, h, m):
        h._hp = 1
        cmb.resolve_physical_attack(
            m, h, cmb.basic_attack_power(m) * 50, "", rng=_RngRoteirizado(1, 100)
        )

    def test_item_sozinho_salva_uma_vez(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equip(_item("death_ignore", 1, "Amulet"))
        self._golpe_letal(h, m)
        assert h.get_isalive() and h.get_hp() == 1

    def test_o_segundo_golpe_letal_no_mesmo_combate_mata(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equip(_item("death_ignore", 1, "Amulet"))
        self._golpe_letal(h, m)
        self._golpe_letal(h, m)
        assert not h.get_isalive()

    def test_dois_itens_nao_dao_duas_vidas(self):
        """O teste é `> 0`, não uma soma: `death_ignore` não empilha."""
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equip(_item("death_ignore", 1, "Amulet"))
        h.equip(_item("death_ignore", 1, "Ring"))
        assert fx.combat_modifier(h, "death_ignore") == 2.0, "premissa: as fontes somam"
        self._golpe_letal(h, m)
        self._golpe_letal(h, m)
        assert not h.get_isalive(), "dois amuletos deram duas ressurreições"

    def test_sem_o_efeito_o_golpe_letal_mata(self):
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        self._golpe_letal(h, m)
        assert not h.get_isalive()


class TestAtivacaoControlada:
    """O canal não pode acordar família que não foi aprovada nesta rodada."""

    # Backlog consciente: on-hit precisa de resolução de proc, e os dois últimos
    # não têm mecânica nenhuma. Ver KNOWN_BACKLOG em test_data_integrity.
    NAO_ATIVADOS = ["stun", "bleed", "poison", "fear", "true_damage", "armageddon"]

    @pytest.mark.parametrize("efeito", NAO_ATIVADOS)
    def test_continua_placebo(self, efeito):
        h = _heroi()
        h.equip(_item(efeito, 50))
        assert h.get_equipment_bonus(efeito) == 0.0
        assert fx.combat_modifier(h, efeito) == 0.0

    def test_efeito_on_hit_nao_aplica_status_no_alvo(self):
        """O caso completo: uma arma de `stun` não atordoa ninguém ainda."""
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        h.equip(_item("stun", 100, "Weapon"))
        for _ in range(20):
            cmb.resolve_physical_attack(
                h, m, cmb.basic_attack_power(h), "", rng=_RngRoteirizado(1, 100)
            )
        assert "stun" not in m.active_effects

    def test_a_lista_de_permissao_e_exatamente_esta(self):
        """Se alguém acrescentar uma família, que seja de propósito e visível."""
        assert Player.EQUIP_COMBAT_EFFECTS == frozenset(
            {
                "evasion",
                "damage_reduction",
                "crit_chance",
                "crit_damage",
                "life_steal",
                "mana_regen",
                "death_ignore",
            }
        )


class TestProvaDeCarga:
    """Se a agregação sumir, estes testes precisam falhar."""

    @pytest.mark.parametrize("efeito", ["evasion", "damage_reduction"])
    def test_sem_a_lista_de_permissao_o_item_volta_a_valer_zero(self, efeito, monkeypatch):
        h = _heroi()
        h.equip(_item(efeito, 9, "Body"))
        assert fx.combat_modifier(h, efeito) == 9.0
        monkeypatch.setattr(Player, "EQUIP_COMBAT_EFFECTS", frozenset())
        assert fx.combat_modifier(h, efeito) == 0.0


class TestDodgeChanceFoiConsolidado:
    """`dodge_chance` e `evasion` eram a mesma mecânica em duas linhas seguidas."""

    def test_o_nome_saiu_do_vocabulario(self):
        assert "dodge_chance" not in fx.COMBAT_MODIFIERS
        assert "evasion" in fx.COMBAT_MODIFIERS

    def test_a_passiva_migrou_sem_mudar_de_valor(self):
        from src.content.passives import get_passive_by_id

        p = get_passive_by_id("reflexos_rapidos")
        assert p is not None and p.effect_type == "evasion" and p.effect_value == 8

    def test_a_passiva_entrega_os_mesmos_8_pontos_de_antes(self):
        """Valor gravado contra o motor ANTES da consolidação."""
        h, m = _heroi(), spawn_by_role("bruiser", 8)
        nu = cmb.hit_chance(m, h)
        h.add_passive_load(_passiva("evasion", 8))
        assert cmb.hit_chance(m, h) == nu - 8
