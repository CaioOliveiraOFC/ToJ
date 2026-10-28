"""Telas da Arena Ranqueada: o hub da Arena, o painel do gladiador, o resultado e a classificação.

Funções puras de desenho, como `arena_screens.py`: recebem dicionários prontos
e não decidem nada. Quem conduz o fluxo e lê as teclas é
`engine/ranked_mode.py`.
"""

from __future__ import annotations

import time

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
        "2.",
        "Arena Ranqueada",
        "O jogo escolhe o adversário. O resultado vale MMR e PR de divisão.",
    )
    tabela.add_row("3.", "Classificação", "A leaderboard publicada, com ranks e percentis.")
    tabela.add_row("Q.", "Voltar", "")
    console.print(tabela)


RESULTADOS = {
    "vitoria": ("green", "Vitória"),
    "derrota": ("red", "Derrota"),
    "empate": ("yellow", "Empate técnico"),
    "anulada": ("dim", "Anulada"),
}

EVENTOS = {
    "posicionamento": "Posicionamento concluído",
    "promocao": "Promoção de divisão",
    "rebaixamento": "Rebaixamento de divisão",
    "escudo": "O escudo segurou a divisão",
    "candidatura": "Candidato a Master",
    "candidatura_perdida": "Candidatura perdida (caiu de Obsidian I)",
    "candidatura_mantida": "Avaliado na atualização: candidatura mantida",
    "promocao_a_elite": "Promovido à elite",
    "em_risco": "Elite em risco",
    "fora_de_risco": "Saiu da zona de risco",
    "rebaixamento_da_elite": "Rebaixado da elite",
    "elite_sobe": "Subiu na elite",
    "elite_desce": "Desceu na elite",
}


def _hora(instante: float | None) -> str:
    if instante is None:
        return "—"
    return time.strftime("%d/%m %H:%M", time.localtime(instante))


def _periodo(segundos: int) -> str:
    if segundos % 86_400 == 0:
        return f"{segundos // 86_400 * 24} h"
    if segundos % 3600 == 0:
        return f"{segundos // 3600} h"
    return f"{segundos // 60} min"


def barra(pr: int, largura: int = 20) -> str:
    cheio = round(largura * max(0, min(100, pr)) / 100)
    return "█" * cheio + "░" * (largura - cheio)


def _descreve_evento(evento: dict) -> str:
    """O evento em texto. As divisões chegam com o nome (`para_nome`, `de_nome`)."""
    texto = EVENTOS.get(evento["evento"], evento["evento"])
    de = evento.get("de_nome", evento.get("de"))
    para = evento.get("para_nome", evento.get("para"))
    if evento["evento"] in ("promocao", "rebaixamento", "posicionamento", "promocao_a_elite"):
        texto += f": {para}"
    elif evento["evento"] in ("rebaixamento_da_elite", "elite_sobe", "elite_desce"):
        texto += f": {de} → {para}"
    if evento.get("motivos"):
        texto += " (" + "; ".join(evento["motivos"]) + ")"
    return texto


def _linha_do_ciclo(ciclo: dict) -> str:
    texto = (
        f"Leaderboard publicada: {_hora(ciclo['publicada_em'])}  |  próxima atualização: "
        f"{_hora(ciclo['proxima'])}  (ciclo de {_periodo(ciclo['periodo'])})"
    )
    if ciclo.get("adiada"):
        texto += "  |  [red]última atualização adiada: estado inconsistente[/red]"
    return texto


def _corpo_da_progressao(status: dict) -> str:
    """O bloco central do painel: posicionamento, divisão com PR, candidatura ou elite."""
    mmr = f"MMR {_num(status['rating'])} ± {_num(2 * status['incerteza'])}" + (
        f"  |  posição ao vivo {status['posicao']} de {status['competitivos']}, "
        f"percentil {_num(status['percentil'], 1)}"
        if status["posicao"]
        else ""
    )
    if not status["posicionado"]:
        return (
            f"[bold]Posicionamento: {status['partidas']} de {status['posicionamento']}[/bold]  "
            f"— etapa: {FASES[status['fase']]}\n"
            "A divisão aparece depois da 10ª partida (empates contam; partidas anuladas, não).\n"
            f"A estimativa já muda desde a primeira: {mmr}"
        )
    if status["elite"]:
        titulo = f"  [bold yellow]★ {status['titulo']}[/bold yellow]" if status["titulo"] else ""
        variacao = status["variacao"]
        seta = ""
        if variacao:
            seta = f" ({'▲' if variacao > 0 else '▼'}{abs(variacao)})"
        risco = (
            "\n[bold red]EM RISCO: na última atualização o percentil ficou abaixo do mínimo "
            "de Master. Abaixo de novo na próxima, ou muito abaixo, e o gladiador sai da "
            "elite.[/bold red]"
            if status["risco"]
            else ""
        )
        return (
            f"[bold magenta]{status['elite']}[/bold magenta]{titulo}\n"
            f"Posição publicada {status['posicao_publicada'] or '—'}{seta}\n{mmr}{risco}"
        )
    linhas = [
        f"[bold]{status['divisao']}[/bold] — {status['pr']}/100 PR",
        f"[cyan]{barra(status['pr'])}[/cyan]",
    ]
    if status["escudo"]:
        linhas.append(f"[dim]Escudo de divisão: mais {status['escudo']} partida(s)[/dim]")
    if status["candidato"]:
        e = status["elegibilidade"]
        ok = "[green]sim[/green]"
        nao = "[red]não[/red]"
        linhas += [
            "[bold yellow]CANDIDATO A MASTER[/bold yellow] — a promoção sai na atualização "
            "da leaderboard, se você estiver na posição de Master nela.",
            f"Hoje: percentil {_num(e['percentil'], 1)} (mínimo {_num(e['minimo'], 1)}) "
            f"{ok if e['percentil_ok'] else nao}  |  incerteza {_num(e['incerteza'])} "
            f"(máximo {_num(e['incerteza_maxima'])}) {ok if e['incerteza_ok'] else nao}",
        ]
    linhas.append(mmr)
    if status["alvo"] and status["alvo"] != status["divisao"]:
        linhas.append(
            f"[dim]Seu MMR corresponde a {status['alvo']}: o PR anda mais rápido na direção "
            "dele.[/dim]"
        )
    return "\n".join(linhas)


