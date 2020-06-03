from random import choice

def fight(fighter1,  fighter2):
    fighters = [fighter1, fighter2]
    order = choose_first(fighters)
    print(f'{order["Attacker"].nick_name} attacks first')
    while True:
        attack(order["Attacker"], order["Defensor"])
        defensor_dead = check_if_died(order['Defensor'])
        if defensor_dead:
            print(f'The {order["Attacker"].nick_name} WIN!!!')
            break
        order = switch_attacker(order)

def attack(attacker, defender):
    damage = abs((attacker._HP * 10 // 100) + (attacker._MG * 10 // 100) - (defender._DF * 5 // 100))
    defender._HP -= damage
    print(f'{attacker.nick_name} deal {damage} in {defender.nick_name}')
    print(f"{attacker.nick_name:^50} {defender.nick_name:^50}")
    print(f'''{attacker.get_hp_bar():<40} X {defender.get_hp_bar():50}''')

def choose_first(fighters):
    while True:
        attacker, defensor = choice(fighters), choice(fighters)
        if attacker != defensor: break;
    return {"Attacker": attacker, "Defensor": defensor}

def check_if_died(figther):
    if figther._HP <= 0: figther.set_isalive(False);
    return True if not figther.isalive else False

def switch_attacker(order_dict):
    new_attacker = order_dict["Defensor"]
    new_defensor = order_dict["Attacker"]
    return {"Attacker": new_attacker, "Defensor": new_defensor}
