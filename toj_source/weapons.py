class Weapon:

    def __init__(self, name, wp_level, avg_dmg):
        self.name = name
        self.wp_level = wp_level
        self.avg_dmg = avg_dmg
        self.equipped = False

    def get_wp_level(self):
        return self.wp_level

    def get_name(self):
        return self.name

    def is_equipped(self):
        return self.equipped

    def set_equipped(self):
        self.equipped = True

class Axe(Weapon):

    base_st, base_mg, base_ag = 10, 2, 2

    def __init__(self, name, add_st=0, add_mg=0, add_ag=0, wp_level=1):
        self.name = name
        self._st = Axe.base_st + add_st
        self._mg = Axe.base_mg + add_mg
        self._ag = Axe.base_ag + add_ag
        self.classes = ["Warrior"]
        super().__init__(name, wp_level, avg_dmg=(self._st + self._mg) // 2)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def type():
        return 'Axe'

    def get_st(self):
        return self._st

    def get_mg(self):
        return self._mg

    def get_ag(self):
        return self._ag

class Sword(Weapon):

    base_st, base_mg, base_ag = 6, 6, 2

    def __init__(self, name, add_st=0, add_mg=0, add_ag=0, wp_level=1):
        self.name = name
        self._st = Sword.base_st + add_st
        self._mg = Sword.base_mg + add_mg
        self._ag = Sword.base_ag + add_ag
        self.classes = ['Warrior', 'Mage', 'Rogue']
        super().__init__(name, wp_level, avg_dmg=(self._st + self._mg) // 2)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def type():
        return 'Sword'

    def get_st(self):
        return self._st

    def get_mg(self):
        return self._mg

    def get_ag(self):
        return self._ag

class Staff(Weapon):

    base_st, base_mg, base_ag = 2, 10, 2

    def __init__(self, name, add_st=0, add_mg=0, add_ag=0, wp_level=1):
        self.name = name
        self._st = Staff.base_st + add_st
        self._mg = Staff.base_mg + add_mg
        self._ag = Staff.base_ag + add_ag
        self.classes = ["Mage"]
        super().__init__(name, wp_level, avg_dmg=(self._st + self._mg) // 2)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def type():
        return 'Staff'

    def get_st(self):
        return self._st

    def get_mg(self):
        return self._mg

    def get_ag(self):
        return self._ag

class Knife(Weapon):

    base_st, base_mg, base_ag = 4, 4, 4

    def __init__(self, name, add_st=0, add_mg=0, add_ag=0, wp_level=1):
        self.name = name
        self._st = Knife.base_st + add_st
        self._mg = Knife.base_mg + add_mg
        self._ag = Knife.base_ag + add_ag
        self.classes = ["Rogue"]
        super().__init__(name, wp_level, avg_dmg=(self._st + self._mg) // 2)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def type():
        return 'Knife'

    def get_st(self):
        return self._st

    def get_mg(self):
        return self._mg

    def get_ag(self):
        return self._ag

def get_wp_attr(wp):
    print(f'Name -> {wp.get_name()}'.center(100))
    classes = ', '.join(wp.get_lst_class())
    print(f'Type -> {wp.type()}'.center(100))
    print(f'Classes -> {classes}'.center(100))
    print(f'Level -> {wp.wp_level}'.center(100))
    print(f'AVG -> {wp.avg_dmg}'.center(100))
    print(f'ST -> {wp.get_st()}'.center(100))
    print(f'MG -> {wp.get_mg()}'.center(100))
    print(f'AG -> {wp.get_ag()}'.center(100))


if __name__ == '__main__':
    pass