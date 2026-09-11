"""A economia: renda do andar, preço, venda, juros e recuperação paga.

"Ouro compra opções." Estes testes fixam as regras que fazem o ouro produzir
decisão — e, em particular, as que já falharam em silêncio antes: uma fórmula
de preço copiada em quatro lugares, um fator de venda que três chamadores
ignoravam, pesos de raridade declarados no JSON e nunca lidos, e a ordem de fim
de andar divergindo entre o jogo e o simulador.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.content import economy
from src.content.factories.loot import get_loot
from src.content.items import get_all_items
from src.content.shop import Shop
from src.entities.heroes import Mage, Rogue, Warrior
from src.shared import economy as formulas
from src.shared.constants import (
    FLOOR_CLEAR_RESTORE_PERCENT,
    INTEREST_CAP_INCOME_RATIO,
    INTEREST_RATE_PERCENT,
    SELL_PRICE_MAX_FACTOR,
    SELL_PRICE_MIN_FACTOR,
)
from src.storage import save_manager

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


@pytest.fixture
def heroi():
    return Warrior("Cofre")


class TestRendaDoAndar:
    """A âncora. Se ela quebrar, todo preço do jogo se move junto."""

    def test_renda_cresce_com_o_andar(self):
        rendas = [formulas.expected_floor_income(f) for f in range(1, 31)]
        assert rendas == sorted(rendas)
        assert rendas[0] > 0

    def test_renda_bate_com_o_que_os_andares_realmente_pagam(self):
        """Contra o gerador de andares de verdade, não contra outra fórmula.

        Uma âncora econômica que só concorda consigo mesma não ancora nada: era
        assim que preço linear e renda geométrica conviveram por tanto tempo.

        Duas verificações, porque a âncora tem dois trabalhos. O acumulado é o
        poder de compra que o jogador leva até ali, e é o que decide se um preço
        é alcançável — tem de bater em TODO andar. O valor de um andar isolado só
        é cobrado a partir do 10: entre o 5 e o 9 o plano de andar sobe e desce
        (o chefe do 5, depois dois andares magros), e nenhuma curva suave segue
        isso. A âncora é um envelope de poder de compra, não uma tabela de
        pagamento.
        """
        import random
        import statistics

        from src.content.factories.monsters import calculate_scaled_monster_level
        from src.mechanics.math_operations import (
            calculate_mini_boss_coin_reward,
            calculate_monster_coin_reward,
        )
        from src.sim.encounters import build_encounter
        from src.sim.harness import _default_floor_plan

        acumulado_real = acumulado_estimado = 0.0
        for andar in range(1, 21):
            medidas = []
            for i in range(30):
                random.seed(4000 + i)
                ouro = 0
                for nome in _default_floor_plan(andar):
                    for mob in build_encounter(
                        nome, andar, lambda: calculate_scaled_monster_level(andar, andar)
                    ):
                        ouro += (
                            calculate_mini_boss_coin_reward(mob.level)
                            if getattr(mob, "is_boss", False)
                            else calculate_monster_coin_reward(mob.level)
                        )
                medidas.append(ouro)
            real = statistics.fmean(medidas)
            estimada = formulas.expected_floor_income(andar)
            acumulado_real += real
            acumulado_estimado += estimada
            assert 0.75 <= acumulado_estimado / acumulado_real <= 1.25, (
                f"andar {andar}: poder de compra acumulado {acumulado_estimado:.0f} "
                f"contra {acumulado_real:.0f} real"
            )
            if andar >= 10:
                assert 0.75 <= estimada / real <= 1.25, (
                    f"andar {andar}: estimativa {estimada:.0f} contra renda real {real:.0f}"
                )


class TestJuros:
    def test_pagos_uma_vez_por_andar(self, heroi):
        heroi.earn_coins(1000)
        primeiro = economy.pay_interest(heroi, 5)
        segundo = economy.pay_interest(heroi, 5)
        assert primeiro > 0
        assert segundo == 0, "o mesmo andar pagou juros duas vezes: isso imprime moeda"

    def test_andar_seguinte_paga_de_novo(self, heroi):
        heroi.earn_coins(1000)
        assert economy.pay_interest(heroi, 5) > 0
        assert economy.pay_interest(heroi, 6) > 0

    def test_saldo_zero_nao_paga_nem_quebra(self, heroi):
        assert heroi.coins == 0
        assert economy.pay_interest(heroi, 7) == 0
        assert heroi.coins == 0

    def test_a_taxa_e_a_declarada_abaixo_do_cap(self, heroi):
        # Saldo pequeno o bastante para o cap não morder.
        heroi.earn_coins(200)
        assert formulas.interest_for(200, 10) == int(200 * INTEREST_RATE_PERCENT / 100)

    def test_o_cap_segura_a_fortuna(self):
        teto = formulas.interest_cap(10)
        assert teto == int(formulas.expected_floor_income(10) * INTEREST_CAP_INCOME_RATIO)
        assert formulas.interest_for(10_000_000, 10) == teto, (
            "sem cap, o juro composto vira renda principal e a masmorra vira detalhe"
        )

    def test_o_cap_nao_congela_a_economia_tardia(self):
        """O teto acompanha a renda: no andar 20 rende mais que no 5, em ouro."""
        assert formulas.interest_cap(20) > formulas.interest_cap(5)

    def test_save_e_load_nao_pagam_duas_vezes(self, heroi, tmp_path, monkeypatch):
        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        heroi.earn_coins(1000)
        pago = economy.pay_interest(heroi, 4)
        assert pago > 0
        save_manager.save_game(heroi, 5, None, slot=1)

        carregado, _, _ = save_manager.load_game(get_all_items(), CLASSES, slot=1)
        assert carregado is not None
        assert carregado.last_interest_floor == 4
        assert economy.pay_interest(carregado, 4) == 0, (
            "salvar e carregar no mesmo andar pagou os juros de novo"
        )


class TestVenda:
    def test_retorno_fica_na_faixa_de_20_a_25(self):
        loja = Shop()
        fora = []
        for item in get_all_items().values():
            for andar in (1, 7, 15, 22):
                preco = loja.get_price(item, andar)
                devolvido = loja.get_sell_price(item, andar)
                fracao = devolvido / preco
                if not (SELL_PRICE_MIN_FACTOR - 0.02 <= fracao <= SELL_PRICE_MAX_FACTOR + 0.02):
                    fora.append((item.name, andar, round(fracao, 3)))
        assert not fora, f"venda fora da faixa: {fora[:5]}"

    def test_o_preco_mostrado_e_o_preco_pago(self, heroi):
        """A tela e a transação chamam a mesma função — era aqui que divergiam."""
        loja = Shop()
        item = get_all_items()["Espada de Ferro"]
        heroi.inventory.append(item)
        anunciado = loja.get_sell_price(item, 6)
        antes = heroi.coins
        assert loja.sell_item(heroi, item, 6)
        assert heroi.coins - antes == anunciado

    def test_venda_nao_e_fonte_primaria_de_renda(self):
        """Vender o que se compra tem de perder dinheiro, e muito."""
        loja = Shop()
        item = get_all_items()["Espada de Ferro"]
        assert loja.get_sell_price(item, 10) < loja.get_price(item, 10) * 0.3

    def test_o_fator_de_venda_e_estavel_entre_execucoes(self):
        """Derivado do id, não sorteado: senão a tela mentiria a cada frame."""
        item = get_all_items()["Espada de Ferro"]
        assert formulas.sell_factor(item.id) == formulas.sell_factor(item.id)


class TestPreco:
    def test_preco_acompanha_a_renda_do_andar(self):
        loja = Shop()
        item = get_all_items()["Espada de Ferro"]
        razao_1 = loja.get_price(item, 1) / formulas.expected_floor_income(1)
        razao_15 = loja.get_price(item, 15) / formulas.expected_floor_income(15)
        assert razao_1 == pytest.approx(razao_15, rel=0.05), (
            "preço e renda voltaram a crescer em curvas diferentes"
        )

    def test_raridade_maior_custa_mais_fatia_do_andar(self):
        loja = Shop()
        por_raridade = {}
        for item in get_all_items().values():
            if getattr(item, "consumable", False):
                continue
            por_raridade.setdefault(item.rarity, []).append(loja.get_price(item, 10))
        medias = {r: sum(v) / len(v) for r, v in por_raridade.items()}
        assert medias["Common"] < medias["Rare"] < medias["Epic"] < medias["Legendary"]

    def test_o_andar_oferece_o_que_cabe_e_o_que_nao_cabe(self):
        """O critério de sucesso: nem "compro tudo", nem "nunca compro nada"."""
        loja = Shop()
        for andar in (3, 10, 18):
            renda = formulas.expected_floor_income(andar)
            precos = [
                loja.get_price(i, andar)
                for i in get_all_items().values()
                if getattr(i, "sold_in_shop", False)
            ]
            assert any(p <= renda * 0.3 for p in precos), f"andar {andar}: nada é acessível"
            assert any(p > renda for p in precos), f"andar {andar}: dá para comprar tudo"

    def test_o_mercador_errante_usa_o_preco_central(self):
        """A quarta cópia da fórmula morava no evento do mercador."""
        import random

        from src.content.factories.dungeons import MERCHANT_DISCOUNT, get_merchant_offers

        random.seed(11)
        ofertas = get_merchant_offers(9)
        assert ofertas
        for oferta in ofertas:
            esperado = int(economy.price_of(oferta["item"], 9) * MERCHANT_DISCOUNT)
            assert abs(oferta["price"] - esperado) <= 1


class TestRaridadeDoLoot:
    def test_sorteio_e_ponderado_pelos_pesos_do_json(self):
        import collections
        import random

        from src.data.loader import load_items_data

        pesos = load_items_data()["rarity_weights"]
        random.seed(3)
        contagem = collections.Counter()
        for _ in range(20000):
            item = get_loot()
            if item:
                contagem[item.rarity] += 1
        total = sum(contagem.values())
        for raridade, peso in pesos.items():
            obtido = 100 * contagem[raridade] / total
            assert abs(obtido - peso) < 2.0, f"{raridade}: {obtido:.1f}% contra {peso}% declarado"

    def test_a_raridade_nao_depende_do_andar(self):
        """O jogo é infinito e a escala por profundidade ainda não foi decidida.

        Este teste existe para que ela não apareça por acidente: `get_loot` não
        recebe o andar, e não deve passar a receber sem uma decisão de design.
        """
        import inspect

        assert not inspect.signature(get_loot).parameters, (
            "get_loot ganhou parâmetro: se for o andar, isso é escala de raridade por "
            "profundidade, que está fora de escopo por decisão explícita"
        )


class TestRecuperacao:
    def test_descanso_gratuito_continua_existindo_mas_enfraquecido(self):
        assert 0 < FLOOR_CLEAR_RESTORE_PERCENT <= 25, (
            "a recuperação gratuita não pode sumir nem voltar a ser forte demais"
        )

    def test_comprar_vida(self, heroi):
        heroi.earn_coins(100_000)
        heroi._hp = int(heroi.base_hp * 0.3)
        antes_hp, antes_ouro = heroi.get_hp(), heroi.coins
        paga = economy.buy_recovery(heroi, 5, "hp")
        assert paga is not None
        assert heroi.get_hp() > antes_hp
        assert heroi.coins == antes_ouro - paga["price"]

    def test_comprar_mana(self, heroi):
        heroi.earn_coins(100_000)
        heroi._mp = 0
        paga = economy.buy_recovery(heroi, 5, "mp")
        assert paga is not None
        assert heroi.get_mp() > 0

    def test_sem_ouro_nao_compra_e_nao_cura(self, heroi):
        heroi._hp = int(heroi.base_hp * 0.2)
        antes = heroi.get_hp()
        assert economy.buy_recovery(heroi, 12, "hp") is None
        assert heroi.get_hp() == antes, "curou sem pagar"
        assert heroi.coins == 0

    def test_recurso_cheio_nao_gera_oferta(self, heroi):
        heroi.earn_coins(100_000)
        assert economy.recovery_offers(heroi, 5) == []
        assert economy.buy_recovery(heroi, 5, "hp") is None

    def test_cura_completa_custa_quase_um_andar_inteiro(self, heroi):
        """Reparar tudo tem de competir com equipar — não pode ser troco."""
        heroi.earn_coins(100_000)
        heroi._hp = 1
        gasto = 0
        while (oferta := economy.buy_recovery(heroi, 8, "hp")) is not None:
            gasto += oferta["price"]
        renda = formulas.expected_floor_income(8)
        assert 0.5 * renda <= gasto <= 1.3 * renda, f"cura completa custou {gasto} de {renda}"

    def test_paga_so_pelo_que_falta(self, heroi):
        """Quem está quase cheio paga proporcionalmente menos."""
        heroi.earn_coins(100_000)
        heroi._hp = int(heroi.base_hp * 0.95)
        quase_cheio = economy.recovery_offers(heroi, 8)[0]["price"]
        heroi._hp = 1
        vazio = economy.recovery_offers(heroi, 8)[0]["price"]
        assert quase_cheio < vazio


class TestPassivasEconomicas:
    """Já estavam integradas; estes testes impedem que voltem a ser placebo."""

    def test_gold_drop_bonus_entra_na_recompensa(self):
        import random

        from src.content.factories.archetypes import spawn_by_role
        from src.content.passives import load_passives
        from src.sim.harness import _award

        passiva = next(p for p in load_passives() if p.effect_type == "gold_drop_bonus")
        sem = Warrior("Sem")
        com = Warrior("Com")
        com.add_passive(passiva)
        for heroi in (sem, com):
            random.seed(5)
            _award(heroi, [spawn_by_role("trash", 5)], 1.0, random.Random(5))
        assert com.coins > sem.coins

    def test_essence_bonus_entra_no_xp(self):
        import random

        from src.content.factories.archetypes import spawn_by_role
        from src.content.passives import load_passives
        from src.sim.harness import _award

        passiva = next(p for p in load_passives() if p.effect_type == "essence_bonus")
        sem = Warrior("Sem")
        com = Warrior("Com")
        com.add_passive(passiva)
        for heroi in (sem, com):
            random.seed(5)
            _award(heroi, [spawn_by_role("trash", 5)], 1.0, random.Random(5))
        assert com.xp_points > sem.xp_points


class TestLivroCaixa:
    def test_entrada_e_saida_sao_registradas(self, heroi):
        heroi.earn_coins(500, source="combat")
        assert heroi.ledger["gold_earned"] == 500
        assert heroi.ledger["max_gold_held"] == 500
        assert heroi.spend_coins(200, source="gear")
        assert heroi.ledger["gold_spent"] == 200
        assert heroi.ledger["gold_spent_on_gear"] == 200
        assert heroi.ledger["purchases"] == 1

    def test_gasto_recusado_nao_entra_no_livro(self, heroi):
        heroi.earn_coins(10)
        assert not heroi.spend_coins(1000, source="gear")
        assert heroi.ledger["gold_spent"] == 0
        assert heroi.coins == 10

    def test_juros_aparecem_separados(self, heroi):
        heroi.earn_coins(1000)
        economy.pay_interest(heroi, 6)
        assert heroi.ledger["gold_from_interest"] > 0
        assert heroi.ledger["interest_payments"] == 1

    def test_a_morte_nao_preserva_ouro_utilizavel(self, tmp_path, monkeypatch):
        """Permadeath: o saldo não vira banco, nem passa para outro personagem.

        Fica o registro — e só. Se um dia alguém acrescentar um banco global,
        este teste é quem avisa.
        """
        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        from src.engine.loop import _economia_da_run

        morto = Warrior("Finado")
        morto.earn_coins(900)
        livro = _economia_da_run(morto)
        save_manager.add_trophy("Finado", "Warrior", 7, 9, "Derrotado", economy=livro)
        save_manager.delete_save(1)

        trofeu = save_manager.get_trophies()[-1]
        assert trofeu["economy"]["gold_lost_on_death"] == 900

        novo = Warrior("Sucessor")
        assert novo.coins == 0, "ouro atravessou a morte e chegou ao próximo personagem"
        assert save_manager.load_game(get_all_items(), CLASSES, slot=1)[0] is None


class TestOrdemDeFimDeAndar:
    def test_a_ordem_esta_declarada(self):
        from src.engine.loop import FIM_DE_ANDAR

        assert FIM_DE_ANDAR == ("evento", "descanso", "loja", "juros", "extracao")

    def test_o_jogo_e_o_simulador_seguem_a_mesma_ordem(self):
        """Medido no código, não na intenção.

        O simulador descansava DEPOIS da loja e o jogo ANTES do evento: dois
        jogos diferentes, um medindo o outro. Com recuperação paga na loja, a
        inversão passa a mudar quanto o jogador gasta, então a ordem vira regra.
        """
        import inspect

        from src.engine import loop
        from src.sim import harness

        def sequencia(fonte: str, marcos: dict[str, str]) -> list[str]:
            achados = [(fonte.index(agulha), nome) for nome, agulha in marcos.items()]
            return [nome for _, nome in sorted(achados)]

        jogo = inspect.getsource(loop.start_game)
        sim = inspect.getsource(harness.simulate_run)

        assert sequencia(
            jogo,
            {
                "evento": "roll_random_event()",
                "descanso": "player.recover(",
                "loja": "UI_OPEN_SHOP",
                "juros": "pay_interest(",
            },
        ) == ["evento", "descanso", "loja", "juros"]

        assert sequencia(
            sim,
            {
                "evento": "_apply_random_event(",
                "descanso": "hero.recover(",
                "loja": "visit_shop(",
                "juros": "pay_interest(",
            },
        ) == ["evento", "descanso", "loja", "juros"]

    def test_loja_e_simulador_usam_as_mesmas_formulas(self):
        """Nenhuma das duas pode ter fórmula própria de preço ou de venda."""
        loja = Shop()
        item = get_all_items()["Espada de Ferro"]
        for andar in (2, 9, 17):
            assert loja.get_price(item, andar) == economy.price_of(item, andar)
            assert loja.get_sell_price(item, andar) == economy.sell_value_of(item, andar)


class TestTelemetriaEconomica:
    def test_a_taxa_de_utilizacao_e_calculada(self):
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.gold_earned = 1000
        t.gold_spent_on_gear = 300
        t.gold_spent_on_consumables = 100
        t.gold_spent_on_recovery = 100
        assert t.gold_spent == 500
        assert t.gold_utilization_rate == 0.5
        assert t.to_dict()["economy"]["gold_utilization_rate"] == 0.5

    def test_sem_renda_a_taxa_nao_divide_por_zero(self):
        from src.sim.telemetry import RunTelemetry

        assert RunTelemetry().gold_utilization_rate == 0.0

    def test_todas_as_metricas_pedidas_existem(self):
        from src.sim.telemetry import RunTelemetry

        esperadas = {
            "gold_earned",
            "gold_spent",
            "gold_unspent",
            "gold_from_interest",
            "max_gold_held",
            "gold_lost_on_death",
            "gold_from_sales",
            "gold_spent_on_gear",
            "gold_spent_on_consumables",
            "gold_spent_on_recovery",
            "items_dropped",
            "items_equipped",
            "items_sold",
            "purchases",
            "interest_payments",
        }
        assert esperadas <= set(RunTelemetry().to_dict()["economy"])
