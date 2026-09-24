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

from src.content import forge, level_up
from src.content.economy import (
    buy_recovery,
    enchant_cost,
    enhancement_cost,
    reroll_cost,
    socket_cost,
)
from src.content.enchantments import MAX_ENCHANTMENTS
from src.content.factories.loot import get_loot
from src.content.forge import award_gem
from src.content.shop import Shop
from src.mechanics.math_operations import generate_essence_multiplier
from src.shared.constants import CLASS_WEIGHTS
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


# Quantos rerolls o BOT gasta numa oferta de nível. Um só, e de novo: é política
# de simulação. O jogador não tem teto — o custo dobrando é que o segura.
BOT_MAX_OFFER_REROLLS = 1


def _pagar_reroll(hero, dungeon_level: int, feitos: int, fonte: str, telemetry=None) -> bool:
    """Cobra um reroll de oferta pela MESMA função que o jogo cobra."""
    custo = reroll_cost(dungeon_level, feitos)
    if not hero.spend_coins(custo, source=fonte):
        return False
    if telemetry is not None:
        campo = f"gold_spent_on_{fonte}"
        setattr(telemetry, campo, getattr(telemetry, campo) + custo)
        telemetry.rerolls += 1
    return True


def on_level_up(
    hero,
    levels_gained: int,
    rng: random.Random,
    toggles: Toggles | None = None,
    telemetry=None,
    picker: PickPolicy | None = None,
    dungeon_level: int = 1,
) -> None:
    """Aplica as escolhas que o jogo oferece a cada nível ganho.

    A GERAÇÃO das ofertas e a CADÊNCIA saem de `content/level_up.py`, a mesma
    fonte que a tela do jogador usa — antes estavam escritas aqui e lá, e duas
    cópias divergem na primeira mudança. O que mora aqui é só a decisão: qual
    carta levar, e quando pagar reroll.

    RESSALVA REGISTRADA: esta função ainda percorre TODAS as passivas e depois
    todas as skills, enquanto o jogo pergunta passiva-e-skill por nível. As duas
    ordens consomem o mesmo gerador, então mudam o sorteio. Unificar move as
    bandas de balanceamento, e por isso fica para a rodada que puder medi-las.
    O BOT_PADRÃO não passa por aqui: ele usa `engine.encounter.resolve_encounter`.
    """
    cfg = toggles or Toggles()
    politica = picker if picker is not None else get_pick_policy(DEFAULT_PICK_POLICY)

    if cfg.passives:
        for _ in range(levels_gained):
            ofertas = [c for c in level_up.ofertas_de_passiva() if c.id not in cfg.banned_passives]
            for feitos in range(BOT_MAX_OFFER_REROLLS):
                if not politica.passive_off_intent(ofertas):
                    break
                if not _pagar_reroll(hero, dungeon_level, feitos, "passive_reroll", telemetry):
                    break
                ofertas = [
                    c for c in level_up.ofertas_de_passiva() if c.id not in cfg.banned_passives
                ]
            escolhida = pick_passive(hero, ofertas, rng, picker)
            if telemetry is not None:
                telemetry.record_offer("passive", ofertas, escolhida)
            if escolhida is not None:
                level_up.aplicar_passiva(hero, escolhida)

    if not cfg.skill_choice:
        return

    def _oferta_de_skill(lvl):
        # `ofertas_de_skill` já marca as cartas como VISTAS — inclusive as que um
        # reroll descarta, que é a regra do jogo.
        return [o for o in level_up.ofertas_de_skill(hero, lvl) if o.id not in cfg.banned_skills]

    nivel = hero.get_level()
    for lvl in level_up.niveis_ganhos(nivel, levels_gained):
        if level_up.oferece_skill(lvl):
            ofertas = _oferta_de_skill(lvl)
            nova, slot = pick_skill(hero, ofertas, rng, picker)
            for feitos in range(BOT_MAX_OFFER_REROLLS):
                # `(None, None)` é o veredito da política: nenhuma das três supera
                # o que o herói já tem. É exatamente a hora de comprar outra amostra.
                if nova is not None:
                    break
                if not _pagar_reroll(hero, dungeon_level, feitos, "skill_reroll", telemetry):
                    break
                ofertas = _oferta_de_skill(lvl)
                nova, slot = pick_skill(hero, ofertas, rng, picker)
            if telemetry is not None:
                telemetry.record_offer("skill", ofertas, nova)
            if nova is not None and slot is not None:
                # Aplicar pela MESMA função da tela: o bot escrevia direto em
                # `hero.skills[slot]` e pulava `learn_skill`.
                level_up.aplicar_skill(hero, nova, slot)


