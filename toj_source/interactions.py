import os
import platform
from random import choice, randrange
from time import sleep
from .math_operations import percentage
from .classes import get_hp_bar
from .items import get_loot, Potion

def get_key():
    """
    Lê um único pressionamento de tecla do usuário, ignorando teclas especiais (como setas)
    que causam erros no Windows.
    """
    try:
        # Para Windows
        import msvcrt
        while True:
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                msvcrt.getch()
                continue
            return key.decode('utf-8')
    except ImportError:
        # Para Unix-like (Linux, macOS)
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def screen_clear():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def line(size=50, simbol='-'):
    print(simbol * size)

def display_battle_ui(player, monster):
    screen_clear()
    print("=== BATALHA ===")
    print(f"{player.get_nick_name():<20}   VS   {monster.nick_name:>20}")
    player_hp_bar = get_hp_bar(player)
    monster_hp_bar = get_hp_bar(monster)
    print(f"{player_hp_bar:<23}  {monster_hp_bar:>23}")
    print(f"MP: {player.get_mp()}/{player.base_mp:<18}")
    line()

def perform_attack(attacker, defender, base_damage, skill_name=""):
    """Executa a lógica de um único ataque e imprime o resultado."""
    crit_chance = 25 if hasattr(attacker, 'get_classname') and attacker.get_classname() == 'Rogue' and skill_name == "Ataque Furtivo" else 10
    
    hit_chance = 85 + (attacker.get_ag() - defender.get_ag())
    if randrange(1, 101) > hit_chance:
        print(f"{attacker.get_nick_name()} errou o ataque!")
        sleep(1.5)
        return

    defense_reduction = defender.get_df() // 2
    damage = max(1, base_damage - defense_reduction)
    
    is_critical = randrange(1, 101) <= crit_chance
    if is_critical:
        damage *= 2

    defender.reduce_hp(damage)
    
    critical_msg = " ATAQUE CRÍTICO!" if is_critical else ""
    print(f"{attacker.get_nick_name()} causou {damage} de dano em {defender.get_nick_name()}.{critical_msg}")
    sleep(1.5)

def use_skill(caster, target, skill):
    """Processa o uso de uma habilidade e seus efeitos."""
    print(f"{caster.get_nick_name()} usa {skill.name}!")
    sleep(1)
    caster.reduce_mp(skill.mana_cost)

    if skill.effect_type == 'damage':
        perform_attack(caster, target, skill.value, skill.name)
    
    elif skill.effect_type == 'heal':
        heal_amount = skill.value
        caster._hp = min(caster.base_hp, caster.get_hp() + heal_amount)
        print(f"{caster.get_nick_name()} recupera {heal_amount} de HP!")
        sleep(1.5)

    elif skill.effect_type == 'status':
        if randrange(1, 101) <= skill.chance:
            target.active_effects[skill.value] = {'duration': skill.duration}
            print(f"{target.get_nick_name()} está sob o efeito de {skill.value}!")
        else:
            print("O efeito falhou!")
        sleep(1.5)

    elif skill.effect_type == 'buff':
        caster.active_buffs[skill.name] = {'value': skill.value, 'duration': skill.duration}
        print(f"{caster.get_nick_name()} recebe o buff {skill.name}!")
        sleep(1.5)

def handle_turn_effects(entity):
    """Aplica e gere os efeitos de status no início do turno."""
    effects_to_remove = []
    buffs_to_remove = []
    skipped_turn = False

    for effect, data in list(entity.active_effects.items()):
        if effect == 'poison':
            poison_damage = 5
            entity.reduce_hp(poison_damage)
            print(f"{entity.get_nick_name()} sofre {poison_damage} de dano de veneno.")
        
        if effect == 'frozen':
            print(f"{entity.get_nick_name()} está congelado e não pode se mover!")
            skipped_turn = True

        data['duration'] -= 1
        if data['duration'] <= 0:
            effects_to_remove.append(effect)
    
    for buff, data in list(entity.active_buffs.items()):
        data['duration'] -= 1
        if data['duration'] <= 0:
            buffs_to_remove.append(buff)

    for effect in effects_to_remove:
        del entity.active_effects[effect]
        print(f"O efeito {effect} em {entity.get_nick_name()} passou.")
    for buff in buffs_to_remove:
        del entity.active_buffs[buff]
        print(f"O buff {buff} em {entity.get_nick_name()} acabou.")
    
    if any([effects_to_remove, buffs_to_remove, 'poison' in entity.active_effects]):
        sleep(1.5)
        
    return skipped_turn

