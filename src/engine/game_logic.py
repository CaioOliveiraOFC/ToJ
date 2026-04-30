#!/usr/bin/env python3
"""Lógica de criação de personagem e inicialização do jogo."""

from src.content.skills import mage_skills, rogue_skills, warrior_skills
from src.entities.heroes import Mage, Rogue, Warrior
from src.ui.prompts import safe_get_key
from src.ui.screens import menu
from src.ui.utils import clear_screen


def create_player():
    """
    Função para criar o personagem do jogador via UI (prompts/screens).
    Coleta classe e nome do jogador usando a camada de UI apropriada.
    """
    clear_screen()
    class_map = {
        "1": ("guerreiro", Warrior, warrior_skills),
        "2": ("mago", Mage, mage_skills),
        "3": ("ladino", Rogue, rogue_skills),
    }

    # Seleção de classe via UI
    while True:
        clear_screen()
        menu(("Guerreiro", "Mago", "Ladino"), "Escolha sua classe:")
        choice = safe_get_key(valid_keys=["1", "2", "3", "0"])
        if choice in class_map:
            class_key, class_constructor, skills = class_map[choice]
            break
        if choice == "0":
            return None

    # Seleção de nome - usando input através da camada de UI
    clear_screen()
    player_name = _prompt_for_name()
    if not player_name:
        return None

    # Criação do personagem
    player = class_constructor(player_name)
    player.learnable_skills = skills
    player.learn_new_skills(show=False)
    return player


def _prompt_for_name() -> str | None:
    """Solicita o nome do jogador via camada de UI."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
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
        return _prompt_for_name()
    return name

# Código legado removido. A função main() anterior violava a Regra 3
# (prints/inputs diretos em engine/). O loop principal agora está em loop.py.
