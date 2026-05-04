from __future__ import annotations

from typing import TYPE_CHECKING

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
    ROGUE_AGILITY_GROWTH_PERCENT,
    ROGUE_BASE_AG,
    ROGUE_BASE_DF,
    ROGUE_BASE_HP,
    ROGUE_BASE_MG,
    ROGUE_BASE_MP,
    ROGUE_BASE_ST,
    ROGUE_HP_GROWTH_PERCENT,
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

if TYPE_CHECKING:
    from src.content.passives import PassiveCard
    from src.content.skills_loader import SkillCard

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
        self.unspent_attribute_points: int = 0
        self.inventory: list[object] = []
        self.equipment = {
            "Weapon": None,
            "Helmet": None,
            "Body": None,
            "Legs": None,
            "Shoes": None,
            "Hands": None,
            "Amulet": None,
            "Ring": None,
        }
        self.skills: dict[int, SkillCard] = {}
        self.initial_skills_learned: int = 0
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, dict[str, object]] = {}
        self.passives: list[PassiveCard] = []

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
        
        item_classes = getattr(item_to_equip, "classes", None)
        if item_classes is not None and self.get_classname() not in item_classes:
            return f"Sua classe ({self.get_classname()}) não pode equipar {getattr(item_to_equip, 'name', 'Item')}."
        
        if self.equipment[slot]:
            self.unequip(slot)
        self.inventory.remove(item_to_equip)
        self.equipment[slot] = item_to_equip
        if slot == "Weapon":
            self.avg_damage += int(getattr(item_to_equip, "damage_bonus", 0))
        elif slot in ("Helmet", "Body", "Legs", "Shoes", "Hands", "Amulet", "Ring"):
            self.base_df += int(getattr(item_to_equip, "defense_bonus", 0))
        self.rest()
        return getattr(item_to_equip, "name", "Item")

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
        return getattr(item_to_unequip, "name", "Item")

    def use_potion(self, item: object) -> str:
        """Usa um item e aplica seus efeitos.

        Args:
            item: Item a ser usado.

        Returns:
            Mensagem descrevendo o efeito aplicado.
        """
        effect_type = getattr(item, "effect_type", None)
        effect_value = int(getattr(item, "effect_value", 0))
        item_name = getattr(item, "name", "Item")

        if effect_type == "max_hp":
            self._hp += effect_value
            if self._hp > self.base_hp:
                self._hp = self.base_hp
            msg = f"Você usou {item_name} e recuperou {effect_value} de HP."
        elif effect_type == "max_mp":
            self._mp += effect_value
            if self._mp > self.base_mp:
                self._mp = self.base_mp
            msg = f"Você usou {item_name} e recuperou {effect_value} de MP."
        elif effect_type == "strength":
            self.active_buffs["Força Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Força aumentada em {effect_value} por 3 turnos!"
        elif effect_type == "defense":
            self.active_buffs["Defesa Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Defesa aumentada em {effect_value} por 3 turnos!"
        elif effect_type == "agility":
            self.active_buffs["Agilidade Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Agilidade aumentada em {effect_value} por 3 turnos!"
        elif effect_type == "speed":
            self.active_buffs["Velocidade Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Velocidade aumentada em {effect_value} por 3 turnos!"
        elif effect_type == "evasion":
            self.active_buffs["Evasão Aumentada"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Evasão aumentada em {effect_value} por 3 turnos!"
        elif effect_type == "crit_chance":
            self.active_buffs["Chance de Crítico"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Chance de crítico +{effect_value}% por 3 turnos!"
        elif effect_type == "crit_damage":
            self.active_buffs["Dano Crítico"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Dano crítico +{effect_value} por 3 turnos!"
        elif effect_type == "life_steal":
            self.active_buffs["Roubo de Vida"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Roubo de vida +{effect_value}% por 3 turnos!"
        elif effect_type == "mana_regen":
            self.active_buffs["Regeneração de Mana"] = {"value": effect_value, "duration": 3}
            msg = f"Você usou {item_name}. Regeneração de mana +{effect_value} por 3 turnos!"
        else:
            msg = f"Você usou {item_name}, mas não teve efeito aparente."

        self.inventory.remove(item)
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

    def add_passive(self, passive: PassiveCard) -> str:
        self.passives.append(passive)
        self._apply_passive_stats(passive)
        return f"Passiva adquirida: {passive.name}!"

    def _apply_passive_stats(self, passive: PassiveCard) -> None:
        effect_type = passive.effect_type
        value = int(passive.effect_value)

        if effect_type == "max_hp":
            old_base_hp = self.base_hp
            self.base_hp += value
            hp_ratio = self._hp / old_base_hp if old_base_hp > 0 else 1
            self._hp = min(int(self.base_hp * hp_ratio), self.base_hp)
        elif effect_type == "max_mp":
            old_base_mp = self.base_mp
            self.base_mp += value
            mp_ratio = self._mp / old_base_mp if old_base_mp > 0 else 1
            self._mp = min(int(self.base_mp * mp_ratio), self.base_mp)
        elif effect_type == "strength":
            self.base_st += value
            self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        elif effect_type == "defense":
            self.base_df += value
        elif effect_type == "agility":
            self.base_ag = min(self.base_ag + value, AGILITY_CAP)

    def add_passive_load(self, passive: PassiveCard) -> None:
        self.passives.append(passive)
        self._apply_passive_stats(passive)

    def get_passive_bonus(self, effect_type: str) -> float:
        return sum(
            float(p.effect_value)
            for p in self.passives
            if p.effect_type == effect_type
        )

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
        """Processa um level up quando XP é suficiente.

        Args:
            show: Se True, retorna mensagens de exibição (default: True).

        Returns:
            Lista de mensagens sobre level up e novas habilidades.
            Retorna lista vazia se não houver XP suficiente.
        """
        needed_xp = self.need_to_up()
        messages: list[str] = []
        if self.xp_points >= needed_xp:
            self.xp_points -= needed_xp
            self.level += 1
            if show:
                messages.append(f"Level up! Agora você está no nível: {self.level}!")
            self._update_stats_on_level_up()
            skill_msgs = self.learn_new_skills(show)
            messages.extend(skill_msgs)
            if show:
                messages.append(f"Você precisa de {self.need_to_next()} XP para o próximo nível.")
        return messages

    def learn_new_skills(self, show: bool = True) -> list[str]:
        """Aprende skills iniciais uma por nível (níveis 1-4).

        Args:
            show: Se True, inclui mensagens de novas habilidades.

        Returns:
            Lista de mensagens sobre habilidades aprendidas.
        """
        messages: list[str] = []
        # Apenas aprende skills iniciais nos níveis 1-4, uma por nível
        if 1 <= self.level <= 4 and self.initial_skills_learned < self.level:
            from src.content.skills_loader import get_initial_skills
            initial_skills = get_initial_skills(self.get_classname())
            while self.initial_skills_learned < self.level and self.initial_skills_learned < len(initial_skills):
                skill = initial_skills[self.initial_skills_learned]
                new_key = self.initial_skills_learned + 1
                self.skills[new_key] = skill
                self.initial_skills_learned += 1
                if show:
                    messages.append(f"Nova habilidade aprendida: {skill.name}!")
        return messages

    def add_skill_with_replacement(self, new_skill: "SkillCard", replace_key: int) -> str:
        """Adiciona nova skill substituindo uma existente na chave especificada.

        Args:
            new_skill: A nova skill a ser adicionada.
            replace_key: A chave da skill a ser substituída.

        Returns:
            Mensagem de confirmação.
        """
        old_skill = self.skills.get(replace_key)
        self.skills[replace_key] = new_skill
        old_name = old_skill.name if old_skill else "Nenhuma"
        return f"Skill {old_name} substituída por {new_skill.name}!"

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
            self.base_hp += int(percentage(ROGUE_HP_GROWTH_PERCENT, self.base_hp, False))
            self.base_st += int(percentage(ROGUE_ST_GROWTH_PERCENT, self.base_st, False))
            self.base_ag = min(int(self.base_ag * (1 + ROGUE_AGILITY_GROWTH_PERCENT / 100)), AGILITY_CAP)
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
        self.skills.clear()
        self.initial_skills_learned = 0
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

    def get_avg_damage(self) -> int:
        """Fórmula Warrior: favorece Força."""
        st = self.get_st()
        mg = self.get_mg()
        return (int(st * 2) + int(mg)) // 4


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

    def get_avg_damage(self) -> int:
        """Fórmula Mage: ataque físico fraco, favorece Magia."""
        st = self.get_st()
        mg = self.get_mg()
        return (int(st) + int(mg * 2)) // 5


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

    def get_avg_damage(self) -> int:
        """Fórmula Rogue: usa AG como identidade."""
        st = self.get_st()
        ag = self.get_ag()
        return (int(st * 1.2) + int(ag * 1.8)) // 3


