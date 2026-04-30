"""Funções de bootstrap e inicialização para o jogo.

Contém lógica de inicialização que não deve estar no main.py,
mantendo o entry point enxuto (<30 linhas).
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from src.content.items import Armor, Potion, Weapon
from src.engine.game_logic import create_player
from src.engine.loop import start_game
from src.entities.heroes import Warrior
from src.storage.save_manager import load_game
from src.ui.auto_test import AutoTester
from src.ui.toj_menu import main_menu

if TYPE_CHECKING:
    pass


def _create_test_hero() -> Warrior:
    """Cria um herói de nível 50 para testes."""
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
    return player


def run_main_loop() -> None:
    """Loop principal de execução do menu e direcionamento de fluxo."""
    while True:
        menu_choice = main_menu()

        if menu_choice == "new_game":
            player = create_player()
            if player:
                start_game(player, 1)
        elif menu_choice == "load_game":
            player, dungeon_level, map_state = load_game()
            if player:
                start_game(player, dungeon_level, map_state)
        elif menu_choice == "quit":
            break
        elif menu_choice == "auto_test":
            player = Warrior("TestBot")
            tester = AutoTester()
            tester.run_test(player)
        elif menu_choice == "test_hero":
            player = _create_test_hero()
            sleep(1)
            start_game(player)