def render_ranked_panel(status: dict) -> None:
    """O painel do gladiador: posicionamento, divisão e PR, candidatura ou elite."""
    render_arena_header("ARENA RANQUEADA")
    cabecalho = (
        f"[bold cyan]{escape(status['nome'])}[/bold cyan] — {status['classe']}  |  "
        f"{status['vitorias']}V {status['empates']}E {status['derrotas']}D"
    )
    corpo = f"{cabecalho}\n\n{_corpo_da_progressao(status)}"
    console.print(Panel(Text.from_markup(corpo, justify="center"), border_style="cyan"))
    console.print(Text.from_markup(_linha_do_ciclo(status["ciclo"]), justify="center"))
    if status["eventos"]:
        console.print(
            Text(
                "Recentes: " + "  |  ".join(_descreve_evento(e) for e in status["eventos"]),
                style="yellow",
                justify="center",
            )
        )
    if status["recentes"]:
        tabela = Table(show_header=True, expand=True, box=None)
        tabela.add_column("#", justify="right", style="dim")
        tabela.add_column("Adversário", style="cyan")
        tabela.add_column("Resultado")
        tabela.add_column("MMR", justify="right")
        tabela.add_column("PR", justify="right")
        for linha in status["recentes"]:
            cor, texto = RESULTADOS[linha["resultado"]]
            if linha["resultado"] in ("empate", "anulada") and linha.get("motivo"):
                texto += f" ({linha['motivo']})"
            delta = linha["depois"] - linha["antes"]
            pr = "" if linha["pr"] is None else f"{'+' if linha['pr'] >= 0 else ''}{linha['pr']}"
            tabela.add_row(
                str(linha["n"]),
                escape(linha["oponente"]),
                f"[{cor}]{texto}[/{cor}]",
                f"{_num(linha['antes'])} → {_num(linha['depois'])} "
                f"({'+' if delta >= 0 else ''}{_num(delta)})",
                pr,
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
    exibicao = info.get("exibicao") or ""
    if info.get("titulo"):
        exibicao += f" ★ {info['titulo']}"
    if info.get("percentil") is not None:
        exibicao += f", percentil {_num(info['percentil'], 1)}"
    console.print(
        Panel(
            Text(
                f"Adversário encontrado: {info['nome']} — {info['classe']}, nível "
                f"{info['nivel']}  |  {exibicao}  |  MMR {_num(info['rating'])}\n"
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
    """O resultado: MMR, PR, a divisão nova e o que mudou na candidatura."""
    cor, nome = RESULTADOS[info["resultado"]]
    st = info["status"]
    delta = info["depois"] - info["antes"]
    linhas = [f"[bold {cor}]{nome.upper()}[/bold {cor}]"]
    if info["resultado"] == "empate":
        if info["motivo"] == "teto":
            linhas.append(f"A partida chegou ao teto de rodadas ({info['rodadas']}).")
        else:
            linhas.append(
                f"Impasse na rodada {info['rodadas']}: ninguém chegava mais a um HP ou MP "
                "mais baixo. Meio ponto para cada lado."
            )
    linhas += [
        "",
        f"MMR {_num(info['antes'])} → [bold]{_num(info['depois'])}[/bold] "
        f"([{cor}]{'+' if delta >= 0 else ''}{_num(delta)}[/{cor}])",
        f"Chance estimada antes da partida: {_num(100 * info['probabilidade'])}%",
    ]
    if info["pr"] is not None and not st["elite"]:
        linhas.append(
            f"PR: [bold]{'+' if info['pr'] >= 0 else ''}{info['pr']}[/bold]  →  "
            f"{st['divisao']} — {st['pr']}/100 PR  [cyan]{barra(st['pr'])}[/cyan]"
        )
    for evento in info["eventos"]:
        if evento["evento"] == "posicionamento":
            continue
        linhas.append(f"[bold yellow]{_descreve_evento(evento)}[/bold yellow]")
    if info["acabou_de_posicionar"]:
        linhas += [
            "",
            f"[bold yellow]Posicionamento concluído: {st['divisao']} — {st['pr']}/100 PR"
            "[/bold yellow]",
            f"Posição {st['posicao']} de {st['competitivos']}, "
            f"percentil {_num(st['percentil'], 1)}",
        ]
    elif st["posicionado"]:
        linhas += [
            "",
            f"Posição ao vivo {st['posicao']} de {st['competitivos']}  |  "
            f"percentil {_num(st['percentil'], 1)}",
        ]
    else:
        linhas += ["", f"Posicionamento: {st['partidas']} de {st['posicionamento']}"]
    if st["candidato"]:
        linhas.append(
            "[bold yellow]Candidato a Master[/bold yellow]: a promoção depende da sua posição "
            f"na próxima atualização da leaderboard ({_hora(st['ciclo']['proxima'])})."
        )
    console.print(
        Panel(
            Text.from_markup("\n".join(linhas), justify="center"),
            title="[bold]Arena Ranqueada[/bold]",
            border_style=cor,
        )
    )
    console.print(Text("Pressione qualquer tecla.", style="dim", justify="center"))


def render_leaderboard_update(info: dict) -> None:
    """A leaderboard acabou de ser atualizada: o que mudou para este gladiador."""
    if info["adiada"]:
        linhas = [
            "[bold red]Atualização da leaderboard adiada[/bold red]",
            "O estado da classificação não passou na verificação de integridade:",
            *[escape(p) for p in info["adiada"][:3]],
            "Ela será tentada de novo na próxima volta ao painel.",
        ]
    else:
        linhas = [f"[bold]Leaderboard atualizada: {_hora(info['publicada_em'])}[/bold]"]
        if info["pulados"]:
            linhas.append(
                f"[dim]{info['pulados']} ciclo(s) passaram com o jogo fechado: vale este "
                "retrato, com o estado gravado.[/dim]"
            )
        for evento in info["eventos"]:
            linhas.append(f"[bold yellow]{_descreve_evento(evento)}[/bold yellow]")
        if not info["eventos"]:
            linhas.append(f"{info['total']} mudança(s) de elite na Ladder; nenhuma sua.")
        linhas.append(f"Próxima atualização: {_hora(info['proxima'])}")
    console.print(
        Panel(
            Text.from_markup("\n".join(linhas), justify="center"),
            title="[bold]Leaderboard[/bold]",
            border_style="yellow",
        )
    )
    console.print(Text("Pressione qualquer tecla.", style="dim", justify="center"))


def render_leaderboard(
    linhas: list[dict], pagina: int, paginas: int, total: int, ciclo: dict | None = None
) -> None:
    """Uma página da leaderboard publicada; o gladiador do jogador vem destacado."""
    render_arena_header("CLASSIFICAÇÃO")
    if ciclo is not None:
        console.print(Text.from_markup(_linha_do_ciclo(ciclo), justify="center"))
    tabela = Table(show_header=True, expand=True)
    tabela.add_column("#", justify="right", style="bold yellow")
    tabela.add_column("±", justify="right")
    tabela.add_column("NOME", style="cyan")
    tabela.add_column("CLASSE", style="magenta")
    tabela.add_column("RANK")
    tabela.add_column("PERCENTIL", justify="right")
    tabela.add_column("MMR", justify="right")
    tabela.add_column("V-E-D", justify="center")
    for linha in linhas:
        nome = escape(linha["nome"]) + (" (você)" if linha["jogador"] else "")
        rank = escape(linha["rank"] or "")
        if linha.get("candidato"):
            rank += " · candidato"
        if linha["titulo"]:
            rank += f" ★ {linha['titulo']}"
        variacao = linha.get("variacao")
        seta = ""
        if variacao:
            seta = f"{'▲' if variacao > 0 else '▼'}{abs(variacao)}"
        estilo = "bold green" if linha["jogador"] else None
        tabela.add_row(
            str(linha["posicao"]),
            seta,
            nome,
            linha["classe"],
            rank,
            _num(linha["percentil"], 1),
            f"{_num(linha['rating'])} ± {_num(2 * linha['incerteza'])}",
            f"{linha['vitorias']}-{linha.get('empates', 0)}-{linha['derrotas']}",
            style=estilo,
        )
    console.print(tabela)
    console.print(
        Text(
            f"Página {pagina}/{paginas}  |  {total} gladiadores na leaderboard publicada  |  "
            "A/D = página  |  Q = voltar",
            style="bold cyan",
        )
    )
