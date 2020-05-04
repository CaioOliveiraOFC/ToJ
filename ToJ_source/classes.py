#!/usr/bin/env python3


class Player:
    
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0


    def show_nick_name(self):
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
            if self.xp_points >= self.need_to_up():
                self.xp_points -= self.need_to_up()
                self.level += 1
                print(f"Level up! now you are level: {self.level}")
            else:
                print(f"You need more xp points! reach: {self.need_to_up()}")
                break
        

    def need_to_next(self):
        return self.need_to_up() - self.xp_points


    def show_level_bar(self):
        level_bar = ['[]' for x in range(10)] 
        percent_of_bar = ((self.xp_points * 100) // self.need_to_up()) // 10
        printable = str()
        if percent_of_bar == 0:
            printable = ''.join(level_bar)
            print(f'|{printable}|')
        else:
            for char in range(0, percent_of_bar):
                level_bar[char] = "[x]"
                printable = ''.join(level_bar)
            print(f"|{printable}|")
                
class Warrior(Player): 

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self.__HP, self.__MP, self.__ST, self.__AG, self.__MG, self.__DF = 104, 89, 103, 60, 23, 30

    def show_atributes(self):
        print(f"Your Helth in Warrior class has: {self.__HP} points")
        print(f"Your Mana in Warrior class has: {self.__MP} points")
        print(f'Your Strength in Warrior class has: {self.__ST} points')
        print(f'Your Agility in Warrior class has: {self.__AG} points')
        print(f'Your Magic in Warrior class has: {self.__MG} points')
        print(f'Your Defense in Warrior class has: {self.__DF} points')
   

    def my_class(self):
        print('You area a Warrior')
   

    def get_HP(self):
        return self.__HP


    def get_MP(self):
        return self.__MP


    def get_ST(self):
        return self.__ST
    

    def get_AG(self):
        return self.__AG

  
    def get_MG(self):
        return self.__MG


    def get_DF(self):
        return self.__DF


class Mage(Player): 

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self.__HP, self.__MP, self.__ST, self.__AG, self.__MG, self.__DF = 96, 100, 32, 54, 100, 23

    def show_atributes(self):
        print(f"Your Helth in Mage class has: {self.__HP} points")
        print(f"Your Mana in Mage class has: {self.__MP} points")
        print(f'Your Strength in Mage class has: {self.__ST} points')
        print(f'Your Agility in Mage class has: {self.__AG} points')
        print(f'Your Magic in Mage class has: {self.__MG} points')
        print(f'Your Defense in Mage class has: {self.__DF} points')


    def my_class(self):
        print('You are a Mage!!')


    def get_HP(self):
        return self.__HP


    def get_MP(self):
        return self.__MP


    def get_ST(self):
        return self.__ST
    

    def get_AG(self):
        return self.__AG

  
    def get_MG(self):
        return self.__MG


    def get_DF(self):
        return self.__DF


class Rogue(Player): 

    def __init__(self, nick_name):
        super().__init__(nick_name)
        self.__HP, self.__MP, self.__ST, self.__AG, self.__MG, self.__DF = 99, 30, 63, 100, 66, 20

    def show_atributes(self):
        print(f"Your Helth in Rogue class has: {self.__HP} points")
        print(f"Your Mana in Rogue class has: {self.__MP} points")
        print(f'Your Strength in Rogue class has: {self.__ST} points')
        print(f'Your Agility in Rogue class has: {self.__AG} points')
        print(f'Your Magic in Rogue class has: {self.__MG} points')
        print(f'Your Defense in Rogue class has: {self.__DF} points')
    
    
    def my_class(self):
        print("You are a Rouge!!")


    def get_HP(self):
        return self.__HP


    def get_MP(self):
        return self.__MP


    def get_ST(self):
        return self.__ST
    

    def get_AG(self):
        return self.__AG

  
    def get_MG(self):
        return self.__MG


    def get_DF(self):
        return self.__DF

if __name__=='__main__':
    p1 = Warrior('TobiasFate')
    p1.show_nick_name()
    p1.show_atributes()
    p2 = Mage('Zlatan97')
    p2.show_nick_name()
    p2.show_atributes()
    p3 = Rogue('WeGaveUp')
    p3.show_nick_name()
    p3.show_atributes()
    print(p3.get_level())
    print(p1.get_HP())
    print(f'You are in level: {p1.level}, with {p1.xp_points} xp points')
    p1.level_up()
    p1.xp_points = 100
    print(f'I gave you 100 xp points')
    p1.show_level_bar()
    p1.level_up()
    print(f'You are in level: {p1.level}, with {p1.xp_points} xp points')
    p1.show_level_bar() 
    p1.xp_points = 100
    print(f'You are in level: {p1.level}, with {p1.xp_points} xp points')
    p1.show_level_bar()
