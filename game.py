#!/usr/bin/env python3

import random
from time import sleep
from toj_source.classes import Warrior, Mage, Rogue, Monster
# Importa a função get_key do novo local
from toj_source.interactions import fight, screen_clear, get_key
from toj_source.map import MapOfGame

def character_creation():
    """
    Lida com o processo de criação do personagem, incluindo nome e classe.
    """
    screen_clear()
    print("--- Criação de Personagem ---")
    
    while True:
        player_name = input("Digite o nome do seu herói: ")
        if player_name.strip():
            break
        print("O nome não pode estar em branco.")

    while True:
        screen_clear()
        print(f"Nome do Herói: {player_name}")
        print("\nEscolha a sua classe:")
        print("1. Guerreiro - Forte e resistente.")
        print("2. Mago - Mestre das artes arcanas.")
        print("3. Ladino - Ágil e especialista em ataques rápidos.")
        
        print("> ", end="", flush=True)
        choice = get_key()
        print(choice) # Mostra a tecla pressionada para o utilizador

        if choice == '1':
            return Warrior(player_name)
        elif choice == '2':
            return Mage(player_name)
        elif choice == '3':
            return Rogue(player_name)
        else:
            print("Opção inválida.")
            sleep(1)

def start_game(player):
    """
    Inicia o loop principal do jogo com o personagem criado.
    """
    dungeon_level = 1
    while True:
        screen_clear()
        print(f"--- Masmorra Nível {dungeon_level} ---")
        print(f"{player.get_nick_name()} ({player.get_classname()}) entra em uma nova área...")
        input("Pressione Enter para continuar...")

        game_map = MapOfGame(height=15, width=30)
        game_map.generate_map(percent_of_walls=0.15)
        game_map.place_player()
        game_map.place_exit()

        enemies_to_create = 2 + dungeon_level
        for _ in range(enemies_to_create):
            monster_level = random.randint(dungeon_level, dungeon_level + 2)
            monster_name = random.choice(["Lobo", "Goblin", "Orc", "Esqueleto"])
            game_map.place_enemy(Monster(f"{monster_name} Nv.{monster_level}", monster_level))

        while True:
            screen_clear()
            print(f"Masmorra Nível {dungeon_level} | Herói: @ (Verde) | Inimigos: & (Vermelho) | Saída: X (Amarelo)")
            print("Use 'w', 'a', 's', 'd' para se mover. Encontre a saída 'X' para avançar.")
            game_map.draw_map()

            print("\nMova-se (w/a/s/d) ou 'q' para sair: ", end="", flush=True)
            move = get_key().lower()

            if move == 'q':
                print("\nVocê desistiu da sua jornada...")
                return

            if move in ['w', 'a', 's', 'd']:
                collided_object = game_map.move_player(move)
                
                if isinstance(collided_object, Monster):
                    screen_clear()
                    print(f"Você encontrou um {collided_object.nick_name} selvagem!")
                    input("Pressione Enter para começar a batalha...")
                    fight(player, collided_object)
                    input("Pressione Enter para continuar sua jornada...")
                
                elif collided_object == 'level_complete':
                    print("\nVocê encontrou a saída! Preparando para o próximo nível...")
                    dungeon_level += 1
                    input("Pressione Enter para descer mais fundo na masmorra.1..")
                    break
            else:
                pass

def main():
    """
    Função principal que exibe o menu e direciona o fluxo do jogo.
    """
    while True:
        screen_clear()
        print("=== Bem-vindo ao The Tales of the Journey ===")
        print("\n1. Novo Jogo")
        print("2. Sair")
        
        print("> ", end="", flush=True)
        choice = get_key()
        print(choice) # Mostra a tecla pressionada

        if choice == '1':
            player = character_creation()
            start_game(player)
        elif choice == '2':
            print("Obrigado por jogar!")
            break
        else:
            print("Opção inválida.")
            sleep(1)

if __name__ == '__main__':
    main()