from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.content.economy import price_of, sell_value_of
from src.content.items import Item, get_all_items

if TYPE_CHECKING:
    from src.entities.heroes import Player


class Shop:
    """Representa a loja do jogo onde o jogador pode comprar itens."""

    def __init__(self):
        pass

    def get_price(self, item: Item, dungeon_level: int) -> int:
        """Preço do item neste andar.

        Delega a `content/economy.py`: a loja não tem fórmula própria. A que
        morava aqui (`base * (1 + andar*0.05)`) crescia linearmente contra uma
        renda geométrica, e era uma de quatro cópias espalhadas pelo projeto.
        """
        return price_of(item, dungeon_level)

    def get_available_items(self, dungeon_level: int, player_class: str) -> list[dict]:
        """Retorna uma lista de itens disponíveis para compra na loja, com seus preços.

        Progressão por andar:
        - Andar 1-3: 8-10 itens (Common + 1-2 Rare)
        - Andar 4-6: 12-15 itens (Common + Rare)
        - Andar 7-9: 15-18 itens (Common + Rare + 1-2 Epic se andar >= 10)
        - Andar 10-14: 18-22 itens (Common + Rare + Epic)
        - Andar 15+: 22-25 itens (Common + Rare + Epic, sem Legendary)

        Todo filtro aqui é DESBLOQUEIO, nunca curva por profundidade: um andar
        mais fundo libera coisa, e nunca muda a proporção entre raridades. A
        masmorra é infinita, então a loja do andar 80 tem de ser a mesma do
        andar 16. A distribuição 60/28/10/2 de `items.json` é do **loot**
        (`factories/loot.py`), não daqui — a loja tem os filtros dela.

        `shop_max_floor` deixou de ser o que era. Ele estava declarado como 15
        em 121 itens — 100% dos equipamentos vendáveis e 0% dos consumíveis —,
        o que não é decisão por item, é o default de quando a masmorra acabava
        no andar 20. O efeito era a loja parar de vender equipamento no andar
        16 e o ouro não comprar mais nada. Os 121 valores foram removidos do
        JSON; o campo continua sendo lido, para o caso de alguém querer um item
        genuinamente limitado no tempo, e quem o declarar precisa dizer por quê.
        """
        all_items = get_all_items()
        available_items = []

        for item in all_items.values():
            if not getattr(item, "sold_in_shop", False):
                continue

            shop_min = getattr(item, "shop_min_floor", 1)
            shop_max = getattr(item, "shop_max_floor", None)

            if dungeon_level < shop_min:
                continue
            if shop_max is not None and dungeon_level > shop_max:
                continue

            rarity = getattr(item, "rarity", "Common")
            if rarity == "Legendary":
                continue
            if rarity == "Epic" and dungeon_level < 10:
                continue

            item_classes = getattr(item, "classes", None)
            if item_classes is not None and player_class not in item_classes:
                continue

            price = self.get_price(item, dungeon_level)
            available_items.append({"item": item, "price": price})

        # Define quantos itens mostrar conforme o andar
        if dungeon_level <= 3:
            max_items = random.randint(8, 10)
        elif dungeon_level <= 6:
            max_items = random.randint(12, 15)
        elif dungeon_level <= 9:
            max_items = random.randint(15, 18)
        elif dungeon_level <= 14:
            max_items = random.randint(18, 22)
        else:
            max_items = random.randint(22, 25)

        # Embaralha 100% e pega os primeiros N
        random.shuffle(available_items)
        return available_items[:max_items]

    def get_sell_price(self, item: Item, dungeon_level: int) -> int:
        """Quanto a loja paga pelo item. A tela e a transação chamam esta."""
        return sell_value_of(item, dungeon_level)

    def buy_item(self, player: "Player", item_to_buy: Item, dungeon_level: int) -> bool:
        """Permite ao jogador comprar um item da loja."""
        price = self.get_price(item_to_buy, dungeon_level)
        categoria = "consumable" if getattr(item_to_buy, "consumable", False) else "gear"
        if player.spend_coins(price, source=categoria):
            player.add_item_to_inventory(item_to_buy)
            return True
        return False

    def sell_item(self, player: "Player", item_to_sell: Item, dungeon_level: int) -> bool:
        """Permite ao jogador vender um item para a loja."""
        if player.remove_item_from_inventory(item_to_sell):
            player.earn_coins(self.get_sell_price(item_to_sell, dungeon_level), source="sale")
            player.ledger["items_sold"] = player.ledger.get("items_sold", 0) + 1
            return True
        return False
