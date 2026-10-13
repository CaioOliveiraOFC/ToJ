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

from src.content.skills_loader import MONSTER_SKILL_CLASS, SkillCard, card_from_json
from src.data.loader import load_monsters_data
from src.entities.monsters import Monster
from src.shared.constants import (
    MAX_ACTIVE_SKILLS,
    MONSTER_BUDGET_AGILITY,
    MONSTER_BUDGET_DEFENSE,
    MONSTER_BUDGET_HP,
    MONSTER_BUDGET_MP,
    MONSTER_BUDGET_OFFENSE,
)
from src.shared.formulas import geometric

# Papéis que ganham a marcação de chefe: entram sozinhos no encontro e pagam
# recompensa de chefe.
MILESTONE_ROLES = ("elite", "boss")

# Eixos de onde o ATAQUE BÁSICO do monstro pode nascer. `df`, `hp` e `mp` são
# legítimos na escala de uma carta, não no básico.
OFFENSIVE_AXES = ("st", "mg", "ag")
_WEIGHT_SUM_TOLERANCE = 1e-9


@dataclass(frozen=True, slots=True)
class Archetype:
    """Perfil de um papel de monstro.

    Os multiplicadores incidem sobre o orçamento do nível. Um arquétipo que ganha
    em um eixo deve perder em outro — é isso que dá a ele uma fraqueza explorável.

    `st` e `mg` são eixos independentes. Antes existia um `attack` só, convertido
    em `st == mg` no spawn: todo monstro era igualmente físico e mágico, e o
    `glass_cannon` carregava 250 de Força que nenhuma carta dele usava só para
    que a conta do ataque básico fechasse.

    `offensive_weights` é o vetor de onde o ATAQUE BÁSICO nasce — o equivalente de
    `CLASS_WEIGHTS` para o monstro, e resolvido pela mesma `weighted_power`. Ele
    tem uma regra dura: **Σpesos = 1**. Com a soma travada, o vetor decide apenas
    a COMPOSIÇÃO do golpe e nunca a magnitude dele, que vem só dos atributos. É o
    que permite a um `skirmisher` trocar Força por Agilidade sem mudar de tamanho.

    A escala das SKILLS continua declarada em cada carta, e ela pode ler `df`,
    `hp` ou `mp` legitimamente. O vetor ofensivo não: o básico nasce de ST/MG/AG.

    `skills` é o KIT COMPLETO, na ordem de aquisição. O que um monstro carrega num
    nível é `deck_for_level` — o validador e a forge continuam lendo o kit todo.
    """

    role: str
    label: str
    hp: float
    st: float
    mg: float
    defense: float
    agility: float
    offensive_weights: tuple[tuple[str, float], ...]
    skill_use_chance: int
    skills: tuple[SkillCard, ...]
    threat: str
    counterplay: str
    names: tuple[str, ...]


# O que o JSON de monstro não precisa repetir em toda carta. São os campos que
# a carta do herói traz do catálogo dele e que, para um monstro, têm sempre o
# mesmo valor: não há assinatura de classe.
#
# `level_required` SAIU daqui. Ele era `1` para as 54 cartas e nada do lado do
# monstro o lia: o monstro nascia com o kit inteiro no nível 1, enquanto o herói
# nasce com uma carta. Agora cada carta declara o nível em que entra no deck, e
# um default aqui esconderia exatamente a carta que esqueceu de declarar —
# `card_from_json` trocaria a ausência por 0 sem avisar.
PADROES_DE_MONSTRO = {
    "skill_class": MONSTER_SKILL_CLASS,
    "is_initial": False,
    "rarity": "Common",
    "target": "enemy",
    "chance": 100,
}


def _skill_from_json(data: dict) -> SkillCard:
    """Monta a carta do monstro com o MESMO construtor da carta do herói.

    Antes esta função montava o `SkillCard` campo a campo, e por isso ela parou
    no tempo: a gramática V2 (`scaling`, `power`, `accuracy_modifier`,
    `secondary`, `requires`) entrou no jogo pelo `card_from_json` e nunca chegou
    aqui. O monstro continuava carregando cartas sem escala — e caía no atalho
    de conteúdo legado do motor, que usa o poder de ataque genérico.

    Um construtor só resolve isso na origem: campo novo na gramática passa a
    valer para os dois lados no mesmo dia, sem ninguém precisar lembrar deste
    arquivo. O que o monstro tem de próprio são os PADRÕES, não a linguagem.
    """
    return card_from_json({**PADROES_DE_MONSTRO, **data})


def _offensive_weights_from_json(role: str, data: dict) -> tuple[tuple[str, float], ...]:
    """Lê o vetor ofensivo do arquétipo e RECUSA um que não some 1.

    A validação é dura porque Σpesos = 1 não é convenção de estilo: é o que
    garante que o vetor escolha composição e não magnitude. Um vetor que soma 1.4
    daria 40% de dano de graça a um arquétipo sem que nenhum atributo dele
    tivesse subido, e o erro apareceria como "o skirmisher está forte" três
    etapas de balanceamento depois.
    """
    bruto = data.get("offensive_weights") or {}
    if not bruto:
        raise ValueError(f"Arquétipo {role!r} não declara `offensive_weights`.")
    desconhecidos = sorted(set(bruto) - set(OFFENSIVE_AXES))
    if desconhecidos:
        raise ValueError(
            f"Arquétipo {role!r} pesa o ataque básico em {desconhecidos}; "
            f"os eixos permitidos são {list(OFFENSIVE_AXES)}."
        )
    pesos = tuple((eixo, float(bruto[eixo])) for eixo in OFFENSIVE_AXES if eixo in bruto)
    soma = sum(peso for _, peso in pesos)
    if abs(soma - 1.0) > _WEIGHT_SUM_TOLERANCE:
        raise ValueError(
            f"Arquétipo {role!r}: os pesos do ataque básico somam {soma:g}, não 1. "
            "O vetor define a composição do golpe; a magnitude vem dos atributos."
        )
    return pesos


