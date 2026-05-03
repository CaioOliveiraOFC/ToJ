"""Menu navegável com arrow keys (cima/baixo) e Enter para selecionar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui import renderer
from src.ui.prompts import get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def escape_markup(text: str) -> str:
    """Escapa caracteres que quebram markup Rich."""
    return text.replace("[", "\\[").replace("]", "\\]")


def navigate_menu(
    items: list[str],
    title: str,
    max_visible: int = 10,
    show_index: bool = True,
) -> int | None:
    """Menu navegável com arrow keys.
    
    Args:
        items: Lista de opções a mostrar.
        title: Título do menu.
        max_visible: Máximo de itens visíveis por página.
        show_index: Se True, mostra número antes de cada opção.
    
    Returns:
        Índice selecionado (0-based) ou None se Cancelar (ESC).
    """
    if not items:
        return None
    
    current_index = 0
    total_items = len(items)
    total_pages = (total_items + max_visible - 1) // max_visible
    current_page = 0
    
    while True:
        renderer.console.clear()
        
        start_idx = current_page * max_visible
        end_idx = min(start_idx + max_visible, total_items)
        visible_items = items[start_idx:end_idx]
        
        panel_content = f"[bold yellow]{escape_markup(title)}[/bold yellow]\n"
        panel_content += "[dim]" + "=" * 40 + "[/dim]\n\n"
        
        for i, item in enumerate(visible_items):
            real_index = start_idx + i
            prefix = ">" if real_index == current_index else " "
            
            if show_index:
                panel_content += f"{prefix} [{real_index + 1:2}] {escape_markup(item)}\n"
            else:
                panel_content += f"{prefix} {escape_markup(item)}\n"
        
        if total_pages > 1:
            panel_content += f"\n[dim]Página {current_page + 1}/{total_pages}[/dim]\n"
        
        panel_content += "\n[dim]W/S navegar | ENTER selecionar | ESC sair[/dim]"
        
        from rich.panel import Panel
        renderer.console.print(Panel(panel_content, border_style="cyan"))
        
        key = get_key()
        
        if key in ("w", "W"):
            current_index -= 1
            if current_index < 0:
                current_index = total_items - 1
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key in ("s", "S"):
            current_index += 1
            if current_index >= total_items:
                current_index = 0
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key == "ENTER":
            return current_index
        
        elif key.lower() == "esc":
            return None


def navigate_shop_buy(
    items: list[dict],
    player_coins: int,
) -> int | None:
    """Menu navegável para comprar itens na loja com split view.
    
    Args:
        items: Lista de {"item": Item, "price": int}.
        player_coins: Moedas do jogador.
    
    Returns:
        Índice selecionado ou None se Cancelar.
    """
    if not items:
        return None
    
    from rich.table import Table
    from rich.panel import Panel
    from rich.console import Console
    
    current_index = 0
    max_visible = 10
    total_items = len(items)
    total_pages = (total_items + max_visible - 1) // max_visible
    current_page = 0
    
    def build_item_details(item) -> str:
        """Constrói o conteúdo do painel de detalhes."""
        content = f"[bold]Nome:[/bold] {escape_markup(item.name)}\n\n"
        content += f"[bold]Descrição:[/bold]\n{escape_markup(item.description)}\n\n"
        
        slot_name = getattr(item, "slot", "Unknown")
        content += f"[bold]Tipo:[/bold] {slot_name}\n"
        
        damage = getattr(item, "damage_bonus", 0)
        defense = getattr(item, "defense_bonus", 0)
        
        if damage > 0:
            content += f"[bold]Dano:[/bold] +{damage}\n"
        if defense > 0:
            content += f"[bold]Defesa:[/bold] +{defense}\n"
        
        effect_type = getattr(item, "effect_type", None)
        effect_value = getattr(item, "effect_value", 0)
        if effect_type and effect_value:
            content += f"[bold]Efeito:[/bold] {effect_type} +{effect_value}\n"
        
        rarity = getattr(item, "rarity", "Common")
        content += f"[bold]Raridade:[/bold] {rarity}\n"
        
        classes = getattr(item, "classes", None)
        if classes:
            classes_str = ", ".join(classes)
        else:
            classes_str = "Todas"
        content += f"[bold]Classes:[/bold] {classes_str}\n"
        
        return content
    
    while True:
        renderer.console.clear()
        
        start_idx = current_page * max_visible
        end_idx = min(start_idx + max_visible, total_items)
        visible_items = items[start_idx:end_idx]
        
        # Painel esquerdo - Lista de itens
        left_content = "[bold yellow]COMPRAR ITENS[/bold yellow]\n"
        left_content += "[dim]" + "=" * 35 + "[/dim]\n\n"
        
        for i, data in enumerate(visible_items):
            real_index = start_idx + i
            item = data["item"]
            price = data["price"]
            
            prefix = ">" if real_index == current_index else " "
            coin_str = f"{price:>5} coins"
            
            if price > player_coins:
                coin_str = f"[red]{coin_str}[/red]"
            
            left_content += f"{prefix} [{real_index + 1:2}] {escape_markup(item.name)} - {coin_str}\n"
        
        if total_pages > 1:
            left_content += f"\n[dim]Página {current_page + 1}/{total_pages}[/dim]\n"
        
        left_content += f"\n[bold cyan]Ouro: {player_coins} coins[/bold cyan]"
        
        left_panel = Panel(left_content, border_style="yellow", title="[yellow]LOJA[/yellow]")
        
        # Painel direito - Detalhes do item selecionado
        selected_item = items[current_index]["item"]
        details_content = build_item_details(selected_item)
        right_panel = Panel(details_content, border_style="cyan", title="[cyan]DETALHES[/cyan]", width=50)
        
        # Criar tabela com dois painéis
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("left", justify="left", width=45)
        table.add_column("right", justify="left", width=52)
        table.add_row(left_panel, right_panel)
        
        # Rodapé
        footer = Panel(
            "[dim]W/S navegar | ENTER comprar | ESC voltar[/dim]",
            border_style="dim"
        )
        
        renderer.console.print(table)
        renderer.console.print(footer)
        
        key = get_key()
        
        if key in ("w", "W"):
            current_index -= 1
            if current_index < 0:
                current_index = total_items - 1
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key in ("s", "S"):
            current_index += 1
            if current_index >= total_items:
                current_index = 0
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key == "ENTER":
            return current_index
        
        elif key.lower() == "esc":
            return None


def navigate_shop_sell(
    inventory: list,
    player_coins: int,
) -> int | None:
    """Menu navegável para vender itens do inventário.
    
    Args:
        inventory: Lista de itens no inventário.
        player_coins: Moedas do jogador.
    
    Returns:
        Índice selecionado ou None se Cancelar.
    """
    if not inventory:
        return None
    
    current_index = 0
    max_visible = 10
    total_items = len(inventory)
    total_pages = (total_items + max_visible - 1) // max_visible
    current_page = 0
    
    while True:
        renderer.console.clear()
        
        start_idx = current_page * max_visible
        end_idx = min(start_idx + max_visible, total_items)
        visible_items = inventory[start_idx:end_idx]
        
        from rich.panel import Panel
        
        panel_content = "[bold yellow]VENDER ITENS[/bold yellow]\n"
        panel_content += "[dim]" + "=" * 50 + "[/dim]\n\n"
        
        from src.content.items import get_all_items
        all_items = get_all_items()
        
        for i, item in enumerate(visible_items):
            real_index = start_idx + i
            
            base_item = all_items.get(item.name)
            if base_item:
                sell_price = int(base_item.price * 0.5)
            else:
                sell_price = 10
            
            prefix = ">" if real_index == current_index else " "
            rarity_color = _get_rarity_color(getattr(item, "rarity", "Common"))
            
            panel_content += f"{prefix} [{real_index + 1:2}] {escape_markup(item.name)} - [green]+{sell_price} coins[/green]\n"
        
        if total_pages > 1:
            panel_content += f"\n[dim]Página {current_page + 1}/{total_pages}[/dim]\n"
        
        panel_content += f"\n[bold cyan]Seu ouro: {player_coins} coins[/bold cyan]\n"
        panel_content += "\n[dim]W/S navegar | ENTER vender | ESC voltar[/dim]"
        
        renderer.console.print(Panel(panel_content, border_style="yellow"))
        
        key = get_key()
        
        if key in ("w", "W"):
            current_index -= 1
            if current_index < 0:
                current_index = total_items - 1
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key in ("s", "S"):
            current_index += 1
            if current_index >= total_items:
                current_index = 0
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key == "ENTER":
            return current_index
        
        elif key.lower() == "esc":
            return None


def navigate_inventory(
    inventory: list,
    equipped_indices: list[int],
) -> int | None:
    """Menu navegável para selecionar item do inventário.
    
    Args:
        inventory: Lista de itens no inventário.
        equipped_indices: Lista de índices dos itens equipados.
    
    Returns:
        Índice selecionado ou None se Cancelar.
    """
    if not inventory:
        return None
    
    current_index = 0
    max_visible = 10
    total_items = len(inventory)
    total_pages = (total_items + max_visible - 1) // max_visible
    current_page = 0
    
    while True:
        renderer.console.clear()
        
        start_idx = current_page * max_visible
        end_idx = min(start_idx + max_visible, total_items)
        visible_items = inventory[start_idx:end_idx]
        
        from rich.panel import Panel
        
        panel_content = "[bold yellow]INVENTÁRIO[/bold yellow]\n"
        panel_content += "[dim]" + "=" * 50 + "[/dim]\n\n"
        
        for i, item in enumerate(visible_items):
            real_index = start_idx + i
            
            prefix = ">" if real_index == current_index else " "
            rarity_color = _get_rarity_color(getattr(item, "rarity", "Common"))
            equipped_mark = "[bold green] (E)[/bold green]" if real_index in equipped_indices else ""
            
            panel_content += f"{prefix} [{real_index + 1:2}] {escape_markup(item.name)}{equipped_mark}\n"
        
        if total_pages > 1:
            panel_content += f"\n[dim]Página {current_page + 1}/{total_pages}[/dim]\n"
        
        panel_content += "\n[dim]W/S navegar | ENTER selecionar | ESC voltar[/dim]"
        
        renderer.console.print(Panel(panel_content, border_style="cyan"))
        
        key = get_key()
        
        if key in ("w", "W"):
            current_index -= 1
            if current_index < 0:
                current_index = total_items - 1
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key in ("s", "S"):
            current_index += 1
            if current_index >= total_items:
                current_index = 0
            if current_index // max_visible != current_page:
                current_page = current_index // max_visible
        
        elif key == "ENTER":
            return current_index
        
        elif key.lower() == "esc":
            return None


def _get_rarity_color(rarity: str) -> str:
    """Retorna a cor Rich para a raridade."""
    colors = {
        "Common": "white",
        "Rare": "cyan",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    return colors.get(rarity, "white")