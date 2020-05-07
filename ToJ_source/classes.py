#!/usr/bin/env python3


class Player:
    
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
    

    def set_xp_points(self, amount):
        self.xp_points = amount


    def get_xp_points(self):
        return self.xp_points


    def get_nick_name(self):
        print(self.nick_name)


    def get_level(self):
        return self.level


    def need_to_up(self):
        if self.level == 1:
            need_to_up = 100
            return need_to_up
        else:
            need_to_up = 0
            for each_level in range(1, self.level):
                need_to_up += (2 ** each_level) * 100
            return need_to_up


    def level_up(self):
        while True:
            if self.get_xp_points() >= self.need_to_up():
                self.set_xp_points(self.xp_points - self.need_to_up())
                self.level += 1
                if self.get_classname() == 'Warrior':
                    self._HP += self._HP * 5//100 
                    self._MP += self._MP * 5//100  
                    self._ST += self._HP * 3//100   
                    self._AG += self._AG * 2//100   
                    self._MG += self._MG * 2//100   
                    self._DF += self._DF * 3//100  
                elif self.get_classname() == 'Mage':
                    self._HP += self._HP * 5//100 
                    self._MP += self._MP * 7//100  
                    self._ST += self._HP * 1//100   
                    self._AG += self._AG * 2//100   
                    self._MG += self._MG * 5//100   
                    self._DF += self._DF * 1//100  
                elif self.get_classname() == 'Rogue':
                    self._HP += self._HP * 6//100 
                    self._MP += self._MP * 5//100  
                    self._ST += self._HP * 2//100   
                    self._AG += self._AG * 5//100   
                    self._MG += self._MG * 2//100   
                    self._DF += self._DF * 3//100 
                print(f"Level up! now you are level: {self.level}")
            else:
                print(f"You need more xp points! reach: {self.need_to_up()}")
                break
        

    def need_to_next(self):
        return self.need_to_up() - self.get_xp_points()


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
        print(f"Your Helth in {self.get_classname()} class has: {self._HP} points")
        print(f"Your Mana in {self.get_classname()} class has: {self._MP} points")
        print(f'Your Strength in {self.get_classname()} class has: {self._ST} points')
        print(f'Your Agility in {self.get_classname()} class has: {self._AG} points')
        print(f'Your Magic in {self.get_classname()} class has: {self._MG} points')
        print(f'Your Defense in {self.get_classname()} class has: {self._DF} points')

        
class Warrior(Player): 

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 104, 89, 103, 60, 23, 30 
   

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

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 104, 89, 103, 60, 23, 30
        

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

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 99, 30, 63, 100, 66, 20


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


class Monster():
    def __init__(self, name):
        self.name = name
        self.level = 1


if __name__=='__main__':
    p1 = Warrior("Zlatan")
    print('Create the object p1')
    print(f'The type of the class is : {type(p1)}')
    print("""
    The atributes of the object is:
    """)
    p1.show_attributes()
    print("""
    The level status for p1 is:
    """)
    print(f'The level of the p1 is: {p1.get_level()}')
    print(f'They have {p1.xp_points} xp points')
    print(f'To the next level he need {p1.need_to_next()} xp points')
    p1.show_level_bar()
    print(F'I gave you more xp points:')
    p1.xp_points = 100
    print('Added 100 xp points for p1')
    p1.show_level_bar()
    print('If the level bar is full, p1 can up your level')
    p1.level_up()
    print("Whenever you up, the game will encourage you to win more")
    print("Now the level bar is: ")
    p1.show_level_bar()
    print("For each level you attributes can be incresed")
    print("""
    The atributes of the object is:
    """)
    p1.show_attributes()
