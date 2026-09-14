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

from src.content.skills_loader import MONSTER_SKILL_CLASS
from src.shared import effect_core as core
from src.shared.constants import (
    CLASS_WEIGHTS,
    MAX_ACTIVE_SKILLS,
    MAX_OFFENSIVE_BUDGET,
    MAX_OFFENSIVE_BUDGET_NEUTRAL,
    MAX_SCALING_STATS,
    MONSTER_REFERENCE_LEVEL,
    RARITY_MULTIPLIERS,
    SKILL_ACCURACY_RANGE,
    SKILL_REFERENCE_NEUTRAL,
    SKILL_REFERENCE_STATS,
    SKILL_SCALING_STATS,
)

NEUTRAL = "Neutral"
CLASSES_VALIDAS = frozenset(SKILL_REFERENCE_STATS) | {NEUTRAL, MONSTER_SKILL_CLASS}
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


def monster_reference(role: str) -> dict:
    """O vetor de referência de um arquétipo, tirado do próprio monstro.

    Medir uma carta de Tanque contra o Guerreiro seria mentir duas vezes: o
    Tanque tem Defesa 101 onde o Guerreiro tem 144, e Agilidade 17 onde o
    Ladino tem 92. A carta pareceria fraca ou absurda por um detalhe da
    planilha, e não pelo que ela faz.

    O número é DERIVADO — nasce de `spawn_by_role` no nível de referência — em
    vez de copiado para uma tabela. Uma cópia congelada seria uma segunda fonte
    de verdade sobre os atributos do monstro, e ela envelheceria em silêncio no
    primeiro ajuste de orçamento de arquétipo.

    O import é local porque `archetypes` importa este módulo pela via do
    carregador de skills; resolver no uso evita o ciclo sem esconder nada.
    """
    from src.content.factories.archetypes import spawn_by_role

    m = spawn_by_role(role, MONSTER_REFERENCE_LEVEL)
    ref = {stat: int(m.get_stat(stat)) for stat in SKILL_SCALING_STATS}
    ref["avg"] = int(m.get_avg_damage())
    return ref


def _referencia(skill_class: str) -> dict:
    return (
        SKILL_REFERENCE_NEUTRAL
        if skill_class == NEUTRAL
        else SKILL_REFERENCE_STATS.get(skill_class, SKILL_REFERENCE_NEUTRAL)
    )


