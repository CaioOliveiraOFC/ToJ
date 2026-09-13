"""Progressão do herói durante uma run simulada.

A simulação de run media um herói que subia de nível mas nunca escolhia passiva,
nunca aprendia skill nova, nunca pegava loot e nunca trocava de equipamento na
loja. Ele atravessava vinte andares com quatro skills comuns, o equipamento do
andar 1 e nenhuma passiva — enquanto o jogo real dá dezenove passivas, oito
escolhas de skill, drops a cada vitória e uma loja entre andares.

Medir assim subestima o poder do jogador por larga margem, e todo o
balanceamento calibrado em cima disso mede um jogo que ninguém joga. Este módulo
reproduz o que o `engine/loop.py` faz entre combates, com as mesmas funções de
conteúdo, para que a simulação e o jogo cheguem ao andar 20 com o mesmo herói.
"""

from __future__ import annotations

import random

from src.content.economy import buy_recovery
from src.content.factories.loot import get_loot
from src.content.passives import generate_passive_choices
from src.content.shop import Shop
from src.content.skills_loader import generate_skill_choices
from src.mechanics.math_operations import generate_essence_multiplier
from src.shared.constants import SKILL_OFFER_LEVEL_INTERVAL, SKILL_OFFER_SIZE
from src.sim.pick_policies import DEFAULT_PICK_POLICY, PickPolicy, get_pick_policy
from src.sim.toggles import Toggles

# A cadência da oferta é a do jogo: `SKILL_OFFER_LEVEL_INTERVAL`, importado, e
# não um "níveis ímpares a partir de 5" reescrito aqui. As duas camadas
# divergiam — o jogo oferecia em 5, 7, 9 e o simulador media outra progressão de
# deck que a do jogador.
# Quantos consumíveis de cura o bot tenta manter em mãos ao sair da loja.
TARGET_HEALING_POTIONS = 3
# Fração do ouro que o bot aceita gastar em equipamento; o resto fica para poção.
GEAR_BUDGET_RATIO = 0.6
# Até onde o bot repara a vida na loja, e quanto do ouro aceita queimar nisso.
# Não é cura completa: pagar para encher a barra toda todo andar consumiria o
# ouro que compra poder, e a decisão "reparar ou equipar" é justamente a que a
# economia precisa produzir. 70% é o suficiente para o andar seguinte ser
# jogável; o resto o descanso gratuito devolve.
RECOVERY_TARGET_HP_PERCENT = 70
RECOVERY_BUDGET_RATIO = 0.5


def pick_passive(hero, choices: list, rng: random.Random, picker: PickPolicy | None = None):
    """Escolhe uma passiva entre as oferecidas, pela política indicada.

    A ordem de preferência vive em `sim/pick_policies.py`, e não aqui, porque o
    scout precisa comparar políticas diferentes: ranking de carta tirado de um
    único jeito de jogar é o ranking daquele jeito de jogar, não do conteúdo.
    """
    return (picker or get_pick_policy(DEFAULT_PICK_POLICY)).pick_passive(hero, choices, rng)


def pick_skill(hero, choices: list, rng: random.Random, picker: PickPolicy | None = None):
    """Escolhe uma skill nova entre as oferecidas, e qual substituir."""
    return (picker or get_pick_policy(DEFAULT_PICK_POLICY)).pick_skill(hero, choices, rng)


def on_level_up(
    hero,
    levels_gained: int,
    rng: random.Random,
    toggles: Toggles | None = None,
    telemetry=None,
    picker: PickPolicy | None = None,
) -> None:
    """Aplica as escolhas que o jogo oferece a cada nível ganho.

    Espelha `engine/loop.py`: uma passiva por nível, e uma oferta de skill a
    cada `SKILL_OFFER_LEVEL_INTERVAL` níveis.
    """
    cfg = toggles or Toggles()

    if cfg.passives:
        for _ in range(levels_gained):
            ofertas = [
                c for c in generate_passive_choices(count=3) if c.id not in cfg.banned_passives
            ]
            escolhida = pick_passive(hero, ofertas, rng, picker)
            if telemetry is not None:
                telemetry.record_offer("passive", ofertas, escolhida)
            if escolhida is not None:
                hero.add_passive(escolhida)

    if not cfg.skill_choice:
        return

    nivel = hero.get_level()
    for lvl in range(nivel - levels_gained + 1, nivel + 1):
        if lvl > 1 and lvl % SKILL_OFFER_LEVEL_INTERVAL == 0:
            ofertas = generate_skill_choices(
                hero.get_classname(),
                lvl,
                hero.active_skill_ids(),
                count=SKILL_OFFER_SIZE,
                seen_ids=hero.seen_skill_ids,
            )
            ofertas = [o for o in ofertas if o.id not in cfg.banned_skills]
            hero.seen_skill_ids.update(o.id for o in ofertas)
            nova, slot = pick_skill(hero, ofertas, rng, picker)
            if telemetry is not None:
                telemetry.record_offer("skill", ofertas, nova)
            if nova is not None and slot is not None:
                hero.skills[slot] = nova


