#!/usr/bin/env python3

from classes import *
from interactions import line, fight
from weapons import Axe, Staff
from armor import *


def main():

    if __name__ == '__main__':

        player1 = Warrior('Player1')
        player2 = Rogue('Player2')
        wp1 = Axe('Police Axe')
        wp2 = Staff('Leoric Staff')
        ar1 = Shoes("God's shoes")
        ar2 = Helmet('Great Head')
        ar3 = Body('Great Body', 30)
        ar4 = Legs('Airline legs')
        compare(player1, player2)
        line(100)
        player1.equip_a_gun(wp1)
        line(100)
        player1.equip_a_armor(ar1)
        line(100)
        player1.equip_a_armor(ar2)
        line(100)
        player2.equip_a_gun(wp2)
        line(100)
        player2.equip_a_armor(ar3)
        line(100)
        player2.equip_a_armor(ar4)
        line(100)
        fight(player2, player1)
        line(100)
        print(player1.inventory)
        line(100)
        print(player2.inventory)


main()
