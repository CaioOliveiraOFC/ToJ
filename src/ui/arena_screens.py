"""Telas da Arena: escolher, preparar, conhecer o adversário, duelar, ver o fim.

Funções puras de desenho, como `screens.py`: recebem o que mostrar e não decidem
nada. Quem conduz o fluxo e lê as teclas é `engine/arena_mode.py`.

O duelo é desenhado a partir da VISÃO que o motor entrega a cada lado
(`DuelView`, por duck typing): a tela do jogador mostra exatamente o que o
controlador dele recebe, e nada da escolha do adversário. A iniciativa nunca
aparece aqui.
"""

from __future__ import annotations

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.shared import effect_core as core
from src.ui import renderer
from src.ui.screens import SLOT_LABELS

console = renderer.console


def _escapa(texto) -> str:
    return escape(str(texto))


def _rotulo_de_efeito(effect_id: str) -> str:
    definicao = core.definition(effect_id)
    return definicao.label if definicao is not None else effect_id


def render_arena_header(subtitle: str = "") -> None:
    console.clear()
    console.print(
        Panel(
            Text("ARENA", justify="center", style="bold red"),
            border_style="red",
            subtitle=subtitle or "Gladiadores extraídos da masmorra",
        )
    )


def render_arena_unavailable(count: int) -> None:
    """Nenhum gladiador do jogador: não há partida possível, e ele precisa saber por quê."""
    render_arena_header()
    console.print(
        Panel(
            Text.from_markup(
                f"Há [bold]{count}[/bold] gladiador(es) extraído(s) nos saves.\n\n"
                "Para lutar na Arena você precisa de um personagem que tenha terminado a "
                "run pela [bold]Extração[/bold]. Volte à masmorra, conquiste a Chave de "
                "Extração e saia vivo para trazer o seu gladiador.\n\n"
                "[dim]Pressione qualquer tecla para voltar.[/dim]",
                justify="center",
            ),
            border_style="yellow",
        )
    )


def render_population_unavailable(reason: str) -> None:
    """A população não passou na conferência: a Arena não abre com adversário duvidoso."""
    render_arena_header()
    console.print(
        Panel(
            Text.from_markup(
                "Os gladiadores da Arena não passaram na conferência de integridade, e "
                "nenhuma partida começa assim.\n\n"
                f"[dim]{_escapa(reason)}[/dim]\n\n"
                "[dim]Reinstale o jogo. Pressione qualquer tecla para voltar.[/dim]",
                justify="center",
            ),
            border_style="red",
        )
    )


def render_gladiator_list(title: str, entries, cursor: int) -> None:
    """A lista de gladiadores elegíveis, com o cursor de seleção."""
    render_arena_header(title)
    tabela = Table(show_header=True, expand=True)
    tabela.add_column("", width=2)
    tabela.add_column("SLOT", style="bold yellow", justify="center", width=6)
    tabela.add_column("NOME", style="cyan")
    tabela.add_column("CLASSE", style="magenta")
    tabela.add_column("NÍVEL", style="green", justify="center")
    tabela.add_column("EXTRAÍDO NO ANDAR", style="red", justify="center")
    for i, entrada in enumerate(entries):
        marca = ">" if i == cursor else " "
        tabela.add_row(
            marca,
            str(entrada.slot),
            _escapa(entrada.name),
            entrada.class_name,
            str(entrada.level),
            str(entrada.floor),
        )
    console.print(tabela)
    console.print(Text("W/S = navegar  |  ENTER = escolher  |  Q = voltar", style="bold cyan"))


def render_opponent_list(
    opponents, cursor: int, class_filter: str, page: int, pages: int, total: int
) -> None:
    """Uma página da população offline, com o cursor e o filtro de classe.

    FORÇA é a referência inicial (o OP medido na geração), não rating. ESTILO é
    como a run PvE daquele gladiador foi jogada.
    """
    render_arena_header("ESCOLHA O ADVERSÁRIO")
    tabela = Table(show_header=True, expand=True)
    tabela.add_column("", width=2)
    tabela.add_column("ID", style="bold yellow", justify="center", width=5)
    tabela.add_column("NOME", style="cyan")
    tabela.add_column("CLASSE", style="magenta")
    tabela.add_column("NÍVEL", style="green", justify="center")
    tabela.add_column("FORÇA", style="red", justify="right")
    tabela.add_column("ESTILO DA RUN", style="dim")
    tabela.add_column("ANDAR", justify="center")
    for i, oponente in enumerate(opponents):
        tabela.add_row(
            ">" if i == cursor else " ",
            oponente.id,
            _escapa(oponente.apelido),
            oponente.nome_da_classe,
            str(oponente.nivel),
            f"{oponente.op:.1f}".replace(".", ","),
            oponente.estilo,
            str(oponente.andar_de_extracao),
        )
    console.print(tabela)
    console.print(
        Text(
            f"Classe: {class_filter}  |  página {page}/{pages}  |  {total} gladiador(es)",
            style="dim",
        )
    )
    console.print(
        Text(
            "W/S = navegar  |  A/D = página  |  F = filtrar classe  |  ENTER = ver ficha  |  "
            "Q = voltar",
            style="bold cyan",
        )
    )