def collect_loot(
    hero,
    rng: random.Random,
    toggles: Toggles | None = None,
    telemetry=None,
    dungeon_level: int = 1,
) -> None:
    """Recolhe o drop do combate e equipa se for melhor que o item atual.

    O jogo dropa item a cada vitória. Ignorar isso na simulação corta a principal
    fonte de equipamento da run.
    """
    if toggles is not None and not toggles.loot:
        return

    # Gema: a MESMA rolagem do jogo, pela mesma função. Nada de "uma gema
    # esperada por andar" — o que se quer medir é a chance que o jogador vive.
    if award_gem(hero, dungeon_level, rng) is not None and telemetry is not None:
        telemetry.gems_found += 1

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

    visita = shop.visit(dungeon_level, hero.get_classname())
    _rerollar_estoque(hero, visita, telemetry)
    ofertas = visita.stock
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


# Quantos rerolls de loja o BOT aceita por visita. É política de simulação, e
# não regra do jogo: o jogador não tem teto nenhum. O bot é conservador porque a
# pergunta desta fase é "o sistema é usável e aparece na telemetria?", e não
# "qual é a linha ótima de cassino" — um bot que rerrolasse até secar mediria a
# própria ganância, não a economia.
BOT_MAX_SHOP_REROLLS = 2
# Fatia do ouro que o bot aceita gastar rerrolando. O reroll nunca pode comer o
# dinheiro que compraria a peça que ele está justamente procurando.
BOT_REROLL_BUDGET_RATIO = 0.25


def _tem_o_que_comprar(hero, ofertas) -> bool:
    """A vitrine tem upgrade de equipamento ou poção que o bot ainda precisa?"""
    faltam_pocoes = (
        sum(
            1
            for i in hero.inventory
            if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
        )
        < TARGET_HEALING_POTIONS
    )
    for oferta in ofertas:
        item = oferta["item"]
        if getattr(item, "consumable", False):
            if faltam_pocoes and getattr(item, "effect_type", None) == "max_hp":
                return True
            continue
        posicoes = _posicoes_do_bot(hero, item)
        if not posicoes:
            continue
        atual = _pior_ocupante(hero, posicoes)
        if atual is None or _peso_do_item(item) > _peso_do_item(atual):
            return True
    return False


def _rerollar_estoque(hero, visita, telemetry=None) -> None:
    """Troca a vitrine enquanto ela não tiver nada que sirva.

    A regra do bot, e só dele: rerrola quando a loja não oferece upgrade nem a
    poção que falta, e para assim que o custo passar da fatia do ouro que ele
    reservou para isso. O jogo real não tem nenhum dos dois limites — quem segura
    o jogador é o preço dobrando, não um contador.
    """
    orcamento = int(hero.coins * BOT_REROLL_BUDGET_RATIO)
    for _ in range(BOT_MAX_SHOP_REROLLS):
        if _tem_o_que_comprar(hero, visita.stock):
            return
        custo = visita.next_reroll_cost
        if custo > orcamento or not visita.reroll(hero):
            return
        orcamento -= custo
        if telemetry is not None:
            telemetry.gold_spent_on_shop_reroll += custo
            telemetry.rerolls += 1


# --- Ferreiro ---------------------------------------------------------------
#
# Limites DO BOT, e não do jogo. O Ferreiro real não tem teto nenhum: o jogador
# pode aprimorar a mesma peça a noite inteira se tiver ouro. O bot é contido
# porque a pergunta desta fase é "o ciclo está vivo e aparece na telemetria?", e
# um bot que torrasse tudo em +N mediria a própria ganância.
BOT_MAX_ENHANCEMENTS_PER_VISIT = 1
BOT_MAX_ENCHANTS_PER_VISIT = 1
BOT_FORGE_BUDGET_RATIO = 0.30


