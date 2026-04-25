import os
import platform
from random import choice, randrange
from time import sleep
from .math_operations import percentage
from .classes import get_hp_bar
from .items import get_loot, Potion

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

console = Console()

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

# Removed the 'line' function as it will be replaced by rich components.

def menu(options, prompt):
    """Exibe um menu de opções usando Rich para uma interface consistente e premium."""
    console.print(Panel(Text(prompt, justify="center", style="bold yellow"), border_style="yellow"))
    
    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Chave", style="bold blue", justify="right", width=4)
    table.add_column("Opção", style="cyan")
    
    for i, option in enumerate(options, 1):
        table.add_row(f"{i}.", option)
        
    console.print(table)
    console.print("=" * console.width, style="dim white")

def display_battle_ui(player, monster):
    screen_clear()
    
    # Battle Title
    console.print(Panel(Text("=== BATALHA ===", justify="center", style="bold red"), border_style="red"))
    
    # Player VS Monster names
    player_name_text = Text(player.get_nick_name(), style="bold blue")
    monster_name_text = Text(monster.nick_name, style="bold magenta")
    vs_text = Text("VS", style="bold white")
    
    name_table = Table(show_header=False, expand=True, box=None)
    name_table.add_column(justify="left")
    name_table.add_column(justify="center")
    name_table.add_column(justify="right")
    name_table.add_row(player_name_text, vs_text, monster_name_text)
    console.print(name_table)

    # HP Bars
    player_hp_bar = get_hp_bar(player)
    monster_hp_bar = get_hp_bar(monster)
    
    hp_table = Table(show_header=False, expand=True, box=None)
    hp_table.add_column(justify="left")
    hp_table.add_column(justify="right")
    hp_table.add_row(Text(player_hp_bar, style="green"), Text(monster_hp_bar, style="red"))
    console.print(hp_table)

    # MP for player
    console.print(f"MP: [cyan]{player.get_mp()}[/cyan]/[dim cyan]{player.base_mp}[/dim cyan]", justify="left")
    console.print("=" * console.width, style="dim white") # Separator line

def perform_attack(attacker, defender, base_damage, skill_name=""):
    """Executa a lógica de um único ataque e imprime o resultado."""
    crit_chance = 25 if hasattr(attacker, 'get_classname') and attacker.get_classname() == 'Rogue' and skill_name == "Ataque Furtivo" else 10
    
    hit_chance = 85 + (attacker.get_ag() - defender.get_ag())
    if randrange(1, 101) > hit_chance:
        console.print(f"[bold red]{attacker.get_nick_name()}[/bold red] [dim white]errou o ataque![/dim white]", justify="center")
        sleep(1.5)
        return

    defense_reduction = defender.get_df() // 2
    damage = max(1, base_damage - defense_reduction)
    
    is_critical = randrange(1, 101) <= crit_chance
    if is_critical:
        damage *= 2

    defender.reduce_hp(damage)
    
    critical_msg = " [bold yellow]ATAQUE CRÍTICO![/bold yellow]" if is_critical else ""
    console.print(f"[bold {('blue' if attacker.my_type() == 'Human' else 'magenta')}]{attacker.get_nick_name()}[/bold {('blue' if attacker.my_type() == 'Human' else 'magenta')}] causou [orange3]{damage}[/orange3] de dano em [bold {('magenta' if defender.my_type() == 'Monster' else 'blue')}]{defender.get_nick_name()}[/bold {('magenta' if defender.my_type() == 'Monster' else 'blue')}].{critical_msg}", justify="center")
    sleep(1.5)

