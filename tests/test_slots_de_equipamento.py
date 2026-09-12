"""Smoke tests das 11 posições de equipamento.

Posição não é categoria: o item declara onde se encaixa ("Weapon", "Ring"), o
personagem tem as posições onde isso cabe ("Weapon1"/"Weapon2", "Ring1"/"Ring2").
Estes testes cobrem só o essencial da estrutura nova — a auditoria completa dos
slots é a próxima rodada.
"""

from __future__ import annotations

import sys
from pathlib import Path

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


def test_classe_compatível_mantém_duas_armas_e_a_incompativel_troca():
    espada = _item("Espada", "Weapon", damage_bonus=8)
    adaga = _item("Adaga", "Weapon", damage_bonus=5)

    ladino = Rogue("Prova")
    ladino.equip(espada)
    ladino.equip(adaga)
    assert (ladino.equipment["Weapon1"], ladino.equipment["Weapon2"]) == (espada, adaga)
    # Uma arma só: o dano é o de antes. Duas: somam, e o balanceamento é outra rodada.
    assert ladino.weapon_percent() == 13

    mago = Mage("Prova")
    mago.equip(espada)
    mago.equip(adaga)
    assert mago.equipment["Weapon1"] is adaga, "a segunda arma devia ter substituído a primeira"
    assert mago.equipment["Weapon2"] is None
    assert mago.weapon_percent() == 5


def test_arma_de_duas_maos_bloqueia_a_secundaria():
    h = Rogue("Prova")
    h.equip(_item("Adaga", "Weapon", damage_bonus=5))
    h.equip(_item("Montante", "Weapon", damage_bonus=12, two_handed=True))
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
