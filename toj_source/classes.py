#!/usr/bin/env python3

from .math_operations import percentage
from .skills import warrior_skills, mage_skills, rogue_skills

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
        self.inventory = {"Weapon": None, "Helmet": None,
                          "Body": None, "Legs": None,
                          "Shoes": None}
        self.skills = {}
        self.learnable_skills = {}

    def reduce_hp(self, quantty):
        self._hp -= quantty
        
    def reduce_mp(self, cost):
        self._mp -= cost

    @staticmethod
    def my_type():
        return 'Human'

    def get_nick_name(self):
        return self.nick_name

    def get_level(self):
        return self.level
    
    # --- CORREÇÃO AQUI: Adicionado o método que faltava ---
    def get_avg_damage(self):
        return self.avg_damage
    # ----------------------------------------------------

    def add_xp_points(self, amount):
        if self.isalive:
            self.xp_points += amount

    def level_up(self, show=True):
        needed_xp = self.need_to_up()
        leveled_up = False
        while self.xp_points >= needed_xp:
            leveled_up = True
            self.xp_points -= needed_xp
            self.level += 1
            self.skill_points += 3
            if show:
                print(f"Level up! Agora você está no nível: {self.level}!".center(100))
            
            self._update_stats_on_level_up()
            self.learn_new_skills(show)
            needed_xp = self.need_to_up()
        
        if leveled_up and show:
             print(f"Você precisa de {self.need_to_next()} XP para o próximo nível.".center(100))

    def learn_new_skills(self, show=True):
        for level, skill in self.learnable_skills.items():
            if self.level >= level and skill not in self.skills.values():
                new_skill_key = len(self.skills) + 1
                self.skills[new_skill_key] = skill
                if show:
                    print(f"Nova habilidade aprendida: {skill.name}!".center(100))

    def _update_stats_on_level_up(self):
        class_name = self.get_classname()
        if class_name == 'Warrior':
            self.base_hp += percentage(17, self.base_hp, False)
            self.base_st += percentage(13, self.base_st, False)
        elif class_name == 'Mage':
            self.base_mp += percentage(15, self.base_mp, False)
            self.base_mg += percentage(15, self.base_mg, False)
        elif class_name == 'Rogue':
            self.base_st += percentage(16, self.base_st, False)
            self.base_ag = min(self.base_ag + 2, 95)
        
        self.avg_damage = (self.base_st + self.base_mg) // 3
        self.rest()

    def rest(self):
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.set_isalive(True)
    
    def get_isalive(self): return self.isalive
    def set_isalive(self, state=True): self.isalive = state
    def need_to_next(self): return max(0, self.need_to_up() - self.xp_points)
    def need_to_up(self): return int(100 * (self.level ** 1.5))

class Warrior(Player):
    base_hp, base_mp, base_st = 104, 30, 104
    base_ag, base_mg, base_df = 3, 30, 30

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = warrior_skills
        self.learn_new_skills(show=False)

    @staticmethod
    def get_classname(): return 'Warrior'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df

class Mage(Player):
    base_hp, base_mp, base_st = 96, 100, 32
    base_ag, base_mg, base_df = 3, 100, 23
    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = mage_skills
        self.learn_new_skills(show=False)
    @staticmethod
    def get_classname(): return 'Mage'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df

class Rogue(Player):
    base_hp, base_mp, base_st = 99, 50, 67
    base_ag, base_mg, base_df = 10, 66, 20
    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        self.avg_damage = (self._st + self._mg) // 3
        self.learnable_skills = rogue_skills
        self.learn_new_skills(show=False)
    @staticmethod
    def get_classname(): return 'Rogue'
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df


class Monster:
    base_hp, base_mp, base_st = 100, 40, 55
    base_ag, base_mg, base_df = 3, 50, 30

    def __init__(self, nick_name, mob_level=1):
        self.nick_name = nick_name
        self.level = max(1, mob_level)
        self.isalive = True
        self._hp, self.base_hp = self.base_hp, self.base_hp
        self._mp, self.base_mp = self.base_mp, self.base_mp
        self._st, self.base_st = self.base_st, self.base_st
        self._ag, self.base_ag = self.base_ag, self.base_ag
        self._mg, self.base_mg = self.base_mg, self.base_mg
        self._df, self.base_df = self.base_df, self.base_df
        for _ in range(self.level):
            self._hp += percentage(10, self._hp, False)
        self.base_hp = self._hp
        self.avg_damage = (self._st + self._mg) // 3

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

def get_hp_bar(entt):
    if entt.base_hp == 0: percent_of_bar = 0
    else:
        current_hp = max(0, entt.get_hp())
        percent_of_bar = int((current_hp / entt.base_hp) * 10)
    percent_of_bar = min(percent_of_bar, 10)
    hp_bar_fill = "[#]" * percent_of_bar
    hp_bar_empty = "[ ]" * (10 - percent_of_bar)
    return f'|{hp_bar_fill}{hp_bar_empty}| {entt.get_hp()}/{entt.base_hp} HP'
