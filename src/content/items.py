from src.shared.constants import RARITY_MULTIPLIERS


class Item:
    """Classe base para todos os itens do jogo.

    Args:
        name: Nome do item.
        description: Descrição do item.
        rarity: Raridade do item (default: "Common").

    Attributes:
        name: Nome do item.
        description: Descrição do item.
        rarity: Raridade do item.
    """

    def __init__(self, name: str, description: str, rarity: str = "Common") -> None:
        self.name: str = name
        self.description: str = description
        self.rarity: str = rarity

class Weapon(Item):
    """Classe para itens que são armas.

    Args:
        name: Nome da arma.
        description: Descrição da arma.
        base_damage: Dano base da arma.
        rarity: Raridade da arma (default: "Common").

    Attributes:
        base_damage: Dano base da arma.
        damage_bonus: Bônus de dano calculado baseado na raridade.
        slot: Slot de equipamento (sempre "Weapon").
    """

    def __init__(self, name: str, description: str, base_damage: int, rarity: str = "Common") -> None:
        super().__init__(name, description, rarity)
        self.base_damage: int = base_damage
        self.damage_bonus: int = int(base_damage * RARITY_MULTIPLIERS[rarity])
        self.slot: str = "Weapon"

class Armor(Item):
    """Classe para itens que são armaduras.

    Esta é uma representação genérica para itens que podem ser lootados.
    A implementação detalhada da armadura está em armor.py.

    Args:
        name: Nome da armadura.
        description: Descrição da armadura.
        base_defense: Defesa base da armadura.
        slot: Slot de equipamento (ex: "Helmet", "Body", "Legs", "Shoes").
        rarity: Raridade da armadura (default: "Common").

    Attributes:
        base_defense: Defesa base da armadura.
        defense_bonus: Bônus de defesa calculado baseado na raridade.
        slot: Slot de equipamento.
    """

    def __init__(self, name: str, description: str, base_defense: int, slot: str, rarity: str = "Common") -> None:
        super().__init__(name, description, rarity)
        self.base_defense: int = base_defense
        self.defense_bonus: int = int(base_defense * RARITY_MULTIPLIERS[rarity])
        self.slot: str = slot

class Potion(Item):
    """Classe para itens consumíveis, como poções.

    Args:
        name: Nome da poção.
        description: Descrição da poção.
        base_effect_value: Valor base do efeito da poção.
        potion_type: Tipo da poção (ex: "Health", "Mana", "Strength", "Defense", "Agility").
        rarity: Raridade da poção (default: "Common").

    Attributes:
        potion_type: Tipo do efeito da poção.
        base_effect_value: Valor base do efeito.
        effect_value: Valor do efeito calculado baseado na raridade.
    """

    def __init__(self, name: str, description: str, base_effect_value: int, potion_type: str = "Health", rarity: str = "Common") -> None:
        super().__init__(name, description, rarity)
        self.potion_type: str = potion_type
        self.base_effect_value: int = base_effect_value
        self.effect_value: int = int(base_effect_value * RARITY_MULTIPLIERS[rarity])

# --- Definição dos Itens do Jogo ---

# Armas
espada_curta = Weapon("Espada Curta", "Uma espada básica e confiável.", 5, "Common")
cajado_simples = Weapon("Cajado Simples", "Um cajado de madeira para iniciantes.", 3, "Common")
adaga_agil = Weapon("Adaga Ágil", "Uma adaga leve, perfeita para ataques rápidos.", 4, "Common")
espada_longa_rara = Weapon("Espada Longa Rara", "Uma espada bem balanceada, com um brilho sutil.", 8, "Rare")
machado_de_batalha_epico = Weapon("Machado de Batalha Épico", "Um machado pesado que causa grande estrago.", 12, "Epic")
arco_lendario = Weapon("Arco Lendário", "Um arco antigo, dizem que nunca erra o alvo.", 15, "Legendary")

