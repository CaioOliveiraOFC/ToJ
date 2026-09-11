"""Escala econômica do jogo: renda do andar, preço, venda, juros e recuperação.

Antes deste módulo, a fórmula de preço existia em quatro cópias
(`content/shop.py`, `content/factories/dungeons.py` e duas linhas de venda em
`ui/`), e o fator de venda era uma constante que três chamadores ignoravam para
usar um `0.5` escrito à mão. Mudar a economia significava encontrar todas as
cópias — e a de `ui/` era a que o jogador lia na tela, então divergir dela era
mentir para ele sobre quanto ia receber.

A fonte de verdade é uma só: `expected_floor_income`. Todo o resto do dinheiro do
jogo é uma proporção dela. É isso que impede o defeito estrutural que a economia
tinha — renda geométrica (×1,12 por nível, e mais monstros por andar) contra
preço linear (+5% por andar): no andar 15 o jogador tinha ouro para comprar a
loja inteira, e o ouro deixava de comprar opção alguma.

`shared/` porque `content/`, `engine/`, `sim/` e `ui/` precisam todos da mesma
conta. Este módulo não conhece item, herói nem loja: recebe números e devolve
números. Quem casa o catálogo com estas fórmulas é `content/economy.py`.
"""

from __future__ import annotations

from src.shared.constants import (
    CONSUMABLE_PRICE_INCOME_RATIO,
    FLOOR_INCOME_BASE_UNITS,
    FLOOR_INCOME_MAX_UNITS,
    FLOOR_INCOME_UNITS_PER_FLOOR,
    GEAR_PRICE_INCOME_RATIO,
    INTEREST_CAP_INCOME_RATIO,
    INTEREST_RATE_PERCENT,
    MONSTER_BASE_COIN_REWARD,
    RECOVERY_MP_STEP_INCOME_RATIO,
    RECOVERY_STEP_PERCENT,
    SELL_PRICE_MAX_FACTOR,
    SELL_PRICE_MIN_FACTOR,
)
from src.shared.formulas import geometric


def floor_income_units(floor: int) -> float:
    """Quantos monstros-padrão do andar cabem na renda esperada dele.

    O andar não paga um monstro: paga o plano de andar inteiro, que cresce de
    três encontros nos primeiros andares até estabilizar. Medido no gerador real
    de andares, a razão entre a renda do andar e o valor de um monstro do nível
    dele é 3,1 no andar 1, 9,2 no 10, 13,4 no 15 e **platô em ~14** do 16 em
    diante — o plano de andar para de crescer ali.

    O platô é o que impede a renda de fugir da curva de tudo o mais: acima dele,
    o dinheiro do andar volta a crescer no mesmo ×1,12 de atributo, dano e XP.

    A reta é um envelope de poder de compra, não uma tabela de pagamento. Do
    andar 10 em diante ela erra menos de 10%; entre o 5 e o 9 erra até 67% para
    cima, porque ali o plano de andar sobe e desce (o chefe do 5, depois dois
    andares magros) e nenhuma curva suave acompanha isso. O que importa para
    preço é o acumulado — quanto ouro o jogador tem em mãos ao chegar —, e esse
    fica dentro de 20% em todo andar. `tests/test_economy.py` cobra as duas
    coisas separadamente, contra o gerador de andares de verdade.
    """
    unidades = FLOOR_INCOME_BASE_UNITS + (max(1, floor) - 1) * FLOOR_INCOME_UNITS_PER_FLOOR
    return min(FLOOR_INCOME_MAX_UNITS, unidades)


def expected_floor_income(floor: int) -> int:
    """Ouro que um andar concluído paga, em média.

    Derivada de `MONSTER_BASE_COIN_REWARD` e da curva geométrica do jogo, não de
    uma tabela à parte: se a recompensa por monstro mudar, os preços, o cap de
    juros e o custo de recuperação seguem junto, sem recalibração manual.
    """
    return int(geometric(MONSTER_BASE_COIN_REWARD, max(1, floor)) * floor_income_units(floor))


