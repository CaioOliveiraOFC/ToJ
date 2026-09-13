"""Skills — loader, modelo e gerador de escolhas."""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.data.loader import load_json
from src.shared.constants import (
    PASSIVE_COMMON_WEIGHT,
    PASSIVE_EPIC_WEIGHT,
    PASSIVE_LEGENDARY_WEIGHT,
    PASSIVE_RARE_WEIGHT,
    SKILL_OFFER_SIZE,
)
from src.shared.registries import set_initial_skill_provider

# Classe das cartas que qualquer um pode receber.
NEUTRAL = "Neutral"

# Classe das cartas de monstro. Não é um pool de oferta — nenhum herói recebe
# uma carta destas —, é a etiqueta que diz contra qual referência o validador
# mede o orçamento delas. A GRAMÁTICA é a mesma; só a régua muda, porque um
# tanque e um ladino não têm os mesmos atributos.
MONSTER_SKILL_CLASS = "Monster"


@dataclass(frozen=True)
class ScalingTerm:
    """Um atributo e o peso dele na construção do BASE da skill."""

    stat: str
    weight: float


@dataclass(frozen=True)
class SecondaryEffect:
    """O efeito secundário de uma skill: no máximo um, e do catálogo global.

    A skill escolhe CHANCE, INTENSIDADE e DURAÇÃO. O que `poison` significa é do
    catálogo — nenhuma carta redefine efeito.
    """

    effect: str
    chance: int = 100
    duration: int = 0
    intensity: float = 0.0


@dataclass(frozen=True)
class Requirement:
    """O que a skill exige do equipamento para poder ser USADA.

    Não impede aprender: o jogador pode pegar a carta e ir atrás do escudo
    depois. É o que permite pivotar uma build em vez de só reagir ao que caiu.
    """

    hand_type: str = ""
    hands: int = 0
    two_weapons: bool = False

    NOMES_DE_MAO = {
        "sword": "uma espada",
        "dagger": "uma adaga",
        "mace": "uma maça",
        "axe": "um machado",
        "staff": "um cajado",
        "wand": "uma varinha",
        "shield": "um escudo",
        "orb": "um orbe",
        "focus": "um foco",
        "bow": "um arco",
    }

    def describe(self) -> str:
        """O requisito em português, para a tela dizer o que falta.

        Sem isto a recusa apareceria como um "não pode usar" sem motivo, e um
        objetivo de build viraria um bug aparente.
        """
        partes = []
        if self.two_weapons:
            partes.append("as duas mãos ocupadas")
        if self.hands:
            partes.append(f"uma arma de {self.hands} mão(s)")
        if self.hand_type:
            partes.append(self.NOMES_DE_MAO.get(self.hand_type, self.hand_type))
        return " e ".join(partes) or "um equipamento específico"