def _kit_from_json(role: str, data: dict) -> tuple[SkillCard, ...]:
    """Lê o kit do arquétipo, na ordem de aquisição, e RECUSA um mal declarado.

    A ordem do JSON É a ordem em que o monstro ganha as cartas, e `level_required`
    é o nível em que cada uma entra. Três regras, todas de estrutura:

    - toda carta declara `level_required` inteiro >= 1 — `card_from_json` trocaria
      a ausência por 0, e uma carta de nível 0 entraria no deck de todo mundo;
    - a primeira carta entra no nível 1: é a assinatura do papel, e um monstro de
      nível 1 sem carta nenhuma é outro arquétipo, não este;
    - a sequência não desce: uma carta declarada depois não pode chegar antes.
    """
    brutos = data.get("skills", [])
    anterior = 0
    for posicao, bruto in enumerate(brutos):
        nivel = bruto.get("level_required")
        carta = bruto.get("id", f"#{posicao}")
        if not isinstance(nivel, int) or isinstance(nivel, bool) or nivel < 1:
            raise ValueError(
                f"Arquétipo {role!r}: a carta {carta!r} não declara `level_required` inteiro >= 1."
            )
        if posicao == 0 and nivel != 1:
            raise ValueError(
                f"Arquétipo {role!r}: a primeira carta ({carta!r}) é a assinatura e "
                f"entra no nível 1, não no {nivel}."
            )
        if nivel < anterior:
            raise ValueError(
                f"Arquétipo {role!r}: {carta!r} entra no nível {nivel}, antes da carta "
                f"declarada antes dela (nível {anterior}). A ordem do JSON é a ordem "
                "de aquisição."
            )
        anterior = nivel
    return tuple(_skill_from_json(s) for s in brutos)


def deck_for_level(archetype: Archetype, level: float) -> list[SkillCard]:
    """As cartas que um monstro deste papel carrega neste nível.

    A mesma lei do herói: a carta entra no nível que ela declara, e o deck tem
    teto `MAX_ACTIVE_SKILLS`. A primeira carta é a assinatura do papel e nunca
    sai. Com o deck cheio, ficam a assinatura e as três cartas mais RECENTES já
    liberadas — o análogo determinístico do herói, que mantém a assinatura e
    troca uma carta quando o deck enche. Assim nenhuma carta do kit fica morta:
    todas entram em algum nível.

    `level` pode ser fracionário: a bisseção da arena mede níveis como 16,5.
    """
    liberadas = [c for c in archetype.skills if c.level_required <= level]
    if len(liberadas) <= MAX_ACTIVE_SKILLS:
        return liberadas
    return [liberadas[0], *liberadas[-(MAX_ACTIVE_SKILLS - 1) :]]


def _archetype_from_json(role: str, data: dict) -> Archetype:
    budget = data.get("budget", {})
    return Archetype(
        role=role,
        label=data.get("label", role),
        hp=float(budget.get("hp", 1.0)),
        st=float(budget.get("st", 1.0)),
        mg=float(budget.get("mg", 1.0)),
        defense=float(budget.get("defense", 1.0)),
        agility=float(budget.get("agility", 1.0)),
        offensive_weights=_offensive_weights_from_json(role, data),
        skill_use_chance=int(data.get("skill_use_chance", 0)),
        skills=_kit_from_json(role, data),
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

    Cada eixo é resolvido pelo seu próprio caminho — orçamento × multiplicador do
    arquétipo × `geometric` — exatamente como HP, defesa e agilidade já eram. Não
    existe mais um passo de conversão no meio: o que o arquétipo declara é o que
    o monstro tem.

    O deck também é do nível: `deck_for_level`, não o kit inteiro. Antes todo
    monstro nascia com as 3 a 7 cartas do arquétipo no nível 1, enquanto o herói
    nasce com uma — e o documento já registrava, do lado do herói, que entregar o
    deck cheio de graça era defeito.

    Args:
        role: Papel do arquétipo.
        level: Nível do monstro.
        name: Nome de exibição. Sem ele, usa o rótulo do papel.

    Returns:
        Instância de `Monster` já configurada com papel, skills e comportamento.
    """
    archetype = get_archetype(role)

    monster = Monster(
        name or f"{archetype.label} Nv.{level}",
        level,
        hp=geometric(MONSTER_BUDGET_HP * archetype.hp, level),
        mp=geometric(MONSTER_BUDGET_MP, level),
        st=geometric(MONSTER_BUDGET_OFFENSE * archetype.st, level),
        mg=geometric(MONSTER_BUDGET_OFFENSE * archetype.mg, level),
        df=geometric(MONSTER_BUDGET_DEFENSE * archetype.defense, level),
        ag=geometric(MONSTER_BUDGET_AGILITY * archetype.agility, level),
        offensive_weights=archetype.offensive_weights,
    )
    monster.role = archetype.role
    monster.skills = deck_for_level(archetype, level)
    monster.skill_use_chance = archetype.skill_use_chance
    if archetype.role in MILESTONE_ROLES:
        monster.is_boss = True
    return monster
