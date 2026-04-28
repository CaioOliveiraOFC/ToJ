from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.shared.types import CombatResult

console = Console()


def get_hp_bar(entt) -> str:
    if getattr(entt, "base_hp", 0) == 0:
        percent_of_bar = 0
    else:
        current_hp = max(0, entt.get_hp())
        percent_of_bar = int((current_hp / entt.base_hp) * 10)
    percent_of_bar = min(percent_of_bar, 10)
    hp_bar_fill = "[#]" * percent_of_bar
    hp_bar_empty = "[ ]" * (10 - percent_of_bar)
    return f"|{hp_bar_fill}{hp_bar_empty}| {entt.get_hp()}/{entt.base_hp} HP"


def show_status(entity) -> None:
    """Exibe os status detalhados de uma entidade usando Rich para uma estética premium."""
    title = f"Status de {entity.get_nick_name()}"

    table = Table(show_header=False, expand=True, border_style="cyan")
    table.add_column("Atributo", style="bold white")
    table.add_column("Valor", style="bold yellow")

    if hasattr(entity, "get_classname"):
        class_name = entity.get_classname()
    elif hasattr(entity, "my_type") and entity.my_type() == "COM":
        class_name = "Monstro"
    else:
        class_name = "Desconhecido"

    table.add_row("Classe", class_name)

    level = entity.get_level() if hasattr(entity, "get_level") else getattr(entity, "level", "N/A")
    table.add_row("Nível", str(level))

    if hasattr(entity, "xp_points"):
        table.add_row("XP", f"{entity.xp_points} / {entity.need_to_up()}")
        table.add_row("Falta para Up", f"{entity.need_to_next()}")

    table.add_row("HP", f"[red]{entity.get_hp()}[/red] / [red]{entity.base_hp}[/red]")
    table.add_row("MP", f"[blue]{entity.get_mp()}[/blue] / [blue]{entity.base_mp}[/blue]")
    table.add_row("Força", str(entity.get_st()))
    table.add_row("Magia", str(entity.get_mg()))
    table.add_row("Agilidade", str(entity.get_ag()))
    table.add_row("Defesa", str(entity.get_df()))
    table.add_row("Dano Médio", str(entity.get_avg_damage()))

    if hasattr(entity, "coins"):
        table.add_row("Moedas", f"[yellow]{entity.coins}[/yellow]")

    console.print(Panel(table, title=f"[bold green]{title}[/bold green]", border_style="green", expand=False))


def render_menu(options: tuple[str, ...] | list[str], prompt: str) -> None:
    """Menu numérico simples (Rich)."""
    console.print(Panel(Text(prompt, justify="center", style="bold yellow"), border_style="yellow"))

    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Chave", style="bold blue", justify="right", width=4)
    table.add_column("Opção", style="cyan")

    for i, option in enumerate(options, 1):
        table.add_row(f"{i}.", option)

    console.print(table)
    console.print("=" * console.width, style="dim white")


def render_battle_start_prompt() -> None:
    console.print("\n[dim]Pressione ENTER para começar a batalha...[/dim]")


def render_compare_opponents(ennt1, ennt2) -> None:
    console.print(Panel(Text("CONFRONTO", justify="center", style="bold yellow"), border_style="yellow"))

    table = Table(show_header=False, expand=True, border_style="dim white")
    table.add_column(Text(ennt1.get_nick_name(), style="bold blue"), justify="left")
    table.add_column(Text("VS", style="bold white"), justify="center")
    table.add_column(Text(ennt2.get_nick_name(), style="bold magenta"), justify="right")

    table.add_row(f"Nível: [green]{ennt1.get_level()}[/green]", "", f"Nível: [green]{ennt2.get_level()}[/green]")
    table.add_row(f"HP: [red]{ennt1.get_hp()}[/red]/[dim red]{ennt1.base_hp}[/dim red]", "", f"HP: [red]{ennt2.get_hp()}[/red]/[dim red]{ennt2.base_hp}[/dim red]")
    table.add_row(f"MP: [cyan]{ennt1.get_mp()}[/cyan]/[dim cyan]{ennt1.base_mp}[/dim cyan]", "", f"MP: [cyan]{ennt2.get_mp()}[/cyan]/[dim cyan]{ennt2.base_mp}[/dim cyan]")
    table.add_row(f"Força: [yellow]{ennt1.get_st()}[/yellow]", "", f"Força: [yellow]{ennt2.get_st()}[/yellow]")
    table.add_row(f"Agilidade: [green]{ennt1.get_ag()}[/green]", "", f"Agilidade: [green]{ennt2.get_ag()}[/green]")
    table.add_row(f"Magia: [blue]{ennt1.get_mg()}[/blue]", "", f"Magia: [blue]{ennt2.get_mg()}[/blue]")
    table.add_row(f"Defesa: [white]{ennt1.get_df()}[/white]", "", f"Defesa: [white]{ennt2.get_df()}[/white]")

    console.print(table)
    console.print("=" * console.width, style="dim white")


