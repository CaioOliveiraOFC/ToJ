#!/usr/bin/env python3
# This is the most important part of the program
# There should be a better way to create lots of classes and use less code but I don't know how

from math_operations import percentage

class Player:
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = (self._st + self._mg) // 3
        self.kill_streak = 0
        self.wins = 0
        self.coins = 0
        self.skill_points = 0
        self.inventory = {"Weapon": None, "Helmet": None,
                          "sdfaBody": None, "Legs": None,
                          "Shoes": None}
        self.skills = {1: None, 2: None, 3: None, 4: None}

    def get_coins(self):
        # This function returns the amount of coins the player has
        return self.coins

    def set_coins(self, amount):
        # This function sets the amount of coins the player has
        self.coins = amount

    def receive_coins(self, amount):
        # This function gives the player coins
        self.coins += amount

    def win(self):
        # This fucntion sets a win condition
        self.wins += 1

    def get_kill_streak(self):
        # This function returns the kill streak 
        return self.kill_streak

    def add_kill_streak(self):
        # This function adds a kill streak
        self.kill_streak += 1

    def reset_kill_streak(self):
        # This function resets the kill streak
        self.kill_streak = 0
    
    def get_avg_damage(self):
        # This function returns the average damage of the player
        return self.avg_damage

    def get_isalive(self):
        # This function returns if the player is alive or not
        return self.isalive

    def set_isalive(self, state=True):
        # This function sets the player's state
        if state is not True and state is not False:
            raise ValueError("Expected True or False")
        self.isalive = bool(state)

    def reduce_hp(self, quantty):
        # This function reduces the player's hp
        self._hp -= quantty

    @staticmethod
    def my_type():
        return 'Human'
        # This function returns the type of the class

    def set_xp_points(self, amount):
        # This function sets the xp points
        self.xp_points = amount

    def add_xp_points(self, amount):
        # This function adds xp points to the player
        self.xp_points += amount

    def get_xp_points(self):
        # This function returns the xp points
        return self.xp_points

    def get_nick_name(self):
        # This function returns the nick name of the player
        return self.nick_name

    def get_level(self):
        # This function returns the level of the player
        return self.level

    def set_level(self, new_level):
        # This function sets the level of the player
        self.level = new_level

    def need_to_up(self):
        # This function returns the xp points needed to level up
        need_to_up: int = 0
        if self.level == 1:
            # This is only for the first level
            need_to_up = self.level + 7 * 10
        else:
            # Loops through the levels and checks how much xp points are needed to level up
            for each_level in range(1, self.level):
                need_to_up += (self.level + 7) * 10
        return need_to_up

    @staticmethod
    def xp_for_level(level):
        # This function calculates how much xp points are needed to the next level of the player
        xp_to_level = 0
        need_to_up = 0
        if level == 1:
            # This is only for the first level
            xp_to_level = (level + 7) * 10
        else:
            # Loops through and calculates how much xp points are needed to level up
            for each_level in range(1, level - 1):
                need_to_up += (level + 7) * 10
                xp_to_level += need_to_up
        return xp_to_level

    def level_up(self, show=True):
        # This function levels up the player
        self.skill_points += 3
        while True:
            if self.get_xp_points() >= self.need_to_up():
                # This checks if the player has enough xp points to level up
                # if true calculates the difference between the xp points and the xp points needed to level up
                self.set_xp_points(self.xp_points - self.need_to_up())
                # Then increases the level of the player
                self.level += 1
                if self.get_classname() == 'Warrior':
                    # If the player is a warrior, he must have more hp and more defense 
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
                    # If the player is a mage, he must have more mp and more mg 
                    self._hp += percentage(17, self._hp, False)
                    self._mp += percentage(15, self._mp, False)
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
                    # If the player is a rogue, he must have more st and more ag
                    # Do not add too much ag cuz it will make the player too strong
                    # TODO: I need to change this class, Rogue is too weak
                    self._hp += percentage(14, self._hp, False)
                    self._mp += percentage(14, self._mp, False)
                    self._st += percentage(17, self._st, False)
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
        # This function returns the xp points needed to his self next level
        operation = self.need_to_up() - self.get_xp_points()
        return operation if operation > 0 else 0

    def get_level_bar(self):
        # This function returns a graphical representation of the player's level
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
        # This function rest the Player
        # This is bacialy a function that heals the Player and resets the cooldown of the spells
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        self.set_isalive()
        #TODO: reset the cooldown of the spells

    def equip_a_gun(self, gun):
        # This function equips a gun to the player
        if not gun.is_equipped():
            # checks if the gun is equiped 
            if gun.get_wp_level() <= self.get_level():
                # Only give the gun to the player if the player has the level to use it
                if self.get_classname() in gun.classes:
                    # Only give the gun to the player if the player is in the class that can use it
                    self._mg += gun.get_mg()
                    self._st += gun.get_st()
                    self._ag += gun.get_ag()
                    self.avg_damage += gun.avg_dmg
                    gun.set_equipped()
                    self.inventory["Weapon"] = gun.name
                    print(f'Congratulations {self.get_nick_name()} now you have {gun.name}'.center(100))
                else:
                    print(f'You need to be {"or".join(gun.get_lst_class())}'.center(100))
            else:
                print(f'You need level -> {gun.get_wp_level()} to use this weapon'.center(100))
        else:
            print('Someone is using this gun'.center(100))

    def equip_a_armor(self, ar):
        # This function equips a armor to the player
        if not ar.is_equipped():
            # checks if the armor is equiped
            if ar.get_ar_level() <= self.get_level():
                # Only give the armor to the player if the player is in the class that can use it
                if self.get_classname() in ar.classes:
                    self._df += ar.get_df()
                    ar.set_equipped()
                    self.inventory[ar.in_space()] = ar.name
                    print(f'Congratulations {self.get_nick_name()} now you have: {ar.name}'.center(100))
                else:
                    print(f'You need to be {"or".join(ar.get_lst_class())}'.center(100))
            else:
                print(f'You need level -> {ar.get_ar_level()} to use this armor'.center(100))
        else:
            print(f'Someone is using this armor'.center(100))

