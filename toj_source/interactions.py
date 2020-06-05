from random import choice
from toj_source.math_operations import percentage
from toj_source.classes import get_hp_bar, get_status_table

def fight(fighter1, fighter2):
    fighters = [fighter1, fighter2]
    order = choose_first(fighters)
    first = f'{order["Attacker"].nick_name} attacks first'
    battle_status1 = f'BATTLE STATUS'
    battle_status2 = f'{fighter1.nick_name} VERSUS {fighter2.nick_name}'
    battle_status3 = get_status_table(order["Attacker"], order["Defensor"])
    line(100, '=')
    print(f'{battle_status1:^100}')
    print(f'{battle_status2:^100}')
    print(f'{first:^100}')
    print(f'{order["Attacker"].nick_name:^50} {order["Defensor"].nick_name:^50}')
    print(f'{battle_status3:^100}')
    line(100, '=')
    if is_computer_fight(fighters):
        while True:
            line(100)
            attack(order["Attacker"], order["Defensor"], fighters)
            line(100)
            died = check_if_died(order["Defensor"])
            if died:
                line(100, '=')
                winner = f'{order["Attacker"].nick_name} WINS!!!'
                print(f'{winner:^100}')
                line(100, '=')
                if order["Attacker"].my_type() == 'Human':
                    spoils = award_xp(order["Defensor"], order["Attacker"])
                    order["Attacker"].add_xp_points(spoils)
                    order["Attacker"].rest()
                    print1 = f'Congratulations {order["Attacker"].nick_name}, you won {spoils} XP'
                    line(100, '=')
                    print(f"{print1:^100}")
                    line(100, '=')
                    battle_status1 = f'BATTLE STATUS'
                    battle_status2 = f'{fighter1.nick_name} VERSUS {fighter2.nick_name}'
                    order["Attacker"].level_up()
                    print('\n\n')
                    order["Defensor"].restart()
                else:
                    order["Defensor"].rest()
                    order["Attacker"].restart()
                break
            order = switch_attacker(order)
    else:
        while True:
            print('PLEASE DO NOT RUN THIS LOOP')
            break


def attack(attacker, defender, entts):
    debuffs = percentage(5, defender.get_df(), False) + percentage(5, defender.get_ag(), False)
    damage = abs(attacker.avg_damage - debuffs)
    defender._hp -= damage
    printable = f'{attacker.nick_name:^} deal {damage} damage in {defender.nick_name}'
    print(f"{printable:^100}")
    print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}")
    print(f'''{get_hp_bar(entts[0]):<40} X {get_hp_bar(entts[1]):50}''')


def choose_first(fighters):
    while True:
        attacker, defensor = choice(fighters), choice(fighters)
        if attacker != defensor: break;
    return {"Attacker": attacker, "Defensor": defensor}


def check_if_died(figther):
    if figther.get_hp() <= 0:
        figther.set_isalive(False)
    return True if not figther.isalive else False


def switch_attacker(order_dict):
    new_attacker = order_dict["Defensor"]
    new_defensor = order_dict["Attacker"]
    return {"Attacker": new_attacker, "Defensor": new_defensor}


def is_computer_fight(fighters):
    return (fighters[0].my_type() == 'Human' and fighters[1].my_type() == 'COM') or \
           (fighters[1].my_type() == 'Human' and fighters[0].my_type() == 'COM')


def award_xp(monster, player):
    award = abs(monster.get_level() - player.get_level()) + 50 * monster.get_level()
    return award


def line(size=15, simbol='-'):
    print(f'{simbol}' * size)


if __name__=="__main__":
    pass