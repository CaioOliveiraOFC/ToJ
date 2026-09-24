from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.shared.types import CombatResult

console = Console()


def hp_exibido(entt) -> int:
    """O HP que o jogador vê. Nunca abaixo de zero.

    `reduce_hp` NÃO limita em zero, e é correto que não limite: o excedente do
    golpe fatal é dado real, que o pós-combate e a telemetria leem. Mas "-71/440"
    na tela não é informação, é vazamento do modelo — HP negativo não existe na
    ficha que o jogador tem na mão.

    A barra já tomava essa decisão e o número ao lado dela não: o mesmo painel
    mostrava dez casas vazias com "-71" escrito na frente. Uma função só, para os
    dois não voltarem a divergir.
    """
    return max(0, int(entt.get_hp()))


def get_hp_bar(entt) -> str:
    if getattr(entt, "base_hp", 0) == 0:
        percent_of_bar = 0
    else:
        percent_of_bar = int((hp_exibido(entt) / entt.base_hp) * 10)
    percent_of_bar = min(percent_of_bar, 10)
    hp_bar_fill = "[#]" * percent_of_bar
    hp_bar_empty = "[ ]" * (10 - percent_of_bar)
    return f"|{hp_bar_fill}{hp_bar_empty}| {hp_exibido(entt)}/{entt.base_hp} HP"


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
    console.print(
        Panel(Text("CONFRONTO", justify="center", style="bold yellow"), border_style="yellow")
    )

    table = Table(show_header=False, expand=True, border_style="dim white")
    table.add_column(Text(ennt1.get_nick_name(), style="bold blue"), justify="left")
    table.add_column(Text("VS", style="bold white"), justify="center")
    table.add_column(Text(ennt2.get_nick_name(), style="bold magenta"), justify="right")

    table.add_row(
        f"Nível: [green]{ennt1.get_level()}[/green]",
        "",
        f"Nível: [green]{ennt2.get_level()}[/green]",
    )
    table.add_row(
        f"HP: [red]{hp_exibido(ennt1)}[/red]/[dim red]{ennt1.base_hp}[/dim red]",
        "",
        f"HP: [red]{hp_exibido(ennt2)}[/red]/[dim red]{ennt2.base_hp}[/dim red]",
    )
    table.add_row(
        f"MP: [cyan]{ennt1.get_mp()}[/cyan]/[dim cyan]{ennt1.base_mp}[/dim cyan]",
        "",
        f"MP: [cyan]{ennt2.get_mp()}[/cyan]/[dim cyan]{ennt2.base_mp}[/dim cyan]",
    )
    table.add_row(
        f"Força: [yellow]{ennt1.get_st()}[/yellow]", "", f"Força: [yellow]{ennt2.get_st()}[/yellow]"
    )
    table.add_row(
        f"Agilidade: [green]{ennt1.get_ag()}[/green]",
        "",
        f"Agilidade: [green]{ennt2.get_ag()}[/green]",
    )
    table.add_row(
        f"Magia: [blue]{ennt1.get_mg()}[/blue]", "", f"Magia: [blue]{ennt2.get_mg()}[/blue]"
    )
    table.add_row(
        f"Defesa: [white]{ennt1.get_df()}[/white]", "", f"Defesa: [white]{ennt2.get_df()}[/white]"
    )

    console.print(table)
    console.print("=" * console.width, style="dim white")


def render_battle_frame(player, monster) -> None:
    """Desenha o quadro de batalha: o herói de um lado, o inimigo do outro.

    Um contra um. Houve uma versão com lista de inimigos numerados, para o
    encontro composto; ela saiu junto com o encontro composto.
    """
    console.clear()

    console.print(
        Panel(Text("=== BATALHA ===", justify="center", style="bold red"), border_style="red")
    )

    name_table = Table(show_header=False, expand=True, box=None)
    name_table.add_column(justify="left")
    name_table.add_column(justify="center")
    name_table.add_column(justify="right")
    name_table.add_row(
        Text(player.get_nick_name(), style="bold blue"),
        Text("VS", style="bold white"),
        Text(monster.get_nick_name(), style="bold magenta"),
    )
    console.print(name_table)

    hp_table = Table(show_header=False, expand=True, box=None)
    hp_table.add_column(justify="left")
    hp_table.add_column(justify="right")
    hp_table.add_row(
        Text(get_hp_bar(player), style="green"),
        Text(get_hp_bar(monster), style="red"),
    )
    console.print(hp_table)

    console.print(
        f"MP: [cyan]{player.get_mp()}[/cyan]/[dim cyan]{player.base_mp}[/dim cyan]",
        justify="left",
    )
    console.print("=" * console.width, style="dim white")


