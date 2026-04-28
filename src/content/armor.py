RARITY_MULTIPLIERS = {
    "Common": 1.0,
    "Rare": 1.15,
    "Epic": 1.32, # ~1.15 * 1.15
    "Legendary": 1.52, # ~1.15 * 1.15 * 1.15
}

class Armor:
    """
    Classe base para todas as armaduras.
    """
    def __init__(self, name, rarity="Common"):
        self.name = name
        self.rarity = rarity
        self.equipped = False

    def get_name(self):
        return self.name

    def get_rarity(self):
        return self.rarity

    def is_equipped(self):
        return self.equipped

    def set_equipped(self):
        self.equipped = True

class Shoes(Armor):
    """
    Classe para a armadura do tipo Sapatos.
    """
    base_df = 10

    def __init__(self, name, add_df=0, rarity="Common"):
        super().__init__(name, rarity)
        self._base_df_value = Shoes.base_df + add_df
        self._df = int(self._base_df_value * RARITY_MULTIPLIERS[rarity])
        self.classes = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Shoes'

    def get_df(self):
        return self._df

class Legs(Armor):
    """
    Classe para a armadura do tipo Calças.
    """
    base_df = 12

    def __init__(self, name, add_df=0, rarity="Common"):
        super().__init__(name, rarity)
        self._base_df_value = Legs.base_df + add_df
        self._df = int(self._base_df_value * RARITY_MULTIPLIERS[rarity])
        self.classes = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Legs'

    def get_df(self):
        return self._df

class Helmet(Armor):
    """
    Classe para a armadura do tipo Capacete.
    """
    base_df = 8

    def __init__(self, name, add_df=0, rarity="Common"):
        super().__init__(name, rarity)
        self._base_df_value = Helmet.base_df + add_df
        self._df = int(self._base_df_value * RARITY_MULTIPLIERS[rarity])
        self.classes = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Helmet'

    def get_df(self):
        return self._df

class Body(Armor):
    """
    Classe para a armadura do tipo Peitoral.
    """
    base_df = 15

    def __init__(self, name, add_df=0, rarity="Common"):
        super().__init__(name, rarity)
        self._base_df_value = Body.base_df + add_df
        self._df = int(self._base_df_value * RARITY_MULTIPLIERS[rarity])
        self.classes = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Body'

    def get_df(self):
        return self._df

# --- Definição das Armaduras do Jogo ---

# Sapatos
sapatos_de_couro = Shoes("Sapatos de Couro", rarity="Common")
sapatos_de_ladrao_raros = Shoes("Sapatos do Ladrão", add_df=2, rarity="Rare")

# Calças
calcas_de_linho = Legs("Calças de Linho", rarity="Common")
calcas_de_ferro_epicas = Legs("Calças de Ferro Forjado", add_df=5, rarity="Epic")

# Capacetes
elmo_simples = Helmet("Elmo Simples", rarity="Common")
cacete_lendario = Helmet("Capacete do Guardião Lendário", add_df=10, rarity="Legendary")

# Peitorais
peitoral_acolchoado = Body("Peitoral Acolchoado", rarity="Common")
armadura_de_placa_rara = Body("Armadura de Placa Temperada", add_df=7, rarity="Rare")

# --- REGISTRO CENTRAL DE ARMADURAS ---
ALL_ARMOR = {
    sapatos_de_couro.name: sapatos_de_couro,
    sapatos_de_ladrao_raros.name: sapatos_de_ladrao_raros,
    calcas_de_linho.name: calcas_de_linho,
    calcas_de_ferro_epicas.name: calcas_de_ferro_epicas,
    elmo_simples.name: elmo_simples,
    cacete_lendario.name: cacete_lendario,
    peitoral_acolchoado.name: peitoral_acolchoado,
    armadura_de_placa_rara.name: armadura_de_placa_rara,
}