def collect_loot(hero, rng: random.Random, toggles: Toggles | None = None, telemetry=None) -> None:
    """Recolhe o drop do combate e equipa se for melhor que o item atual.

    O jogo dropa item a cada vitória. Ignorar isso na simulação corta a principal
    fonte de equipamento da run.
    """
    if toggles is not None and not toggles.loot:
        return
    item = get_loot()
    if item is None:
        return
    hero.add_item_to_inventory(item)
    if telemetry is not None:
        telemetry.items_from_loot += 1
    if equip_if_better(hero, item) and telemetry is not None:
        telemetry.items_equipped_from_loot += 1
        telemetry.equipped_by_slot[str(item.slot)] += 1


def equip_if_better(hero, item) -> bool:
    """Equipa o item se ele render mais que o ocupante do slot."""
    posicoes = _posicoes_do_bot(hero, item)
    if not posicoes:
        return False
    classes = getattr(item, "classes", None)
    if classes and hero.get_classname() not in classes:
        return False

    atual = _pior_ocupante(hero, posicoes)
    if atual is not None and _peso_do_item(atual) >= _peso_do_item(item):
        return False
    return bool(hero.equip(item))


def _posicoes_do_bot(hero, item) -> tuple[str, ...]:
    """As posições que o BOT considera — todas as que o personagem tem.

    Duas mãos e dois anéis são anatomia, não capacidade opcional: o bot que
    ignorasse a segunda posição mediria um personagem que não existe. A peça
    de duas mãos já sai daqui filtrada, porque `available_positions_for` sabe
    que ela toma o par.
    """
    return hero.available_positions_for(item)


def _pior_ocupante(hero, posicoes):
    """A peça mais fraca entre as posições da categoria, ou `None` se há vaga.

    Com duas posições para a mesma categoria, a comparação certa é contra a que
    sairia — a pior — e não contra uma chave fixa. Havendo posição livre, não há
    nada para comparar: o item entra.
    """
    ocupantes = [hero.equipment.get(p) for p in posicoes]
    if any(o is None for o in ocupantes):
        return None
    return min(ocupantes, key=_peso_do_item)


def _peso_do_item(item) -> float:
    """Quanto um item vale, somando dano, defesa e efeito passivo."""
    return (
        float(getattr(item, "damage_bonus", 0))
        + float(getattr(item, "defense_bonus", 0))
        + float(getattr(item, "effect_value", 0)) / 4
    )


def visit_shop(
    hero,
    shop: Shop,
    dungeon_level: int,
    rng: random.Random,
    toggles: Toggles | None = None,
    telemetry=None,
) -> None:
    """Gasta o ouro do andar como um jogador gastaria.

    Na ordem em que um jogador resolve as coisas: primeiro descarta o que a
    mochila acumulou, porque isso é ouro parado e não disputa orçamento com
    nada; depois repara a vida, porque chegar ao andar seguinte ferido é a forma
    mais comum de perder a run; depois repõe cura, porque sem consumível o
    próximo andar vira aposta; e só então melhora equipamento, dentro de uma
    fração do ouro restante — guardar tudo para uma compra futura é uma decisão
    que nenhum jogador de permadeath toma.
    """
    if toggles is not None and not toggles.shop:
        return

    _vender_dominados(hero, shop, dungeon_level)
    _repair(hero, dungeon_level, telemetry)

    ofertas = shop.get_available_items(dungeon_level, hero.get_classname())
    if not ofertas:
        return

    curas = [
        o
        for o in ofertas
        if getattr(o["item"], "consumable", False) and o["item"].effect_type == "max_hp"
    ]
    curas.sort(key=lambda o: -o["item"].effect_value)
    em_maos = sum(
        1
        for i in hero.inventory
        if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
    )
    for oferta in curas:
        while em_maos < TARGET_HEALING_POTIONS and hero.coins >= oferta["price"]:
            if not shop.buy_item(hero, oferta["item"], dungeon_level):
                break
            em_maos += 1
            if telemetry is not None:
                telemetry.items_bought += 1
                telemetry.gold_spent_on_consumables += int(oferta["price"])

    orcamento = int(hero.coins * GEAR_BUDGET_RATIO)
    equipamentos = [
        o
        for o in ofertas
        if hero.positions_for(getattr(o["item"], "slot", None))
        and not getattr(o["item"], "consumable", False)
    ]
    equipamentos.sort(key=lambda o: -_peso_do_item(o["item"]))
    for oferta in equipamentos:
        item = oferta["item"]
        if oferta["price"] > orcamento or oferta["price"] > hero.coins:
            continue
        atual = _pior_ocupante(hero, _posicoes_do_bot(hero, item))
        if atual is not None and _peso_do_item(atual) >= _peso_do_item(item):
            continue
        if shop.buy_item(hero, item, dungeon_level):
            orcamento -= oferta["price"]
            if telemetry is not None:
                telemetry.items_bought += 1
                telemetry.gold_spent_on_gear += int(oferta["price"])
            if equip_if_better(hero, item) and telemetry is not None:
                telemetry.items_equipped_from_shop += 1
                telemetry.equipped_by_slot[str(item.slot)] += 1


