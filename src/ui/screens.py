"""Funções puras de renderização de telas (Rich apenas, sem lógica de fluxo).

Toda lógica de interação (loops, input) está em ui/shop_flow.py e ui/inventory_flow.py.
"""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.shared.constants import (
    ESSENCE_MULT_GOOD,
    ESSENCE_MULT_MAX,
    ESSENCE_MULT_MIN,
    ESSENCE_MULT_POOR,
)
from src.ui import renderer

if TYPE_CHECKING:
    from src.entities.base import Entity
    from src.entities.heroes import Player
    from src.entities.monsters import Monster


# Rótulo de cada POSIÇÃO de equipamento, na ordem em que a ficha as mostra. As
# duas últimas entradas são CATEGORIAS de item, não posições: a mochila lista o
# item pela categoria que ele declara ("Weapon"), e a ficha pela posição que ele
# ocupa ("Weapon1"). O mesmo mapa atende os dois.
SLOT_LABELS = {
    "Helmet": "Elmo",
    "Amulet": "Amuleto",
    "Weapon1": "Arma 1",
    "Weapon2": "Arma 2",
    "Body": "Armadura",
    "Legs": "Perneiras",
    "Hands": "Mãos",
    "Shoes": "Botas",
    "Ring1": "Anel 1",
    "Ring2": "Anel 2",
    "Accessory": "Acessório",
    "Weapon": "Arma",
    "Ring": "Anel",
}


def menu(options: tuple[str, ...] | list[str], prompt: str) -> None:
    renderer.render_menu(options, prompt)


def render_fight_intro(player: "Player", monster: "Monster") -> None:
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("--- Início da Batalha ---", justify="center", style="bold green"),
            border_style="green",
        )
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
        Panel(
            action_menu_table,
            title="[bold yellow]Escolha sua ação[/bold yellow]",
            border_style="yellow",
        )
    )


def render_battle_no_skills_message() -> None:
    renderer.console.print(
        Panel(
            Text("Você não tem habilidades para usar!", justify="center", style="red"),
            border_style="red",
        )
    )


def render_skill_select_panel(player: "Player") -> None:
    skill_table = Table(show_header=False, expand=True, border_style="dim white")
    skill_table.add_column("Chave", style="bold blue", justify="right")
    skill_table.add_column("Habilidade", style="cyan")
    skill_table.add_column("Custo", style="magenta", justify="left")
    skill_table.add_column("Recarga", style="dim white", justify="left")
    for key, skill in player.skills.items():
        cooldown_remaining = 0
        if hasattr(player, "skill_cooldowns"):
            cooldown_remaining = player.skill_cooldowns.get(getattr(skill, "id", ""), 0)
        if cooldown_remaining > 0:
            skill_table.add_row(
                str(key) + ".",
                f"[dim]{skill.name} (recarga: {cooldown_remaining})[/dim]",
                f"{player.skill_mana_cost(skill)} MP",
                f"[red]{cooldown_remaining} turnos[/red]",
            )
        elif not player.can_use_skill(skill):
            # A carta continua listada: o requisito é um objetivo de build, e
            # esconder a carta faria o jogador esquecer que ele existe. Dizer o
            # que falta aqui evita que ele descubra escolhendo e sendo recusado.
            skill_table.add_row(
                str(key) + ".",
                f"[dim]{skill.name}[/dim]",
                f"{player.skill_mana_cost(skill)} MP",
                f"[yellow]exige {skill.requires.describe()}[/yellow]",
            )
        else:
            skill_table.add_row(
                str(key) + ".", skill.name, f"{player.skill_mana_cost(skill)} MP", ""
            )
    skill_table.add_row("0.", "Voltar", "", "")
    renderer.console.print(
        Panel(
            skill_table,
            title="[bold yellow]Escolha uma habilidade[/bold yellow]",
            border_style="yellow",
        )
    )


def render_skill_on_cooldown_message(skill_name: str, remaining: int) -> None:
    renderer.console.print(
        Panel(
            Text(
                f"{skill_name} está em recarga por {remaining} turno(s)!",
                justify="center",
                style="yellow",
            ),
            border_style="yellow",
        )
    )


def render_skill_requirement_message(skill_name: str, requisito: str) -> None:
    """A carta está no deck, mas a mão não tem o que ela pede.

    Dizer o que falta, em vez de só recusar: o requisito é um objetivo de build,
    e um "não pode usar" sem motivo o transformaria num bug aparente.
    """
    renderer.console.print(
        Panel(
            Text(
                f"{skill_name} exige {requisito}.",
                justify="center",
                style="yellow",
            ),
            border_style="yellow",
        )
    )


def render_battle_insufficient_mana_message() -> None:
    renderer.console.print(
        Panel(Text("Mana insuficiente!", justify="center", style="red"), border_style="red")
    )


def render_battle_no_potions_message() -> None:
    renderer.console.print(
        Panel(
            Text("Você não tem poções para usar!", justify="center", style="red"),
            border_style="red",
        )
    )


def render_potion_select_panel(potions: list[object]) -> None:
    potion_table = Table(show_header=False, expand=True, border_style="dim white")
    potion_table.add_column("Chave", style="bold blue", justify="right")
    potion_table.add_column("Poção", style="cyan")
    potion_table.add_column("Descrição", style="dim white")
    for i, potion in enumerate(potions, 1):
        potion_table.add_row(
            str(i) + ".", getattr(potion, "name", "?"), getattr(potion, "description", "")
        )
    potion_table.add_row("0.", "Voltar", "")
    renderer.console.print(
        Panel(
            potion_table,
            title="[bold yellow]Escolha uma poção[/bold yellow]",
            border_style="yellow",
        )
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
            Panel(
                Text("Você foi derrotado...", justify="center", style="bold red"),
                border_style="red",
            )
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


def render_shop_main(options: dict[str, str], player_coins: int) -> None:
    """Renderiza a tela principal da loja.

    As opções chegam prontas: quem monta o menu é o fluxo, que é quem sabe se há
    o que equipar e quanto custa o próximo reroll. Montá-lo aqui obrigava o
    fluxo a recalcular as mesmas teclas por fora, e as duas contas divergiam na
    primeira opção nova.
    """

    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Bem-vindo à Loja do Mercador!", justify="center", style="bold green"),
            border_style="green",
            subtitle=f"Seu Ouro: [bold yellow]{player_coins}[/bold yellow]",
        )
    )

    shop_options = options

    options_table = Table(
        show_header=False, expand=True, highlight=True, row_styles=["none", "dim"]
    )
    options_table.add_column("Opção", style="bold blue", justify="right")
    options_table.add_column("Descrição", style="cyan")

    for key, value in shop_options.items():
        options_table.add_row(key, value)

    renderer.console.print(options_table)
    renderer.console.print("\n")


