"""Telas, menus e fluxos interativos (Rich + `prompts`)."""

from __future__ import annotations

from time import sleep

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.content.items import Potion
from src.content.shop import Shop
from src.entities.heroes import Player
from src.ui import renderer
from src.ui.prompts import safe_get_key


def menu(options: tuple[str, ...] | list[str], prompt: str) -> None:
    renderer.render_menu(options, prompt)


def render_fight_intro(player, monster) -> None:
    renderer.console.clear()
    renderer.console.print(
        Panel(Text("--- Início da Batalha ---", justify="center", style="bold green"), border_style="green")
    )
    renderer.render_compare_opponents(player, monster)
    renderer.render_battle_start_prompt()


def render_turn_banner(attacker) -> None:
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


def render_battle_frame(player, monster) -> None:
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


def render_skill_select_panel(player) -> None:
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


def render_post_battle(player, monster) -> None:
    from src.content.factories.loot import get_loot
    from src.mechanics.math_operations import calculate_mini_boss_xp_reward, calculate_monster_xp_reward

    xp_base_reward = calculate_monster_xp_reward(monster.level)
    if getattr(monster, "is_boss", False):
        xp_base_reward = calculate_mini_boss_xp_reward(monster.level)

    if not player.get_isalive():
        renderer.console.print(
            Panel(Text("Você foi derrotado...", justify="center", style="bold red"), border_style="red")
        )
        pity_xp = xp_base_reward // 10
        player.add_xp_points(pity_xp)
    else:
        renderer.console.print(
            Panel(
                Text.from_markup(
                    f"Você derrotou [bold magenta]{monster.get_nick_name()}[/bold magenta]!",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )
        player.add_xp_points(xp_base_reward)
        dropped_item = get_loot()
        if dropped_item:
            renderer.console.print(
                Panel(
                    Text.from_markup(
                        f"Você encontrou [bold yellow]{dropped_item.name}[/bold yellow]!",
                        justify="center",
                        style="yellow",
                    ),
                    border_style="yellow",
                    width=80,
                )
            )

    player.level_up(show=True)
    player.rest()


def shop_menu(player: Player, shop: Shop, dungeon_level: int) -> None:
    """Interface da loja (Rich + teclas)."""
    while True:
        renderer.console.clear()
        renderer.console.print(
            Panel(
                Text("Bem-vindo à Loja do Mercador!", justify="center", style="bold green"),
                border_style="green",
                subtitle=f"Seu Ouro: [bold yellow]{player.coins}[/bold yellow]",
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

        choice = safe_get_key(valid_keys=["1", "2", "3"])

        if choice == "1":
            while True:
                renderer.console.clear()
                renderer.console.print(
                    Panel(
                        Text("Itens à Venda", justify="center", style="bold cyan"),
                        border_style="cyan",
                        subtitle=f"Seu Ouro: [bold yellow]{player.coins}[/bold yellow]",
                    )
                )

                items_for_sale = shop.get_available_items(dungeon_level)
                if not items_for_sale:
                    renderer.console.print(
                        Panel(
                            Text("O mercador não tem nada para vender no momento.", justify="center", style="dim white"),
                            border_style="dim white",
                        )
                    )
                    sleep(1.5)
                    break

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

                item_choices = [str(i) for i in range(1, len(items_for_sale) + 1)] + ["0"]
                item_choice = safe_get_key(valid_keys=item_choices)

                if item_choice == "0":
                    break

                try:
                    chosen_item_id = int(item_choice)
                    chosen_item_data = items_for_sale[chosen_item_id - 1]
                    item_to_buy = chosen_item_data["item"]
                    price = chosen_item_data["price"]

                    if player.coins >= price:
                        if shop.buy_item(player, item_to_buy, dungeon_level):
                            renderer.console.print(
                                Panel(
                                    Text(
                                        f"Você comprou [bold green]{item_to_buy.name}[/bold green] por [bold yellow]{price}[/bold yellow] ouro.",
                                        justify="center",
                                        style="green",
                                    ),
                                    border_style="green",
                                )
                            )
                    else:
                        renderer.console.print(
                            Panel(
                                Text("Você não tem ouro suficiente para comprar este item.", justify="center", style="red"),
                                border_style="red",
                            )
                        )
                    sleep(1.5)

                except (ValueError, IndexError):
                    renderer.console.print(
                        Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="red"), border_style="red")
                    )
                    sleep(1.5)

        elif choice == "2":
            while True:
                renderer.console.clear()
                renderer.console.print(
                    Panel(
                        Text("Seus Itens para Venda", justify="center", style="bold magenta"),
                        border_style="magenta",
                        subtitle=f"Seu Ouro: [bold yellow]{player.coins}[/bold yellow]",
                    )
                )

                if not player.inventory:
                    renderer.console.print(
                        Panel(Text("Você não tem itens para vender.", justify="center", style="dim white"), border_style="dim white")
                    )
                    sleep(1.5)
                    break

                player_inventory_table = Table(show_header=True, expand=True, border_style="dim white")
                player_inventory_table.add_column("ID", style="bold blue")
                player_inventory_table.add_column("Item", style="cyan")
                player_inventory_table.add_column("Preço Venda", style="yellow", justify="right")
                player_inventory_table.add_column("Descrição", style="dim white")

                for i, item in enumerate(player.inventory, 1):
                    sell_price = int(shop.get_price(item, dungeon_level) * 0.5)
                    player_inventory_table.add_row(str(i), item.name, str(sell_price), getattr(item, "description", "Sem descrição"))
                player_inventory_table.add_row("0", "Voltar", "", "")

                renderer.console.print(player_inventory_table)
                renderer.console.print("\n")

                sell_choices = [str(i) for i in range(1, len(player.inventory) + 1)] + ["0"]
                sell_choice = safe_get_key(valid_keys=sell_choices)

                if sell_choice == "0":
                    break

                try:
                    chosen_item_id = int(sell_choice)
                    item_to_sell = player.inventory[chosen_item_id - 1]

                    sell_price = int(shop.get_price(item_to_sell, dungeon_level) * 0.5)
                    if shop.sell_item(player, item_to_sell, dungeon_level):
                        renderer.console.print(
                            Panel(
                                Text(
                                    f"Você vendeu [bold green]{item_to_sell.name}[/bold green] por [bold yellow]{sell_price}[/bold yellow] ouro.",
                                    justify="center",
                                    style="green",
                                ),
                                border_style="green",
                            )
                        )
                    sleep(1.5)

                except (ValueError, IndexError):
                    renderer.console.print(
                        Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="red"), border_style="red")
                    )
                    sleep(1.5)

        elif choice == "3":
            renderer.console.print(
                Panel(
                    Text("Você se despede do mercador e volta à aventura.", justify="center", style="dim white"),
                    border_style="dim white",
                )
            )
            sleep(1.5)
            break

        else:
            renderer.console.print(
                Panel(Text("Escolha inválida. Tente novamente.", justify="center", style="bold red"), border_style="red")
            )
            sleep(1.5)
