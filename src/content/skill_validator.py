"""Skill Budget Validator: as leis que todo conteúdo de skill precisa obedecer.

O catálogo vai ser escrito por IA em JSON, e IA devaneia. O motor é quem define
as leis, e elas são verificadas ANTES de a carta entrar no jogo — estaticamente,
sem rodar combate:

    JSON  ->  loader  ->  VALIDATOR  ->  integridade  ->  jogo

O orçamento não é o balanceamento final. É guardrail: ele barra o absurdo, não
afina o razoável. Uma carta pode passar aqui e ainda assim ser forte demais — o
que ela não pode é entrar sem ninguém saber quanto custa.

A medida é comparável entre classes de propósito. `power` sozinho não serve:
a Agilidade do Ladino vale 92 onde a Força do Guerreiro vale 191, então a mesma
pancada exige quase o dobro de `power` nele. Medir contra um personagem de
REFERÊNCIA por classe corrige isso — o orçamento é o dano em % do ataque básico
daquela referência, e 200% quer dizer a mesma coisa para os três.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.shared import effect_core as core
from src.shared.constants import (
    MAX_ACTIVE_SKILLS,
    MAX_OFFENSIVE_BUDGET,
    MAX_OFFENSIVE_BUDGET_NEUTRAL,
    MAX_SCALING_STATS,
    RARITY_MULTIPLIERS,
    SKILL_ACCURACY_RANGE,
    SKILL_REFERENCE_NEUTRAL,
    SKILL_REFERENCE_STATS,
    SKILL_SCALING_STATS,
)

NEUTRAL = "Neutral"
CLASSES_VALIDAS = frozenset(SKILL_REFERENCE_STATS) | {NEUTRAL}
TIPOS_VALIDOS = frozenset({"damage", "buff", "heal", "status", "damage_reduction"})
ALVOS_VALIDOS = frozenset({"self", "enemy"})

# Tipos de peça que uma skill pode exigir. Espelha `Item.hand_type`, que é
# descritivo: o validador é quem impede um requisito inventado de passar.
HAND_TYPES_VALIDOS = frozenset(
    {"sword", "dagger", "mace", "axe", "staff", "wand", "shield", "orb", "focus", "bow"}
)

# Quanto cada coisa custa de orçamento, além do dano. Números redondos e
# deliberadamente grosseiros: é guardrail, não planilha de balanceamento.
CUSTO_CONTROLE = 60  # roubar o turno vale mais que qualquer outra coisa
CUSTO_DOT = 30
CUSTO_DEBUFF = 25
CUSTO_BUFF = 20
CUSTO_POR_TURNO_DE_DURACAO = 5
CUSTO_POR_PONTO_DE_ACERTO = 2  # accuracy positiva é poder

# Créditos por custo assumido. Têm TETO: sem ele, bastaria pedir cooldown 99
# para justificar qualquer absurdo.
CREDITO_MAX = 60
CREDITO_POR_TURNO_DE_RECARGA = 8
CREDITO_POR_PONTO_DE_MANA = 1.5  # sobre `mana_cost_percent`
CREDITO_POR_REQUISITO = 20


@dataclass
class Veredito:
    """O resultado da validação de uma carta."""

    skill_id: str
    erros: list[str] = field(default_factory=list)
    orcamento: int = 0
    teto: int = 0

    @property
    def ok(self) -> bool:
        return not self.erros

    def __str__(self) -> str:
        if self.ok:
            return f"PASS  {self.skill_id}  (orçamento {self.orcamento}/{self.teto})"
        return f"FAIL  {self.skill_id}\n" + "\n".join(f"      - {e}" for e in self.erros)


def _referencia(skill_class: str) -> dict:
    return (
        SKILL_REFERENCE_NEUTRAL
        if skill_class == NEUTRAL
        else SKILL_REFERENCE_STATS.get(skill_class, SKILL_REFERENCE_NEUTRAL)
    )


def offensive_budget(skill, com_bonus: bool = True) -> int:
    """Dano da carta em % do ataque básico da referência da classe dela.

    Zero para skill que não causa dano — o custo dela é medido pelos efeitos.

    É a unidade em que este projeto compara duas cartas de dano depois da V2.
    `effect_value` não serve mais: ele era o dano da carta e agora é sempre
    zero. E `power` sozinho tampouco — a Agilidade do Ladino vale 92 onde a
    Força do Guerreiro vale 191, então a mesma pancada pede quase o dobro de
    `power` nele, e comparar os dois números diretamente diria que o Ladino bate
    mais forte.

    `com_bonus=False` devolve o PISO da carta: o que ela entrega quando a
    condição situacional não ajuda. As duas pontas juntas são o que separa uma
    carta dominada (pior nas duas) de uma aposta diferente (pior no piso, melhor
    no teto).
    """
    escala = getattr(skill, "scaling", ())
    if skill.effect_type != "damage" or not escala:
        return 0
    ref = _referencia(skill.skill_class)
    base = sum(ref.get(t.stat, 0) * t.weight for t in escala) * float(skill.power)
    if com_bonus and getattr(skill, "bonus_percent", 0):
        # A condição não é garantida, mas o teto tem de contar o melhor caso:
        # é ele que decide se a carta pode quebrar o jogo quando alinha.
        base *= 1 + skill.bonus_percent / 100
    return int(base / max(1, ref["avg"]) * 100)


def effect_budget(skill) -> int:
    """Quanto os efeitos da carta custam, principal e secundário somados."""
    total = 0
    for efeito, chance, duracao in _efeitos_da_carta(skill):
        definicao = core.definition(efeito)
        if definicao is None:
            continue
        if definicao.family == core.FAMILY_CONTROL:
            custo = CUSTO_CONTROLE
        elif definicao.family == core.FAMILY_DOT:
            custo = CUSTO_DOT
        elif definicao.positive:
            custo = CUSTO_BUFF
        else:
            custo = CUSTO_DEBUFF
        total += int(custo * max(0, min(100, chance)) / 100)
        total += max(0, duracao - 1) * CUSTO_POR_TURNO_DE_DURACAO
    if getattr(skill, "accuracy_modifier", 0) > 0:
        total += skill.accuracy_modifier * CUSTO_POR_PONTO_DE_ACERTO
    return total


def _efeitos_da_carta(skill):
    """Os efeitos que a carta aplica: o principal, quando é status, e o secundário."""
    if skill.effect_type == "status" and isinstance(skill.effect_value, str):
        yield skill.effect_value, int(skill.chance or 100), int(skill.duration or 0)
    sec = getattr(skill, "secondary", None)
    if sec is not None:
        yield sec.effect, int(sec.chance), int(sec.duration)


def budget_credit(skill) -> int:
    """Créditos por custo assumido, com TETO.

    Cooldown enorme e requisito de equipamento devolvem orçamento, mas nunca o
    suficiente para justificar uma carta absurda: `CREDITO_MAX` é o que impede
    "cooldown 99" de virar licença para tudo.
    """
    credito = max(0, int(skill.cooldown) - 1) * CREDITO_POR_TURNO_DE_RECARGA
    credito += int(float(getattr(skill, "mana_cost_percent", 0)) * CREDITO_POR_PONTO_DE_MANA)
    if getattr(skill, "requires", None) is not None:
        credito += CREDITO_POR_REQUISITO
    if getattr(skill, "accuracy_modifier", 0) < 0:
        credito += abs(skill.accuracy_modifier) * CUSTO_POR_PONTO_DE_ACERTO
    return min(CREDITO_MAX, credito)


def validate(skill) -> Veredito:
    """Valida uma carta contra todas as leis. Devolve o veredito com motivos."""
    v = Veredito(skill_id=str(getattr(skill, "id", "?")))
    erro = v.erros.append

    if skill.skill_class not in CLASSES_VALIDAS:
        erro(f"classe inválida: {skill.skill_class!r} (use {sorted(CLASSES_VALIDAS)})")
    if skill.effect_type not in TIPOS_VALIDOS:
        erro(f"tipo inválido: {skill.effect_type!r} (use {sorted(TIPOS_VALIDOS)})")
    if skill.target not in ALVOS_VALIDOS:
        erro(f"alvo inválido: {skill.target!r}")
    if skill.rarity not in RARITY_MULTIPLIERS:
        erro(f"raridade inválida: {skill.rarity!r}")

    # Custo: toda skill ativa paga MP e recarga. Skill de graça não tem decisão.
    if float(getattr(skill, "mana_cost_percent", 0)) <= 0 and int(skill.mana_cost) <= 0:
        erro("sem custo de mana: toda skill ativa precisa de MP > 0")
    if int(skill.cooldown) <= 0:
        erro("sem recarga: toda skill ativa precisa de cooldown > 0")

    # Escala
    escala = list(getattr(skill, "scaling", ()))
    if skill.effect_type == "damage":
        if not escala:
            erro("skill de dano sem `scaling`: o poder precisa vir de algum atributo")
        if float(getattr(skill, "power", 0)) <= 0:
            erro("skill de dano sem `power` positivo")
    if len(escala) > MAX_SCALING_STATS:
        erro(f"{len(escala)} atributos de escala; o máximo é {MAX_SCALING_STATS}")
    for termo in escala:
        if termo.stat not in SKILL_SCALING_STATS:
            erro(f"atributo de escala inválido: {termo.stat!r} (use {list(SKILL_SCALING_STATS)})")
        if termo.weight <= 0:
            erro(f"peso não positivo em {termo.stat!r}: {termo.weight}")
    if escala:
        soma = sum(t.weight for t in escala)
        if abs(soma - 1.0) > 0.001:
            erro(f"os pesos de escala somam {soma:.3f}; precisam somar 1.0")
    if len({t.stat for t in escala}) != len(escala):
        erro("atributo repetido no `scaling`")

    # Acerto
    lo, hi = SKILL_ACCURACY_RANGE
    if not lo <= int(getattr(skill, "accuracy_modifier", 0)) <= hi:
        erro(f"accuracy_modifier {skill.accuracy_modifier} fora da faixa {lo}..{hi}")

    # Efeitos: no máximo um secundário, e sempre do catálogo global
    sec = getattr(skill, "secondary", None)
    if sec is not None:
        if core.definition(sec.effect) is None:
            erro(f"efeito secundário desconhecido: {sec.effect!r} — não está no catálogo global")
        if not 0 < sec.chance <= 100:
            erro(f"chance do secundário fora de 0..100: {sec.chance}")
        if sec.duration < 0:
            erro(f"duração negativa no secundário: {sec.duration}")
        if sec.intensity < 0:
            erro(f"intensidade negativa no secundário: {sec.intensity}")
    if skill.effect_type == "status":
        if not isinstance(skill.effect_value, str) or core.definition(skill.effect_value) is None:
            erro(f"status principal desconhecido: {skill.effect_value!r}")
        if not 0 < int(skill.chance) <= 100:
            erro(f"chance fora de 0..100: {skill.chance}")
        if sec is not None and sec.effect == skill.effect_value:
            erro("secundário repete o efeito principal")

    # Requisito de equipamento
    req = getattr(skill, "requires", None)
    if req is not None:
        if req.hand_type and req.hand_type not in HAND_TYPES_VALIDOS:
            erro(f"hand_type inválido: {req.hand_type!r}")
        if req.hands and req.hands not in (1, 2):
            erro(f"requisito de mãos inválido: {req.hands}")
        if not (req.hand_type or req.hands or req.two_weapons):
            erro("`requires` vazio: declare o que a skill exige, ou remova o campo")
        if req.two_weapons and req.hands == 2:
            erro("requisito contraditório: duas armas E uma peça de duas mãos")

    # Orçamento
    v.orcamento = offensive_budget(skill) + effect_budget(skill) - budget_credit(skill)
    v.teto = MAX_OFFENSIVE_BUDGET_NEUTRAL if skill.skill_class == NEUTRAL else MAX_OFFENSIVE_BUDGET
    if v.orcamento > v.teto:
        erro(f"offensive budget {v.orcamento} > permitted {v.teto}")
    return v


def validate_all(skills) -> list[Veredito]:
    """Valida um catálogo inteiro. Devolve só os vereditos, sem levantar."""
    return [validate(s) for s in skills]


def assert_catalogo_valido(skills) -> None:
    """Levanta com o relatório completo se alguma carta for inválida."""
    reprovadas = [v for v in validate_all(skills) if not v.ok]
    if reprovadas:
        raise ValueError(
            f"{len(reprovadas)} skill(s) reprovadas pelo validador:\n"
            + "\n".join(str(v) for v in reprovadas)
        )


__all__ = [
    "MAX_ACTIVE_SKILLS",
    "Veredito",
    "assert_catalogo_valido",
    "budget_credit",
    "effect_budget",
    "offensive_budget",
    "validate",
    "validate_all",
]
