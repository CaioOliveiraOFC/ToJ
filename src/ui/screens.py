"""Funções puras de renderização de telas (Rich apenas, sem lógica de fluxo).

Toda lógica de interação (loops, input) foi movida para engine/shop_flow.py e engine/inventory_flow.py.
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.content.items import Armor, Potion, Weapon
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
    sleep(1)


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


def render_potion_select_panel(potions: list[Potion]) -> None:
    potion_table = Table(show_header=False, expand=True, border_style="dim white")
    potion_table.add_column("Chave", style="bold blue", justify="right")
    potion_table.add_column("Poção", style="cyan")
    potion_table.add_column("Descrição", style="dim white")
    for i, potion in enumerate(potions, 1):
        potion_table.add_row(str(i) + ".", potion.name, potion.description)
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
) -> None:
    """
    Renderiza tela de pós-batalha (puramente visual - dumb UI).

    Todos os dados (XP ganho, loot, mensagens) devem ser calculados
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

    # Exibir XP ganhado
    renderer.console.print(
        Panel(
            Text(f"XP ganho: {xp_gained}", justify="center", style="cyan"),
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
        sleep(1.5)
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
            Text(
                f"Você comprou [bold green]{item_name}[/bold green] por [bold yellow]{price}[/bold yellow] ouro.",
                justify="center",
                style="green",
            ),
            border_style="green",
        )
    )
    sleep(1.5)


def render_shop_insufficient_gold() -> None:
    """Renderiza mensagem de ouro insuficiente."""
    renderer.console.print(
        Panel(
            Text("Você não tem ouro suficiente para comprar este item.", justify="center", style="red"),
            border_style="red",
        )
    )
    sleep(1.5)


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
        sleep(1.5)
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
    sleep(1.5)


def render_shop_invalid_choice() -> None:
    """Renderiza mensagem de escolha inválida na loja."""
    renderer.console.print(
        Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="red"), border_style="red")
    )
    sleep(1.5)


def render_shop_farewell() -> None:
    """Renderiza mensagem de despedida da loja."""
    renderer.console.print(
        Panel(
            Text("Você se despede do mercador e volta à aventura.", justify="center", style="dim white"),
            border_style="dim white",
        )
    )
    sleep(1.5)


# =============================================================================
# INVENTÁRIO - Funções puras de renderização
# =============================================================================


def render_inventory_main(player: "Player") -> None:
    """Renderiza a tela principal do inventário."""
    renderer.console.clear()

    # Criação do painel principal do inventário
    renderer.console.print(Panel(
        Text("Mochila e Equipamentos", justify="center", style="bold green"),
        border_style="green",
        subtitle=f"Ouro: [bold yellow]{player.coins}[/bold yellow]"
    ))

    renderer.show_status(player)

    # Equipamentos
    equip_table = Table(title="[bold cyan]--- Equipamento ---[/bold cyan]", show_header=False, expand=True, border_style="dim cyan")
    equip_table.add_column("Slot", style="bold blue")
    equip_table.add_column("Item", style="cyan")

    for slot, item in player.equipment.items():
        if item:
            equip_table.add_row(slot.capitalize(), item.name)
        else:
            equip_table.add_row(slot.capitalize(), "[dim]Vazio[/dim]")

    renderer.console.print(equip_table)
    renderer.console.print("\n")

    # Itens na Mochila
    inv_table = Table(title="[bold magenta]--- Itens na Mochila ---[/bold magenta]", show_header=True, expand=True, border_style="dim magenta")
    inv_table.add_column("ID", style="bold blue", justify="right")
    inv_table.add_column("Item", style="cyan")
    inv_table.add_column("Tipo", style="yellow")

    if not player.inventory:
        renderer.console.print(Panel(Text("Sua mochila está vazia.", justify="center", style="dim white"), border_style="dim white"))
    else:
        for i, item in enumerate(player.inventory):
            inv_table.add_row(str(i + 1), item.name, item.__class__.__name__)
        renderer.console.print(inv_table)

    renderer.console.print("\n[dim white](número do item)[/dim white] selecionar | [dim white](x)[/dim white] sair do inventário")


def render_inventory_item_details(item: object, is_equipped: bool) -> None:
    """Renderiza os detalhes de um item do inventário."""
    renderer.console.clear()

    details_table = Table(show_header=False, expand=True, border_style="dim yellow")
    details_table.add_column("Atributo", style="bold cyan")
    details_table.add_column("Valor", style="white")

    details_table.add_row("Nome", item.name)
    if hasattr(item, 'description'):
        details_table.add_row("Descrição", item.description)
    details_table.add_row("Tipo", item.__class__.__name__)

    if isinstance(item, Weapon):
        details_table.add_row("Dano", str(item.damage))
    elif isinstance(item, Armor):
        details_table.add_row("Defesa", str(item.defense))
    elif isinstance(item, Potion):
        details_table.add_row("Tipo de Efeito", getattr(item, 'potion_type', 'Desconhecido'))
        details_table.add_row("Poder de Efeito", f"+{getattr(item, 'effect_value', 0)}")

    renderer.console.print(Panel(details_table, title="[bold yellow]Detalhes do Item[/bold yellow]", border_style="yellow"))

    # Ações
    action_table = Table(show_header=False, expand=True, border_style="dim white")

    if isinstance(item, Potion):
        action_table.add_row("[bold blue]u[/bold blue]", "Usar Poção")

    if isinstance(item, (Weapon, Armor)):
        if is_equipped:
            action_table.add_row("[bold blue]e[/bold blue]", "Desequipar Item")
        else:
            action_table.add_row("[bold blue]e[/bold blue]", "Equipar Item")

    action_table.add_row("[bold blue]c[/bold blue]", "Cancelar")

    renderer.console.print(Panel(action_table, title="[bold cyan]Opções[/bold cyan]", border_style="cyan"))


def render_inventory_item_used(item_name: str) -> None:
    """Renderiza mensagem de item usado."""
    renderer.console.print(Panel(f"Você usou [bold green]{item_name}[/bold green].", border_style="green"))
    sleep(1.5)


def render_inventory_item_equipped(item_name: str) -> None:
    """Renderiza mensagem de item equipado."""
    renderer.console.print(Panel(f"Você equipou [bold green]{item_name}[/bold green].", border_style="green"))
    sleep(1.5)


def render_inventory_item_unequipped(item_name: str) -> None:
    """Renderiza mensagem de item desequipado."""
    renderer.console.print(Panel(f"Você desequipou [bold yellow]{item_name}[/bold yellow].", border_style="yellow"))
    sleep(1.5)


def render_dungeon_status(
    dungeon_level: int, hp: int, max_hp: int, mp: int, max_mp: int
) -> None:
    """Renderiza o status da masmorra na parte superior da tela."""
    from rich.text import Text
    status_text = (
        f"Masmorra Nível {dungeon_level} | "
        f"Herói: @ | Inimigos: & | Saída: X | "
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
    sleep(1.5)


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
    """Renderiza as linhas do mapa no console."""
    for line in map_lines:
        renderer.console.print(line)