def render_shop_reroll_success(paid: int, next_cost: int) -> None:
    """O reroll aconteceu — e o próximo já custa o dobro, na cara do jogador."""
    renderer.console.print(
        f"[bold yellow]Estoque renovado[/bold yellow] por [bold yellow]{paid}[/bold yellow] "
        f"de ouro. O próximo custa [bold red]{next_cost}[/bold red].",
        justify="center",
    )


def render_shop_reroll_denied(cost: int, coins: int) -> None:
    """Sem ouro não há reroll — e nada muda: nem estoque, nem contador."""
    renderer.console.print(
        f"[dim white]Renovar custa[/dim white] [bold yellow]{cost}[/bold yellow] "
        f"[dim white]e você tem[/dim white] [bold yellow]{coins}[/bold yellow].",
        justify="center",
    )


def render_recovery_menu(
    offers: list[dict], player_coins: int, hp: int, max_hp: int, mp: int, max_mp: int
) -> None:
    """Menu de recuperação paga: o preço do combate mal jogado, em ouro."""
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("Curandeiro do Mercado", justify="center", style="bold green"),
            border_style="green",
            subtitle=(
                f"Ouro: [bold yellow]{player_coins}[/bold yellow]  |  "
                f"HP {hp}/{max_hp}  |  MP {mp}/{max_mp}"
            ),
        )
    )

    if not offers:
        renderer.console.print(
            Panel(
                Text("Você já está inteiro. Guarde o seu ouro.", justify="center", style="cyan"),
                border_style="cyan",
            )
        )
        return

    tabela = Table(show_header=True, expand=True, row_styles=["none", "dim"])
    tabela.add_column("Opção", style="bold blue", justify="right")
    tabela.add_column("Recuperar", style="cyan")
    tabela.add_column("Preço", style="yellow", justify="right")
    for i, oferta in enumerate(offers, 1):
        pode = "" if player_coins >= oferta["price"] else " [red](sem ouro)[/red]"
        tabela.add_row(
            f"{i}.",
            f"+{oferta['amount']} de {oferta['label']}{pode}",
            str(oferta["price"]),
        )
    tabela.add_row("0.", "Voltar", "")
    renderer.console.print(tabela)
    renderer.console.print("\n")


def render_recovery_success(label: str, amount: int, price: int) -> None:
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"+[bold green]{amount}[/bold green] de {label} por "
                f"[bold yellow]{price}[/bold yellow] de ouro.",
                justify="center",
            ),
            border_style="green",
        )
    )


def render_interest_paid(amount: int, saldo: int, cap: int) -> None:
    """Juros do andar concluído.

    Mostra o teto junto: sem ele, o jogador que bateu no cap vê um número menor
    do que esperava e não tem como saber por quê — e "guardar capital" deixa de
    ser uma decisão informada.
    """
    if amount <= 0:
        return
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"Juros do andar: [bold yellow]+{amount}[/bold yellow] de ouro "
                f"(teto {cap}).  Saldo: [bold yellow]{saldo}[/bold yellow].",
                justify="center",
            ),
            title="[bold green]Rendimento[/bold green]",
            border_style="green",
        )
    )


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
                Text(
                    "O mercador não tem nada para vender no momento.",
                    justify="center",
                    style="dim white",
                ),
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
        item_table.add_row(
            str(i), item.display_name, str(price), getattr(item, "description", "Sem descrição")
        )
    item_table.add_row("0", "Voltar", "", "")

    renderer.console.print(item_table)
    renderer.console.print("\n")


def render_shop_purchase_success(item_name: str, price: int) -> None:
    """Renderiza mensagem de compra bem-sucedida."""
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"Você comprou [bold green]{item_name}[/bold green] "
                f"por [bold yellow]{price}[/bold yellow] ouro.",
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
            Text(
                "Você não tem ouro suficiente para comprar este item.",
                justify="center",
                style="red",
            ),
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
            Panel(
                Text("Você não tem itens para vender.", justify="center", style="dim white"),
                border_style="dim white",
            )
        )
        sleep(0.8)
        return

    player_inventory_table = Table(show_header=True, expand=True, border_style="dim white")
    player_inventory_table.add_column("ID", style="bold blue")
    player_inventory_table.add_column("Item", style="cyan")
    player_inventory_table.add_column("Preço Venda", style="yellow", justify="right")
    player_inventory_table.add_column("Descrição", style="dim white")

    for i, item in enumerate(inventory, 1):
        sell_price = shop.get_sell_price(item, dungeon_level)
        player_inventory_table.add_row(
            str(i),
            item.display_name,
            str(sell_price),
            getattr(item, "description", "Sem descrição"),
        )
    player_inventory_table.add_row("0", "Voltar", "", "")

    renderer.console.print(player_inventory_table)
    renderer.console.print("\n")


