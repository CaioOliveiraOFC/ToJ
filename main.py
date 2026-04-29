#!/usr/bin/env python3
"""Entry point: bootstrap e orquestração do menu principal."""

from time import sleep

from src.content.items import Armor, Potion, Weapon
from src.engine.game_logic import create_player
from src.engine.loop import start_game
from src.entities.heroes import Warrior
from src.storage.save_manager import load_game
from src.ui.auto_test import AutoTester
from src.ui.prompts import safe_get_key
from src.ui.toj_menu import main_menu


def main() -> None:
    """Função principal que exibe o menu e direciona o fluxo do jogo."""
    while True:
        menu_choice = main_menu()

        if menu_choice == 'new_game':
            player = create_player()
            if player:
                start_game(player, 1)
            else:
                print("Criação de personagem cancelada ou falhou. Voltando ao menu principal.")
                sleep(1.5)
        elif menu_choice == 'load_game':
            player, dungeon_level, map_state = load_game()
            if player:
                start_game(player, dungeon_level, map_state)
            else:
                print("Falha ao carregar o jogo ou nenhum jogo salvo. Voltando ao menu principal.")
                sleep(1.5)
        elif menu_choice == 'quit':
            print("Obrigado por jogar Tales of the Journey!")
            sleep(2)
            break
        elif menu_choice == 'auto_test':
            player = Warrior("TestBot")
            tester = AutoTester()
            tester.run_test(player)
        elif menu_choice == 'test_hero':
            player = Warrior("Tester")
            player.set_level(50)
            player.add_item_to_inventory(Potion("Super Poção de Cura", "Poção forte", 50, "Health"))
            player.add_item_to_inventory(Potion("Mega Poção de Mana", "Mana forte", 30, "Mana"))
            test_sword = Weapon("Espada do Teste", "Arma apelona", 15)
            player.add_item_to_inventory(test_sword)
            player.equip(test_sword)
            test_armor = Armor("Armadura do Teste", "Armadura grossa", 10, "Body")
            player.add_item_to_inventory(test_armor)
            player.equip(test_armor)
            print(f"\nHerói de teste '{player.nick_name}' criado no nível 50. Pressione Enter para começar.")
            safe_get_key(allow_escape=False)
            start_game(player)
        elif not menu_choice:
            pass
        else:
            print("Opção inválida do menu. Reiniciando...")
            sleep(1.5)


if __name__ == '__main__':
    main()
