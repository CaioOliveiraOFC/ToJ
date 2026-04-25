#!/usr/bin/env python3

import random
from time import sleep
from toj_source.classes import Warrior, Mage, Rogue, Monster, show_status
from toj_source.interactions import fight
from toj_source.utils import clear_screen, safe_get_key
from toj_source.map import MapOfGame
from toj_source.items import Potion, Weapon, Armor
from toj_source.save_manager import save_game, load_game, check_save_file
from toj_source.game_logic import generate_monsters_for_level
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()
def inventory_menu(player):
    """
    Exibe o inventário do jogador usando Rich Panel e Table.
    """
    while True:
        console.clear()
        
        # Criação do painel principal do inventário
        console.print(Panel(
            Text("Mochila e Equipamentos", justify="center", style="bold green"),
            border_style="green",
            subtitle=f"Ouro: [bold yellow]{player.coins}[/bold yellow]"
        ))

        show_status(player)

        # Equipamentos
        equip_table = Table(title="[bold cyan]--- Equipamento ---[/bold cyan]", show_header=False, expand=True, border_style="dim cyan")
        equip_table.add_column("Slot", style="bold blue")
        equip_table.add_column("Item", style="cyan")
        
        for slot, item in player.equipment.items():
            if item:
                equip_table.add_row(slot.capitalize(), item.name)
            else:
                equip_table.add_row(slot.capitalize(), "[dim]Vazio[/dim]")
        
        console.print(equip_table)
        console.print("\n")

        # Itens na Mochila
        inv_table = Table(title="[bold magenta]--- Itens na Mochila ---[/bold magenta]", show_header=True, expand=True, border_style="dim magenta")
        inv_table.add_column("ID", style="bold blue", justify="right")
        inv_table.add_column("Item", style="cyan")
        inv_table.add_column("Tipo", style="yellow")
        
        if not player.inventory:
            console.print(Panel(Text("Sua mochila está vazia.", justify="center", style="dim white"), border_style="dim white"))
        else:
            for i, item in enumerate(player.inventory):
                inv_table.add_row(str(i + 1), item.name, item.__class__.__name__)
            console.print(inv_table)

        console.print("\n[dim white](número do item)[/dim white] selecionar | [dim white](x)[/dim white] sair do inventário")
        
        valid_choices = ['x'] + [str(i + 1) for i in range(len(player.inventory))]
        choice = safe_get_key(valid_keys=valid_choices)

        if choice == 'x':
            break
        elif choice and choice.isdigit():
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                console.clear()
                
                details_table = Table(show_header=False, expand=True, border_style="dim yellow")
                details_table.add_column("Atributo", style="bold cyan")
                details_table.add_column("Valor", style="white")
                
                details_table.add_row("Nome", selected_item.name)
                if hasattr(selected_item, 'description'):
                    details_table.add_row("Descrição", selected_item.description)
                details_table.add_row("Tipo", selected_item.__class__.__name__)
                
                if isinstance(selected_item, Weapon):
                    details_table.add_row("Dano", str(selected_item.damage))
                elif isinstance(selected_item, Armor):
                    details_table.add_row("Defesa", str(selected_item.defense))
                elif isinstance(selected_item, Potion):
                    details_table.add_row("Tipo de Efeito", getattr(selected_item, 'potion_type', 'Desconhecido'))
                    details_table.add_row("Poder de Efeito", f"+{getattr(selected_item, 'effect_value', 0)}")
                
                console.print(Panel(details_table, title="[bold yellow]Detalhes do Item[/bold yellow]", border_style="yellow"))
                
                # Ações
                action_table = Table(show_header=False, expand=True, border_style="dim white")
                action_options = []
                
                if isinstance(selected_item, Potion):
                    action_options.append('u')
                    action_table.add_row("[bold blue]u[/bold blue]", "Usar Poção")
                
                if isinstance(selected_item, (Weapon, Armor)):
                    is_equipped = False
                    for slot, equipped_item in player.equipment.items():
                        if equipped_item == selected_item:
                            is_equipped = True
                            break
                    if is_equipped:
                        action_options.append('e')
                        action_table.add_row("[bold blue]e[/bold blue]", "Desequipar Item")
                    else:
                        action_options.append('e')
                        action_table.add_row("[bold blue]e[/bold blue]", "Equipar Item")
                
                action_options.append('c')
                action_table.add_row("[bold blue]c[/bold blue]", "Cancelar")
                
                console.print(Panel(action_table, title="[bold cyan]Opções[/bold cyan]", border_style="cyan"))

                action_choice = safe_get_key(valid_keys=action_options, allow_escape=False)

                if action_choice == 'u':
                    if isinstance(selected_item, Potion):
                        player.use_potion(selected_item)
                        console.print(Panel(f"Você usou [bold green]{selected_item.name}[/bold green].", border_style="green"))
                        sleep(1.5)
                elif action_choice == 'e':
                    if isinstance(selected_item, (Weapon, Armor)):
                        is_equipped = False
                        for slot, equipped_item in player.equipment.items():
                            if equipped_item == selected_item:
                                player.unequip(slot)
                                console.print(Panel(f"Você desequipou [bold yellow]{selected_item.name}[/bold yellow].", border_style="yellow"))
                                is_equipped = True
                                break
                        if not is_equipped:
                            player.equip(selected_item)
                            console.print(Panel(f"Você equipou [bold green]{selected_item.name}[/bold green].", border_style="green"))
                        sleep(1.5)
                elif action_choice == 'c': 
                    continue


