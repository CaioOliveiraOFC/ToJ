"""Reroll: comprar outra amostra do RNG, com risco econômico.

Loja, oferta de skill e oferta de passiva usam a MESMA curva de custo. O que
muda entre elas não é o preço — é o contexto do contador, que vive na oferta e
morre com ela.

Não existe teto de tentativas, e é de propósito: quem segura o jogador é o custo
dobrando, não uma regra. Estes testes cobram a regra e a contabilidade, não o
equilíbrio dos números — isso é balanceamento, e é outra fase.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content import economy  # noqa: E402
from src.content.factories.monsters import routine_monster_count  # noqa: E402
from src.content.shop import Shop  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.shared import economy as formulas  # noqa: E402
from src.shared.constants import (  # noqa: E402
    BOSS_FLOOR_INTERVAL,
    REROLL_COST_GROWTH,
    REROLL_FIRST_INCOME_RATIO,
)


@pytest.fixture
def heroi():
    h = Warrior("Teste")
    h.set_level(10)
    return h


class TestAncoraUsaAPopulacaoReal:
    """A renda esperada deixou de ser uma reta ajustada à mão."""

    @pytest.mark.parametrize("andar", [1, 5, 10, 11, 20, 50])
    def test_as_unidades_saem_do_gerador_de_andares(self, andar):
        unidades = economy.floor_income_units(andar)
        comuns = routine_monster_count(andar)
        assert unidades >= comuns, "A renda não pode valer menos que os monstros comuns."
        # Sem chefe, o excedente é só a chance de elite: menos de um monstro.
        if andar % BOSS_FLOOR_INTERVAL != 0:
            assert unidades - comuns < 1.0

    def test_o_andar_de_chefe_paga_mais_que_o_seguinte(self):
        """O chefe entra convertido em unidades, e é por isso que a curva tem pico."""
        assert economy.expected_floor_income(10) > economy.expected_floor_income(11)

    def test_a_renda_cresce_no_mesmo_ponto_do_ciclo(self):
        for andar in range(1, 26):
            assert economy.expected_floor_income(andar + BOSS_FLOOR_INTERVAL) > (
                economy.expected_floor_income(andar)
            )


class TestCurvaDeCusto:
    """Uma fórmula só, e ela dobra."""

    @pytest.mark.parametrize("andar", [1, 7, 20])
    def test_a_curva_e_quinze_por_cento_dobrando(self, andar):
        renda = economy.expected_floor_income(andar)
        esperado = [
            max(1, int(renda * REROLL_FIRST_INCOME_RATIO * REROLL_COST_GROWTH**n)) for n in range(5)
        ]
        assert [economy.reroll_cost(andar, n) for n in range(5)] == esperado

    def test_as_proporcoes_declaradas(self):
        """15% / 30% / 60% / 120% / 240% da renda do andar."""
        renda = 10_000  # renda redonda: a proporção aparece sem ruído de int()
        assert [formulas.reroll_price(renda, n) for n in range(5)] == [
            1500,
            3000,
            6000,
            12000,
            24000,
        ]

    def test_loja_skill_e_passiva_pagam_a_mesma_coisa(self):
        """Três consumidores, uma curva. Três fórmulas seriam três economias."""
        andar = 12
        visita = Shop().visit(andar, "Warrior")
        for n in range(4):
            preco = economy.reroll_cost(andar, n)
            assert visita.next_reroll_cost == preco
            visita.rerolls_done += 1
        # skill e passiva chamam a mesma função — provado pelo próprio nome único
        assert economy.reroll_cost(andar, 0) == formulas.reroll_price(
            economy.expected_floor_income(andar), 0
        )

    def test_nao_existe_teto_de_tentativas(self):
        """O custo é o limitador, e não um contador."""
        assert economy.reroll_cost(10, 12) > economy.reroll_cost(10, 11) > 0


class TestLojaRerolla:
    def test_cobra_uma_vez_e_troca_o_estoque(self, heroi):
        heroi.earn_coins(100_000)
        visita = Shop().visit(10, "Warrior")
        antes, custo = heroi.coins, visita.next_reroll_cost
        nomes_antes = [o["item"].name for o in visita.stock]

        assert visita.reroll(heroi) is True
        assert heroi.coins == antes - custo, "Reroll cobrou mais de uma vez."
        assert visita.rerolls_done == 1
        assert visita.next_reroll_cost == custo * 2
        # O estoque é outro sorteio; com 159 itens, sair idêntico seria acaso.
        assert [o["item"].name for o in visita.stock] != nomes_antes or len(nomes_antes) < 3

    def test_sem_ouro_nada_muda(self, heroi):
        visita = Shop().visit(10, "Warrior")
        heroi.coins = visita.next_reroll_cost - 1
        estoque = list(visita.stock)
        moedas = heroi.coins

        assert visita.reroll(heroi) is False
        assert heroi.coins == moedas
        assert visita.stock == estoque
        assert visita.rerolls_done == 0, "Tentativa negada não pode consumir contador."

    def test_o_contador_reinicia_em_nova_visita(self, heroi):
        heroi.earn_coins(100_000)
        loja = Shop()
        primeira = loja.visit(10, "Warrior")
        primeira.reroll(heroi)
        primeira.reroll(heroi)
        assert primeira.rerolls_done == 2

        segunda = loja.visit(10, "Warrior")
        assert segunda.rerolls_done == 0
        assert segunda.next_reroll_cost == economy.reroll_cost(10, 0)

    def test_o_gasto_entra_no_livro_caixa(self, heroi):
        heroi.earn_coins(100_000)
        visita = Shop().visit(10, "Warrior")
        custo = visita.next_reroll_cost
        visita.reroll(heroi)
        assert heroi.ledger["gold_spent_on_shop_reroll"] == custo
        assert heroi.ledger["gold_spent"] >= custo


class TestOfertasRerollam:
    """Skill e passiva, pelo fluxo real da UI."""

    @staticmethod
    def _teclas(sequencia):
        it = iter(sequencia)
        return lambda *a, **k: next(it)

    def test_skill_descartada_conta_como_vista(self, heroi, monkeypatch):
        from src.content.skills_loader import generate_skill_choices
        from src.ui import screens, skill_flow

        heroi.earn_coins(100_000)
        monkeypatch.setattr(screens, "render_skill_selection", lambda *a, **k: None)
        monkeypatch.setattr(skill_flow, "safe_get_key", self._teclas(["r", "1"]))

        ofertas = generate_skill_choices("Warrior", 10, [], seen_ids=heroi.seen_skill_ids)
        heroi.seen_skill_ids.update(c.id for c in ofertas)
        descartadas = {c.id for c in ofertas}

        escolhida = skill_flow.run_skill_selection_flow(heroi, ofertas, dungeon_level=10)

        assert escolhida is not None
        assert descartadas <= heroi.seen_skill_ids, (
            "O jogador viu as cartas descartadas e elas sumiram de `seen_skill_ids`."
        )
        assert heroi.ledger["gold_spent_on_skill_reroll"] == economy.reroll_cost(10, 0)

    def test_passiva_nao_cria_seen_ids(self, heroi, monkeypatch):
        from src.content.passives import generate_passive_choices
        from src.ui import passive_flow, screens

        heroi.earn_coins(100_000)
        monkeypatch.setattr(screens, "render_passive_selection", lambda *a, **k: None)
        monkeypatch.setattr(screens, "render_passive_acquired", lambda *a, **k: None)
        monkeypatch.setattr(passive_flow, "safe_get_key", self._teclas(["r", "1"]))

        passive_flow.run_passive_selection_flow(
            heroi, generate_passive_choices(3), dungeon_level=10
        )

        assert not hasattr(heroi, "seen_passive_ids")
        assert heroi.ledger["gold_spent_on_passive_reroll"] == economy.reroll_cost(10, 0)

    def test_sem_ouro_a_oferta_de_passiva_fica_como_esta(self, heroi, monkeypatch):
        from src.content.passives import generate_passive_choices
        from src.ui import passive_flow, screens

        monkeypatch.setattr(screens, "render_passive_selection", lambda *a, **k: None)
        monkeypatch.setattr(screens, "render_passive_acquired", lambda *a, **k: None)
        monkeypatch.setattr(screens, "render_offer_reroll_denied", lambda *a, **k: None)
        monkeypatch.setattr(passive_flow, "safe_get_key", self._teclas(["r", "1"]))

        ofertas = generate_passive_choices(3)
        nomes = [c.name for c in ofertas]
        heroi.coins = 0
        passive_flow.run_passive_selection_flow(heroi, ofertas, dungeon_level=10)

        assert [c.name for c in ofertas] == nomes, "Oferta mudou sem pagamento."
        assert heroi.ledger.get("gold_spent_on_passive_reroll", 0) == 0


class TestSimuladorUsaOMesmoSistema:
    def test_o_bot_gasta_e_a_telemetria_registra(self):
        from src.sim.harness import simulate_run

        r = simulate_run("Warrior", max_floor=20, iterations=40, policy="smart", seed=7)
        eco = r["telemetry"]["economy"]
        assert eco["rerolls"] > 0, "O bot não conseguiu usar o sistema de reroll."
        assert eco["gold_spent_on_rerolls"] > 0
        assert eco["gold_spent_on_rerolls"] == (
            eco["gold_spent_on_shop_reroll"]
            + eco["gold_spent_on_skill_reroll"]
            + eco["gold_spent_on_passive_reroll"]
        )

    def test_o_livro_caixa_fecha(self):
        """Uma transação, uma fonte: o total é a soma dos destinos."""
        heroi = Warrior("Teste")
        heroi.earn_coins(100_000)
        visita = Shop().visit(10, "Warrior")
        visita.reroll(heroi)
        heroi.spend_coins(50, source="gear")

        destinos = sum(v for k, v in heroi.ledger.items() if k.startswith("gold_spent_on_"))
        assert destinos == heroi.ledger["gold_spent"]

    def test_o_bot_respeita_o_ouro_disponivel(self):
        """Política do BOT, não regra do jogo: ele nunca fica devendo."""
        from src.sim import progression

        heroi = Warrior("Teste")
        heroi.set_level(10)
        heroi.coins = 5
        visita = Shop().visit(10, "Warrior")
        progression._rerollar_estoque(heroi, visita, None)
        assert heroi.coins == 5
        assert visita.rerolls_done == 0