def render_shop_sell_success(item_name: str, sell_price: int) -> None:
    """Renderiza mensagem de venda bem-sucedida."""
    renderer.console.print(
        Panel(
            Text(
                f"Você vendeu [bold green]{item_name}[/bold green] "
                f"por [bold yellow]{sell_price}[/bold yellow] ouro.",
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
        Panel(
            Text("Escolha inválida. Tente novamente.", justify="center", style="red"),
            border_style="red",
        )
    )
    sleep(0.8)


def render_shop_farewell() -> None:
    """Renderiza mensagem de despedida da loja."""
    renderer.console.print(
        Panel(
            Text(
                "Você se despede do mercador e volta à aventura.",
                justify="center",
                style="dim white",
            ),
            border_style="dim white",
        )
    )
    sleep(0.8)


def render_shop_equip_prompt(item_name: str, slot: str, bonus_text: str) -> None:
    """Prompt interativo para equipar direto da loja quando slot vazio."""
    slot_names = SLOT_LABELS
    slot_label = slot_names.get(slot, slot)
    body = Text(justify="center")
    body.append(f"Slot {slot_label} está vazio!\n", style="bold green")
    body.append(f"Equipar {item_name} agora te dá ", style="white")
    body.append(f"{bonus_text}", style="bold green")
    body.append(" sem perder nada.\n\n", style="white")
    body.append("Deseja equipar agora?\n", style="yellow")
    body.append("[S] Sim  |  [N] Não (fica na mochila)", style="dim")
    renderer.console.print(Panel(body, border_style="green", title="Equipar agora?"))


def render_position_choice(item_name: str, ocupantes: list[tuple[str, str]]) -> None:
    """Pergunta qual peça sai quando todas as posições da categoria estão cheias.

    Só aparece com mais de uma posição possível e nenhuma livre: com vaga, o
    personagem resolve sozinho. Sem isto, um segundo anel sempre substituía o
    primeiro, e o jogador não tinha como escolher.
    """
    body = Text(justify="left")
    body.append(f"{item_name}\n\n", style="bold cyan")
    body.append("Todas as posições estão ocupadas. Qual peça sai?\n\n", style="yellow")
    for i, (posicao, ocupante) in enumerate(ocupantes, start=1):
        body.append(f"  [{i}] ", style="bold white")
        body.append(f"{SLOT_LABELS.get(posicao, posicao)}: ", style="white")
        body.append(f"{ocupante}\n", style="dim")
    body.append("\n  [C] Cancelar", style="dim")
    renderer.console.print(Panel(body, border_style="cyan", title="Substituir qual?"))


def render_shop_swap_comparison(new_item, old_item, slot: str) -> None:
    """Mostra comparação simples antigo vs novo ao trocar na loja."""
    slot_names = SLOT_LABELS
    slot_label = slot_names.get(slot, slot)
    renderer.console.print(
        Panel(
            Text(f"Trocar equipamento - {slot_label}", justify="center", style="bold yellow"),
            border_style="yellow",
        )
    )
    table = Table(show_header=True, expand=True, border_style="dim white")
    table.add_column("Atributo", style="bold white")
    table.add_column("Equipado", style="cyan", justify="center")
    table.add_column("Novo", style="green", justify="center")
    table.add_column("Diferença", style="yellow", justify="center")

    def _fmt(v):
        return str(v) if v else "-"

    attrs = []
    ndmg = getattr(new_item, "damage_bonus", 0)
    odmg = getattr(old_item, "damage_bonus", 0)
    if ndmg or odmg:
        attrs.append(("Dano", odmg, ndmg))
    ndef = getattr(new_item, "defense_bonus", 0)
    odef = getattr(old_item, "defense_bonus", 0)
    if ndef or odef:
        attrs.append(("Defesa", odef, ndef))
    neff = getattr(new_item, "effect_type", None)
    oeff = getattr(old_item, "effect_type", None)
    neffv = getattr(new_item, "effect_value", 0)
    oeffv = getattr(old_item, "effect_value", 0)
    if neff or oeff:
        # efeito como linha única se tipos iguais, senão duas linhas
        if neff == oeff and neff:
            diff = neffv - oeffv
            diff_str = f"{diff:+d}" if diff else "="
            table.add_row(f"Efeito ({neff})", str(oeffv), str(neffv), diff_str)
        else:
            if oeff:
                table.add_row(f"Efeito ({oeff})", str(oeffv), "-", "-")
            if neff:
                table.add_row(f"Efeito ({neff})", "-", str(neffv), "-")
    for label, old_v, new_v in attrs:
        diff = new_v - old_v
        if diff > 0:
            diff_str = f"[green]+{diff}[/green]"
        elif diff < 0:
            diff_str = f"[red]{diff}[/red]"
        else:
            diff_str = "[yellow]=[/yellow]"
        # usar Text para valores, mas tabela aceita markup via Text.from_markup? Mantém simples
        table.add_row(label, _fmt(old_v), _fmt(new_v), diff_str)

    if not attrs and not (neff or oeff):
        table.add_row("Bônus", "-", "-", "[yellow]=[/yellow]")

    renderer.console.print(table)
    # Resumo (ASCII para compatibilidade Windows cp1252)
    total_new = getattr(new_item, "damage_bonus", 0) + getattr(new_item, "defense_bonus", 0)
    total_old = getattr(old_item, "damage_bonus", 0) + getattr(old_item, "defense_bonus", 0)
    if total_new > total_old:
        resumo = "[bold green]>> Upgrade geral[/bold green]"
    elif total_new < total_old:
        resumo = "[bold red]<< Downgrade geral[/bold red]"
    else:
        resumo = "[bold yellow]== Equivalente[/bold yellow] -- escolha por efeito/raridade"
    renderer.console.print(
        Panel(
            Text.from_markup(
                f"Equipado: {old_item.display_name}\nNovo: {new_item.display_name}\n{resumo}\n\n"
                "[S] Equipar agora  |  [N] Manter na mochila",
                justify="center",
            ),
            border_style="cyan",
            title="Equipar?",
        )
    )


def render_shop_old_sell_prompt(old_item_name: str, sell_price: int, slot: str) -> None:
    """Pergunta se deseja vender/descartar o item antigo após troca."""
    slot_names = SLOT_LABELS
    label = slot_names.get(slot, slot)
    body = Text(justify="center")
    body.append(f"{old_item_name} foi para a mochila (slot {label}).\n", style="white")
    body.append(f"Vender agora por {sell_price} ouro?\n\n", style="bold yellow")
    body.append("[S] Vender  |  [D] Descartar  |  [N] Manter na mochila", style="dim")
    renderer.console.print(Panel(body, border_style="yellow", title="O que fazer com o antigo?"))


def render_shop_old_discarded(item_name: str) -> None:
    renderer.console.print(
        Panel(
            Text(f"{item_name} descartado.", justify="center", style="dim"),
            border_style="dim",
        )
    )
    sleep(0.6)


def render_shop_old_kept(item_name: str) -> None:
    renderer.console.print(
        Panel(
            Text(f"{item_name} mantido na mochila.", justify="center", style="dim"),
            border_style="dim",
        )
    )
    sleep(0.6)


def render_shop_equip_inventory_empty() -> None:
    renderer.console.print(
        Panel(
            Text("Nenhum item equipável na mochila.", justify="center", style="dim white"),
            border_style="dim white",
        )
    )
    sleep(0.8)


def render_shop_equip_success(item_name: str, slot: str) -> None:
    slot_names = SLOT_LABELS
    slot_label = slot_names.get(slot, slot)
    renderer.console.print(
        Panel(
            Text(
                f"{item_name} equipado em {slot_label}! Bônus aplicado.",
                justify="center",
                style="bold green",
            ),
            border_style="green",
        )
    )
    sleep(0.8)


def render_shop_equip_failed(msg: str) -> None:
    renderer.console.print(
        Panel(
            Text(f"Não foi possível equipar: {msg}", justify="center", style="red"),
            border_style="red",
        )
    )
    sleep(0.8)


def render_shop_kept_in_inventory(item_name: str) -> None:
    renderer.console.print(
        Panel(
            Text(
                f"{item_name} guardado na mochila. Equipe quando quiser via inventário (I).",
                justify="center",
                style="dim",
            ),
            border_style="dim",
        )
    )
    sleep(0.6)


# =============================================================================
# INVENTÁRIO - Funções puras de renderização
# =============================================================================


def _create_inventory_header_panel(player: "Player") -> Panel:
    """Cria o painel de cabeçalho do inventário."""
    return Panel(
        Text("Mochila e Equipamentos", justify="center", style="bold green"),
        border_style="green",
        subtitle=f"Ouro: [bold yellow]{player.coins}[/bold yellow]",
    )


def _create_equipment_table(player: "Player") -> Table:
    """Cria a tabela de equipamentos do jogador."""
    equip_table = Table(
        title="[bold cyan]--- Equipamento ---[/bold cyan]",
        show_header=False,
        expand=True,
        border_style="dim cyan",
    )
    equip_table.add_column("Slot", style="bold blue")
    equip_table.add_column("Item", style="cyan")

    for slot, item in player.equipment.items():
        if item:
            equip_table.add_row(slot.capitalize(), item.display_name)
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
        border_style="dim magenta",
    )
    inv_table.add_column("ID", style="bold blue", justify="right")
    inv_table.add_column("Item", style="cyan")
    inv_table.add_column("Tipo", style="yellow")

    for i, item in enumerate(player.inventory):
        inv_table.add_row(str(i + 1), item.display_name, item.__class__.__name__)

    return inv_table


def _render_empty_inventory_message() -> None:
    """Renderiza mensagem de inventário vazio."""
    renderer.console.print(
        Panel(
            Text("Sua mochila está vazia.", justify="center", style="dim white"),
            border_style="dim white",
        )
    )


def render_dungeon_status(
    dungeon_level: int,
    hp: int,
    max_hp: int,
    mp: int,
    max_mp: int,
    essence_multiplier: float = 1.0,
) -> None:
    """Renderiza o status da masmorra na parte superior da tela."""
    # Determina a cor do multiplicador baseado no valor. Os limiares vêm de
    # `shared/constants.py`, derivados da média e do desvio do sorteio: com os
    # valores digitados aqui, apertar o desvio deixava a tela pintando de verde
    # um andar que passou a ser comum.
    if essence_multiplier < ESSENCE_MULT_POOR:
        mult_color = "red"
    elif essence_multiplier > ESSENCE_MULT_GOOD:
        mult_color = "green"
    else:
        mult_color = "yellow"

    status_text = (
        f"Masmorra Nível {dungeon_level} | "
        f"Multiplicador: [{mult_color}]{essence_multiplier}x[/] | "
        f"HP: {hp}/{max_hp} | MP: {mp}/{max_mp}"
    )
    renderer.console.print(Text.from_markup(status_text, style="bold cyan"))
    renderer.console.print(Text("Use 'w', 'a', 's', 'd' para mover.", style="dim"))


def render_dungeon_controls() -> None:
    """Renderiza os controles disponíveis no mapa."""
    renderer.console.print("\n[dim](i)nventário | (c) status | (p)ara Salvar | (q) para Sair[/dim]")


def render_game_saved(message: str = "Jogo salvo!") -> None:
    """Renderiza mensagem de confirmação de salvamento."""
    renderer.console.print(
        Panel(Text(message, justify="center", style="green"), border_style="green")
    )
    sleep(0.8)


def render_level_complete(dungeon_level: int) -> None:
    """Renderiza mensagem de conclusão de nível."""
    renderer.console.print(
        Panel(
            Text(
                f"Você completou a Masmorra Nível {dungeon_level}!",
                justify="center",
                style="bold green",
            ),
            border_style="green",
        )
    )
    renderer.console.print(
        Panel(
            Text(
                "Pressione qualquer tecla para avançar para o próximo nível...",
                justify="center",
                style="yellow",
            ),
            border_style="yellow",
        )
    )


def render_extraction_prompt(
    player_name: str,
    dungeon_level: int,
    xp_points: int,
    level: int,
    hp: int,
    max_hp: int,
    coins: int,
    essence_multiplier: float = 1.0,
) -> None:
    """Tela de decisão entre EXTRAIR (preservar) e CONTINUAR (arriscar)."""
    renderer.console.print(
        Panel(
            Text("- Decisão de Extração -", justify="center", style="bold yellow"),
            border_style="yellow",
        )
    )
    body = Text(justify="center")
    body.append(f"Andar concluído: {dungeon_level}\n", style="bold cyan")
    body.append(
        f"Aventureiro: {player_name}  |  Nível: {level}  |  HP: {hp}/{max_hp}  |  Ouro: {coins}\n",
        style="white",
    )
    body.append(f"Essência acumulada (XP): {xp_points}\n", style="bold green")
    body.append(
        f"Estimativa para o próximo andar: ~{essence_multiplier}x "
        f"(faixa {ESSENCE_MULT_MIN}x - {ESSENCE_MULT_MAX}x)\n",
        style="dim cyan",
    )
    body.append("Valor exato só é sorteado ao entrar - pode variar.\n\n", style="dim")
    body.append("Se você CONTINUAR e morrer no próximo andar,\n", style="bold red")
    body.append(
        "toda a essência, nível e progresso desta run serão perdidos (permadeath).\n", style="red"
    )
    body.append("Se você EXTRAIR, a run encerra agora e seu personagem\n", style="bold green")
    body.append("é preservado com tudo que conquistou até aqui.\n", style="green")
    body.append("Custa a sua Chave de Extração.\n", style="bold yellow")
    renderer.console.print(Panel(body, border_style="cyan", title="Extrair ou Continuar?"))
    renderer.console.print(
        Text(
            "[1] EXTRAIR  - encerrar e preservar  |  [2] CONTINUAR - descer",
            justify="center",
            style="bold white",
        )
    )
    renderer.console.print(Text("Escolha 1 ou 2 e pressione ENTER.", justify="center", style="dim"))


def render_extraction_no_key(dungeon_level: int) -> None:
    """A casa da Extração sem a Chave. Ela fica; o que falta é o preço."""
    renderer.console.print(
        Panel(
            Text(
                f"Portal de Extração do andar {dungeon_level}.\n"
                "Falta a CHAVE DE EXTRAÇÃO — ela cai de monstro derrotado, e só de lá.\n"
                "O portal continua aqui enquanto você estiver neste andar.",
                justify="center",
                style="yellow",
            ),
            border_style="yellow",
            title="Portal trancado",
        )
    )


def render_extraction_failed(dungeon_level: int) -> None:
    """A gravação falhou. Nada foi cobrado, e a run continua de pé."""
    renderer.console.print(
        Panel(
            Text(
                f"A Extração do andar {dungeon_level} NÃO foi concluída:\n"
                "não foi possível gravar o personagem.\n"
                "Sua Chave continua com você e o portal continua aqui — "
                "a run não foi encerrada.",
                justify="center",
                style="bold red",
            ),
            border_style="red",
            title="Extração falhou",
        )
    )


def render_extraction_success(dungeon_level: int) -> None:
    """Confirmação após extração bem-sucedida."""
    renderer.console.print(
        Panel(
            Text(
                f"Extração concluída no andar {dungeon_level}!\nSeu progresso foi preservado.",
                justify="center",
                style="bold green",
            ),
            border_style="green",
        )
    )
    sleep(0.8)


def render_continue_prompt() -> None:
    """Renderiza prompt para continuar jornada."""
    renderer.console.print(
        Panel(
            Text(
                "Pressione qualquer tecla para continuar sua jornada...",
                justify="center",
                style="yellow",
            ),
            border_style="yellow",
        )
    )


def render_map(map_lines: list[str]) -> None:
    """Renderiza as linhas do mapa no console com cores."""

    for line in map_lines:
        colored_line = Text()
        for char in line:
            if char == "@":
                colored_line.append(char, style="bold green")
            elif char == "&":
                colored_line.append(char, style="bold red")
            elif char == "B":
                colored_line.append(char, style="bold magenta")
            elif char == "X":
                colored_line.append(char, style="dim")
            elif char == "D":
                colored_line.append(char, style="bold yellow")
            else:
                colored_line.append(char, style="white")
        renderer.console.print(colored_line)


def _rodape_oferta(reroll_cost: int | None, coins: int | None, sufixo: str = "") -> str:
    """A linha do rodapé das telas de oferta, com o preço do próximo reroll.

    O preço fica visível SEMPRE, e não escondido atrás de um submenu: a decisão
    que o reroll cria é ver 150 virar 300 virar 600 e apertar de novo assim
    mesmo. Escondê-lo transformaria a curva exponencial numa surpresa.
    """
    partes = []
    if reroll_cost is not None:
        preço = f"[R] Trocar a oferta — {reroll_cost} ouro"
        if coins is not None and coins < reroll_cost:
            preço += f" (você tem {coins})"
        partes.append(preço)
    if sufixo:
        partes.append(sufixo)
    return "   |   ".join(partes)


def render_offer_reroll_denied(cost: int, coins: int) -> None:
    """Sem ouro, a oferta fica como está — e a tentativa não conta."""
    renderer.console.print(
        f"[dim white]Trocar custa[/dim white] [bold yellow]{cost}[/bold yellow] "
        f"[dim white]e você tem[/dim white] [bold yellow]{coins}[/bold yellow].",
        justify="center",
    )


def render_passive_selection(
    choices: list, reroll_cost: int | None = None, coins: int | None = None
) -> None:
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
                Text.from_markup(f"[bold {color}]{name}[/bold {color}]\n[dim]{description}[/dim]"),
                title=f"[bold]{i}. [{rarity}] [{category}][/bold]",
                border_style=color,
            )
        )
    if reroll_cost is not None:
        renderer.console.print(
            Panel(
                Text(_rodape_oferta(reroll_cost, coins), justify="center", style="dim"),
                border_style="dim",
            )
        )


