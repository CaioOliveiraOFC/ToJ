"""Interações: as leis que ligam um efeito ao outro.

Um efeito é uma PEÇA. Uma interação é uma LEI sobre duas peças, e a lei pertence
ao jogo — não à carta que colocou a peça no tabuleiro.

É a diferença que este módulo existe para manter. "A skill X quebra o gelo" seria
uma regra da skill X: cada carta nova precisaria reimplementá-la, o monstro nunca
a teria, e o jogador aprenderia trinta casos especiais em vez de uma lei. Aqui a
regra é: *alvo congelado + golpe crítico = Quebra Gélida*. Quem congelou, com o
quê, e quem está batendo, não entra na pergunta.

Disso decorre tudo o mais. A FONTE não importa: skill, passiva, item,
encantamento ou monstro colocam a mesma peça e destravam a mesma lei. O ATOR não
importa: herói e monstro leem este mesmo arquivo, e não existe `hero_shatter` ao
lado de `monster_shatter`.

    peça entra (efeito aplicado)      golpe sendo resolvido
            ↓                                 ↓
      resolver interações              resolver interações
            ↓                                 ↓
    stack / duração / estado            DamageModifiers

Vive em `shared/` pelo mesmo motivo que `effect_core`: `mechanics/` precisa
resolver o golpe e o núcleo precisa resolver o turno, e `shared/` é a camada que
as duas enxergam. Importa `effect_core` — a lei é construída sobre a peça —, e o
núcleo NÃO importa daqui: ele recebe a lei de quem o chama.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.shared import effect_core as core

# --- como uma lei é resolvida ---------------------------------------------
# STRIKE: entra no funil do golpe, como fator do bucket ×MULT.
# APPLY: muda a peça que está entrando — stack, duração.
# TICK: muda o que um efeito faz a cada turno.
# CORE: já resolvida pelo núcleo de efeitos; declarada aqui para que a pergunta
#   "quais interações existem no jogo?" tenha UMA resposta, e não duas listas.
KIND_STRIKE = "strike"
KIND_APPLY = "apply"
KIND_TICK = "tick"
KIND_CORE = "core"


@dataclass(frozen=True)
class Interaction:
    """Uma lei global. Declarada aqui, e em nenhum outro lugar."""

    id: str
    label: str
    kind: str
    trigger: str
    effect: str
    # Onde a lei já mora, quando ela é anterior a este módulo. Uma interação
    # `CORE` não é reimplementada aqui: este campo diz onde ela acontece, para
    # que ninguém a duplique achando que faltava.
    resolved_by: str = ""


# Quanto cada lei de golpe vale no bucket ×MULT. Fator, e nunca uma multiplicação
# depois do funil: `_calculate_damage` continua sendo o único lugar onde o dano
# é montado, e o teto de ×MULT continua valendo para estes dois como para o
# crítico.
SHATTER_XMULT = 1.25
AMBUSH_XMULT = 1.20

# Quanto o dreno de Mana Burn cresce contra uma mente turva. Não é dano e não
# entra em funil de dano nenhum: é MP, pela mesma regra de Mana Burn.
MENTAL_COLLAPSE_DRAIN = 1.5

# Quanto uma oportunidade de interação vale para quem está escolhendo a jogada.
# MULTIPLICATIVO de propósito: as métricas de dano e de controle vivem em escalas
# diferentes, e um bônus fixo desequilibraria uma das duas. Sem oportunidade o
# valor não muda em nada — a lei é prioridade ADICIONAL, nunca uma ordem.
OPPORTUNITY_BONUS = 0.5


CATALOG: dict[str, Interaction] = {}


def _lei(*interacoes: Interaction) -> None:
    for i in interacoes:
        CATALOG[i.id] = i


_lei(
    # --- as oito que o motor já resolvia. Reconhecidas, não reimplementadas ---
    Interaction(
        id="empowered_weakened",
        label="Força e Fraqueza",
        kind=KIND_CORE,
        trigger="Fortalecido e Enfraquecido no mesmo alvo",
        effect="Somam no mesmo saldo de Força: +20 e -15 resolvem +5.",
        resolved_by="effect_core.OPPOSING_PAIRS + attribute_percent",
    ),
    Interaction(
        id="arcane_surge_hexed",
        label="Surto e Maldição",
        kind=KIND_CORE,
        trigger="Surto Arcano e Amaldiçoado no mesmo alvo",
        effect="Somam no mesmo saldo de Magia.",
        resolved_by="effect_core.OPPOSING_PAIRS + attribute_percent",
    ),
    Interaction(
        id="quickened_slowed",
        label="Pressa e Peso",
        kind=KIND_CORE,
        trigger="Acelerado e Lentificado no mesmo alvo",
        effect="Somam no mesmo saldo de Agilidade.",
        resolved_by="effect_core.OPPOSING_PAIRS + attribute_percent",
    ),
    Interaction(
        id="fortified_vulnerable",
        label="Guarda e Brecha",
        kind=KIND_CORE,
        trigger="Fortificado e Vulnerável no mesmo alvo",
        effect="Somam no mesmo saldo de Defesa.",
        resolved_by="effect_core.OPPOSING_PAIRS + attribute_percent",
    ),
    Interaction(
        id="vitality_frailty",
        label="Vigor e Fragilidade",
        kind=KIND_CORE,
        trigger="Vitalidade e Fragilidade no mesmo alvo",
        effect="Somam no mesmo teto de HP.",
        resolved_by="effect_core.OPPOSING_PAIRS + resource_percent",
    ),
    Interaction(
        id="focused_clouded",
        label="Foco e Névoa",
        kind=KIND_CORE,
        trigger="Concentrado e Mente Turva no mesmo alvo",
        effect="Somam no mesmo teto de MP.",
        resolved_by="effect_core.OPPOSING_PAIRS + resource_percent",
    ),
    Interaction(
        id="precision_fear",
        label="Mira e Medo",
        kind=KIND_CORE,
        trigger="Preciso e Amedrontado na mesma entidade",
        effect="Disputam a MESMA chance de acerto, numa soma só.",
        resolved_by="effect_core.accuracy_shift",
    ),
    Interaction(
        id="sleep_damage",
        label="Sono e Dor",
        kind=KIND_CORE,
        trigger="Adormecido levando dano",
        effect="O dano acorda o alvo.",
        resolved_by="effect_core.break_on_damage (breaks_on_damage no catálogo)",
    ),
    # --- as oito novas -----------------------------------------------------
    Interaction(
        id="quebra_gelida",
        label="QUEBRA GÉLIDA",
        kind=KIND_STRIKE,
        trigger="Alvo Congelado + golpe crítico que acerta",
        effect=f"×{SHATTER_XMULT} no bucket ×MULT, e o Congelado sai depois do golpe.",
    ),
    Interaction(
        id="emboscada",
        label="EMBOSCADA",
        kind=KIND_STRIKE,
        trigger="Atacante Invisível + ação ofensiva",
        effect=f"×{AMBUSH_XMULT} no bucket ×MULT. A invisibilidade sai na tentativa, "
        "acertando ou errando.",
    ),
    Interaction(
        id="ferida_aberta",
        label="FERIDA ABERTA",
        kind=KIND_APPLY,
        trigger="Sangramento entrando num alvo Vulnerável",
        effect="Um stack a mais de Sangramento, respeitando o teto do catálogo.",
    ),
    Interaction(
        id="toxicidade",
        label="TOXICIDADE",
        kind=KIND_APPLY,
        trigger="Veneno entrando num alvo Frágil",
        effect="Um turno a mais de duração. Intensidade e stacks não mudam.",
    ),
    Interaction(
        id="panico",
        label="PÂNICO",
        kind=KIND_APPLY,
        trigger="Medo entrando num alvo que já sangra",
        effect="Um turno a mais de Medo. A penalidade de acerto é a mesma.",
    ),
    Interaction(
        id="hemorragia_fria",
        label="HEMORRAGIA FRIA",
        kind=KIND_STRIKE,
        trigger="Quebra Gélida num alvo que já sangra",
        effect="Um stack a mais de Sangramento, respeitando o teto.",
    ),
    Interaction(
        id="ferida_septica",
        label="FERIDA SÉPTICA",
        kind=KIND_APPLY,
        trigger="Sangramento e Veneno coexistindo, e um deles sendo reaplicado",
        effect="A aplicação de um renova a duração do outro. Nenhum stack extra.",
    ),
    Interaction(
        id="colapso_mental",
        label="COLAPSO MENTAL",
        kind=KIND_TICK,
        trigger="Queima de Mana drenando um alvo de Mente Turva",
        effect=f"O dreno de MP vale ×{MENTAL_COLLAPSE_DRAIN}. Não é dano e não entra no funil.",
    ),
)


def all_interactions() -> tuple[Interaction, ...]:
    """Todas as leis do jogo, na ordem em que foram declaradas."""
    return tuple(CATALOG.values())


def label(interaction_id: str) -> str:
    lei = CATALOG.get(interaction_id)
    return lei.label if lei else interaction_id


# --- leis de golpe ---------------------------------------------------------


def strike_interactions(attacker, defender, *, is_critical: bool) -> tuple[str, ...]:
    """Quais leis de golpe disparam NESTE golpe. Leitura pura, sem mutação.

    Pura porque `damage_modifiers` é chamado também para ESTIMAR dano — pela
    política do bot e pelos testes — e uma estimativa não pode gastar o gelo
    nem a invisibilidade de ninguém. Quem consome é `consume_strike`, depois
    que o golpe aconteceu de verdade.
    """
    disparadas = []
    if core.has_effect(attacker, "invisible"):
        disparadas.append("emboscada")
    if is_critical and core.has_effect(defender, "frozen"):
        disparadas.append("quebra_gelida")
    return tuple(disparadas)


def strike_xmult(triggered) -> list[float]:
    """Os fatores de ×MULT das leis que dispararam. Entram no funil, e só nele."""
    fatores = {"quebra_gelida": SHATTER_XMULT, "emboscada": AMBUSH_XMULT}
    return [fatores[i] for i in triggered if i in fatores]


def consume_strike(attacker, defender, triggered) -> tuple[str, ...]:
    """Cobra o preço das leis de golpe, DEPOIS do dano. Devolve o que aconteceu.

    Quebra Gélida é uma TROCA: o golpe vale mais e o controle acaba. Emboscada é
    outra: o golpe vale mais e a posição foi revelada.
    """
    aconteceram = list(triggered)
    if "emboscada" in triggered:
        core.remove_effect(attacker, "invisible")
    if "quebra_gelida" in triggered:
        core.remove_effect(defender, "frozen")
        # Hemorragia Fria: o gelo estilhaçado abre o que já sangrava. Depende de
        # Quebra Gélida ter acontecido, então mora aqui e não em `strike_interactions`.
        if _add_stack(defender, "bleed"):
            aconteceram.append("hemorragia_fria")
    return tuple(aconteceram)


def reveal_on_attempt(attacker) -> bool:
    """A tentativa ofensiva revela quem estava escondido, mesmo se errar.

    "Atacou, revelou a posição." Sem isto o atacante guardaria a invisibilidade
    até acertar, e a Emboscada deixaria de ser uma escolha de momento.
    """
    return bool(core.remove_effect(attacker, "invisible"))


# --- leis de aplicação -----------------------------------------------------


def duration_before_apply(target, effect_id: str, duration: int) -> tuple[int, tuple[str, ...]]:
    """A duração com que a peça vai entrar, e quais leis a mudaram.

    Muda DURAÇÃO, nunca chance: o efeito precisa passar pela resistência do alvo
    sozinho, como qualquer outro. Uma lei que também aumentasse a chance de
    aplicar seria um segundo sistema de status por fora do núcleo.
    """
    disparadas = []
    if effect_id == "poison" and core.has_effect(target, "frailty"):
        duration += 1
        disparadas.append("toxicidade")
    elif effect_id == "fear" and core.has_effect(target, "bleed"):
        duration += 1
        disparadas.append("panico")
    return duration, tuple(disparadas)


def after_apply(target, effect_id: str) -> tuple[str, ...]:
    """As leis que disparam depois que a peça ENTROU. Devolve o que aconteceu."""
    disparadas = []
    if effect_id == "bleed" and core.has_effect(target, "vulnerable"):
        if _add_stack(target, "bleed"):
            disparadas.append("ferida_aberta")
    # Ferida Séptica: sangue e veneno se alimentam. Renova a duração do OUTRO,
    # sem stack extra — quem governa stack continua sendo o catálogo.
    parceiro = {"bleed": "poison", "poison": "bleed"}.get(effect_id)
    if parceiro and core.has_effect(target, parceiro) and _refresh(target, parceiro):
        disparadas.append("ferida_septica")
    return tuple(disparadas)


# --- leis de turno ---------------------------------------------------------


def drain_scale(entity, effect_id: str) -> tuple[float, tuple[str, ...]]:
    """Quanto o dreno deste turno é multiplicado, e por qual lei.

    O núcleo recebe esta função de quem o chama; ele não importa este módulo.
    Assim a lei continua declarada num lugar só e o núcleo continua sem
    dependência nenhuma.
    """
    if effect_id == "mana_burn" and core.has_effect(entity, "clouded"):
        return MENTAL_COLLAPSE_DRAIN, ("colapso_mental",)
    return 1.0, ()


# --- oportunidade, para quem está escolhendo a jogada ----------------------


def applicable_effects(skill) -> tuple[str, ...]:
    """Os efeitos que ESTA carta consegue colocar no alvo.

    Lido por duck typing, como o resto: uma carta de status carrega o efeito em
    `effect_value`, e qualquer carta pode levar um `secondary`.
    """
    efeitos = []
    if str(getattr(skill, "effect_type", "")) == "status":
        nome = str(getattr(skill, "effect_value", "") or "")
        if core.definition(nome) is not None:
            efeitos.append(nome)
    secundario = getattr(skill, "secondary", None)
    nome = str(getattr(secundario, "effect", "") or "")
    if core.definition(nome) is not None:
        efeitos.append(nome)
    return tuple(efeitos)


def opportunities(caster, target, skill) -> tuple[str, ...]:
    """Quais leis esta carta destrava CONTRA ESTE ALVO, AGORA.

    Nunca por gosto de arquétipo: não existe "o controlador prefere veneno
    porque a Toxicidade existe". Existe "o alvo está Frágil E esta carta aplica
    veneno". Sem o estado no alvo, ou sem a carta conseguindo pôr a outra peça,
    a resposta é vazia — e a escolha do monstro não muda em nada.
    """
    if target is None:
        return ()
    achadas: list[str] = []

    for efeito in applicable_effects(skill):
        _, por_duracao = duration_before_apply(target, efeito, 1)
        achadas.extend(por_duracao)
        if efeito == "bleed" and core.has_effect(target, "vulnerable"):
            achadas.append("ferida_aberta")
        if efeito == "mana_burn" and core.has_effect(target, "clouded"):
            achadas.append("colapso_mental")
        parceiro = {"bleed": "poison", "poison": "bleed"}.get(efeito)
        if parceiro and core.has_effect(target, parceiro):
            achadas.append("ferida_septica")

    if str(getattr(skill, "effect_type", "")) == "damage":
        # O golpe pode critar — a Quebra Gélida é uma chance, não uma certeza, e
        # por isso vale como oportunidade e não como execução garantida.
        if core.has_effect(target, "frozen"):
            achadas.append("quebra_gelida")
        if core.has_effect(caster, "invisible"):
            achadas.append("emboscada")

    return tuple(dict.fromkeys(achadas))


def opportunity_weight(caster, target, skill) -> float:
    """O peso que uma carta ganha por destravar lei. 1.0 quando não destrava nada."""
    return 1.0 + OPPORTUNITY_BONUS * len(opportunities(caster, target, skill))


# --- utilidades internas ---------------------------------------------------


def _add_stack(entity, effect_id: str) -> bool:
    """Um stack a mais, respeitando o teto do catálogo. Devolve se subiu.

    Mexe na instância que já existe, e não reaplica o efeito: reaplicar passaria
    de novo pela regra de empilhamento e renovaria durações que a lei não
    mandou renovar.
    """
    definicao = core.definition(effect_id)
    if definicao is None:
        return False
    for instancia in core.instances(entity):
        if instancia.effect != effect_id:
            continue
        if instancia.stacks >= definicao.max_stacks:
            return False
        instancia.stacks += 1
        return True
    return False


def _refresh(entity, effect_id: str) -> bool:
    """Devolve o efeito à duração padrão do catálogo. Devolve se mudou algo."""
    definicao = core.definition(effect_id)
    if definicao is None:
        return False
    mudou = False
    for instancia in core.instances(entity):
        if instancia.effect == effect_id and instancia.duration < definicao.default_duration:
            instancia.duration = definicao.default_duration
            mudou = True
    return mudou
