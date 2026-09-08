#!/usr/bin/env python3

from time import sleep

from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.storage.save_manager import get_trophies, list_slots
from src.ui.prompts import get_key, safe_get_key
from src.ui.screens import menu
from src.ui.utils import clear_screen

console = Console()



def typewriter_effect(text: str, style: str = "white", speed: float = 0.04, return_text: bool = False) -> Text | None:
    """Exibe texto com um efeito de máquina de escrever ou retorna o texto estilizado."""
    typed_content = ""
    for char in text:
        typed_content += char
        if not return_text:
            # Clear the current line and print the new content
            console.print(Text(typed_content, style=style), end="\r")
            sleep(speed)
    if not return_text:
        console.print(Text(typed_content, style=style)) # Print final line with newline
    return Text(text, style=style) if return_text else None

def splash_screen():
    clear_screen()
    f = Figlet(font='doom', justify='center') # Changed to 'doom' for a darker feel
    ascii_art = f.renderText('Tales of the Journey')

    story_text = [
        "No reino sombrio de Eldoria, uma antiga escuridão ressurgiu...",
        "Monstros sedentos por sangue perambulam, e a esperança se esvai...",
        "Você, um aventureiro sem nome, é a última fagulha...",
        "Seu destino aguarda nas profundezas da masmorra...",
        "[bold red]A jornada começa agora![/bold red]",
    ]

    # Animação do título
    console.print(Panel(Text(ascii_art, justify="center", style="bold dark_red"), border_style="red", width=console.width))
    sleep(0.5)

    console.print("\n") # Espaço após o título

    # Animação da história com typewriter effect e Panels
    for line in story_text:
        typewriter_effect(line, style="italic cyan", speed=0.03, return_text=False)
        sleep(0.2) # Short pause after typing
        console.print(Panel(Text(line, justify="center", style="italic cyan"), border_style="dim white", width=80))
        sleep(0.5) # Pausa para leitura do painel completo

    console.print("\n") # Espaço antes do prompt
    console.print(Panel(Text.from_markup("Pressione [bold green]qualquer tecla[/bold green] para começar sua aventura...", justify="center", style="bold yellow"), border_style="yellow", width=80))
    safe_get_key(allow_escape=False)

def game_over_screen(player_name="Aventureiro"):
    clear_screen()
    f = Figlet(font='doom', justify='center')
    game_over_art = f.renderText('GAME OVER')

    # Enhanced Game Over Panel
    panel_content = Text(game_over_art, justify="center", style="bold red")
    panel_content.append("\n\n")
    panel_content.append(Text(f"A MORTE TE ALCANÇOU, {player_name.upper()}!", justify="center", style="bold red"))
    panel_content.append("\n")
    panel_content.append(Text("Seu legado se perde nas sombras...", justify="center", style="dim white"))

    console.print(Panel(
        panel_content,
        title="[bold red]-- Fim da Jornada --[/bold red]",
        border_style="bold red",
        subtitle="[italic]A escuridão prevaleceu...[/italic]",
        width=console.width
    ))

    console.print(Panel(
        Text("Toda jornada tem um fim, mas a lenda... a lenda pode recomeçar.", justify="center", style="italic white"),
        border_style="dim white"
    ))
    sleep(0.8)
    console.print(Panel(
        Text.from_markup("Pressione [bold green]qualquer tecla[/bold green] para retornar ao menu principal...", justify="center", style="bold yellow"),
        border_style="yellow"
    ))
    safe_get_key(allow_escape=False)

