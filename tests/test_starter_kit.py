"""Starter Kit: toda nova jornada começa com exatamente uma peça Lv1.

O contrato, em ordem: a pool cobre toda categoria equipável e só tem peça Lv1
válida que as três classes equipam; a nova jornada recebe UM starter, equipado,
sem mudar nível, ouro ou skill; o sorteio é reproduzível e sorteia a categoria
antes do item; a origem pertence ao exemplar e sobrevive ao save; e a peça que
só existe como starter fica fora de drop, loja e das réguas sintéticas.
"""

from __future__ import annotations

import copy
import json
import random
import statistics

import pytest

from src.content import economy, starter_kit
from src.content.factories import loot
from src.content.items import get_all_items
from src.content.starter_kit import (
    STARTER_ORIGIN,
    roll_starter,
    starter_categories,
    starter_pool,
)
from src.engine.game_logic import create_player_for_new_run, create_player_from_data
from src.entities.heroes import Mage, Rogue, Warrior
from src.sim.harness import make_hero
from src.storage.save_manager import _serializar, player_from_save_data, to_save_data

CLASSES = ("warrior", "mage", "rogue")
FABRICA = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


def _categorias_equipaveis() -> set[str]:
    # Categoria, não posição: Weapon1/Weapon2 e Ring1/Ring2 colapsam.
    return {Warrior.category_of(p) for p in Warrior.EQUIPMENT_POSITIONS}


def _starters(heroi) -> list:
    pecas = [*heroi.equipment.values(), *heroi.inventory]
    return [p for p in pecas if p is not None and getattr(p, "origin", None) == STARTER_ORIGIN]


def _equipadas(heroi) -> list:
    return [p for p in heroi.equipment.values() if p is not None]


class TestPool:
    def test_toda_categoria_equipavel_tem_starter(self):
        assert set(starter_categories()) == _categorias_equipaveis()
        assert len(starter_categories()) == len(_categorias_equipaveis())
        for categoria, itens in starter_pool().items():
            assert itens, f"{categoria} sem starter"

    def test_a_pool_so_tem_pecas_lv1_validas_do_catalogo(self):
        catalogo = get_all_items()
        for categoria, itens in starter_pool().items():
            for item in itens:
                assert catalogo[item.name] is item, f"{item.id} não é a definição do catálogo"
                assert item.slot == categoria
                assert not item.consumable
                assert item.rarity == "Common" and item.shop_min_floor <= 1, f"{item.id} não é Lv1"
                assert not item.classes, f"{item.id} é restrito a {item.classes}"

    @pytest.mark.parametrize("classe", CLASSES)
    def test_toda_classe_equipa_toda_peca_da_pool(self, classe):
        for itens in starter_pool().values():
            for item in itens:
                heroi = create_player_from_data(classe, "Prova")
                exemplar = item.instance()
                heroi.add_item_to_inventory(exemplar)
                heroi.equip(exemplar)
                assert exemplar in heroi.equipment.values(), f"{classe} não equipa {item.id}"

    def test_o_carregador_recusa_pool_mal_declarada(self, monkeypatch):
        starter_pool.cache_clear()
        monkeypatch.setattr(
            starter_kit, "load_json", lambda _: {"categories": {"Helmet": ["nao_existe"]}}
        )
        try:
            with pytest.raises(ValueError, match="nao_existe"):
                starter_pool()
        finally:
            starter_pool.cache_clear()


class TestNovaJornada:
    @pytest.mark.parametrize("classe", CLASSES)
    def test_recebe_exatamente_um_starter_equipado(self, classe):
        for semente in range(30):
            heroi = create_player_for_new_run(classe, "Prova", rng=random.Random(semente))
            assert len(_starters(heroi)) == 1, semente
            assert len(_equipadas(heroi)) == 1, semente
            assert _equipadas(heroi)[0].origin == STARTER_ORIGIN
            assert heroi.inventory == []

    @pytest.mark.parametrize("classe", CLASSES)
    def test_continua_nivel_1_sem_ouro_com_a_skill_inicial(self, classe):
        neutro = create_player_from_data(classe, "Prova")
        heroi = create_player_for_new_run(classe, "Prova", rng=random.Random(5))
        assert heroi.get_level() == neutro.get_level() == 1
        assert heroi.coins == 0
        assert [s.id for s in heroi.skills.values()] == [s.id for s in neutro.skills.values()]
        assert len(heroi.skills) == 1
        assert heroi.passives == []
        # O starter pode subir o teto: a jornada começa com o teto novo cheio.
        assert heroi.get_hp() == heroi.base_hp
        assert heroi.get_mp() == heroi.base_mp

    def test_a_criacao_neutra_continua_sem_starter(self):
        for classe in CLASSES:
            assert _equipadas(create_player_from_data(classe, "Prova")) == []

    def test_mesma_seed_mesmo_starter(self):
        for semente in range(40):
            a = create_player_for_new_run("rogue", "A", rng=random.Random(semente))
            b = create_player_for_new_run("rogue", "B", rng=random.Random(semente))
            assert [(p, i.id) for p, i in a.equipment.items() if i] == [
                (p, i.id) for p, i in b.equipment.items() if i
            ], semente
        vistas = {roll_starter(random.Random(s)).slot for s in range(200)}
        assert len(vistas) >= 5, "o sorteio não está variando a categoria"

    def test_categoria_e_sorteada_antes_do_item(self):
        class Gravador:
            def __init__(self):
                self.chamadas = []

            def choice(self, seq):
                seq = tuple(seq)
                self.chamadas.append(seq)
                return seq[-1]

        rng = Gravador()
        exemplar = roll_starter(rng)
        categorias = starter_categories()
        assert len(rng.chamadas) == 2
        # 1ª: as categorias, cada uma UMA vez — sorteio uniforme por construção.
        assert rng.chamadas[0] == categorias
        assert len(set(categorias)) == len(categorias)
        # 2ª: só os itens da categoria sorteada.
        escolhida = categorias[-1]
        assert rng.chamadas[1] == starter_pool()[escolhida]
        assert exemplar.slot == escolhida

    def test_origem_fica_no_exemplar_e_nao_na_definicao(self):
        exemplar = roll_starter(random.Random(3))
        definicao = get_all_items()[exemplar.name]
        assert exemplar.origin == STARTER_ORIGIN
        assert exemplar is not definicao
        assert definicao.origin is None
        # Só o item: nem socket sorteado nem bônus escondido.
        assert exemplar.socket_count == definicao.socket_count == 0
        assert exemplar.enchantments == []
        assert exemplar.enhancement_level == 0

    def test_depois_de_recebido_e_uma_peca_comum(self):
        heroi = create_player_for_new_run("warrior", "Prova", rng=random.Random(11))
        posicao, starter = next((p, i) for p, i in heroi.equipment.items() if i)
        heroi.unequip(posicao)
        assert heroi.equipment[posicao] is None
        assert starter in heroi.inventory
        heroi.equip(starter)
        assert heroi.equipment[posicao] is starter