def render_passive_acquired(message: str) -> None:
    """Renderiza confirmação de passiva adquirida."""
    renderer.console.print(
        Panel(Text(message, justify="center", style="bold green"), border_style="green")
    )
    sleep(1.5)


def _dano_previsto(card, player) -> str:
    """O que esta carta faria na mão deste herói, agora.

    Sem herói (uma tela de catálogo, um teste) não há resposta honesta: o dano
    da V2 não existe fora de um personagem. Devolve "?" em vez de inventar.
    """
    if player is None:
        return "?"
    from src.content.skills_loader import damage_preview

    return str(damage_preview(card, player))


def render_skill_selection(
    choices: list,
    player: "Player" | None = None,
    reroll_cost: int | None = None,
    coins: int | None = None,
) -> None:
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
        # O custo percentual só existe em relação a um herói. Sem ele, cai no
        # valor absoluto do JSON em vez de exibir um número inventado.
        mana_cost = (
            player.skill_mana_cost(card) if player is not None else getattr(card, "mana_cost", 0)
        )
        effect_type = getattr(card, "effect_type", "")
        effect_value = getattr(card, "effect_value", 0)
        description = getattr(card, "description", "")

        # Mostra o valor do efeito de forma legível
        if effect_type == "damage":
            # O dano REAL desta carta para ESTE herói. Depois da V2 a carta não
            # carrega número de dano — `effect_value` é sempre zero —, e a tela
            # anunciava "Dano: 0" em todas as cartas de dano do jogo. O número
            # útil é o que o motor vai calcular, e ele já depende dos atributos,
            # do equipamento e das gemas de quem está escolhendo.
            effect_text = f"Dano: {_dano_previsto(card, player)}"
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
            Text(_rodape_oferta(reroll_cost, coins, "Pressione 0 para cancelar"), justify="center"),
            border_style="dim",
        )
    )