class Warrior(Player):
    # This class is the Warrior class
    # First we define the class status that every Warrior player must have
    # Warrior will have more HP and more DF than the other classes
    base_hp, base_mp, base_st = 104, 89, 104
    base_ag, base_mg, base_df = 3, 30, 30

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Warrior.base_hp, Warrior.base_mp, Warrior.base_st
        self._ag, self._mg, self._df = Warrior.base_ag, Warrior.base_mg, Warrior.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        # This function returns the class name
        return 'Warrior'

    def get_hp(self):
        # This function returns the HP of the player
        return self._hp

    def get_mp(self):
        # This function returns the MP of the player
        return self._mp

    def get_st(self):
        # This function returns the ST of the player
        return self._st

    def get_ag(self):
        # This function returns the AG of the player
        return self._ag

    def get_mg(self):
        # This function returns the MG of the player
        return self._mg

    def get_df(self):
        # This function returns the DF of the player
        return self._df

    def set_hp(self, new_hp):
        # This function sets the HP of the player
        self._hp = new_hp

    def set_mp(self, new_mp):
        # This function sets the MP of the player
        self._mp = new_mp

    def set_st(self, new_st):
        # This function sets the ST of the player
        self._st = new_st

    def set_ag(self, new_ag):
        # This function sets the AG of the player
        self._ag = new_ag

    def set_mg(self, new_mg):
        # This function sets the MG of the player
        self._mg = new_mg

    def set_df(self, new_df):
        # This function sets the DF of the player
        self._df = new_df


class Mage(Player):
    # This class is the Mage class
    # First we define the class status that every Mage player must have
    # Mage will have more MP and more MG than the other classes
    base_hp, base_mp, base_st = 96, 100, 32
    base_ag, base_mg, base_df = 3, 100, 23

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Mage.base_hp, Mage.base_mp, Mage.base_st
        self._ag, self._mg, self._df = Mage.base_ag, Mage.base_mg, Mage.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        # This function returns the class name
        return 'Mage'

    def get_hp(self):
        # This function returns the HP of the player
        return self._hp

    def get_mp(self):
        # This function returns the MP of the player
        return self._mp

    def get_st(self):
        # This function returns the ST of the player
        return self._st

    def get_ag(self):
        # This function returns the AG of the player
        return self._ag

    def get_mg(self):
        # This function returns the MG of the player
        return self._mg

    def get_df(self):
        # This function returns the DF of the player
        return self._df

    def set_hp(self, new_hp):
        # This function sets the HP of the player
        self._hp = new_hp

    def set_mp(self, new_mp):
        # This function sets the MP of the player
        self._mp = new_mp

    def set_st(self, new_st):
        # This function sets the ST of the player
        self._st = new_st

    def set_ag(self, new_ag):
        # This function sets the AG of the player
        self._ag = new_ag

    def set_mg(self, new_mg):
        # This function sets the MG of the player
        self._mg = new_mg

    def set_df(self, new_df):
        # This function sets the DF of the player
        self._df = new_df


class Rogue(Player):
    # This class is the Rogue class
    # First we define the class status that every Rogue player must have
    # Rogue will have more AG and more ST than the other classes
    # BASE STATUS:
    base_hp, base_mp, base_st = 99, 30, 67
    base_ag, base_mg, base_df = 10, 66, 20

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = Rogue.base_hp, Rogue.base_mp, Rogue.base_st
        self._ag, self._mg, self._df = Rogue.base_ag, Rogue.base_mg, Rogue.base_df
        super().__init__(nick_name)

    @staticmethod
    def get_classname():
        # This function returns the class name
        return 'Rogue'

    def get_hp(self):
        # This function returns the HP of the player
        return self._hp

    def get_mp(self):
        # This function returns the MP of the player
        return self._mp

    def get_st(self):
        # This function returns the ST of the player
        return self._st

    def get_ag(self):
        # This function returns the AG of the player
        return self._ag

    def get_mg(self):
        # This function returns the MG of the player
        return self._mg

    def get_df(self):
        # This function returns the DF of the player
        return self._df

    def set_hp(self, new_hp):
        # This function sets the HP of the player
        self._hp = new_hp

    def set_mp(self, new_mp):
        # This function sets the MP of the player
        self._mp = new_mp

    def set_st(self, new_st):
        # This function sets the ST of the player
        self._st = new_st

    def set_ag(self, new_ag):
        # This function sets the AG of the player
        self._ag = new_ag

    def set_mg(self, new_mg):
        # This function sets the MG of the player
        self._mg = new_mg

    def set_df(self, new_df):
        # This function sets the DF of the player
        self._df = new_df

