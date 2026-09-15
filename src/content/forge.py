"""O Ferreiro: acesso, custo e contabilidade dos três eixos de equipamento.

A mecânica dos três já existia e funcionava — `Item.increase_enhancement`,
`Item.socket`/`unsocket`, `Item.enchant` — e mesmo assim nenhum jogador jamais
tinha aprimorado uma espada. Faltava a PORTA: um lugar onde gastar ouro para
mexer no equipamento. Era a diferença entre "implementado" e "jogável", e é só
isso que este módulo acrescenta.

Não há regra nova de item aqui. Cada serviço faz três coisas, nesta ordem:

    cobra pelo preço central  →  chama a mecânica que já existe  →  registra

Nenhuma operação altera estado antes de a cobrança passar. Sem ouro, nada
acontece: nem o item muda, nem a bolsa, nem o contador.

O Ferreiro não tem teto em nada. `+N` não para, encantamento só esbarra no
`MAX_ENCHANTMENTS` mecânico, e engastar não tem limite além dos sockets da peça.
O que segura é a conta — e o mesmo ouro que paga o Ferreiro é o que compraria
equipamento na loja, poção, recuperação ou um reroll.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.content.economy import (
    enchant_cost,
    enhancement_cost,
    reenchant_cost,
    socket_cost,
    unsocket_cost,
)
from src.content.enchantments import MAX_ENCHANTMENTS, roll_enchantment
from src.content.gems import roll_gem_drop

if TYPE_CHECKING:
    from src.content.gems import Gem
    from src.content.items import Item
    from src.entities.heroes import Player


def award_gem(player: "Player", dungeon_level: int, rng=None) -> "Gem | None":
    """Rola a gema desta vitória e, se cair, põe na bolsa. Devolve a pedra.

    A porta única do drop de gema: jogo e simulador chamam esta, e é por isso
    que a chance medida na simulação é a chance que o jogador vive. A rolagem é
    independente do loot de item — as duas acontecem na mesma vitória e nenhuma
    tira a vez da outra.

    A pedra vai para `player.gems`, e não para o inventário: gema não é
    equipamento nem consumível, e todo consumidor de `inventory` — a loja, o
    descarte do bot, a tela de itens do combate — teria de aprender a ignorá-la.
    """
    gema = roll_gem_drop(dungeon_level, rng or random)
    if gema is None:
        return None
    player.gems.append(gema)
    player.ledger["gems_found"] = player.ledger.get("gems_found", 0) + 1
    return gema


def enhanceable(player: "Player") -> list["Item"]:
    """As peças que o Ferreiro aceita aprimorar: o que está equipado."""
    return [item for item in player.equipment.values() if item is not None]


def socketable(player: "Player") -> list["Item"]:
    """As peças equipadas que têm onde cravar uma pedra."""
    return [item for item in enhanceable(player) if int(getattr(item, "socket_count", 0) or 0) > 0]


def enhance(player: "Player", item: "Item", dungeon_level: int) -> int | None:
    """Sobe a peça um rank. Devolve o novo `+N`, ou `None` se não deu.

    Determinístico: não existe chance de falha, e é por isso que o preço precisa
    doer. Quem compra `+1` recebe `+1`.
    """
    custo = enhancement_cost(item, dungeon_level)
    if not player.spend_coins(custo, source="enhancement"):
        return None
    return item.increase_enhancement()


def socket(player: "Player", item: "Item", gem: "Gem", index: int, dungeon_level: int) -> bool:
    """Crava uma pedra da bolsa num socket VAZIO da peça.

    Recusa socket ocupado de propósito. A mecânica de baixo nível sabe
    substituir, e o fluxo real não usa isso: trocar sem retirar seria uma troca
    de graça e um item mudando sem o jogador ter decidido o que sai. Para trocar,
    retira-se primeiro — e paga-se as duas pontas.
    """
    if gem not in player.gems:
        return False
    if not 0 <= index < int(getattr(item, "socket_count", 0) or 0):
        return False
    if item.gems[index] is not None:
        return False
    if not player.spend_coins(socket_cost(dungeon_level), source="socket"):
        return False
    return player.socket_gem(item, gem, index)


def unsocket(player: "Player", item: "Item", index: int, dungeon_level: int) -> "Gem | None":
    """Retira a pedra e devolve à bolsa. Ela não quebra e não perde nível."""
    if not 0 <= index < int(getattr(item, "socket_count", 0) or 0):
        return None
    if item.gems[index] is None:
        return None
    if not player.spend_coins(unsocket_cost(dungeon_level), source="unsocket"):
        return None
    return player.unsocket_gem(item, index)


def enchant(player: "Player", item: "Item", dungeon_level: int, rng=None):
    """Acrescenta uma camada de encantamento sorteada. Devolve ela, ou `None`."""
    camadas = len(getattr(item, "enchantments", ()))
    if camadas >= MAX_ENCHANTMENTS:
        return None
    if not player.spend_coins(enchant_cost(dungeon_level, camadas), source="enchant"):
        return None
    encanto = roll_enchantment(rng or random)
    item.enchant(encanto)
    return encanto


def reenchant(player: "Player", item: "Item", index: int, dungeon_level: int, rng=None):
    """Troca a camada `index` por outro sorteio. Devolve o novo, ou `None`.

    Aposta pura: sai do mesmo sorteio de `enchant`, então não garante efeito
    diferente nem valor maior. O antigo desaparece e não há como voltar.
    """
    if not 0 <= index < len(getattr(item, "enchantments", ())):
        return None
    if not player.spend_coins(reenchant_cost(dungeon_level, index), source="reenchant"):
        return None
    encanto = roll_enchantment(rng or random)
    item.enchant(encanto, index)
    return encanto
