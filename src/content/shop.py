from src.content.items import ALL_ITEMS, RARITY_MULTIPLIERS, Armor, Potion, Weapon


class Shop:
    """Representa a loja do jogo onde o jogador pode comprar itens."""

    def __init__(self):
        pass

    def get_price(self, item, dungeon_level):
        """Calcula o preço de um item baseado em sua raridade e nível da dungeon."""
        base_price = 10 # Base price for a common item

        # Adjust base price based on item type
        if isinstance(item, Potion):
            base_price = item.base_effect_value * 2 # Potions are priced based on their effect
        elif isinstance(item, Weapon):
            base_price = item.base_damage * 10
        elif isinstance(item, Armor):
            base_price = item.base_defense * 10

        # Apply rarity multiplier
        price = base_price * RARITY_MULTIPLIERS.get(item.rarity, 1.0)

        # Further adjust price based on dungeon level for higher-tier items
        # This makes items more expensive but also potentially better quality in higher levels
        price *= (1 + (dungeon_level / 20)) # Small scaling with dungeon level

        return int(price)

    def get_available_items(self, dungeon_level):
        """Retorna uma lista de itens disponíveis para compra na loja, com seus preços."""
        available_items = []

        # Determine which items are available based on dungeon level
        # For simplicity, early levels have common/rare, later levels add epic/legendary

        if dungeon_level < 5:
            shop_item_names = [
                "Espada Curta", "Cajado Simples", "Adaga Ágil",
                "Elmo de Couro", "Peitoral de Couro", "Botas de Couro",
                "Poção de Cura Pequena", "Poção de Mana Pequena"
            ]
        elif dungeon_level < 10:
            shop_item_names = [
                "Espada Longa", "Machado de Batalha", "Arco Curto",
                "Peitoral de Ferro", "Manoplas de Ferro", "Escudo Pequeno",
                "Poção de Cura Média", "Poção de Mana Média", "Poção de Força", "Poção de Defesa"
            ]
        elif dungeon_level < 15:
            shop_item_names = [
                "Espada Larga Rara", "Cajado Mágico Raro", "Arco Longo Raro",
                "Peitoral de Placa", "Elmo de Placa", "Escudo Grande",
                "Poção de Cura Maior", "Poção de Mana Maior", "Elixir da Potência", "Elixir da Resiliência"
            ]
        else: # Higher levels
            shop_item_names = [
                "Espada Lendária", "Cajado Arcana Lendário", "Arco Élfico Lendário",
                "Armadura de Dragão Épica", "Luvas de Ouro Épicas", "Escudo Torre Épico",
                "Poção de Cura Épica", "Poção de Mana Épica", "Elixir da Grande Potência", "Elixir da Suprema Resiliência", "Poção da Velocidade"
            ]

        for item_name in shop_item_names:
            item = ALL_ITEMS.get(item_name)
            if item:
                price = self.get_price(item, dungeon_level)
                available_items.append({"item": item, "price": price})

        return available_items

    def buy_item(self, player, item_to_buy, dungeon_level):
        """
        Permite ao jogador comprar um item da loja.
        Retorna True se a compra for bem-sucedida, False caso contrário.
        """
        price = self.get_price(item_to_buy, dungeon_level)
        if player.coins >= price:
            player.coins -= price
            player.inventory.append(item_to_buy)
            return True
        else:
            return False

    def sell_item(self, player, item_to_sell, dungeon_level):
        """
        Permite ao jogador vender um item para a loja.
        Retorna True se a venda for bem-sucedida, False caso contrário.
        """
        if item_to_sell in player.inventory:
            sell_price = int(self.get_price(item_to_sell, dungeon_level) * 0.5)
            player.coins += sell_price
            player.inventory.remove(item_to_sell)
            return True
        else:
            return False

