from __future__ import annotations

from src.entities.base import Entity
from src.shared.constants import (
    AGILITY_CAP,
    DAMAGE_FORMULA_DIVISOR,
    MAGE_BASE_AG,
    MAGE_BASE_DF,
    MAGE_BASE_HP,
    MAGE_BASE_MG,
    MAGE_BASE_MP,
    MAGE_BASE_ST,
    MAGE_MG_GROWTH_PERCENT,
    MAGE_MP_GROWTH_PERCENT,
    ROGUE_AGILITY_INCREMENT,
    ROGUE_BASE_AG,
    ROGUE_BASE_DF,
    ROGUE_BASE_HP,
    ROGUE_BASE_MG,
    ROGUE_BASE_MP,
    ROGUE_BASE_ST,
    ROGUE_ST_GROWTH_PERCENT,
    WARRIOR_BASE_AG,
    WARRIOR_BASE_DF,
    WARRIOR_BASE_HP,
    WARRIOR_BASE_MG,
    WARRIOR_BASE_MP,
    WARRIOR_BASE_ST,
    WARRIOR_HP_GROWTH_PERCENT,
    WARRIOR_ST_GROWTH_PERCENT,
    XP_BASE_COST,
    XP_EXPONENT,
)


def percentage(percent: int, whole: int, remainder: bool = True) -> int | float:
    """Calcula a porcentagem de um valor.

    Args:
        percent: Porcentagem a ser calculada.
        whole: Valor base para o cálculo.
        remainder: Se True, retorna float; se False, retorna int (default: True).

    Returns:
        Resultado do cálculo percentual.
    """
    if remainder:
        return (percent * whole) / 100
    return (percent * whole) // 100