def offensive_budget(skill, com_bonus: bool = True, reference: dict | None = None) -> int:
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

    `reference` troca a régua sem trocar a LEI. É por aqui que uma carta de
    monstro é medida contra o arquétipo dela em vez de contra uma classe de
    herói — mesma conta, personagem de referência diferente.
    """
    escala = getattr(skill, "scaling", ())
    if skill.effect_type != "damage" or not escala:
        return 0
    ref = reference or _referencia(skill.skill_class)
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


def _custo_percentual(skill, ref: dict) -> float:
    """Quanto a carta cobra em % da mana máxima de quem a lança.

    A carta do herói declara isso; a do monstro traz só o custo absoluto. Como
    o crédito de orçamento é sobre o que se PAGA, e o que se paga é a fração da
    barra, o absoluto é convertido contra a mana da referência. Sem isso toda
    carta de monstro entraria com crédito de mana zero e pareceria mais cara do
    que é — o validador puniria o monstro por um detalhe de formato.
    """
    declarado = float(getattr(skill, "mana_cost_percent", 0) or 0)
    if declarado:
        return declarado
    return float(getattr(skill, "mana_cost", 0) or 0) / max(1, ref.get("mp", 1)) * 100


def budget_credit(skill, reference: dict | None = None) -> int:
    """Créditos por custo assumido, com TETO.

    Cooldown enorme e requisito de equipamento devolvem orçamento, mas nunca o
    suficiente para justificar uma carta absurda: `CREDITO_MAX` é o que impede
    "cooldown 99" de virar licença para tudo.
    """
    ref = reference or _referencia(skill.skill_class)
    credito = max(0, int(skill.cooldown) - 1) * CREDITO_POR_TURNO_DE_RECARGA
    credito += int(_custo_percentual(skill, ref) * CREDITO_POR_PONTO_DE_MANA)
    if getattr(skill, "requires", None) is not None:
        credito += CREDITO_POR_REQUISITO
    if getattr(skill, "accuracy_modifier", 0) < 0:
        credito += abs(skill.accuracy_modifier) * CUSTO_POR_PONTO_DE_ACERTO
    return min(CREDITO_MAX, credito)


def validate(skill, reference: dict | None = None) -> Veredito:
    """Valida uma carta contra todas as leis. Devolve o veredito com motivos.

    UMA entrada de validação para o jogo inteiro. Herói e monstro obedecem às
    MESMAS leis estruturais — escala válida, no máximo dois atributos somando
    1.0, MP e recarga obrigatórios, acerto dentro da faixa, efeito do catálogo
    global, orçamento não absurdo.

    `reference` é a única coisa que muda entre eles, e muda porque tem de mudar:
    obrigar uma carta de Tanque a ser medida contra o Guerreiro não é tratá-los
    igual, é fingir que têm os mesmos atributos. A lei é a mesma; a régua é a do
    personagem que vai usar a carta.
    """
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
    ref = reference or _referencia(skill.skill_class)
    v.orcamento = (
        offensive_budget(skill, reference=ref)
        + effect_budget(skill)
        - budget_credit(skill, reference=ref)
    )
    v.teto = MAX_OFFENSIVE_BUDGET_NEUTRAL if skill.skill_class == NEUTRAL else MAX_OFFENSIVE_BUDGET
    if v.orcamento > v.teto:
        erro(f"offensive budget {v.orcamento} > permitted {v.teto}")
    return v


# --- identidade de uma carta de dano ----------------------------------------
#
# Uma carta de dano sem NENHUM traço próprio é um ataque básico mais caro: a
# escolha entre ela e as outras vira aritmética fixa, e o deck deixa de precisar
# ser lido. A regra existe para impedir isso.
#
# Por um tempo ela exigiu especificamente uma CONDIÇÃO SITUACIONAL, e depois
# passou a aceitar condição, efeito secundário, mira ou requisito — mas seguia
# ignorando de onde o golpe NASCE. Um Guerreiro que transforma Defesa em dano é
# uma ideia inteira, mesmo sem mais nada: a carta não parece com nenhuma outra
# da classe e monta uma build diferente.
#
# O que NÃO pode contar é o trivial. Toda skill V2 tem `scaling`, então aceitar
# qualquer escala destruiria a proteção — e preço também não serve: duas cartas
# de 100% Força que só diferem em mana e recarga continuam sendo uma ideia só.


def primary_stat(skill_class: str) -> frozenset[str]:
    """O atributo de onde o dano daquela classe nasce por padrão.

    Não é uma tabela nova: sai de `CLASS_WEIGHTS`, que já define a identidade
    ofensiva de cada classe e é o que o ataque básico usa. Se um dia o Guerreiro
    deixar de ser uma classe de Força, esta regra acompanha sozinha.

    - Monster devolve `{st, mg}` porque o ataque básico do monstro é
      literalmente `(st + mg) / 2`: escalar em qualquer um dos dois é escalar no
      ataque básico dele.
    - Neutral devolve vazio: o pool universal não tem atributo natural, e é por
      isso que `df` ou `hp` ali já são uma escolha de design, não o caminho óbvio.
    """
    if skill_class == MONSTER_SKILL_CLASS:
        return frozenset({"st", "mg"})
    pesos = CLASS_WEIGHTS.get(skill_class)
    if not pesos:
        return frozenset()
    maior = max(pesos.values())
    return frozenset(nome for nome, peso in pesos.items() if peso == maior)


def scaling_is_distinctive(skill) -> bool:
    """A escala desta carta é uma ideia, ou o caminho óbvio da classe?

    É ideia quando:
      - mistura dois atributos (o híbrido é sempre uma escolha), ou
      - nasce de um atributo que NÃO é o primário da classe.

    `Guerreiro 100% Força` é o caminho óbvio e não conta sozinho.
    `Guerreiro 100% Defesa` e `Guerreiro 70% Força + 30% Defesa` contam.
    """
    escala = getattr(skill, "scaling", ())
    if not escala:
        return False
    if len(escala) > 1:
        return True
    return escala[0].stat not in primary_stat(skill.skill_class)


def damage_identity(skill) -> list[str]:
    """Os traços que fazem esta carta de dano ser ela mesma. Vazio = genérica."""
    marcas = []
    if getattr(skill, "bonus_condition", "") and getattr(skill, "bonus_percent", 0):
        marcas.append("condição situacional")
    if getattr(skill, "secondary", None):
        marcas.append("efeito secundário")
    if getattr(skill, "accuracy_modifier", 0):
        marcas.append("mira própria")
    if getattr(skill, "requires", None):
        marcas.append("requisito de equipamento")
    if scaling_is_distinctive(skill):
        marcas.append("escala distintiva")
    return marcas


# --- similaridade conceitual ------------------------------------------------
#
# 204 cartas não podem ser 40 ideias e 164 renomes. O que define uma carta é o
# que ela DECIDE: de quem é, o que faz, de qual atributo nasce, o que aplica, o
# que exige e quando rende mais. Duas cartas com essa mesma assinatura oferecem
# a mesma decisão ao jogador — são a mesma carta com dois nomes, e a segunda
# gasta um dos três espaços do menu com nada.
#
# Número NÃO entra na assinatura. "A mesma carta com o valor maior" é
# exatamente o caso que esta regra existe para recusar: o catálogo já teve três
# buffs de Agilidade do Ladino que só diferiam em 30, 45 e 50.


def skill_signature(skill, role: str = "") -> tuple:
    """A identidade conceitual de uma carta.

    `role` existe porque toda carta de monstro carrega `skill_class="Monster"`:
    sem ele, o Torpor do Controlador e o Esmagar do Chefe pareceriam a mesma
    carta, quando a diferença entre os arquétipos é justamente o que o jogador
    precisa aprender a ler.
    """
    escala = tuple(sorted((t.stat, round(t.weight, 2)) for t in skill.scaling))
    req = skill.requires
    chave_req = ()
    if req is not None:
        chave_req = tuple(
            sorted(
                (k, v)
                for k, v in (
                    ("hand_type", req.hand_type),
                    ("hands", req.hands),
                    ("two_weapons", req.two_weapons),
                )
                if v
            )
        )
    return (
        role or skill.skill_class,
        skill.effect_type,
        escala,
        # Só o `effect_value` que é um NOME conta: em `status` ele é o efeito
        # aplicado, e `poison` e `frozen` são decisões diferentes. Em buff, cura
        # e mitigação ele é um número, e número não distingue carta.
        str(skill.effect_value) if skill.effect_type == "status" else "",
        skill.effect_stat,
        skill.secondary.effect if skill.secondary else "",
        skill.bonus_condition,
        chave_req,
    )


def find_clones(cartas) -> list[list[str]]:
    """Grupos de cartas que oferecem a mesma decisão. Aceita `(papel, carta)`."""
    grupos: dict[tuple, list[str]] = {}
    for entrada in cartas:
        papel, carta = entrada if isinstance(entrada, tuple) else ("", entrada)
        grupos.setdefault(skill_signature(carta, papel), []).append(carta.id)
    return [ids for ids in grupos.values() if len(ids) > 1]


def validate_all(skills, reference: dict | None = None) -> list[Veredito]:
    """Valida um catálogo inteiro. Devolve só os vereditos, sem levantar."""
    return [validate(s, reference=reference) for s in skills]


def validate_monster_catalog() -> list[Veredito]:
    """Valida as cartas de TODOS os arquétipos, cada uma contra o papel dela.

    A carta de monstro não diz a que arquétipo pertence — quem sabe disso é o
    arquétipo, que a carrega. Por isso a varredura começa neles, e não na lista
    de cartas.
    """
    from src.content.factories.archetypes import all_archetypes

    vereditos = []
    for role, arquetipo in sorted(all_archetypes().items()):
        if not arquetipo.skills:
            continue
        ref = monster_reference(role)
        vereditos += [validate(s, reference=ref) for s in arquetipo.skills]
    return vereditos


def assert_catalogo_valido(skills, reference: dict | None = None) -> None:
    """Levanta com o relatório completo se alguma carta for inválida."""
    reprovadas = [v for v in validate_all(skills, reference=reference) if not v.ok]
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
    "damage_identity",
    "effect_budget",
    "find_clones",
    "monster_reference",
    "offensive_budget",
    "primary_stat",
    "scaling_is_distinctive",
    "skill_signature",
    "validate",
    "validate_all",
    "validate_monster_catalog",
]