class Monster:
    # This class is the Monster Class
    # The monsters are defined based on the stage of the game
    # The more the satege, the more stronger the monsters
    # The strenght of the monster will be defined randomly 
    base_hp, base_mp, base_st = 100, 40, 55
    base_ag, base_mg, base_df = 3, 50, 30

    def __init__(self, nick_name, mob_level=1):
        """ This function is the constructor of the Monster class """
        # The mosnter only need a nick name and the level of the mob
        self.nick_name = nick_name
        if mob_level == 0:
            # 0 is a invalid level
            # set the level to 1
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
            # calculates if the level of the monster is between 1 and 9
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
            # calculates if the level of the monster is between 10 and 19
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
            # calculates if the level of the monster is between 20 and infinit, It only can reach level 20
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
        # This function returns the average damage of the monster
        return self.avg_damage

    def reduce_hp(self, quantty):
        # This function reduces the HP of the monster
        self._hp -= quantty

    @staticmethod
    def my_type():
        # This function returns the type of the monster
        return 'COM'

    @staticmethod
    def get_classname():
        # This function returns the class name
        return 'Monster'

    def get_level(self):
        # This function returns the level of the monster
        return self.level

    def set_isalive(self, state=True):
        # This function checks if the monster is alive
        self.isalive = state

    def get_isalive(self):
        # This function returns the state of the monster
        return self.isalive

    def set_level(self, new_level):
        # This function sets the level of the monster
        self.level = new_level

    def get_hp(self):
        # This function returns the HP of the monster
        return self._hp

    def get_mp(self):
        # This function returns the MP of the monster
        return self._mp

    def get_st(self):
        # This function returns the ST of the monster
        return self._st

    def get_ag(self):
        # This function returns the AG of the monster
        return self._ag

    def get_mg(self):
        # This function returns the MG of the monster
        return self._mg

    def get_df(self):
        # This function returns the DF of the monster
        return self._df

    def set_hp(self, new_hp):
        # This function sets the HP of the monster
        self._hp = new_hp

    def set_mp(self, new_mp):
        # This function sets the MP of the monster
        self._mp = new_mp

    def set_st(self, new_st):
        # This function sets the ST of the monster
        self._st = new_st

    def set_ag(self, new_ag):
        # This function sets the AG of the monster
        self._ag = new_ag

    def set_mg(self, new_mg):
        # This function sets the MG of the monster
        self._mg = new_mg

    def set_df(self, new_df):
        # This function sets the DF of the monster
        self._df = new_df

    def restart(self):
        # This function restarts the monster
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
    """ This function compares the status of the two entities """
    print(f'Class |{ennt1.get_classname()} X {ennt2.get_classname()}| Class'.center(102))
    print(f'Level |{ennt1.get_level():<4} X {ennt2.get_level():>4}| Level'.center(100))
    print(f"AVG |{ennt1.avg_damage:<5} X {ennt2.avg_damage:>5}| AVG".center(100))
    print(f"HP |{ennt1.get_hp():<5} X {ennt2.get_hp():>5}| HP".center(100))
    print(f'MP |{ennt1.get_mp():<5} X {ennt2.get_mp():>5}| MP'.center(100))
    print(f'ST |{ennt1.get_st():<5} X {ennt2.get_st():>5}| ST'.center(100))
    print(f'AG |{ennt1.get_ag():<5} X {ennt2.get_ag():>5}| AG'.center(100))
    print(f'MG |{ennt1.get_mg():<5} X {ennt2.get_mg():>5}| MG'.center(100))
    print(f'DF |{ennt1.get_df():<5} X {ennt2.get_df():>5}| DF'.center(100))

def show_status(ennt1):
    """ this function shows the status of the entity """
    print(f'show status of {ennt1.get_nick_name()}')
    print (f'class |{ennt1.get_classname()}| class')
    print(f'level |{ennt1.get_level():<4}| level')
    print(f"avg |{ennt1.avg_damage:<5}| avg")
    print(f"hp |{ennt1.get_hp():<5}| hp")
    print(f'mp |{ennt1.get_mp():<5}| mp')
    print(f'st |{ennt1.get_st():<5}| st')
    print(f'ag |{ennt1.get_ag():<5}| ag')
    print(f'mg |{ennt1.get_mg():<5}| mg')
    print(f'df |{ennt1.get_df():<5}| df')

if __name__ == '__main__':
    pass
    # did I forget something?
    # No i didn't forget anything
    # i'm done with this file now
