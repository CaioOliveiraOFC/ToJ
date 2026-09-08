"""Arquétipos de monstro — carregados de `data/monsters.json`.

Antes disto o jogo tinha 121 nomes de monstro e uma única criatura: as quatro
categorias do JSON mudavam apenas a lista de onde o nome era sorteado, e
`create_monster` aplicava as mesmas fórmulas a todas. Sem papéis diferentes não
existe counterplay, porque não existe nada a counterar.

Cada arquétipo distribui o mesmo orçamento de nível de um jeito diferente, e a
regra que fecha o sistema é: **todo arquétipo precisa de pelo menos uma classe
que sofre contra ele**. O skirmisher existe para que esquiva não seja resposta
universal; o controlador existe para que depender de MP tenha custo; o tank
existe para que dano explosivo não resolva tudo.

Este módulo só contém as fórmulas. Os valores — multiplicadores, skills, nomes,
ameaça e counterplay de cada papel — vivem em `src/data/monsters.json`, como
manda a regra 5 da arquitetura: dados em JSON, sem hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.content.skills_loader import SkillCard
from src.data.loader import load_monsters_data
from src.entities.monsters import Monster
from src.shared.constants import (
    MONSTER_ATTACK_TO_STAT_RATIO,
    MONSTER_BUDGET_AGILITY,
    MONSTER_BUDGET_ATTACK,
    MONSTER_BUDGET_DEFENSE,
    MONSTER_BUDGET_HP,
    MONSTER_BUDGET_MP,
)
from src.shared.formulas import geometric

# Papéis que ganham a marcação de chefe: entram sozinhos no encontro e pagam
# recompensa de chefe.
MILESTONE_ROLES = ("elite", "boss")


@dataclass(frozen=True, slots=True)
class Archetype:
    """Perfil de um papel de monstro.

    Os multiplicadores incidem sobre o orçamento do nível. Um arquétipo que ganha
    em um eixo deve perder em outro — é isso que dá a ele uma fraqueza explorável.
    """

    role: str
    label: str
    hp: float
    attack: float
    defense: float
    agility: float
    skill_use_chance: int
    skills: tuple[SkillCard, ...]
    threat: str
    counterplay: str
    names: tuple[str, ...]


def _skill_from_json(data: dict) -> SkillCard:
    """Monta uma skill de monstro reaproveitando o mesmo `SkillCard` do herói.

    Reusar a carta do herói significa que `combat.apply_skill` trata os dois lados
    com o mesmo código — o monstro não ganha uma segunda implementação de dano
    que possa divergir da do jogador.
    """
    return SkillCard(
        id=data["id"],
        name=data["name"],
        skill_class="Monster",
        level_required=1,
        mana_cost=int(data.get("mana_cost", 0)),
        effect_type=data["effect_type"],
        effect_value=data["effect_value"],
        effect_stat=data.get("effect_stat", ""),
        description=data.get("description", ""),
        target=data.get("target", "enemy"),
        duration=int(data.get("duration", 0)),
        chance=int(data.get("chance", 100)),
        rarity=data.get("rarity", "Common"),
        is_initial=False,
        cooldown=int(data.get("cooldown", 0)),
    )


def _archetype_from_json(role: str, data: dict) -> Archetype:
    budget = data.get("budget", {})
    return Archetype(
        role=role,
        label=data.get("label", role),
        hp=float(budget.get("hp", 1.0)),
        attack=float(budget.get("attack", 1.0)),
        defense=float(budget.get("defense", 1.0)),
        agility=float(budget.get("agility", 1.0)),
        skill_use_chance=int(data.get("skill_use_chance", 0)),
        skills=tuple(_skill_from_json(s) for s in data.get("skills", [])),
        threat=data.get("threat", ""),
        counterplay=data.get("counterplay", ""),
        names=tuple(data.get("names", ())),
    )


_ARCHETYPE_CACHE: dict[str, Archetype] | None = None
_ROLE_WEIGHT_CACHE: dict[str, int] | None = None


def _load() -> tuple[dict[str, Archetype], dict[str, int]]:
    """Carrega e cacheia os arquétipos e os pesos de sorteio do JSON."""
    global _ARCHETYPE_CACHE, _ROLE_WEIGHT_CACHE
    if _ARCHETYPE_CACHE is None or _ROLE_WEIGHT_CACHE is None:
        data = load_monsters_data()
        _ARCHETYPE_CACHE = {
            role: _archetype_from_json(role, payload)
            for role, payload in data["archetypes"].items()
        }
        _ROLE_WEIGHT_CACHE = dict(data["routine_role_weights"])
    return _ARCHETYPE_CACHE, _ROLE_WEIGHT_CACHE


def reload_archetypes() -> None:
    """Descarta o cache. Útil ao editar o JSON durante o desenvolvimento."""
    global _ARCHETYPE_CACHE, _ROLE_WEIGHT_CACHE
    _ARCHETYPE_CACHE = None
    _ROLE_WEIGHT_CACHE = None


def all_archetypes() -> dict[str, Archetype]:
    """Todos os arquétipos, indexados pelo papel."""
    return _load()[0]


def routine_role_weights() -> dict[str, int]:
    """Peso de aparição de cada papel num andar comum.

    Elite e chefe não estão aqui: eles são colocados pelo gerador do andar, não
    sorteados junto com a população comum.
    """
    return _load()[1]


def get_archetype(role: str) -> Archetype:
    """Resolve o papel. Papel desconhecido é erro, não silêncio."""
    archetypes = all_archetypes()
    if role not in archetypes:
        raise ValueError(f"Arquétipo desconhecido: {role!r}. Use um de {sorted(archetypes)}.")
    return archetypes[role]


def spawn_by_role(role: str, level: int, name: str | None = None) -> Monster:
    """Cria um monstro do papel pedido, com o orçamento do nível.

    O ataque é fixado através de `st` e `mg` porque `Monster` deriva
    `avg_damage = (st + mg) // DAMAGE_FORMULA_DIVISOR` — manter essa derivação
    preserva os valores que a tela de status já mostra.

    Args:
        role: Papel do arquétipo.
        level: Nível do monstro.
        name: Nome de exibição. Sem ele, usa o rótulo do papel.

    Returns:
        Instância de `Monster` já configurada com papel, skills e comportamento.
    """
    archetype = get_archetype(role)

    attack = geometric(MONSTER_BUDGET_ATTACK * archetype.attack, level)
    stat_for_attack = int(attack * MONSTER_ATTACK_TO_STAT_RATIO)

    monster = Monster(
        name or f"{archetype.label} Nv.{level}",
        level,
        hp=geometric(MONSTER_BUDGET_HP * archetype.hp, level),
        mp=geometric(MONSTER_BUDGET_MP, level),
        st=stat_for_attack,
        mg=stat_for_attack,
        df=geometric(MONSTER_BUDGET_DEFENSE * archetype.defense, level),
        ag=geometric(MONSTER_BUDGET_AGILITY * archetype.agility, level),
    )
    monster.role = archetype.role
    monster.skills = list(archetype.skills)
    monster.skill_use_chance = archetype.skill_use_chance
    if archetype.role in MILESTONE_ROLES:
        monster.is_boss = True
    return monster
