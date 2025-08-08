import random

class Item:
    """Classe base para todos os itens do jogo."""
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Weapon(Item):
    """Classe para itens que são armas."""
    def __init__(self, name, description, damage_bonus):
        super().__init__(name, description)
        self.damage_bonus = damage_bonus
        self.slot = "Weapon"

class Armor(Item):
    """Classe para itens que são armaduras."""
    def __init__(self, name, description, defense_bonus, slot):
        super().__init__(name, description)
        self.defense_bonus = defense_bonus
        self.slot = slot # Ex: "Helmet", "Body", etc.

class Potion(Item):
    """Classe para itens consumíveis, como poções."""
    def __init__(self, name, description, heal_amount):
        super().__init__(name, description)
        self.heal_amount = heal_amount

# --- Definição dos Itens do Jogo ---

# Armas
espada_curta = Weapon("Espada Curta", "Uma espada básica e confiável.", 5)
cajado_simples = Weapon("Cajado Simples", "Um cajado de madeira para iniciantes.", 3)
adaga_agil = Weapon("Adaga Ágil", "Uma adaga leve, perfeita para ataques rápidos.", 4)

# Armaduras
elmo_de_couro = Armor("Elmo de Couro", "Proteção simples para a cabeça.", 2, "Helmet")
peitoral_de_ferro = Armor("Peitoral de Ferro", "Oferece boa proteção para o torso.", 5, "Body")

# Poções
pocao_de_cura_pequena = Potion("Poção de Cura Pequena", "Restaura 50 pontos de vida.", 50)

# --- REGISTO CENTRAL DE ITENS ---
# Este dicionário mapeia o nome de cada item ao seu objeto.
# É essencial para a função de carregar o jogo.
ALL_ITEMS = {
    espada_curta.name: espada_curta,
    cajado_simples.name: cajado_simples,
    adaga_agil.name: adaga_agil,
    elmo_de_couro.name: elmo_de_couro,
    peitoral_de_ferro.name: peitoral_de_ferro,
    pocao_de_cura_pequena.name: pocao_de_cura_pequena,
}

# --- Tabela de Loot ---
loot_table = list(ALL_ITEMS.values())

def get_loot():
    """
    Sorteia um item da tabela de loot. Tem 30% de chance de retornar um item.
    """
    if random.randint(1, 100) <= 30: # 30% de chance de drop
        return random.choice(loot_table)
    return None