@dataclass(frozen=True)
class SkillCard:
    """Carta de skill carregada do JSON.

    A carta descreve COMO o personagem transforma os atributos dele numa ação.
    Ela não carrega poder próprio: `scaling` diz de quais atributos o golpe
    nasce e `power` diz o peso da ação. O dano sai do personagem.
    """

    id: str
    name: str
    skill_class: str
    level_required: int
    mana_cost: int
    effect_type: str
    effect_value: int | str
    description: str
    target: str
    duration: int
    chance: int
    rarity: str
    is_initial: bool
    cooldown: int = 0
    # Para skills de buff: qual atributo o buff modifica ("st", "ag", "df",
    # "mg", "crit_chance", ...). Antes, o motor reconhecia buffs por nome
    # literal, então qualquer buff cujo nome não estivesse na lista era um
    # no-op silencioso. Nomear o alvo do efeito no dado resolve isso na origem.
    effect_stat: str = ""
    # Custo em percentual da mana MÁXIMA de quem lança. `mana_cost` é o custo
    # absoluto herdado: ele fica como piso e como valor de exibição para
    # conteúdo que ainda não migrou, mas quem tem percentual paga o percentual.
    #
    # A razão é a mesma que já obrigou poções e curas a virarem percentuais: a
    # mana do herói cresce em progressão geométrica e o número do JSON não
    # crescia. No andar 5 o Mago gastava 74% da mana num andar e ficava seco em
    # 57% das runs; no andar 20 gastava 1%. O custo deixava de existir
    # exatamente onde o jogador tem mais skills para escolher, e a decisão
    # virava "use sempre a de maior dano".
    mana_cost_percent: float = 0.0
    # Condição situacional que rende `bonus_percent` de dano a mais. Existe para
    # que uma skill de dano seja mais do que um ataque básico caro: sem ela, a
    # decisão "qual skill uso" é aritmética fixa — sempre a de maior valor —, e
    # o deck não precisa ser lido, só ordenado. Com ela, congelar o alvo passa a
    # valer o turno que custou, porque a skill seguinte cobra por isso.
    bonus_condition: str = ""
    bonus_percent: int = 0

    # --- gramática V2 ---
    # De quais atributos o golpe nasce. Até dois, somando 1.0. Vazio em skill
    # que não causa dano — não há o que escalar num buff.
    scaling: tuple[ScalingTerm, ...] = ()
    # Peso da AÇÃO. Diferencia golpe leve de golpe pesado, e atua na construção
    # do BASE — nunca vira um MULT escondido depois do funil.
    power: float = 0.0
    # Quanto esta ação específica ajuda ou atrapalha o acerto. Entra na MESMA
    # conta de `hit_chance`, ao lado de precisão e medo.
    accuracy_modifier: int = 0
    secondary: SecondaryEffect | None = None
    requires: Requirement | None = None


_SKILL_REGISTRY: dict[str, SkillCard] | None = None


def _get_registry() -> dict[str, SkillCard]:
    """Carrega e cacheia o registro de skills. Chave: id."""
    global _SKILL_REGISTRY
    if _SKILL_REGISTRY is None:
        data = load_json("skills.json")
        _SKILL_REGISTRY = {s["id"]: card_from_json(s) for s in data["skills"]}
    return _SKILL_REGISTRY


def card_from_json(dados: dict) -> SkillCard:
    """Constrói a carta a partir do JSON, incluindo a gramática V2."""
    campos = {}
    for nome, campo in SkillCard.__dataclass_fields__.items():
        if nome in ("scaling", "power", "accuracy_modifier", "secondary", "requires"):
            continue
        padrao = "" if campo.type == "str" else 0
        campos[nome] = dados.get(nome, padrao)
    campos["scaling"] = tuple(
        ScalingTerm(str(t["stat"]), float(t["weight"])) for t in dados.get("scaling", ())
    )
    campos["power"] = float(dados.get("power", 0) or 0)
    campos["accuracy_modifier"] = int(dados.get("accuracy_modifier", 0) or 0)
    sec = dados.get("secondary")
    campos["secondary"] = (
        SecondaryEffect(
            effect=str(sec["effect"]),
            chance=int(sec.get("chance", 100)),
            duration=int(sec.get("duration", 0)),
            intensity=float(sec.get("intensity", 0) or 0),
        )
        if sec
        else None
    )
    req = dados.get("requires")
    campos["requires"] = (
        Requirement(
            hand_type=str(req.get("hand_type", "")),
            hands=int(req.get("hands", 0)),
            two_weapons=bool(req.get("two_weapons", False)),
        )
        if req
        else None
    )
    return SkillCard(**campos)


def damage_preview(skill, caster) -> int:
    """Quanto esta carta faria na mão deste personagem, agora.

    Existe porque, depois da V2, a carta não carrega número de dano: perguntar
    "quanto vale" só faz sentido com um personagem junto. A tela de escolha
    precisa desse número — sem ele ela anunciava `effect_value`, que hoje é zero
    em toda skill de dano, e o jogador escolhia entre três cartas de "Dano: 0".

    Fica em `content/`, e não na tela, por duas razões. A primeira é o diagrama:
    `ui/` não importa `mechanics/`. A segunda é a que importa — a conta é UMA
    só, a do motor. Uma prévia calculada à parte é a promessa de divergir do
    dano real no primeiro ajuste de fórmula, e uma tela que mente sobre o dano é
    pior do que uma que não o mostra.
    """
    from src.mechanics.combat import skill_damage_base

    return skill_damage_base(caster, skill)


