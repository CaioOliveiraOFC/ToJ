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

from src.content.factories.loot import get_loot
from src.content.passives import generate_passive_choices
from src.content.shop import Shop
from src.content.skills_loader import generate_skill_choices
from src.mechanics.math_operations import generate_essence_multiplier

# O jogo oferece escolha de skill nos níveis ímpares a partir deste.
SKILL_CHOICE_MIN_LEVEL = 5
# Quantos consumíveis de cura o bot tenta manter em mãos ao sair da loja.
TARGET_HEALING_POTIONS = 3
# Fração do ouro que o bot aceita gastar em equipamento; o resto fica para poção.
GEAR_BUDGET_RATIO = 0.6
# Ordem de preferência de passivas para um jogador competente: primeiro o que
# mantém a run viva, depois o que a encurta, por último o que a enriquece.
PASSIVE_PRIORITY = (
    "max_hp", "defense", "damage_reduction", "death_ignore",
    "strength", "crit_chance", "agility",
    "potion_heal_bonus", "max_mp", "dodge_chance", "stun_chance",
    "essence_bonus", "gold_drop_bonus",
)


def pick_passive(hero, choices: list, rng: random.Random):
    """Escolhe uma passiva entre as três oferecidas.

    A heurística é a de um jogador competente: prioriza o que resolve o problema
    mais próximo — sobrevivência quando a classe é frágil, dano quando ela já
    aguenta. Um bot que sorteia ao acaso mede a média das builds, não a build que
    alguém montaria.
    """
    if not choices:
        return None

    # Sobrevivência primeiro. Numa masmorra de permadeath decidida por atrito, o
    # que encerra a run é acabar a vida, não demorar a matar — e uma heurística
    # que dependesse dos atributos da classe acabaria dando builds diferentes por
    # acidente de arredondamento, em vez de por decisão.
    for efeito in PASSIVE_PRIORITY:
        for carta in choices:
            if carta.effect_type == efeito:
                return carta
    return max(choices, key=lambda c: float(c.effect_value) if str(c.effect_value).replace(".", "").isdigit() else 0)


def pick_skill(hero, choices: list, rng: random.Random):
    """Escolhe uma skill nova entre as oferecidas, e qual substituir.

    Prefere dano, depois controle, depois cura — a ordem que a política de
    combate sabe usar. Substitui a skill de menor valor entre as que o herói já
    tem, para o slot novo não desperdiçar a escolha.
    """
    if not choices:
        return None, None

    ordem = {"damage": 0, "status": 1, "heal": 2, "damage_reduction": 3, "buff": 4}
    nova = min(choices, key=lambda s: (ordem.get(s.effect_type, 9), -_valor(s)))

    if len(hero.skills) < 4:
        return nova, max(hero.skills, default=0) + 1

    pior = min(hero.skills, key=lambda k: _valor(hero.skills[k]))
    if _valor(nova) <= _valor(hero.skills[pior]):
        return None, None
    return nova, pior


def _valor(skill) -> float:
    """Valor bruto de uma skill, para comparar candidatas."""
    try:
        return float(skill.effect_value)
    except (TypeError, ValueError):
        return 25.0  # skills de status não têm valor numérico; valem como controle


def on_level_up(hero, levels_gained: int, rng: random.Random) -> None:
    """Aplica as escolhas que o jogo oferece a cada nível ganho.

    Espelha `engine/loop.py`: uma passiva por nível, e uma skill nos níveis
    ímpares a partir de `SKILL_CHOICE_MIN_LEVEL`.
    """
    for _ in range(levels_gained):
        escolhida = pick_passive(hero, generate_passive_choices(count=3), rng)
        if escolhida is not None:
            hero.add_passive(escolhida)

    nivel = hero.get_level()
    for lvl in range(nivel - levels_gained + 1, nivel + 1):
        if lvl >= SKILL_CHOICE_MIN_LEVEL and lvl % 2 == 1:
            conhecidas = [s.id for s in hero.skills.values()]
            ofertas = generate_skill_choices(hero.get_classname(), lvl, conhecidas, count=3)
            nova, slot = pick_skill(hero, ofertas, rng)
            if nova is not None and slot is not None:
                hero.skills[slot] = nova


def collect_loot(hero, rng: random.Random) -> None:
    """Recolhe o drop do combate e equipa se for melhor que o item atual.

    O jogo dropa item a cada vitória. Ignorar isso na simulação corta a principal
    fonte de equipamento da run.
    """
    item = get_loot()
    if item is None:
        return
    hero.add_item_to_inventory(item)
    equip_if_better(hero, item)


def equip_if_better(hero, item) -> bool:
    """Equipa o item se ele render mais que o ocupante do slot."""
    slot = getattr(item, "slot", None)
    if not slot or slot not in hero.equipment:
        return False
    classes = getattr(item, "classes", None)
    if classes and hero.get_classname() not in classes:
        return False

    atual = hero.equipment[slot]
    if atual is not None and _peso_do_item(atual) >= _peso_do_item(item):
        return False
    return bool(hero.equip(item))


def _peso_do_item(item) -> float:
    """Quanto um item vale, somando dano, defesa e efeito passivo."""
    return (
        float(getattr(item, "damage_bonus", 0))
        + float(getattr(item, "defense_bonus", 0))
        + float(getattr(item, "effect_value", 0)) / 4
    )


def visit_shop(hero, shop: Shop, dungeon_level: int, rng: random.Random) -> None:
    """Gasta o ouro do andar como um jogador gastaria.

    Primeiro repõe cura, porque sem consumível o próximo andar vira aposta.
    Depois melhora equipamento, dentro de uma fração do ouro restante — guardar
    tudo para uma compra futura é uma decisão que nenhum jogador de permadeath
    toma.
    """
    ofertas = shop.get_available_items(dungeon_level, hero.get_classname())
    if not ofertas:
        return

    curas = [
        o for o in ofertas
        if getattr(o["item"], "consumable", False) and o["item"].effect_type == "max_hp"
    ]
    curas.sort(key=lambda o: -o["item"].effect_value)
    em_maos = sum(
        1 for i in hero.inventory
        if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
    )
    for oferta in curas:
        while em_maos < TARGET_HEALING_POTIONS and hero.coins >= oferta["price"]:
            if not shop.buy_item(hero, oferta["item"], dungeon_level):
                break
            em_maos += 1

    orcamento = int(hero.coins * GEAR_BUDGET_RATIO)
    equipamentos = [
        o for o in ofertas
        if getattr(o["item"], "slot", None) in hero.equipment
        and not getattr(o["item"], "consumable", False)
    ]
    equipamentos.sort(key=lambda o: -_peso_do_item(o["item"]))
    for oferta in equipamentos:
        item = oferta["item"]
        if oferta["price"] > orcamento or oferta["price"] > hero.coins:
            continue
        atual = hero.equipment.get(item.slot)
        if atual is not None and _peso_do_item(atual) >= _peso_do_item(item):
            continue
        if shop.buy_item(hero, item, dungeon_level):
            orcamento -= oferta["price"]
            equip_if_better(hero, item)


def floor_essence_multiplier(dungeon_level: int) -> float:
    """Multiplicador de Essência do andar, como o jogo sorteia."""
    return generate_essence_multiplier(dungeon_level)
