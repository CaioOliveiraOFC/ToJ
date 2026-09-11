"""Fonte única de verdade do dinheiro: preço, venda, juros e recuperação paga.

`shared/economy.py` tem a aritmética e não conhece o jogo. Este módulo é a ponte:
conhece o catálogo de itens, o herói e o andar, e é o **único** lugar que qualquer
outra camada deve chamar para perguntar quanto custa alguma coisa.

Antes disso a resposta dependia de quem perguntava. A fórmula de preço existia em
quatro cópias, e o fator de venda em quatro — três delas um `0.5` escrito à mão
que ignorava a constante. Duas dessas cópias estavam em `ui/`, ou seja: o número
que o jogador lia na tela e o número que ele recebia eram calculados em lugares
diferentes, e nada garantia que fossem iguais.

Se um efeito econômico novo aparecer depois (bônus de venda, ouro extra contra um
arquétipo, juros em equipamento), ele entra aqui, em uma função, e o jogo inteiro
o respeita. É esse o motivo de centralizar — não elegância.
"""

from __future__ import annotations

import statistics
from typing import TYPE_CHECKING

from src.content.items import get_all_items
from src.shared import economy as formulas
from src.shared.constants import (
    RECOVERY_HP_STEP_INCOME_RATIO,
    RECOVERY_MP_STEP_INCOME_RATIO,
    RECOVERY_STEP_PERCENT,
)

if TYPE_CHECKING:
    from src.content.items import Item
    from src.entities.heroes import Player

# Referência de preço por (raridade, é consumível). O `price` do JSON diz o valor
# RELATIVO do item dentro do seu grupo; a mediana do grupo é o que traduz isso em
# proporção da renda do andar. Mediana e não média: um Legendary de 2800 puxaria
# a média do grupo inteiro e achataria todos os outros.
_REFERENCIA: dict[tuple[str, bool], float] | None = None


def _referencias() -> dict[tuple[str, bool], float]:
    global _REFERENCIA
    if _REFERENCIA is None:
        grupos: dict[tuple[str, bool], list[float]] = {}
        for item in get_all_items().values():
            chave = (
                str(getattr(item, "rarity", "Common")),
                bool(getattr(item, "consumable", False)),
            )
            grupos.setdefault(chave, []).append(float(getattr(item, "price", 50)))
        _REFERENCIA = {chave: statistics.median(precos) for chave, precos in grupos.items()}
    return _REFERENCIA


def reload_prices() -> None:
    """Descarta a referência de preço (útil quando o catálogo é recarregado)."""
    global _REFERENCIA
    _REFERENCIA = None


def price_of(item: "Item", dungeon_level: int) -> int:
    """Preço de compra do item no andar dado."""
    raridade = str(getattr(item, "rarity", "Common"))
    consumivel = bool(getattr(item, "consumable", False))
    referencia = _referencias().get((raridade, consumivel), float(getattr(item, "price", 50)))
    return formulas.item_price(
        raridade, float(getattr(item, "price", 50)), referencia, dungeon_level, consumivel
    )


def sell_value_of(item: "Item", dungeon_level: int) -> int:
    """Quanto o mercador paga pelo item no andar dado.

    A mesma função serve a loja e a tela: era em cima dessa divergência que o
    jogador via "vale 120" e recebia outro número.
    """
    return formulas.sell_value(
        price_of(item, dungeon_level), str(getattr(item, "id", getattr(item, "name", "?")))
    )


def expected_floor_income(dungeon_level: int) -> int:
    """Renda esperada do andar — a âncora de toda a escala econômica."""
    return formulas.expected_floor_income(dungeon_level)


# --- Juros -----------------------------------------------------------------


def pay_interest(player: "Player", dungeon_level: int) -> int:
    """Paga os juros do andar concluído, no máximo uma vez por andar.

    A trava mora no herói (`last_interest_floor`) e é salva junto com ele, e não
    no laço que chama: laço tem dois (o jogo e o simulador), o save pode voltar
    no meio do andar, e "exatamente um pagamento por andar concluído" é uma
    regra do dinheiro, não do laço. Quem paga duas vezes imprime moeda.
    """
    if dungeon_level <= int(getattr(player, "last_interest_floor", 0)):
        return 0
    juros = formulas.interest_for(int(getattr(player, "coins", 0)), dungeon_level)
    player.last_interest_floor = dungeon_level
    if juros > 0:
        player.earn_coins(juros, source="interest")
    return juros


def interest_preview(player: "Player", dungeon_level: int) -> tuple[int, int]:
    """O que os juros pagariam agora e qual é o teto do andar — para a tela.

    Existe para o jogador poder decidir: sem ver o rendimento antes de gastar,
    "guardar capital" não é uma opção, é uma aposta às cegas.
    """
    return (
        formulas.interest_for(int(getattr(player, "coins", 0)), dungeon_level),
        formulas.interest_cap(dungeon_level),
    )


# --- Recuperação paga ------------------------------------------------------

# Cada recurso: rótulo, quanto falta, quanto restaurar, proporção do preço.
_RECURSOS = {
    "hp": ("Vida", RECOVERY_HP_STEP_INCOME_RATIO),
    "mp": ("Mana", RECOVERY_MP_STEP_INCOME_RATIO),
}


def _faltando(player: "Player", resource: str) -> tuple[int, int]:
    """Quanto falta e qual é o máximo do recurso."""
    if resource == "hp":
        return max(0, int(player.base_hp) - int(player.get_hp())), int(player.base_hp)
    return max(0, int(player.base_mp) - int(player.get_mp())), int(player.base_mp)


def recovery_offers(player: "Player", dungeon_level: int) -> list[dict]:
    """As compras de recuperação disponíveis, já com preço e efeito.

    Um passo por recurso, não cura completa de botão único: se "encher tudo"
    fosse a única oferta, a decisão econômica desapareceria — ou dá para pagar e
    é sempre certo pagar, ou não dá e não há decisão nenhuma. Em passos, o
    jogador escolhe **quanto** reparar, e pode parar na metade para comprar
    outra coisa.
    """
    ofertas: list[dict] = []
    for recurso, (rotulo, ratio) in _RECURSOS.items():
        falta, maximo = _faltando(player, recurso)
        if falta <= 0 or maximo <= 0:
            continue
        percentual = min(RECOVERY_STEP_PERCENT, falta * 100 / maximo)
        quantidade = max(1, int(maximo * percentual / 100))
        ofertas.append(
            {
                "resource": recurso,
                "label": rotulo,
                "amount": quantidade,
                "percent": percentual,
                "price": formulas.recovery_price(dungeon_level, percentual, ratio),
            }
        )
    return ofertas


def buy_recovery(player: "Player", dungeon_level: int, resource: str) -> dict | None:
    """Compra um passo de recuperação. Devolve a oferta paga, ou None.

    None cobre os dois jeitos de não comprar — recurso já cheio e ouro
    insuficiente — e em nenhum dos dois o herói é alterado.
    """
    oferta = next(
        (o for o in recovery_offers(player, dungeon_level) if o["resource"] == resource), None
    )
    if oferta is None:
        return None
    if not player.spend_coins(int(oferta["price"]), source="recovery"):
        return None
    if resource == "hp":
        player.heal(int(oferta["amount"]))
    else:
        player.restore_mp(int(oferta["amount"]))
    return oferta
