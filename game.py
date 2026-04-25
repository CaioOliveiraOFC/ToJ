#!/usr/bin/env python3

import random
from time import sleep
from toj_source.classes import Warrior, Mage, Rogue, Monster, show_status
from toj_source.interactions import fight, screen_clear, get_key
from toj_source.map import MapOfGame
from toj_source.items import Potion, Weapon, Armor
from toj_source.save_manager import save_game, load_game, check_save_file
from toj_source.game_logic import generate_monsters_for_level # Importar a nova função


def safe_get_key(valid_keys=None, allow_escape=True):
    """Lê uma tecla com segurança."""
    while True:
        key = get_key()
        if not key:
            continue
        key = key.lower()
        if allow_escape and key == '\x1b':
            return None
        if valid_keys is None or key in valid_keys:
            return key


def inventory_menu(player):
    """
    Exibe o inventário do jogador, permitindo usar poções, equipar/desequipar itens.
    """
    while True:
        screen_clear()
        print("=== Inventário ===")
        print(f"Ouro: {player.coins}")

        show_status(player) # Display player stats

        print("\n--- Equipamento ---")
        for slot, item in player.equipment.items():
            if item:
                print(f"- {slot}: {item.name}")
            else:
                print(f"- {slot}: Vazio")

        print("\n--- Itens na Mochila ---")
        if not player.inventory:
            print("Sua mochila está vazia.")
        else:
            for i, item in enumerate(player.inventory):
                print(f"{i + 1}. {item.name} ({item.__class__.__name__})")

        print("\n(número do item) para selecionar | (x)sair do inventário")
        
        valid_choices = ['x'] + [str(i + 1) for i in range(len(player.inventory))]
        choice = safe_get_key(valid_keys=valid_choices)

        if choice == 'x':
            break
        elif choice and choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                screen_clear()
                print(f"=== Detalhes do Item ===")
                print(f"Nome: {selected_item.name}")
                if hasattr(selected_item, 'description'):
                    print(f"Descrição: {selected_item.description}")
                print(f"Tipo: {selected_item.__class__.__name__}")
                if isinstance(selected_item, Weapon):
                    print(f"Dano: {selected_item.damage}")
                elif isinstance(selected_item, Armor):
                    print(f"Defesa: {selected_item.defense}")
                elif isinstance(selected_item, Potion):
                    print(f"Tipo: {selected_item.potion_type}")
                    print(f"Poder de Efeito: +{selected_item.effect_value}")

                print("\n--- Ações ---")
                action_options = []
                if isinstance(selected_item, Potion):
                    action_options.append('u')
                    print("(u)sar")
                if isinstance(selected_item, (Weapon, Armor)):
                    # Check if item is already equipped
                    is_equipped = False
                    for slot, equipped_item in player.equipment.items():
                        if equipped_item == selected_item:
                            is_equipped = True
                            break
                    if is_equipped:
                        action_options.append('e') # 'e' for unequip in this context
                        print("(e)desequipar")
                    else:
                        action_options.append('e') # 'e' for equip in this context
                        print("(e)equipar")
                
                action_options.append('c')
                print("(c)ancelar")

                action_choice = safe_get_key(valid_keys=action_options, allow_escape=False)

                if action_choice == 'u':
                    if isinstance(selected_item, Potion):
                        player.use_potion(selected_item)
                        print(f"\nVocê usou {selected_item.name}.")
                        input("Pressione Enter para continuar...")
                    else:
                        print("\nVocê só pode usar poções.")
                        input("Pressione Enter para continuar...")
                elif action_choice == 'e':
                    if isinstance(selected_item, (Weapon, Armor)):
                        is_equipped = False
                        for slot, equipped_item in player.equipment.items():
                            if equipped_item == selected_item:
                                player.unequip(slot)
                                print(f"\nVocê desequipou {selected_item.name}.")
                                is_equipped = True
                                break
                        if not is_equipped:
                            player.equip(selected_item)
                            print(f"\nVocê equipou {selected_item.name}.")
                        input("Pressione Enter para continuar...")
                    else:
                        print("\nVocê só pode equipar armas ou armaduras.")
                        input("Pressione Enter para continuar...")
                elif action_choice == 'c': 
                    continue
            else:
                print("\nEscolha de item inválida.")
                input("Pressione Enter para continuar...")
        else:
            print("\nOpção inválida.")
            input("Pressione Enter para continuar...")


