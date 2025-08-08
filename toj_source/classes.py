#!/usr/bin/env python3

from .math_operations import percentage
from .skills import warrior_skills, mage_skills, rogue_skills
from .items import Item, Weapon, Armor

class Player:
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = 0
        self.kill_streak = 0
        self.wins = 0
        self.coins = 0
        self.skill_points = 0
        self.inventory = [] 
        self.equipment = {
            "Weapon": None, "Helmet": None, "Body": None, 
            "Legs": None, "Shoes": None
        }
        self.skills = {}
        self.learnable_skills = {}
        self.active_effects = {}
        self.active_buffs = {}

    def add_item_to_inventory(self, item):
        if item:
            self.inventory.append(item)
            print(f"Você obteve: {item.name}!")

    def equip(self, item_to_equip):
        if not isinstance(item_to_equip, (Weapon, Armor)):
            print(f"{item_to_equip.name} não pode ser equipado.")
            return
        if self.equipment[item_to_equip.slot]:
            self.unequip(item_to_equip.slot)
        self.inventory.remove(item_to_equip)
        self.equipment[item_to_equip.slot] = item_to_equip
        if isinstance(item_to_equip, Weapon):
            self.avg_damage += item_to_equip.damage_bonus
        elif isinstance(item_to_equip, Armor):
            self.base_df += item_to_equip.defense_bonus
        print(f"{item_to_equip.name} equipado.")
        self.rest()

    def unequip(self, slot):
        item_to_unequip = self.equipment[slot]
        if not item_to_unequip:
            return
        if isinstance(item_to_unequip, Weapon):
            self.avg_damage -= item_to_unequip.damage_bonus
        elif isinstance(item_to_unequip, Armor):
            self.base_df -= item_to_unequip.defense_bonus
        self.equipment[slot] = None
        self.inventory.append(item_to_unequip)
        print(f"{item_to_unequip.name} desequipado.")
        self.rest()

    def use_potion(self, potion):
        self._hp += potion.heal_amount
        if self._hp > self.base_hp:
            self._hp = self.base_hp
        self.inventory.remove(potion)
        print(f"Você usou {potion.name} e recuperou {potion.heal_amount} de HP.")

    def rest(self):
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.active_effects.clear()
        self.active_buffs.clear()
        self.set_isalive(True)
        
    def get_stat(self, stat):
        base_value = getattr(self, f"base_{stat}")
        if stat == 'st' and 'Grito de Guerra' in self.active_buffs:
            return base_value + self.active_buffs['Grito de Guerra']['value']
        if stat == 'ag' and 'Cortina de Fumaça' in self.active_buffs:
            return base_value + self.active_buffs['Cortina de Fumaça']['value']
        return base_value

    def reduce_hp(self, quantty): self._hp -= quantty
    def reduce_mp(self, cost): self._mp -= cost
    @staticmethod
    def my_type(): return 'Human'
    def get_nick_name(self): return self.nick_name
    def get_level(self): return self.level
    def get_avg_damage(self): return self.avg_damage
    def add_xp_points(self, amount):
        if self.isalive: self.xp_points += amount
    def level_up(self, show=True):
        needed_xp = self.need_to_up()
        leveled_up = False
        while self.xp_points >= needed_xp:
            leveled_up = True; self.xp_points -= needed_xp; self.level += 1
            if show: print(f"Level up! Agora você está no nível: {self.level}!".center(100))
            self._update_stats_on_level_up(); self.learn_new_skills(show)
            needed_xp = self.need_to_up()
        if leveled_up and show: print(f"Você precisa de {self.need_to_next()} XP para o próximo nível.".center(100))
    def learn_new_skills(self, show=True):
        for level, skill in self.learnable_skills.items():
            if self.level >= level and skill not in self.skills.values():
                new_skill_key = len(self.skills) + 1; self.skills[new_skill_key] = skill
                if show: print(f"Nova habilidade aprendida: {skill.name}!".center(100))
    def _update_stats_on_level_up(self):
        class_name = self.get_classname()
        if class_name == 'Warrior': self.base_hp += percentage(17, self.base_hp, False); self.base_st += percentage(13, self.base_st, False)
        elif class_name == 'Mage': self.base_mp += percentage(15, self.base_mp, False); self.base_mg += percentage(15, self.base_mg, False)
        elif class_name == 'Rogue': self.base_st += percentage(16, self.base_st, False); self.base_ag = min(self.base_ag + 2, 95)
        self.avg_damage = (self.base_st + self.base_mg) // 3; self.rest()
    def get_isalive(self): return self.isalive
    def set_isalive(self, state=True): self.isalive = state
    def need_to_next(self): return max(0, self.need_to_up() - self.xp_points)
    def need_to_up(self): return int(100 * (self.level ** 1.5))
    def set_level(self, target_level):
        self.level = 1
        for i in range(target_level - 1):
            self.level += 1
            self._update_stats_on_level_up()
            self.learn_new_skills(show=False)
        self.rest()
        print(f"{self.nick_name} foi definido para o nível {self.level}.")

