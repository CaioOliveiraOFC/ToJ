#!/usr/bin/env python3

from toj_source.classes import *
from toj_source.interactions import *


def main():
    if __name__ == '__main__':

        line()
        print('My entts')
        line()

        player1 = Warrior('Player1')
        player2 = Rogue('Player2')
        player3 = Mage('Player3')
        mobs = {1: 'Wolf',
                2: 'Bear',
                3: 'Goblin',
                4: 'Black Knight',
                5: 'Nemesis',
                6: 'Rakanoth',
                7: 'Thanos'}

        mob1 = Monster(mobs[1], 1)
        mob2 = Monster(mobs[2], 1)
        mob3 = Monster(mobs[3], 1)
        mob4 = Monster(mobs[4], 1)
        mob5 = Monster(mobs[5], 4)
        mob6 = Monster(mobs[6], 6)
        mob7 = Monster(mobs[7], 3)

        # Each instance is a entity
        entities = [player1,
                    player2,
                    player3,
                    mob1, mob2, mob3, mob4,
                    mob5, mob6, mob7]

        line()
        print('Fight example')
        line()
        fight(player1, mob4)
        fight(player1, mob4)
        fight(player1, mob4)
        fight(player1, mob4)
        fight(player1, mob4)
        fight(player1, mob4)


main()
