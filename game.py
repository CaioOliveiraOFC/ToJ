#!/usr/bin/env python3

import random
from time import sleep
from toj_source.classes import Warrior, Mage, Rogue, Monster
from toj_source.interactions import fight, screen_clear, get_key
from toj_source.map import MapOfGame
from toj_source.items import Potion, Weapon, Armor


def safe_get_key(valid_keys=None, allow_escape=True):
    """
    Lê uma tecla com segurança.
    - Se valid_keys for None, retorna qualquer tecla.
    - Se valid_keys for lista, retorna apenas se estiver nela.
    - ESC (\x1b) retorna None se allow_escape=True.
    """
    while True:
        key = get_key()
        if not key:
            continue  # ignora None ou vazio
        key = key.lower()
        if allow_escape and key == '\x1b':
            return None
        if valid_keys is None or key in valid_keys:
            return key


def inventory_menu(player):
    """Exibe e gerencia o inventário do jogador."""
    while True:
        screen_clear()
        print("--- Inventário ---")
        print("\nEquipamento:")
        for slot, item in player.equipment.items():
            item_name = item.name if item else "Vazio"
            print(f"- {slot}: {item_name}")

        print("\nMochila:")
        if not player.inventory:
            print("- Vazia")
        else:
            for i, item in enumerate(player.inventory, 1):
                print(f"{i}. {item.name} - {item.description}")

        print("\nEscolha um item da mochila para (E)quipar/(U)sar, ou (S)air (ESC para voltar).")

        choice = safe_get_key(
            valid_keys=[str(i) for i in range(1, len(player.inventory) + 1)] + ['s']
        )

        if choice is None or choice == 's':
            break

        if choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                print(f"\nO que fazer com {selected_item.name}? (E)quipar / (U)sar (ESC para voltar)")
                action = safe_get_key(valid_keys=['e', 'u'])
                if action is None:
                    continue
                if action == 'e':
                    player.equip(selected_item)
                    sleep(1.5)
                elif action == 'u':
                    if isinstance(selected_item, Potion):
                        player.use_potion(selected_item)
                        sleep(1.5)
                    else:
                        print("Este item não pode ser usado.")
                        sleep(1)


def start_game(player):
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

            print("\nMova-se (w/a/s/d), (i)nventário ou 'q' para sair (ESC para voltar): ")
            move = safe_get_key(valid_keys=['w', 'a', 's', 'd', 'i', 'q'])

            if move is None or move == 'q':
                return
            elif move == 'i':
                inventory_menu(player)
            elif move in ['w', 'a', 's', 'd']:
                collided_object = game_map.move_player(move)

                if isinstance(collided_object, Monster):
                    fight(player, collided_object)
                    input("Pressione Enter para continuar sua jornada...")

                elif collided_object == 'level_complete':
                    dungeon_level += 1
                    break


def character_creation():
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
        print("1. Guerreiro\n2. Mago\n3. Ladino")
        choice = safe_get_key(valid_keys=['1', '2', '3'])
        if choice == '1':
            return Warrior(player_name)
        elif choice == '2':
            return Mage(player_name)
        elif choice == '3':
            return Rogue(player_name)


def main():
    """Função principal que exibe o menu e direciona o fluxo do jogo."""
    while True:
        screen_clear()
        print("=== Bem-vindo ao The Tales of the Journey ===")
        print("\n1. Novo Jogo")
        print("2. Sair")
        print("9. MODO DE TESTE (Herói Nível 50)")

        choice = safe_get_key(valid_keys=['1', '2', '9'])
        if choice is None or choice == '2':
            print("\nObrigado por jogar!")
            break

        if choice == '1':
            player = character_creation()
            start_game(player)
        elif choice == '9':
            player = Warrior("Tester")
            player.set_level(50)
            input(f"\nHerói de teste '{player.nick_name}' criado no nível 50. Pressione Enter para começar.")
            start_game(player)


if __name__ == '__main__':
    main()
