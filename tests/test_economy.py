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
        """Cresce por CICLO de andar, e não andar a andar.

        A âncora deixou de ser uma reta ajustada e passou a ser a população real
        do andar. Com isso ela ganhou a cadência do chefe: o andar 10 paga o
        chefe e o 11 não, então a renda sobe num pico e recua depois dele. É a
        verdade sobre o que um full clear paga, e comparar andares vizinhos
        deixou de ser a pergunta certa.

        O que não pode acontecer é a renda parar de crescer: comparada no mesmo
        ponto do ciclo — de cinco em cinco andares —, ela sobe sempre.
        """
        from src.shared.constants import BOSS_FLOOR_INTERVAL

        rendas = [economy.expected_floor_income(f) for f in range(1, 31)]
        assert rendas[0] > 0
        for i in range(len(rendas) - BOSS_FLOOR_INTERVAL):
            assert rendas[i + BOSS_FLOOR_INTERVAL] > rendas[i], (
                f"andar {i + 1 + BOSS_FLOOR_INTERVAL} não paga mais que o {i + 1}"
            )

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
            estimada = economy.expected_floor_income(andar)
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
        renda = economy.expected_floor_income(10)
        assert formulas.interest_for(200, renda) == int(200 * INTEREST_RATE_PERCENT / 100)

    def test_o_cap_segura_a_fortuna(self):
        renda = economy.expected_floor_income(10)
        teto = economy.interest_cap(10)
        assert teto == int(renda * INTEREST_CAP_INCOME_RATIO)
        assert formulas.interest_for(10_000_000, renda) == teto, (
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
        razao_1 = loja.get_price(item, 1) / economy.expected_floor_income(1)
        razao_15 = loja.get_price(item, 15) / economy.expected_floor_income(15)
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
            renda = economy.expected_floor_income(andar)
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
        renda = economy.expected_floor_income(8)
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

        assert FIM_DE_ANDAR == ("evento", "descanso", "loja", "ferreiro", "juros", "extracao")

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
                # Ferreiro depois da loja: investir na peça que já se tem vem
                # depois de ver a peça que dá para comprar, e as duas saem da
                # mesma carteira.
                "ferreiro": "UI_OPEN_FORGE",
                "juros": "pay_interest(",
            },
        ) == ["evento", "descanso", "loja", "ferreiro", "juros"]

        assert sequencia(
            sim,
            {
                "evento": "_apply_random_event(",
                "descanso": "hero.recover(",
                "loja": "visit_shop(",
                "ferreiro": "visit_forge(",
                "juros": "pay_interest(",
            },
        ) == ["evento", "descanso", "loja", "ferreiro", "juros"]

    def test_loja_e_simulador_usam_as_mesmas_formulas(self):
        """Nenhuma das duas pode ter fórmula própria de preço ou de venda."""
        loja = Shop()
        item = get_all_items()["Espada de Ferro"]
        for andar in (2, 9, 17):
            assert loja.get_price(item, andar) == economy.price_of(item, andar)
            assert loja.get_sell_price(item, andar) == economy.sell_value_of(item, andar)