def _ganho_por_ouro(item, dungeon_level: int) -> float:
    """Quanto poder um ouro compra ao aprimorar ESTA peça.

    O `+N` multiplica a base da peça, então o ganho marginal é proporcional ao
    que ela já rende; o custo cresce com o rank. Dividir um pelo outro é o que
    faz o bot preferir a peça onde o ouro rende mais, em vez de sempre a mais
    cara ou sempre a primeira da lista.
    """
    custo = enhancement_cost(item, dungeon_level)
    if custo <= 0:
        return 0.0
    return _peso_do_item(item) / custo


def _gema_preferida(hero, gemas: list):
    """A pedra que mais serve a esta classe, pelos pesos que a classe já tem.

    Sem tabela nova: `CLASS_WEIGHTS` já diz de quais atributos o dano da classe
    nasce, e é isso que torna um Rubi bom para o Guerreiro e uma Safira boa para
    o Mago. O jogo real aceita qualquer gema em qualquer socket — a preferência
    é só do bot.
    """
    pesos = dict(CLASS_WEIGHTS.get(hero.get_classname(), {}))
    return max(gemas, key=lambda g: pesos.get(g.stat, 0.0) * g.percent)


def visit_forge(hero, dungeon_level: int, toggles: Toggles | None = None, telemetry=None) -> None:
    """O Ferreiro do bot: engasta o que achou, aprimora e encanta uma peça.

    DEPOIS da loja, de propósito: comprar a peça melhor vem antes de investir na
    que já se tem, e as duas saem da mesma carteira. O orçamento é uma fração do
    ouro que sobrou, então o Ferreiro nunca come o dinheiro da poção.
    """
    if toggles is not None and not getattr(toggles, "forge", True):
        return

    orcamento = int(hero.coins * BOT_FORGE_BUDGET_RATIO)

    # 1. Engastar: socket vazio é poder parado, e a gema já foi paga com sorte.
    for item in forge.socketable(hero):
        for slot, ocupante in enumerate(item.gems):
            if ocupante is not None or not hero.gems:
                continue
            custo = socket_cost(dungeon_level)
            if custo > orcamento:
                break
            gema = _gema_preferida(hero, hero.gems)
            if forge.socket(hero, item, gema, slot, dungeon_level):
                orcamento -= custo
                if telemetry is not None:
                    telemetry.gold_spent_on_socket += custo
                    telemetry.gems_socketed += 1

    # 2. Aprimorar a peça onde o ouro rende mais.
    for _ in range(BOT_MAX_ENHANCEMENTS_PER_VISIT):
        pecas = forge.enhanceable(hero)
        if not pecas:
            break
        melhor = max(pecas, key=lambda i: _ganho_por_ouro(i, dungeon_level))
        custo = enhancement_cost(melhor, dungeon_level)
        if custo > orcamento or forge.enhance(hero, melhor, dungeon_level) is None:
            break
        orcamento -= custo
        if telemetry is not None:
            telemetry.gold_spent_on_enhancement += custo
            telemetry.items_enhanced += 1

    # 3. Encantar uma peça que ainda tem camada livre. O bot não reencanta nesta
    #    V1: trocar é aposta, e apostar sem dado medido não ensina nada.
    for _ in range(BOT_MAX_ENCHANTS_PER_VISIT):
        candidatas = [i for i in forge.enhanceable(hero) if len(i.enchantments) < MAX_ENCHANTMENTS]
        if not candidatas:
            break
        alvo = min(candidatas, key=lambda i: len(i.enchantments))
        custo = enchant_cost(dungeon_level, len(alvo.enchantments))
        if custo > orcamento or forge.enchant(hero, alvo, dungeon_level) is None:
            break
        orcamento -= custo
        if telemetry is not None:
            telemetry.gold_spent_on_enchant += custo
            telemetry.enchantments_added += 1


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
