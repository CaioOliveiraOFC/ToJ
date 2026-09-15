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
    ENCHANT_COST_GROWTH,
    ENCHANT_FIRST_INCOME_RATIO,
    ENHANCEMENT_COST_GROWTH,
    ENHANCEMENT_COST_ITEM_RATIO,
    ESSENCE_PENALTY_FLOOR,
    ESSENCE_UNPAID_EXIT_PENALTY,
    EXIT_FEE_INCOME_RATIO,
    GEAR_PRICE_INCOME_RATIO,
    INTEREST_CAP_INCOME_RATIO,
    INTEREST_RATE_PERCENT,
    MONSTER_BASE_COIN_REWARD,
    RECOVERY_MP_STEP_INCOME_RATIO,
    RECOVERY_STEP_PERCENT,
    REROLL_COST_GROWTH,
    REROLL_FIRST_INCOME_RATIO,
    SELL_PRICE_MAX_FACTOR,
    SELL_PRICE_MIN_FACTOR,
    SOCKET_COST_INCOME_RATIO,
    UNSOCKET_COST_INCOME_RATIO,
)
from src.shared.formulas import geometric


def floor_income(floor: int, units: float) -> int:
    """Ouro que um andar concluído paga, em média.

    `units` é quantos monstros-padrão daquele andar a população dele vale. Quem
    sabe esse número é quem conhece o gerador de andares, e este módulo não
    conhece — ele faz a aritmética e nada mais.

    Era uma RETA ajustada à mão aqui dentro, com platô em 14 unidades a partir do
    andar 16. A reta tinha sido calibrada contra um plano de andar do simulador
    que levava 14 lutas ao andar 20 contra os 10 monstros que o jogo gera. Com a
    população real, a reta errava 38% para cima no acumulado até o andar 20 e 24%
    para BAIXO no andar 50, onde o platô mentia e o jogo continuava crescendo.

    Quem calcula as unidades é `content/economy.py`, a partir de
    `content/factories/monsters.py` — a mesma fonte que povoa o andar de verdade.
    """
    return int(geometric(MONSTER_BASE_COIN_REWARD, max(1, floor)) * units)


def reroll_price(income: int, rerolls_done: int) -> int:
    """Quanto custa comprar outra amostra, depois de `rerolls_done` tentativas.

        renda × 0,15 × 2 ** tentativas_feitas

    Uma curva só para os três consumidores — loja, skill e passiva. Três
    fórmulas seriam três economias, e a primeira a divergir tornaria "rerollar"
    uma palavra sem preço fixo.

    Cresce dobrando porque a decisão interessante não é a primeira tentativa, é
    a quarta: 15%, 30%, 60%, 120%, 240% da renda do andar. Quem insiste queima o
    capital que compraria equipamento — e essa é a troca, não um castigo.
    """
    tentativas = max(0, int(rerolls_done))
    return max(1, int(income * REROLL_FIRST_INCOME_RATIO * REROLL_COST_GROWTH**tentativas))


def exit_price(income: int) -> int:
    """Quanto custa usar a saída do andar."""
    return max(1, int(income * EXIT_FEE_INCOME_RATIO))


def essence_penalty(unpaid_exits: int) -> float:
    """Quanto uma sequência de saídas não pagas tira do multiplicador."""
    return max(0, int(unpaid_exits)) * ESSENCE_UNPAID_EXIT_PENALTY


def essence_after_penalty(rolled: float, unpaid_exits: int) -> float:
    """O multiplicador efetivo do andar: o sorteado, menos a penalidade.

        efetivo = max(PISO, sorteado - 0,2 × saídas_não_pagas)

    O piso é ABSOLUTO e vale inclusive quando o próprio sorteio já veio baixo:
    um roll de 0,5x com três saídas em aberto continua 0,5x. É o que impede a
    punição de virar espiral — quem está no piso ainda ganha o bastante para
    voltar a lutar, pagar uma saída e zerar tudo.
    """
    return max(ESSENCE_PENALTY_FLOOR, float(rolled) - essence_penalty(unpaid_exits))


def enhancement_price(item_price: int, current_level: int) -> int:
    """Custo de subir uma peça de `+N` para `+N+1`.

    Proporção do PREÇO DA PEÇA, e não da renda do andar: o que se compra é uma
    fração do valor daquele exemplar, então aprimorar o que já é caro é caro.
    Cresce 50% por rank, sem teto — o `+N` não tem hard cap, e quem o segura é
    a conta, não uma regra.
    """
    escala = ENHANCEMENT_COST_GROWTH ** max(0, int(current_level))
    return max(1, int(item_price * ENHANCEMENT_COST_ITEM_RATIO * escala))


def socket_price(income: int) -> int:
    """Custo de engastar uma gema."""
    return max(1, int(income * SOCKET_COST_INCOME_RATIO))


def unsocket_price(income: int) -> int:
    """Custo de retirar uma gema. Metade de engastar, e a pedra volta inteira."""
    return max(1, int(income * UNSOCKET_COST_INCOME_RATIO))


def enchant_price(income: int, layer: int) -> int:
    """Custo da camada `layer` de encantamento (0 para a primeira).

    Dobra por camada. Vale tanto para acrescentar quanto para REENCANTAR: quem
    troca a terceira camada paga o preço da terceira, porque o que se compra é o
    lugar na peça, não a ordem em que se comprou.
    """
    escala = ENCHANT_COST_GROWTH ** max(0, int(layer))
    return max(1, int(income * ENCHANT_FIRST_INCOME_RATIO * escala))


def interest_for(gold: int, income: int) -> int:
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
    return int(min(bruto, interest_cap(income)))


def interest_cap(income: int) -> int:
    """Teto de juros do andar — o que a tela mostra ao jogador."""
    return int(income * INTEREST_CAP_INCOME_RATIO)


def item_price(
    rarity: str, relative_price: float, rarity_reference: float, income: int, consumable: bool
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
    return max(1, int(income * proporcao * peso))


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


def recovery_price(
    income: int, percent: float, ratio: float = RECOVERY_MP_STEP_INCOME_RATIO
) -> int:
    """Custo de restaurar `percent` do máximo de um recurso, no andar dado.

    Linear no que é de fato restaurado, e cobrado só sobre isso: quem está a 90%
    paga por 10%, não por um passo inteiro. O preço por passo é calibrado para
    que a cura completa custe quase a renda de um andar — cara o bastante para
    competir com equipamento, e não tão cara que o combate ruim vire sentença.
    """
    if percent <= 0:
        return 0
    passos = percent / RECOVERY_STEP_PERCENT
    return max(1, int(income * ratio * passos))
