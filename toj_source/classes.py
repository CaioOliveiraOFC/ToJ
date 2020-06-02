#!/usr/bin/env python3

from random import choice, shuffle

class Player:
    
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True 
        self.base_HP = self._HP
        self.base_MP = self._MP
        self.base_ST = self._ST
        self.base_AG = self._AG
        self.base_MG = self._MG
        self.base_DF = self._DF
    

    def get_isalive(self):
        return isalive


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
                    self._HP += self._HP * 27//100 
                    self._MP += self._MP * 27//100  
                    self._ST += self._HP * 25//100   
                    self._AG += self._AG * 24//100   
                    self._MG += self._MG * 24//100   
                    self._DF += self._DF * 25//100 
                    self.base_HP = self._HP
                    self.base_MP = self._MP
                    self.base_ST = self._ST
                    self.base_AG = self._AG
                    self.base_MG = self._MG
                    self.base_DF = self._DF
                elif self.get_classname() == 'Mage':
                    self._HP += self._HP * 27//100 
                    self._MP += self._MP * 29//100  
                    self._ST += self._HP * 23//100   
                    self._AG += self._AG * 24//100   
                    self._MG += self._MG * 27//100   
                    self._DF += self._DF * 23//100  
                    self.base_HP = self._HP
                    self.base_MP = self._MP
                    self.base_ST = self._ST
                    self.base_AG = self._AG
                    self.base_MG = self._MG
                    self.base_DF = self._DF
                elif self.get_classname() == 'Rogue':
                    self._HP += self._HP * 28//100 
                    self._MP += self._MP * 27//100
                    self._ST += self._HP * 24//100
                    self._AG += self._AG * 27//100   
                    self._MG += self._MG * 24//100   
                    self._DF += self._DF * 23//100 
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
        print(f"your helth in {self.get_classname()} class has: {self._hp} points")
        print(f"your mana in {self.get_classname()} class has: {self._mp} points")
        print(f'your strength in {self.get_classname()} class has: {self._st} points')
        print(f'your agility in {self.get_classname()} class has: {self._ag} points')
        print(f'your magic in {self.get_classname()} class has: {self._mg} points')
        print(f'your defense in {self.get_classname()} class has: {self._df} points')


    def attack(self, defender):
        #attack = [0 for x in range((defender._AG - (20//100)) // 100)]
        #fail_attack = [1 for x in range(self._AG * 10//100)]
        #mix = attack[:] + fail_attack[:]
        #attack_prob = [choice(mix) for x in range(10)]
        #shuffle(attack_prob)
        #if choice(attack_prob) == 0: 
        damage = abs((self._ST * 10//100) + (self._MG * 10//100) - (defender._DF * 5//100))
        defender._HP -= damage
        print(f"{self.nick_name} deal {damage} of damage in {defender.nick_name}", end=', ')
        print(f"Now {defender.nick_name} have {defender._HP} of HP")
        #else:
        #    print(f'{self.nick_name} has missed the attack!!')


    def show_HP_bar(self):
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
    
            

class Warrior(Player): 

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 104, 89, 103, 60, 10, 23 
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

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 96, 100, 32, 54, 100, 20
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

    def __init__(self, nick_name):
        self._HP, self._MP, self._ST, self._AG, self._MG, self._DF = 99, 30, 63, 65, 66, 20
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


class Monster():

    base._HP, base._MP, base._ST, = 45, 15 , 31
    base._AG, base._MG, base._DF = 34, 33, 10

    def __init__(self, name):
        self.name = name
        self.level = 1
        for atr in range(len(self.level)):
            self._HP += (base_HP * (5/100)) + base_HP
            self._MP += (base_MP * (5/100)) + base_MP
            self._ST += (base_ST * (5/100)) + base_ST    
            self._AG += (base_AG * (5/100)) + base_AG
            self._MG += (base_MG * (5/100)) + base_MG
            self._DF += (base_DF * (5/100)) + base_DF


    def show_attributes(self):
        print(f"your helth in {self.name} class has: {self._HP} points")
        print(f"your mana in {self.name} class has: {self._MP} points")
        print(f'your strength in {self.name} class has: {self._ST} points')
        print(f'your agility in {self.name} class has: {self._AG} points')
        print(f'your magic in {self.name} class has: {self._MG} points')
        print(f'your defense in {self.name} class has: {self._DF} points')
    
    
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


if __name__=='__main__':
    pass
