"""Aprimoramento `+N`: a primeira progressão do próprio item.

`+N` não é um buff do personagem nem um percentual de dano: é um eixo do
EXEMPLAR, que fortalece os stats base que a peça já tem. Duas Espadas de Ferro
podem estar +3 e +17 ao mesmo tempo, e é isso que a maior parte destes testes
protege — porque o catálogo entrega objetos compartilhados, e sem exemplar
próprio aprimorar uma espada aprimoraria todas as espadas do jogo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.items import Item, get_all_items  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.shared.formulas import enhancement_multiplier  # noqa: E402


def _item(nome: str, **kw) -> Item:
    kw.setdefault("slot", "Weapon")
    return Item(item_id=nome, name=nome, description="prova", **kw)


class TestHandsRequired:
    """A anatomia é de duas mãos: 3 não é um número maior, é um erro."""

    @pytest.mark.parametrize("valor", [0, 3, 7, -1])
    def test_valor_fora_do_contrato_levanta(self, valor):
        with pytest.raises(ValueError):
            _item("Absurdo", hands_required=valor)

    @pytest.mark.parametrize("valor", [1, 2])
    def test_um_e_dois_sao_aceitos(self, valor):
        assert _item("Ok", hands_required=valor).hands_required == valor


class TestExemplarProprio:
    """`+N` pertence à instância, nunca à definição do catálogo."""

    def test_dois_exemplares_da_mesma_definicao_tem_ranks_diferentes(self):
        definicao = get_all_items()["Espada Longa"]
        a, b = definicao.instance(), definicao.instance()
        a.increase_enhancement(3)
        b.increase_enhancement(17)
        assert (a.enhancement_level, b.enhancement_level) == (3, 17)
        assert a.damage_bonus != b.damage_bonus

    def test_aprimorar_um_exemplar_nao_toca_no_catalogo(self):
        definicao = get_all_items()["Espada Longa"]
        base = definicao.damage_bonus
        definicao.instance().increase_enhancement(50)
        assert get_all_items()["Espada Longa"].damage_bonus == base
        assert get_all_items()["Espada Longa"].enhancement_level == 0

    def test_a_loja_entrega_exemplares_e_nao_a_definicao(self):
        from src.content.shop import Shop

        catalogo = get_all_items()
        ofertas = Shop().get_available_items(5, "Warrior")
        assert ofertas, "premissa: a loja oferece algo no andar 5"
        for oferta in ofertas:
            assert oferta["item"] is not catalogo.get(oferta["item"].name)


class TestOQueMais:
    """`+N` fortalece stat base. Efeito especial não anda de carona."""

    def test_escala_dano_e_defesa(self):
        peca = _item("Peça", damage_bonus=10, defense_bonus=8)
        peca.increase_enhancement(25)
        assert peca.damage_bonus > 10
        assert peca.defense_bonus > 8

    @pytest.mark.parametrize(
        "efeito", ["max_hp", "max_mp", "strength", "agility", "speed", "magic_damage", "defense"]
    )
    def test_escala_atributo_base(self, efeito):
        peca = _item("Peça", effect_type=efeito, effect_value=20, rarity="Common")
        base = peca.effect_value
        peca.increase_enhancement(25)
        assert peca.effect_value > base, efeito

    @pytest.mark.parametrize(
        "efeito",
        [
            "stun",
            "bleed",
            "poison",
            "fear",
            "death_ignore",
            "mana_regen",
            "life_steal",
            "crit_chance",
            "crit_damage",
            "evasion",
            "damage_reduction",
        ],
    )
    def test_nao_escala_efeito_especial(self, efeito):
        """Um item +50 não atordoa mais nem rouba mais vida por ser +50."""
        peca = _item("Peça", effect_type=efeito, effect_value=20)
        peca.increase_enhancement(50)
        assert peca.effect_value == 20, efeito

    def test_nao_escala_resistencia_a_status(self):
        """Resistência tem teto em 100 e o rank não tem: +N ali seria imunidade."""
        peca = _item("Anel", slot="Ring", status_resistances={"frozen": 20})
        peca.increase_enhancement(500)
        assert peca.status_resistances == {"frozen": 20}

    def test_valor_negativo_nao_piora(self):
        """`defense_bonus` desce a -3 no catálogo: é desvantagem declarada."""
        peca = _item("Placa", damage_bonus=10, defense_bonus=-3)
        peca.increase_enhancement(50)
        assert peca.defense_bonus == -3

    def test_a_base_continua_respondivel(self):
        peca = _item("Peça", damage_bonus=10)
        peca.increase_enhancement(25)
        assert peca.base_damage_bonus == 10
        assert peca.damage_bonus == int(10 * enhancement_multiplier(25) + 0.5)


class TestCurva:
    def test_rank_zero_nao_muda_nada(self):
        assert enhancement_multiplier(0) == 1.0

    def test_cresce_e_a_margem_diminui(self):
        anterior, margem_anterior = 1.0, None
        for n in (1, 5, 10, 25, 50, 100, 500, 1000):
            atual = enhancement_multiplier(n)
            assert atual > anterior
            margem = atual - enhancement_multiplier(n - 1)
            if margem_anterior is not None:
                assert margem < margem_anterior
            anterior, margem_anterior = atual, margem


class TestNasOnzePosicoes:
    def test_cada_exemplar_resolve_o_proprio_rank(self):
        h = Warrior("Prova")
        espada = _item("Espada", damage_bonus=10)
        escudo = _item("Escudo", damage_bonus=0, defense_bonus=10)
        espada.increase_enhancement(10)
        escudo.increase_enhancement(4)
        h.equip(espada)
        h.equip(escudo)
        assert h.weapon_percent() == espada.damage_bonus
        assert h.equipment_percent("df") == espada.defense_bonus + escudo.defense_bonus

    def test_dois_aneis_com_ranks_diferentes(self):
        h = Mage("Prova")
        a = _item("Anel A", slot="Ring", effect_type="max_hp", effect_value=10, rarity="Common")
        b = _item("Anel B", slot="Ring", effect_type="max_hp", effect_value=10, rarity="Common")
        a.increase_enhancement(15)
        b.increase_enhancement(2)
        h.equip(a)
        h.equip(b)
        assert a.effect_value > b.effect_value
        assert h.equipment_percent("hp") == a.effect_value + b.effect_value

    def test_peca_de_duas_maos_nao_conta_duas_vezes(self):
        h = Rogue("Prova")
        maca = _item("Maça de Guerra", damage_bonus=12, hands_required=2)
        maca.increase_enhancement(20)
        h.equip(maca)
        assert h.equipment["Weapon2"] is None
        assert h.weapon_percent() == maca.damage_bonus


class TestDisplayName:
    def test_rank_zero_mostra_o_nome_puro(self):
        assert _item("Espada de Ferro").display_name == "Espada de Ferro"

    def test_rank_aparece_sem_contaminar_o_nome(self):
        peca = _item("Espada de Ferro")
        peca.increase_enhancement(27)
        assert peca.display_name == "Espada de Ferro +27"
        assert peca.name == "Espada de Ferro", "o nome é a chave do catálogo e do save"


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

    def _registro(self):
        return self._Registro({"Espada de Ferro": _item("Espada de Ferro", damage_bonus=6)})

    def test_dois_exemplares_iguais_com_ranks_diferentes_sobrevivem(self, save_isolado):
        registro = self._registro()
        h = Rogue("Ferreiro")
        a = registro.get("Espada de Ferro").instance()
        b = registro.get("Espada de Ferro").instance()
        a.increase_enhancement(3)
        b.increase_enhancement(17)
        h.equip(a, position="Weapon1")
        h.equip(b, position="Weapon2")
        save_isolado.save_game(h, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(
            registro, {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}, slot=1
        )
        assert carregado.equipment["Weapon1"].enhancement_level == 3
        assert carregado.equipment["Weapon2"].enhancement_level == 17
        assert carregado.equipment["Weapon1"] is not carregado.equipment["Weapon2"]

    def test_save_antigo_sem_enhancement_vira_rank_zero(self, save_isolado):
        """Formato anterior guardava só o nome, como string."""
        registro = self._registro()
        h = Warrior("Antigo")
        h.equip(registro.get("Espada de Ferro").instance())
        save_isolado.save_game(h, 3, None, slot=1)

        caminho = save_isolado.get_slot_file(1)
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        dados["equipment"] = {"Weapon": "Espada de Ferro"}
        dados["inventory"] = ["Espada de Ferro"]
        Path(caminho).write_text(json.dumps(dados), encoding="utf-8")

        carregado, _, _ = save_isolado.load_game(
            registro, {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}, slot=1
        )
        assert carregado.equipment["Weapon1"].enhancement_level == 0
        assert carregado.inventory[0].enhancement_level == 0