def display_final_stats(level: int, actions: int, battles: int, crashes: int):
    clear_screen()
    console.print(Panel(
        Text("RELATÓRIO DA JORNADA", justify="center", style="bold green"),
        title="[bold green]-- Jornada Concluída! --[/bold green]",
        border_style="green",
        subtitle="Detalhes de sua aventura em Eldoria.",
        width=console.width
    ))

    stats_table = Table(show_header=False, expand=True, box=None)
    stats_table.add_column("Métrica", style="bold cyan", justify="right")
    stats_table.add_column("Valor", style="yellow")

    stats_table.add_row("Nível Final Alcançado:", str(level))
    stats_table.add_row("Ações Tomadas:", str(actions))
    stats_table.add_row("Total de Batalhas:", str(battles))
    stats_table.add_row("Falhas Críticas (Crashes):", "[red]" + str(crashes) + "[/red]" if crashes > 0 else "[green]" + str(crashes) + "[/green]")

    console.print(Panel(stats_table, border_style="blue", title="[bold blue]Estatísticas da Aventura[/bold blue]"))

    console.print(Panel(
        Text("Obrigado por jogar Tales of the Journey! Esperamos vê-lo novamente.", justify="center", style="italic dim white"),
        border_style="dim white"
    ))
    sleep(0.8)
    console.print(Panel(
        Text.from_markup("Pressione [bold green]qualquer tecla[/bold green] para continuar...", justify="center", style="bold yellow"),
        border_style="yellow"
    ))
    safe_get_key(allow_escape=False)

def options_menu():
    while True:
        clear_screen()
        console.print(Panel(Text("OPÇÕES DO JOGO", justify="center", style="bold cyan"), border_style="cyan", subtitle="Ajuste sua experiência."))

        options_map = {
            "1": "Volume (não implementado)",
            "2": "Dificuldade (não implementado)",
            "3": "Voltar ao Menu Principal"
        }

        options_table = Table(show_header=False, expand=True, highlight=True, row_styles=["none", "dim"])
        options_table.add_column("Opção", style="bold blue", justify="right")
        options_table.add_column("Descrição", style="cyan")

        for key, value in options_map.items():
            options_table.add_row(key, value)

        console.print(options_table)
        console.print("\n")

        choice = safe_get_key(valid_keys=["1", "2", "3"])

        if choice == '1':
            console.print(Panel(Text("Função de Volume ainda não implementada.", justify="center", style="yellow"), border_style="yellow"))
            sleep(0.4)
        elif choice == '2':
            console.print(Panel(Text("Função de Dificuldade ainda não implementada.", justify="center", style="yellow"), border_style="yellow"))
            sleep(0.4)
        elif choice == '3':
            break
        else:
            console.print(Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="bold red"), border_style="red"))
            sleep(0.4)

def character_creation_flow() -> tuple[str, str] | None:
    """
    Fluxo de criação de personagem - coleta classe e nome via UI.

    Returns:
        Tupla (class_key, player_name) ou None se cancelado.
        A criação da entidade Player deve ser feita pela engine.
    """
    class_map = {
        "1": "warrior",
        "2": "mage",
        "3": "rogue",
    }

    # Seleção de classe
    while True:
        clear_screen()
        menu(("Guerreiro", "Mago", "Ladino"), "Escolha sua classe:")
        choice = safe_get_key(valid_keys=["1", "2", "3", "0"])
        if choice in class_map:
            class_key = class_map[choice]
            break
        if choice == "0":
            return None

    # Seleção de nome
    clear_screen()
    player_name = _prompt_for_name()
    if not player_name:
        return None

    # Retorna dados brutos - a engine fará a criação da entidade
    return class_key, player_name


def _prompt_for_name() -> str | None:
    """Solicita o nome do jogador via camada de UI."""
    while True:
        console.print(Panel(
            Text("Digite o nome do seu herói:", justify="center", style="bold cyan"),
            border_style="cyan"
        ))
        console.print("[dim](Pressione ESC para cancelar)[/dim]\n")

        name = console.input("[bold green]Nome:[/bold green] ").strip()
        if not name:
            console.print(Panel(
                Text("Nome não pode estar em branco.", style="red"),
                border_style="red"
            ))
            safe_get_key(allow_escape=False)
            continue
        return name