class TestTelemetriaEconomica:
    def test_a_taxa_de_utilizacao_usa_o_inflow_liquido(self):
        """O denominador é combate + juros + venda, e está documentado."""
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.gold_from_combat = 600
        t.gold_from_interest = 200
        t.gold_from_sales = 200
        t.gold_spent_on_gear = 300
        t.gold_spent_on_consumables = 100
        t.gold_spent_on_recovery = 100
        assert t.total_liquid_gold_inflow == 1000
        assert t.gold_spent == 500
        assert t.gold_utilization_rate == 0.5
        assert t.to_dict()["economy"]["gold_utilization_rate"] == 0.5

    def test_venda_e_juros_nao_entram_na_renda_primaria(self):
        """Vender é converter item em ouro, não criar riqueza."""
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.gold_from_combat = 100
        t.gold_from_interest = 50
        t.gold_from_sales = 70
        assert t.gold_from_primary_income == 100
        assert t.total_liquid_gold_inflow == 220

    def test_sem_renda_a_taxa_nao_divide_por_zero(self):
        from src.sim.telemetry import RunTelemetry

        assert RunTelemetry().gold_utilization_rate == 0.0

    def test_todas_as_metricas_pedidas_existem(self):
        from src.sim.telemetry import RunTelemetry

        esperadas = {
            "gold_from_combat",
            "gold_from_primary_income",
            "total_liquid_gold_inflow",
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


class TestLojaEmMasmorraInfinita:
    """A masmorra é infinita; a loja não pode parar num andar arbitrário.

    121 itens — 100% dos equipamentos vendáveis e 0% dos consumíveis — carregavam
    `shop_max_floor: 15`. Não era design por item: era o default de quando o jogo
    acabava no andar 20. O efeito era o andar 16 em diante oferecer só poção.
    """

    def test_equipamento_continua_a_venda_depois_do_15(self):
        import random

        loja = Shop()
        for andar in (16, 20, 25, 40, 120):
            random.seed(andar)
            equipamentos = [
                o
                for o in loja.get_available_items(andar, "Warrior")
                if not getattr(o["item"], "consumable", False)
            ]
            assert len(equipamentos) >= 5, f"andar {andar}: só {len(equipamentos)} equipamentos"

    def test_nenhum_teto_arbitrario_novo_no_catalogo(self):
        """Nem 999, nem 9999, nem 15 de volta: a correção foi deleção."""
        from src.data.loader import load_items_data

        com_teto = [
            i
            for i in load_items_data()["items"]
            if i.get("sold_in_shop") and i.get("shop_max_floor") is not None
        ]
        assert not com_teto, (
            "item vendável voltou a declarar teto de andar sem razão documentada: "
            f"{[i['id'] for i in com_teto][:5]}"
        )

    def test_shop_min_floor_continua_valendo(self):
        """Desbloqueio continua sendo desbloqueio."""
        loja = Shop()
        atrasados = [i for i in get_all_items().values() if getattr(i, "shop_min_floor", 1) > 1]
        assert atrasados
        for item in atrasados:
            antes = item.shop_min_floor - 1
            ofertas = {o["item"].id for o in loja.get_available_items(antes, "Warrior")}
            assert item.id not in ofertas, f"{item.id} apareceu no andar {antes}"

    def test_a_mistura_de_raridades_da_loja_nao_muda_com_a_profundidade(self):
        """Nenhum scaling novo por andar — nem para cima, nem para baixo.

        Isto NÃO cobra 60/28/10/2: aquela é a tabela de loot. A loja tem os
        filtros dela. O que se cobra aqui é só que a proporção do andar 16 seja
        a mesma do andar 60.
        """
        import collections
        import random

        loja = Shop()

        def mistura(andar: int) -> dict[str, float]:
            contagem = collections.Counter()
            for i in range(120):
                random.seed(andar * 1000 + i)
                for oferta in loja.get_available_items(andar, "Warrior"):
                    contagem[oferta["item"].rarity] += 1
            total = sum(contagem.values())
            return {r: c / total for r, c in contagem.items()}

        raso, fundo = mistura(16), mistura(60)
        assert raso.keys() == fundo.keys()
        for raridade in raso:
            assert abs(raso[raridade] - fundo[raridade]) < 0.03, (
                f"{raridade}: {raso[raridade]:.1%} no andar 16 contra "
                f"{fundo[raridade]:.1%} no 60 — isso é scaling por profundidade"
            )

    def test_legendary_continua_fora_da_loja_em_qualquer_profundidade(self):
        import random

        loja = Shop()
        for andar in (10, 25, 50, 200):
            random.seed(andar)
            assert not [
                o
                for o in loja.get_available_items(andar, "Warrior")
                if o["item"].rarity == "Legendary"
            ]


class TestVendaNoSimulador:
    """O bot não vendia nada, então a faixa de 20–25% nunca foi medida."""

    def _com_arma(self, forte: bool):
        from src.sim.progression import _descartavel

        heroi = Warrior("Bot")
        armas = sorted(
            (i for i in get_all_items().values() if i.slot == "Weapon" and not i.classes),
            key=lambda i: i.damage_bonus,
        )
        return heroi, armas, _descartavel

    def test_vende_item_claramente_inferior(self):
        """Com as DUAS mãos ocupadas por peças melhores, a terceira é dominada.

        Antes bastava uma arma equipada para a segunda ser descartável. O
        personagem tem duas mãos, então uma segunda arma tem onde ir — e só a
        partir da terceira existe algo a vender.
        """
        heroi, armas, descartavel = self._com_arma(True)
        boa, segunda, ruim = armas[-1], armas[-2], armas[0]
        for arma in (boa, segunda):
            heroi.inventory.append(arma)
            heroi.equip(arma)
        heroi.inventory.append(ruim)
        assert descartavel(heroi, ruim)

    def test_nao_vende_upgrade(self):
        heroi, armas, descartavel = self._com_arma(True)
        boa, ruim = armas[-1], armas[0]
        heroi.inventory.append(ruim)
        heroi.equip(ruim)
        heroi.inventory.append(boa)
        assert not descartavel(heroi, boa), "vendeu o upgrade que deveria equipar"

    def test_nao_vende_o_que_esta_equipado(self):
        """Item equipado sai do inventário, então nem chega ao descarte."""
        heroi, armas, _ = self._com_arma(True)
        arma = armas[-1]
        heroi.inventory.append(arma)
        heroi.equip(arma)
        assert arma not in heroi.inventory
        assert heroi.equipment["Weapon1"] is arma

    def test_nao_vende_item_utilizavel_de_slot_vazio(self):
        """Veste antes de descartar: slot vazio não tem com o que comparar."""
        from src.sim.progression import _vender_dominados

        heroi = Warrior("Bot")
        arma = next(i for i in get_all_items().values() if i.slot == "Weapon" and not i.classes)
        heroi.inventory.append(arma)
        assert heroi.equipment["Weapon1"] is None
        _vender_dominados(heroi, Shop(), 5)
        assert heroi.equipment["Weapon1"] is arma, "vendeu o item que deveria ter equipado"
        assert heroi.coins == 0

    def test_nao_vende_consumivel(self):
        from src.sim.progression import _descartavel

        heroi = Warrior("Bot")
        pocao = get_all_items()["Poção de Cura Pequena"]
        assert not descartavel_seguro(heroi, pocao, _descartavel)

    def test_vende_item_de_outra_classe(self):
        from src.sim.progression import _descartavel

        heroi = Warrior("Bot")
        alheio = next(
            i for i in get_all_items().values() if i.classes and "Warrior" not in i.classes
        )
        heroi.inventory.append(alheio)
        assert _descartavel(heroi, alheio)

    def test_a_venda_do_bot_usa_a_funcao_do_jogo(self):
        """Mesma `Shop.sell_item`, mesmo preço, sem fórmula duplicada."""
        from src.sim.progression import _vender_dominados

        loja = Shop()
        heroi, armas, _ = self._com_arma(True)
        boa, segunda, ruim = armas[-1], armas[-2], armas[0]
        for arma in (boa, segunda):
            heroi.inventory.append(arma)
            heroi.equip(arma)
        heroi.inventory.append(ruim)
        esperado = loja.get_sell_price(ruim, 7)
        _vender_dominados(heroi, loja, 7)
        assert heroi.coins == esperado

    def test_o_ouro_de_venda_chega_a_telemetria(self):
        from src.sim.harness import simulate_run

        r = simulate_run("Warrior", 8, 6, "smart", loadout="expected", collect_telemetry=True)
        economia = r["telemetry"]["economy"]
        assert economia["items_sold"] > 0, "o bot ainda não vende nada"
        assert economia["gold_from_sales"] > 0
        assert economia["gold_from_sales"] <= economia["total_liquid_gold_inflow"]


def descartavel_seguro(heroi, item, fn) -> bool:
    heroi.inventory.append(item)
    return fn(heroi, item)


class TestTelemetriaPorFaixa:
    def test_o_andar_cai_na_faixa_certa(self):
        from src.sim.telemetry import band_index, band_label

        assert [band_index(f) for f in (1, 5, 6, 10, 11, 20, 21, 25)] == [0, 0, 1, 1, 2, 3, 4, 4]
        assert band_label(0) == "1-5"
        assert band_label(4) == "21-25"

    def test_as_faixas_nao_tem_teto(self):
        """A masmorra é infinita: o andar 137 tem faixa como qualquer outro."""
        from src.sim.telemetry import band_index, band_label

        assert band_label(band_index(137)) == "136-140"

    def test_o_livro_caixa_e_creditado_a_faixa_do_andar(self):
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.start_run()
        livro = {"gold_from_combat": 0, "gold_from_interest": 0, "gold_from_sale": 0}

        livro["gold_from_combat"] = 100
        t.record_floor(3, livro, coins=40)
        livro["gold_from_combat"] = 250
        livro["gold_from_interest"] = 10
        t.record_floor(7, livro, coins=90)

        assert t.by_band[0].gold_from_combat == 100
        assert t.by_band[0].gold_from_interest == 0
        assert t.by_band[1].gold_from_combat == 150, "o delta do andar foi para a faixa errada"
        assert t.by_band[1].gold_from_interest == 10
        assert t.by_band[0].carrying_balance == 40

    def test_juros_e_venda_nao_viram_recompensa_de_combate(self):
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.start_run()
        t.record_floor(2, {"gold_from_interest": 30, "gold_from_sale": 70}, coins=100)
        faixa = t.by_band[0]
        assert faixa.gold_from_combat == 0
        assert faixa.gold_from_interest == 30
        assert faixa.gold_from_sales == 70
        assert faixa.total_liquid_gold_inflow == 100

    def test_conta_andares_e_runs_observados(self):
        """Sem o tamanho da amostra, a média da faixa profunda engana."""
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        for _ in range(3):
            t.start_run()
            for andar in (1, 2, 3):
                t.record_floor(andar, {}, coins=0)
        t.start_run()
        for andar in (1, 2, 3, 6, 7):
            t.record_floor(andar, {}, coins=0)

        assert t.by_band[0].floors_observed == 12
        assert t.by_band[0].runs_observed == 4
        assert t.by_band[1].floors_observed == 2
        assert t.by_band[1].runs_observed == 1

    def test_uma_run_nova_nao_herda_o_livro_da_anterior(self):
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.start_run()
        t.record_floor(1, {"gold_from_combat": 500}, coins=0)
        t.start_run()
        t.record_floor(1, {"gold_from_combat": 80}, coins=0)
        assert t.by_band[0].gold_from_combat == 580, (
            "o retrato do livro atravessou a fronteira da run e produziu delta negativo"
        )

    def test_interest_payments_ignora_pagamento_zero(self, heroi):
        """Definição: contam só os pagamentos maiores que zero."""
        assert economy.pay_interest(heroi, 3) == 0
        assert heroi.ledger["interest_payments"] == 0
        heroi.earn_coins(500)
        assert economy.pay_interest(heroi, 4) > 0
        assert heroi.ledger["interest_payments"] == 1

    def test_a_serializacao_traz_as_faixas(self):
        from src.sim.telemetry import RunTelemetry

        t = RunTelemetry()
        t.start_run()
        t.record_floor(12, {"gold_from_combat": 900}, coins=300)
        faixa = t.to_dict()["economy_by_band"]["11-15"]
        assert faixa["gold_from_combat"] == 900
        assert faixa["floors_observed"] == 1
        assert faixa["runs_observed"] == 1
        assert faixa["carrying_balance"] == 300