# Armaduras (representações genéricas para loot)
# As armaduras detalhadas com slots e defesa são definidas em armor.py
elmo_de_couro = Armor("Elmo de Couro", "Proteção simples para a cabeça.", 2, "Helmet", "Common")
peitoral_de_ferro = Armor("Peitoral de Ferro", "Oferece boa proteção para o torso.", 5, "Body", "Common")
botas_de_couro_raras = Armor("Botas de Couro Raras", "Botas leves que oferecem alguma proteção.", 3, "Shoes", "Rare")
perneiras_de_placa_epicas = Armor("Perneiras de Placa Épicas", "Proteção pesada para as pernas.", 7, "Legs", "Epic")

# Poções
pocao_de_cura_pequena = Potion("Poção de Cura Pequena", "Restaura uma pequena quantidade de vida.", 50, "Health", "Common")
pocao_de_cura_media = Potion("Poção de Cura Média", "Restaura uma quantidade moderada de vida.", 100, "Health", "Rare")
pocao_de_mana_pequena = Potion("Poção de Mana Pequena", "Restaura uma pequena quantidade de mana.", 30, "Mana", "Common")
pocao_de_forca = Potion("Poção de Força", "Aumenta temporariamente o dano em 15%. (Efeito: +15)", 15, "Strength", "Rare")
pocao_de_defesa = Potion("Poção de Defesa", "Aumenta temporariamente a defesa em 10. (Efeito: +10)", 10, "Defense", "Rare")
pocao_de_agilidade = Potion("Poção de Agilidade", "Aumenta temporariamente a agilidade em 20%. (Efeito: +20)", 20, "Agility", "Epic")
pocao_de_cura_epica = Potion("Poção de Cura Épica", "Restaura uma grande quantidade de vida.", 200, "Health", "Epic")

# 5 Novas Poções com efeitos escaláveis
pocao_de_cura_maior = Potion("Poção de Cura Maior", "Restaura uma grande quantidade de vida. Muito potente.", 400, "Health", "Legendary")
pocao_de_mana_maior = Potion("Poção de Mana Maior", "Restaura uma grande quantidade de mana.", 150, "Mana", "Epic")
elixir_da_potencia = Potion("Elixir da Potência", "Aumenta significativamente o atributo de força por um tempo.", 30, "Strength", "Epic")
elixir_da_resiliencia = Potion("Elixir da Resiliência", "Aumenta significativamente o atributo de defesa por um tempo.", 20, "Defense", "Epic")
pocao_da_velocidade = Potion("Poção da Velocidade", "Aumenta drasticamente o atributo de agilidade por um tempo.", 40, "Agility", "Legendary")


# --- REGISTRO CENTRAL DE ITENS ---
# Este dicionário mapeia o nome de cada item ao seu objeto.
# É essencial para a função de carregar o jogo.
ALL_ITEMS = {
    # Weapons
    espada_curta.name: espada_curta,
    cajado_simples.name: cajado_simples,
    adaga_agil.name: adaga_agil,
    espada_longa_rara.name: espada_longa_rara,
    machado_de_batalha_epico.name: machado_de_batalha_epico,
    arco_lendario.name: arco_lendario,

    # Armors (generic for items.py)
    elmo_de_couro.name: elmo_de_couro,
    peitoral_de_ferro.name: peitoral_de_ferro,
    botas_de_couro_raras.name: botas_de_couro_raras,
    perneiras_de_placa_epicas.name: perneiras_de_placa_epicas,

    # Potions
    pocao_de_cura_pequena.name: pocao_de_cura_pequena,
    pocao_de_cura_media.name: pocao_de_cura_media,
    pocao_de_mana_pequena.name: pocao_de_mana_pequena,
    pocao_de_forca.name: pocao_de_forca,
    pocao_de_defesa.name: pocao_de_defesa,
    pocao_de_agilidade.name: pocao_de_agilidade,
    pocao_de_cura_epica.name: pocao_de_cura_epica,
    pocao_de_cura_maior.name: pocao_de_cura_maior,
    pocao_de_mana_maior.name: pocao_de_mana_maior,
    elixir_da_potencia.name: elixir_da_potencia,
    elixir_da_resiliencia.name: elixir_da_resiliencia,
    pocao_da_velocidade.name: pocao_da_velocidade,
}
