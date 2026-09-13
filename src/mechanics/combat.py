"""Regras puras de combate (sem I/O)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from src.shared import combat_topics as T
from src.shared import effect_core as core
from src.shared import effects as fx
from src.shared.constants import (
    BASE_HIT_CHANCE,
    BASIC_ATTACK_POWER_MULT,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_CHANCE_HIGH,
    CRIT_DAMAGE_BASE,
    DAMAGE_REDUCTION_DEFAULT_PERCENT,
    DAMAGE_REDUCTION_DURATION,
    DEFENSE_K,
    FLEE_RANGE_MAX,
    HIT_AGILITY_SWING,
    HIT_CHANCE_CEIL,
    HIT_CHANCE_FLOOR,
    MAGIC_SHIELD_DAMAGE_PER_MP,
    MP_REGEN_PERCENT_PER_TURN,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
    SKILL_BONUS_HEALTHY_RATIO,
    SKILL_BONUS_WOUNDED_RATIO,
    STUN_DURATION,
    XMULT_CAP,
)
from src.shared.types import CombatResult, GameEvent

PublishFn = Callable[[str, GameEvent], None] | None


def _emit(publish: PublishFn, topic: str, *, type_: str, payload: dict[str, Any]) -> None:
    if publish is None:
        return
    publish(topic, GameEvent(type=type_, payload=payload, source="mechanics.combat"))


@dataclass(frozen=True, slots=True)
class SkillApplyResult:
    """Resultado da aplicação mecânica de uma habilidade."""

    kind: Literal["damage", "heal", "status", "buff"]
    mp_spent: int
    strike: CombatResult | None = None
    heal_amount: int = 0
    status_effect: str | None = None
    status_success: bool | None = None
    buff_name: str | None = None


def _rng(rng: random.Random | None) -> random.Random:
    return rng if rng is not None else random


def _defense_modifier(defense_target: int) -> float:
    """DEFENSE_MODIFIER = k / (k + defense_target) — curva hiperbólica."""
    return DEFENSE_K / (DEFENSE_K + max(0, defense_target))


def _apply_xmult_cap(xmult_raw: float) -> float:
    """min(xmult_raw, XMULT_CAP) — teto de multiplicadores puros."""
    return min(xmult_raw, XMULT_CAP)


@dataclass(frozen=True)
class DamageModifiers:
    """Os quatro baldes de um golpe. Um recipiente, não um framework.

    `flat`       soma antes de qualquer percentual, em pontos de dano.
    `mult`       percentuais ADITIVOS entre si: +10% e +20% resolvem ×1,30.
    `xmult`      amplificações MULTIPLICATIVAS: ×1,2 e ×1,5 resolvem ×1,8.
                 É este produto — e só ele — que `XMULT_CAP` limita.
    `mitigation` redutores multiplicativos (medo, redução de dano). Ficam fora
                 do cap de propósito: um cap sobre amplificação só faz sentido
                 sobre termos ≥ 1. Se um redutor entrasse no mesmo produto, o
                 teto passaria a medir o saldo entre ataque e defesa, e um
                 crítico absurdo passaria por baixo dele acompanhado de uma
                 redução forte.

    A defesa não é balde: `k/(k+df)` é função não-linear do atributo já
    resolvido do defensor, e é a única etapa com retorno decrescente por
    construção. Mistura-la aqui esconderia isso e diluiria o cap.
    """

    flat: list[int] = field(default_factory=list)
    mult: list[float] = field(default_factory=list)
    xmult: list[float] = field(default_factory=list)
    mitigation: list[float] = field(default_factory=list)


def damage_modifiers(attacker, defender, *, is_critical: bool) -> DamageModifiers:
    """Reúne tudo o que modifica ESTE golpe, dos dois lados.

    É o ponto único da CAMADA B — o golpe. Entra aqui o que modifica um ataque
    específico: crítico, efeitos de combate, mitigação, e futuramente
    encantamentos. Não entra o que resolve atributo: nível, item base, `+N` e
    gemas são camada A e já chegam resolvidos dentro de `base_power`.

    Enquanto a coleta do golpe estiver em um lugar só, nenhuma fonte volta a
    multiplicar por fora do funil.

    Lê atacante e defensor pelo mesmo caminho (`fx.combat_modifier`), que já
    resolve herói e monstro por duck typing.
    """
    xmult: list[float] = []
    if is_critical:
        xmult.append(CRIT_DAMAGE_BASE + fx.combat_modifier(attacker, "crit_damage") / 100)

    # `+MULT`: percentuais ADITIVOS entre si. O bucket existe desde a
    # centralização da linguagem de poder e nunca tinha dono — este é o
    # primeiro. Pergunta pela MECÂNICA (`damage_percent`), como todo o resto:
    # o funil não sabe que encantamento existe, nem precisa saber.
    mult: list[float] = []
    percentual = fx.combat_modifier(attacker, "damage_percent")
    if percentual:
        mult.append(percentual / 100)

    return DamageModifiers(
        mult=mult,
        xmult=xmult,
        # Status do atacante que reduzem o dano que ele causa (weakened, fear) e
        # do defensor que reduzem o que ele recebe (redução ativa e passiva).
        mitigation=[
            fx.outgoing_damage_multiplier(attacker),
            fx.incoming_damage_multiplier(defender),
        ],
    )


def _calculate_damage(
    base_power: float,
    flat_mods: list[int] | None = None,
    mult_mods: list[float] | None = None,
    xmult_mods: list[float] | None = None,
    defense_target: int = 0,
    mitigation: list[float] | None = None,
) -> int:
    """O funil: todo dano de golpe sai daqui.

        (BASE + ΣFLAT) × (1 + Σ+MULT) × Π×MULT_capado × DEFESA × Π_mitigação

    Amplificação e mitigação são produtos separados porque só o primeiro é
    capado — ver `DamageModifiers`.
    """
    flat_total = sum(flat_mods) if flat_mods else 0
    mult_total = 1.0 + sum(mult_mods) if mult_mods else 1.0

    xmult_raw = 1.0
    if xmult_mods:
        for v in xmult_mods:
            xmult_raw *= v
    xmult_capped = _apply_xmult_cap(xmult_raw)

    def_mod = _defense_modifier(defense_target)

    raw = (base_power + flat_total) * mult_total * xmult_capped * def_mod
    dano = max(1, int(raw))

    # Truncando a cada termo, e não no produto: é o que o motor já fazia quando
    # estas multiplicações eram três linhas soltas aqui fora. Multiplicar tudo
    # de uma vez e truncar no fim mudaria o dano de alguns golpes por 1 ponto.
    for redutor in mitigation or ():
        dano = int(dano * redutor)
    return max(1, dano)


def hit_chance(attacker, defender) -> int:
    """Chance de acerto, a partir da diferença *relativa* de agilidade.

    A fórmula antiga era `85 + AG_atacante - AG_defensor`, sem piso. Como a
    agilidade do Ladino crescia 18% ao nível e a do monstro era a constante 3,
    a chance de o monstro acertar caía a zero por volta do nível 13: a classe
    ficava imune a dano, e nenhum balanceamento de monstro alcançava isso.

    Usando a diferença relativa, a vantagem de quem investe em agilidade é
    grande, permanente e limitada — e continua valendo a mesma coisa no nível 1
    e no nível 20, porque os dois lados escalam juntos.
    """
    att_ag = max(0, attacker.get_ag())
    def_ag = max(0, defender.get_ag())
    total = att_ag + def_ag
    swing = 0.0 if total <= 0 else HIT_AGILITY_SWING * (att_ag - def_ag) / total

    chance = BASE_HIT_CHANCE + swing
    chance -= fx.combat_modifier(defender, "evasion")
    # Medo é do ATACANTE e mexe na confiabilidade do golpe, não na Agilidade
    # dele nem no tamanho do dano. Entra no cálculo de acerto que já existe —
    # uma segunda rolagem paralela é como `Esmagar` acabou atordoando por dois
    # caminhos independentes.
    chance -= core.accuracy_penalty(attacker)
    chance -= core.concealment_penalty(defender)

    return int(max(HIT_CHANCE_FLOOR, min(HIT_CHANCE_CEIL, chance)))


def basic_attack_power(attacker) -> int:
    """BASE_POWER de um ataque básico: uma FRAÇÃO do poder total da entidade.

    Existe para que o ataque básico e a skill não paguem o mesmo número. A
    skill de dano rende `poder * (1 + effect_value/100)`; enquanto o básico
    rendia o `poder` inteiro, de graça e sem recarga, a skill mediana do jogo
    valia 1,65 ataque gratuito — e a linha ótima do jogador era não gastar
    recurso nenhum, ou repetir a mesma skill até o fim do combate.

    Vive aqui, ao lado de `skill_damage_base`, porque a política do simulador
    precisa estimar o dano com a mesma fórmula que o motor aplica.

    Não é modificador e por isso não vira balde de `DamageModifiers`: as duas
    funções respondem "qual é o BASE desta ação", que é a entrada do funil, não
    algo que o modifica. Transformá-las em `+MULT` também mudaria dano — o
    truncamento passaria a acontecer depois, e 23 de 120 combinações de classe e
    nível saíam 1 ponto diferentes.
    """
    return max(1, int(attacker.get_avg_damage() * BASIC_ATTACK_POWER_MULT))


def skill_mana_cost(caster, skill) -> int:
    """Quanto de mana a skill custa para ESTE lançador.

    Delega para a entidade, que é quem conhece o próprio teto de mana. Existe
    como ponta única de leitura para os pontos que antes liam `skill.mana_cost`
    solto — política de escolha, bot de combate, IA do monstro e laço do jogo —,
    porque um custo conferido num lugar e cobrado em outro deixa o herói lançar
    o que não pode pagar.
    """
    metodo = getattr(caster, "skill_mana_cost", None)
    if callable(metodo):
        return int(metodo(skill))
    return int(getattr(skill, "mana_cost", 0) or 0)


def bonus_condition_met(caster, skill, target) -> bool:
    """A condição situacional da skill está satisfeita contra este alvo?

    Sem alvo não há situação para ler, então o bônus não conta — é o caso da
    estimativa feita fora de um combate.
    """
    condicao = str(getattr(skill, "bonus_condition", "") or "")
    if not condicao or target is None:
        return False

    efeitos = getattr(target, "active_effects", {}) or {}
    if condicao == "target_controlled":
        return any(e in fx.TURN_SKIPPING_STATUSES for e in efeitos)
    if condicao == "target_afflicted":
        return bool(efeitos)
    if condicao == "target_wounded":
        return _fracao_de_vida(target) <= SKILL_BONUS_WOUNDED_RATIO
    if condicao == "target_healthy":
        return _fracao_de_vida(target) >= SKILL_BONUS_HEALTHY_RATIO
    if condicao == "caster_wounded":
        return _fracao_de_vida(caster) <= SKILL_BONUS_WOUNDED_RATIO
    # Condição desconhecida nunca dispara. `tests/test_data_integrity.py` recusa
    # uma grafia fora de `BONUS_CONDITIONS` antes que ela chegue até aqui: um
    # bônus que nunca acontece é exatamente o tipo de placebo que passa despercebido.
    return False


def _fracao_de_vida(entidade) -> float:
    teto = int(getattr(entidade, "base_hp", 0) or 0)
    if teto <= 0:
        return 1.0
    return max(0.0, entidade.get_hp() / teto)


def skill_damage_base(caster, skill, target=None) -> int:
    """BASE_POWER total de uma skill de dano, antes de defesa e crítico.

    `effect_value` é um **percentual sobre o poder base**, não uma soma fixa.
    Como soma fixa, a skill anti-escalava: o poder base cresce a cada nível e o
    valor da skill não, então no nível 20 o Apocalipse entregava apenas +30%
    sobre um ataque básico que é gratuito e sem recarga. Como percentual, a
    skill mantém o mesmo peso relativo do nível 1 ao 20.

    Vive aqui, e não na política do simulador, porque o bot precisa estimar o
    dano com a mesma fórmula que o motor aplica. Duas cópias da fórmula divergem
    na primeira mudança de balanceamento.
    """
    base_power = caster.get_avg_damage()
    bonus_percent = int(skill.effect_value)
    if bonus_condition_met(caster, skill, target):
        bonus_percent += int(getattr(skill, "bonus_percent", 0) or 0)
    return max(1, int(base_power * (1 + bonus_percent / 100)))


def resolve_physical_attack(
    attacker,
    defender,
    base_damage: int,
    skill_name: str = "",
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> CombatResult:
    """
    Resolve um golpe físico: acerto, crítico, pipeline de dano e aplica `take_damage`.
    `base_damage` é o BASE_POWER (vindo de get_avg_damage() com pesos de classe).
    """
    r = _rng(rng)

    if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) > hit_chance(attacker, defender):
        miss = CombatResult(
            attacker_id=attacker.get_nick_name(),
            defender_id=defender.get_nick_name(),
            damage=0,
            was_critical=False,
            was_evaded=True,
            did_defender_die=False,
            notes=("miss",),
        )
        _emit(
            publish,
            T.COMBAT_PHYSICAL_STRIKE,
            type_="physical_strike",
            payload={"attacker": attacker, "defender": defender, "strike": miss},
        )
        return miss

    crit_chance = (
        CRIT_CHANCE_HIGH
        if hasattr(attacker, "get_classname")
        and attacker.get_classname() == "Rogue"
        and skill_name == "Ataque Furtivo"
        else CRIT_CHANCE_DEFAULT
    )
    crit_chance += int(fx.combat_modifier(attacker, "crit_chance"))
    crit_chance = min(crit_chance, CRIT_CHANCE_CAP)

    is_critical = r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) <= crit_chance

    mods = damage_modifiers(attacker, defender, is_critical=is_critical)
    damage = _calculate_damage(
        base_power=float(base_damage),
        flat_mods=mods.flat,
        mult_mods=mods.mult,
        xmult_mods=mods.xmult,
        defense_target=defender.get_df(),
        mitigation=mods.mitigation,
    )

    # A Égide fica fora do funil de propósito: não é modificador, é STATE. Ela
    # consome mana do defensor, e o quanto ela absorve depende do saldo — uma
    # subtração com custo, não um fator.
    damage = _absorve_com_egide(defender, damage, publish)

    # Stun da PASSIVA do atacante. O stun que a skill carrega é rolado por
    # `apply_skill`, a partir do `stun_chance` do JSON.
    #
    # Aqui havia um caso especial: se o nome da skill fosse "Esmagar", esta
    # rolagem usava uma constante do motor em vez da passiva. Como `apply_skill`
    # também rola o `stun_chance` da skill, Esmagar atordoava por dois caminhos
    # independentes — o JSON declarava 30% e o jogo entregava 46% —, e a passiva
    # de atordoamento do herói era silenciosamente descartada em todo golpe de
    # Esmagar, que é justamente onde ela deveria valer mais.
    _aplicar_procs_on_hit(attacker, defender, r, publish)

    defender.take_damage(damage)
    fx.wake_on_damage(defender)

    # Roubo de vida: devolve ao atacante um percentual do dano causado.
    life_steal = fx.combat_modifier(attacker, "life_steal")
    if life_steal > 0:
        attacker.heal(max(1, int(damage * life_steal / 100)))

    dead = defender.get_hp() <= 0
    if dead and _survive_lethal_blow(defender):
        dead = False
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": defender, "kind": "death_ignored"},
        )
    if dead:
        defender.set_isalive(False)

    strike = CombatResult(
        attacker_id=attacker.get_nick_name(),
        defender_id=defender.get_nick_name(),
        damage=int(damage),
        was_critical=bool(is_critical),
        was_evaded=False,
        did_defender_die=bool(dead),
        notes=("hit",),
    )
    _emit(
        publish,
        T.COMBAT_PHYSICAL_STRIKE,
        type_="physical_strike",
        payload={"attacker": attacker, "defender": defender, "strike": strike},
    )
    return strike


def try_apply_status(
    target,
    status: str,
    base_chance: float,
    duration: int,
    r: random.Random,
    publish: PublishFn = None,
    *,
    applied_kind: str | None = None,
    source_id: str = "",
) -> bool:
    """Tenta aplicar um status negativo. Devolve se pegou.

    O único caminho de aplicação de status vindo de um ataque. Responde, nesta
    ordem: qual era a chance base, quanto o alvo resiste, qual a chance efetiva,
    rolou, aplica ou não.

    Dano e status são resolvidos em separado de propósito. Um golpe pode tirar a
    vida inteira e mesmo assim não congelar; um alvo com 100% de resistência a
    `frozen` leva o dano normalmente. Por isso resistência a status não entra em
    `DamageModifiers.mitigation` — são sistemas vizinhos, não o mesmo sistema.

    Chance efetiva zero não consome rolagem, que é o que `_try_apply_stun` já
    fazia quando a chance era zero. Sem consumir, a imunidade também não desloca
    o RNG do resto do turno.
    """
    if not hasattr(target, "active_effects"):
        return False
    chance = fx.effective_status_chance(base_chance, fx.status_resistance(target, status))
    if chance <= 0:
        if base_chance > 0:
            _emit(
                publish,
                T.COMBAT_TURN_EFFECT,
                type_="turn_effect",
                payload={"entity": target, "kind": "status_resisted", "status": status},
            )
        return False
    if r.randrange(PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX) > chance:
        return False
    # Passou a rolagem. O NÚCLEO decide o resto: se empilha, se renova, qual o
    # teto de stacks, quanto dura. O combate não conhece nenhuma dessas regras.
    if core.apply_effect(target, status, source_id=source_id, duration=duration) is None:
        return False
    if applied_kind:
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": target, "kind": applied_kind},
        )
    return True


def _fonte_da_skill(skill) -> str:
    """A identidade de uma skill como FONTE de efeito.

    A carta, não quem a lança: a regra é que a mesma skill reaplicada renove a
    contribuição dela em vez de empilhar. Duas cartas diferentes que aplicam
    `weakened` são duas fontes e somam; a mesma carta lançada quatro vezes
    continua valendo uma.
    """
    return str(getattr(skill, "id", None) or getattr(skill, "name", "") or "skill")


def _try_apply_stun(
    target, chance: int, r: random.Random, publish: PublishFn, source_id: str = "skill"
) -> bool:
    """Rola atordoamento pelo resolvedor central. Devolve se atordoou.

    Existe para que os três caminhos que atordoam — passiva do atacante, skill de
    dano e skill de status — usem a mesma rolagem e a mesma duração. Enquanto o
    código estava duplicado, o ramo de status simplesmente não tinha a sua cópia:
    `Golpe Baixo` declara 15% de atordoamento no JSON e entregava 0%.
    """
    if not chance:
        return False
    return try_apply_status(
        target,
        "stun",
        int(chance),
        STUN_DURATION,
        r,
        publish,
        applied_kind="stun_applied",
        source_id=source_id,
    )


# Efeito que o atacante pode aplicar ao acertar, e o modificador que carrega a
# chance. Uma tabela, e não quatro blocos de `if`: a quinta família entra aqui
# como uma linha, e a mecânica de cada uma já é do núcleo.
ONHIT_PROCS = {
    "stun": "stun_chance",
    "bleed": "bleed_chance",
    "poison": "poison_chance",
    "fear": "fear_chance",
}


def _aplicar_procs_on_hit(attacker, defender, r: random.Random, publish: PublishFn) -> None:
    """Rola os efeitos que o atacante aplica ao acertar.

    A chance vem de `combat_modifier`, então equipamento, encantamento, passiva
    e buff chegam pelo mesmo caminho — e o alvo resiste pela mesma regra, porque
    quem aplica é `try_apply_status`, que é a única porta de entrada de status.

    O combate não sabe quanto dura um sangramento nem quantos stacks ele aceita.
    Isso é do catálogo.
    """
    for effect_id, modificador in ONHIT_PROCS.items():
        chance = int(fx.combat_modifier(attacker, modificador))
        if chance <= 0:
            continue
        definicao = core.definition(effect_id)
        try_apply_status(
            defender,
            effect_id,
            chance,
            definicao.default_duration if definicao else 1,
            r,
            publish,
            applied_kind=f"{effect_id}_applied",
            source_id=getattr(attacker, "nick_name", "atacante"),
        )


def _absorve_com_egide(defender, damage: int, publish: PublishFn) -> int:
    """Égide de Mana: troca mana por dano evitado. Devolve o dano que passa.

    O nome distingue esta mitigação passiva da skill `Barreira Arcana`, que é
    outra coisa: um buff de defesa que o Mago escolhe lançar. As duas reduzem
    dano e ambas são do Mago, então dividir o nome garantiria confusão assim que
    a mecânica ganhasse voz na tela — que é o que acabou de acontecer.

    Existe porque cada classe precisa de uma forma de não morrer, e o Mago não
    tinha nenhuma: mesma vida efetiva do Ladino, sem a esquiva que a compensa, e
    +5% de dano sobre o Guerreiro para pagar por 20% menos vida. A reserva de
    mana era a compensação escrita, mas só rendia em luta longa — e ele morria
    no andar 4, contra os encontros mais comuns do jogo.

    Absorver custa MP, então a decisão não é de graça: o que a barreira gasta
    aguentando é skill que não será lançada. É essa tensão que faz a reserva
    pesar, em vez de ser um número grande parado na ficha.
    """
    fracao = int(getattr(defender, "magic_shield_percent", 0) or 0)
    if fracao <= 0 or damage <= 1:
        return damage

    mana = int(getattr(defender, "get_mp", lambda: 0)())
    if mana <= 0:
        return damage

    desejado = int(damage * fracao / 100)
    # O que a mana em caixa realmente cobre: sem isso, um Mago seco continuaria
    # absorvendo e a barreira viraria redução de dano gratuita.
    possivel = min(desejado, int(mana * MAGIC_SHIELD_DAMAGE_PER_MP))
    if possivel <= 0:
        return damage

    custo = max(1, int(possivel / MAGIC_SHIELD_DAMAGE_PER_MP))
    defender.reduce_mp(custo)
    _emit(
        publish,
        T.COMBAT_TURN_EFFECT,
        type_="turn_effect",
        payload={"entity": defender, "kind": "magic_shield", "absorbed": possivel, "mp": custo},
    )
    return max(1, damage - possivel)


def _survive_lethal_blow(entity) -> bool:
    """`death_ignore`: sobrevive com 1 de HP a um golpe letal, uma vez por combate.

    Uma vez por combate, e não uma vez por run, porque um efeito que ressuscita
    para sempre transforma qualquer encontro perdido em encontro vencido e apaga
    a decisão de fugir.

    Pergunta pela MECÂNICA, não pela fonte: antes lia `get_passive_bonus` direto,
    então o Amuleto da Imortalidade era decoração e só a passiva valia. Agora
    passiva, buff e equipamento chegam pela mesma porta.

    O teste é `> 0`, e não uma soma de vidas: dois amuletos não dão duas
    ressurreições. É um estado binário por combate, guardado em
    `_death_ignore_used` — e é isso que impede o efeito de virar uma pilha.
    """
    if fx.combat_modifier(entity, "death_ignore") <= 0:
        return False
    if getattr(entity, "_death_ignore_used", False):
        return False
    entity._death_ignore_used = True
    entity._hp = 1
    return True


def apply_skill(
    caster,
    target,
    skill: Any,
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> SkillApplyResult:
    """Aplica efeitos de habilidade no estado (sem prints)."""
    r = _rng(rng)

    # Cooldown: verifica se skill está em recarga
    skill_id = getattr(skill, "id", None)
    skill_cooldown = int(getattr(skill, "cooldown", 0) or 0)
    if skill_id and hasattr(caster, "skill_cooldowns"):
        remaining = caster.skill_cooldowns.get(skill_id, 0)
        if remaining > 0:
            # Em cooldown — não consome MP nem aplica efeito
            out = SkillApplyResult(kind="damage", mp_spent=0, strike=None)
            _emit(
                publish,
                T.COMBAT_SKILL_CAST,
                type_="skill_cast",
                payload={"caster": caster, "skill": skill, "on_cooldown": True},
            )
            return out

    _emit(
        publish,
        T.COMBAT_SKILL_CAST,
        type_="skill_cast",
        payload={"caster": caster, "skill": skill},
    )
    custo = skill_mana_cost(caster, skill)
    caster.reduce_mp(custo)

    # Aplica cooldown após uso bem-sucedido (se houver).
    #
    # `+ 1` porque a recarga é gravada no turno do uso e decrementada no início
    # do turno SEGUINTE do mesmo ator, antes de ele agir. Sem o ajuste,
    # `cooldown: 1` virava zero e sumia antes da primeira chance de reusar — ou
    # seja, quatro skills do JSON declaravam uma recarga que não existia. Com
    # ele, `cooldown: N` bloqueia exatamente N turnos do ator.
    if skill_id and hasattr(caster, "skill_cooldowns") and skill_cooldown > 0:
        caster.skill_cooldowns[skill_id] = skill_cooldown + 1

    if skill.effect_type == "damage":
        total_base = skill_damage_base(caster, skill, target)
        strike = resolve_physical_attack(
            caster, target, total_base, str(skill.name), rng=r, publish=None
        )
        # Stun que a skill carrega. Só rola se o golpe conectou: um ataque
        # esquivado não atordoa.
        if strike and not strike.was_evaded:
            _try_apply_stun(
                target,
                int(getattr(skill, "stun_chance", 0) or 0),
                r,
                publish,
                _fonte_da_skill(skill),
            )
        out = SkillApplyResult(kind="damage", mp_spent=custo, strike=strike)
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "heal":
        # Percentual do HP máximo, não valor fixo: uma cura de 50 pontos era
        # irrelevante para um herói com milhares de HP no fim do jogo.
        max_hp = int(getattr(caster, "base_hp", caster.get_hp()))
        heal_amount = max(1, int(max_hp * int(skill.effect_value) / 100))
        heal_amount += int(heal_amount * fx.combat_modifier(caster, "potion_heal_bonus") / 100)
        caster.heal(heal_amount)
        out = SkillApplyResult(kind="heal", mp_spent=custo, heal_amount=heal_amount)
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "status":
        if try_apply_status(
            target,
            str(skill.effect_value),
            int(skill.chance),
            int(skill.duration),
            r,
            publish,
            source_id=_fonte_da_skill(skill),
        ):
            # O atordoamento da skill também vale aqui. Este ramo não o rolava:
            # o bloco existia só na versão de dano, então `Golpe Baixo` aplicava
            # `weakened` em 100% das vezes e nunca os seus 15% de atordoamento.
            # Só rola quando o status pegou — uma skill que falhou não atordoa.
            _try_apply_stun(
                target,
                int(getattr(skill, "stun_chance", 0) or 0),
                r,
                publish,
                _fonte_da_skill(skill),
            )
            out = SkillApplyResult(
                kind="status",
                mp_spent=custo,
                status_effect=str(skill.effect_value),
                status_success=True,
            )
        else:
            out = SkillApplyResult(
                kind="status",
                mp_spent=custo,
                status_effect=str(skill.effect_value),
                status_success=False,
            )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "buff":
        # O buff declara qual atributo modifica. Sem isso, o motor precisava
        # reconhecer o buff pelo nome, e todo nome fora da lista era um no-op.
        recipient = caster if getattr(skill, "target", "self") == "self" else target
        stat = str(getattr(skill, "effect_stat", "") or "")
        recipient.active_buffs[str(skill.name)] = {
            "stat": stat,
            "value": fx.buff_value(recipient, stat, int(skill.effect_value)),
            "duration": int(skill.duration),
        }
        out = SkillApplyResult(
            kind="buff",
            mp_spent=custo,
            buff_name=str(skill.name),
        )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": target, "result": out},
        )
        return out

    if skill.effect_type == "damage_reduction":
        # O MESMO caminho do buff do herói. Antes esta era a única mecânica com
        # representação exclusiva de monstro: um dicionário solto em
        # `active_effects`, fora do ciclo de buff, lido por uma exceção em
        # `incoming_damage_multiplier` e por outra na IA. Três lugares sabiam de
        # um formato que só o monstro usava.
        #
        # `damage_reduction` não é status: não se resiste a ele, não empilha por
        # stack, e quem o lança põe em si mesmo. É modificador de combate, e o
        # canal de modificador de combate é `active_buffs`, com a fonte na chave.
        value = (
            int(skill.effect_value)
            if isinstance(skill.effect_value, int)
            else DAMAGE_REDUCTION_DEFAULT_PERCENT
        )
        duration = int(skill.duration) if skill.duration else DAMAGE_REDUCTION_DURATION
        recipient = caster if getattr(skill, "target", "self") == "self" else target
        recipient.active_buffs[str(skill.name)] = {
            "stat": "damage_reduction",
            "value": value,
            "duration": duration,
        }
        out = SkillApplyResult(
            kind="buff",
            mp_spent=custo,
            buff_name=str(skill.name),
        )
        _emit(
            publish,
            T.COMBAT_SKILL_OUTCOME,
            type_="skill_outcome",
            payload={"caster": caster, "target": recipient, "result": out},
        )
        return out

    raise ValueError(f"Unknown skill.effect_type: {getattr(skill, 'effect_type', None)!r}")


def process_turn_start_effects(
    entity,
    *,
    rng: random.Random | None = None,
    publish: PublishFn = None,
) -> bool:
    """
    Processa efeitos no início do turno do `entity`.

    Publica `COMBAT_TURN_EFFECT` quando `publish` é fornecido.
    Retorna `True` se o turno deve ser pulado (congelado, atordoado ou dormindo).
    """
    _ = _rng(rng)

    skipped_turn = False

    # Cooldowns: decrementa a cada turno.
    if hasattr(entity, "skill_cooldowns"):
        for sid in list(entity.skill_cooldowns.keys()):
            entity.skill_cooldowns[sid] -= 1
            if entity.skill_cooldowns[sid] <= 0:
                del entity.skill_cooldowns[sid]
                _emit(
                    publish,
                    T.COMBAT_TURN_EFFECT,
                    type_="turn_effect",
                    payload={"entity": entity, "kind": "cooldown_expired", "skill_id": sid},
                )

    # Regeneração de mana: a base do turno, mais o que vier de buff ou passiva.
    max_mp = int(getattr(entity, "base_mp", entity.get_mp()))
    mana_regen = fx.combat_modifier(entity, "mana_regen")
    mana_regen += max(1, max_mp * MP_REGEN_PERCENT_PER_TURN / 100)
    if mana_regen > 0:
        entity.reduce_mp(-int(mana_regen))
        if entity.get_mp() > max_mp:
            entity._mp = max_mp

    # O NÚCLEO passa o turno: aplica DoT e dreno, decrementa e expira. Ele não
    # publica evento nem conhece a tela — devolve o que aconteceu, e a voz é
    # dada aqui.
    relatorio = core.tick_effects(entity)
    skipped_turn = relatorio["skip_turn"]

    for effect_id, dano in relatorio["dot"].items():
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": f"{effect_id}_tick", "damage": dano},
        )
    for effect_id, quanto in relatorio["drain"].items():
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": f"{effect_id}_tick", "amount": quanto},
        )
    for instancia in core.instances(entity, core.FAMILY_CONTROL):
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": instancia.effect},
        )

    for effect in relatorio["expired"]:
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": "effect_expired", "name": effect},
        )

    buffs_to_remove: list[str] = []
    for buff, data in list(getattr(entity, "active_buffs", {}).items()):
        data["duration"] -= 1
        if data["duration"] <= 0:
            buffs_to_remove.append(buff)

    for buff in buffs_to_remove:
        del entity.active_buffs[buff]
        _emit(
            publish,
            T.COMBAT_TURN_EFFECT,
            type_="turn_effect",
            payload={"entity": entity, "kind": "buff_expired", "name": buff},
        )

    if entity.get_hp() <= 0:
        entity.set_isalive(False)

    return skipped_turn


def roll_flee_success(*, rng: random.Random | None = None) -> bool:
    r = _rng(rng)
    return r.randrange(0, FLEE_RANGE_MAX) == 0
