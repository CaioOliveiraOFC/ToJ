import os
import platform
from random import choice, randrange
from time import sleep
from .math_operations import percentage
# CORREÇÃO: A função 'compare' foi movida para este ficheiro, então não é mais importada.
from .classes import get_hp_bar

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
            # Teclas especiais no Windows (como setas) enviam dois bytes.
            # O primeiro é b'\xe0' ou b'\x00'. Nós os ignoramos.
            if key in [b'\xe0', b'\x00']:
                msvcrt.getch() # Lê e descarta o segundo byte da tecla especial.
                continue # Pede a próxima tecla, ignorando a especial.
            # Se a tecla for válida, descodifica e retorna.
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

def perform_attack(attacker, defender, base_damage):
    hit_chance = 85 + (attacker.get_ag() - defender.get_ag())
    if randrange(1, 101) > hit_chance:
        print(f"{attacker.get_nick_name()} errou o ataque!")
        sleep(1.5)
        return

    defense_reduction = defender.get_df() // 2
    damage = max(1, base_damage - defense_reduction)
    
    is_critical = randrange(1, 101) <= 10
    if is_critical:
        damage *= 2

    defender.reduce_hp(damage)
    
    critical_msg = " ATAQUE CRÍTICO!" if is_critical else ""
    print(f"{attacker.get_nick_name()} causou {damage} de dano em {defender.nick_name}.{critical_msg}")
    sleep(1.5)

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
    """Sistema de luta baseado em turnos com recompensas detalhadas."""
    player.rest()
    
    screen_clear()
    print("--- Início da Batalha ---".center(50))
    # CORREÇÃO: Chama a função 'compare_opponents' que agora está neste ficheiro.
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
        print(f"É a vez de {attacker.get_nick_name()} atacar.")
        sleep(1)

        if attacker.my_type() == 'Human':
            action_taken = False
            while not action_taken:
                display_battle_ui(player, monster)
                print("Escolha sua ação:\n1. Ataque Normal\n2. Habilidades\n3. Tentar Fugir")
                print("> ", end="", flush=True)
                choice = get_key()
                print(choice)

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
                        
                        print("> ", end="", flush=True)
                        skill_choice = get_key()
                        print(skill_choice)

                        if skill_choice == '0': break
                        if skill_choice.isdigit() and int(skill_choice) in player.skills:
                            chosen_skill = player.skills[int(skill_choice)]
                            if player.get_mp() >= chosen_skill.mana_cost:
                                player.reduce_mp(chosen_skill.mana_cost)
                                perform_attack(player, monster, chosen_skill.damage)
                                action_taken = True
                                break
                            else:
                                print("Mana insuficiente!")
                                sleep(1)
                        else:
                            print("Habilidade inválida.")
                            sleep(1)
                elif choice == '3':
                    if randrange(0, 2) == 0:
                        print("Você conseguiu fugir da batalha!")
                        sleep(2)
                        player.rest()
                        return
                    else:
                        print("A fuga falhou!")
                        action_taken = True
                else:
                    print("Ação inválida.")
                    sleep(1)
        else:
            perform_attack(monster, player, monster.get_avg_damage())

        if defender.get_hp() <= 0:
            defender.set_isalive(False)
            break
            
        attacker_index = (attacker_index + 1) % 2

    # --- Fim da Batalha ---
    display_battle_ui(player, monster)
    xp_base_reward = 50 * monster.level

    if not player.get_isalive():
        print("Você foi derrotado...")
        pity_xp = xp_base_reward // 10
        print(f"Você ganhou {pity_xp} de XP de consolação.")
        player.add_xp_points(pity_xp)
    else:
        print(f"Você derrotou {monster.nick_name}!")
        print(f"Você ganhou {xp_base_reward} de XP.")
        player.add_xp_points(xp_base_reward)
        
    player.level_up(show=True)
    player.rest()