def _vender_dominados(hero, shop: Shop, dungeon_level: int) -> None:
    """Converte em ouro o que a mochila acumulou e não serve mais para nada.

    O bot nunca vendia nada, e sem venda a faixa de 20–25% da Economia V1 era um
    número que ninguém tinha medido. A política é a mais simples que ainda é
    defensável — item claramente dominado, e nada além disso. Não é IA de
    inventário: não tenta prever build futura, não especula com preço, não
    guarda peça para um slot que talvez melhore.

    A ordem importa e é a parte fácil de errar: **veste antes de descartar**.
    Um item cujo slot está vazio não tem com o que ser comparado, e a regra de
    "pior que o equipado" o trataria como lixo justamente quando ele é a única
    coisa que o herói tem para aquele slot. `equip_if_better` já resolve o slot
    vazio (equipa) e o upgrade (troca); o que sobra depois dele é, por
    construção, o que o herói olhou e recusou.
    """
    for item in list(hero.inventory):
        if getattr(item, "consumable", False):
            continue
        equip_if_better(hero, item)

    for item in list(hero.inventory):
        if _descartavel(hero, item):
            # `shop.sell_item` é a função do jogo real, e já escreve o
            # livro-caixa do herói (`gold_from_sale`, `items_sold`). Nenhum
            # contador aqui: um segundo contador para o mesmo evento é como os
            # dois `gold_earned` com significados diferentes nasceram.
            shop.sell_item(hero, item, dungeon_level)


def _descartavel(hero, item) -> bool:
    """O item está na mochila e não há motivo visível para mantê-lo lá."""
    if getattr(item, "consumable", False):
        return False
    posicoes = _posicoes_do_bot(hero, item)
    if not posicoes:
        return False

    # Classe errada: o herói não pode equipá-lo em nenhuma circunstância.
    classes = getattr(item, "classes", None)
    if classes and hero.get_classname() not in classes:
        return True

    atual = _pior_ocupante(hero, posicoes)
    if atual is None:
        # Posição vazia e item utilizável: `equip_if_better` acabou de rodar,
        # então chegar aqui significa que ele recusou — não vender por precaução.
        return False
    return _peso_do_item(item) <= _peso_do_item(atual)


def _repair(hero, dungeon_level: int, telemetry=None) -> None:
    """Compra recuperação até a vida ficar jogável, dentro de um orçamento.

    Vem antes da loja de itens porque é a decisão que o jogador toma primeiro:
    chegar ao andar seguinte com 20% de vida é a forma mais comum de perder a
    run, e nenhum equipamento comprado agora compensa isso.
    """
    orcamento = int(hero.coins * RECOVERY_BUDGET_RATIO)
    while orcamento > 0 and hero.get_hp() * 100 / max(1, hero.base_hp) < RECOVERY_TARGET_HP_PERCENT:
        paga = buy_recovery(hero, dungeon_level, "hp")
        if paga is None or paga["price"] > orcamento:
            break
        orcamento -= int(paga["price"])
        if telemetry is not None:
            telemetry.gold_spent_on_recovery += int(paga["price"])
            telemetry.recovery_purchases += 1


def floor_essence_multiplier(dungeon_level: int) -> float:
    """Multiplicador de Essência do andar, como o jogo sorteia."""
    return generate_essence_multiplier(dungeon_level)
