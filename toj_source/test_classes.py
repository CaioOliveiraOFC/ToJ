#!/usr/bin/env python3

from toj_source.classes import *
from toj_source.interactions import *
from toj_source.weapons import *


def main():
    if __name__ == '__main__':

        line(100)
        print('My entts'.center(100))
        line(100)

        Sword = Weapon('Simple Sword', 1, ['Warrior', 'Mage', 'Rogue'], 12, 6, 6, 2)

        player1 = Warrior('Player1')
        player1.set_xp_points(6120)
        player1.level_up(False)
        player2 = Rogue('Player2')
        player2.set_xp_points(6120)
        player2.level_up(False)
        player3 = Mage('Player3')
        player3.set_xp_points(6120)
        player3.level_up(False)
        player4 = Mage('Player4')
        player4.set_xp_points(6120)
        player4.level_up(False)
        mobs = {1: 'Wolf', 2: 'Bear',
                3: 'Goblin', 4: 'Black Knight',
                5: 'Nemesis', 6: 'Rakanoth',
                7: 'Thanos', 8: 'Demon',
                9: 'Red Skull', 10: 'Black Skull',
                11: 'Corrupt Paladin', 12: 'Stranger Villager'}

        mob1 = Monster(mobs[1], 10)
        mob2 = Monster(mobs[2], 11)
        mob3 = Monster(mobs[3], 13)
        mob4 = Monster(mobs[4], 11)
        mob5 = Monster(mobs[5], 11)
        mob6 = Monster(mobs[6], 11)
        mob7 = Monster(mobs[7], 11)
        mob8 = Monster(mobs[8], 8)
        mob9 = Monster(mobs[9], 11)
        mob10 = Monster(mobs[10], 11)
        mob11 = Monster(mobs[11], 20)
        mob12 = Monster(mobs[12], 13)
        # Each instance is a entity
        entities = [player1,
                    player2,
                    player3,
                    mob1, mob2, mob3, mob4,
                    mob5, mob6, mob7, mob8,
                    mob9, mob10]

        line(100)
        print('Fight example'.center(100))
        line(100)
        mobs = [mob1, mob2, mob3, mob4,
                mob5, mob6, mob7, mob8,
                mob9, mob10]

        fight(player3, player1)
        fight(player3, player2)
        line(100, simbol="=")
        print(f'{player3.get_kill_streak()} player3 max kill streak'.center(100))
        print(f'{player3.wins} player3 wins'.center(100))
        print(f'{player2.get_kill_streak()} player2 max kill streak'.center(100))
        print(f'{player2.wins} player2 wins'.center(100))
        line(100, simbol="=")


main()