class Warrior(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 104, 30, 104, 5, 30, 30
    def __init__(self, nick_name):
        super().__init__(nick_name) # CORREÇÃO: Adicionada a chamada ao construtor da classe pai
        self._hp, self.base_hp = self.base_hp, self.base_hp; self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st; self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg; self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = warrior_skills; self.learn_new_skills(show=False)
    @staticmethod
    def get_classname(): return 'Warrior'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self.get_stat('st')
    def get_ag(self): return self.get_stat('ag')
    def get_mg(self): return self.get_stat('mg')
    def get_df(self): return self.get_stat('df')

class Mage(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 96, 100, 32, 5, 100, 23
    def __init__(self, nick_name):
        super().__init__(nick_name) # CORREÇÃO: Adicionada a chamada ao construtor da classe pai
        self._hp, self.base_hp = self.base_hp, self.base_hp; self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st; self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg; self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = mage_skills; self.learn_new_skills(show=False)
    @staticmethod
    def get_classname(): return 'Mage'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self.get_stat('st')
    def get_ag(self): return self.get_stat('ag')
    def get_mg(self): return self.get_stat('mg')
    def get_df(self): return self.get_stat('df')

class Rogue(Player):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 99, 50, 75, 15, 66, 20
    def __init__(self, nick_name):
        super().__init__(nick_name) # CORREÇÃO: Adicionada a chamada ao construtor da classe pai
        self._hp, self.base_hp = self.base_hp, self.base_hp; self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st; self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg; self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = rogue_skills; self.learn_new_skills(show=False)
    @staticmethod
    def get_classname(): return 'Rogue'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self.get_stat('st')
    def get_ag(self): return self.get_stat('ag')
    def get_mg(self): return self.get_stat('mg')
    def get_df(self): return self.get_stat('df')

class Monster:
    def __init__(self, nick_name, mob_level=1):
        self.nick_name = nick_name; self.level = max(1, mob_level); self.isalive = True
        self._hp, self.base_hp = self.base_hp, self.base_hp; self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st; self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg; self._df, self.base_df = self.base_df, self.base_df
        for _ in range(self.level): self._hp += percentage(10, self._hp, False)
        self.base_hp = self._hp; self.avg_damage = (self._st + self._mg) // 3
        self.active_effects = {}; self.active_buffs = {}
    def get_avg_damage(self): return self.avg_damage
    def reduce_hp(self, quantty): self._hp -= quantty
    @staticmethod
    def my_type(): return 'COM'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_ag(self): return self._ag
    def get_df(self): return self._df
    def get_st(self): return self._st
    def get_mg(self): return self._mg
    def get_nick_name(self): return self.nick_name
    def get_isalive(self): return self.isalive
    def set_isalive(self, state=True): self.isalive = state
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 100, 40, 55, 3, 50, 30

def get_hp_bar(entt):
    if entt.base_hp == 0: percent_of_bar = 0
    else:
        current_hp = max(0, entt.get_hp()); percent_of_bar = int((current_hp / entt.base_hp) * 10)
    percent_of_bar = min(percent_of_bar, 10)
    hp_bar_fill = "[#]" * percent_of_bar; hp_bar_empty = "[ ]" * (10 - percent_of_bar)
    return f'|{hp_bar_fill}{hp_bar_empty}| {entt.get_hp()}/{entt.base_hp} HP'
