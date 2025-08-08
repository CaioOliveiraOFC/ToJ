#!/usr/bin/env python3

import random
from time import sleep
from toj_source.classes import Warrior, Mage, Rogue, Monster
from toj_source.interactions import fight, screen_clear, get_key
from toj_source.map import MapOfGame
from toj_source.items import Potion, Weapon, Armor
# Importa as novas funções de save/load
from toj_source.save_manager import save_game, load_game, check_save_file


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
    # ... (código do inventário permanece o mesmo) ...
    pass


def start_game(player, start_level=1):
    dungeon_level = start_level
    while True:
        # ... (código de geração de masmorra permanece o mesmo) ...

        while True:
            screen_clear()
            print(f"Masmorra Nível {dungeon_level} | Herói: @ | Inimigos: & | Saída: X")
            print("Use 'w', 'a', 's', 'd' para mover.")
            game_map.draw_map()

            print("\n(i)nventário | (p)ara Salvar | (q) para Sair")
            move = safe_get_key(valid_keys=['w', 'a', 's', 'd', 'i', 'q', 'p'])

            if move is None or move == 'q':
                return
            elif move == 'i':
                inventory_menu(player)
            elif move == 'p': # Opção para Salvar
                save_game(player, dungeon_level)
                sleep(1.5)
            elif move in ['w', 'a', 's', 'd']:
                collided_object = game_map.move_player(move)

                if isinstance(collided_object, Monster):
                    fight(player, collided_object)
                    input("Pressione Enter para continuar sua jornada...")

                elif collided_object == 'level_complete':
                    dungeon_level += 1
                    break


def character_creation():
    # ... (código de criação de personagem permanece o mesmo) ...
    pass


def main():
    """Função principal que exibe o menu e direciona o fluxo do jogo."""
    while True:
        screen_clear()
        print("=== Bem-vindo ao The Tales of the Journey ===")
        print("\n1. Novo Jogo")
        
        # Mostra a opção de carregar apenas se existir um ficheiro de save
        if check_save_file():
            print("2. Carregar Jogo")
        
        print("3. Sair")
        print("9. MODO DE TESTE (Herói Nível 50)")

        valid_keys = ['1', '3', '9']
        if check_save_file():
            valid_keys.append('2')

        choice = safe_get_key(valid_keys=valid_keys)
        
        if choice == '1':
            player = character_creation()
            start_game(player)
        elif choice == '2' and check_save_file():
            player, dungeon_level = load_game()
            if player and dungeon_level:
                input(f"\nBem-vindo de volta, {player.get_nick_name()}! Pressione Enter para continuar.")
                start_game(player, start_level=dungeon_level)
        elif choice == '3':
            print("\nObrigado por jogar!")
            break
        elif choice == '9':
            player = Warrior("Tester")
            player.set_level(50)
            input(f"\nHerói de teste '{player.nick_name}' criado no nível 50. Pressione Enter para começar.")
            start_game(player)


if __name__ == '__main__':
    main()