def render_battle_frame(player, monster) -> None:
    console.clear()

    console.print(Panel(Text("=== BATALHA ===", justify="center", style="bold red"), border_style="red"))

    player_name_text = Text(player.get_nick_name(), style="bold blue")
    monster_name_text = Text(monster.get_nick_name(), style="bold magenta")
    vs_text = Text("VS", style="bold white")

    name_table = Table(show_header=False, expand=True, box=None)
    name_table.add_column(justify="left")
    name_table.add_column(justify="center")
    name_table.add_column(justify="right")
    name_table.add_row(player_name_text, vs_text, monster_name_text)
    console.print(name_table)

    player_hp_bar = get_hp_bar(player)
    monster_hp_bar = get_hp_bar(monster)

    hp_table = Table(show_header=False, expand=True, box=None)
    hp_table.add_column(justify="left")
    hp_table.add_column(justify="right")
    hp_table.add_row(Text(player_hp_bar, style="green"), Text(monster_hp_bar, style="red"))
    console.print(hp_table)

    console.print(
        f"MP: [cyan]{player.get_mp()}[/cyan]/[dim cyan]{player.base_mp}[/dim cyan]",
        justify="left",
    )
    console.print("=" * console.width, style="dim white")


def render_physical_strike_result(attacker, defender, result: CombatResult) -> None:
    if result.was_evaded:
        console.print(
            f"[bold red]{attacker.get_nick_name()}[/bold red] [dim white]errou o ataque![/dim white]",
            justify="center",
        )
        return

    att_color = "blue" if attacker.my_type() == "Human" else "magenta"
    def_color = "magenta" if defender.my_type() == "COM" else "blue"
    critical_msg = " [bold yellow]ATAQUE CRÍTICO![/bold yellow]" if result.was_critical else ""

    console.print(
        f"[bold {att_color}]{attacker.get_nick_name()}[/bold {att_color}] causou [orange3]{result.damage}[/orange3] de dano em "
        f"[bold {def_color}]{defender.get_nick_name()}[/bold {def_color}].{critical_msg}",
        justify="center",
    )


def render_skill_cast_banner(caster, skill) -> None:
    console.print(
        Panel(
            Text.from_markup(
                f"{caster.get_nick_name()} usa [bold green]{skill.name}[/bold green]!",
                justify="center",
                style="white",
            ),
            border_style="green",
        )
    )


def render_heal_result(caster, heal_amount: int) -> None:
    console.print(
        f"[bold green]{caster.get_nick_name()}[/bold green] recupera [bold cyan]{heal_amount}[/bold cyan] de HP!",
        justify="center",
    )


def render_status_apply(target, effect: str) -> None:
    console.print(
        f"[bold purple]{target.get_nick_name()}[/bold purple] está sob o efeito de [yellow]{effect}[/yellow]!",
        justify="center",
    )


def render_status_failed() -> None:
    console.print("[dim red]O efeito falhou![/dim red]", justify="center")


def render_buff_applied(caster, buff_name: str) -> None:
    console.print(
        f"[bold blue]{caster.get_nick_name()}[/bold blue] recebe o buff [bold yellow]{buff_name}[/bold yellow]!",
        justify="center",
    )


def render_flee_success_message() -> None:
    console.print(
        Panel(Text("Você conseguiu fugir da batalha!", justify="center", style="green"), border_style="green")
    )


def render_flee_failed_message() -> None:
    console.print(Panel(Text("A fuga falhou!", justify="center", style="red"), border_style="red"))


def render_turn_effect_message(entity, event: tuple[str, ...]) -> None:
    kind = event[0]
    if kind == "poison_tick":
        dmg = event[1]
        console.print(
            f"[bold green4]{entity.get_nick_name()}[/bold green4] sofre [orange3]{dmg}[/orange3] de dano de veneno.",
            justify="center",
        )
    elif kind == "frozen":
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] está [bold cyan]congelado[/bold cyan] e não pode se mover!",
            justify="center",
        )
    elif kind == "effect_expired":
        eff = event[1]
        console.print(
            f"O efeito [dim white]{eff}[/dim white] em [dim blue]{entity.get_nick_name()}[/dim blue] passou.",
            justify="center",
        )
    elif kind == "buff_expired":
        buff = event[1]
        console.print(
            f"O buff [dim white]{buff}[/dim white] em [dim blue]{entity.get_nick_name()}[/dim blue] acabou.",
            justify="center",
        )

