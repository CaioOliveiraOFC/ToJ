from src.shared.constants import RARITY_MULTIPLIERS
from src.data.loader import load_json


class Item:
    """Classe base para todos os itens do jogo.

    Attributes:
        id: Identificador único do item.
        name: Nome do item.
        description: Descrição do item.
        rarity: Raridade do item.
        slot: Slot de equipamento.
        classes: Lista de classes que podem usar o item (None = todas).
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        rarity: str = "Common",
        slot: str = "Body",
        damage_bonus: int = 0,
        defense_bonus: int = 0,
        effect_type: str | None = None,
        effect_value: int = 0,
        classes: list[str] | None = None,
        sold_in_shop: bool = True,
        droppable: bool = True,
        price: int = 50,
        shop_min_floor: int = 1,
        shop_max_floor: int | None = None,
    ) -> None:
        self.id: str = item_id
        self.name: str = name
        self.description: str = description
        self.rarity: str = rarity
        self.slot: str = slot
        self.damage_bonus: int = damage_bonus
        self.defense_bonus: int = defense_bonus
        self.effect_type: str | None = effect_type
        self.effect_value: int = effect_value
        self.classes: list[str] | None = classes
        self.sold_in_shop: bool = sold_in_shop
        self.droppable: bool = droppable
        self.price: int = price
        self.shop_min_floor: int = shop_min_floor
        self.shop_max_floor: int | None = shop_max_floor

        if effect_type and effect_value:
            multiplier = RARITY_MULTIPLIERS.get(rarity, 1.0)
            if effect_type in ("max_hp", "max_mp", "agility", "strength", "defense"):
                self.effect_value = int(effect_value * multiplier)

    @property
    def is_potion(self) -> bool:
        """Verifica se o item é uma poção (legacy)."""
        return self.effect_type in ("max_hp", "max_mp", "agility", "strength", "defense")
    
    @property
    def is_usable(self) -> bool:
        """Verifica se o item pode ser usado (não é equipamento)."""
        if not self.effect_type or self.effect_value <= 0:
            return False
        return self.effect_type in (
            "max_hp", "max_mp", "agility", "strength", "defense",
            "speed", "evasion", "crit_chance", "crit_damage",
            "life_steal", "mana_regen"
        )


def _create_item_from_json(item_data: dict) -> Item:
    """Cria um objeto Item a partir de dados do JSON."""
    return Item(
        item_id=item_data.get("id", ""),
        name=item_data.get("name", ""),
        description=item_data.get("description", ""),
        rarity=item_data.get("rarity", "Common"),
        slot=item_data.get("slot", "Body"),
        damage_bonus=item_data.get("damage_bonus", 0),
        defense_bonus=item_data.get("defense_bonus", 0),
        effect_type=item_data.get("effect_type"),
        effect_value=item_data.get("effect_value", 0),
        classes=item_data.get("classes"),
        sold_in_shop=item_data.get("sold_in_shop", True),
        droppable=item_data.get("droppable", True),
        price=item_data.get("price", 50),
        shop_min_floor=item_data.get("shop_min_floor", 1),
        shop_max_floor=item_data.get("shop_max_floor", None),
    )


# --- GERADOR DINÂMICO DE ITENS ---

_ALL_ITEMS_CACHE: dict[str, Item] | None = None


def _load_all_items() -> dict[str, Item]:
    """Carrega todos os itens do JSON e gera ALL_ITEMS."""
    global _ALL_ITEMS_CACHE
    if _ALL_ITEMS_CACHE is not None:
        return _ALL_ITEMS_CACHE

    data = load_json("items.json")
    items_list = data.get("items", [])

    _ALL_ITEMS_CACHE = {}
    for item_data in items_list:
        item = _create_item_from_json(item_data)
        _ALL_ITEMS_CACHE[item.name] = item

    return _ALL_ITEMS_CACHE


def get_all_items() -> dict[str, Item]:
    """Retorna o dicionário de todos os itens (gerado dinamicamente do JSON)."""
    return _load_all_items()


# Alias para compatibilidade
ALL_ITEMS = property(lambda self: _load_all_items())


def reload_items() -> None:
    """Recarrega os itens (útil para desenvolvimento)."""
    global _ALL_ITEMS_CACHE
    _ALL_ITEMS_CACHE = None
    _load_all_items()


# --- COMPATIBILIDADE COM CÓDIGO EXISTENTE ---
# Para acesso direto via Item class (não recomendado, use get_all_items())

def __getattr__(name: str) -> Item:
    items = _load_all_items()
    if name in items:
        return items[name]
    raise AttributeError(f"Item '{name}' not found")


# Garante que ALL_ITEMS esteja carregado ao importar
_load_all_items()


# --- COMPATIBILIDADE COM CÓDIGO EXISTENTE ---
# Para manter compatibilidade com código que espera classes separadas

class Weapon(Item):
    """Classe de compatibilidade para armas."""
    pass


class Armor(Item):
    """Classe de compatibilidade para armaduras."""
    pass


class Potion(Item):
    """Classe de compatibilidade para poções."""
    pass


# Exporta ALL_ITEMS para compatibilidade (propriedade dinâmica)
class _ALL_ITEMS_Dict:
    """Proxy para manter compatibilidade com ALL_ITEMS."""
    def __getitem__(self, key):
        return _load_all_items()[key]
    
    def __contains__(self, key):
        return key in _load_all_items()
    
    def keys(self):
        return _load_all_items().keys()
    
    def values(self):
        return _load_all_items().values()
    
    def items(self):
        return _load_all_items().items()
    
    def __len__(self):
        return len(_load_all_items())
    
    def get(self, key, default=None):
        return _load_all_items().get(key, default)


ALL_ITEMS = _ALL_ITEMS_Dict()