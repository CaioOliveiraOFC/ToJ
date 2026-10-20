"""Starter Kit: a única peça que uma nova jornada recebe.

Toda jornada nova começa com exatamente UM item Lv1, sorteado de uma pool
própria (`data/starter_kit.json`), separada do loot. A pool é a mesma para as
três classes, e o sorteio tem duas etapas, uniformes nas duas:

1. a CATEGORIA equipável — Weapon, Ring, Helmet… —, nunca a posição física.
   `Weapon1`/`Weapon2` e `Ring1`/`Ring2` são duas mãos e dois dedos para a mesma
   categoria; sortear posição daria peso dobrado a arma e anel;
2. o item dentro da categoria.

A peça nasce por `Item.instance()`, e não por `spawn()`: o starter é o item, sem
socket sorteado nem bônus escondido. Depois de recebida ela é uma peça comum —
vende, troca, descarta. O que a distingue é `origin = "starter"`, gravado no
EXEMPLAR para telemetria e histórico; a definição do catálogo não muda.

Nada aqui toca drop, loja ou progressão. A peça que só existe como starter
(`starter_only`) fica fora do loot e da loja pelos campos de sempre do catálogo.
"""

from __future__ import annotations

import random
from functools import lru_cache

from src.content.items import Item, get_all_items
from src.data.loader import load_json

STARTER_ORIGIN = "starter"
STARTER_FILE = "starter_kit.json"
# Lv1 no catálogo é "disponível desde o andar 1": só o Common tem
# `shop_min_floor` 1; Rare começa no 5.
STARTER_RARITY = "Common"
STARTER_MAX_MIN_FLOOR = 1


@lru_cache(maxsize=1)
def starter_pool() -> dict[str, tuple[Item, ...]]:
    """A pool por categoria, em ordem estável, validada contra o catálogo.

    RECUSA pool mal declarada em vez de corrigi-la em silêncio: um id que não
    existe, uma peça na categoria errada, consumível, peça acima do Lv1 ou que
    alguma classe não equipa. Os itens devolvidos são as DEFINIÇÕES do catálogo;
    quem entrega um starter tira um exemplar delas.
    """
    dados = load_json(STARTER_FILE)
    por_id = {item.id: item for item in get_all_items().values()}
    pool: dict[str, tuple[Item, ...]] = {}
    for categoria, ids in dados["categories"].items():
        if not ids:
            raise ValueError(f"Starter Kit: a categoria {categoria!r} não tem item.")
        itens = []
        for item_id in ids:
            item = por_id.get(item_id)
            if item is None:
                raise ValueError(f"Starter Kit: {item_id!r} não existe no catálogo.")
            if item.slot != categoria:
                raise ValueError(
                    f"Starter Kit: {item_id!r} é {item.slot!r}, declarado em {categoria!r}."
                )
            if item.consumable:
                raise ValueError(f"Starter Kit: {item_id!r} é consumível.")
            if item.rarity != STARTER_RARITY or item.shop_min_floor > STARTER_MAX_MIN_FLOOR:
                raise ValueError(f"Starter Kit: {item_id!r} não é peça Lv1.")
            if item.classes:
                raise ValueError(
                    f"Starter Kit: {item_id!r} é restrito a {item.classes}; "
                    "a pool é das três classes."
                )
            itens.append(item)
        pool[categoria] = tuple(itens)
    return pool


def starter_categories() -> tuple[str, ...]:
    """As categorias sorteáveis, na ordem do arquivo. A ordem é parte da reprodução."""
    return tuple(starter_pool())


def roll_starter(rng=None) -> Item:
    """Sorteia um starter: categoria primeiro, item depois. Devolve um EXEMPLAR.

    `rng` é o gerador da jornada; sem ele, o `random` global que o jogo já usa.
    Os dois sorteios são `choice` sobre sequências de ordem fixa, então a mesma
    semente dá o mesmo starter.
    """
    r = rng if rng is not None else random
    pool = starter_pool()
    categoria = r.choice(starter_categories())
    modelo = r.choice(pool[categoria])
    exemplar = modelo.instance()
    exemplar.origin = STARTER_ORIGIN
    return exemplar


def grant_starter(player, rng=None) -> Item:
    """Entrega e equipa o starter da jornada. Devolve o exemplar entregue.

    Pelo caminho normal do jogo: o item entra no inventário e é equipado de lá,
    como uma compra seguida de "equipar".
    """
    exemplar = roll_starter(rng)
    player.add_item_to_inventory(exemplar)
    player.equip(exemplar)
    if exemplar not in player.equipment.values():
        raise RuntimeError(f"Starter Kit: {player.get_classname()} não equipou {exemplar.name!r}.")
    return exemplar