def start_game(player, start_level=1):
    dungeon_level = start_level
    while True:
        MAP_HEIGHT = 12 + (dungeon_level // 5) * 2
        MAP_WIDTH = 25 + (dungeon_level // 5) * 4
        
        game_map = MapOfGame(height=MAP_HEIGHT, width=MAP_WIDTH)
        # Reduzindo de 0.2 para 0.05 para deixar o mapa absurdamente mais aberto
        game_map.generate_map(percent_of_walls=0.05 + min(dungeon_level * 0.01, 0.15))

        game_map.place_player()
        game_map.place_exit()

        # Substituindo a geração de monstros placeholder pela função de game_logic
        monsters_to_place = generate_monsters_for_level(dungeon_level)
        for monster in monsters_to_place:
            game_map.place_enemy(monster)

        while True:
            screen_clear()
            print(f"Masmorra Nível {dungeon_level} | Herói: @ | Inimigos: & | Saída: X | HP: {player.get_hp()}/{player.base_hp} | MP: {player.get_mp()}/{player.base_mp}")
            print("Use 'w', 'a', 's', 'd' para mover.")
            game_map.draw_map()

            print("\n(i)nventário | (p)ara Salvar | (q) para Sair")
            move = safe_get_key(valid_keys=['w', 'a', 's', 'd', 'i', 'q', 'p'])

            if move is None or move == 'q':
                save_game(player, dungeon_level, game_map.get_map_state()) 
                print("Jogo salvo automaticamente ao sair.")
                sleep(1.5)
                return
            elif move == 'i':
                inventory_menu(player)
            elif move == 'p':
                save_game(player, dungeon_level, game_map.get_map_state()) 
                print("Jogo salvo!")
                sleep(1.5)
            elif move in ['w', 'a', 's', 'd']:
                collided_object = game_map.move_player(move)

                if isinstance(collided_object, Monster):
                    fight(player, collided_object)
                    if not player.get_isalive():
                        print("\nVocê foi derrotado! Fim de jogo.")
                        input("Pressione Enter para voltar ao menu principal...")
                        return 
                    player.add_xp_points(collided_object.level * 10) 
                    player.level_up() 
                    input("Pressione Enter para continuar sua jornada...")

                elif collided_object == 'level_complete':
                    print(f"Você completou a Masmorra Nível {dungeon_level}!")
                    input("Pressione Enter para avançar para o próximo nível...")
                    dungeon_level += 1
                    break 


def character_creation():
    from toj_source.game_logic import create_player 
    return create_player()


def main():
    """Função principal que exibe o menu e direciona o fluxo do jogo."""
    while True:
        screen_clear()
        print("=== Bem-vindo ao The Tales of the Journey ===")
        print("\n1. Novo Jogo")

        if check_save_file():
            print("2. Carregar Jogo")

        print("3. Sair")
        print("8. MODO DE AUTO-TESTE (BOT)")
        print("9. MODO DE TESTE (Herói Nível 50)")

        valid_keys = ['1', '3', '8', '9']
        if check_save_file():
            valid_keys.append('2')

        choice = safe_get_key(valid_keys=valid_keys)

        if choice == '1':
            player = character_creation()
            start_game(player)
        elif choice == '2' and check_save_file():
            player, dungeon_level, map_state = load_game()
            if player and dungeon_level and map_state:
                input(f"\nBem-vindo de volta, {player.get_nick_name()}! Pressione Enter para continuar.")
                game_map = MapOfGame(height=map_state['height'], width=map_state['width'])
                game_map.grid = map_state['grid']
                game_map.player_pos = map_state['player_pos']
                game_map.exit_pos = map_state['exit_pos']
                game_map.enemies_pos = {tuple(pos): Monster(m['nick_name'], m['level']) for pos, m in map_state['enemies_pos'].items()} 
                start_game(player, start_level=dungeon_level)
            else:
                print("Erro ao carregar o jogo.")
                input("Pressione Enter para continuar...")
        elif choice == '3':
            print("\nObrigado por jogar!")
            break
        elif choice == '8':
            player = Warrior("TestBot")
            from toj_source.auto_test import AutoTester
            tester = AutoTester()
            tester.run_test(player)
        elif choice == '9':
            player = Warrior("Tester")
            player.set_level(50)
            from toj_source.items import Potion, Weapon, Armor 
            player.add_item_to_inventory(Potion("Super Poção de Cura", "Poção forte", 50, "Health"))
            player.add_item_to_inventory(Potion("Mega Poção de Mana", "Mana forte", 30, "Mana"))
            test_sword = Weapon("Espada do Teste", "Arma apelona", 15)
            player.add_item_to_inventory(test_sword)
            player.equip(test_sword)
            test_armor = Armor("Armadura do Teste", "Armadura grossa", 10, "Body")
            player.add_item_to_inventory(test_armor)
            player.equip(test_armor)


            input(f"\nHerói de teste '{player.nick_name}' criado no nível 50. Pressione Enter para começar.")
            start_game(player)


if __name__ == '__main__':
    main()