class Player(Entity):
    """Classe base para personagens jogáveis (heróis).

    Attributes:
        nick_name: Nome do jogador.
        level: Nível atual.
        xp_points: Pontos de experiência acumulados.
        isalive: Indica se o jogador está vivo.
        avg_damage: Dano médio calculado.
        kill_streak: Sequência de kills.
        wins: Vitórias.
        coins: Moedas do jogador.
        skill_points: Pontos de habilidade disponíveis.
        inventory: Lista de itens no inventário.
        equipment: Dicionário de equipamentos por slot.
        skills: Habilidades aprendidas.
        learnable_skills: Habilidades disponíveis para aprender.
        active_effects: Efeitos ativos no jogador.
        active_buffs: Buffs ativos no jogador.
    """

    def __init__(self, nick_name: str) -> None:
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = 0
        self.kill_streak = 0
        self.wins = 0
        self.coins = 0
        self.skill_points = 0
        self.inventory: list[object] = []
        self.equipment = {
            "Weapon": None,
            "Helmet": None,
            "Body": None,
            "Legs": None,
            "Shoes": None,
        }
        self.skills: dict[int, object] = {}
        self.learnable_skills: dict[int, object] = {}
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, dict[str, object]] = {}

    def add_item_to_inventory(self, item: object) -> str | None:
        """Adiciona item ao inventário.

        Args:
            item: Item a ser adicionado.

        Returns:
            Mensagem de confirmação ou None.
        """
        if item:
            self.inventory.append(item)
            return f"Você obteve: {getattr(item, 'name', 'Item')}!"
        return None

    def remove_item_from_inventory(self, item: object) -> bool:
        """Remove item do inventário.

        Args:
            item: Item a ser removido.

        Returns:
            True se o item foi removido, False caso contrário.
        """
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def spend_coins(self, amount: int) -> bool:
        """Gasta moedas se houver saldo suficiente.

        Args:
            amount: Quantidade de moedas a gastar.

        Returns:
            True se a transação foi bem-sucedida, False caso contrário.
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def earn_coins(self, amount: int) -> None:
        """Adiciona moedas ao jogador.

        Args:
            amount: Quantidade de moedas a adicionar.
        """
        self.coins += amount

    def equip(self, item_to_equip: object) -> str | None:
        """Equipa um item no slot correspondente.

        Args:
            item_to_equip: Item a ser equipado.

        Returns:
            Mensagem de confirmação ou mensagem de erro.
        """
        slot = getattr(item_to_equip, "slot", None)
        if not slot or slot not in self.equipment:
            return f"{getattr(item_to_equip, 'name', 'Item')} não pode ser equipado."
        if self.equipment[slot]:
            self.unequip(slot)
        self.inventory.remove(item_to_equip)
        self.equipment[slot] = item_to_equip
        if slot == "Weapon":
            self.avg_damage += int(getattr(item_to_equip, "damage_bonus", 0))
        else:
            self.base_df += int(getattr(item_to_equip, "defense_bonus", 0))
        self.rest()
        return f"{getattr(item_to_equip, 'name', 'Item')} equipado."

    def unequip(self, slot: str) -> str | None:
        """Desequipa um item do slot especificado.

        Args:
            slot: Slot do item a ser desequipado.

        Returns:
            Mensagem de confirmação ou None se slot estava vazio.
        """
        item_to_unequip = self.equipment.get(slot)
        if not item_to_unequip:
            return None
        if slot == "Weapon":
            self.avg_damage -= int(getattr(item_to_unequip, "damage_bonus", 0))
        else:
            self.base_df -= int(getattr(item_to_unequip, "defense_bonus", 0))
        self.equipment[slot] = None
        self.inventory.append(item_to_unequip)
        self.rest()
        return f"{getattr(item_to_unequip, 'name', 'Item')} desequipado."

    def use_potion(self, potion: object) -> str:
        """Usa uma poção e aplica seus efeitos.

        Args:
            potion: Poção a ser usada.

        Returns:
            Mensagem descrevendo o efeito aplicado.
        """
        potion_type = getattr(potion, "potion_type", None)
        effect_value = int(getattr(potion, "effect_value", 0))
        potion_name = getattr(potion, "name", "Poção")

        if potion_type == "Health":
            self._hp += effect_value
            if self._hp > self.base_hp:
                self._hp = self.base_hp
            msg = f"Você usou {potion_name} e recuperou {effect_value} de HP."
        elif potion_type == "Mana":
            self._mp += effect_value
            if self._mp > self.base_mp:
                self._mp = self.base_mp
            msg = f"Você usou {potion_name} e recuperou {effect_value} de MP."
        elif potion_type == "Strength":
            self.active_buffs["Força Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {potion_name}. Força aumentada em {effect_value} por 3 turnos!"
        elif potion_type == "Defense":
            self.active_buffs["Defesa Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {potion_name}. Defesa aumentada em {effect_value} por 3 turnos!"
        elif potion_type == "Agility":
            self.active_buffs["Agilidade Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {potion_name}. Agilidade aumentada em {effect_value} por 3 turnos!"
        else:
            msg = f"Você usou {potion_name}, mas não teve efeito aparente."

        self.inventory.remove(potion)
        return msg

    def rest(self) -> None:
        """Restaura HP, MP, limpa efeitos e marca como vivo."""
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.active_effects.clear()
        self.active_buffs.clear()
        self.set_isalive(True)

    def get_stat(self, stat: str) -> int:
        """Retorna o valor de um atributo considerando buffs ativos.

        Args:
            stat: Nome do atributo ('st', 'ag', 'mg', 'df').

        Returns:
            Valor do atributo com buffs aplicados.
        """
        base_value = int(getattr(self, f"base_{stat}"))
        if stat == "st" and "Grito de Guerra" in self.active_buffs:
            base_value += int(self.active_buffs["Grito de Guerra"]["value"])
        if stat == "ag" and "Cortina de Fumaça" in self.active_buffs:
            base_value += int(self.active_buffs["Cortina de Fumaça"]["value"])
        if stat == "st" and "Força Aumentada" in self.active_buffs:
            base_value += int(self.active_buffs["Força Aumentada"]["value"])
        if stat == "df" and "Defesa Aumentada" in self.active_buffs:
            base_value += int(self.active_buffs["Defesa Aumentada"]["value"])
        if stat == "ag" and "Agilidade Aumentada" in self.active_buffs:
            base_value += int(self.active_buffs["Agilidade Aumentada"]["value"])
        return base_value

    @staticmethod
    def my_type() -> str:
        """Retorna o tipo da entidade."""
        return "Human"

    def get_avg_damage(self) -> int:
        """Retorna o dano médio do jogador."""
        return self.avg_damage

    def add_xp_points(self, amount: int) -> None:
        """Adiciona pontos de experiência.

        Args:
            amount: Quantidade de XP a adicionar.
        """
        if self.isalive:
            self.xp_points += amount

    def level_up(self, show: bool = True) -> list[str]:
        """Processa level up quando XP é suficiente.

        Args:
            show: Se True, retorna mensagens de exibição (default: True).

        Returns:
            Lista de mensagens sobre level up e novas habilidades.
        """
        needed_xp = self.need_to_up()
        leveled_up = False
        messages: list[str] = []
        while self.xp_points >= needed_xp:
            leveled_up = True
            self.xp_points -= needed_xp
            self.level += 1
            if show:
                messages.append(f"Level up! Agora você está no nível: {self.level}!")
            self._update_stats_on_level_up()
            skill_msgs = self.learn_new_skills(show)
            messages.extend(skill_msgs)
            needed_xp = self.need_to_up()
        if leveled_up and show:
            messages.append(f"Você precisa de {self.need_to_next()} XP para o próximo nível.")
        return messages

    def learn_new_skills(self, show: bool = True) -> list[str]:
        """Aprende novas habilidades disponíveis no nível atual.

        Args:
            show: Se True, inclui mensagens de novas habilidades (default: True).

        Returns:
            Lista de mensagens sobre habilidades aprendidas.
        """
        messages: list[str] = []
        for level, skill in self.learnable_skills.items():
            if self.level >= level and skill not in self.skills.values():
                new_skill_key = len(self.skills) + 1
                self.skills[new_skill_key] = skill
                if show:
                    skill_name = getattr(skill, 'name', 'Habilidade')
                    messages.append(f"Nova habilidade aprendida: {skill_name}!")
        return messages

    def _update_stats_on_level_up(self) -> None:
        """Atualiza atributos base ao subir de nível (método interno)."""
        class_name = self.get_classname()
        if class_name == "Warrior":
            self.base_hp += int(percentage(WARRIOR_HP_GROWTH_PERCENT, self.base_hp, False))
            self.base_st += int(percentage(WARRIOR_ST_GROWTH_PERCENT, self.base_st, False))
        elif class_name == "Mage":
            self.base_mp += int(percentage(MAGE_MP_GROWTH_PERCENT, self.base_mp, False))
            self.base_mg += int(percentage(MAGE_MG_GROWTH_PERCENT, self.base_mg, False))
        elif class_name == "Rogue":
            self.base_st += int(percentage(ROGUE_ST_GROWTH_PERCENT, self.base_st, False))
            self.base_ag = min(self.base_ag + ROGUE_AGILITY_INCREMENT, AGILITY_CAP)
        self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        self.rest()

    def need_to_next(self) -> int:
        """Retorna a quantidade de XP necessária para o próximo nível."""
        return max(0, self.need_to_up() - self.xp_points)

    def need_to_up(self) -> int:
        """Retorna a quantidade total de XP necessária para subir de nível."""
        return int(XP_BASE_COST * (self.level**XP_EXPONENT))

    def set_level(self, target_level: int) -> str:
        """Define o nível do jogador ajustando atributos.

        Args:
            target_level: Nível desejado.

        Returns:
            Mensagem de confirmação.
        """
        self.level = 1
        for _ in range(target_level - 1):
            self.level += 1
            self._update_stats_on_level_up()
            self.learn_new_skills(show=False)
        self.rest()
        return f"{self.nick_name} foi definido para o nível {self.level}."


class Warrior(Player):
    """Classe Guerreiro - focada em força física e HP alto.

    Attributes:
        base_hp: HP base do guerreiro.
        base_mp: MP base do guerreiro.
        base_st: Força base do guerreiro.
        base_ag: Agilidade base do guerreiro.
        base_mg: Magia base do guerreiro.
        base_df: Defesa base do guerreiro.
    """

    base_hp: int = WARRIOR_BASE_HP
    base_mp: int = WARRIOR_BASE_MP
    base_st: int = WARRIOR_BASE_ST
    base_ag: int = WARRIOR_BASE_AG
    base_mg: int = WARRIOR_BASE_MG
    base_df: int = WARRIOR_BASE_DF

    def __init__(self, nick_name: str) -> None:
        """Inicializa um guerreiro.

        Args:
            nick_name: Nome do jogador.
        """
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // DAMAGE_FORMULA_DIVISOR

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Warrior"

    def get_hp(self) -> int:
        """Retorna os pontos de vida atuais."""
        return self._hp

    def get_mp(self) -> int:
        """Retorna os pontos de mana atuais."""
        return self._mp

    def get_st(self) -> int:
        """Retorna a força com buffs aplicados."""
        return self.get_stat("st")

    def get_ag(self) -> int:
        """Retorna a agilidade com buffs aplicados."""
        return self.get_stat("ag")

    def get_mg(self) -> int:
        """Retorna a magia com buffs aplicados."""
        return self.get_stat("mg")

    def get_df(self) -> int:
        """Retorna a defesa com buffs aplicados."""
        return self.get_stat("df")


class Mage(Player):
    """Classe Mago - focada em magia e MP alto.

    Attributes:
        base_hp: HP base do mago.
        base_mp: MP base do mago.
        base_st: Força base do mago.
        base_ag: Agilidade base do mago.
        base_mg: Magia base do mago.
        base_df: Defesa base do mago.
    """

    base_hp: int = MAGE_BASE_HP
    base_mp: int = MAGE_BASE_MP
    base_st: int = MAGE_BASE_ST
    base_ag: int = MAGE_BASE_AG
    base_mg: int = MAGE_BASE_MG
    base_df: int = MAGE_BASE_DF

    def __init__(self, nick_name: str) -> None:
        """Inicializa um mago.

        Args:
            nick_name: Nome do jogador.
        """
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // DAMAGE_FORMULA_DIVISOR

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Mage"

    def get_hp(self) -> int:
        """Retorna os pontos de vida atuais."""
        return self._hp

    def get_mp(self) -> int:
        """Retorna os pontos de mana atuais."""
        return self._mp

    def get_st(self) -> int:
        """Retorna a força com buffs aplicados."""
        return self.get_stat("st")

    def get_ag(self) -> int:
        """Retorna a agilidade com buffs aplicados."""
        return self.get_stat("ag")

    def get_mg(self) -> int:
        """Retorna a magia com buffs aplicados."""
        return self.get_stat("mg")

    def get_df(self) -> int:
        """Retorna a defesa com buffs aplicados."""
        return self.get_stat("df")


class Rogue(Player):
    """Classe Ladino - focada em agilidade e ataques rápidos.

    Attributes:
        base_hp: HP base do ladino.
        base_mp: MP base do ladino.
        base_st: Força base do ladino.
        base_ag: Agilidade base do ladino.
        base_mg: Magia base do ladino.
        base_df: Defesa base do ladino.
    """

    base_hp: int = ROGUE_BASE_HP
    base_mp: int = ROGUE_BASE_MP
    base_st: int = ROGUE_BASE_ST
    base_ag: int = ROGUE_BASE_AG
    base_mg: int = ROGUE_BASE_MG
    base_df: int = ROGUE_BASE_DF

    def __init__(self, nick_name: str) -> None:
        """Inicializa um ladino.

        Args:
            nick_name: Nome do jogador.
        """
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // DAMAGE_FORMULA_DIVISOR

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Rogue"

    def get_hp(self) -> int:
        """Retorna os pontos de vida atuais."""
        return self._hp

    def get_mp(self) -> int:
        """Retorna os pontos de mana atuais."""
        return self._mp

    def get_st(self) -> int:
        """Retorna a força com buffs aplicados."""
        return self.get_stat("st")

    def get_ag(self) -> int:
        """Retorna a agilidade com buffs aplicados."""
        return self.get_stat("ag")

    def get_mg(self) -> int:
        """Retorna a magia com buffs aplicados."""
        return self.get_stat("mg")

    def get_df(self) -> int:
        """Retorna a defesa com buffs aplicados."""
        return self.get_stat("df")


