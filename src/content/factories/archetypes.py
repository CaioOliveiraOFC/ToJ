"""Arquétipos de monstro — papel, orçamento e comportamento.

Antes disto o jogo tinha 121 nomes de monstro e uma única criatura: as quatro
categorias do JSON mudavam apenas a lista de onde o nome era sorteado, e
`create_monster` aplicava as mesmas fórmulas a todas. Sem papéis diferentes não
existe counterplay, porque não existe nada a counterar.

Cada arquétipo distribui o mesmo orçamento de nível de um jeito diferente, e a
regra que fecha o sistema é: **todo arquétipo precisa de pelo menos uma classe
que sofre contra ele**. O skirmisher existe para que esquiva não seja resposta
universal; o controlador existe para que depender de MP tenha custo; o tank
existe para que dano explosivo não resolva tudo.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.content.skills_loader import SkillCard
from src.entities.monsters import Monster
from src.shared.constants import (
    GROWTH_RATE,
    MONSTER_BUDGET_AGILITY,
    MONSTER_BUDGET_ATTACK,
    MONSTER_BUDGET_DEFENSE,
    MONSTER_BUDGET_HP,
    MONSTER_BUDGET_MP,
)


def _skill(
    skill_id: str,
    name: str,
    effect_type: str,
    effect_value,
    *,
    mana_cost: int = 20,
    cooldown: int = 3,
    duration: int = 2,
    chance: int = 100,
    target: str = "enemy",
    effect_stat: str = "",
) -> SkillCard:
    """Monta uma skill de monstro reaproveitando o mesmo `SkillCard` do herói.

    Reusar a carta do herói significa que `combat.apply_skill` trata os dois lados
    com o mesmo código — o monstro não ganha uma segunda implementação de dano
    que possa divergir da do jogador.
    """
    return SkillCard(
        id=skill_id,
        name=name,
        skill_class="Monster",
        level_required=1,
        mana_cost=mana_cost,
        effect_type=effect_type,
        effect_value=effect_value,
        effect_stat=effect_stat,
        description="",
        target=target,
        duration=duration,
        chance=chance,
        rarity="Common",
        is_initial=False,
        cooldown=cooldown,
    )


@dataclass(frozen=True, slots=True)
class Archetype:
    """Perfil de um papel de monstro.

    Os multiplicadores incidem sobre o orçamento do nível. Um arquétipo que ganha
    em um eixo deve perder em outro — é isso que dá a ele uma fraqueza explorável.
    """

    role: str
    label: str
    hp: float = 1.0
    attack: float = 1.0
    defense: float = 1.0
    agility: float = 1.0
    skill_use_chance: int = 0
    skills: tuple[SkillCard, ...] = ()
    threat: str = ""
    counterplay: str = ""
    names: tuple[str, ...] = field(default=())


ARCHETYPES: dict[str, Archetype] = {
    "trash": Archetype(
        role="trash",
        label="Trash",
        hp=0.60, attack=0.70, defense=0.85, agility=0.95,
        threat="Acúmulo. Nunca mata sozinho, drena recurso em grupo.",
        counterplay="Matar rápido e gastar pouco.",
        names=("Goblin", "Rato Gigante", "Slime Verde", "Kobold", "Esqueleto",
               "Morcego Vampiro", "Verme da Terra", "Corvo Sanguinário"),
    ),
    "bruiser": Archetype(
        role="bruiser",
        label="Bruiser",
        hp=1.0, attack=1.0, defense=1.0, agility=1.0,
        skill_use_chance=25,
        skills=(_skill("mob_golpe_pesado", "Golpe Pesado", "damage", 40, mana_cost=15, cooldown=3),),
        threat="Pressão constante. O combate padrão.",
        counterplay="Trocar dano com vantagem.",
        names=("Orc", "Bandido", "Lobo Faminto", "Hobgoblin", "Cultista Fanático",
               "Javali Atroz", "Homem-Lagarto"),
    ),
    "tank": Archetype(
        role="tank",
        label="Tank",
        hp=1.9, attack=0.75, defense=1.9, agility=0.6,
        skill_use_chance=35,
        skills=(_skill("mob_carapaca", "Carapaça", "damage_reduction", 35,
                       mana_cost=20, cooldown=4, duration=3, target="self"),),
        threat="Duração. Alonga o combate e força atrito.",
        counterplay="Dano contínuo em vez de explosão; trazer recurso de sobra.",
        names=("Golem de Pedra", "Troll das Cavernas", "Gárgula", "Esqueleto Encouraçado",
               "Golem de Ferro", "Ente Corrompido"),
    ),
    "glass_cannon": Archetype(
        role="glass_cannon",
        label="Glass cannon",
        hp=0.55, attack=1.9, defense=0.5, agility=1.1,
        skill_use_chance=45,
        skills=(_skill("mob_rajada", "Rajada Arcana", "damage", 70, mana_cost=25, cooldown=2),),
        threat="Pico de dano. Pune quem erra a ordem de foco.",
        counterplay="Matar primeiro ou atordoar.",
        names=("Necromante", "Cultista", "Aparição", "Lich Aprendiz",
               "Elemental do Fogo Menor", "Anomalia Arcana"),
    ),
    "skirmisher": Archetype(
        role="skirmisher",
        label="Skirmisher",
        hp=0.75, attack=0.95, defense=0.7, agility=2.6,
        skill_use_chance=30,
        skills=(_skill("mob_corte_rapido", "Corte Rápido", "damage", 30, mana_cost=12, cooldown=2),),
        threat="Acerta quem esquiva e age primeiro.",
        counterplay="Controle, ou defesa que não dependa de esquiva.",
        names=("Caçador Furtivo", "Assassino das Sombras", "Harpia", "Warg",
               "Sombra", "Centauro Batedor"),
    ),
    "controller": Archetype(
        role="controller",
        label="Controlador",
        hp=0.9, attack=0.8, defense=0.9, agility=1.3,
        skill_use_chance=55,
        skills=(
            _skill("mob_torpor", "Torpor", "status", "stun", mana_cost=25, cooldown=3,
                   duration=1, chance=55),
            _skill("mob_queima_mana", "Queima de Mana", "status", "mana_burn",
                   mana_cost=20, cooldown=3, duration=2, chance=75),
        ),
        threat="Nega turnos e recurso.",
        counterplay="Matar rápido, ou não depender de MP.",
        names=("Banshee", "Súcubo", "Mestre das Ilusões", "Espectro Uivante",
               "Devorador de Mentes Menor", "Naga"),
    ),
    "support": Archetype(
        role="support",
        label="Suporte",
        hp=0.8, attack=0.6, defense=1.0, agility=1.0,
        skill_use_chance=60,
        skills=(
            _skill("mob_regenerar", "Regenerar", "heal", 30, mana_cost=25, cooldown=3,
                   target="self"),
            _skill("mob_bencao", "Bênção Sombria", "buff", 25, mana_cost=20, cooldown=4,
                   duration=3, target="self", effect_stat="df"),
        ),
        threat="Multiplica os outros. Sozinho é inofensivo.",
        counterplay="Prioridade de alvo: matar antes do resto.",
        names=("Cultista Sombrio", "Xamã Goblin", "Aclito Corrompido", "Espectro Curandeiro"),
    ),
    "elite": Archetype(
        role="elite",
        label="Elite",
        hp=1.8, attack=1.4, defense=1.25, agility=1.1,
        skill_use_chance=45,
        skills=(
            _skill("mob_investida_brutal", "Investida Brutal", "damage", 55,
                   mana_cost=25, cooldown=3),
            _skill("mob_rugido", "Rugido", "status", "weakened", mana_cost=20,
                   cooldown=4, duration=3, chance=70),
        ),
        threat="Marco do andar. Testa se a build funciona.",
        counterplay="Chegar com recurso. Preparar antes de engajar.",
        names=("Minotauro", "Cavaleiro Corrompido", "Manticora", "Ogre",
               "Wyvern", "Dullahan", "Quimera"),
    ),
    "boss": Archetype(
        role="boss",
        label="Boss",
        hp=3.0, attack=1.5, defense=1.4, agility=1.15,
        skill_use_chance=55,
        skills=(
            _skill("boss_devastar", "Devastar", "damage", 80, mana_cost=30, cooldown=3),
            _skill("boss_esmagar", "Esmagar", "status", "stun", mana_cost=30,
                   cooldown=4, duration=1, chance=50),
            _skill("boss_couraca", "Couraça Ancestral", "damage_reduction", 30,
                   mana_cost=25, cooldown=5, duration=3, target="self"),
        ),
        threat="Portão a cada 5 andares. Exige execução por muitos turnos.",
        counterplay="Plano, recurso e uso correto de controle.",
        names=("Dragão Jovem", "Lich Menor", "Rei Goblin", "Lorde Vampiro",
               "Behemoth", "Rei Esqueleto", "Titã Ancião"),
    ),
}

# Papéis que povoam um andar comum, com o peso de aparição. Elite e boss são
# colocados pelo gerador do andar, não sorteados aqui.
ROUTINE_ROLE_WEIGHTS: dict[str, int] = {
    "trash": 42,
    "bruiser": 24,
    "skirmisher": 12,
    "glass_cannon": 10,
    "tank": 7,
    "controller": 3,
    "support": 2,
}


def scale(base: float, level: int) -> int:
    """Aplica a razão de crescimento comum ao nível pedido."""
    return max(1, int(round(base * (GROWTH_RATE ** (max(1, level) - 1)))))


def get_archetype(role: str) -> Archetype:
    """Resolve o papel. Papel desconhecido é erro, não silêncio."""
    if role not in ARCHETYPES:
        raise ValueError(f"Arquétipo desconhecido: {role!r}. Use um de {sorted(ARCHETYPES)}.")
    return ARCHETYPES[role]


def spawn_by_role(role: str, level: int, name: str | None = None) -> Monster:
    """Cria um monstro do papel pedido, com o orçamento do nível.

    O ataque é fixado através de `st` e `mg` porque `Monster` deriva
    `avg_damage = (st + mg) // 3` — manter essa derivação preserva os valores que
    a tela de status já mostra.
    """
    arch = get_archetype(role)

    attack = scale(MONSTER_BUDGET_ATTACK * arch.attack, level)
    stat_for_attack = int(attack * 1.5)

    monster = Monster(
        name or f"{arch.label} Nv.{level}",
        level,
        hp=scale(MONSTER_BUDGET_HP * arch.hp, level),
        mp=scale(MONSTER_BUDGET_MP, level),
        st=stat_for_attack,
        mg=stat_for_attack,
        df=scale(MONSTER_BUDGET_DEFENSE * arch.defense, level),
        ag=scale(MONSTER_BUDGET_AGILITY * arch.agility, level),
    )
    monster.role = arch.role
    monster.skills = list(arch.skills)
    monster.skill_use_chance = arch.skill_use_chance
    if arch.role in ("elite", "boss"):
        monster.is_boss = True
    return monster
