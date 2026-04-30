from __future__ import annotations

from src.entities.base import Entity


def percentage(percent: int, whole: int, remainder: bool = True) -> int | float:
    if remainder:
        return (percent * whole) / 100
    return (percent * whole) // 100


class Player(Entity):
    def __init__(self, nick_name: str):
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
        """Adiciona item ao inventário e retorna mensagem de confirmação."""
        if item:
            self.inventory.append(item)
            return f"Você obteve: {getattr(item, 'name', 'Item')}!"
        return None

    def equip(self, item_to_equip: object) -> str | None:
        """Equipa um item e retorna mensagem de confirmação."""
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
        """Desequipa um item e retorna mensagem de confirmação."""
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
        """Usa uma poção e retorna mensagem descrevendo o efeito."""
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
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.active_effects.clear()
        self.active_buffs.clear()
        self.set_isalive(True)

    def get_stat(self, stat: str) -> int:
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
        return "Human"

    def get_avg_damage(self) -> int:
        return self.avg_damage

    def add_xp_points(self, amount: int) -> None:
        if self.isalive:
            self.xp_points += amount

    def level_up(self, show: bool = True) -> list[str]:
        """Processa level up e retorna lista de mensagens para exibição."""
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
        """Aprende novas habilidades e retorna lista de mensagens."""
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
        class_name = self.get_classname()
        if class_name == "Warrior":
            self.base_hp += int(percentage(17, self.base_hp, False))
            self.base_st += int(percentage(13, self.base_st, False))
        elif class_name == "Mage":
            self.base_mp += int(percentage(15, self.base_mp, False))
            self.base_mg += int(percentage(15, self.base_mg, False))
        elif class_name == "Rogue":
            self.base_st += int(percentage(16, self.base_st, False))
            self.base_ag = min(self.base_ag + 2, 95)
        self.avg_damage = (self.base_st + self.base_mg) // 3
        self.rest()

    def need_to_next(self) -> int:
        return max(0, self.need_to_up() - self.xp_points)

    def need_to_up(self) -> int:
        return int(100 * (self.level**1.5))

    def set_level(self, target_level: int) -> str:
        """Define o nível do jogador e retorna mensagem de confirmação."""
        self.level = 1
        for _ in range(target_level - 1):
            self.level += 1
            self._update_stats_on_level_up()
            self.learn_new_skills(show=False)
        self.rest()
        return f"{self.nick_name} foi definido para o nível {self.level}."


class Warrior(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 104, 30, 104, 5, 30, 30

    def __init__(self, nick_name: str):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname() -> str:
        return "Warrior"

    def get_hp(self) -> int:
        return self._hp

    def get_mp(self) -> int:
        return self._mp

    def get_st(self) -> int:
        return self.get_stat("st")

    def get_ag(self) -> int:
        return self.get_stat("ag")

    def get_mg(self) -> int:
        return self.get_stat("mg")

    def get_df(self) -> int:
        return self.get_stat("df")


class Mage(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 96, 100, 32, 5, 100, 23

    def __init__(self, nick_name: str):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname() -> str:
        return "Mage"

    def get_hp(self) -> int:
        return self._hp

    def get_mp(self) -> int:
        return self._mp

    def get_st(self) -> int:
        return self.get_stat("st")

    def get_ag(self) -> int:
        return self.get_stat("ag")

    def get_mg(self) -> int:
        return self.get_stat("mg")

    def get_df(self) -> int:
        return self.get_stat("df")


class Rogue(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 99, 50, 75, 15, 66, 20

    def __init__(self, nick_name: str):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname() -> str:
        return "Rogue"

    def get_hp(self) -> int:
        return self._hp

    def get_mp(self) -> int:
        return self._mp

    def get_st(self) -> int:
        return self.get_stat("st")

    def get_ag(self) -> int:
        return self.get_stat("ag")

    def get_mg(self) -> int:
        return self.get_stat("mg")

    def get_df(self) -> int:
        return self.get_stat("df")