def _resumo_de_poder(skill, player) -> str:
    """Uma linha comparável entre as cinco cartas da tela de substituição.

    Trocar uma carta por outra é a decisão mais cara do deck e ela era tomada
    às cegas: a tela mostrava só nome, custo e descrição. Dano contra dano é o
    mínimo para a escolha ser uma escolha.
    """
    tipo = getattr(skill, "effect_type", "")
    if tipo == "damage":
        return f"Dano: {_dano_previsto(skill, player)}"
    if tipo == "heal":
        return f"Cura: {getattr(skill, 'effect_value', 0)}% do HP máximo"
    if tipo == "status":
        return f"Status: {getattr(skill, 'effect_value', '')}"
    if tipo == "buff":
        return f"Buff: +{getattr(skill, 'effect_value', 0)}"
    return str(getattr(skill, "effect_value", ""))


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
                f"[dim]Custo: {player.skill_mana_cost(new_skill)} MP "
                f"| {_resumo_de_poder(new_skill, player)}[/dim]\n"
                f"[dim]{new_skill.description}[/dim]"
            ),
            title="[bold green]Nova Skill[/bold green]",
            border_style="green",
        )
    )

    # Mostra as 4 skills atuais
    renderer.console.print(
        Panel(
            Text(
                "Escolha qual skill substituir (1-4) ou 0 para cancelar:",
                justify="center",
                style="bold yellow",
            ),
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
                    f"[dim]Custo: {player.skill_mana_cost(skill)} MP "
                    f"| {_resumo_de_poder(skill, player)}[/dim]\n"
                    f"[dim]{skill.description}[/dim]"
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
        Panel(
            Text("Skill não substituída.", justify="center", style="bold yellow"),
            border_style="yellow",
        )
    )
    sleep(1.0)


# --- Eventos Aleatórios ---


def render_merchant_event(offers: list[dict], coins: int) -> None:
    """Tela do Mercador Errante: mostra ofertas raras com preço."""
    renderer.console.print(
        Panel(
            Text("- Mercador Errante -", justify="center", style="bold yellow"),
            border_style="yellow",
        )
    )
    body = Text(justify="center")
    body.append("Um mercador surge da neblina com itens raros.\n", style="italic cyan")
    body.append(f"Seu ouro: {coins}\n\n", style="bold white")
    for idx, entry in enumerate(offers, 1):
        item = entry["item"]
        price = entry["price"]
        name = getattr(item, "name", "?")
        rarity = getattr(item, "rarity", "Common")
        desc = getattr(item, "description", "")
        body.append(f"[{idx}] {name} [{rarity}] - {price} ouro\n", style="yellow")
        if desc:
            body.append(f"    {desc}\n", style="dim")
    renderer.console.print(Panel(body, border_style="cyan", title="Ofertas"))
    renderer.console.print(Text("[1-3] Comprar  |  [0] Sair", justify="center", style="dim"))


def render_merchant_purchase_success(item_name: str, price: int) -> None:
    renderer.console.print(
        Panel(
            Text(
                f"Você comprou {item_name} por {price} ouro!", justify="center", style="bold green"
            ),
            border_style="green",
        )
    )
    sleep(0.8)


def render_altar_event(cost_hp: int, player_hp: int, max_hp: int) -> None:
    """Tela do Altar: escolha de risco/recompensa."""
    renderer.console.print(
        Panel(
            Text("- Altar Sombrio -", justify="center", style="bold red"),
            border_style="red",
        )
    )
    body = Text(justify="center")
    body.append("O altar pulsa com energia sombria.\n", style="italic white")
    body.append(f"Sacrifício: {cost_hp} HP (você tem {player_hp}/{max_hp})\n", style="bold red")
    body.append("Recompensa: Benção do Altar (+15 dano por 5 turnos)\n\n", style="bold green")
    body.append("O que você faz?\n", style="white")
    body.append("[1] Sacrificar HP e receber a benção\n", style="yellow")
    body.append("[2] Recusar e partir\n", style="dim")
    renderer.console.print(Panel(body, border_style="magenta"))


def render_altar_success() -> None:
    renderer.console.print(
        Panel(
            Text(
                "O altar consome seu sangue e concede a Benção do Altar!",
                justify="center",
                style="bold magenta",
            ),
            border_style="magenta",
        )
    )
    sleep(0.8)


def render_altar_refused() -> None:
    renderer.console.print(
        Panel(
            Text("Você recusa o pacto e se afasta do altar.", justify="center", style="dim"),
            border_style="dim",
        )
    )
    sleep(0.6)


def render_altar_no_hp() -> None:
    renderer.console.print(
        Panel(
            Text("Você está fraco demais para o sacrifício.", justify="center", style="bold red"),
            border_style="red",
        )
    )
    sleep(0.8)


def render_fountain_event(heal_amount: int, player_hp: int, max_hp: int) -> None:
    """Tela da Fonte: cura sem custo."""
    renderer.console.print(
        Panel(
            Text("- Fonte Cristalina -", justify="center", style="bold blue"),
            border_style="blue",
        )
    )
    body = Text(justify="center")
    body.append("Águas cristalinas brilham à sua frente.\n", style="italic cyan")
    body.append(
        f"Beber cura {heal_amount} HP (você tem {player_hp}/{max_hp})\n\n", style="bold green"
    )
    body.append("[1] Beber da fonte  |  [2] Ignorar\n", style="white")
    renderer.console.print(Panel(body, border_style="blue"))


def render_fountain_healed(healed: int, potion_name: str | None = None) -> None:
    text = f"Você bebeu e recuperou {healed} HP!"
    if potion_name:
        text += f"\nEncontrou: {potion_name}!"
    renderer.console.print(
        Panel(
            Text(text, justify="center", style="bold green"),
            border_style="green",
        )
    )
    sleep(0.8)


def render_fountain_ignored() -> None:
    renderer.console.print(
        Panel(
            Text("Você ignora a fonte e segue em frente.", justify="center", style="dim"),
            border_style="dim",
        )
    )
    sleep(0.5)


def render_character_status(player) -> None:
    """Tela dedicada de Status do Personagem - consolidada."""
    from src.ui.navigation_menu import escape_markup

    # Cabeçalho
    title = f"{player.get_nick_name()} - {player.get_classname()}  |  Nível {player.get_level()}"
    renderer.console.print(
        Panel(Text(title, justify="center", style="bold cyan"), border_style="cyan")
    )

    # XP
    try:
        xp_atual = player.xp_points
        xp_needed = player.need_to_next()
        xp_total = player.need_to_up()
    except Exception:
        xp_atual = getattr(player, "xp_points", 0)
        xp_needed = 0
        xp_total = 0
    xp_text = (
        f"XP: {xp_atual} / {xp_total}  (falta {xp_needed} pro próximo nível)"
        if xp_total
        else f"XP: {xp_atual}"
    )
    renderer.console.print(
        Panel(Text(xp_text, justify="center", style="green"), border_style="green")
    )

    # HP/MP
    try:
        hp = player.get_hp()
        max_hp = getattr(player, "base_hp", hp)
        mp = player.get_mp()
        max_mp = getattr(player, "base_mp", mp)
    except Exception:
        hp = max_hp = mp = max_mp = 0
    hp_mp_text = f"HP: {hp}/{max_hp}   |   MP: {mp}/{max_mp}"
    renderer.console.print(
        Panel(Text(hp_mp_text, justify="center", style="bold white"), border_style="white")
    )

    # Atributos base
    try:
        atk = (
            player.get_avg_damage()
            if hasattr(player, "get_avg_damage")
            else getattr(player, "avg_damage", 0)
        )
        base_df = getattr(player, "base_df", getattr(player, "base_ag", 0))
        base_ag = getattr(player, "base_ag", 0)
        base_st = getattr(player, "base_st", 0)
        base_mg = getattr(player, "base_mg", 0)
        attrs_text = (
            f"ATK: {atk}  |  DEF: {base_df}  |  AGI: {base_ag}  |  ST: {base_st}  |  MG: {base_mg}"
        )
    except Exception:
        attrs_text = "Atributos indisponíveis"
    renderer.console.print(
        Panel(
            Text(attrs_text, justify="center", style="yellow"),
            border_style="yellow",
            title="Atributos",
        )
    )

    # Equipamento
    if hasattr(player, "equipment") and isinstance(player.equipment, dict):
        equip_lines = []
        slot_names = SLOT_LABELS
        has_any = False
        for slot, item in player.equipment.items():
            label = slot_names.get(slot, slot)
            if item:
                has_any = True
                equip_lines.append(f"[{label}] {escape_markup(getattr(item, 'name', str(item)))}")
            else:
                equip_lines.append(f"[{label}] [dim]Vazio[/dim]")
        if not has_any and not equip_lines:
            equip_text = "Nenhum equipamento"
        else:
            equip_text = "\n".join(equip_lines) if equip_lines else "Nenhum equipamento"
    else:
        equip_text = "Nenhum equipamento"
    renderer.console.print(
        Panel(Text.from_markup(equip_text), border_style="magenta", title="Equipamento")
    )

    # Passivas
    passives = getattr(player, "passives", [])
    if passives:
        passive_lines = []
        for p in passives:
            name = escape_markup(getattr(p, "name", str(p)))
            desc = escape_markup(getattr(p, "description", ""))
            rarity = getattr(p, "rarity", "")
            passive_lines.append(f"- {name} [{rarity}] {desc}")
        passive_text = "\n".join(passive_lines)
    else:
        passive_text = "[dim]Nenhuma passiva ativa[/dim]"
    renderer.console.print(
        Panel(Text.from_markup(passive_text), border_style="blue", title="Passivas")
    )

    # Cooldowns
    cooldowns = getattr(player, "skill_cooldowns", {})
    if cooldowns:
        cd_lines = []
        for sid, rem in cooldowns.items():
            # Tenta resolver nome da skill pelo id
            skill_name = sid
            try:
                from src.content.skills_loader import get_skill_by_id

                sc = get_skill_by_id(sid)
                if sc:
                    skill_name = sc.name
            except Exception:
                pass
            cd_lines.append(f"{escape_markup(skill_name)}: {rem} turno(s)")
        cd_text = "\n".join(cd_lines)
    else:
        cd_text = "[dim]Nenhum cooldown ativo[/dim]"
    renderer.console.print(
        Panel(Text.from_markup(cd_text), border_style="yellow", title="Cooldowns")
    )

    # Efeitos temporários
    active_effects = getattr(player, "active_effects", {})
    active_buffs = getattr(player, "active_buffs", {})
    effect_lines = []
    for name, data in {**active_effects, **active_buffs}.items():
        try:
            dur = data.get("duration", "?") if isinstance(data, dict) else "?"
            val = data.get("value", "") if isinstance(data, dict) else ""
            val_str = f" (+{val})" if val != "" else ""
            effect_lines.append(f"{escape_markup(str(name))}{val_str} - {dur} turno(s) restantes")
        except Exception:
            effect_lines.append(f"{escape_markup(str(name))}")
    if effect_lines:
        effect_text = "\n".join(effect_lines)
    else:
        effect_text = "[dim]Nenhum efeito temporário[/dim]"
    renderer.console.print(
        Panel(Text.from_markup(effect_text), border_style="red", title="Efeitos Temporários")
    )

    renderer.console.print(
        Panel(Text("[Q] Voltar", justify="center", style="dim"), border_style="dim")
    )


# --- Ferreiro ---------------------------------------------------------------
# Texto direto, sem enfeite: o que importa é o jogador ver o preço antes de
# apertar, e ver que ele subiu depois.


def render_forge_main(coins: int, gem_count: int) -> None:
    renderer.console.clear()
    renderer.console.print(
        Panel(
            Text("FERREIRO", justify="center", style="bold yellow"),
            border_style="yellow",
            subtitle=(
                f"Ouro: [bold yellow]{coins}[/bold yellow]  |  "
                f"Gemas na bolsa: [bold cyan]{gem_count}[/bold cyan]"
            ),
        )
    )
    for chave, rotulo in (("1", "Aprimorar"), ("2", "Gemas"), ("3", "Encantar"), ("0", "Voltar")):
        renderer.console.print(f"  [bold blue]{chave}[/bold blue]  [cyan]{rotulo}[/cyan]")
    renderer.console.print("")


def _linha_preco(indice: int, texto: str, preco: int, coins: int) -> str:
    cor = "yellow" if coins >= preco else "red"
    return f"  [bold blue]{indice}[/bold blue]  {texto} — [bold {cor}]{preco}[/bold {cor}] ouro"


def render_forge_enhance_menu(items: list, costs: list[int], coins: int) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text("Aprimorar", justify="center", style="bold yellow")))
    for i, (item, custo) in enumerate(zip(items, costs, strict=False), 1):
        proximo = int(getattr(item, "enhancement_level", 0) or 0) + 1
        renderer.console.print(_linha_preco(i, f"{item.display_name} → +{proximo}", custo, coins))
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_gem_items(items: list, bag: list) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text("Gemas", justify="center", style="bold yellow")))
    for i, item in enumerate(items, 1):
        cravadas = sum(1 for g in item.gems if g is not None)
        renderer.console.print(
            f"  [bold blue]{i}[/bold blue]  {item.display_name} "
            f"[dim]({cravadas}/{item.socket_count} sockets)[/dim]"
        )
    renderer.console.print(f"\n  [dim]Bolsa: {len(bag)} gema(s)[/dim]")
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_sockets(
    item, bag: list, socket_price: int, unsocket_price: int, coins: int
) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text(item.display_name, justify="center", style="bold yellow")))
    for i, gem in enumerate(item.gems, 1):
        if gem is None:
            renderer.console.print(
                _linha_preco(i, "[dim]Vazio[/dim] — engastar", socket_price, coins)
            )
        else:
            renderer.console.print(
                _linha_preco(i, f"{gem.display_name} — retirar", unsocket_price, coins)
            )
    renderer.console.print(
        f"\n  [dim]Bolsa: {', '.join(g.display_name for g in bag) or 'vazia'}[/dim]"
    )
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_gem_bag(bag: list) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text("Qual gema?", justify="center", style="bold yellow")))
    for i, gem in enumerate(bag, 1):
        renderer.console.print(
            f"  [bold blue]{i}[/bold blue]  {gem.display_name} "
            f"[dim](+{gem.percent:.0f}% {gem.stat})[/dim]"
        )
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_enchant_items(items: list, dungeon_level: int) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text("Encantar", justify="center", style="bold yellow")))
    for i, item in enumerate(items, 1):
        renderer.console.print(
            f"  [bold blue]{i}[/bold blue]  {item.display_name} "
            f"[dim]({len(item.enchantments)} encantamento(s))[/dim]"
        )
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_enchant_layers(item, add_price, swap_prices: list[int], coins: int) -> None:
    renderer.console.clear()
    renderer.console.print(Panel(Text(item.display_name, justify="center", style="bold yellow")))
    for i, encanto in enumerate(item.enchantments, 1):
        renderer.console.print(
            _linha_preco(i, f"{encanto.display_name} — reencantar", swap_prices[i - 1], coins)
        )
    if add_price is not None:
        cor = "yellow" if coins >= add_price else "red"
        renderer.console.print(
            f"  [bold blue]A[/bold blue]  Adicionar encantamento — "
            f"[bold {cor}]{add_price}[/bold {cor}] ouro"
        )
    else:
        renderer.console.print("  [dim]Peça no limite de encantamentos.[/dim]")
    renderer.console.print("  [bold blue]0[/bold blue]  Voltar\n")


