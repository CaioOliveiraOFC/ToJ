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
        mob2 = Monster(mobs[2], 2)
        mob3 = Monster(mobs[3], 4)
        mob4 = Monster(mobs[4], 6)
        mob5 = Monster(mobs[5], 8)
        mob6 = Monster(mobs[6], 16)
        mob7 = Monster(mobs[7], 32)

        # Each instance is a entity
        entities = [player1,
                    player2,
                    player3,
                    mob1, mob2, mob3, mob4,
                    mob5, mob6, mob7]

        line()
        print('Fight example')
        line()
        fight(player2, player1)


main()
