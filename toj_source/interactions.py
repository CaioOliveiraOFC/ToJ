import os
import platform
from random import choice, randrange
from .math_operations import percentage
from .classes import get_hp_bar, compare
from time import sleep

def screen_clear():
    """
    Limpa a tela do terminal de forma compatível com Windows, Linux e macOS.
    """
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def fight(fighter1, fighter2):
    fighters = [fighter1, fighter2]
    order = choose_first(fighters)
    line(100, '=')
    print('STATUS DA BATALHA'.center(100))
    print(f'{fighter1.nick_name} VERSUS {fighter2.nick_name}'.center(100))
    print(f'{order["Attacker"].nick_name} ataca primeiro'.center(100))
    line(100, '=')
    
    compare(fighter1, fighter2)
    line(100, '=')
    
    is_pvp = not is_computer_fight(fighters)

    while True:
        print(f"{order['Attacker'].nick_name:^50} {order['Defensor'].nick_name:^50}".center(100))
        print(f'{get_hp_bar(order["Attacker"]):<50} X {get_hp_bar(order["Defensor"]):>50}'.center(100))
        input("Pressione Enter para o próximo turno...")
        line(100)
        attack(order["Attacker"], order["Defensor"], fighters)
        line(100)
        
        if check_if_died(order["Defensor"]):
            line(100, '=')
            winner = f'{order["Attacker"].nick_name} VENCEU!!!'
            print(f'{winner:^100}')
            line(100, '=')
            
            order["Attacker"].win()
            order["Attacker"].add_kill_streak()
            order["Attacker"].rest()
            
            if not is_pvp and order["Attacker"].my_type() == 'Human':
                spoils = award_xp(order["Defensor"])
                order["Attacker"].add_xp_points(spoils)
                print1 = f'Parabéns {order["Attacker"].nick_name}, você ganhou {spoils} XP'
                print2 = f'{order["Attacker"].get_level_bar()}'
                line(100, '=')
                print(f"{print1:^100}")
                print(f'{print2:^100}')
                line(100, '=')
                print(f'Você tem {order["Attacker"].get_xp_points()} pontos de xp'.center(100))
                order["Attacker"].level_up(show=True)
            
            order["Defensor"].rest()
            order["Defensor"].reset_kill_streak()
            break
            
        order = switch_attacker(order)

def attack(attacker, defender, entts):
    # Lógica de ataque simplificada e mais clara
    # Chance de acerto baseada na agilidade
    hit_chance = 75 + (attacker.get_ag() - defender.get_ag())
    if randrange(1, 101) > hit_chance:
        print(f'{attacker.nick_name} errou o ataque!'.center(100))
        return

    # Cálculo do dano
    base_damage = attacker.get_avg_damage()
    defense_reduction = percentage(50, defender.get_df(), False) # Defesa reduz 50% do seu valor em dano
    damage = max(1, base_damage - defense_reduction) # Garante pelo menos 1 de dano

    # Chance de crítico
    critical_chance = 5 + (attacker.get_ag() // 10) # 5% de base + bônus de agilidade
    is_critical = randrange(1, 101) <= critical_chance
    if is_critical:
        damage *= 2
        
    defender.reduce_hp(damage)
    
    critical_msg = ' um ataque CRÍTICO!!' if is_critical else ''
    print(f'{attacker.nick_name} causou {damage} de dano em {defender.nick_name}{critical_msg}'.center(100))

def choose_first(fighters):
    attacker = choice(fighters)
    defensor = fighters[1] if fighters[0] == attacker else fighters[0]
    return {"Attacker": attacker, "Defensor": defensor}

def check_if_died(figther):
    if figther.get_hp() <= 0:
        figther.set_isalive(False)
    return not figther.get_isalive()

def switch_attacker(order_dict):
    return {"Attacker": order_dict["Defensor"], "Defensor": order_dict["Attacker"]}

def is_computer_fight(fighters):
    return 'COM' in [f.my_type() for f in fighters]

def award_xp(monster):
    # Lógica de XP corrigida
    award = (30 * monster.get_level())
    if monster.get_level() >= 50:
        award += percentage(50, award, False)
    elif monster.get_level() >= 30:
        award += percentage(30, award, False)
    elif monster.get_level() >= 20:
        award += percentage(20, award, False)
    elif monster.get_level() >= 10:
        award += percentage(10, award, False)
    
    choosed = randrange(90, 101)
    return percentage(choosed, award, False)

def line(size=15, simbol='-'):
    print(f'{simbol}' * size)

def menu(list_of_itens, msg):
    print(f'{msg}')
    for i, item in enumerate(list_of_itens, 1):
        print(f'{i}-{item}')
