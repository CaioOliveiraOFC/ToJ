#!/usr/bin/env python3

from toj_source.classes import *
from toj_source.interactions import *

def main():
    if __name__ == '__main__':

        line()
        print('My entts')
        line()

        player1 = Warrior('Player1')
        player2 = Warrior('Player2')
        player3 = Rogue('Player3')
        mobs = {1: 'Wolf',
                2: 'Bear',
                3: 'Goblin',
                4: 'Black Knight'}

        player3.set_xp_points(400000)
        player3.level_up()
        player3.show_hp_bar()

        mob1 = Monster(mobs[1], 1)
        mob2 = Monster(mobs[2], 2)
        mob3 = Monster(mobs[3], 4)
        mob4 = Monster(mobs[4], 8)

        # Each instance is a entity
        entities = [player1,
                    player2,
                    player3,
                    mob1, mob2, mob3, mob4]

        for entt in entities:
            line()
            entt.show_attributes()

        line()
        print('Fight example')
        line()
        fight(player1, player2)
        player1.rest()
        fight(player3, player1)


main()