def render_forge_enhanced(name: str, paid: int) -> None:
    renderer.console.print(
        f"[bold green]{name}[/bold green] — pago [bold yellow]{paid}[/bold yellow] de ouro.",
        justify="center",
    )
    sleep(0.8)


def render_forge_socketed(gem: str, item: str, paid: int) -> None:
    renderer.console.print(
        f"[bold cyan]{gem}[/bold cyan] cravada em [bold green]{item}[/bold green] "
        f"por [bold yellow]{paid}[/bold yellow].",
        justify="center",
    )
    sleep(0.8)


def render_forge_unsocketed(gem: str, paid: int) -> None:
    renderer.console.print(
        f"[bold cyan]{gem}[/bold cyan] voltou para a bolsa por [bold yellow]{paid}[/bold yellow].",
        justify="center",
    )
    sleep(0.8)


def render_forge_enchanted(label: str, paid: int) -> None:
    renderer.console.print(
        f"[bold magenta]{label}[/bold magenta] — pago [bold yellow]{paid}[/bold yellow].",
        justify="center",
    )
    sleep(0.8)


def render_forge_denied(cost: int, coins: int) -> None:
    renderer.console.print(
        f"[dim white]Custa[/dim white] [bold yellow]{cost}[/bold yellow] "
        f"[dim white]e você tem[/dim white] [bold yellow]{coins}[/bold yellow].",
        justify="center",
    )
    sleep(0.8)


