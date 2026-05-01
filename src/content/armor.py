"""
Definições de armaduras - fornecem apenas dados base/conteúdo.

A lógica de cálculo de defesa efetiva (aplicação de multiplicadores de raridade,
buffs, etc.) é responsabilidade da camada entities/.
"""


class Armor:
    """Classe base para todas as armaduras.

    Fornece apenas dados base; cálculo de defesa efetiva é feito por entities/.

    Args:
        name: Nome da armadura.
        rarity: Raridade da armadura (default: "Common").
        base_defense: Defesa base da armadura (default: 0).
        bonus_defense: Bônus de defesa adicional (default: 0).

    Attributes:
        name: Nome da armadura.
        rarity: Raridade da armadura.
        equipped: Indica se a armadura está equipada.
        base_defense: Defesa base da armadura.
        bonus_defense: Bônus de defesa adicional.
    """

    def __init__(self, name: str, rarity: str = "Common", base_defense: int = 0, bonus_defense: int = 0) -> None:
        self.name: str = name
        self.rarity: str = rarity
        self.equipped: bool = False
        self.base_defense: int = base_defense
        self.bonus_defense: int = bonus_defense

    def get_name(self) -> str:
        """Retorna o nome da armadura."""
        return self.name

    def get_rarity(self) -> str:
        """Retorna a raridade da armadura."""
        return self.rarity

    def is_equipped(self) -> bool:
        """Retorna True se a armadura está equipada."""
        return self.equipped

    def set_equipped(self) -> None:
        """Marca a armadura como equipada."""
        self.equipped = True

    def get_base_defense(self) -> int:
        """Retorna a defesa base (sem multiplicadores de raridade)."""
        return self.base_defense + self.bonus_defense


class Shoes(Armor):
    """Classe para a armadura do tipo Sapatos.

    Args:
        name: Nome dos sapatos.
        add_df: Bônus de defesa adicional (default: 0).
        rarity: Raridade dos sapatos (default: "Common").
    """

    SLOT_BASE_DEFENSE: int = 10

    def __init__(self, name: str, add_df: int = 0, rarity: str = "Common") -> None:
        super().__init__(
            name=name,
            rarity=rarity,
            base_defense=Shoes.SLOT_BASE_DEFENSE,
            bonus_defense=add_df
        )
        self.classes: list[str] = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self) -> list[str]:
        """Retorna a lista de classes que podem usar este item."""
        return self.classes

    @staticmethod
    def in_space() -> str:
        """Retorna o slot de equipamento."""
        return 'Shoes'


class Legs(Armor):
    """Classe para a armadura do tipo Calças.

    Args:
        name: Nome das calças.
        add_df: Bônus de defesa adicional (default: 0).
        rarity: Raridade das calças (default: "Common").
    """

    SLOT_BASE_DEFENSE: int = 12

    def __init__(self, name: str, add_df: int = 0, rarity: str = "Common") -> None:
        super().__init__(
            name=name,
            rarity=rarity,
            base_defense=Legs.SLOT_BASE_DEFENSE,
            bonus_defense=add_df
        )
        self.classes: list[str] = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self) -> list[str]:
        """Retorna a lista de classes que podem usar este item."""
        return self.classes

    @staticmethod
    def in_space() -> str:
        """Retorna o slot de equipamento."""
        return 'Legs'


class Helmet(Armor):
    """Classe para a armadura do tipo Capacete.

    Args:
        name: Nome do capacete.
        add_df: Bônus de defesa adicional (default: 0).
        rarity: Raridade do capacete (default: "Common").
    """

    SLOT_BASE_DEFENSE: int = 8

    def __init__(self, name: str, add_df: int = 0, rarity: str = "Common") -> None:
        super().__init__(
            name=name,
            rarity=rarity,
            base_defense=Helmet.SLOT_BASE_DEFENSE,
            bonus_defense=add_df
        )
        self.classes: list[str] = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self) -> list[str]:
        """Retorna a lista de classes que podem usar este item."""
        return self.classes

    @staticmethod
    def in_space() -> str:
        """Retorna o slot de equipamento."""
        return 'Helmet'


class Body(Armor):
    """Classe para a armadura do tipo Peitoral.

    Args:
        name: Nome do peitoral.
        add_df: Bônus de defesa adicional (default: 0).
        rarity: Raridade do peitoral (default: "Common").
    """

    SLOT_BASE_DEFENSE: int = 15

    def __init__(self, name: str, add_df: int = 0, rarity: str = "Common") -> None:
        super().__init__(
            name=name,
            rarity=rarity,
            base_defense=Body.SLOT_BASE_DEFENSE,
            bonus_defense=add_df
        )
        self.classes: list[str] = ['Warrior', 'Rogue', 'Mage']

    def get_lst_class(self) -> list[str]:
        """Retorna a lista de classes que podem usar este item."""
        return self.classes

    @staticmethod
    def in_space() -> str:
        """Retorna o slot de equipamento."""
        return 'Body'

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