def render_physical_strike_result(attacker, defender, result: CombatResult) -> None:
    if result.was_evaded:
        console.print(
            f"[bold red]{attacker.get_nick_name()}[/bold red] "
            "[dim white]errou o ataque![/dim white]",
            justify="center",
        )
        return

    att_color = "blue" if attacker.my_type() == "Human" else "magenta"
    def_color = "magenta" if defender.my_type() == "COM" else "blue"
    critical_msg = " [bold yellow]ATAQUE CRÍTICO![/bold yellow]" if result.was_critical else ""

    console.print(
        f"[bold {att_color}]{attacker.get_nick_name()}[/bold {att_color}] "
        f"causou [orange3]{result.damage}[/orange3] de dano em "
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
        f"[bold green]{caster.get_nick_name()}[/bold green] "
        f"recupera [bold cyan]{heal_amount}[/bold cyan] de HP!",
        justify="center",
    )


def render_status_apply(target, effect: str) -> None:
    console.print(
        f"[bold purple]{target.get_nick_name()}[/bold purple] "
        f"está sob o efeito de [yellow]{effect}[/yellow]!",
        justify="center",
    )


def render_status_failed() -> None:
    console.print("[dim red]O efeito falhou![/dim red]", justify="center")


def render_buff_applied(caster, buff_name: str) -> None:
    console.print(
        f"[bold blue]{caster.get_nick_name()}[/bold blue] "
        f"recebe o buff [bold yellow]{buff_name}[/bold yellow]!",
        justify="center",
    )


def render_flee_success_message() -> None:
    console.print(
        Panel(
            Text("Você conseguiu fugir da batalha!", justify="center", style="green"),
            border_style="green",
        )
    )


def render_flee_failed_message() -> None:
    console.print(Panel(Text("A fuga falhou!", justify="center", style="red"), border_style="red"))


def render_interaction_message(entity, label: str) -> None:
    """Anuncia uma lei que disparou. Alto, curto e com o alvo nomeado."""
    console.print(
        f"[bold yellow]{label}![/bold yellow] [dim white]({entity.get_nick_name()})[/dim white]",
        justify="center",
    )


def render_turn_effect_message(entity, event: tuple[str, ...]) -> None:
    kind = event[0]
    if kind == "poison_tick":
        dmg = event[1]
        console.print(
            f"[bold green4]{entity.get_nick_name()}[/bold green4] "
            f"sofre [orange3]{dmg}[/orange3] de dano de veneno.",
            justify="center",
        )
    elif kind in ("stun", "sleep"):
        rotulo = "atordoado" if kind == "stun" else "dormindo"
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] está "
            f"[bold yellow]{rotulo}[/bold yellow] e perde o turno!",
            justify="center",
        )
    elif kind == "stun_applied":
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] foi "
            "[bold yellow]atordoado[/bold yellow]!",
            justify="center",
        )
    elif kind == "status_resisted":
        # Resistir precisa ser visível: é a única forma de o jogador aprender
        # que o equipamento defensivo dele está trabalhando.
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] resiste a "
            f"[bold yellow]{event[1]}[/bold yellow]!",
            justify="center",
        )
    elif kind == "mana_burn_tick":
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] perde "
            f"[bold magenta]{event[1]}[/bold magenta] de mana drenada.",
            justify="center",
        )
    elif kind == "magic_shield":
        console.print(
            f"A Égide de [bold blue]{entity.get_nick_name()}[/bold blue] absorve "
            f"[bold cyan]{event[1]}[/bold cyan] de dano "
            f"([bold magenta]{event[2]}[/bold magenta] de mana).",
            justify="center",
        )
    elif kind == "frozen":
        console.print(
            f"[bold blue]{entity.get_nick_name()}[/bold blue] está "
            "[bold cyan]congelado[/bold cyan] e não pode se mover!",
            justify="center",
        )
    elif kind == "effect_expired":
        eff = event[1]
        console.print(
            f"O efeito [dim white]{eff}[/dim white] em "
            f"[dim blue]{entity.get_nick_name()}[/dim blue] passou.",
            justify="center",
        )
    elif kind == "buff_expired":
        buff = event[1]
        console.print(
            f"O buff [dim white]{buff}[/dim white] em "
            f"[dim blue]{entity.get_nick_name()}[/dim blue] acabou.",
            justify="center",
        )
