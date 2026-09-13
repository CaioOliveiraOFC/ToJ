"""Encantamentos: a terceira dimensão, e a prova de que ela não toca as outras.

    +N            multiplica a base da PEÇA
    Gema          soma percentual de ATRIBUTO
    Encantamento  altera o MODIFICADOR de combate

Três campos, três caminhos, três perguntas diferentes. Estes testes travam a
separação nos dois sentidos, porque é ela que permite responder de onde veio
cada ponto de poder.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.enchantments import (  # noqa: E402
    ENCHANT_EFFECTS,
    MAX_ENCHANTMENTS,
    Enchantment,
    create_enchantment,
)
from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.gems import create_gem  # noqa: E402
from src.content.items import Item, get_all_items  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effects as fx  # noqa: E402


def _item(nome: str, **kw) -> Item:
    kw.setdefault("slot", "Weapon")
    return Item(item_id=nome, name=nome, description="prova", **kw)


def _heroi_com(peca) -> Warrior:
    h = Warrior("Prova")
    h.level = 8
    h.equip(peca)
    return h


class TestSocketsSoEmEquipavel:
    """Micro-fix: poção não tem onde cravar uma gema."""

    def test_consumivel_raro_nasce_sem_socket(self):
        import random

        r = random.Random(5)
        pocao = next(
            i for i in get_all_items().values() if i.consumable and i.rarity in ("Rare", "Epic")
        )
        assert {pocao.spawn(r).socket_count for _ in range(300)} == {0}

    def test_equipavel_da_mesma_raridade_continua_recebendo(self):
        import random

        r = random.Random(5)
        arma = next(i for i in get_all_items().values() if i.rarity == "Epic" and i.slot)
        assert max(arma.spawn(r).socket_count for _ in range(300)) > 0


class TestEncantamento:
    def test_efeito_desconhecido_levanta(self):
        with pytest.raises(ValueError):
            Enchantment("teletransporte", 10)

    def test_valor_precisa_ser_positivo(self):
        with pytest.raises(ValueError):
            Enchantment("crit_chance", 0)

    def test_nao_tem_escada_propria(self):
        """`+N` é exclusivo de equipamento; encantamento se troca, não se sobe."""
        encanto = create_enchantment("crit_chance", 5)
        assert not hasattr(encanto, "enhancement_level")
        assert not hasattr(encanto, "level")


class TestAPI:
    def test_adicionar_ate_o_teto_e_depois_substituir(self):
        peca = _item("Espada")
        for i in range(MAX_ENCHANTMENTS):
            assert peca.enchant(create_enchantment("crit_chance", i + 1)) is None
        assert len(peca.enchantments) == MAX_ENCHANTMENTS
        # Cheio: substitui o primeiro e devolve quem saiu.
        saiu = peca.enchant(create_enchantment("life_steal", 9))
        assert saiu.effect == "crit_chance" and saiu.value == 1
        assert len(peca.enchantments) == MAX_ENCHANTMENTS

    def test_substituir_por_indice_devolve_o_anterior(self):
        peca = _item("Espada")
        antigo = create_enchantment("crit_chance", 5)
        peca.enchant(antigo)
        assert peca.enchant(create_enchantment("crit_chance", 20), 0) is antigo
        assert peca.enchantments == [peca.enchantments[0]]
        assert peca.enchantment_bonus("crit_chance") == 20

    def test_remover_nao_deixa_residuo(self):
        peca = _item("Espada")
        a, b = create_enchantment("crit_chance", 5), create_enchantment("life_steal", 8)
        peca.enchant(a)
        peca.enchant(b)
        assert peca.disenchant(0) is a
        assert peca.enchantments == [b]
        assert peca.enchantment_bonus("crit_chance") == 0
        assert peca.enchantment_bonus("life_steal") == 8

    def test_remover_posicao_inexistente_devolve_none(self):
        assert _item("Espada").disenchant(3) is None

    def test_dois_exemplares_iguais_com_encantamentos_diferentes(self):
        definicao = get_all_items()["Espada Longa"]
        a, b = definicao.instance(), definicao.instance()
        a.enchant(create_enchantment("crit_chance", 5))
        b.enchant(create_enchantment("life_steal", 8))
        assert a.enchantment_bonus("crit_chance") == 5
        assert b.enchantment_bonus("crit_chance") == 0
        assert get_all_items()["Espada Longa"].enchantments == [], "o catálogo foi alterado"


class TestChegaAoMotor:
    """Cada efeito precisa chegar ao canal certo — nenhum pode ser placebo."""

    @pytest.mark.parametrize(
        "efeito", ["crit_chance", "crit_damage", "damage_reduction", "life_steal", "evasion"]
    )
    def test_efeito_soma_em_combat_modifier(self, efeito):
        peca = _item("Espada")
        peca.enchant(create_enchantment(efeito, 12))
        h = _heroi_com(peca)
        assert fx.combat_modifier(h, efeito) == 12.0

    def test_mana_regen_chega_ao_inicio_do_turno(self):
        peca = _item("Cajado")
        peca.enchant(create_enchantment("mana_regen", 20))
        nu, encantado = Warrior("A"), _heroi_com(peca)
        nu.level = 8
        for h in (nu, encantado):
            h._mp = 0
            cmb.process_turn_start_effects(h)
        assert encantado.get_mp() == nu.get_mp() + 20

    def test_evasion_chega_a_chance_de_acerto(self):
        peca = _item("Manto", slot="Body")
        peca.enchant(create_enchantment("evasion", 9))
        h, m = _heroi_com(peca), spawn_by_role("bruiser", 8)
        nu = Warrior("Nu")
        nu.level = 8
        assert cmb.hit_chance(m, h) == cmb.hit_chance(m, nu) - 9

    def test_damage_percent_entra_no_bucket_mult(self):
        """O `+MULT` existia vazio desde a centralização. Este é o primeiro dono."""
        peca = _item("Espada", damage_bonus=10)
        h, m = _heroi_com(peca), spawn_by_role("bruiser", 8)

        def golpe():
            mods = cmb.damage_modifiers(h, m, is_critical=False)
            dano = cmb._calculate_damage(
                base_power=float(cmb.basic_attack_power(h)),
                flat_mods=mods.flat,
                mult_mods=mods.mult,
                xmult_mods=mods.xmult,
                defense_target=m.get_df(),
                mitigation=mods.mitigation,
            )
            return dano, mods

        antes, mods_antes = golpe()
        assert mods_antes.mult == []

        peca.enchant(create_enchantment("damage_percent", 25))
        depois, mods_depois = golpe()
        assert mods_depois.mult == [0.25]
        assert mods_depois.xmult == [] and mods_depois.flat == []
        assert depois > antes

    def test_damage_percent_e_aditivo_entre_fontes(self):
        """`+MULT` soma antes de multiplicar: 10% e 15% dão 1,25x, não 1,265x."""
        a, b = _item("Espada"), _item("Escudo")
        a.enchant(create_enchantment("damage_percent", 10))
        b.enchant(create_enchantment("damage_percent", 15))
        h = _heroi_com(a)
        h.equip(b, "Weapon2")
        mods = cmb.damage_modifiers(h, spawn_by_role("bruiser", 8), is_critical=False)
        assert sum(mods.mult) == pytest.approx(0.25)

    def test_todo_efeito_da_allowlist_tem_consumidor(self):
        """Nenhum encantamento pode nascer placebo, como 58 itens nasceram."""
        peca = _item("Espada")
        h = _heroi_com(peca)
        for efeito in ENCHANT_EFFECTS:
            peca.enchantments = [create_enchantment(efeito, 10)]
            assert fx.combat_modifier(h, efeito) == 10.0, efeito


class TestAsTresNaoSeMisturam:
    def test_rank_nao_altera_encantamento(self):
        peca = _item("Espada", damage_bonus=10)
        peca.enchant(create_enchantment("crit_chance", 5))
        antes = peca.enchantment_bonus("crit_chance")
        peca.increase_enhancement(500)
        assert peca.enchantment_bonus("crit_chance") == antes
        assert peca.damage_bonus > 10, "o rank devia ter subido o dano da peça"

    def test_gema_nao_altera_encantamento(self):
        peca = _item("Espada", socket_count=1)
        peca.enchant(create_enchantment("crit_chance", 5))
        antes = peca.enchantment_bonus("crit_chance")
        peca.socket(create_gem("Rubi", 40))
        assert peca.enchantment_bonus("crit_chance") == antes
        assert peca.gem_percent("st") > 0

    def test_encantamento_nao_altera_rank_nem_gema(self):
        peca = _item("Espada", damage_bonus=10, socket_count=1)
        peca.increase_enhancement(10)
        peca.socket(create_gem("Rubi", 5))
        dano, gema = peca.damage_bonus, peca.gem_percent("st")
        peca.enchant(create_enchantment("damage_percent", 50))
        assert peca.damage_bonus == dano
        assert peca.gem_percent("st") == gema

    def test_os_tres_convivem_na_mesma_peca(self):
        peca = _item("Espada", damage_bonus=10, socket_count=1)
        peca.increase_enhancement(12)
        peca.socket(create_gem("Rubi", 8))
        peca.enchant(create_enchantment("crit_chance", 5))
        h = _heroi_com(peca)
        assert peca.damage_bonus > 10  # +N
        assert h.equipment_percent("st") > 0  # gema
        assert fx.combat_modifier(h, "crit_chance") == 5  # encantamento


class TestSave:
    @pytest.fixture
    def save_isolado(self, tmp_path, monkeypatch):
        from src.storage import save_manager

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
        monkeypatch.setattr(
            save_manager, "get_slot_file", lambda s: str(tmp_path / f"slot_{s}.json")
        )
        return save_manager

    class _Registro:
        def __init__(self, pecas):
            self._pecas = pecas

        def get(self, nome):
            return self._pecas.get(nome)

    FABRICAS = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}

    def test_as_tres_dimensoes_voltam_juntas(self, save_isolado):
        definicao = _item("Espada de Ferro", damage_bonus=6, socket_count=2)
        registro = self._Registro({"Espada de Ferro": definicao})

        peca = definicao.instance()
        peca.increase_enhancement(12)
        peca.socket(create_gem("Rubi", 8))
        peca.enchant(create_enchantment("crit_chance", 5))
        peca.enchant(create_enchantment("life_steal", 8))
        h = Rogue("Encantador")
        h.equip(peca, position="Weapon1")
        save_isolado.save_game(h, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(registro, self.FABRICAS, slot=1)
        arma = carregado.equipment["Weapon1"]
        assert arma.display_name == "Espada de Ferro +12"
        assert arma.gems[0].display_name == "Rubi Nv. 8"
        assert [(e.effect, e.value) for e in arma.enchantments] == [
            ("crit_chance", 5.0),
            ("life_steal", 8.0),
        ]

    def test_save_antigo_sem_encantamentos_carrega(self, save_isolado):
        definicao = _item("Espada de Ferro", damage_bonus=6)
        registro = self._Registro({"Espada de Ferro": definicao})
        h = Warrior("Antigo")
        h.equip(definicao.instance())
        save_isolado.save_game(h, 3, None, slot=1)

        caminho = Path(save_isolado.get_slot_file(1))
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        dados["equipment"] = {"Weapon": "Espada de Ferro"}
        caminho.write_text(json.dumps(dados), encoding="utf-8")

        carregado, _, _ = save_isolado.load_game(registro, self.FABRICAS, slot=1)
        assert carregado.equipment["Weapon1"].enchantments == []
