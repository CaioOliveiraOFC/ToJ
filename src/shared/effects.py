"""Registro de efeitos: buffs, status e modificadores de combate.

Antes deste módulo o motor reconhecia buffs por nome literal — havia uma cadeia
de `if` comparando com "Grito de Guerra", "Cortina de Fumaça" e mais três nomes.
Qualquer buff cujo nome não estivesse nessa lista era escrito no dicionário de
estado e nunca lido: 12 das 14 skills de buff, 6 dos 11 tipos de poção e 10 das
29 passivas eram no-ops silenciosos.

A correção não é aumentar a lista de nomes, é parar de identificar efeito por
nome. Aqui um efeito declara **qual atributo ele modifica**, e o motor consulta
o atributo. Conteúdo novo passa a funcionar sem tocar no motor, que é a razão de
os dados estarem em JSON.

Vive em `shared/` porque `entities/` precisa somar buffs para responder
`get_stat`, e `entities/` só pode importar de `shared/`. O módulo não importa
nada do projeto: ele lê o estado das entidades por duck typing, o que o mantém
sem dependência de camada nenhuma.
"""

from __future__ import annotations

# Atributos base que um buff pode somar. Lidos por `get_stat`.
ATTRIBUTE_STATS = ("st", "ag", "mg", "df", "hp", "mp")

# Modificadores que não são atributos: entram no cálculo de combate.
# `evasion` reduz a chance de o atacante acertar.
# `damage_reduction` reduz o dano recebido, em percentual.
# `life_steal` devolve ao atacante um percentual do dano causado.
# `mana_regen` restaura MP no início de cada turno.
COMBAT_MODIFIERS = (
    "crit_chance",
    "crit_damage",
    "evasion",
    "damage_reduction",
    "life_steal",
    "mana_regen",
    "dodge_chance",
    "stun_chance",
)

# Status que fazem a entidade perder o turno.
TURN_SKIPPING_STATUSES = ("frozen", "stun", "sleep")

# Status que sofrem dano ou perda de recurso a cada turno.
DAMAGE_OVER_TIME = ("poison", "bleed")

# Status que reduzem o dano causado pela entidade afetada, em percentual.
OUTGOING_DAMAGE_PENALTY = {"weakened": 30, "fear": 20}

# Status que drenam MP por turno.
RESOURCE_DRAIN = ("mana_burn",)

# `sleep` acorda ao levar dano — dormir para sempre seria atordoamento eterno,
# não sono, e removeria o counterplay de simplesmente bater no alvo.
BREAKS_ON_DAMAGE = ("sleep",)

# Nomes de buff legados usados por poções e skills antigas, mapeados para o
# atributo que eles sempre pretenderam modificar. Existe para que saves e
# conteúdo anteriores continuem válidos sem precisar de migração.
LEGACY_BUFF_STATS = {
    "Grito de Guerra": "st",
    "Cortina de Fumaça": "ag",
    "Força Aumentada": "st",
    "Defesa Aumentada": "df",
    "Agilidade Aumentada": "ag",
    "Velocidade Aumentada": "ag",
    "Evasão Aumentada": "evasion",
    "Chance de Crítico": "crit_chance",
    "Dano Crítico": "crit_damage",
    "Roubo de Vida": "life_steal",
    "Regeneração de Mana": "mana_regen",
}


def buff_value(entity, stat: str, raw: int) -> int:
    """Converte o valor declarado de um buff no valor efetivo.

    Para atributos (st, ag, mg, df), `raw` é um **percentual do atributo base**:
    um buff de defesa fixo em +8 pontos vale 23% no nível 1 e 2,6% no nível 20,
    ou seja, anti-escala junto com o herói e vira ruído no fim do jogo. Para
    modificadores que já são percentuais (crítico, evasão, roubo de vida), o
    valor é literal.
    """
    if stat in ATTRIBUTE_STATS:
        base = int(getattr(entity, f"base_{stat}", 0))
        return max(1, int(base * raw / 100))
    return int(raw)


def buff_stat(name: str, data: dict) -> str:
    """Descobre qual atributo um buff ativo modifica.

    Prefere o campo explícito `stat`; cai no mapa de nomes legados quando o buff
    veio de conteúdo antigo que não declarava o alvo do efeito.
    """
    declared = data.get("stat")
    if declared:
        return str(declared)
    return LEGACY_BUFF_STATS.get(name, "")


def sum_buffs(entity, stat: str) -> int:
    """Soma o valor de todos os buffs ativos que modificam `stat`."""
    total = 0
    for name, data in getattr(entity, "active_buffs", {}).items():
        if not isinstance(data, dict):
            continue
        if buff_stat(name, data) == stat:
            total += int(data.get("value", 0))
    return total


def combat_modifier(entity, kind: str) -> float:
    """Valor total de um modificador de combate: buffs somados às passivas.

    Buff e passiva somam porque representam a mesma coisa por caminhos
    diferentes — uma poção de crítico e a passiva Lâmina Afiada devem se
    acumular, não competir.
    """
    total = float(sum_buffs(entity, kind))
    getter = getattr(entity, "get_passive_bonus", None)
    if callable(getter):
        total += float(getter(kind))
    return total


def outgoing_damage_multiplier(entity) -> float:
    """Multiplicador de dano causado, considerando status debilitantes."""
    effects = getattr(entity, "active_effects", {})
    penalty = 0
    for name, data in effects.items():
        if name in OUTGOING_DAMAGE_PENALTY:
            value = data.get("value") if isinstance(data, dict) else None
            penalty += int(value if value is not None else OUTGOING_DAMAGE_PENALTY[name])
    return max(0.1, 1 - min(90, penalty) / 100)


def incoming_damage_multiplier(entity) -> float:
    """Multiplicador de dano recebido, considerando redução ativa e passiva."""
    reduction = 0.0
    effects = getattr(entity, "active_effects", {})
    data = effects.get("damage_reduction")
    if isinstance(data, dict):
        reduction += float(data.get("value", 0))
    reduction += combat_modifier(entity, "damage_reduction")
    return max(0.1, 1 - min(80.0, reduction) / 100)


def wake_on_damage(entity) -> list[str]:
    """Remove os status que quebram ao levar dano. Devolve o que foi removido."""
    effects = getattr(entity, "active_effects", {})
    removed = [name for name in BREAKS_ON_DAMAGE if name in effects]
    for name in removed:
        del effects[name]
    return removed
