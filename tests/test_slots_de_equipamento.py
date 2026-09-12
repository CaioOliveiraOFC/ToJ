"""Smoke tests das 11 posições de equipamento.

Posição não é categoria: o item declara onde se encaixa ("Weapon", "Ring"), o
personagem tem as posições onde isso cabe ("Weapon1"/"Weapon2", "Ring1"/"Ring2").
Estes testes cobrem só o essencial da estrutura nova — a auditoria completa dos
slots é a próxima rodada.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.items import Item  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402


def _item(nome: str, slot: str, **kw) -> Item:
    return Item(item_id=nome, name=nome, description="prova", slot=slot, **kw)


def test_dois_aneis_diferentes_ocupam_as_duas_posicoes_e_somam():
    h = Warrior("Prova")
    h.equip(_item("Anel do Inverno", "Ring", effect_type="evasion", effect_value=4))
    h.equip(_item("Anel da Vitalidade", "Ring", effect_type="evasion", effect_value=6))
    assert h.equipment["Ring1"].name == "Anel do Inverno"
    assert h.equipment["Ring2"].name == "Anel da Vitalidade"
    assert h.get_equipment_bonus("evasion") == 10


def test_toda_classe_tem_duas_maos():
    """Duas mãos são anatomia, não capacidade de classe.

    O Mago não tem menos mãos que o Guerreiro. Se uma combinação for proibida
    depois, a proibição vem do ITEM — `classes`, proficiência, requisito.
    """
    for classe in (Warrior, Rogue, Mage):
        h = classe("Prova")
        h.equip(_item("Espada", "Weapon", damage_bonus=8, hand_type="sword"))
        h.equip(_item("Escudo", "Weapon", defense_bonus=6, hand_type="shield"))
        assert h.equipment["Weapon1"].name == "Espada", classe.__name__
        assert h.equipment["Weapon2"].name == "Escudo", classe.__name__


COMBINACOES_DE_MAO = [
    ("Espada + Escudo", ("sword", 10, 0), ("shield", 0, 6)),
    ("Cajado + Orbe", ("staff", 7, 0), ("orb", 0, 2)),
    ("Adaga + Adaga", ("dagger", 5, 0), ("dagger", 5, 0)),
    ("Espada + Espada", ("sword", 10, 0), ("sword", 8, 0)),
    ("Varinha + Foco", ("wand", 4, 0), ("focus", 0, 1)),
]


@pytest.mark.parametrize("nome,primeira,segunda", COMBINACOES_DE_MAO)
def test_combinacoes_de_duas_maos_coexistem(nome, primeira, segunda):
    """A anatomia suporta as combinações, e cada peça contribui com o que declara."""
    h = Mage("Prova")  # a classe que antes não podia usar a segunda mão
    pecas = []
    for i, (tipo, dano, defesa) in enumerate((primeira, segunda)):
        peca = _item(
            f"{nome}-{i}", "Weapon", damage_bonus=dano, defense_bonus=defesa, hand_type=tipo
        )
        pecas.append(peca)
        h.equip(peca)
    assert h.equipment["Weapon1"] is pecas[0], nome
    assert h.equipment["Weapon2"] is pecas[1], nome
    # Ocupar uma mão não é o mesmo que somar dano: o escudo declara zero e
    # contribui zero, e a defesa dele entra pelo caminho da defesa.
    assert h.weapon_percent() == primeira[1] + segunda[1]
    assert h.equipment_percent("df") == primeira[2] + segunda[2]


def test_arma_de_duas_maos_bloqueia_a_secundaria():
    h = Rogue("Prova")
    h.equip(_item("Adaga", "Weapon", damage_bonus=5))
    h.equip(_item("Montante", "Weapon", damage_bonus=12, hands_required=2))
    assert h.equipment["Weapon1"].name == "Montante"
    assert h.equipment["Weapon2"] is None, "a peça de duas mãos deixou a secundária ocupada"
    # E não é escrita nas duas posições: contaria o dano dela duas vezes.
    assert h.weapon_percent() == 12
    assert h.equip(_item("Adaga 2", "Weapon", damage_bonus=5), position="Weapon2").startswith(
        "Adaga 2 não vai"
    )


def test_desequipar_devolve_ao_inventario_sem_duplicar():
    h = Warrior("Prova")
    anel = _item("Anel", "Ring")
    h.inventory.append(anel)
    h.equip(anel)
    assert anel not in h.inventory
    h.unequip("Ring1")
    assert h.inventory.count(anel) == 1
    assert h.equipment["Ring1"] is None


def test_item_de_accessory_pode_ser_equipado():
    h = Warrior("Prova")
    grimorio = _item("Grimório", "Accessory", defense_bonus=3)
    h.equip(grimorio)
    assert h.equipment["Accessory"] is grimorio


def test_save_antigo_carrega_weapon_e_ring_nas_primeiras_posicoes():
    """`Weapon`/`Ring` do save viram `Weapon1`/`Ring1`; as novas nascem vazias."""
    from src.storage.save_manager import POSICAO_LEGADA

    h = Warrior("Prova")
    salvo = {"Weapon": "Espada", "Ring": "Anel", "Helmet": "Elmo"}
    pecas = {
        "Espada": _item("Espada", "Weapon", damage_bonus=8),
        "Anel": _item("Anel", "Ring"),
        "Elmo": _item("Elmo", "Helmet", defense_bonus=2),
    }
    for slot, nome in salvo.items():
        posicao = POSICAO_LEGADA.get(slot, slot)
        h.equip(pecas[nome], posicao if posicao in h.equipment else None)

    assert h.equipment["Weapon1"].name == "Espada"
    assert h.equipment["Ring1"].name == "Anel"
    assert h.equipment["Helmet"].name == "Elmo"
    assert h.equipment["Weapon2"] is h.equipment["Ring2"] is h.equipment["Accessory"] is None


@pytest.fixture
def save_isolado(tmp_path, monkeypatch):
    """`save_manager` apontando para um diretório temporário."""
    from src.storage import save_manager

    monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
    monkeypatch.setattr(
        save_manager, "get_slot_file", lambda slot: str(tmp_path / f"slot_{slot}.json")
    )
    return save_manager


class _Registro:
    """Registro de itens de teste, com a interface que `load_game` usa."""

    def __init__(self, pecas):
        self._pecas = pecas

    def get(self, nome):
        return self._pecas.get(nome)


def _fabricas():
    return {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


class TestDuasMaos:
    """As TRANSIÇÕES, não só o estado final: nada pode ser duplicado nem perdido."""

    def test_two_handed_devolve_as_duas_armas_anteriores(self):
        h = Rogue("Prova")
        a, b = _item("A", "Weapon", damage_bonus=8), _item("B", "Weapon", damage_bonus=5)
        montante = _item("Montante", "Weapon", damage_bonus=12, hands_required=2)
        for peca in (a, b, montante):
            h.inventory.append(peca)
        h.equip(a)
        h.equip(b)

        h.equip(montante)
        assert h.equipment["Weapon1"] is montante
        assert h.equipment["Weapon2"] is None
        assert h.inventory.count(a) == 1 and h.inventory.count(b) == 1
        # Nem perdida nem duplicada: cada peça existe uma vez, em um lugar só.
        for peca in (a, b, montante):
            equipadas = sum(1 for v in h.equipment.values() if v is peca)
            assert equipadas + h.inventory.count(peca) == 1

    def test_segunda_arma_e_recusada_sem_perder_o_item(self):
        h = Rogue("Prova")
        montante = _item("Montante", "Weapon", damage_bonus=12, hands_required=2)
        adaga = _item("Adaga", "Weapon", damage_bonus=5)
        h.inventory += [montante, adaga]
        h.equip(montante)

        assert h.equip(adaga, position="Weapon2").startswith("Adaga não vai")
        assert h.equipment["Weapon2"] is None
        assert adaga in h.inventory, "a peça recusada sumiu"

    def test_tirar_a_de_duas_maos_libera_a_secundaria(self):
        h = Rogue("Prova")
        montante = _item("Montante", "Weapon", damage_bonus=12, hands_required=2)
        adaga = _item("Adaga", "Weapon", damage_bonus=5)
        h.inventory += [montante, adaga]
        h.equip(montante)
        h.unequip("Weapon1")

        h.equip(adaga)
        assert h.equipment["Weapon1"] is adaga
        assert h.can_equip_in_hand(_item("Outra", "Weapon"), "Weapon2")


class TestUnequip:
    """Posição inexistente não pode parecer posição vazia."""

    def test_posicao_inexistente_levanta_erro(self):
        h = Warrior("Prova")
        with pytest.raises(KeyError):
            h.unequip("Weapon")  # a grafia de antes das 11 posições

    def test_posicao_valida_e_vazia_devolve_none(self):
        assert Warrior("Prova").unequip("Weapon2") is None


class TestDoisAneis:
    def test_permanecem_equipados_e_somam_uma_vez_cada(self):
        h = Warrior("Prova")
        h.equip(_item("A", "Ring", effect_type="evasion", effect_value=4))
        h.equip(_item("B", "Ring", effect_type="evasion", effect_value=6))
        assert h.get_equipment_bonus("evasion") == 10

    def test_trocar_o_segundo_nao_mexe_no_primeiro(self):
        h = Warrior("Prova")
        primeiro = _item("A", "Ring", effect_type="evasion", effect_value=4)
        h.equip(primeiro)
        h.equip(_item("B", "Ring", effect_type="evasion", effect_value=6))
        h.unequip("Ring2")
        h.equip(_item("C", "Ring", effect_type="evasion", effect_value=9), position="Ring2")
        assert h.equipment["Ring1"] is primeiro
        assert h.get_equipment_bonus("evasion") == 13

    def test_remover_um_tira_so_a_contribuicao_dele(self):
        h = Warrior("Prova")
        h.equip(_item("A", "Ring", effect_type="evasion", effect_value=4))
        h.equip(_item("B", "Ring", effect_type="evasion", effect_value=6))
        h.unequip("Ring1")
        assert h.get_equipment_bonus("evasion") == 6


class TestSaveRoundTrip:
    """O save de verdade, por `save_game`/`load_game` — não um mapeamento à mão."""

    PECAS = {
        "Espada": {"slot": "Weapon", "damage_bonus": 8},
        "Adaga": {"slot": "Weapon", "damage_bonus": 5},
        "Montante": {"slot": "Weapon", "damage_bonus": 12, "hands_required": 2},
        "Anel A": {"slot": "Ring", "effect_type": "evasion", "effect_value": 4},
        "Anel B": {"slot": "Ring", "effect_type": "evasion", "effect_value": 6},
        "Grimório": {"slot": "Accessory", "defense_bonus": 3},
        "Elmo": {"slot": "Helmet", "defense_bonus": 2},
    }

    def _registro(self):
        return _Registro({nome: _item(nome, **kw) for nome, kw in self.PECAS.items()})

    def test_save_antigo_cai_nas_primeiras_posicoes(self, save_isolado):
        """`Weapon`/`Ring` de um save anterior às 11 posições."""
        registro = self._registro()
        heroi = Warrior("Antigo")
        heroi.equip(registro.get("Espada"))
        save_isolado.save_game(heroi, 3, None, slot=1)

        caminho = save_isolado.get_slot_file(1)
        dados = json.loads(open(caminho, encoding="utf-8").read())
        dados["equipment"] = {"Weapon": "Espada", "Ring": "Anel A", "Helmet": "Elmo"}
        open(caminho, "w", encoding="utf-8").write(json.dumps(dados))

        carregado, _, _ = save_isolado.load_game(registro, _fabricas(), slot=1)
        assert carregado.equipment["Weapon1"].name == "Espada"
        assert carregado.equipment["Ring1"].name == "Anel A"
        assert carregado.equipment["Helmet"].name == "Elmo"
        assert carregado.equipment["Weapon2"] is None
        assert carregado.equipment["Ring2"] is None
        assert carregado.equipment["Accessory"] is None

    def test_save_novo_preserva_todas_as_posicoes(self, save_isolado):
        registro = self._registro()
        heroi = Rogue("Novo")
        esperado = {
            "Weapon1": "Espada",
            "Weapon2": "Adaga",
            "Ring1": "Anel A",
            "Ring2": "Anel B",
            "Accessory": "Grimório",
        }
        for posicao, nome in esperado.items():
            heroi.equip(registro.get(nome), position=posicao)
        save_isolado.save_game(heroi, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(registro, _fabricas(), slot=1)
        assert {p: carregado.equipment[p].name for p in esperado} == esperado

    def test_save_com_arma_de_duas_maos(self, save_isolado):
        registro = self._registro()
        heroi = Rogue("DuasMaos")
        heroi.equip(registro.get("Montante"))
        save_isolado.save_game(heroi, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(registro, _fabricas(), slot=1)
        assert carregado.equipment["Weapon1"].name == "Montante"
        assert carregado.equipment["Weapon2"] is None

    def test_peca_recusada_no_carregamento_volta_para_a_mochila(self, save_isolado):
        """Peça restrita por classe, num save carregado por outra: nada evapora.

        `load_game` retirava a peça do inventário ANTES de tentar equipar, e a
        recusa a apagava do jogo.
        """
        registro = self._registro()
        exclusiva = _item("Lâmina do Ladino", slot="Weapon", damage_bonus=9, classes=["Rogue"])
        registro._pecas["Lâmina do Ladino"] = exclusiva

        heroi = Rogue("Restrito")
        heroi.equip(registro.get("Espada"), position="Weapon1")
        heroi.equip(exclusiva, position="Weapon2")
        save_isolado.save_game(heroi, 3, None, slot=1)

        caminho = save_isolado.get_slot_file(1)
        dados = json.loads(open(caminho, encoding="utf-8").read())
        dados["player_class"] = "Mage"
        open(caminho, "w", encoding="utf-8").write(json.dumps(dados))

        carregado, _, _ = save_isolado.load_game(registro, _fabricas(), slot=1)
        assert carregado.equipment["Weapon1"].name == "Espada"
        assert carregado.equipment["Weapon2"] is None
        assert [i.name for i in carregado.inventory] == ["Lâmina do Ladino"]

    def test_accessory_sobrevive_ao_round_trip(self, save_isolado):
        registro = self._registro()
        heroi = Warrior("Acessorio")
        heroi.equip(registro.get("Grimório"))
        assert heroi.equipment["Accessory"].name == "Grimório"
        save_isolado.save_game(heroi, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(registro, _fabricas(), slot=1)
        assert carregado.equipment["Accessory"].name == "Grimório"
        assert carregado.unequip("Accessory") == "Grimório"
        assert carregado.equipment["Accessory"] is None


class TestSelecaoDePosicao:
    """A pergunta só aparece quando existe escolha."""

    def _anel(self, nome):
        return _item(nome, "Ring")

    def test_nao_pergunta_quando_ha_vaga_ou_posicao_unica(self):
        from src.ui.navigation_menu import escolher_posicao

        h = Warrior("Prova")
        assert escolher_posicao(h, self._anel("X")) is None
        h.equip(self._anel("A"))
        assert escolher_posicao(h, self._anel("X")) is None, "havia Ring2 livre"
        assert escolher_posicao(h, _item("Elmo", "Helmet")) is None, "categoria de posição única"

    def test_pergunta_e_respeita_a_escolha_quando_tudo_esta_ocupado(self, monkeypatch):
        import src.ui.navigation_menu as nm

        h = Warrior("Prova")
        h.equip(self._anel("A"))
        h.equip(self._anel("B"))
        monkeypatch.setattr(nm.screens, "render_position_choice", lambda *a, **k: None)

        monkeypatch.setattr(nm, "get_key", lambda: "2")
        assert nm.escolher_posicao(h, self._anel("X")) == "Ring2"
        monkeypatch.setattr(nm, "get_key", lambda: "c")
        assert nm.escolher_posicao(h, self._anel("X")) is nm.CANCELADO


class TestSimuladorRepresentaAAnatomia:
    """O herói de medição precisa ter as mesmas mãos que o jogador."""

    @pytest.mark.parametrize("classe", ["Warrior", "Mage", "Rogue"])
    def test_loadout_preenche_as_duas_maos_e_os_dois_aneis(self, classe):
        from src.sim.harness import make_hero

        h = make_hero(classe, 8, "expected")
        for posicao in ("Weapon1", "Weapon2", "Ring1", "Ring2"):
            assert h.equipment[posicao] is not None, f"{classe} sem {posicao}"

    @pytest.mark.parametrize("classe", ["Warrior", "Mage", "Rogue"])
    def test_loadout_nunca_repete_a_mesma_instancia(self, classe):
        """A mesma peça em duas posições seria contada duas vezes por todo
        agregador que soma `equipment.values()`."""
        from src.sim.harness import make_hero

        equipadas = [v for v in make_hero(classe, 8, "expected").equipment.values() if v]
        assert len({id(v) for v in equipadas}) == len(equipadas)


class TestLojaTemAMesmaEscolha:
    """A loja e a mochila usam o mesmo helper: paridade por construção."""

    def _com_dois_aneis(self):
        h = Warrior("Prova")
        h.equip(_item("A", "Ring", effect_type="evasion", effect_value=4))
        h.equip(_item("B", "Ring", effect_type="evasion", effect_value=6))
        return h

    def test_a_loja_usa_o_mesmo_helper_do_inventario(self):
        from src.ui import navigation_menu, shop_flow

        assert shop_flow.equipar_escolhendo_posicao is navigation_menu.equipar_escolhendo_posicao

    def test_respeita_a_posicao_escolhida(self, monkeypatch):
        import src.ui.navigation_menu as nm

        h = self._com_dois_aneis()
        primeiro = h.equipment["Ring1"]
        novo = _item("C", "Ring", effect_type="evasion", effect_value=9)
        monkeypatch.setattr(nm.screens, "render_position_choice", lambda *a, **k: None)
        monkeypatch.setattr(nm, "get_key", lambda: "2")

        nm.equipar_escolhendo_posicao(h, novo)
        assert h.equipment["Ring1"] is primeiro
        assert h.equipment["Ring2"] is novo

    def test_cancelar_nao_altera_nada(self, monkeypatch):
        import src.ui.navigation_menu as nm

        h = self._com_dois_aneis()
        antes = dict(h.equipment)
        novo = _item("C", "Ring")
        monkeypatch.setattr(nm.screens, "render_position_choice", lambda *a, **k: None)
        monkeypatch.setattr(nm, "get_key", lambda: "c")

        nm.equipar_escolhendo_posicao(h, novo)
        assert h.equipment == antes
        assert novo not in h.equipment.values()