def interest_for(gold: int, floor: int) -> int:
    """Juros pagos ao concluir um andar, sobre o ouro carregado.

    Existe para criar uma decisão, não para criar dinheiro: o cap é uma fração da
    renda do andar, então o rendimento nunca compete com jogar o andar. E como o
    cap cresce na mesma curva da renda enquanto o juro composto cresceria mais
    rápido, a fortuna grande rende em linha reta e vai perdendo peso relativo —
    é o que impede a bola de neve irrestrita.
    """
    if gold <= 0:
        return 0
    bruto = gold * INTEREST_RATE_PERCENT / 100
    teto = expected_floor_income(floor) * INTEREST_CAP_INCOME_RATIO
    return int(min(bruto, teto))


def interest_cap(floor: int) -> int:
    """Teto de juros do andar — o que a tela mostra ao jogador."""
    return int(expected_floor_income(floor) * INTEREST_CAP_INCOME_RATIO)


def item_price(
    rarity: str, relative_price: float, rarity_reference: float, floor: int, consumable: bool
) -> int:
    """Preço de um item no andar, em proporção à renda esperada dele.

    O `price` do JSON deixa de ser o valor absoluto e passa a ser o valor
    **relativo dentro da raridade**: um Common de 60 continua valendo o dobro de
    um Common de 30, mas a escala de "quanto é um Common" vem da economia do
    andar. É o que faz o Epic continuar caro no andar 20 — antes ele custava 102%
    da renda de um andar e o jogador comprava tudo.

    Consumível tem tabela própria: pela raridade, uma poção pequena seria um
    equipamento Common, e ninguém compra três equipamentos Common por andar.
    """
    tabela = CONSUMABLE_PRICE_INCOME_RATIO if consumable else GEAR_PRICE_INCOME_RATIO
    proporcao = tabela.get(rarity, tabela["Common"])
    peso = (relative_price / rarity_reference) if rarity_reference > 0 else 1.0
    return max(1, int(expected_floor_income(floor) * proporcao * peso))


def sell_factor(item_id: str) -> float:
    """Fração do preço que a venda devolve, entre 20% e 25%.

    Derivada do id, não sorteada: o preço que a tela mostra e o preço que o
    mercador paga têm de ser o mesmo número, e um `random` no meio faria a tela
    mentir. Cada item tem o seu fator, estável entre sessões.
    """
    faixa = SELL_PRICE_MAX_FACTOR - SELL_PRICE_MIN_FACTOR
    # `sum` dos bytes, não `hash()`: `hash` de str é semeado por processo, então
    # o mesmo item venderia por preços diferentes a cada execução do jogo.
    semente = sum(str(item_id).encode("utf-8")) % 1000
    return SELL_PRICE_MIN_FACTOR + faixa * semente / 999


def sell_value(price_at_floor: int, item_id: str) -> int:
    """Quanto o mercador paga por um item cujo preço de venda é `price_at_floor`.

    Entre 20% e 25%: acumular loot para revender não deve ser fonte primária de
    renda. Venda é válvula de descarte e recuperação parcial de valor.
    """
    return max(1, int(price_at_floor * sell_factor(item_id)))


def recovery_price(floor: int, percent: float, ratio: float = RECOVERY_MP_STEP_INCOME_RATIO) -> int:
    """Custo de restaurar `percent` do máximo de um recurso, no andar dado.

    Linear no que é de fato restaurado, e cobrado só sobre isso: quem está a 90%
    paga por 10%, não por um passo inteiro. O preço por passo é calibrado para
    que a cura completa custe quase a renda de um andar — cara o bastante para
    competir com equipamento, e não tão cara que o combate ruim vire sentença.
    """
    if percent <= 0:
        return 0
    passos = percent / RECOVERY_STEP_PERCENT
    return max(1, int(expected_floor_income(floor) * ratio * passos))
