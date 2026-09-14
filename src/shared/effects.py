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

from src.shared import effect_core as core

# Atributos base que um buff pode somar. Lidos por `get_stat`.
ATTRIBUTE_STATS = ("st", "ag", "mg", "df", "hp", "mp")

# Modificadores que não são atributos: entram no cálculo de combate.
# `evasion` reduz a chance de o atacante acertar.
# `damage_reduction` reduz o dano recebido, em percentual.
# `life_steal` devolve ao atacante um percentual do dano causado.
# `mana_regen` restaura MP no início de cada turno.
# `precision` soma pontos à chance de o ATACANTE acertar — a mesma conta que a
# agilidade relativa, o medo e a mira da ação alimentam. Não é um segundo
# sorteio e não toca no tamanho do golpe.
# `status_resistance` é resistência GLOBAL à aplicação de status: soma com a
# resistência específica do alvo e muda só a chance de o estado pegar.
COMBAT_MODIFIERS = (
    "crit_chance",
    "crit_damage",
    "evasion",
    "damage_reduction",
    "life_steal",
    "mana_regen",
    "stun_chance",
    "precision",
    "status_resistance",
)

# Os status negativos que um alvo pode resistir. É a união das famílias abaixo,
# montada a partir delas para não virar uma segunda lista que envelhece sozinha.
#
# Ficam de fora, e de propósito: `damage_reduction` (buff que o lançador põe em
# si mesmo), `invisible` (benéfico) e os rótulos de poção `true_damage` e
# `death_ignore` — ninguém resiste ao próprio consumível.

# As famílias agora vêm do CATÁLOGO, e não de listas paralelas: um status novo
# entra em `effect_core.CATALOG` e todo mundo enxerga, sem ninguém precisar
# lembrar de acrescentá-lo aqui também.
TURN_SKIPPING_STATUSES = core.effects_of_family(core.FAMILY_CONTROL)
DAMAGE_OVER_TIME = core.effects_of_family(core.FAMILY_DOT)
RESOURCE_DRAIN = core.effects_of_family(core.FAMILY_DRAIN)


# Quanto vale um turno de controle, por família de status. Serve para comparar
# duas cartas de controle entre si — na escolha da carta e na hora de lançá-la.
#
# Sem isto, as duas camadas tratavam todo status como equivalente: a política de
# escolha dava a mesma constante para os oito, e o bot de combate pegava o
# primeiro da lista. `Raio Congelante`, que rouba o turno inteiro do inimigo,
# empatava com `Golpe Baixo`, que só reduz o dano dele — e quem decidia era a
# ordem em que as cartas tinham entrado no deck.
#
# Roubar o turno vale mais que qualquer outra coisa: é o dano do inimigo inteiro
# a zero naquela rodada. Dano por turno vem depois, porque acumula. O resto
# apenas reduz uma parcela.
# Condições que uma skill de dano pode exigir para render o bônus. O nome vive
# aqui porque o dado (JSON) e o motor precisam concordar sobre a grafia, e uma
# condição escrita errada seria um bônus que nunca acontece — placebo silencioso,
# que é o defeito mais caro que esta base já teve.
BONUS_CONDITIONS = (
    "target_controlled",  # alvo perdendo o turno: atordoado, congelado, dormindo
    "target_afflicted",  # alvo sob qualquer status
    "target_wounded",  # alvo abaixo do limiar de execução
    "target_healthy",  # alvo ainda intacto: recompensa a abertura
    "caster_wounded",  # quem lança está abaixo do limiar: golpe de desespero
)


def negative_statuses() -> tuple[str, ...]:
    """Os status resistíveis, na grafia que o motor usa. Vêm do catálogo."""
    return core.negative_effects()


def status_resistance(entity, status: str) -> float:
    """Quanto `entity` resiste a `status`, em percentual de 0 a 100.

    Resistência a STATUS não é resistência a DANO: ela muda a chance de o estado
    pegar, e não o tamanho do golpe. Um alvo com 100% de resistência a `frozen`
    leva o dano inteiro e simplesmente não congela.

    Lê por duck typing, como o resto do módulo. Sem o método ou sem o campo,
    devolve zero — que é o que todo personagem e todo monstro têm hoje.
    """
    getter = getattr(entity, "get_status_resistance", None)
    if callable(getter):
        return _clamp_percent(getter(status))
    return _clamp_percent((getattr(entity, "resistances", None) or {}).get(status, 0))


def effective_status_chance(base_chance: float, resistance: float) -> float:
    """`base × (1 - resistência/100)`. Delegada ao núcleo — a regra é uma só."""
    return core.effective_chance(base_chance, resistance)


def _clamp_percent(valor) -> float:
    return max(0.0, min(100.0, float(valor or 0)))


def control_weight(effect: str) -> float:
    """Peso de um status como controle. Maior é melhor."""
    if effect in TURN_SKIPPING_STATUSES:
        return 3.0
    if effect in DAMAGE_OVER_TIME:
        return 2.0
    return 1.0


# Quais efeitos quebram ao levar dano. Declarado no catálogo, por efeito.
BREAKS_ON_DAMAGE = tuple(d.effect_id for d in core.CATALOG.values() if d.breaks_on_damage)

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
    """Valor total de um modificador de combate: buff, passiva e equipamento.

    As três somam porque representam a mesma coisa por caminhos diferentes —
    uma poção de crítico e a passiva Lâmina Afiada devem se acumular, não
    competir. E as três são fontes SEPARADAS: equipamento não entra por
    `get_passive_bonus`, ou "de onde veio este número?" deixa de ter resposta.

    Duck typing, como o resto do módulo: o monstro não tem equipamento e não
    tem o método, então soma zero sem precisar de exceção.
    """
    total = float(sum_buffs(entity, kind))
    for fonte in ("get_passive_bonus", "get_equipment_bonus"):
        getter = getattr(entity, fonte, None)
        if callable(getter):
            total += float(getter(kind))
    return total


def outgoing_damage_multiplier(entity) -> float:
    """Multiplicador de dano causado pela entidade.

    Vazio hoje, e de propósito. `weakened` virou efeito de ATRIBUTO (reduz Força,
    e o dano cai por consequência) e `fear` virou efeito de ACERTO (o golpe
    falha mais, e não bate mais fraco). Nenhum dos dois multiplica o dano por
    fora — mas o ponto continua aqui, porque é o lugar certo caso um efeito
    genuinamente multiplicativo apareça, e tirá-lo obrigaria a reabrir o funil.
    """
    return 1.0


def incoming_damage_multiplier(entity) -> float:
    """Multiplicador de dano recebido: buff, passiva, equipamento e encantamento.

    Uma leitura só. Havia uma segunda, para o dicionário solto que a skill de
    monstro escrevia — a última mecânica com representação exclusiva de monstro,
    e a exceção morreu junto com ela.
    """
    return max(0.1, 1 - min(80.0, combat_modifier(entity, "damage_reduction")) / 100)


def wake_on_damage(entity) -> list[str]:
    """Remove os status que quebram ao levar dano. Delegada ao núcleo."""
    return core.break_on_damage(entity)
