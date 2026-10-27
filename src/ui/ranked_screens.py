"""Telas da Arena Ranqueada: o hub da Arena, o painel do gladiador, o resultado e a classificação.

Funções puras de desenho, como `arena_screens.py`: recebem dicionários prontos
e não decidem nada. Quem conduz o fluxo e lê as teclas é
`engine/ranked_mode.py`.
"""

from __future__ import annotations

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.ui import renderer
from src.ui.arena_screens import render_arena_header

console = renderer.console

FASES = {
    "descoberta": "Descoberta",
    "nivelamento": "Nivelamento",
    "validacao": "Validação",
    "ranqueada": "Ranqueada",
}


def _num(valor: float, casas: int = 0) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def render_arena_hub() -> None:
    render_arena_header("ESCOLHA O MODO")
    tabela = Table(show_header=False, expand=True, border_style="dim white")
    tabela.add_column("Opção", style="bold blue", justify="right")
    tabela.add_column("Modo", style="cyan")
    tabela.add_column("O que é", style="dim")
    tabela.add_row("1.", "Duelo Livre", "Você escolhe o adversário. Não mexe no rating.")
    tabela.add_row(
        "2.", "Arena Ranqueada", "O jogo escolhe o adversário. Vitória e derrota valem rating."
    )
    tabela.add_row("3.", "Classificação", "A Ladder inteira, com ranks e percentis.")
    tabela.add_row("Q.", "Voltar", "")
    console.print(tabela)


def render_ranked_panel(status: dict) -> None:
    """O painel do gladiador na Ranqueada: posicionamento ou rank, e o histórico recente."""
    render_arena_header("ARENA RANQUEADA")
    cabecalho = (
        f"[bold cyan]{escape(status['nome'])}[/bold cyan] — {status['classe']}  |  "
        f"{status['vitorias']}V {status['derrotas']}D"
    )
    if status["posicionado"]:
        titulo = f"  [bold yellow]★ {status['titulo']}[/bold yellow]" if status["titulo"] else ""
        corpo = (
            f"{cabecalho}\n\n"
            f"[bold]{status['rank']}[/bold]{titulo}\n"
            f"Posição {status['posicao']} de {status['competitivos']}  |  "
            f"percentil {_num(status['percentil'], 1)}\n"
            f"Rating {_num(status['rating'])} ± {_num(2 * status['incerteza'])}"
        )
    else:
        corpo = (
            f"{cabecalho}\n\n"
            f"[bold]Posicionamento: {status['partidas']} de {status['posicionamento']}[/bold]  "
            f"— etapa: {FASES[status['fase']]}\n"
            "O rank aparece depois da 10ª partida. A estimativa já muda desde a primeira:\n"
            f"rating {_num(status['rating'])} ± {_num(2 * status['incerteza'])}"
        )
    console.print(Panel(Text.from_markup(corpo, justify="center"), border_style="cyan"))
    if status["recentes"]:
        tabela = Table(show_header=True, expand=True, box=None)
        tabela.add_column("#", justify="right", style="dim")
        tabela.add_column("Adversário", style="cyan")
        tabela.add_column("Resultado")
        tabela.add_column("Rating", justify="right")
        for linha in status["recentes"]:
            cor, texto = {True: ("green", "Vitória"), False: ("red", "Derrota")}.get(
                linha["venceu"], ("dim", "Sem resultado")
            )
            tabela.add_row(
                str(linha["n"]),
                escape(linha["oponente"]),
                f"[{cor}]{texto}[/{cor}]",
                f"{_num(linha['antes'])} → {_num(linha['depois'])} "
                f"({'+' if linha['depois'] >= linha['antes'] else ''}"
                f"{_num(linha['depois'] - linha['antes'])})",
            )
        console.print(Panel(tabela, title="Últimas partidas", border_style="dim white"))
    if status.get("mundo"):
        console.print(Text(status["mundo"], style="dim", justify="center"))
    console.print(
        Text(
            "[ENTER] Buscar partida  |  [C] Classificação  |  [Q] Voltar",
            style="bold yellow",
            justify="center",
        )
    )