def show_slots_menu(title: str, allow_new: bool = True) -> int | None:
    """Mostra menu de slots e retorna slot selecionado (1-10) ou None para cancelar."""
    slots = list_slots()
    current_index = 0

    while True:
        clear_screen()

        console.print(Panel(
            Text(title, justify="center", style="bold cyan"),
            border_style="cyan",
            subtitle="Escolha um slot"
        ))

        table = Table(show_header=True, expand=True)
        table.add_column("SLOT", style="bold yellow", justify="center", width=8)
        table.add_column("NOME", style="cyan")
        table.add_column("CLASSE", style="magenta")
        table.add_column("NÍVEL", style="green", justify="center")
        table.add_column("ANDAR", style="red", justify="center")

        for i, s in enumerate(slots):
            prefix = ">" if i == current_index else " "
            name = s.get("name", "-") if s["occupied"] else "[dim]-[/dim]"
            cls = s.get("class", "-") if s["occupied"] else "[dim]-[/dim]"
            lvl = str(s.get("level", 0)) if s["occupied"] else "[dim]-[/dim]"
            floor = str(s.get("floor", 0)) if s["occupied"] else "[dim]-[/dim]"
            table.add_row(
                f"{prefix} {s['slot']} {prefix}",
                name,
                cls,
                lvl,
                floor
            )

        console.print(table)
        console.print()
        console.print(Text("W/S = navegar  |  ENTER = carregar  |  Q = voltar", style="bold cyan"))

        key = get_key()

        if key.lower() == "q":
            return None
        elif key.lower() == "w":
            current_index = (current_index - 1) % 10
        elif key.lower() == "s":
            current_index = (current_index + 1) % 10
        elif key.upper() == "ENTER":
            if not slots[current_index]["occupied"]:
                console.print(Panel(
                    Text("Slot vazio. Selecione um slot ocupado.", style="bold yellow"),
                    border_style="yellow"
                ))
                sleep(0.8)
                continue
            return slots[current_index]["slot"]


def select_new_slot() -> int | None:
    """Seleciona slot para novo jogo (apenas slots vazios)."""
    current_index = 0

    while True:
        clear_screen()
        slots = list_slots()
        available = [i for i, s in enumerate(slots) if not s["occupied"]]

        console.print(Panel(
            Text("ESCOLHA UM SLOT PARA NOVO JOGO", justify="center", style="bold cyan"),
            border_style="cyan",
            subtitle="Selecione um slot VAZIO"
        ))

        table = Table(show_header=True, expand=True)
        table.add_column("SLOT", style="bold yellow", justify="center", width=8)
        table.add_column("NOME", style="cyan")
        table.add_column("CLASSE", style="magenta")
        table.add_column("NÍVEL", style="green", justify="center")
        table.add_column("ANDAR", style="red", justify="center")

        for i, s in enumerate(slots):
            prefix = ">" if i == current_index else " "
            if s["occupied"]:
                name = f"[red]{s.get('name', '-')}[/red]"
                cls = f"[red]{s.get('class', '-')}[/red]"
                lvl = f"[red]{s.get('level', 0)}[/red]"
                floor = f"[red]{s.get('floor', 0)}[/red]"
            else:
                name = "[green]DISPONÍVEL[/green]"
                cls = "-"
                lvl = "-"
                floor = "-"
            table.add_row(
                f"{prefix} {s['slot']} {prefix}",
                name,
                cls,
                lvl,
                floor
            )

        console.print(table)
        console.print()

        if not available:
            console.print(Panel(
                Text("Todos os slots estão ocupados!", style="bold red"),
                border_style="red"
            ))
            console.print()
            console.print(Text("Pressione Q para voltar", style="dim"))
            key = get_key()
            if key.lower() == "q":
                return None
            continue

        console.print(Text("W/S = navegar  |  ENTER = criar  |  Q = voltar", style="bold cyan"))

        key = get_key()

        if key.lower() == "q":
            return None
        elif key.lower() == "w":
            current_index = (current_index - 1) % 10
        elif key.lower() == "s":
            current_index = (current_index + 1) % 10
        elif key.upper() == "ENTER":
            if not slots[current_index]["occupied"]:
                return slots[current_index]["slot"]
            console.print(Panel(
                Text("Slot ocupado. Escolha um slot vazio.", style="bold yellow"),
                border_style="yellow"
            ))
            sleep(0.8)