def compare_opponents(ennt1, ennt2):
    """ Esta função imprime uma comparação lado a lado dos status de duas entidades. """
    line_width = 50
    print('VS'.center(line_width))
    print(f'{ennt1.get_nick_name():^24} | {ennt2.get_nick_name():^24}'.center(line_width))
    print('-'*line_width)
    print(f'Nível: {ennt1.get_level():<18} | Nível: {ennt2.level:<18}')
    print(f'HP: {ennt1.get_hp()}/{ennt1.base_hp:<20} | HP: {ennt2.get_hp()}/{ennt2.base_hp:<20}')
    print(f'MP: {ennt1.get_mp()}/{ennt1.base_mp:<20} | MP: {ennt2.get_mp()}/{ennt2.base_mp:<20}')
    print(f'Força: {ennt1.get_st():<16} | Força: {ennt2.get_st():<16}')
    print(f'Agilidade: {ennt1.get_ag():<13} | Agilidade: {ennt2.get_ag():<13}')
    print(f'Magia: {ennt1.get_mg():<17} | Magia: {ennt2.get_mg():<17}')
    print(f'Defesa: {ennt1.get_df():<16} | Defesa: {ennt2.get_df():<16}')
    print('-'*line_width)

def fight(player, monster):
    player.rest()
    
    screen_clear()
    print("--- Início da Batalha ---".center(50))
    compare_opponents(player, monster)
    input("Pressione Enter para começar a batalha...")
    
    turn_order = [player, monster]
    if player.get_ag() < monster.get_ag():
        turn_order = [monster, player]

    attacker_index = 0
    while player.get_isalive() and monster.isalive:
        attacker = turn_order[attacker_index]
        defender = turn_order[(attacker_index + 1) % 2]
        
        display_battle_ui(player, monster)
        print(f"É a vez de {attacker.get_nick_name()}.")
        sleep(1)

        if handle_turn_effects(attacker):
            attacker_index = (attacker_index + 1) % 2
            continue

        if attacker.my_type() == 'Human':
            action_taken = False
            while not action_taken:
                display_battle_ui(player, monster)
                print("Escolha sua ação:\n1. Ataque Normal\n2. Habilidades\n3. Usar Item\n4. Tentar Fugir")
                
                choice = safe_get_key(valid_keys=['1', '2', '3', '4'])

                if choice == '1':
                    perform_attack(player, monster, player.get_avg_damage())
                    action_taken = True
                
                elif choice == '2':
                    if not player.skills:
                        print("Você não tem habilidades para usar!")
                        sleep(1)
                        continue
                    
                    while True:
                        display_battle_ui(player, monster)
                        print("Escolha uma habilidade:")
                        for key, skill in player.skills.items():
                            print(f"{key}. {skill.name} (Custo: {skill.mana_cost} MP)")
                        print("0. Voltar")
                        
                        skill_keys = [str(k) for k in player.skills.keys()] + ['0']
                        skill_choice = safe_get_key(skill_keys)

                        if skill_choice == '0': break
                        
                        if skill_choice and skill_choice.isdigit() and int(skill_choice) in player.skills:
                            chosen_skill = player.skills[int(skill_choice)]
                            if player.get_mp() >= chosen_skill.mana_cost:
                                use_skill(player, monster, chosen_skill)
                                action_taken = True
                                break
                            else:
                                print("Mana insuficiente!")
                                sleep(1)
                
                elif choice == '3':
                    potions = [item for item in player.inventory if isinstance(item, Potion)]
                    if not potions:
                        print("Você não tem poções para usar!")
                        sleep(1)
                        continue
                    
                    while True:
                        display_battle_ui(player, monster)
                        print("Escolha uma poção para usar:")
                        for i, potion in enumerate(potions, 1):
                            print(f"{i}. {potion.name} - {potion.description}")
                        print("0. Voltar")

                        potion_keys = [str(i) for i in range(1, len(potions) + 1)] + ['0']
                        potion_choice = safe_get_key(potion_keys)

                        if potion_choice == '0': break

                        if potion_choice and potion_choice.isdigit():
                            player.use_potion(potions[int(potion_choice) - 1])
                            action_taken = True
                            sleep(1.5)
                            break
                
                elif choice == '4':
                    if randrange(0, 2) == 0:
                        print("Você conseguiu fugir da batalha!")
                        sleep(2)
                        player.rest()
                        return
                    else:
                        print("A fuga falhou!")
                        sleep(1.5)
                        action_taken = True
        else:
            perform_attack(monster, player, monster.get_avg_damage())

        if defender.get_hp() <= 0:
            defender.set_isalive(False)
            break
            
        attacker_index = (attacker_index + 1) % 2

    xp_base_reward = 50 * monster.level
    if not player.get_isalive():
        print("Você foi derrotado...")
        pity_xp = xp_base_reward // 10
        player.add_xp_points(pity_xp)
    else:
        print(f"Você derrotou {monster.nick_name}!")
        player.add_xp_points(xp_base_reward)
        dropped_item = get_loot()
        if dropped_item:
            player.add_item_to_inventory(dropped_item)
    player.level_up(show=True)
    player.rest()

def safe_get_key(valid_keys=None, allow_escape=True):
    """Função auxiliar para a função fight, para não precisar importá-la de game.py"""
    while True:
        key = get_key()
        if not key:
            continue
        key = key.lower()
        if allow_escape and key == '\x1b':
            return None
        if valid_keys is None or key in valid_keys:
            return key
