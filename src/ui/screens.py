"""Funções puras de renderização de telas (Rich apenas, sem lógica de fluxo).

Toda lógica de interação (loops, input) está em ui/shop_flow.py e ui/inventory_flow.py.
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.ui import renderer

if TYPE_CHECKING:
    from src.entities.base import Entity
    from src.entities.heroes import Player
    from src.entities.monsters import Monster


def menu(options: tuple[str, ...] | list[str], prompt: str) -> None:
    renderer.render_menu(options, prompt)


def render_fight_intro(player: "Player", monster: "Monster") -> None:
    renderer.console.clear()
    renderer.console.print(
        Panel(Text("--- Início da Batalha ---", justify="center", style="bold green"), border_style="green")
    )
    renderer.render_compare_opponents(player, monster)
    renderer.render_battle_start_prompt()


def render_turn_banner(attacker: "Entity") -> None:
    color = "blue" if attacker.my_type() == "Human" else "magenta"
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"É a vez de [bold {color}]{attacker.get_nick_name()}[/bold {color}].",
                justify="center",
                style="white",
            ),
            border_style="blue",
        )
    )
    sleep(0.5)


def render_battle_frame(player: "Player", monster: "Monster") -> None:
    renderer.render_battle_frame(player, monster)


def render_battle_action_panel() -> None:
    action_menu_table = Table(show_header=False, expand=True, border_style="dim white")
    action_menu_table.add_column("Opção", style="bold blue", justify="right")
    action_menu_table.add_column("Descrição", style="cyan")
    action_menu_table.add_row("1.", "Ataque Normal")
    action_menu_table.add_row("2.", "Habilidades")
    action_menu_table.add_row("3.", "Usar Item")
    action_menu_table.add_row("4.", "Tentar Fugir")
    renderer.console.print(
        Panel(action_menu_table, title="[bold yellow]Escolha sua ação[/bold yellow]", border_style="yellow")
    )


def render_battle_no_skills_message() -> None:
    renderer.console.print(
        Panel(Text("Você não tem habilidades para usar!", justify="center", style="red"), border_style="red")
    )


def render_skill_select_panel(player: "Player") -> None:
    skill_table = Table(show_header=False, expand=True, border_style="dim white")
    skill_table.add_column("Chave", style="bold blue", justify="right")
    skill_table.add_column("Habilidade", style="cyan")
    skill_table.add_column("Custo", style="magenta", justify="left")
    for key, skill in player.skills.items():
        skill_table.add_row(str(key) + ".", skill.name, f"{skill.mana_cost} MP")
    skill_table.add_row("0.", "Voltar", "")
    renderer.console.print(
        Panel(skill_table, title="[bold yellow]Escolha uma habilidade[/bold yellow]", border_style="yellow")
    )


def render_battle_insufficient_mana_message() -> None:
    renderer.console.print(Panel(Text("Mana insuficiente!", justify="center", style="red"), border_style="red"))


def render_battle_no_potions_message() -> None:
    renderer.console.print(
        Panel(Text("Você não tem poções para usar!", justify="center", style="red"), border_style="red")
    )


def render_potion_select_panel(potions: list[object]) -> None:
    potion_table = Table(show_header=False, expand=True, border_style="dim white")
    potion_table.add_column("Chave", style="bold blue", justify="right")
    potion_table.add_column("Poção", style="cyan")
    potion_table.add_column("Descrição", style="dim white")
    for i, potion in enumerate(potions, 1):
        potion_table.add_row(str(i) + ".", getattr(potion, "name", "?"), getattr(potion, "description", ""))
    potion_table.add_row("0.", "Voltar", "")
    renderer.console.print(
        Panel(potion_table, title="[bold yellow]Escolha uma poção[/bold yellow]", border_style="yellow")
    )


def render_battle_invalid_potion_message() -> None:
    renderer.console.print(
        Panel(Text("Escolha inválida de poção!", justify="center", style="red"), border_style="red")
    )


def render_post_battle(
    player_name: str,
    monster_name: str,
    xp_gained: int,
    player_won: bool,
    dropped_item_name: str | None,
    level_up_messages: list[str],
    coins_gained: int = 0,
    essence_multiplier: float = 1.0,
) -> None:
    """
    Renderiza tela de pós-batalha (puramente visual - dumb UI).

    Todos os dados (XP ganho, loot, moedas, mensagens) devem ser calculados
    e passados pela camada de engine. Esta função apenas exibe.
    """
    if not player_won:
        renderer.console.print(
            Panel(Text("Você foi derrotado...", justify="center", style="bold red"), border_style="red")
        )
    else:
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"Você derrotou [bold magenta]{monster_name}[/bold magenta]!",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )

    # Exibir XP e moedas ganhadas com multiplicador
    mult_text = f" (×{essence_multiplier})" if essence_multiplier != 1.0 else ""
    rewards_text = f"XP ganho: [bold cyan]{xp_gained}{mult_text}[/bold cyan]"
    if coins_gained > 0:
        rewards_text += f" | Moedas: [bold yellow]{coins_gained}[/bold yellow]"

    renderer.console.print(
        Panel(
            Text.from_markup(rewards_text, justify="center"),
            border_style="cyan",
        )
    )

    # Exibir loot se houver
    if dropped_item_name:
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"Você encontrou [bold yellow]{dropped_item_name}[/bold yellow]!",
                    justify="center",
                    style="yellow",
                ),
                border_style="yellow",
                width=80,
            )
        )

    # Exibir mensagens de level up
    for msg in level_up_messages:
        renderer.console.print(
            Panel(Text(msg, justify="center", style="bold blue"), border_style="blue")
        )


# =============================================================================
# LOJA - Funções puras de renderização
# =============================================================================


def render_shop_main(shop: object, player_coins: int) -> None:
    """Renderiza a tela principal da loja."""

    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Bem-vindo à Loja do Mercador!", justify="center", style="bold green"),
            border_style="green",
            subtitle=f"Seu Ouro: [bold yellow]{player_coins}[/bold yellow]",
        )
    )

    shop_options = {"1": "Comprar Itens", "2": "Vender Itens", "3": "Sair da Loja"}

    options_table = Table(show_header=False, expand=True, highlight=True, row_styles=["none", "dim"])
    options_table.add_column("Opção", style="bold blue", justify="right")
    options_table.add_column("Descrição", style="cyan")

    for key, value in shop_options.items():
        options_table.add_row(key, value)

    renderer.console.print(options_table)
    renderer.console.print("\n")


def render_shop_buy_menu(items_for_sale: list[dict], player_coins: int) -> None:
    """Renderiza o menu de compra de itens."""
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Itens à Venda", justify="center", style="bold cyan"),
            border_style="cyan",
            subtitle=f"Seu Ouro: [bold yellow]{player_coins}[/bold yellow]",
        )
    )

    if not items_for_sale:
        renderer.console.print(
            Panel(
                Text("O mercador não tem nada para vender no momento.", justify="center", style="dim white"),
                border_style="dim white",
            )
        )
        sleep(0.8)
        return

    item_table = Table(show_header=True, expand=True, border_style="dim white")
    item_table.add_column("ID", style="bold blue")
    item_table.add_column("Item", style="cyan")
    item_table.add_column("Preço", style="yellow", justify="right")
    item_table.add_column("Descrição", style="dim white")

    for i, item_data in enumerate(items_for_sale, 1):
        item = item_data["item"]
        price = item_data["price"]
        item_table.add_row(str(i), item.name, str(price), getattr(item, "description", "Sem descrição"))
    item_table.add_row("0", "Voltar", "", "")

    renderer.console.print(item_table)
    renderer.console.print("\n")


def render_shop_purchase_success(item_name: str, price: int) -> None:
    """Renderiza mensagem de compra bem-sucedida."""
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"Você comprou [bold green]{item_name}[/bold green] por [bold yellow]{price}[/bold yellow] ouro.",
                justify="center",
                style="green",
            ),
            border_style="green",
        )
    )
    sleep(0.8)


def render_shop_insufficient_gold() -> None:
    """Renderiza mensagem de ouro insuficiente."""
    renderer.console.print(
        Panel(
            Text("Você não tem ouro suficiente para comprar este item.", justify="center", style="red"),
            border_style="red",
        )
    )
    sleep(0.8)


def render_shop_sell_menu(
    inventory: list, shop: object, dungeon_level: int, player_coins: int
) -> None:
    """Renderiza o menu de venda de itens."""
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Seus Itens para Venda", justify="center", style="bold magenta"),
            border_style="magenta",
            subtitle=f"Seu Ouro: [bold yellow]{player_coins}[/bold yellow]",
        )
    )

    if not inventory:
        renderer.console.print(
            Panel(Text("Você não tem itens para vender.", justify="center", style="dim white"), border_style="dim white")
        )
        sleep(0.8)
        return

    player_inventory_table = Table(show_header=True, expand=True, border_style="dim white")
    player_inventory_table.add_column("ID", style="bold blue")
    player_inventory_table.add_column("Item", style="cyan")
    player_inventory_table.add_column("Preço Venda", style="yellow", justify="right")
    player_inventory_table.add_column("Descrição", style="dim white")

    for i, item in enumerate(inventory, 1):
        sell_price = int(shop.get_price(item, dungeon_level) * 0.5)
        player_inventory_table.add_row(str(i), item.name, str(sell_price), getattr(item, "description", "Sem descrição"))
    player_inventory_table.add_row("0", "Voltar", "", "")

    renderer.console.print(player_inventory_table)
    renderer.console.print("\n")


def render_shop_sell_success(item_name: str, sell_price: int) -> None:
    """Renderiza mensagem de venda bem-sucedida."""
    renderer.console.print(
        Panel(
            Text(
                f"Você vendeu [bold green]{item_name}[/bold green] por [bold yellow]{sell_price}[/bold yellow] ouro.",
                justify="center",
                style="green",
            ),
            border_style="green",
        )
    )
    sleep(0.8)


def render_shop_invalid_choice() -> None:
    """Renderiza mensagem de escolha inválida na loja."""
    renderer.console.print(
        Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="red"), border_style="red")
    )
    sleep(0.8)


def render_shop_farewell() -> None:
    """Renderiza mensagem de despedida da loja."""
    renderer.console.print(
        Panel(
            Text("Você se despede do mercador e volta à aventura.", justify="center", style="dim white"),
            border_style="dim white",
        )
    )
    sleep(0.8)


# =============================================================================
# INVENTÁRIO - Funções puras de renderização
# =============================================================================


def _create_inventory_header_panel(player: "Player") -> Panel:
    """Cria o painel de cabeçalho do inventário."""
    return Panel(
        Text("Mochila e Equipamentos", justify="center", style="bold green"),
        border_style="green",
        subtitle=f"Ouro: [bold yellow]{player.coins}[/bold yellow]"
    )


def _create_equipment_table(player: "Player") -> Table:
    """Cria a tabela de equipamentos do jogador."""
    equip_table = Table(
        title="[bold cyan]--- Equipamento ---[/bold cyan]",
        show_header=False,
        expand=True,
        border_style="dim cyan"
    )
    equip_table.add_column("Slot", style="bold blue")
    equip_table.add_column("Item", style="cyan")

    for slot, item in player.equipment.items():
        if item:
            equip_table.add_row(slot.capitalize(), item.name)
        else:
            equip_table.add_row(slot.capitalize(), "[dim]Vazio[/dim]")

    return equip_table


def _create_inventory_table(player: "Player") -> Table | None:
    """Cria a tabela de itens na mochila. Retorna None se o inventário estiver vazio."""
    if not player.inventory:
        return None

    inv_table = Table(
        title="[bold magenta]--- Itens na Mochila ---[/bold magenta]",
        show_header=True,
        expand=True,
        border_style="dim magenta"
    )
    inv_table.add_column("ID", style="bold blue", justify="right")
    inv_table.add_column("Item", style="cyan")
    inv_table.add_column("Tipo", style="yellow")

    for i, item in enumerate(player.inventory):
        inv_table.add_row(str(i + 1), item.name, item.__class__.__name__)

    return inv_table


def _render_empty_inventory_message() -> None:
    """Renderiza mensagem de inventário vazio."""
    renderer.console.print(
        Panel(
            Text("Sua mochila está vazia.", justify="center", style="dim white"),
            border_style="dim white"
        )
    )


def render_dungeon_status(
    dungeon_level: int, hp: int, max_hp: int, mp: int, max_mp: int,
    essence_multiplier: float = 1.0,
) -> None:
    """Renderiza o status da masmorra na parte superior da tela."""
    # Determina a cor do multiplicador baseado no valor
    if essence_multiplier < 0.8:
        mult_color = "red"
    elif essence_multiplier > 1.5:
        mult_color = "green"
    else:
        mult_color = "yellow"

    status_text = (
        f"Masmorra Nível {dungeon_level} | "
        f"Multiplicador: [{mult_color}]{essence_multiplier}x[/] | "
        f"HP: {hp}/{max_hp} | MP: {mp}/{max_mp}"
    )
    renderer.console.print(Text(status_text, style="bold cyan"))
    renderer.console.print(Text("Use 'w', 'a', 's', 'd' para mover.", style="dim"))


def render_dungeon_controls() -> None:
    """Renderiza os controles disponíveis no mapa."""
    renderer.console.print("\n[dim](i)nventário | (p)ara Salvar | (q) para Sair[/dim]")


def render_game_saved(message: str = "Jogo salvo!") -> None:
    """Renderiza mensagem de confirmação de salvamento."""
    renderer.console.print(Panel(Text(message, justify="center", style="green"), border_style="green"))
    sleep(0.8)


def render_level_complete(dungeon_level: int) -> None:
    """Renderiza mensagem de conclusão de nível."""
    renderer.console.print(Panel(
        Text(f"Você completou a Masmorra Nível {dungeon_level}!", justify="center", style="bold green"),
        border_style="green"
    ))
    renderer.console.print(Panel(
        Text("Pressione qualquer tecla para avançar para o próximo nível...", justify="center", style="yellow"),
        border_style="yellow"
    ))


def render_continue_prompt() -> None:
    """Renderiza prompt para continuar jornada."""
    renderer.console.print(Panel(
        Text("Pressione qualquer tecla para continuar sua jornada...", justify="center", style="yellow"),
        border_style="yellow"
    ))


def render_map(map_lines: list[str]) -> None:
    """Renderiza as linhas do mapa no console com cores."""
    from rich.text import Text
    
    for line in map_lines:
        colored_line = Text()
        for char in line:
            if char == '@':
                colored_line.append(char, style="bold green")
            elif char == '&':
                colored_line.append(char, style="bold red")
            elif char == 'B':
                colored_line.append(char, style="bold magenta")
            elif char == 'X':
                colored_line.append(char, style="dim")
            elif char == 'D':
                colored_line.append(char, style="bold yellow")
            else:
                colored_line.append(char, style="white")
        renderer.console.print(colored_line)


def render_passive_selection(choices: list) -> None:
    """Renderiza as 3 cartas de passivas para escolha."""
    rarity_colors = {
        "Common": "white",
        "Rare": "blue",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Escolha uma Passiva Permanente", justify="center", style="bold cyan"),
            border_style="cyan",
        )
    )
    for i, card in enumerate(choices, 1):
        color = rarity_colors.get(getattr(card, "rarity", "Common"), "white")
        category = getattr(card, "category", "")
        rarity = getattr(card, "rarity", "")
        name = getattr(card, "name", "?")
        description = getattr(card, "description", "")
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"[bold {color}]{name}[/bold {color}]\n"
                    f"[dim]{description}[/dim]"
                ),
                title=f"[bold]{i}. [{rarity}] [{category}][/bold]",
                border_style=color,
            )
        )


def render_passive_acquired(message: str) -> None:
    """Renderiza confirmação de passiva adquirida."""
    renderer.console.print(
        Panel(Text(message, justify="center", style="bold green"), border_style="green")
    )
    sleep(1.5)


def render_skill_selection(choices: list) -> None:
    """Renderiza as 3 cartas de skills para escolha."""
    rarity_colors = {
        "Common": "white",
        "Rare": "blue",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Escolha uma Habilidade", justify="center", style="bold cyan"),
            border_style="cyan",
        )
    )
    for i, card in enumerate(choices, 1):
        color = rarity_colors.get(getattr(card, "rarity", "Common"), "white")
        name = getattr(card, "name", "?")
        rarity = getattr(card, "rarity", "")
        mana_cost = getattr(card, "mana_cost", 0)
        effect_type = getattr(card, "effect_type", "")
        effect_value = getattr(card, "effect_value", 0)
        description = getattr(card, "description", "")

        # Mostra o valor do efeito de forma legível
        if effect_type == "damage":
            effect_text = f"Dano: {effect_value}"
        elif effect_type == "heal":
            effect_text = f"Cura: {effect_value}"
        elif effect_type == "buff":
            effect_text = f"Buff: +{effect_value}"
        elif effect_type == "status":
            effect_text = f"Status: {effect_value}"
        else:
            effect_text = str(effect_value)

        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"[bold {color}]{name}[/bold {color}]\n"
                    f"[dim]Custo: {mana_cost} MP | {effect_text}[/dim]\n"
                    f"[dim]{description}[/dim]"
                ),
                title=f"[bold]{i}. [{rarity}][/bold]",
                border_style=color,
            )
        )
    renderer.console.print(
        Panel(
            Text("Pressione 0 para cancelar", justify="center", style="dim"),
            border_style="dim"
        )
    )



def render_skill_replacement_choice(player: "Player", new_skill: object) -> None:
    """Renderiza a nova skill e pede para escolher qual das 4 atuais substituir."""
    rarity_colors = {
        "Common": "white",
        "Rare": "blue",
        "Epic": "magenta",
        "Legendary": "yellow",
    }
    renderer.console.clear()

    # Mostra a nova skill
    rarity = getattr(new_skill, "rarity", "Common")
    color_new = rarity_colors.get(rarity, "white")
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"[bold]Nova Habilidade:[/bold]\n"
                f"[bold {color_new}]{new_skill.name}[/bold {color_new}]\n"
                f"[dim]Custo: {new_skill.mana_cost} MP | {new_skill.description}[/dim]"
            ),
            title="[bold green]Nova Skill[/bold green]",
            border_style="green",
        )
    )

    # Mostra as 4 skills atuais
    renderer.console.print(
        Panel(
            Text("Escolha qual skill substituir (1-4) ou 0 para cancelar:", justify="center", style="bold yellow"),
            border_style="yellow",
        )
    )

    skill_keys = [k for k in player.skills if k <= 4]
    for key in sorted(skill_keys):
        skill = player.skills[key]
        rarity = getattr(skill, "rarity", "Common")
        color = rarity_colors.get(rarity, "white")
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"[bold {color}]{key}. {skill.name}[/bold {color}]\n"
                    f"[dim]Custo: {skill.mana_cost} MP | {skill.description}[/dim]"
                ),
                border_style=color,
            )
        )

    renderer.console.print(
        Panel(
            Text("0. Cancelar", justify="left", style="dim"),
            border_style="dim",
        )
    )


def render_skill_acquired(message: str) -> None:
    """Renderiza confirmação de skill adquirida/substituída."""
    renderer.console.print(
        Panel(Text(message, justify="center", style="bold green"), border_style="green")
    )
    sleep(1.5)


def render_skill_not_replaced() -> None:
    """Renderiza mensagem de que a skill não foi substituída."""
    renderer.console.print(
        Panel(Text("Skill não substituída.", justify="center", style="bold yellow"), border_style="yellow")
    )
    sleep(1.0)
