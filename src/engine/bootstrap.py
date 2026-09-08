"""Funções de bootstrap e inicialização para o jogo.

Contém lógica de inicialização que não deve estar no main.py,
mantendo o entry point enxuto (<30 linhas).
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from src.content.items import ALL_ITEMS, get_all_items
from src.engine.events import EventBus
from src.engine.game_logic import create_player_from_data
from src.engine.loop import start_game
from src.entities.heroes import Mage, Rogue, Warrior
from src.storage.save_manager import load_game
from src.ui import screens
from src.ui.ui_event_handlers import call_character_creation, call_main_menu, register_ui_handlers

# Import condicional - AutoTester foi movido para fora da camada UI
try:
    from tests.auto_test import AutoTester
except ImportError:
    AutoTester = None  # type: ignore

if TYPE_CHECKING:
    pass

# Registries para injeção de dependências no load_game
PLAYER_FACTORY = {
    "Warrior": Warrior,
    "Mage": Mage,
    "Rogue": Rogue,
}

# EventBus global para comunicação engine ↔ ui
_game_event_bus: EventBus | None = None
_ui_cleanup: callable | None = None

# Slot atual do jogador
_current_slot: int = 1


def _get_game_publish() -> callable:
    """Retorna publish callback para eventos de UI."""
    global _game_event_bus, _ui_cleanup
    if _game_event_bus is None:
        _game_event_bus = EventBus()
        _ui_cleanup = register_ui_handlers(_game_event_bus)
    return _game_event_bus.publish


def _create_test_hero() -> Warrior:
    """Cria um herói de nível 50 para testes."""
    player = Warrior("Tester")
    player.set_level(50)

    all_items = get_all_items()

    health_potion = all_items.get("Poção de Cura Grande")
    if health_potion:
        player.add_item_to_inventory(health_potion)

    mana_potion = all_items.get("Poção de Mana Grande")
    if mana_potion:
        player.add_item_to_inventory(mana_potion)

    sword = all_items.get("Espada Longa")
    if sword:
        player.add_item_to_inventory(sword)
        player.equip(sword)

    armor = all_items.get("Peitoral de Ferro")
    if armor:
        player.add_item_to_inventory(armor)
        player.equip(armor)

    return player


def run_main_loop() -> None:
    """Loop principal de execução do menu e direcionamento de fluxo."""
    _get_game_publish()  # Inicializa o event bus

    while True:
        menu_result = call_main_menu()

        if menu_result == 'quit':
            break
        elif menu_result == 'auto_test':
            if AutoTester is None:
                screens.render_game_saved("AutoTester não disponível.")
                continue
            player = Warrior("TestBot")
            tester = AutoTester()
            tester.run_test(player)
        elif menu_result == 'test_hero':
            player = _create_test_hero()
            sleep(0.5)
            start_game(player, 1, None, slot=1)
        elif isinstance(menu_result, tuple):
            choice, slot = menu_result
            if choice == "new_game":
                result = call_character_creation()
                if result:
                    class_key, player_name = result
                    player = create_player_from_data(class_key, player_name)
                    if player:
                        start_game(player, 1, None, slot=slot)
            elif choice == "load_game":
                player, dungeon_level, map_state = load_game(
                    item_registry=ALL_ITEMS,
                    player_factory=PLAYER_FACTORY,
                    slot=slot,
                )
                if player:
                    start_game(player, dungeon_level, map_state, slot=slot)
                else:
                    screens.render_game_saved("Falha ao carregar save. O arquivo pode estar corrompido.")
