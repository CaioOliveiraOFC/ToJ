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


def generation_rules() -> dict[str, Any]:
    """Regras de povoamento de andar, como estão no JSON.

    Público porque a simulação de run precisa montar andares com as mesmas
    regras do jogo. Enquanto ela tinha a própria tabela, o andar 3 simulado
    trazia um elite garantido que o jogo nunca gera antes do andar 4 — e era
    esse elite, não o design, que encerrava metade das runs do Mago ali.
    """
    return dict(_get_monsters_data()["generation"])


def _pick_role(dungeon_level: int, rng=None) -> str:
    """Sorteia um papel para o andar, respeitando a profundidade mínima.

    Papéis de controle e suporte exigem que o jogador reordene alvos, então só
    entram a partir do andar configurado em `generation.advanced_role_min_floor`.
    Antes disso o andar é de aprendizado.
    """
    r = rng if rng is not None else random
    generation = _get_monsters_data()["generation"]
    weights = dict(routine_role_weights())
    if dungeon_level < int(generation["advanced_role_min_floor"]):
        for role in generation["advanced_roles"]:
            weights.pop(role, None)
    roles = list(weights)
    return r.choices(roles, weights=[weights[r_] for r_ in roles], k=1)[0]


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


def routine_monster_count(dungeon_level: int) -> int:
    """Quantos monstros COMUNS o andar coloca. Sem elite e sem chefe.

    A quantidade vem do JSON. A correção relevante: `scaling_per_3_levels` valia
    1, então a conta era `2 + andar`, e o andar 20 spawnava 22 monstros. O nome
    da chave prometia uma divisão por 3 que não acontecia.

    Existe como função separada porque a conta era feita em três lugares: aqui,
    no plano de andar do simulador e no modelo de XP. Três cópias da mesma regra
    é três chances de o simulador medir uma masmorra que o jogo não tem — e foi
    exatamente o que aconteceu: o plano do simulador levava 14 monstros ao andar
    20 contra os 10 do jogo.
    """
    generation = _get_monsters_data()["generation"]
    scaling_step = max(1, int(generation.get("scaling_per_3_levels", 3)))
    return max(
        int(generation.get("min_monsters", 1)),
        int(generation.get("base_count", 3)) + dungeon_level // scaling_step,
    )


def floor_role_plan(dungeon_level: int, rng=None) -> list[str]:
    """Os PAPÉIS que o andar coloca no mapa: os comuns mais o elite eventual.

    A ESTRUTURA do andar — quantos monstros e de quais arquétipos — sem criar
    monstro nenhum. É o que o jogo e o simulador precisam ter em comum: o
    simulador quer saber quantas lutas o andar tem, e não quais exemplares.

    O chefe não entra: quem o coloca é quem monta o andar, a cada
    `BOSS_FLOOR_INTERVAL`, e ele não é população gerada.

    `rng` existe para a comparação entre jogo e simulador ser reprodutível com
    uma semente conhecida. O padrão é o `random` global, que é o que o jogo
    sempre usou — passar nada mantém as mesmas probabilidades e a mesma fonte.
    """
    r = rng if rng is not None else random
    generation = _get_monsters_data()["generation"]

    roles = [_pick_role(dungeon_level, r) for _ in range(routine_monster_count(dungeon_level))]

    # Elite: o marco do andar. Testa se a build funciona, sem ser um chefe.
    if dungeon_level >= int(generation["advanced_role_min_floor"]) and r.random() < float(
        generation["elite_spawn_chance"]
    ):
        roles.append("elite")

    return roles


def generate_monsters_for_level(dungeon_level: int, player_level: int = 1) -> list[Monster]:
    """Gera a população de um andar, a partir do plano de papéis.

    Args:
        dungeon_level: Nível atual da masmorra.
        player_level: Nível atual do jogador.

    Returns:
        Lista de monstros do andar, com papéis variados.
    """
    monsters: list[Monster] = []
    for role in floor_role_plan(dungeon_level):
        level = calculate_scaled_monster_level(dungeon_level, player_level)
        monsters.append(create_monster(_name_for(role, level), level, role))
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