def render_opponent_origin(opponent) -> None:
    """De onde o adversário veio: a run PvE que o extraiu, e a força de referência."""
    console.print(
        Panel(
            Text(
                f"{opponent.id}  |  extraído no andar {opponent.andar_de_extracao}  |  "
                f"run {opponent.estilo}  |  força de referência "
                + f"{opponent.op:.1f}".replace(".", ",")
                + "  |  controlado pela IA",
                justify="center",
                style="dim",
            ),
            title="Origem",
            border_style="dim white",
        )
    )


def render_build_sheet(hero, title: str) -> None:
    """A ficha pública de um gladiador: atributos, equipamento, skills e passivas.

    É a mesma ficha para o próprio gladiador e para o adversário: na Arena a
    build é informação pública. Os números são os do gladiador PRONTO para o
    duelo — HP e MP cheios.
    """
    console.print(
        Panel(
            Text(
                f"{hero.get_nick_name()} — {hero.get_classname()}  |  Nível {hero.get_level()}",
                justify="center",
                style="bold cyan",
            ),
            border_style="cyan",
            title=title,
        )
    )
    atributos = (
        f"HP {hero.base_hp}  |  MP {hero.base_mp}  |  ST {hero.get_st()}  |  "
        f"MG {hero.get_mg()}  |  AG {hero.get_ag()}  |  DF {hero.get_df()}"
    )
    console.print(Panel(Text(atributos, justify="center", style="yellow"), title="Atributos"))

    equipamento = Table(show_header=False, expand=True, box=None)
    equipamento.add_column("Posição", style="bold")
    equipamento.add_column("Peça")
    for posicao, item in hero.equipment.items():
        nome = _escapa(item.display_name) if item is not None else "[dim]Vazio[/dim]"
        equipamento.add_row(SLOT_LABELS.get(posicao, posicao), nome)

    skills = Table(show_header=True, expand=True, box=None)
    skills.add_column("Skill", style="green")
    skills.add_column("MP", style="magenta", justify="right")
    skills.add_column("Recarga", justify="right")
    skills.add_column("", style="yellow")
    for skill in hero.skills.values():
        aviso = "" if hero.can_use_skill(skill) else f"exige {skill.requires.describe()}"
        skills.add_row(
            _escapa(skill.name),
            str(hero.skill_mana_cost(skill)),
            str(int(getattr(skill, "cooldown", 0) or 0)),
            aviso,
        )
    if not hero.skills:
        skills.add_row("[dim]Nenhuma skill[/dim]", "", "", "")

    passivas = (
        "\n".join(f"- {_escapa(p.name)}: {_escapa(p.description)}" for p in hero.passives)
        or "[dim]Nenhuma passiva[/dim]"
    )

    grade = Table(show_header=False, expand=True, box=None)
    grade.add_column(ratio=1)
    grade.add_column(ratio=1)
    grade.add_row(
        Panel(equipamento, title="Equipamento", border_style="magenta"),
        Panel(skills, title="Skills", border_style="green"),
    )
    console.print(grade)
    console.print(Panel(Text.from_markup(passivas), title="Passivas", border_style="blue"))


def render_prep_menu() -> None:
    console.print(
        Panel(
            Text(
                "[E] Equipamentos  |  [ENTER] Confirmar configuração  |  [Q] Voltar",
                justify="center",
                style="bold yellow",
            ),
            title="Preparação",
            border_style="yellow",
        )
    )


def render_save_loadout_prompt() -> None:
    console.print(
        Panel(
            Text.from_markup(
                "O equipamento mudou. Gravar esta configuração no save do gladiador?\n"
                "[bold]\\[S][/bold] Gravar  |  [bold]\\[N][/bold] Só para este duelo",
                justify="center",
            ),
            border_style="cyan",
        )
    )


def render_opponent_menu() -> None:
    console.print(
        Panel(
            Text(
                "[ENTER] Lutar contra este gladiador  |  [Q] Escolher outro",
                justify="center",
                style="bold yellow",
            ),
            border_style="yellow",
        )
    )


def render_notice(message: str, style: str = "yellow") -> None:
    console.print(Panel(Text(message, justify="center", style=style), border_style=style))


