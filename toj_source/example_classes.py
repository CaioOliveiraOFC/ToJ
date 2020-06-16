#!/usr/bin/env python3

from toj_source.classes import *
from toj_source.interactions import *
from toj_source.weapons import *


def main():
    if __name__ == '__main__':

        line(100)
        print('My entts'.center(100))
        line(100)

        sword1 = Sword('Simple Sword')

        player1 = Warrior('Player1')
        player1.set_xp_points(6120)
        player1.level_up(False)
        player2 = Rogue('Player2')
        player2.set_xp_points(6120)
        player2.level_up(False)
        player3 = Mage('Player3')
        player3.set_xp_points(6120)
        player3.level_up(False)
        # player4 = Mage('Player4')
        # player4.set_xp_points(6120)
        # player4.level_up(False)
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

        line(100)
        print('Fight example'.center(100))
        line(100)
        mobs = [mob1, mob2, mob3, mob4,
                mob5, mob6, mob7, mob8,
                mob9, mob10]
        players = [player1, player2, player3]

        for mob in mobs:
            for player in players:
                fight(player, mob)

        line(100, simbol="=")
        for player in players:
            print(f'{player.get_kill_streak()} {player.get_nick_name()} max kill streak'.center(100))
            print(f'{player.wins} {player.get_nick_name()} wins'.center(100))
        line(100, simbol="=")


main()
