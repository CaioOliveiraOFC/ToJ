from random import choice, randrange
from toj_source.math_operations import percentage
from toj_source.classes import get_hp_bar, compare

def fight(fighter1, fighter2):
    fighters = [fighter1, fighter2]
    order = choose_first(fighters)
    first = f'{order["Attacker"].nick_name} attacks first'
    battle_status1 = f'BATTLE STATUS'
    battle_status2 = f'{fighter1.nick_name} VERSUS {fighter2.nick_name}'
    line(100, '=')
    print(f'{battle_status1:^100}')
    print(f'{battle_status2:^100}')
    print(f'{first:^100}')
    line(100, '=')
    compare(fighter1, fighter2)
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
                    order["Attacker"].win()
                    spoils = award_xp(order["Defensor"])
                    order["Attacker"].add_xp_points(spoils)
                    order["Attacker"].rest()
                    print1 = f'Congratulations {order["Attacker"].nick_name}, you won {spoils} XP'
                    print2 = f'{order["Attacker"].get_level_bar()}'
                    line(100, '=')
                    print(f"{print1:^100}")
                    print(f'{print2:^100}')
                    line(100, '=')
                    print(f'You have {order["Attacker"].get_xp_points()} xp points'.center(100))
                    order["Attacker"].level_up()
                    order["Defensor"].restart()
                    order["Attacker"].add_kill_streak()
                else:
                    order["Defensor"].rest()
                    order["Defensor"].reset_kill_streak()
                    order["Attacker"].restart()
                break
            order = switch_attacker(order)
    else:
        while True:
            line(100)
            attack(order["Attacker"], order["Defensor"], fighters)
            line(100)
            died = check_if_died(order["Defensor"])
            if died:
                line(100, '=')
                winner = f'{order["Attacker"].nick_name} WINS!!!'
                order["Attacker"].win()
                print(f'{winner:^100}')
                line(100, '=')
                order["Defensor"].rest()
                order["Defensor"].reset_kill_streak()
                order["Attacker"].rest()
                order["Attacker"].add_kill_streak()
                break
            order = switch_attacker(order)


def attack(attacker, defender, entts):
    debuffs = percentage(30, defender.get_df(), False)
    if debuffs > attacker.get_avg_damage():
        damage = attacker.get_avg_damage()
    else:
        damage = attacker.get_avg_damage() - debuffs
    critical_value = percentage(96, damage, False)
    chosed_for_debf = randrange(90, 101)
    damage = percentage(chosed_for_debf, damage, False)
    miss = defender.get_ag() - percentage(5, attacker.get_ag(), False)
    chosed_for_hit = randrange(1, 99)
    if chosed_for_hit >= miss:
        defender.reduce_hp(damage)
        critical = ''
        if damage >= critical_value:
            critical = ' a critical damage!!'
        print(f'{attacker.nick_name:^} deal {damage} damage in {defender.nick_name}{critical}'.center(100))
        print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}".center(100))
        print(f'{get_hp_bar(entts[0]):<40} X {get_hp_bar(entts[1]):50}'.center(100))
    else:
        print(f'{attacker.nick_name} has missed the attack'.center(100).center(100))
        print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}".center(100))
        print(f'{get_hp_bar(entts[0]):<40} X {get_hp_bar(entts[1]):50}'.center(100))


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


def award_xp(monster):
    award = (30 * monster.get_level())
    if monster.get_level() >= 10:
        award += percentage(10, award, False)
    elif monster.get_level() >= 20:
        award += percentage(15, award, False)
    elif monster.get_level() >= 30:
        award += percentage(20, award, False)
    else:
        award += percentage(25, award, False)
    choosed = randrange(90, 101)
    award = percentage(choosed, award, False)
    return award


def line(size=15, simbol='-'):
    print(f'{simbol}' * size)


if __name__ == '__main__':
    pass