def use_skill(caster, target, skill):
    """Processa o uso de uma habilidade e seus efeitos."""
    console.print(Panel(Text.from_markup(f"{caster.get_nick_name()} usa [bold green]{skill.name}[/bold green]!", justify="center", style="white"), border_style="green"))
    sleep(1)
    caster.reduce_mp(skill.mana_cost)

    if skill.effect_type == 'damage':
        perform_attack(caster, target, skill.value, skill.name)
    
    elif skill.effect_type == 'heal':
        heal_amount = skill.value
        caster._hp = min(caster.base_hp, caster.get_hp() + heal_amount)
        console.print(f"[bold green]{caster.get_nick_name()}[/bold green] recupera [bold cyan]{heal_amount}[/bold cyan] de HP!", justify="center")
        sleep(1.5)

    elif skill.effect_type == 'status':
        if randrange(1, 101) <= skill.chance:
            target.active_effects[skill.value] = {'duration': skill.duration}
            console.print(f"[bold purple]{target.get_nick_name()}[/bold purple] está sob o efeito de [yellow]{skill.value}[/yellow]!", justify="center")
        else:
            console.print("[dim red]O efeito falhou![/dim red]", justify="center")
        sleep(1.5)

    elif skill.effect_type == 'buff':
        caster.active_buffs[skill.name] = {'value': skill.value, 'duration': skill.duration}
        console.print(f"[bold blue]{caster.get_nick_name()}[/bold blue] recebe o buff [bold yellow]{skill.name}[/bold yellow]!", justify="center")
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
            console.print(f"[bold green4]{entity.get_nick_name()}[/bold green4] sofre [orange3]{poison_damage}[/orange3] de dano de veneno.", justify="center")
        
        if effect == 'frozen':
            console.print(f"[bold blue]{entity.get_nick_name()}[/bold blue] está [bold cyan]congelado[/bold cyan] e não pode se mover!", justify="center")
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
        console.print(f"O efeito [dim white]{effect}[/dim white] em [dim blue]{entity.get_nick_name()}[/dim blue] passou.", justify="center")
    for buff in buffs_to_remove:
        del entity.active_buffs[buff]
        console.print(f"O buff [dim white]{buff}[/dim white] em [dim blue]{entity.get_nick_name()}[/dim blue] acabou.", justify="center")
    
    if any([effects_to_remove, buffs_to_remove, 'poison' in entity.active_effects]):
        sleep(1.5)
        
    return skipped_turn

def compare_opponents(ennt1, ennt2):
    """ Esta função imprime uma comparação lado a lado dos status de duas entidades. """
    console.print(Panel(Text("CONFRONTO", justify="center", style="bold yellow"), border_style="yellow"))

    table = Table(show_header=False, expand=True, border_style="dim white")
    table.add_column(Text(ennt1.get_nick_name(), style="bold blue"), justify="left")
    table.add_column(Text("VS", style="bold white"), justify="center")
    table.add_column(Text(ennt2.get_nick_name(), style="bold magenta"), justify="right")
    
    table.add_row(f"Nível: [green]{ennt1.get_level()}[/green]", "", f"Nível: [green]{ennt2.level}[/green]")
    table.add_row(f"HP: [red]{ennt1.get_hp()}[/red]/[dim red]{ennt1.base_hp}[/dim red]", "", f"HP: [red]{ennt2.get_hp()}[/red]/[dim red]{ennt2.base_hp}[/dim red]")
    table.add_row(f"MP: [cyan]{ennt1.get_mp()}[/cyan]/[dim cyan]{ennt1.base_mp}[/dim cyan]", "", f"MP: [cyan]{ennt2.get_mp()}[/cyan]/[dim cyan]{ennt2.base_mp}[/dim cyan]")
    table.add_row(f"Força: [yellow]{ennt1.get_st()}[/yellow]", "", f"Força: [yellow]{ennt2.get_st()}[/yellow]")
    table.add_row(f"Agilidade: [green]{ennt1.get_ag()}[/green]", "", f"Agilidade: [green]{ennt2.get_ag()}[/green]")
    table.add_row(f"Magia: [blue]{ennt1.get_mg()}[/blue]", "", f"Magia: [blue]{ennt2.get_mg()}[/blue]")
    table.add_row(f"Defesa: [white]{ennt1.get_df()}[/white]", "", f"Defesa: [white]{ennt2.get_df()}[/white]")
    
    console.print(table)
    console.print("=" * console.width, style="dim white") # Separator line