class TestSave:
    def _ida_e_volta(self, heroi):
        dados = json.loads(json.dumps(to_save_data(heroi, 1)))
        carregado, _, _ = player_from_save_data(dados, get_all_items(), FABRICA)
        return dados, carregado

    def test_save_e_load_preservam_a_origem(self):
        heroi = create_player_for_new_run("mage", "Prova", rng=random.Random(21))
        posicao = next(p for p, i in heroi.equipment.items() if i)
        dados, carregado = self._ida_e_volta(heroi)
        assert dados["equipment"][posicao]["origin"] == STARTER_ORIGIN
        assert carregado.equipment[posicao].origin == STARTER_ORIGIN
        assert carregado.equipment[posicao].name == heroi.equipment[posicao].name

    def test_save_antigo_sem_origem_continua_valido(self):
        heroi = create_player_for_new_run("warrior", "Prova", rng=random.Random(8))
        posicao = next(p for p, i in heroi.equipment.items() if i)
        dados = json.loads(json.dumps(to_save_data(heroi, 1)))
        antigo = copy.deepcopy(dados)
        antigo["equipment"][posicao].pop("origin")
        carregado, _, _ = player_from_save_data(antigo, get_all_items(), FABRICA)
        assert carregado.equipment[posicao].name == heroi.equipment[posicao].name
        assert carregado.equipment[posicao].origin is None
        # O formato mais antigo, só o nome, também carrega.
        so_nome = copy.deepcopy(dados)
        so_nome["equipment"][posicao] = heroi.equipment[posicao].name
        carregado, _, _ = player_from_save_data(so_nome, get_all_items(), FABRICA)
        assert carregado.equipment[posicao].origin is None

    def test_item_comum_salva_sem_origem(self):
        espada = get_all_items()["Espada de Ferro"].instance()
        assert "origin" not in _serializar(espada)


class TestIsolamento:
    """A peça que só existe como starter não entra em drop, loja ou régua."""

    def _exclusivos(self):
        return [i for i in get_all_items().values() if i.starter_only]

    def test_exclusivos_existem_so_na_pool(self):
        exclusivos = self._exclusivos()
        assert exclusivos, "nenhuma peça exclusiva: o teste perdeu o objeto"
        na_pool = {i.id for itens in starter_pool().values() for i in itens}
        for item in exclusivos:
            assert item.id in na_pool
            assert not item.droppable and not item.sold_in_shop

    def test_exclusivos_nao_caem_nem_sao_vendidos(self):
        nomes = {i.name for i in self._exclusivos()}
        assert not nomes & {i.name for i in loot._build_loot_table()}
        vendidos = {i.name for i in get_all_items().values() if i.sold_in_shop}
        assert not nomes & vendidos

    def test_exclusivos_nao_entram_no_loadout_de_medicao(self):
        nomes = {i.name for i in self._exclusivos()}
        for classe in ("Warrior", "Mage", "Rogue"):
            for nivel in (1, 5, 12, 20, 40):
                heroi = make_hero(classe, nivel, "expected")
                equipado = {i.name for i in heroi.equipment.values() if i}
                assert not nomes & equipado, (classe, nivel)

    def test_exclusivos_nao_movem_o_preco_de_referencia(self):
        precos = [
            float(i.price)
            for i in get_all_items().values()
            if i.rarity == "Common" and not i.consumable and not i.starter_only
        ]
        assert economy._referencias()[("Common", False)] == statistics.median(precos)
