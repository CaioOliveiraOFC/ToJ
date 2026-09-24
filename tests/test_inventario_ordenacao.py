"""Abrir o inventário não pode estourar.

`get_item_sort_key` fazia `slot_order = slot_order.get(slot, 99)`. A atribuição
torna `slot_order` LOCAL em toda a função, então a leitura do lado direito
acontecia antes da inicialização e qualquer peça equipável no inventário
derrubava a tela com `UnboundLocalError`. `effect_order`, logo abaixo, nunca
teve o problema — ele é lido e nunca reatribuído.

O teste ABRE a tela de verdade: chama `navigate_inventory` com a leitura de
tecla trocada por uma que sai na hora. Isso passa pelo `sorted(...)` real, com
as três categorias que a chave separa, em vez de exercitar uma cópia da função.
"""

from __future__ import annotations

import pytest

from src.content.items import get_all_items
from src.entities.heroes import Warrior
from src.ui import navigation_menu


def _item(predicado):
    for definicao in get_all_items().values():
        if predicado(definicao):
            return definicao.instance()
    raise AssertionError("catálogo sem item para este caso")


@pytest.fixture
def heroi_com_os_tres_tipos():
    """Um equipável, um consumível e um item que não é nem um nem outro.

    São as três categorias que `get_item_sort_key` separa, e só a primeira
    passava pelo ramo quebrado.
    """
    heroi = Warrior("Teste")
    equipavel = _item(lambda i: getattr(i, "slot", None) == "Weapon")
    consumivel = _item(lambda i: not getattr(i, "slot", None) and getattr(i, "is_usable", False))
    outro = _item(lambda i: not getattr(i, "slot", None) and not getattr(i, "is_usable", False))
    for peca in (equipavel, consumivel, outro):
        heroi.add_item_to_inventory(peca)
    return heroi, (equipavel, consumivel, outro)


def test_abrir_o_inventario_com_as_tres_categorias_nao_estoura(
    heroi_com_os_tres_tipos, monkeypatch
):
    heroi, _ = heroi_com_os_tres_tipos
    monkeypatch.setattr(navigation_menu, "get_key", lambda: "q")
    assert navigation_menu.navigate_inventory(list(heroi.inventory), heroi, []) is False


def test_a_ordenacao_agrupa_equipavel_antes_de_consumivel_antes_de_outro(
    heroi_com_os_tres_tipos, monkeypatch
):
    """A correção é de escopo, não de regra: a ordem continua a mesma.

    Renomear a local para `slot_rank` não pode reordenar nada — por isso o teste
    fixa a ordem das categorias, e não só a ausência de exceção.
    """
    heroi, (equipavel, consumivel, outro) = heroi_com_os_tres_tipos
    vistos: list[list[str]] = []

    ordena = sorted

    def espiao(itens, *, key):
        ordenado = ordena(itens, key=key)
        vistos.append([i.name for i in ordenado])
        return ordenado

    monkeypatch.setattr(navigation_menu, "get_key", lambda: "q")
    monkeypatch.setattr(navigation_menu, "sorted", espiao, raising=False)
    navigation_menu.navigate_inventory(list(heroi.inventory), heroi, [])

    assert vistos, "a view não chegou a ordenar o inventário"
    assert vistos[0] == [equipavel.name, consumivel.name, outro.name]


def test_inventario_vazio_continua_abrindo(monkeypatch):
    monkeypatch.setattr(navigation_menu, "get_key", lambda: "q")
    assert navigation_menu.navigate_inventory([], Warrior("Teste"), []) is False