def start_game(player, start_level=1, initial_map_state=None):
    dungeon_level = start_level
    while True:
        MAP_HEIGHT = 12 + (dungeon_level // 5) * 2
        MAP_WIDTH = 25 + (dungeon_level // 5) * 4
        
        game_map = MapOfGame(height=MAP_HEIGHT, width=MAP_WIDTH)

        if initial_map_state and dungeon_level == start_level: # Only load map state for the initial level if provided
            game_map.load_map_state(initial_map_state) # Will implement this method in MapOfGame
        else:
            # Reduzindo de 0.2 para 0.05 para deixar o mapa absurdamente mais aberto
            game_map.generate_map(percent_of_walls=0.05 + min(dungeon_level * 0.01, 0.15))
            game_map.place_player()
            game_map.place_exit()
            # Substituindo a geração de monstros placeholder pela função de game_logic
            monsters_to_place = generate_monsters_for_level(dungeon_level)
            
            # Gerar Mini-Chefe a cada 5 níveis
            if dungeon_level % 5 == 0:
                from toj_source.math_operations import calculate_mini_boss_hp, calculate_mini_boss_strength, calculate_mini_boss_defense, calculate_mini_boss_magic
                boss_level = dungeon_level + 2
                boss = Monster(f"Chefe Nv.{boss_level}", boss_level)
                boss.is_boss = True
                boss.base_hp = calculate_mini_boss_hp(dungeon_level)
                boss._hp = boss.base_hp
                boss.base_st = calculate_mini_boss_strength(dungeon_level)
                boss._st = boss.base_st
                boss.base_df = calculate_mini_boss_defense(dungeon_level)
                boss._df = boss.base_df
                boss.base_mg = calculate_mini_boss_magic(dungeon_level)
                boss._mg = boss.base_mg
                boss.avg_damage = (boss._st + boss._mg) // 3
                monsters_to_place.append(boss)

            for monster in monsters_to_place:
                game_map.place_enemy(monster)

        while True:
            clear_screen()
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
                        from toj_source.toj_menu import game_over_screen
                        game_over_screen(player.get_nick_name())
                        return 
                    # After defeating a monster, update the map grid to reflect the empty space
                    game_map.grid[game_map.player_pos['y']][game_map.player_pos['x']] = '.'

                    print("Pressione qualquer tecla para continuar sua jornada...")
                    safe_get_key(allow_escape=False)

                elif collided_object == 'level_complete':
                    print(f"Você completou a Masmorra Nível {dungeon_level}!")
                    print("Pressione qualquer tecla para avançar para o próximo nível...")
                    safe_get_key(allow_escape=False)
                    dungeon_level += 1
                    # No need to reset initial_map_state as it's only for the very first map load.
                    # Subsequent maps are always generated anew.
                    initial_map_state = None 
                    break 


def character_creation():
    from toj_source.game_logic import create_player 
    return create_player()


def main():
    """Função principal que exibe o menu e direciona o fluxo do jogo."""
    from toj_source.toj_menu import main_menu
    
    while True:
        menu_choice = main_menu() # Assuming main_menu returns 'new_game', 'load_game', or 'quit'

        if menu_choice == 'new_game':
            player = character_creation()
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
            from toj_source.auto_test import AutoTester
            tester = AutoTester()
            tester.run_test(player)
        elif menu_choice == 'test_hero':
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
            print(f"\nHerói de teste '{player.nick_name}' criado no nível 50. Pressione Enter para começar.")
            safe_get_key(allow_escape=False)
            start_game(player)
        elif menu_choice == 'None' or not menu_choice:
            pass # Ignorar opções que não retornam
        else: 
            print("Opção inválida do menu. Reiniciando...")
            sleep(1.5)


if __name__ == '__main__':
    main()