def load_skills() -> list[SkillCard]:
    """Retorna lista de todas as skills disponíveis."""
    return list(_get_registry().values())


def get_skill_by_id(skill_id: str) -> SkillCard | None:
    """Busca skill pelo ID. Retorna None se não encontrada."""
    return _get_registry().get(skill_id)


def get_skill_by_name_fallback(skill_name: str) -> SkillCard | None:
    """Fallback para buscar skill pelo nome (para migração de saves antigos)."""
    for skill in _get_registry().values():
        if skill.name == skill_name:
            return skill
    return None


def get_skills_for_class(class_name: str) -> list[SkillCard]:
    """Retorna todas as skills de uma classe específica."""
    return [s for s in load_skills() if s.skill_class == class_name]


def get_initial_skills(class_name: str) -> list[SkillCard]:
    """A skill inicial da classe. Uma só — a assinatura, não um sorteio."""
    return [s for s in get_skills_for_class(class_name) if s.is_initial]


def get_offer_pool(class_name: str) -> list[SkillCard]:
    """As cartas que esta classe pode receber: as dela mais as Neutral.

    Exclusiva significa exclusiva: um Guerreiro nunca vê uma carta de Mago. As
    Neutral são ferramentas universais, e o validador as segura num teto
    ofensivo menor para não virarem uma quarta classe.
    """
    return [s for s in load_skills() if s.skill_class in (class_name, NEUTRAL)]


def generate_skill_choices(
    class_name: str,
    player_level: int,
    player_skill_ids: list[str],
    count: int = SKILL_OFFER_SIZE,
    seen_ids: set[str] | None = None,
) -> list[SkillCard]:
    """Monta a oferta: `count` cartas distintas, priorizando o inédito.

    Três regras, nesta ordem:

    1. carta já ATIVA nunca aparece — oferecer o que o jogador já tem é gastar
       um dos três espaços com nada;
    2. cartas nunca vistas nesta run vêm primeiro;
    3. só quando as inéditas elegíveis acabam é que as já vistas voltam.

    Sem a regra 2, o jogador via a mesma carta três vezes antes de conhecer
    metade do catálogo, e a escolha virava sorteio. `seen_ids` é estado de run e
    é salvo com o herói.

    Havendo menos de `count` candidatas, devolve o que existir — a oferta menor
    é a resposta honesta a um catálogo pequeno.
    """
    ativas = set(player_skill_ids)
    vistas = set(seen_ids or ())
    elegiveis = [
        s
        for s in get_offer_pool(class_name)
        if s.level_required <= player_level and s.id not in ativas
    ]
    ineditas = [s for s in elegiveis if s.id not in vistas]
    repescagem = [s for s in elegiveis if s.id in vistas]

    escolhidas: list[SkillCard] = []
    for pool in (ineditas, repescagem):
        escolhidas += _sortear_por_raridade(pool, count - len(escolhidas))
        if len(escolhidas) >= count:
            break
    return escolhidas


def _sortear_por_raridade(pool: list[SkillCard], quantas: int) -> list[SkillCard]:
    """Tira `quantas` cartas distintas do pool, com peso por raridade."""
    if quantas <= 0 or not pool:
        return []
    pesos_por_raridade = {
        "Common": PASSIVE_COMMON_WEIGHT,
        "Rare": PASSIVE_RARE_WEIGHT,
        "Epic": PASSIVE_EPIC_WEIGHT,
        "Legendary": PASSIVE_LEGENDARY_WEIGHT,
    }
    restante = list(pool)
    pesos = [pesos_por_raridade.get(s.rarity, 1) for s in restante]
    escolhidas: list[SkillCard] = []
    while restante and len(escolhidas) < quantas:
        [pick] = random.choices(restante, weights=pesos, k=1)
        i = restante.index(pick)
        escolhidas.append(restante.pop(i))
        pesos.pop(i)
    return escolhidas


# Registra este módulo como a fonte de skills iniciais. `entities/` consulta o
# registro em `shared/` e nunca importa de `content/`, como manda a regra 3 da
# arquitetura: entidades não conhecem dados.
set_initial_skill_provider(get_initial_skills)