def _coluna_do_gladiador(lutador, cor: str) -> Panel:
    efeitos = [_rotulo_de_efeito(e) for e in lutador.effects] + list(lutador.buffs)
    linha_de_efeitos = (
        "Efeitos: " + ", ".join(f"[yellow]{_escapa(e)}[/yellow]" for e in efeitos)
        if efeitos
        else "[dim]Sem efeitos ativos[/dim]"
    )
    linhas = Text.from_markup(
        f"[bold {cor}]{_escapa(lutador.name)}[/bold {cor}]  "
        f"[dim]{lutador.class_name} • Nível {lutador.level}[/dim]\n"
        f"[green]{_escapa(renderer.barra_de_hp(lutador.hp, lutador.hp_max))}[/green]\n"
        f"MP: [cyan]{lutador.mp}[/cyan]/[dim cyan]{lutador.mp_max}[/dim cyan]\n"
        f"{linha_de_efeitos}"
    )
    return Panel(linhas, border_style=cor)


def render_duel_frame(view, log_lines) -> None:
    """O quadro do duelo, a partir da visão do lado do jogador."""
    console.clear()
    console.print(
        Panel(
            Text(f"=== ARENA — RODADA {view.round_number} ===", justify="center", style="bold red"),
            border_style="red",
        )
    )
    grade = Table(show_header=False, expand=True, box=None)
    grade.add_column(ratio=1)
    grade.add_column(ratio=1)
    grade.add_row(
        _coluna_do_gladiador(view.me, "blue"), _coluna_do_gladiador(view.opponent, "magenta")
    )
    console.print(grade)
    if log_lines:
        console.print(
            Panel(
                Text("\n".join(log_lines)),
                title="Última rodada",
                border_style="dim white",
            )
        )


def render_duel_actions() -> None:
    tabela = Table(show_header=False, expand=True, border_style="dim white")
    tabela.add_column("Opção", style="bold blue", justify="right")
    tabela.add_column("Descrição", style="cyan")
    tabela.add_row("1.", "Ataque básico")
    tabela.add_row("2.", "Skill")
    tabela.add_row("3.", "Render-se")
    console.print(
        Panel(
            tabela,
            title="[bold yellow]Escolha sua ação[/bold yellow]",
            subtitle="[dim]O adversário escolhe ao mesmo tempo, sem ver a sua[/dim]",
            border_style="yellow",
        )
    )


def render_duel_skill_panel(rows) -> None:
    """As skills do deck: `(tecla, nome, custo, situação)`. Situação vazia = disponível."""
    tabela = Table(show_header=False, expand=True, border_style="dim white")
    tabela.add_column("Chave", style="bold blue", justify="right")
    tabela.add_column("Skill", style="cyan")
    tabela.add_column("Custo", style="magenta")
    tabela.add_column("Situação")
    for tecla, nome, custo, situacao in rows:
        if situacao:
            tabela.add_row(
                f"{tecla}.",
                f"[dim]{_escapa(nome)}[/dim]",
                f"{custo} MP",
                f"[red]{_escapa(situacao)}[/red]",
            )
        else:
            tabela.add_row(f"{tecla}.", _escapa(nome), f"{custo} MP", "[green]disponível[/green]")
    tabela.add_row("0.", "Voltar", "", "")
    console.print(
        Panel(tabela, title="[bold yellow]Escolha uma skill[/bold yellow]", border_style="yellow")
    )


def render_surrender_confirm() -> None:
    render_notice("Render-se encerra o duelo com derrota. Confirmar? [S] Sim  |  [N] Não", "red")


def render_round_summary(lines) -> None:
    """O que a rodada resolveu, na ordem em que resolveu. Texto puro, sem markup."""
    console.print(
        Panel(
            Text("\n".join(lines)),
            title="[bold]Rodada resolvida[/bold]",
            subtitle="[dim]Pressione qualquer tecla[/dim]",
            border_style="white",
        )
    )


def render_duel_result(
    player_won: bool, winner_name: str, loser_name: str, reason: str, rounds: int
) -> None:
    cor = "green" if player_won else "red"
    titulo = "VITÓRIA" if player_won else "DERROTA"
    console.print(
        Panel(
            Text.from_markup(
                f"[bold {cor}]{titulo}[/bold {cor}]\n\n"
                f"[bold]{_escapa(winner_name)}[/bold] venceu [bold]{_escapa(loser_name)}[/bold] "
                f"por {reason}, em {rounds} rodada(s).\n\n"
                "[dim]Partida offline: nenhum gladiador morre, nada é gravado no save e não "
                "há XP, ouro nem recompensa.[/dim]",
                justify="center",
            ),
            title="[bold]Fim do duelo[/bold]",
            border_style=cor,
        )
    )


def render_after_match_menu(wins: int, losses: int) -> None:
    """O placar da sessão do gladiador e o que fazer em seguida."""
    console.print(
        Panel(
            Text(
                f"Nesta sessão: {wins} vitória(s), {losses} derrota(s)\n"
                "[R] Revanche  |  [A] Outro adversário  |  [Q] Voltar à Arena",
                justify="center",
                style="bold yellow",
            ),
            border_style="yellow",
        )
    )