def fight(player, monster):
    player.rest()
    
    screen_clear()
    console.print(Panel(Text("--- Início da Batalha ---", justify="center", style="bold green"), border_style="green"))
    compare_opponents(player, monster)
    console.input(Panel(Text.from_markup("Pressione [bold green]ENTER[/bold green] para começar a batalha...", justify="center", style="yellow"), border_style="yellow"))
    
    turn_order = [player, monster]
    if player.get_ag() < monster.get_ag():
        turn_order = [monster, player]

    attacker_index = 0
    while player.get_isalive() and monster.isalive:
        attacker = turn_order[attacker_index]
        defender = turn_order[(attacker_index + 1) % 2]
        
        display_battle_ui(player, monster)
        console.print(Panel(Text.from_markup(f"É a vez de [bold {('blue' if attacker.my_type() == 'Human' else 'magenta')}]{attacker.get_nick_name()}[/bold {('blue' if attacker.my_type() == 'Human' else 'magenta')}].", justify="center", style="white"), border_style="blue"))
        sleep(1)

        if handle_turn_effects(attacker):
            attacker_index = (attacker_index + 1) % 2
            continue

        if attacker.my_type() == 'Human':
            action_taken = False
            while not action_taken:
                display_battle_ui(player, monster)
                
                action_menu_table = Table(show_header=False, expand=True, border_style="dim white")
                action_menu_table.add_column("Opção", style="bold blue", justify="right")
                action_menu_table.add_column("Descrição", style="cyan")
                action_menu_table.add_row("1.", "Ataque Normal")
                action_menu_table.add_row("2.", "Habilidades")
                action_menu_table.add_row("3.", "Usar Item")
                action_menu_table.add_row("4.", "Tentar Fugir")
                
                console.print(Panel(action_menu_table, title="[bold yellow]Escolha sua ação[/bold yellow]", border_style="yellow"))
                
                choice = safe_get_key(valid_keys=['1', '2', '3', '4'])

                if choice == '1':
                    perform_attack(player, monster, player.get_avg_damage())
                    action_taken = True
                
                elif choice == '2':
                    if not player.skills:
                        console.print(Panel(Text("Você não tem habilidades para usar!", justify="center", style="red"), border_style="red"))
                        sleep(1)
                        continue
                    
                    while True:
                        display_battle_ui(player, monster)
                        
                        skill_table = Table(show_header=False, expand=True, border_style="dim white")
                        skill_table.add_column("Chave", style="bold blue", justify="right")
                        skill_table.add_column("Habilidade", style="cyan")
                        skill_table.add_column("Custo", style="magenta", justify="left")

                        for key, skill in player.skills.items():
                            skill_table.add_row(str(key) + ".", skill.name, f"{skill.mana_cost} MP")
                        skill_table.add_row("0.", "Voltar", "")
                        
                        console.print(Panel(skill_table, title="[bold yellow]Escolha uma habilidade[/bold yellow]", border_style="yellow"))
                        
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
                                console.print(Panel(Text("Mana insuficiente!", justify="center", style="red"), border_style="red"))
                                sleep(1)
                
                elif choice == '3':
                    potions = [item for item in player.inventory if isinstance(item, Potion)]
                    if not potions:
                        console.print(Panel(Text("Você não tem poções para usar!", justify="center", style="red"), border_style="red"))
                        sleep(1)
                        continue
                    
                    while True:
                        display_battle_ui(player, monster)
                        
                        potion_table = Table(show_header=False, expand=True, border_style="dim white")
                        potion_table.add_column("Chave", style="bold blue", justify="right")
                        potion_table.add_column("Poção", style="cyan")
                        potion_table.add_column("Descrição", style="dim white")

                        for i, potion in enumerate(potions, 1):
                            potion_table.add_row(str(i) + ".", potion.name, potion.description)
                        potion_table.add_row("0.", "Voltar", "")

                        console.print(Panel(potion_table, title="[bold yellow]Escolha uma poção[/bold yellow]", border_style="yellow"))

                        potion_keys = [str(i) for i in range(1, len(potions) + 1)] + ['0']
                        potion_choice = safe_get_key(potion_keys)

                        if potion_choice == '0': break

                        if potion_choice and potion_choice.isdigit():
                            if 0 < int(potion_choice) <= len(potions):
                                player.use_potion(potions[int(potion_choice) - 1])
                                action_taken = True
                                sleep(1.5)
                                break
                            else:
                                console.print(Panel(Text("Escolha inválida de poção!", justify="center", style="red"), border_style="red"))
                                sleep(1)
                
                elif choice == '4':
                    if randrange(0, 2) == 0:
                        console.print(Panel(Text("Você conseguiu fugir da batalha!", justify="center", style="green"), border_style="green"))
                        sleep(2)
                        player.rest()
                        return
                    else:
                        console.print(Panel(Text("A fuga falhou!", justify="center", style="red"), border_style="red"))
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
        console.print(Panel(Text("Você foi derrotado...", justify="center", style="bold red"), border_style="red"))
        pity_xp = xp_base_reward // 10
        player.add_xp_points(pity_xp)
    else:
        console.print(Panel(Text.from_markup(f"Você derrotou [bold magenta]{monster.nick_name}[/bold magenta]!", justify="center", style="bold green"), border_style="green"))
        player.add_xp_points(xp_base_reward)
        dropped_item = get_loot()
        if dropped_item:
            # Wrapped the loot message in a Panel for more emphasis.
            console.print(Panel(Text.from_markup(f"Você encontrou [bold yellow]{dropped_item.name}[/bold yellow]!", justify="center", style="yellow"), border_style="yellow", width=80))
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
