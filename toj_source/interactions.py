# This module is where the interactions happens
# Any interaction beetween the classes is done here

from random import choice, randrange
from math_operations import percentage
from classes import get_hp_bar, compare
from time import sleep
from os import system

def fight(fighter1, fighter2):
    # The fight is done here
    # it creates a array of two fighters
    fighters = [fighter1, fighter2]
    # the order is made by the funciton choose_first()
    order = choose_first(fighters)
    line(100, '=')
    print(f'BATTLE STATUS'.center(100))
    print(f'{fighter1.nick_name} VERSUS {fighter2.nick_name}'.center(100))
    print(f'{order["Attacker"].nick_name} attacks first'.center(100))
    line(100, '=')
    
    compare(fighter1, fighter2)
    line(100, '=')
    print(f"{order['Attacker'].nick_name:^50} {order['Defensor'].nick_name:^50}".center(100))
    print(f'{get_hp_bar(order["Attacker"]):<40} X {get_hp_bar(order["Defensor"]):50}'.center(100))
    
    if is_computer_fight(fighters):
        # Check if its a computer agains player fight
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
                    # If the winner is a human player then the xp is awarded to him and the monster is killed
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
                    # Otherwise he just lose the fight and reset his stats
                    order["Defensor"].rest()
                    order["Defensor"].reset_kill_streak()
                    order["Attacker"].restart()
                break
            order = switch_attacker(order)
    else:
        # if it's a PVP Jfight
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
    # TODO: I NEED TO FIX THIS PART
    # The attack is done here
    # TODO: I NEED TO FIX WHOLE FUNCTION
    debuffs = percentage(30, defender.get_df(), False)
     # first it calculates the amount of damage that the defender can take
    if debuffs > attacker.get_avg_damage():
        # To be fair, if the defender has a high defense it can take damage
        # than the attacker only deals the max damage of his average damage
        # Does not use debuffs calculation here beacuse the defender does not need
        damage = attacker.get_avg_damage()
    else:
        damage = attacker.get_avg_damage() - debuffs
    critical_value = percentage(98, damage, False)
    chosed_for_debf = randrange(90, 101)
    damage = percentage(chosed_for_debf, damage, False)
    miss = defender.get_ag() - percentage(5, attacker.get_ag(), False)
    chosed_for_hit = randrange(1, 99)
    if chosed_for_hit >= miss:
        defender.reduce_hp(damage)
        critical = ''
        if damage >= critical_value:
            critical = ' a critical damage!!'
        print(f'{attacker.nick_name:^} dealt {damage} damage in {defender.nick_name}{critical}'.center(100))
        print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}".center(100))
        print(f'{get_hp_bar(entts[0]):<40} X {get_hp_bar(entts[1]):50}'.center(100))
        
    else:
        print(f'{attacker.nick_name} has missed the attack'.center(100).center(100))
        print(f"{entts[0].nick_name:^50} {entts[1].nick_name:^50}".center(100))
        print(f'{get_hp_bar(entts[0]):<40} X {get_hp_bar(entts[1]):50}'.center(100))
        


def choose_first(fighters):
    # This function chooses the first attacker
    while True:
        attacker, defensor = choice(fighters), choice(fighters)
        if attacker != defensor: break;
    return {"Attacker": attacker, "Defensor": defensor}


def check_if_died(figther):
    # This function checks if the fighter is dead after the attack
    if figther.get_hp() <= 0:
        figther.set_isalive(False)
    return True if not figther.isalive else False


def switch_attacker(order_dict):
    # This function switches the attacker and the defensor
    new_attacker = order_dict["Defensor"]
    new_defensor = order_dict["Attacker"]
    return {"Attacker": new_attacker, "Defensor": new_defensor}


def is_computer_fight(fighters):
    # This function checks if the fight is between a computer and a player
    return (fighters[0].my_type() == 'Human' and fighters[1].my_type() == 'COM') or \
           (fighters[1].my_type() == 'Human' and fighters[0].my_type() == 'COM')


def award_xp(monster):
    # This function awards the xp to the player
    award = (30 * monster.get_level())
    if monster.get_level() >= 10:
        award += percentage(10, award, False)
    elif monster.get_level() >= 20:
        award += percentage(20, award, False)
    elif monster.get_level() >= 30:
        award += percentage(30, award, False)
    else:
        award += percentage(40, award, False)
    choosed = randrange(90, 101)
    award = percentage(choosed, award, False)
    return award


def line(size=15, simbol='-'):
    # This function prints a line
    print(f'{simbol}' * size)


def menu(list_of_itens, msg):
    # This function prints a menu
    print(f'{msg:}')
    c = 1
    for item in list_of_itens:
        print(f'{c}-{item}')
        c += 1

def screen_clear():
    # This function clears the screen
        _ = system('clear')

if __name__ == '__main__':
    pass
