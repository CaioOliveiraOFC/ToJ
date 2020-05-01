#!/usr/bin/env python3


class Player:
    # class atributes
    def __init__(self, nick_name):
        self.nick_name = nick_name

    def show_nick_name(self):
        print(self.nick_name)


class Warrior(Player): 

    #STATIC ATRIBUTES
    HP, MP, ST, AG, MG, DF = 104, 89, 103, 60, 23, 30

    def __init__(self, nick_name):
        Player.__init__(self, nick_name)

    def show_atributes(self):
        print(f"Your Helth in Warrior class has: {self.HP} points")
        print(f"Your Mana in Warrior class has: {self.MP} points")
        print(f'Your Strength in Warrior class has: {self.ST} points')
        print(f'Your Agility in Warrior class has: {self.AG} points')
        print(f'Your Magic in Warrior class has: {self.MG} points')
        print(f'Your Defense in Warrior class has: {self.DF} points')



if __name__=='__main__':
    p1 = Warrior('TobiasFate')
    p1.show_nick_name()
    p1.show_atributes()
    
