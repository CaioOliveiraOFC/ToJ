#!/usr/bin/env python3

from toj_source.math_operations import percentage
from toj_source.weapons import *


class Player:

    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = (self._st + self._mg) // 3
        self.kill_streak = 0
        self.wins = 0
        self.has_gun = False

    def set_has_hun(self, state=True):
        try:
            self.has_gun = state
        except ValueError:
            self.has_gun = False

    def win(self):
        self.wins += 1

    def get_kill_streak(self):
        return self.kill_streak

    def add_kill_streak(self):
        self.kill_streak += 1

    def reset_kill_streak(self):
        self.kill_streak = 0

    def get_avg_damage(self):
        return self.avg_damage

    def get_isalive(self):
        return self.isalive

    def set_isalive(self, state=True):
        if state is not True and state is not False:
            raise ValueError("Expected True or False")
        self.isalive = bool(state)

    def reduce_hp(self, quantty):
        self._hp -= quantty

    @staticmethod
    def my_type():
        return 'Human'

    def set_xp_points(self, amount):
        self.xp_points = amount

    def add_xp_points(self, amount):
        self.xp_points += amount

    def get_xp_points(self):
        return self.xp_points

    def get_nick_name(self):
        return self.nick_name

    def get_level(self):
        return self.level

    def set_level(self, new_level):
        self.level = new_level

    def need_to_up(self):
        need_to_up: int = 0
        if self.level == 1:
            need_to_up = self.level + 7 * 10
        else:
            for each_level in range(1, self.level):
                need_to_up += (self.level + 7) * 10
        return need_to_up

    @staticmethod
    def xp_for_level(level):
        xp_to_level = 0
        need_to_up = 0
        if level == 1:
            xp_to_level = (level + 7) * 10
        else:
            for each_level in range(1, level-1):
                need_to_up += (level + 7) * 10
                xp_to_level += need_to_up
        return xp_to_level

    def level_up(self, show=True):
        while True:
            if self.get_xp_points() >= self.need_to_up():
                self.set_xp_points(self.xp_points - self.need_to_up())
                self.level += 1
                if self.get_classname() == 'Warrior':
                    self._hp += percentage(17, self._hp, False)
                    self._mp += percentage(14, self._mp, False)
                    self._st += percentage(13, self._st, False)
                    self._ag += 1
                    if self._ag >= 91:
                        self._ag = 90
                    self._mg += percentage(12, self._mg, False)
                    self._df += percentage(13, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                    self.avg_damage = (self._st + self._mg) // 3
                elif self.get_classname() == 'Mage':
                    self._hp += percentage(17, self._hp, False)
                    self._mp += percentage(17, self._mp, False)
                    self._st += percentage(11, self._st, False)
                    self._ag += 1
                    if self._ag >= 91:
                        self._ag = 90
                    self._mg += percentage(15, self._mg, False)
                    self._df += percentage(11, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                    self.avg_damage = (self._st + self._mg) // 3
                elif self.get_classname() == 'Rogue':
                    self._hp += percentage(14, self._hp, False)
                    self._mp += percentage(14, self._mp, False)
                    self._st += percentage(14, self._st, False)
                    self._ag += 1
                    if self._ag >= 96:
                        self._ag = 95
                    self._mg += percentage(12, self._mg, False)
                    self._df += percentage(11, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                    self.avg_damage = (self._st + self._mg) // 3
                if show:
                    print(f"Level up! now you are level: {self.level}".center(100))
            else:
                if show:
                    print(f"You need more xp points! reach: {self.need_to_up()}".center(100))
                break

    def need_to_next(self):
        operation = self.need_to_up() - self.get_xp_points()
        return operation if operation > 0 else 0

    def get_level_bar(self):
        level_bar = ['[ ]' for x in range(10)]
        try:
            percent_of_bar = ((self.get_xp_points() * 100) // self.need_to_up()) // 10
        except ZeroDivisionError:
            percent_of_bar = self.get_xp_points() * 100 // 10
        printable = str()
        if percent_of_bar == 0:
            printable = ''.join(level_bar)
            return f'|{printable}|'
        else:
            try:
                for char in range(0, percent_of_bar):
                    level_bar[char] = "[x]"
                    printable = ''.join(level_bar)
                return f"|{printable}|"
            except IndexError:
                level_bar = ['[x]' for x in range(10)]
                printable = ''.join(level_bar)
                return f"|{printable}|"

    def rest(self):
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        self.set_isalive()

    def equip_a_gun(self, arm):
        if not arm.is_equiped():
            if arm.get_wp_level() <= self.get_level():
                if self.get_classname() in arm.classes:
                    self.has_gun = True
                    self._mg += arm.get_mg()
                    self._st += arm.get_st()
                    self._ag += arm.get_ag()
                    self.avg_damage += arm.avg_dmg
                    print(f'Congratulations {self.get_nick_name()} now you have {arm.name}'.center(100))
                else:
                    print(f'You need to be {"or".join(arm.get_lst_class())}'.center(100))
            else:
                print(f'You need level -> {arm.get_wp_level()} to use this weapon'.center(100))
        else:
            print('Someone is using this gun'.center(100))


class Warrior(Player):

    base_hp, base_mp, base_st = 104, 89, 104
    base_ag, base_mg, base_df = 3, 30, 30

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Warrior.base_hp, Warrior.base_mp, Warrior.base_st
        self._ag, self._mg, self._df = Warrior.base_ag, Warrior.base_mg, Warrior.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        return 'Warrior'

    def get_hp(self):
        return self._hp

    def get_mp(self):
        return self._mp

    def get_st(self):
        return self._st

    def get_ag(self):
        return self._ag

    def get_mg(self):
        return self._mg

    def get_df(self):
        return self._df

    def set_hp(self, new_HP):
        self._hp = new_HP

    def set_mp(self, new_MP):
        self._mp = new_MP

    def set_st(self, new_ST):
        self._st = new_ST

    def set_ag(self, new_AG):
        self._ag = new_AG

    def set_mg(self, new_MG):
        self._mg = new_MG

    def set_df(self, new_DF):
        self._df = new_DF


class Mage(Player):

    base_hp, base_mp, base_st = 96, 100, 32
    base_ag, base_mg, base_df = 3, 100, 23

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Mage.base_hp, Mage.base_mp, Mage.base_st
        self._ag, self._mg, self._df = Mage.base_ag, Mage.base_mg, Mage.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        return 'Mage'

    def get_hp(self):
        return self._hp

    def get_mp(self):
        return self._mp

    def get_st(self):
        return self._st

    def get_ag(self):
        return self._ag

    def get_mg(self):
        return self._mg

    def get_df(self):
        return self._df

    def set_hp(self, new_HP):
        self._hp = new_HP

    def set_mp(self, new_MP):
        self._mp = new_MP

    def set_st(self, new_ST):
        self._st = new_ST

    def set_ag(self, new_AG):
        self._ag = new_AG

    def set_mg(self, new_MG):
        self._mg = new_MG

    def set_df(self, new_DF):
        self._df = new_DF


class Rogue(Player):

    base_hp, base_mp, base_st = 99, 30, 67
    base_ag, base_mg, base_df = 7, 66, 20

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Rogue.base_hp, Rogue.base_mp, Rogue.base_st
        self._ag, self._mg, self._df = Rogue.base_ag, Rogue.base_mg, Rogue.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        return 'Rogue'

    def get_hp(self):
        return self._hp

    def get_mp(self):
        return self._mp

    def get_st(self):
        return self._st

    def get_ag(self):
        return self._ag

    def get_mg(self):
        return self._mg

    def get_df(self):
        return self._df

    def set_hp(self, new_HP):
        self._hp = new_HP

    def set_mp(self, new_MP):
        self._mp = new_MP

    def set_st(self, new_ST):
        self._st = new_ST

    def set_ag(self, new_AG):
        self._ag = new_AG

    def set_mg(self, new_MG):
        self._mg = new_MG

    def set_df(self, new_DF):
        self._df = new_DF


class Monster:

    base_hp, base_mp, base_st = 100, 40, 55
    base_ag, base_mg, base_df = 3, 50, 30

    def __init__(self, nick_name, mob_level=1):
        self.nick_name = nick_name
        if mob_level == 0:
            self.level = 1
        else:
            self.level = mob_level
        self.isalive = True
        self._hp = Monster.base_hp
        self._mp = Monster.base_mp
        self._st = Monster.base_st
        self._ag = Monster.base_ag
        self._mg = Monster.base_mg
        self._df = Monster.base_df
        if 10 > self.level >= 1:
            for level in range(self.level):
                self._hp += percentage(10, self._hp, False)
                self._mp += percentage(8, self._mp, False)
                self._st += percentage(8, self._st, False)
                self._ag += 1
                self._mg += percentage(8, self._mg, False)
                self._df += percentage(10, self._df, False)
                self.base_hp, self.base_mp, self.base_st = self._hp, self._mp, self._st
                self.base_ag, self.base_mg, self.base_df = self._ag, self._mg, self._df
            self.avg_damage = (self._st + self._mg) // 3
        elif 20 > self.level >= 10:
            for level in range(self.level):
                self._hp += percentage(11, self._hp, False)
                self._mp += percentage(11, self._mp, False)
                self._st += percentage(11, self._st, False)
                self._ag += 1
                self._mg += percentage(11, self._mg, False)
                self._df += percentage(13, self._df, False)
                self.base_hp, self.base_mp, self.base_st = self._hp, self._mp, self._st
                self.base_ag, self.base_mg, self.base_df = self._ag, self._mg, self._df
            self.avg_damage = (self._st + self._mg) // 3
        else:
            for level in range(self.level):
                self._hp += percentage(15, self._hp, False)
                self._mp += percentage(15, self._mp, False)
                self._st += percentage(15, self._st, False)
                self._ag += 1
                if self._ag >= 61:
                    self._ag = 60
                self._mg += percentage(14, self._mg, False)
                self._df += percentage(15, self._df, False)
                self.base_hp, self.base_mp, self.base_st = self._hp, self._mp, self._st
                self.base_ag, self.base_mg, self.base_df = self._ag, self._mg, self._df
            self.avg_damage = (self._st + self._mg) // 3

    def get_avg_damage(self):
        return self.avg_damage

    def reduce_hp(self, quantty):
        self._hp -= quantty

    @staticmethod
    def my_type():
        return 'COM'

    @staticmethod
    def get_classname():
        return 'Monster'

    def get_level(self):
        return self.level

    def set_isalive(self, state=True):
        self.isalive = state

    def get_isalive(self):
        return self.isalive

    def set_level(self, new_level):
        self.level = new_level

    def get_hp(self):
        return self._hp

    def get_mp(self):
        return self._mp

    def get_st(self):
        return self._st

    def get_ag(self):
        return self._ag

    def get_mg(self):
        return self._mg

    def get_df(self):
        return self._df

    def set_hp(self, new_HP):
        self._hp = new_HP

    def set_mp(self, new_MP):
        self._mp = new_MP

    def set_st(self, new_ST):
        self._st = new_ST

    def set_ag(self, new_AG):
        self._ag = new_AG

    def set_mg(self, new_MG):
        self._mg = new_MG

    def set_df(self, new_DF):
        self._df = new_DF

    def restart(self):
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        self.set_isalive()

def show_hp_bar(entt):
    """
    ------> Print the HP bar of the entt
    :param entt: Player or Monster
    """
    printable = str()
    hp_bar = ['[ ]' for x in range(10)]
    percent_of_bar = (entt.get_hp() * 100) // entt.base_hp // 10
    if percent_of_bar <= 0:
        printable = ''.join(hp_bar)
        print(f"{entt.get_nick_name()} have {entt.get_hp()} HP points: ")
        print(f'|{printable}|')
    else:
        for char in range(percent_of_bar):
            hp_bar[char] = "[#]"
            printable = ''.join(hp_bar)
        print(f"{entt.get_nick_name()} have {entt.get_hp()} HP points: ")
        print(f'|{printable}|')

def get_hp_bar(entt):
    """
    ------> Get the HP bar of the entt
    :param entt: Player or Monster
    :return: Return string with the HP bar
    """
    printable = str()
    hp_bar = ['[ ]' for x in range(10)]
    percent_of_bar = (entt.get_hp() * 100) // entt.base_hp // 10
    if percent_of_bar <= 0:
        printable = ''.join(hp_bar)
        return f'|{printable}| {entt.get_hp()} HP points'
    else:
        for char in range(percent_of_bar):
            try:
                hp_bar[char] = "[#]"
                printable = ''.join(hp_bar)
            except IndexError:
                break
        return f'|{printable}| {entt.get_hp()} HP points'

def compare(ennt1, ennt2):
    print(f'Class |{ennt1.get_classname()} X {ennt2.get_classname()}| Class'.center(102))
    print(f'Level |{ennt1.get_level():<4} X {ennt2.get_level():>4}| Level'.center(100))
    print(f"AVG |{ennt1.avg_damage:<5} X {ennt2.avg_damage:>5}| AVG".center(100))
    print(f"HP |{ennt1.get_hp():<5} X {ennt2.get_hp():>5}| HP".center(100))
    print(f'MP |{ennt1.get_mp():<5} X {ennt2.get_mp():>5}| MP'.center(100))
    print(f'ST |{ennt1.get_st():<5} X {ennt2.get_st():>5}| ST'.center(100))
    print(f'AG |{ennt1.get_ag():<5} X {ennt2.get_ag():>5}| AG'.center(100))
    print(f'MG |{ennt1.get_mg():<5} X {ennt2.get_mg():>5}| MG'.center(100))
    print(f'DF |{ennt1.get_df():<5} X {ennt2.get_df():>5}| DF'.center(100))


if __name__ == '__main__':
    pass
