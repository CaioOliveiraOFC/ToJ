#!/usr/bin/env python3

from pyfiglet import Figlet
from os import system as s
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from time import sleep

console = Console()

def clear_screen():
    s('cls' if s('echo %OS%') == 'Windows_NT' else 'clear')

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
    sleep(1.5)

    console.print("\n") # Espaço após o título

    # Animação da história com typewriter effect e Panels
    for line in story_text:
        typewriter_effect(line, style="italic cyan", speed=0.03, return_text=False)
        sleep(0.5) # Short pause after typing
        console.print(Panel(Text(line, justify="center", style="italic cyan"), border_style="dim white", width=80))
        sleep(1.5) # Pausa para leitura do painel completo

    console.print("\n") # Espaço antes do prompt
    console.print(Panel(Text("Pressione [bold green]ENTER[/bold green] para começar sua aventura...", justify="center", style="bold yellow"), border_style="yellow", width=80))
    input("") # Espera pelo Enter

def main_menu():
    while True:
        clear_screen()
        console.print(Panel(Text("MENU PRINCIPAL", justify="center", style="bold magenta"), border_style="magenta", subtitle="Escolha seu destino, aventureiro."))
        
        menu_options = {
            "1": "Iniciar Nova Jornada",
            "2": "Carregar Aventura",
            "3": "Opções do Jogo",
            "4": "Sair do Jogo"
        }

        table = Table(show_header=False, expand=True, highlight=True, row_styles=["none", "dim"])
        table.add_column("Opção", style="bold blue", justify="right")
        table.add_column("Descrição", style="cyan")

        for key, value in menu_options.items():
            table.add_row(key, value)
        
        console.print(table)
        console.print("\n")
        
        choice = console.input("[bold green]Sua escolha, mortal:[/bold green] ")
        
        if choice == '1':
            console.print(Panel(Text("Adentrando as sombras da nova jornada...", justify="center", style="green"), border_style="green"))
            sleep(1.5)
            # Aqui seria a chamada para a criação de personagem/início do jogo
        elif choice == '2':
            console.print(Panel(Text("Revisitando memórias antigas... (não implementado)", justify="center", style="yellow"), border_style="yellow"))
            sleep(1.5)
        elif choice == '3':
            console.print(Panel(Text("Configurando o seu destino... (não implementado)", justify="center", style="yellow"), border_style="yellow"))
            sleep(1.5)
        elif choice == '4':
            console.print(Panel(Text("Até que a escuridão nos encontre novamente, aventureiro!", justify="center", style="red"), border_style="red"))
            sleep(1.5)
            break
        else:
            console.print(Panel(Text("Um erro em sua escolha, aventureiro. Tente novamente.", justify="center", style="bold red"), border_style="red"))
            sleep(1.5)

if __name__ == '__main__':
    splash_screen()
    main_menu()