def render_opponent_found(info: dict) -> None:
    """O adversário que o matchmaking encontrou, antes da ficha completa."""
    rank = f"{info['rank']}, percentil {_num(info['percentil'], 1)}" if info["rank"] else ""
    console.print(
        Panel(
            Text(
                f"Adversário encontrado: {info['nome']} — {info['classe']}, nível "
                f"{info['nivel']}  |  {rank}  |  rating {_num(info['rating'])}\n"
                f"Etapa: {FASES[info['fase']]}  |  chance estimada de vitória "
                f"{_num(100 * info['probabilidade'])}%",
                justify="center",
                style="bold magenta",
            ),
            title="Matchmaking",
            border_style="magenta",
        )
    )
    console.print(
        Text(
            "[ENTER] Lutar  |  [Q] Voltar (o adversário continua reservado)",
            style="bold yellow",
            justify="center",
        )
    )


def render_ranked_result(info: dict) -> None:
    """A alteração de rating, e o rank quando o posicionamento termina."""
    cor = "green" if info["venceu"] else "red"
    delta = info["depois"] - info["antes"]
    linhas = [
        f"[bold {cor}]{'VITÓRIA' if info['venceu'] else 'DERROTA'}[/bold {cor}]",
        "",
        f"Rating {_num(info['antes'])} → [bold]{_num(info['depois'])}[/bold] "
        f"([{cor}]{'+' if delta >= 0 else ''}{_num(delta)}[/{cor}])",
        f"Chance estimada antes da partida: {_num(100 * info['probabilidade'])}%",
    ]
    if info["acabou_de_posicionar"]:
        linhas += [
            "",
            f"[bold yellow]Posicionamento concluído: {info['rank']}[/bold yellow]",
            f"Posição {info['posicao']} de {info['competitivos']}, "
            f"percentil {_num(info['percentil'], 1)}",
        ]
    elif info["rank"]:
        linhas += [
            "",
            f"{info['rank']}  |  posição {info['posicao']} de {info['competitivos']}  |  "
            f"percentil {_num(info['percentil'], 1)}",
        ]
    else:
        linhas += ["", f"Posicionamento: {info['partidas']} de {info['posicionamento']}"]
    console.print(
        Panel(
            Text.from_markup("\n".join(linhas), justify="center"),
            title="[bold]Arena Ranqueada[/bold]",
            border_style=cor,
        )
    )
    console.print(Text("Pressione qualquer tecla.", style="dim", justify="center"))


def render_leaderboard(linhas: list[dict], pagina: int, paginas: int, total: int) -> None:
    """Uma página da classificação; o gladiador do jogador vem destacado."""
    render_arena_header("CLASSIFICAÇÃO")
    tabela = Table(show_header=True, expand=True)
    tabela.add_column("#", justify="right", style="bold yellow")
    tabela.add_column("NOME", style="cyan")
    tabela.add_column("CLASSE", style="magenta")
    tabela.add_column("RANK")
    tabela.add_column("PERCENTIL", justify="right")
    tabela.add_column("RATING", justify="right")
    tabela.add_column("V-D", justify="center")
    for linha in linhas:
        nome = escape(linha["nome"]) + (" (você)" if linha["jogador"] else "")
        rank = linha["rank"] + (f" ★ {linha['titulo']}" if linha["titulo"] else "")
        estilo = "bold green" if linha["jogador"] else None
        tabela.add_row(
            str(linha["posicao"]),
            nome,
            linha["classe"],
            rank,
            _num(linha["percentil"], 1),
            f"{_num(linha['rating'])} ± {_num(2 * linha['incerteza'])}",
            f"{linha['vitorias']}-{linha['derrotas']}",
            style=estilo,
        )
    console.print(tabela)
    console.print(
        Text(
            f"Página {pagina}/{paginas}  |  {total} gladiadores competitivos  |  "
            "A/D = página  |  Q = voltar",
            style="bold cyan",
        )
    )
