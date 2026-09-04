"""Geração procedural de monstros a partir dos arquétipos.

Antes, as quatro categorias do JSON (`common`, `uncommon`, `rare`, `boss`)
mudavam apenas a lista de onde o nome era sorteado: `create_monster` aplicava as
mesmas fórmulas a todas, e os campos `weight` e `min_level` das categorias nunca
eram lidos por nenhum código. Na prática o jogo tinha 121 nomes para uma única
criatura, e por isso nenhum encontro exigia uma resposta diferente de outro.

Agora o papel vem primeiro: o gerador sorteia um arquétipo com peso, e o
arquétipo decide atributos, comportamento e ameaça.
"""

from __future__ import annotations

import random
from typing import Any

from src.content.factories.archetypes import (
    all_archetypes,
    get_archetype,
    routine_role_weights,
    spawn_by_role,
)
from src.data.loader import load_monsters_data
from src.entities.monsters import Monster
from src.shared.constants import DEFAULT_MONSTER_ROLE as DEFAULT_ROLE
from src.shared.constants import MINI_BOSS_LEVEL_BONUS


def calculate_scaled_monster_level(dungeon_level: int, player_level: int) -> int:
    """Nível do monstro, com variação controlada em torno do andar.

    Os deslocamentos, os pesos e os limites de segurança contra RNG injusto vêm
    de `generation.level_variation` no JSON.

    Args:
        dungeon_level: Nível atual da masmorra.
        player_level: Nível atual do jogador.

    Returns:
        Nível do monstro calculado com segurança.
    """
    variation = _get_monsters_data()["generation"]["level_variation"]

    monster_level = random.choices(
        [dungeon_level + offset for offset in variation["offsets"]],
        weights=variation["weights"],
        k=1,
    )[0]

    monster_level = min(monster_level, dungeon_level + int(variation["max_above_floor"]))
    if player_level <= int(variation["early_player_level"]):
        monster_level = min(monster_level, player_level + int(variation["early_max_above_player"]))
    if dungeon_level == 1:
        monster_level = min(monster_level, int(variation["first_floor_max_level"]))

    return max(1, monster_level)


def _get_monsters_data() -> dict[str, Any]:
    """Carrega e retorna os dados de monstros do JSON."""
    return load_monsters_data()


def _pick_role(dungeon_level: int) -> str:
    """Sorteia um papel para o andar, respeitando a profundidade mínima.

    Papéis de controle e suporte exigem que o jogador reordene alvos, então só
    entram a partir do andar configurado em `generation.advanced_role_min_floor`.
    Antes disso o andar é de aprendizado.
    """
    generation = _get_monsters_data()["generation"]
    weights = dict(routine_role_weights())
    if dungeon_level < int(generation["advanced_role_min_floor"]):
        for role in generation["advanced_roles"]:
            weights.pop(role, None)
    roles = list(weights)
    return random.choices(roles, weights=[weights[r] for r in roles], k=1)[0]


def _name_for(role: str, level: int) -> str:
    """Nome de exibição do monstro. O nome é sabor; o papel é a regra."""
    archetype = get_archetype(role)
    pool = archetype.names or (archetype.label,)
    return f"{random.choice(pool)} Nv.{level}"


def create_monster(nick_name: str, level: int, role: str = DEFAULT_ROLE) -> Monster:
    """Cria um monstro do papel indicado, com o orçamento do nível.

    Mantém a assinatura histórica (`nick_name`, `level`) porque o carregamento de
    save reconstrói monstros por nome e nível.
    """
    lvl = max(1, int(level))
    if role not in all_archetypes():
        role = DEFAULT_ROLE
    return spawn_by_role(role, lvl, name=nick_name)


def generate_monsters_for_level(dungeon_level: int, player_level: int = 1) -> list[Monster]:
    """Gera a população de um andar.

    A quantidade vem do JSON. A correção relevante: `scaling_per_3_levels` valia
    1, então a conta era `2 + andar`, e o andar 20 spawnava 22 monstros. O nome
    da chave prometia uma divisão por 3 que não acontecia.

    Args:
        dungeon_level: Nível atual da masmorra.
        player_level: Nível atual do jogador.

    Returns:
        Lista de monstros do andar, com papéis variados.
    """
    generation = _get_monsters_data()["generation"]

    scaling_step = max(1, int(generation.get("scaling_per_3_levels", 3)))
    count = max(
        int(generation.get("min_monsters", 1)),
        int(generation.get("base_count", 3)) + dungeon_level // scaling_step,
    )

    monsters: list[Monster] = []
    for _ in range(count):
        level = calculate_scaled_monster_level(dungeon_level, player_level)
        role = _pick_role(dungeon_level)
        monsters.append(create_monster(_name_for(role, level), level, role))

    # Elite: o marco do andar. Testa se a build funciona, sem ser um chefe.
    if (
        dungeon_level >= int(generation["advanced_role_min_floor"])
        and random.random() < float(generation["elite_spawn_chance"])
    ):
        level = calculate_scaled_monster_level(dungeon_level, player_level)
        monsters.append(create_monster(_name_for("elite", level), level, "elite"))

    return monsters


def create_boss_for_level(dungeon_level: int) -> Monster:
    """Cria o chefe do andar, com o bônus de nível de chefe.

    Args:
        dungeon_level: Nível atual da masmorra.

    Returns:
        Instância de Monster configurada como chefe.
    """
    boss_level = dungeon_level + MINI_BOSS_LEVEL_BONUS
    return create_monster(_name_for("boss", boss_level), boss_level, "boss")