def render_forge_empty(message: str) -> None:
    renderer.console.print(f"[dim white]{message}[/dim white]", justify="center")
    sleep(0.8)


def render_exit_paid(fee: int) -> None:
    renderer.console.print(
        f"[dim white]Taxa de saída:[/dim white] [bold yellow]{fee}[/bold yellow] de ouro.",
        justify="center",
    )
    sleep(0.6)


def render_exit_unpaid(fee: int, coins: int, streak: int, penalty: float) -> None:
    """Subiu sem pagar. Não há dívida — há Essência a menos no próximo andar."""
    renderer.console.print(
        f"[bold red]Saída não paga[/bold red]: custa [bold yellow]{fee}[/bold yellow] "
        f"e você tem [bold yellow]{coins}[/bold yellow]. "
        f"[dim white]{streak}ª seguida — Essência -{penalty:.1f}x no próximo andar.[/dim white]",
        justify="center",
    )
    sleep(1.2)


def render_essence_penalty(rolled: float, penalty: float, effective: float) -> None:
    """As três linhas que o jogador precisa ver: roll, desconto e resultado."""
    renderer.console.print(
        f"[dim white]Essência:[/dim white] [bold]{rolled:.1f}x[/bold] "
        f"[dim white]— penalidade de saída[/dim white] [bold red]-{penalty:.1f}x[/bold red] "
        f"[dim white]= efetiva[/dim white] [bold cyan]{effective:.1f}x[/bold cyan]",
        justify="center",
    )
    sleep(0.8)
