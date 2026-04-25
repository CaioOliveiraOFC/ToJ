import random
import copy

# Rarity system
RARITY_MULTIPLIERS = {
    "Common": 1.0,
    "Rare": 1.15,
    "Epic": 1.32, # ~1.15 * 1.15
    "Legendary": 1.52, # ~1.15 * 1.15 * 1.15
}

class Item:
    """Classe base para todos os itens do jogo."""
    def __init__(self, name, description, rarity="Common"):
        self.name = name
        self.description = description
        self.rarity = rarity

class Weapon(Item):
    """Classe para itens que são armas."""
    def __init__(self, name, description, base_damage, rarity="Common"):
        super().__init__(name, description, rarity)
        self.base_damage = base_damage
        self.damage_bonus = int(base_damage * RARITY_MULTIPLIERS[rarity])
        self.slot = "Weapon"

class Armor(Item):
    """Classe para itens que são armaduras. Esta é uma representação genérica para itens que podem ser lootados, a implementação detalhada da armadura está em armor.py."""
    def __init__(self, name, description, base_defense, slot, rarity="Common"):
        super().__init__(name, description, rarity)
        self.base_defense = base_defense
        self.defense_bonus = int(base_defense * RARITY_MULTIPLIERS[rarity])
        self.slot = slot # Ex: "Helmet", "Body", etc.

class Potion(Item):
    """Classe para itens consumíveis, como poções."""
    def __init__(self, name, description, base_effect_value, potion_type="Health", rarity="Common"):
        super().__init__(name, description, rarity)
        self.potion_type = potion_type # Ex: "Health", "Mana", "Strength", "Defense", "Agility"
        self.base_effect_value = base_effect_value
        self.effect_value = int(base_effect_value * RARITY_MULTIPLIERS[rarity])

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

# --- Tabela de Loot ---
# random.seed(42) # Removido para garantir aleatoriedade real na geração de mapas e loot
loot_table = list(ALL_ITEMS.values())

def get_loot():
    """
    Sorteia um item da tabela de loot. Tem 30% de chance de retornar um item.
    A raridade do item pode influenciar a chance de drop ou os atributos do item.
    """
    if random.randint(1, 100) <= 30: # 30% de chance de drop
        return copy.copy(random.choice(loot_table))
    return None
