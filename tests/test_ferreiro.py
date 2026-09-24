"""O Ferreiro: a porta que faltava para +N, gemas e encantamentos.

As três mecânicas já existiam e funcionavam — e nenhum jogador jamais tinha
aprimorado uma espada, porque não havia onde. Estes testes cobram o ACESSO: que
o serviço cobre, chame a mecânica que já existe e registre; e que sem ouro nada
aconteça.

Não medem equilíbrio. Os preços são calibração inicial, para a fase final ter o
que medir.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content import economy, forge  # noqa: E402
from src.content.enchantments import (  # noqa: E402
    ENCHANT_EFFECTS,
    ENCHANT_VALUE_RANGES,
    MAX_ENCHANTMENTS,
    roll_enchantment,
)
from src.content.gems import create_gem, gem_max_level, roll_gem_drop  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.shared.constants import GEM_DROP_CHANCE  # noqa: E402


@pytest.fixture
def heroi():
    h = Warrior("Teste")
    h.set_level(10)
    h.earn_coins(500_000)
    return h


@pytest.fixture
def peca(heroi):
    item = get_all_items()["Espada Longa"].instance()
    item.socket_count = 2
    item.gems = [None, None]
    heroi.add_item_to_inventory(item)
    heroi.equip(item)
    return item


class TestGemaEntraNaRun:
    def test_a_gema_cai_pela_chance_declarada(self):
        r = random.Random(1)
        quedas = sum(1 for _ in range(20_000) if roll_gem_drop(10, r) is not None)
        assert abs(quedas / 20_000 - GEM_DROP_CHANCE) < 0.01

    def test_a_gema_vai_para_a_bolsa_e_nao_para_o_inventario(self, heroi):
        class SempreCai(random.Random):
            def random(self):
                return 0.0

        gema = forge.award_gem(heroi, 10, SempreCai(0))
        assert gema is not None
        assert gema in heroi.gems
        assert gema not in heroi.inventory
        assert heroi.ledger["gems_found"] == 1

    def test_o_nivel_segue_o_patamar_lento_do_andar(self):
        """`1 + andar // 5`, e não `1..andar`: o andar 20 daria Nv.20."""
        assert [gem_max_level(f) for f in (1, 5, 10, 20, 50)] == [1, 2, 3, 5, 11]

        from src.content.gems import random_gem

        r = random.Random(3)
        for andar in (1, 10, 50):
            teto = gem_max_level(andar)
            niveis = {random_gem(andar, r).level for _ in range(400)}
            assert max(niveis) <= teto
            assert min(niveis) >= max(1, teto - 1)

    def test_a_vitoria_pode_largar_item_e_gema(self, heroi):
        """Rolagens independentes: uma não ocupa o lugar da outra."""
        from src.engine import encounter

        class SempreCai(random.Random):
            def random(self):
                return 0.0

        # `process_post_battle` mudou de casa: de `engine/loop.py` para
        # `engine/encounter.py`, que é o core que o jogador e o bot dividem.
        # O patch segue a função, não o módulo antigo.
        original = encounter.get_loot
        encounter.get_loot = lambda: get_all_items()["Espada Longa"].instance()
        try:
            antes_inv = len(heroi.inventory)
            forge.award_gem(heroi, 5, SempreCai(0))
            encounter.process_post_battle(heroi, [_monstro()], 1.0, 5)
            assert len(heroi.inventory) > antes_inv
            assert heroi.gems
        finally:
            encounter.get_loot = original


def _monstro():
    from src.content.factories.archetypes import spawn_by_role

    return spawn_by_role("trash", 5)


class TestAprimorar:
    def test_cobra_uma_vez_e_sobe_exatamente_um(self, heroi, peca):
        custo = economy.enhancement_cost(peca, 10)
        antes = heroi.coins
        assert forge.enhance(heroi, peca, 10) == 1
        assert heroi.coins == antes - custo
        assert peca.enhancement_level == 1
        assert heroi.ledger["gold_spent_on_enhancement"] == custo

    def test_o_custo_cresce_a_cada_rank(self, heroi, peca):
        custos = []
        for _ in range(5):
            custos.append(economy.enhancement_cost(peca, 10))
            forge.enhance(heroi, peca, 10)
        assert custos == sorted(custos) and custos[0] < custos[-1]

    def test_sem_ouro_nada_muda(self, heroi, peca):
        heroi.coins = economy.enhancement_cost(peca, 10) - 1
        moedas = heroi.coins
        assert forge.enhance(heroi, peca, 10) is None
        assert peca.enhancement_level == 0
        assert heroi.coins == moedas


class TestGemasNoFerreiro:
    def test_engastar_cobra_e_move_bolsa_para_socket(self, heroi, peca):
        gema = create_gem("Rubi", 3)
        heroi.gems.append(gema)
        custo, antes = economy.socket_cost(10), heroi.coins

        assert forge.socket(heroi, peca, gema, 0, 10) is True
        assert peca.gems[0] is gema
        assert gema not in heroi.gems
        assert heroi.coins == antes - custo
        assert heroi.ledger["gold_spent_on_socket"] == custo

    def test_retirar_cobra_e_devolve_a_pedra_inteira(self, heroi, peca):
        gema = create_gem("Rubi", 3)
        heroi.gems.append(gema)
        forge.socket(heroi, peca, gema, 0, 10)
        custo, antes = economy.unsocket_cost(10), heroi.coins

        retirada = forge.unsocket(heroi, peca, 0, 10)
        assert retirada is gema
        assert gema in heroi.gems, "A gema tem de voltar para a bolsa."
        assert gema.level == 3, "A gema não quebra e não perde nível."
        assert peca.gems[0] is None
        assert heroi.coins == antes - custo

    def test_socket_cheio_recusa_engaste(self, heroi, peca):
        """Trocar exige retirar antes — nada de troca de graça."""
        primeira, segunda = create_gem("Rubi", 2), create_gem("Safira", 2)
        heroi.gems.extend([primeira, segunda])
        forge.socket(heroi, peca, primeira, 0, 10)
        antes = heroi.coins

        assert forge.socket(heroi, peca, segunda, 0, 10) is False
        assert peca.gems[0] is primeira
        assert segunda in heroi.gems
        assert heroi.coins == antes, "Recusa não pode cobrar."

    def test_sem_ouro_nada_muda(self, heroi, peca):
        gema = create_gem("Rubi", 1)
        heroi.gems.append(gema)
        heroi.coins = 0
        assert forge.socket(heroi, peca, gema, 0, 10) is False
        assert peca.gems[0] is None
        assert gema in heroi.gems


class TestEncantar:
    def test_usa_os_efeitos_reais_e_as_faixas_declaradas(self):
        r = random.Random(5)
        for _ in range(200):
            e = roll_enchantment(r)
            assert e.effect in ENCHANT_EFFECTS
            minimo, maximo = ENCHANT_VALUE_RANGES[e.effect]
            assert minimo <= e.value <= maximo

    def test_a_curva_e_cinquenta_por_cento_dobrando(self):
        renda = economy.expected_floor_income(10)
        esperado = [max(1, int(renda * 0.50 * 2**n)) for n in range(5)]
        assert [economy.enchant_cost(10, n) for n in range(5)] == esperado

    def test_acrescentar_cobra_e_para_no_teto_mecanico(self, heroi, peca):
        for camada in range(MAX_ENCHANTMENTS):
            custo = economy.enchant_cost(10, camada)
            antes = heroi.coins
            assert forge.enchant(heroi, peca, 10, random.Random(camada)) is not None
            assert heroi.coins == antes - custo
        assert len(peca.enchantments) == MAX_ENCHANTMENTS
        assert forge.enchant(heroi, peca, 10, random.Random(9)) is None

    def test_reencantar_troca_somente_a_camada_escolhida(self, heroi, peca):
        for camada in range(3):
            forge.enchant(heroi, peca, 10, random.Random(camada))
        vizinhos = [(e.effect, e.value) for e in peca.enchantments]

        novo = forge.reenchant(heroi, peca, 1, 10, random.Random(99))
        assert novo is not None
        atuais = [(e.effect, e.value) for e in peca.enchantments]
        assert len(atuais) == 3
        assert atuais[0] == vizinhos[0] and atuais[2] == vizinhos[2]
        assert atuais[1] == (novo.effect, novo.value)

    def test_reencantar_paga_o_preco_da_posicao(self, heroi, peca):
        for camada in range(3):
            forge.enchant(heroi, peca, 10, random.Random(camada))
        antes = heroi.coins
        forge.reenchant(heroi, peca, 2, 10, random.Random(1))
        assert heroi.coins == antes - economy.reenchant_cost(10, 2)
        assert economy.reenchant_cost(10, 2) == economy.enchant_cost(10, 2)

    def test_sem_ouro_nada_muda(self, heroi, peca):
        heroi.coins = 0
        assert forge.enchant(heroi, peca, 10) is None
        assert peca.enchantments == []


class TestSaveLoad:
    @pytest.fixture
    def save_isolado(self, tmp_path, monkeypatch):
        from src.storage import save_manager

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
        monkeypatch.setattr(
            save_manager, "get_slot_file", lambda s: str(tmp_path / f"slot_{s}.json")
        )
        return save_manager

    def test_round_trip_com_mais_n_gemas_e_encantamentos(self, save_isolado, heroi, peca):
        """As três dimensões no MESMO exemplar, indo e voltando do disco."""
        save_manager = save_isolado
        forge.enhance(heroi, peca, 10)
        forge.enhance(heroi, peca, 10)
        gema = create_gem("Topázio", 4)
        heroi.gems.append(gema)
        forge.socket(heroi, peca, gema, 1, 10)
        forge.enchant(heroi, peca, 10, random.Random(7))
        heroi.gems.append(create_gem("Ônix", 2))

        esperado = {
            "rank": peca.enhancement_level,
            "gemas": [(g.gem_type, g.level) if g else None for g in peca.gems],
            "encantos": [(e.effect, e.value) for e in peca.enchantments],
            "bolsa": [(g.gem_type, g.level) for g in heroi.gems],
        }

        posicao = next(k for k, v in heroi.equipment.items() if v is peca)
        save_manager.save_game(heroi, 10, None, slot=1)

        from src.content.items import get_all_items as registro_itens
        from src.entities.heroes import Mage, Rogue

        class _Registro:
            def get(self, nome):
                return registro_itens()[nome]

        carregado, _, _ = save_manager.load_game(
            _Registro(), {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}, slot=1
        )
        item = carregado.equipment[posicao]

        assert item.enhancement_level == esperado["rank"]
        assert [(g.gem_type, g.level) if g else None for g in item.gems] == esperado["gemas"]
        assert [(e.effect, e.value) for e in item.enchantments] == esperado["encantos"]
        assert [(g.gem_type, g.level) for g in carregado.gems] == esperado["bolsa"]


class TestSimuladorUsaOFerreiro:
    def test_o_bot_encontra_gemas_e_gasta_no_ferreiro(self):
        from src.sim.harness import simulate_run

        r = simulate_run("Warrior", max_floor=20, iterations=30, policy="smart", seed=7)
        eq, eco = r["telemetry"]["equipment"], r["telemetry"]["economy"]
        assert eq["gems_found"] > 0
        assert eq["gems_socketed"] > 0
        assert eq["items_enhanced"] > 0
        assert eq["enchantments_added"] > 0
        assert eco["gold_spent_on_forge"] > 0

    def test_o_ledger_fecha_com_os_destinos(self, heroi, peca):
        gema = create_gem("Rubi", 1)
        heroi.gems.append(gema)
        forge.enhance(heroi, peca, 10)
        forge.socket(heroi, peca, gema, 0, 10)
        forge.unsocket(heroi, peca, 0, 10)
        forge.enchant(heroi, peca, 10, random.Random(1))
        forge.reenchant(heroi, peca, 0, 10, random.Random(2))

        destinos = sum(v for k, v in heroi.ledger.items() if k.startswith("gold_spent_on_"))
        assert destinos == heroi.ledger["gold_spent"]
