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


def _find_equipped_slot_by_item(player, item) -> str | None:
    """Encontra o slot onde o item está equipado."""
    for slot, equipped_item in player.equipment.items():
        if equipped_item == item:
            return slot
    return None


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
        
        elif key.lower() == "q":
            return None


def navigate_shop_buy(
    items: list[dict],
    player_coins: int,
    player,
) -> int | None:
    """Menu navegável para comprar itens na loja com split view.
    
    Args:
        items: Lista de {"item": Item, "price": int}.
        player_coins: Moedas do jogador.
        player: Objeto do jogador para status.
    
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
        
        # Painel do meio - Detalhes do item selecionado
        selected_item = items[current_index]["item"]
        details_content = build_item_details(selected_item)
        middle_panel = Panel(details_content, border_style="cyan", title="[cyan]DETALHES[/cyan]", width=40)
        
        # Painel direito - Status do jogador com bônus do item
        status_content = build_player_status(player, selected_item)
        right_panel = Panel(status_content, border_style="green", title="[green]STATUS[/green]", width=40)
        
        # Criar tabela com três painéis
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("left", justify="left", width=38)
        table.add_column("middle", justify="left", width=42)
        table.add_column("right", justify="left", width=42)
        table.add_row(left_panel, middle_panel, right_panel)
        
        # Rodapé
        footer = Panel(
            "[dim]W/S navegar | ENTER comprar | [Q] voltar[/dim]",
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
        
        elif key.lower() == "q":
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
        panel_content += "\n[dim]W/S navegar | ENTER vender | [Q] voltar[/dim]"
        
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
        
        elif key.lower() == "q":
            return None


def navigate_inventory(
    inventory: list,
    player,
    equipped_indices: list[int],
) -> int | bool:
    """Menu navegável para selecionar item do inventário com 3 painéis.
    
    Args:
        inventory: Lista de itens no inventário (original, não ordenada).
        player: Objeto do jogador (para status e equipamentos).
        equipped_indices: Parâmetro legado (não usado mais).
    
    Returns:
        int: índice selecionado (para detalhes).
        None: ação realizada (equipar/usar) - precisa recarregar.
        False: ESC pressionado - sair.
    """
    from rich.panel import Panel
    from rich.table import Table
    
    # Ordering: Equipables first (by slot), then Usables (by effect), then Others
    SLOT_ORDER = {"Weapon": 1, "Helmet": 2, "Body": 3, "Legs": 4, "Shoes": 5, "Hands": 6, "Amulet": 7, "Ring": 8}
    EFFECT_ORDER = {"max_hp": 1, "max_mp": 2, "strength": 3, "defense": 4, "agility": 5, "speed": 6, "evasion": 7, "crit_chance": 8, "crit_damage": 9, "life_steal": 10, "mana_regen": 11}
    
    def get_item_sort_key(item):
        slot = getattr(item, "slot", None)
        is_equippable = slot is not None
        is_usable = getattr(item, "is_usable", False)
        
        # Category: 1=Equippable, 2=Usable, 3=Other
        if is_equippable:
            category = 1
            slot_order = SLOT_ORDER.get(slot, 99)
        elif is_usable:
            category = 2
            slot_order = EFFECT_ORDER.get(getattr(item, "effect_type", ""), 99)
        else:
            category = 3
            slot_order = 99
        
        # Within category, sort by rarity (Common < Rare < Epic < Legendary)
        rarity_order = {"Common": 0, "Rare": 1, "Epic": 2, "Legendary": 3}.get(getattr(item, "rarity", "Common"), 99)
        
        return (category, slot_order, rarity_order, item.name)
    
    # Sort inventory
    sorted_inventory = sorted(inventory, key=get_item_sort_key)
    
    # Remove duplicates by id (keep first occurrence)
    seen_ids = set()
    unique_inventory = []
    for item in sorted_inventory:
        if id(item) not in seen_ids:
            seen_ids.add(id(item))
            unique_inventory.append(item)
    sorted_inventory = unique_inventory
    
    # Build equipped items set (for O(1) lookup)
    equipped_items = set()
    for equipped_item in player.equipment.values():
        if equipped_item:
            equipped_items.add(id(equipped_item))
    
    current_index = 0
    max_visible = 10
    total_items = len(sorted_inventory)
    total_pages = (total_items + max_visible - 1) // max_visible if total_items > 0 else 1
    current_page = 0
    
    feedback_message = ""
    pending_action = None  # For Epic+ confirmation
    
    def build_item_details(item, equipped_in_slot=None) -> str:
        """Constrói o conteúdo do painel de detalhes do item."""
        content = f"[bold]Nome:[/bold] {escape_markup(item.name)}\n\n"
        content += f"[bold]Descrição:[/bold]\n{escape_markup(item.description)}\n\n"
        
        slot_name = getattr(item, "slot", "Unknown")
        content += f"[bold]Tipo:[/bold] {slot_name}\n"
        
        damage = getattr(item, "damage_bonus", 0)
        defense = getattr(item, "defense_bonus", 0)
        
        is_equippable = slot_name != "Unknown"
        is_usable = getattr(item, "is_usable", False)
        
        # Comparison with equipped
        if equipped_in_slot:
            content += "[bold cyan]Ao equipar:[/bold cyan]\n"
            equip_damage = getattr(equipped_in_slot, "damage_bonus", 0)
            equip_defense = getattr(equipped_in_slot, "defense_bonus", 0)
            
            if damage > 0:
                diff = damage - equip_damage
                arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
                color = "green" if diff > 0 else "red" if diff < 0 else "white"
                content += f"[bold]Dano:[/bold] +{damage} [{color}]{arrow} {abs(diff)}[/{color}] (atual:+{equip_damage})\n"
            if defense > 0:
                diff = defense - equip_defense
                arrow = "↑" if diff > 0 else "↓" if diff < 0 else "="
                color = "green" if diff > 0 else "red" if diff < 0 else "white"
                content += f"[bold]Defesa:[/bold] +{defense} [{color}]{arrow} {abs(diff)}[/{color}] (atual:+{equip_defense})\n"
        else:
            if damage > 0:
                content += f"[bold]Dano:[/bold] +{damage}\n"
            if defense > 0:
                content += f"[bold]Defesa:[/bold] +{defense}\n"
        
        effect_type = getattr(item, "effect_type", None)
        effect_value = getattr(item, "effect_value", 0)
        if effect_type and effect_value:
            content += f"[bold]Efeito:[/bold] {effect_type} +{effect_value}\n"
        
        rarity = getattr(item, "rarity", "Common")
        if rarity in ("Epic", "Legendary"):
            content += f"[bold]Raridade:[/bold] [{'magenta' if rarity == 'Epic' else 'yellow'}]{rarity}[/]\n"
        else:
            content += f"[bold]Raridade:[/bold] {rarity}\n"
        
        classes = getattr(item, "classes", None)
        if classes:
            classes_str = ", ".join(classes)
        else:
            classes_str = "Todas"
        content += f"[bold]Classes:[/bold] {classes_str}\n"
        
        # Show action hints - only for actually usable items (potions)
        if is_equippable:
            content += "\n[dim][E] para equipar[dim]\n"
        elif is_usable:
            content += "\n[dim][U] para usar[dim]\n"
        
        return content
    
    def build_player_status(player, selected_item=None) -> str:
        """Constrói o conteúdo do painel de status do jogador."""
        content = f"[bold]Classe:[/bold] {player.get_classname()}\n"
        content += f"[bold]Nível:[/bold] {player.level}\n\n"
        
        content += f"[red]HP:[/red] {player.get_hp()}/{player.base_hp}\n"
        content += f"[blue]MP:[/blue] {player.get_mp()}/{player.base_mp}\n\n"
        
        # Calculate base stats
        current_atk = player.avg_damage + player.get_passive_bonus('strength')
        current_def = player.base_df + player.get_passive_bonus('defense')
        
        # Calculate bonus from selected item (compared to currently equipped)
        atk_bonus = 0
        def_bonus = 0
        if selected_item:
            selected_slot = getattr(selected_item, "slot", None)
            equipped_item = player.equipment.get(selected_slot) if selected_slot else None
            
            if selected_slot == "Weapon":
                new_damage = getattr(selected_item, "damage_bonus", 0)
                equipped_damage = getattr(equipped_item, "damage_bonus", 0) if equipped_item else 0
                atk_bonus = new_damage - equipped_damage
            elif selected_slot in ("Helmet", "Body", "Legs", "Shoes", "Hands", "Amulet", "Ring"):
                new_def = getattr(selected_item, "defense_bonus", 0)
                equipped_def = getattr(equipped_item, "defense_bonus", 0) if equipped_item else 0
                def_bonus = new_def - equipped_def
        
        # Display stats with bonuses
        atk_color = "green" if atk_bonus > 0 else "white" if atk_bonus == 0 else "red"
        def_color = "green" if def_bonus > 0 else "white" if def_bonus == 0 else "red"
        
        if atk_bonus != 0:
            content += f"[bold]ATK:[/bold] {current_atk} [{atk_color}]({atk_bonus:+d})[/{atk_color}]\n"
        else:
            content += f"[bold]ATK:[/bold] {current_atk}\n"
        
        if def_bonus != 0:
            content += f"[bold]DEF:[/bold] {current_def} [{def_color}]({def_bonus:+d})[/{def_color}]\n"
        else:
            content += f"[bold]DEF:[/bold] {current_def}\n"
        
        content += f"[bold]AGI:[/bold] {player.base_ag}\n\n"
        
        content += f"[bold]Ouro:[/bold] {player.coins}\n\n"
        
        content += "[bold]Equipamentos:[/bold]\n"
        slot_names = {
            "Weapon": "Arma", "Helmet": "Elmo", "Body": "Armadura",
            "Legs": "Perneiras", "Shoes": "Botas", "Hands": "Mãos",
            "Amulet": "Amuleto", "Ring": "Anel",
        }
        
        selected_slot = getattr(selected_item, "slot", None) if selected_item else None
        
        for slot, equipped_item in player.equipment.items():
            slot_label = slot_names.get(slot, slot)
            
            if equipped_item:
                # Check if this slot will be replaced
                if slot == selected_slot:
                    content += f"  [{slot_label}] {escape_markup(equipped_item.name)} [yellow]← será trocado[yellow]\n"
                else:
                    content += f"  [{slot_label}] {escape_markup(equipped_item.name)}\n"
            else:
                # Check if selected item could fill this slot
                if selected_slot == slot:
                    content += f"  [{slot_label}] [green]← upgrade![green]\n"
                else:
                    content += f"  [{slot_label}] [dim]Vazio[dim]\n"
        
        return content
    
    def build_active_effects_content(player) -> str:
        """Constrói o conteúdo do painel de efeitos ativos."""
        active_buffs = getattr(player, "active_buffs", {})
        
        if not active_buffs:
            return "[dim]Nenhum efeito ativo[/dim]\n"
        
        content = "[bold yellow]EFEITOS ATIVOS[/bold yellow]\n"
        content += "[dim]" + "=" * 25 + "[/dim]\n\n"
        
        for buff_name, buff_data in active_buffs.items():
            value = buff_data.get("value", 0)
            duration = buff_data.get("duration", 0)
            
            stat_map = {
                "Força Aumentada": "FOR",
                "Defesa Aumentada": "DEF",
                "Agilidade Aumentada": "AGI",
                "Velocidade Aumentada": "VEL",
                "Evasão Aumentada": "EVA",
                "Chance de Crítico": "CRIT%",
                "Dano Crítico": "CRITD",
                "Roubo de Vida": "LS",
                "Regeneração de Mana": "MPREG",
                "Grito de Guerra": "FOR",
                "Cortina de Fumaça": "AGI",
            }
            
            stat_label = stat_map.get(buff_name, "")
            content += f"[green]+{value}[/green] {stat_label} ({buff_name[:12]}) "
            content += f"[cyan]⏱{duration}[/cyan]\n"
        
        return content
    
    # Main loop
    iteration = 0
    while True:
        iteration += 1
        
        # Clear console with better compatibility
        try:
            import sys
            # Use ANSI escape sequence to clear screen and move cursor to top
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
        except:
            pass
        renderer.console.clear()
        
        # Debug: print iteration number (remove in production)
        # print(f"DEBUG iteration: {iteration}")
        
        start_idx = current_page * max_visible
        end_idx = min(start_idx + max_visible, total_items)
        visible_items = sorted_inventory[start_idx:end_idx]
        
        # Painel esquerdo - Lista de itens (ou mensagem de vazio)
        left_content = "[bold yellow]INVENTÁRIO[/bold yellow]\n"
        left_content += "[dim]" + "=" * 35 + "[/dim]\n\n"
        
        if total_items == 0:
            left_content += "[dim]Inventário vazio[/dim]\n"
            left_content += "\n[dim]Você pode ver seu status.[/dim]\n"
        else:
            for i, item in enumerate(visible_items):
                real_index = start_idx + i
                
                prefix = ">" if real_index == current_index else " "
                is_equipped = id(item) in equipped_items
                equipped_mark = "[bold green] (E)[/bold green]" if is_equipped else ""
                
                left_content += f"{prefix} [{real_index + 1:2}] {escape_markup(item.name)}{equipped_mark}\n"
            
            if total_pages > 1:
                left_content += f"\n[dim]Página {current_page + 1}/{total_pages}[/dim]\n"
        
        left_panel = Panel(left_content, border_style="cyan", title="[cyan]INVENTÁRIO[/cyan]", width=40)
        
        # Painel do meio - Detalhes do item
        if total_items == 0:
            middle_content = "[dim]Selecione um item[/dim]\n"
        else:
            selected_item = sorted_inventory[current_index]
            equipped_in_slot = player.equipment.get(getattr(selected_item, "slot", None))
            middle_content = build_item_details(selected_item, equipped_in_slot)
        
        middle_panel = Panel(middle_content, border_style="yellow", title="[yellow]DETALHES[/yellow]", width=40)
        
        # Painel direito - Status do jogador
        selected_for_status = sorted_inventory[current_index] if total_items > 0 else None
        status_content = build_player_status(player, selected_for_status)
        right_panel = Panel(status_content, border_style="green", title="[green]STATUS[/green]", width=40)
        
        # Painel 4 - Efeitos ativos (condicional)
        active_buffs = getattr(player, "active_buffs", {})
        if active_buffs:
            effects_content = build_active_effects_content(player)
            effects_panel = Panel(effects_content, border_style="magenta", title="[magenta]BUFFS[/magenta]", width=40)
        else:
            effects_panel = None
        
        # Criar tabela com 3 ou 4 painéis
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("left", justify="left", width=42)
        table.add_column("middle", justify="left", width=42)
        table.add_column("right", justify="left", width=42)
        
        if effects_panel:
            table.add_column("effects", justify="left", width=42)
            table.add_row(left_panel, middle_panel, right_panel, effects_panel)
        else:
            table.add_row(left_panel, middle_panel, right_panel)
        
        renderer.console.print(table)
        
        # Rodapé com opções
        if pending_action == "use_confirm":
            footer_content = "[yellow]⚠️ Item épico — confirme o uso[/yellow]\n[U] Confirmar  [ESC] Cancelar"
        elif total_items == 0:
            footer_content = "[dim]W/S para navegar | ESC sair[dim]"
        else:
            selected_item = sorted_inventory[current_index]
            is_equippable = hasattr(selected_item, "slot")
            is_usable = getattr(selected_item, "is_usable", False)
            is_epic = getattr(selected_item, "rarity", "Common") in ("Epic", "Legendary")
            
            if is_equippable:
                footer_content = "[E] Equipar  [Q] Sair  |  W/S navegar"
            elif is_usable and is_epic:
                footer_content = "[U] Usar (risco)  [Q] Sair  |  W/S navegar"
            elif is_usable:
                footer_content = "[U] Usar  [Q] Sair  |  W/S navegar"
            else:
                footer_content = "[Q] Sair  |  W/S navegar"
        
        if feedback_message:
            # Red for errors (contains "não pode"), green for success
            if "não pode" in feedback_message.lower():
                footer_content += f"\n[red]{feedback_message}[/red]"
            else:
                footer_content += f"\n[green]{feedback_message}[/green]"
        
        footer_panel = Panel(footer_content, border_style="dim")
        renderer.console.print(footer_panel)
        
        key = get_key()
        
        if pending_action == "use_confirm":
            if key.lower() == "q":
                pending_action = None
                feedback_message = ""
            elif key in ("u", "U"):
                # Confirm use
                selected_item = sorted_inventory[current_index]
                from src.content.items import Item
                if isinstance(selected_item, Item):
                    msg = player.use_potion(selected_item)
                    feedback_message = f"{selected_item.name} usado."
                # Reload inventory
                return None  # Exit to refresh
            continue
        
        # Handle navigation
        if key in ("w", "W"):
            current_index -= 1
            if current_index < 0:
                current_index = total_items - 1
            if total_items > 0 and current_index // max_visible != current_page:
                current_page = current_index // max_visible
            feedback_message = ""
        
        elif key in ("s", "S"):
            current_index += 1
            if total_items > 0 and current_index >= total_items:
                current_index = 0
            if total_items > 0 and current_index // max_visible != current_page:
                current_page = current_index // max_visible
            feedback_message = ""
        
        elif key in ("e", "E") and total_items > 0:
            selected_item = sorted_inventory[current_index]
            if hasattr(selected_item, "slot"):
                is_equipped = id(selected_item) in equipped_items
                if is_equipped:
                    slot = _find_equipped_slot_by_item(player, selected_item)
                    if slot:
                        player.unequip(slot)
                        feedback_message = f"{selected_item.name} desequipado."
                else:
                    msg = player.equip(selected_item)
                    if "não pode" in msg.lower() or "não pode" in str(msg).lower():
                        feedback_message = msg
                    else:
                        feedback_message = f"{selected_item.name} equipado."
                # Reload and rebuild
                return None  # Exit to refresh
        
        elif key in ("u", "U") and total_items > 0:
            selected_item = sorted_inventory[current_index]
            is_usable = getattr(selected_item, "is_usable", False)
            rarity = getattr(selected_item, "rarity", "Common")
            
            if is_usable:
                if rarity in ("Epic", "Legendary"):
                    pending_action = "use_confirm"
                    feedback_message = "⚠️ Item épico — confirme o uso"
                else:
                    from src.content.items import Item
                    if isinstance(selected_item, Item):
                        msg = player.use_potion(selected_item)
                        feedback_message = f"{selected_item.name} usado."
                    return None  # Exit to refresh
        
        elif key.lower() == "q":
            return False  # ESC means exit the inventory


def _get_rarity_color(rarity: str) -> str:
    """Retorna a cor Rich para a raridade."""
    colors = {
        "Common": "white",
        "Rare": "cyan",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    return colors.get(rarity, "white")