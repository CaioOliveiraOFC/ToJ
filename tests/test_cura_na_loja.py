"""KI-004: a cura básica está sempre à venda quando a Loja existe.

Na auditoria do instrumento (`0ab837b9`), com a política de poção já corrigida,
240 de 300 runs não beberam nenhuma poção no mapa, e 231 nunca tiveram uma. A
causa era a oferta: a poção era sorteada junto com todo o resto da vitrine, e a
Poção de Cura Pequena aparecia em 16% das Lojas dos andares 1-3; no drop, cura
saía em cerca de 0,5% das vitórias.

O que muda é só a oferta da cura básica — a poção Common, a que existe desde o
andar 1. Ela vira linha fixa da vitrine. As poções maiores continuam sendo
achado: sorteadas com o resto, como antes. Preço, desbloqueio por andar,
raridade, o resto da vitrine e o drop continuam como estavam.
"""

from __future__ import annotations

import random

import pytest

from src.content.economy import price_of
from src.content.items import get_all_items
from src.content.shop import Shop


def _e_cura(item) -> bool:
    return getattr(item, "consumable", False) and getattr(item, "effect_type", None) == "max_hp"


def _basica(item) -> bool:
    return _e_cura(item) and getattr(item, "rarity", "Common") == "Common"


def _curas_liberadas(andar: int, classe: str) -> set[str]:
    """As poções de cura que o catálogo libera para a Loja deste andar."""
    liberadas = set()
    for item in get_all_items().values():
        if not _e_cura(item) or not getattr(item, "sold_in_shop", False):
            continue
        if andar < getattr(item, "shop_min_floor", 1):
            continue
        maximo = getattr(item, "shop_max_floor", None)
        if maximo is not None and andar > maximo:
            continue
        raridade = getattr(item, "rarity", "Common")
        if raridade == "Legendary" or (raridade == "Epic" and andar < 10):
            continue
        classes = getattr(item, "classes", None)
        if classes is not None and classe not in classes:
            continue
        liberadas.add(item.id)
    return liberadas


@pytest.fixture
def rng_isolado():
    estado = random.getstate()
    yield
    random.setstate(estado)


ANDARES = (1, 2, 3, 4, 6, 9, 10, 15, 30)


@pytest.mark.usefixtures("rng_isolado")
class TestACuraBasicaEstaAVenda:
    @pytest.mark.parametrize("andar", ANDARES)
    def test_toda_vitrine_tem_a_cura_basica(self, andar):
        liberadas = _curas_liberadas(andar, "Warrior")
        basicas = {i.id for i in get_all_items().values() if i.id in liberadas and _basica(i)}
        assert basicas, f"o andar {andar} não libera cura básica"
        for semente in range(40):
            random.seed(semente)
            vitrine = Shop().get_available_items(andar, "Warrior")
            assert basicas <= {o["item"].id for o in vitrine}, (andar, semente)

    def test_as_pocoes_maiores_continuam_sendo_achado(self):
        """A Média, liberada no andar 4, aparece em umas vitrines e não em outras."""
        presencas = set()
        for semente in range(60):
            random.seed(semente)
            vitrine = Shop().get_available_items(6, "Warrior")
            presencas.add(any(o["item"].name == "Poção de Cura Média" for o in vitrine))
        assert presencas == {True, False}

    @pytest.mark.parametrize("andar", ANDARES)
    def test_nenhuma_cura_fora_do_que_o_andar_libera(self, andar):
        liberadas = _curas_liberadas(andar, "Mage")
        for semente in range(20):
            random.seed(semente)
            vitrine = Shop().get_available_items(andar, "Mage")
            assert {o["item"].id for o in vitrine if _e_cura(o["item"])} <= liberadas

    @pytest.mark.parametrize("andar", (1, 4, 10))
    def test_o_preco_e_o_de_sempre(self, andar):
        random.seed(3)
        for oferta in Shop().get_available_items(andar, "Mage"):
            assert oferta["price"] == price_of(oferta["item"], andar)

    @pytest.mark.parametrize("andar", (1, 5, 12))
    def test_o_resto_da_vitrine_continua_sorteado_no_mesmo_tamanho(self, andar):
        tamanhos, conjuntos = set(), set()
        for semente in range(30):
            random.seed(semente)
            vitrine = Shop().get_available_items(andar, "Warrior")
            resto = [o for o in vitrine if not _basica(o["item"])]
            tamanhos.add(len(resto))
            conjuntos.add(frozenset(o["item"].id for o in resto))
        faixa = {1: range(8, 11), 5: range(12, 16), 12: range(18, 23)}[andar]
        assert tamanhos <= set(faixa)
        assert len(conjuntos) > 1, "o resto da vitrine deixou de ser sorteado"

    def test_o_drop_nao_mudou(self):
        """A cura vem da Loja; a tabela de loot continua a mesma."""
        from src.content.factories import loot

        curas_na_tabela = [i for i in loot._build_loot_table() if _e_cura(i)]
        assert len(curas_na_tabela) == 3
