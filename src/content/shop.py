from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.items import get_all_items, Item
from src.shared.constants import (
    RARITY_MULTIPLIERS,
    SELL_PRICE_FACTOR,
)

if TYPE_CHECKING:
    from src.entities.heroes import Player


class Shop:
    """Representa a loja do jogo onde o jogador pode comprar itens."""

    def __init__(self):
        pass

    def get_price(self, item: Item, dungeon_level: int) -> int:
        """Calcula o preço de um item baseado no preço base do JSON e nível da dungeon."""
        base_price = getattr(item, "price", 50)
        
        price = base_price * (1 + (dungeon_level * 0.05))
        
        return int(price)

    def get_available_items(self, dungeon_level: int, player_class: str) -> list[dict]:
        """Retorna uma lista de itens disponíveis para compra na loja, com seus preços.
        
        Progressão por andar:
        - Andar 1-3: 8-10 itens (Common + 1-2 Rare)
        - Andar 4-6: 12-15 itens (Common + Rare)
        - Andar 7-9: 15-18 itens (Common + Rare + 1-2 Epic se andar >= 10)
        - Andar 10-14: 18-22 itens (Common + Rare + Epic)
        - Andar 15+: 22-25 itens (Common + Rare + Epic, sem Legendary)
        """
        import random
        
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

    def buy_item(self, player: "Player", item_to_buy: Item, dungeon_level: int) -> bool:
        """Permite ao jogador comprar um item da loja."""
        price = self.get_price(item_to_buy, dungeon_level)
        if player.spend_coins(price):
            player.add_item_to_inventory(item_to_buy)
            return True
        return False

    def sell_item(self, player: "Player", item_to_sell: Item, dungeon_level: int) -> bool:
        """Permite ao jogador vender um item para a loja."""
        if player.remove_item_from_inventory(item_to_sell):
            sell_price = int(self.get_price(item_to_sell, dungeon_level) * SELL_PRICE_FACTOR)
            player.earn_coins(sell_price)
            return True
        return False