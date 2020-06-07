#!/usr/bin/env python3

from toj_source.math_operations import percentage


class Player:

    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = (self._st + self._mg) // 2

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

    def dead_or_alive(self):
        """
        -----> Return string Dead or Alive
        """
        return "alive" if self.isalive else "dead"

    def show_alive_state(self):
        return f"{self.get_nick_name()} is {self.dead_or_alive()}"

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
        for each_level in range(1, self.level):
            need_to_up += (2 ** each_level) * 70
        return need_to_up if self.level != 1 else 100

    def level_up(self):
        while True:
            if self.get_xp_points() >= self.need_to_up():
                self.set_xp_points(self.xp_points - self.need_to_up())
                self.level += 1
                if self.get_classname() == 'Warrior':
                    self._hp += percentage(27, self._hp, False)
                    self._mp += percentage(27, self._mp, False)
                    self._st += percentage(25, self._st, False)
                    self._ag += percentage(24, self._ag, False)
                    self._mg += percentage(24, self._mg, False)
                    self._df += percentage(25, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                elif self.get_classname() == 'Mage':
                    self._hp += percentage(27, self._hp, False)
                    self._mp += percentage(29, self._mp, False)
                    self._st += percentage(23, self._st, False)
                    self._ag += percentage(24, self._ag, False)
                    self._mg += percentage(27, self._mg, False)
                    self._df += percentage(23, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                elif self.get_classname() == 'Rogue':
                    self._hp += percentage(28, self._hp, False)
                    self._mp += percentage(27, self._mp, False)
                    self._st += percentage(24, self._st, False)
                    self._ag += percentage(27, self._ag, False)
                    self._mg += percentage(24, self._mg, False)
                    self._df += percentage(23, self._df, False)
                    self.base_hp = self._hp
                    self.base_mp = self._mp
                    self.base_st = self._st
                    self.base_ag = self._ag
                    self.base_mg = self._mg
                    self.base_df = self._df
                print(f"Level up! now you are level: {self.level}")
            else:
                print(f"You need more xp points! reach: {self.need_to_up()}")
                break

    def need_to_next(self):
        operation = self.need_to_up() - self.get_xp_points()
        return operation if operation > 0 else 0

    def get_level_bar(self):
        level_bar = ['[ ]' for x in range(10)]
        percent_of_bar = ((self.get_xp_points() * 100) // self.need_to_up()) // 10
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


class Warrior(Player):

    base_hp, base_mp, base_st = 104, 89, 103
    base_ag, base_mg, base_df = 60, 10, 30

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
    base_ag, base_mg, base_df = 54, 100, 23

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

    base_hp, base_mp, base_st = 99, 30, 63
    base_ag, base_mg, base_df = 65, 66, 20

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

    base_hp, base_mp, base_st = 45, 15, 30
    base_ag, base_mg, base_df = 35, 30, 10

    def __init__(self, nick_name, mob_level):
        self.nick_name = nick_name
        self.level = mob_level
        self.isalive = True
        self._hp = Monster.base_hp
        self._mp = Monster.base_mp
        self._st = Monster.base_st
        self._ag = Monster.base_ag
        self._mg = Monster.base_mg
        self._df = Monster.base_df
        for level in range(self.level):
            self._hp += 10
            self._mp += 10
            self._st += 5
            self._ag += 5
            self._mg += 5
            self._df += 10
            self.base_hp, self.base_mp, self.base_st = self._hp, self._mp, self._st
            self.base_ag, self.base_mg, self.base_df = self._ag, self._mg, self._df
        self.avg_damage = (self._st + self._mg) // 2

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

def get_info(entity_to_get):
    return f"""your helth in {entity_to_get.get_classname()} class has: {entity_to_get.get_hp()} points
    your mana in {entity_to_get.get_classname()} class has: {entity_to_get.get_mp()} points
    your strength in {entity_to_get.get_classname()} class has: {entity_to_get.get_st()} points
    your agility in {entity_to_get.get_classname()} class has: {entity_to_get.get_ag()} points
    your magic in {entity_to_get.get_classname()} class has: {entity_to_get.get_mg()} points
    your defense in {entity_to_get.get_classname()} class has: {entity_to_get.get_df()} points"""

def get_status_table(attacker, defender):
    return f'''
    [HP] {attacker.get_hp()} x [HP] {defender.get_hp()}
    [MP] {attacker.get_mp()} x [MP] {defender.get_mp()}    
    [ST] {attacker.get_st()} x [ST] {defender.get_st()}
    [AG] {attacker.get_ag()} x [AG] {defender.get_ag()}
    [MG] {attacker.get_mg()} x [MG] {defender.get_mg()}
    [DF] {attacker.get_df()} x [DF] {defender.get_df()}
    '''


if __name__ == '__main__':
    pass