def show_trophies() -> None:
    """Mostra o livro de troféus (personagens que morreram)."""
    while True:
        clear_screen()
        trophies = get_trophies()

        console.print(Panel(
            Text("LIVRO DE TROFÉUS", justify="center", style="bold red"),
            border_style="red",
            subtitle="Heróis que findaram na masmorra"
        ))

        if not trophies:
            console.print(Panel(
                Text("Nenhum herói caiu em batalha ainda.", style="dim white"),
                border_style="dim"
            ))
        else:
            table = Table(show_header=True, expand=True)
            table.add_column("Nome", style="cyan")
            table.add_column("Classe", style="magenta")
            table.add_column("Nível", style="green")
            table.add_column("Andar", style="red")
            table.add_column("Data", style="dim")
            table.add_column("Causa", style="yellow")

            for t in trophies:
                table.add_row(
                    t.get("name", "?"),
                    t.get("class", "?"),
                    str(t.get("level", 0)),
                    str(t.get("floor", 0)),
                    t.get("date", "-"),
                    t.get("cause", "-")
                )

            console.print(table)
            console.print(f"\n[bold]Total de baixas: {len(trophies)}[/bold]")

        console.print("\n[dim]Q para voltar ao menu[/dim]")
        key = safe_get_key(valid_keys=["q"])
        if key == "q":
            return


def main_menu():
    while True:
        clear_screen()
        console.print(Panel(Text("MENU PRINCIPAL", justify="center", style="bold magenta"), border_style="magenta", subtitle="Escolha seu destino, aventureiro."))

        slots = list_slots()
        occupied_count = sum(1 for s in slots if s["occupied"])

        menu_options = {
            "1": f"Nova Jornada ({10 - occupied_count} slots disponíveis)",
            "2": f"Carregar Aventura ({occupied_count} slots ocupados)",
            "3": "Livro de Troféus",
            "4": "Opções do Jogo",
            "5": "Sair do Jogo",
            "6": "MODO DE AUTO-TESTE (BOT)",
            "7": "MODO DE TESTE (Herói Nível 50)"
        }

        table = Table(show_header=False, expand=True, highlight=True, row_styles=["none", "dim"])
        table.add_column("Opção", style="bold blue", justify="right")
        table.add_column("Descrição", style="cyan")

        for key, value in menu_options.items():
            table.add_row(key, value)

        console.print(table)
        console.print("\n")

        choice = safe_get_key(valid_keys=["1", "2", "3", "4", "5", "6", "7"])

        if choice == '1':
            slot = select_new_slot()
            if slot:
                console.print(Panel(Text(f"Iniciando nova jornada no slot {slot}...", justify="center", style="green"), border_style="green"))
                sleep(0.4)
                return ('new_game', slot)
            # Se cancelou, continua no menu
        elif choice == '2':
            slot = show_slots_menu("CARREGAR AVENTURA")
            if slot:
                console.print(Panel(Text(f"Carregando aventura do slot {slot}...", justify="center", style="yellow"), border_style="yellow"))
                sleep(0.4)
                return ('load_game', slot)
        elif choice == '3':
            show_trophies()
        elif choice == '4':
            options_menu()
        elif choice == '5':
            console.print(Panel(Text("Até que a escuridão nos encontre novamente, aventureiro!", justify="center", style="red"), border_style="red"))
            sleep(0.4)
            return 'quit'
        elif choice == '6':
            console.print(Panel(Text("Iniciando a simulação...", justify="center", style="magenta"), border_style="magenta"))
            sleep(0.4)
            return 'auto_test'
        elif choice == '7':
            console.print(Panel(Text("Iniciando MODO DE TESTE com herói nível 50...", justify="center", style="magenta"), border_style="magenta"))
            sleep(0.4)
            return 'test_hero'
        else:
            console.print(Panel(Text("Um erro em sua escolha, aventureiro. Tente novamente.", justify="center", style="bold red"), border_style="red"))
            sleep(0.4)

if __name__ == '__main__':
    splash_screen()
    main_menu()
    # For testing game over and final stats:
    # game_over_screen("Tester")
    # display_final_stats(level=6, actions=299, battles=68, crashes=0)
