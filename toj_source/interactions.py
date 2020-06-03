from random import choice
from time import sleep
from os import system, name


def fight(fighter1, fighter2):
    fighters = [fighter1, fighter2]
    order = choose_first(fighters)
    first = f'{order["Attacker"].nick_name} attacks first'
    print(f'{first:^100}')
    while True:
        #sleep(3)
        line(100)
        attack(order["Attacker"], order["Defensor"], fighters)
        defensor_dead = check_if_died(order['Defensor'])
        line(100)
        if defensor_dead:
            line(100)
            winner = f'The {order["Attacker"].nick_name} WIN!!!'
            print(f'{winner:^100}')
            line(100)
            break
        order = switch_attacker(order)


def attack(attacker, defender, entts):
    damage = abs((attacker._ST * 10 // 100) + (attacker._MG * 10 // 100) - (defender._DF * 5 // 100))
    defender._HP -= damage
    printable = f'{attacker.nick_name:^} deal {damage} damage in {defender.nick_name}'
    print(f"{printable:^100}")
    print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}")
    print(f'''{attacker.get_hp_bar():<40} X {defender.get_hp_bar():50}''')


def choose_first(fighters):
    while True:
        attacker, defensor = choice(fighters), choice(fighters)
        if attacker != defensor: break;
    return {"Attacker": attacker, "Defensor": defensor}


def check_if_died(figther):
    if figther._HP <= 0:
        figther.set_isalive(False)
    return True if not figther.isalive else False


def switch_attacker(order_dict):
    new_attacker = order_dict["Defensor"]
    new_defensor = order_dict["Attacker"]
    return {"Attacker": new_attacker, "Defensor": new_defensor}


def line(size=15):
    print('-' * size)


def clear_screen():
    system('cls' if name == 'nt' else 'clear')
