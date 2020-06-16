class Armor:

    def __init__(self, name, ar_level):
        self.name = name
        self.ar_level = ar_level
        self.equipped = False

    def get_name(self):
        return self.name

    def get_ar_level(self):
        return self.ar_level

    def is_equipped(self):
        return self.equipped

    def set_equipped(self):
        self.equipped = True

    def get_level(self):
        return self.ar_level

class Shoes(Armor):

    base_df = 10

    def __init__(self, name, add_df=0, ar_level=1):
        self._df = Shoes.base_df + add_df
        self.classes = ['Warrior', 'Rogue', 'Mage']
        super().__init__(name, ar_level)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Shoes'

    def get_df(self):
        return self._df

class Legs(Armor):
    base_df = 10

    def __init__(self, name, add_df=0, ar_level=1):
        self._df = Shoes.base_df + add_df
        self.classes = ['Warrior', 'Rogue', 'Mage']
        super().__init__(name, ar_level)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Legs'

    def get_df(self):
        return self._df

class Helmet(Armor):
    base_df = 10

    def __init__(self, name, add_df=0, ar_level=1):
        self._df = Shoes.base_df + add_df
        self.classes = ['Warrior', 'Rogue', 'Mage']
        super().__init__(name, ar_level)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Helmet'

    def get_df(self):
        return self._df

class Body(Armor):

    base_df = 10

    def __init__(self, name, add_df=0, ar_level=1):
        self._df = Shoes.base_df + add_df
        self.classes = ['Warrior', 'Rogue', 'Mage']
        super().__init__(name, ar_level)

    def get_lst_class(self):
        return self.classes

    @staticmethod
    def in_space():
        return 'Body'

    def get_df(self):
        return self._df