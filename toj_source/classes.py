#!/usr/bin/env python3

from toj_source.math_operations import percentage

class Player:

    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = (self._ST + self._MG) // 3

    def get_avg_damage(self):
        return self.avg_damage

    def get_isalive(self):
        return self.isalive

    def set_isalive(self, state=True):
        if state != True and state != False:
            raise ValueError("Expected True or False")
        self.isalive = bool(state)

    def dead_or_alive(self):
        """
        -----> Return string Dead or Alive
        """
        return "alive" if self.isalive else "dead"

    def show_alive_state(self):
        return f"{self.get_nick_name()} is {self.dead_or_alive()}"

    def set_xp_points(self, amount):
        self.xp_points = amount

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
            need_to_up += (2 ** each_level) * 100
        return need_to_up if self.level != 1 else 100

    def level_up(self):
        while True:
            if self.get_xp_points() >= self.need_to_up():
                self.set_xp_points(self.xp_points - self.need_to_up())
                self.level += 1
                if self.get_classname() == 'Warrior':
                    self._HP += percentage(27, self._HP, False)
                    self._MP += percentage(27, self._MP, False)
                    self._ST += percentage(25, self._ST, False)
                    self._AG += percentage(24, self._AG, False)
                    self._MG += percentage(24, self._MG, False)
                    self._DF += percentage(25, self._DF, False)
                    self.base_HP = self._HP
                    self.base_MP = self._MP
                    self.base_ST = self._ST
                    self.base_AG = self._AG
                    self.base_MG = self._MG
                    self.base_DF = self._DF
                elif self.get_classname() == 'Mage':
                    self._HP += percentage(27, self._HP, False)
                    self._MP += percentage(29, self._MP, False)
                    self._ST += percentage(23, self._ST, False)
                    self._AG += percentage(24, self._AG, False)
                    self._MG += percentage(27, self._MG, False)
                    self._DF += percentage(23, self._DF, False)
                    self.base_HP = self._HP
                    self.base_MP = self._MP
                    self.base_ST = self._ST
                    self.base_AG = self._AG
                    self.base_MG = self._MG
                    self.base_DF = self._DF
                elif self.get_classname() == 'Rogue':
                    self._HP += percentage(28, self._HP, False)
                    self._MP += percentage(27, self._MP, False)
                    self._ST += percentage(24, self._ST, False)
                    self._AG += percentage(27, self._AG, False)
                    self._MG += percentage(24, self._MG, False)
                    self._DF += percentage(23, self._DF, False)
                    self.base_HP = self._HP
                    self.base_MP = self._MP
                    self.base_ST = self._ST
                    self.base_AG = self._AG
                    self.base_MG = self._MG
                    self.base_DF = self._DF
                print(f"Level up! now you are level: {self.level}")
            else:
                print(f"You need more xp points! reach: {self.need_to_up()}")
                break

    def need_to_next(self):
        operation = self.need_to_up() - self.get_xp_points()
        return operation if operation > 0 else 0

    def show_level_bar(self):
        level_bar = ['[ ]' for x in range(10)]
        percent_of_bar = ((self.get_xp_points() * 100) // self.need_to_up()) // 10
        printable = str()
        if percent_of_bar == 0:
            printable = ''.join(level_bar)
            print(f'|{printable}|')
        else:
            try:
                for char in range(0, percent_of_bar):
                    level_bar[char] = "[x]"
                    printable = ''.join(level_bar)
                print(f'You have {self.get_xp_points()} xp points')
                print(f"|{printable}|")
            except IndexError:
                level_bar = ['[x]' for x in range(10)]
                printable = ''.join(level_bar)
                print(f'You have {self.get_xp_points} xp points')
                print(f'|{printable}|')

    def show_attributes(self):
        print(f"your helth in {self.get_classname()} class has: {self._HP} points")
        print(f"your mana in {self.get_classname()} class has: {self._MP} points")
        print(f'your strength in {self.get_classname()} class has: {self._ST} points')
        print(f'your agility in {self.get_classname()} class has: {self._AG} points')
        print(f'your magic in {self.get_classname()} class has: {self._MG} points')
        print(f'your defense in {self.get_classname()} class has: {self._DF} points')

    def show_hp_bar(self):
        printable = str()
        hp_bar = ['[ ]' for x in range(10)]
        percent_of_bar = (self.get_HP() * 100) // self.base_HP // 10
        if percent_of_bar <= 0:
            printable = ''.join(hp_bar)
            print(f"{self.get_nick_name()} have {self.get_HP()} HP points: ")
            print(f'|{printable}|')
        else:
            for char in range(percent_of_bar):
                hp_bar[char] = "[#]"
                printable = ''.join(hp_bar)
            print(f"{self.get_nick_name()} have {self.get_HP()} HP points: ")
            print(f'|{printable}|')

    def get_hp_bar(self):
        printable = str()
        hp_bar = ['[ ]' for x in range(10)]
        percent_of_bar = (self.get_HP() * 100) // self.base_HP // 10
        if percent_of_bar <= 0:
            printable = ''.join(hp_bar)
            return f'|{printable}| {self._HP} HP points'
        else:
            for char in range(percent_of_bar):
                hp_bar[char] = "[#]"
                printable = ''.join(hp_bar)
            return f'|{printable}| {self._HP} HP points'

    def rest(self):
        self._HP, self._MP, self._ST = self.base_HP, self.base_MP, self.base_ST
        self._AG, self._MG, self._DF = self.base_AG, self.base_MG, self.base_DF

class Warrior(Player):

    base_HP, base_MP, base_ST = 104, 89, 103
    base_AG, base_MG, base_DF = 60, 10, 30

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST = Warrior.base_HP, Warrior.base_MP, Warrior.base_ST
        self._AG, self._MG, self._DF = Warrior.base_AG, Warrior.base_MG, Warrior.base_DF
        super().__init__(nick_name)

    def get_classname(self):
        return 'Warrior'

    def get_HP(self):
        return self._HP

    def get_MP(self):
        return self._MP

    def get_ST(self):
        return self._ST

    def get_AG(self):
        return self._AG

    def get_MG(self):
        return self._MG

    def get_DF(self):
        return self._DF

    def set_HP(self, new_HP):
        self._HP = new_HP

    def set_MP(self, new_MP):
        self._MP = new_MP

    def set_ST(self, new_ST):
        self._ST = new_ST

    def set_AG(self, new_AG):
        self._AG = new_AG

    def set_MG(self, new_MG):
        self._MG = new_MG

    def set_DF(self, new_DF):
        self._DF = new_DF


class Mage(Player):

    base_HP, base_MP, base_ST = 96, 100, 32
    base_AG, base_MG, base_DF = 54, 100, 23

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST = Mage.base_HP, Mage.base_MP, Mage.base_ST
        self._AG, self._MG, self._DF = Mage.base_AG, Mage.base_MG, Mage.base_DF
        super().__init__(nick_name)

    def get_classname(self):
        return 'Mage'

    def get_HP(self):
        return self._HP

    def get_MP(self):
        return self._MP

    def get_ST(self):
        return self._ST

    def get_AG(self):
        return self._AG

    def get_MG(self):
        return self._MG

    def get_DF(self):
        return self._DF

    def set_HP(self, new_HP):
        self._HP = new_HP

    def set_MP(self, new_MP):
        self._MP = new_MP

    def set_ST(self, new_ST):
        self._ST = new_ST

    def set_AG(self, new_AG):
        self._AG = new_AG

    def set_MG(self, new_MG):
        self._MG = new_MG

    def set_DF(self, new_DF):
        self._DF = new_DF


class Rogue(Player):

    base_HP, base_MP, base_ST = 99, 30, 63
    base_AG, base_MG, base_DF = 65, 66, 20

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST = Mage.base_HP, Mage.base_MP, Mage.base_ST
        self._AG, self._MG, self._DF = Mage.base_AG, Mage.base_MG, Mage.base_DF
        super().__init__(nick_name)

    def get_classname(self):
        return 'Rogue'

    def get_HP(self):
        return self._HP

    def get_MP(self):
        return self._MP

    def get_ST(self):
        return self._ST

    def get_AG(self):
        return self._AG

    def get_MG(self):
        return self._MG

    def get_DF(self):
        return self._DF

    def set_HP(self, new_HP):
        self._HP = new_HP

    def set_MP(self, new_MP):
        self._MP = new_MP

    def set_ST(self, new_ST):
        self._ST = new_ST

    def set_AG(self, new_AG):
        self._AG = new_AG

    def set_MG(self, new_MG):
        self._MG = new_MG

    def set_DF(self, new_DF):
        self._DF = new_DF


class Monster:

    base_HP, base_MP, base_ST = 45, 15, 30
    base_AG, base_MG, base_DF = 35, 30, 10

    def __init__(self, nick_name, mob_level):
        self.nick_name = nick_name
        self.level = mob_level
        self.isalive = True
        self._HP = Monster.base_HP
        self._MP = Monster.base_MP
        self._ST = Monster.base_ST
        self._AG = Monster.base_AG
        self._MG = Monster.base_MG
        self._DF = Monster.base_DF
        for level in range(self.level):
            self._HP += 5
            self._MP += 5
            self._ST += 5
            self._AG += 5
            self._MG += 5
            self._DF += 5

    def show_attributes(self):
        print(f"{self.nick_name} Monster has: {self._HP} HP points")
        print(f"{self.nick_name} Monster has: {self._HP} MP points")
        print(f"{self.nick_name} Monster has: {self._HP} ST points")
        print(f"{self.nick_name} Monster has: {self._HP} AG points")
        print(f"{self.nick_name} Monster has: {self._HP} MG points")
        print(f"{self.nick_name} Monster has: {self._HP} DF points")

    def get_level(self):
        return self.level

    def set_isalive(self, state):
        self.isalive = state

    def get_isalive(self):
        return self.isalive

    def set_level(self, new_level):
        self.level = new_level

    def get_HP(self):
        return self._HP

    def get_MP(self):
        return self._MP

    def get_ST(self):
        return self._ST

    def get_ag(self):
        return self._AG

    def get_MG(self):
        return self._MG

    def get_DF(self):
        return self._DF

    def set_HP(self, new_HP):
        self._HP = new_HP

    def set_MP(self, new_MP):
        self._MP = new_MP

    def set_ST(self, new_ST):
        self._ST = new_ST

    def set_AG(self, new_AG):
        self._AG = new_AG

    def set_MG(self, new_MG):
        self._MG = new_MG

    def set_DF(self, new_DF):
        self._DF = new_DF


if __name__ == '__main__':
    pass
