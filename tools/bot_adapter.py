"""A fronteira. O único lugar que enxerga o jogo real e o cérebro do bot.

    ADAPTADOR (aqui)  responde "o que esta ação FAZ"    -> ActionMechanicsView
    POLICY (src/sim/bot)  responde "quanto isso VALE"    -> Score -> Decision
    ENGINE (mechanics/battle)  executa a Action          (inalterado)

Três responsabilidades, e nenhuma delas é decidir:

1. **Observar.** Monta `MapState`, `ProgressionState` e `CombatState` a partir do
   mapa e do herói reais, respeitando a régua de informação: no mapa o jogador
   vê `&` e `B`, então `TargetView` não carrega nome nem nível. Depois da
   colisão, o que a ficha humana revelaria passa a ser informação legítima — e a
   colisão é o evento que revela, não a chamada de render: em headless
   `render_fight_intro` nunca roda.

2. **Enumerar o que é LEGAL.** MP, recarga, requisito de equipamento, existência
   do item e alcançabilidade da casa são regra do jogo. `_usable_skills` e
   `_consumables` de `sim/policies.py` continuam sendo a fonte — importadas e
   chamadas AQUI, com o `Hero` real. O cérebro recebe o resultado e, por
   construção, não consegue escolher fora dele.

3. **Traduzir.** `action_id` -> objeto real -> `battle.Action`. O cérebro devolve
   uma string; quem sabe o que ela significa é este módulo.

Os números mecânicos saem das funções canônicas (`mechanics/combat.py`) e dos
estimadores que o projeto já usa. Nenhuma fórmula de dano, mitigação ou acerto é
reescrita aqui nem no cérebro.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from src.content import extraction, forge
from src.content.economy import exit_fee
from src.content.factories import features as feat
from src.content.factories.dungeons import RANDOM_EVENT_TYPES, altar_hp_cost
from src.content.floor_exit import unpaid_streak
from src.engine.map_analysis import campo_de_custo, rota_do_campo
from src.entities.heroes import POTION_BUFFS
from src.mechanics import combat as combat_mech
from src.mechanics.battle import Action, build_turn_order
from src.shared import effect_core as core
from src.shared import effects as fx
from src.shared import interactions as ix
from src.shared.constants import (
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_CHANCE_HIGH,
    FLEE_RANGE_MAX,
    MAGIC_SHIELD_DAMAGE_PER_MP,
    RANDOM_EVENT_ALTAR_HP_COST_PERCENT,
    RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT,
)
from src.shared.economy import essence_after_penalty
from src.shared.effects import TURN_SKIPPING_STATUSES
from src.sim.bot import (
    ActionMechanicsView,
    ActionOption,
    CombatState,
    EventoView,
    InteractionView,
    MapState,
    ProgressionState,
    ServiceView,
    StatusView,
    TargetView,
)
from src.sim.policies import (
    _consumables,
    _usable_skills,
)

# As famílias de skill que o jogo conhece. Quem classifica é o dado da carta.
FAMILIAS_DE_SKILL = ("damage", "heal", "buff", "damage_reduction", "status")
# Consumíveis, por efeito. `max_hp` cura, `max_mp` repõe mana, o resto é elixir.
CURA = ("max_hp",)
MANA = ("max_mp",)
ELIXIR = (
    "strength",
    "defense",
    "agility",
    "crit_chance",
    "damage_reduction",
    "life_steal",
    "evasion",
)

CHANCE_DE_FUGA = 1.0 / FLEE_RANGE_MAX


# --- observação do combate -------------------------------------------------


def _chance_de_acerto(atacante, defensor, accuracy_modifier: int = 0) -> float:
    """A chance de acerto REAL, pela função canônica.

    `hit_chance` já resolve agilidade relativa, evasão, precisão, medo,
    ocultação e o modificador de mira da ação. Nada disso é recalculado aqui.
    """
    return combat_mech.hit_chance(atacante, defensor, accuracy_modifier) / 100


def _chance_de_critico(atacante, nome_da_skill: str = "") -> float:
    """Mirror mínimo da regra de crit em `mechanics/combat.py:383-391`.
    Protegido por teste de paridade.

    Não existe função canônica: a regra é código inline dentro de
    `resolve_physical_attack`. O mirror usa SÓ constantes e modificadores
    canônicos e a condição que já está no motor, sem duplicar número nenhum.

    DÍVIDA REGISTRADA: promover esta leitura a função pública do engine em
    rodada estrutural própria. Enquanto isso, o teste de paridade é o contrato.
    """
    base = (
        CRIT_CHANCE_HIGH
        if (
            hasattr(atacante, "get_classname")
            and atacante.get_classname() == "Rogue"
            and nome_da_skill == "Ataque Furtivo"
        )
        else CRIT_CHANCE_DEFAULT
    )
    base += int(fx.combat_modifier(atacante, "crit_chance"))
    return min(base, CRIT_CHANCE_CAP) / 100


def _dano_do_funil(atacante, defensor, base_power: int, *, critico: bool) -> int:
    """O dano que SAI DO FUNIL, para um golpe que acerta.

    DEPENDÊNCIA DE API PRIVADA, deliberada: `combat._calculate_damage` é o funil
    único do jogo, e `tools/` é a camada autorizada a conhecer `mechanics`.
    Chamar a privada é estritamente melhor que copiar a fórmula — uma cópia
    diverge na primeira mudança de balanceamento, e esta chamada não pode.
    O uso fica encapsulado NESTE módulo, e o teste de paridade falha se o
    comportamento divergir.

    Estágio: BASE + flat, ×(1+Σmult), ×Πxmult capado, × defesa, × mitigação.
    ANTES de Égide, procs on-hit, roubo de vida e interações de golpe.
    """
    mods = combat_mech.damage_modifiers(atacante, defensor, is_critical=critico)
    return combat_mech._calculate_damage(
        base_power=float(base_power),
        flat_mods=list(getattr(mods, "flat", ()) or ()),
        mult_mods=list(mods.mult),
        xmult_mods=list(mods.xmult),
        defense_target=defensor.get_df(),
        mitigation=list(mods.mitigation),
    )


def _golpe_esperado(atacante, defensor, base_power: int, nome_da_skill: str = "") -> int:
    """O golpe esperado: funil, com a expectativa do crítico e do acerto.

    Uma média sobre as duas rolagens que o motor faz — acerto e crítico. É o
    número que a policy compara, e é a MESMA unidade dos dois lados do combate.
    """
    p_crit = _chance_de_critico(atacante, nome_da_skill)
    normal = _dano_do_funil(atacante, defensor, base_power, critico=False)
    critico = _dano_do_funil(atacante, defensor, base_power, critico=True)
    por_acerto = normal * (1 - p_crit) + critico * p_crit
    return max(1, int(por_acerto * _chance_de_acerto(atacante, defensor)))


def _dano_basico_esperado(atacante, defensor) -> int:
    return _golpe_esperado(atacante, defensor, combat_mech.basic_attack_power(atacante))


def _egide_absorve(defensor, dano_de_entrada: int, mp: int | None = None) -> int:
    """Quanto a Égide absorve do próximo golpe, com o MP que ela TERÁ.

    Leitura NÃO-MUTANTE: não gasta mana, não simula ataque, não reproduz a
    execução. Só a capacidade, a partir do estado real e de
    `MAGIC_SHIELD_DAMAGE_PER_MP`.

    `mp` existe porque a ORDEM do motor importa: `combat.apply_skill` faz
    `caster.reduce_mp(custo)` ANTES de o golpe resolver, e `_absorve_com_egide`
    só dispara quando o herói é DEFENSOR — ou seja, no turno do monstro, depois
    de a skill já ter cobrado a mana. Declarar a capacidade com o MP de antes
    seria prometer um escudo que não vai existir. Cada ação declara a Égide que
    sobra DEPOIS do que ela mesma gasta ou repõe.

    Mesma dívida registrada de `_chance_de_critico`: `_absorve_com_egide` é
    privada E muta, então não há leitura canônica para reutilizar.
    """
    fracao = int(getattr(defensor, "magic_shield_percent", 0) or 0)
    mana = int(getattr(defensor, "get_mp", lambda: 0)()) if mp is None else max(0, int(mp))
    if fracao <= 0 or mana <= 0 or dano_de_entrada <= 1:
        return 0
    return max(0, min(int(dano_de_entrada * fracao / 100), int(mana * MAGIC_SHIELD_DAMAGE_PER_MP)))


def _age_antes(hero, monstro) -> bool:
    """Quem começa. Derivado da regra real: `battle.build_turn_order`."""
    ordem = build_turn_order(hero, [monstro])
    return bool(ordem) and ordem[0] is hero


def estado_do_combate(hero, monstro, turno: int) -> CombatState:
    """A posição, com o que a ficha revelou e o que mudou desde então.

    Remontado a cada turno do herói: HP, MP, efeitos e recargas são os atuais;
    os atributos do oponente são os que a colisão revelou. Nada de futuro.
    """
    return CombatState(
        turno=turno,
        hp=hero.get_hp(),
        hp_max=hero.base_hp,
        mp=hero.get_mp(),
        mp_max=hero.base_mp,
        # ESPERADO, com a chance de acerto embutida: o golpe que erra não tira
        # vida. Se a linha de base não tivesse o mesmo desconto que as ações, o
        # ataque básico se penalizaria pela própria taxa de erro e apareceria
        # como pior que ele mesmo.
        dano_basico=_dano_basico_esperado(hero, monstro),
        alvo_nivel=int(getattr(monstro, "level", 0)),
        alvo_hp=monstro.get_hp(),
        alvo_hp_max=int(getattr(monstro, "base_hp", monstro.get_hp())),
        # O MP do alvo está na MESMA ficha do confronto que o HP e os atributos
        # (`render_compare_opponents`), então é informação legítima. É o que
        # `mana_burn` tem para drenar.
        alvo_mp=int(getattr(monstro, "get_mp", lambda: 0)()),
        alvo_mp_max=int(getattr(monstro, "base_mp", 0) or 0),
        alvo_dano=_dano_basico_esperado(monstro, hero),
        alvo_efeitos=tuple(sorted(getattr(monstro, "active_effects", {}) or {})),
        meus_efeitos=tuple(sorted(getattr(hero, "active_effects", {}) or {})),
    )


def _sonda_de_buff(hero, monstro, stat: str, valor: int, rotulo: str) -> dict:
    """Levanta o buff de VERDADE, mede pelas funções canônicas, e desfaz.

    É o que evita reimplementar a curva de defesa, o teto de redução e a conta
    de acerto: a resposta vem de quem é dono dela. Escreve no MESMO formato que
    `combat.apply_skill` usa (`{stat, value, duration}`), com `fx.buff_value`
    resolvendo o valor — então o que se mede é o buff que o jogo aplicaria.

    Mede as TRÊS consequências da agilidade, porque o motor tem as três:
    quanto o golpe dele passa a doer, quanto o meu passa a doer, e quem age
    primeiro (`build_turn_order`). A versão anterior media só a primeira, e
    comparava bruto com esperado — por isso `Guarda Alta` marcava zero e
    `Sombra Rápida` era invisível.

    Não toca RNG e desfaz no `finally`. Há teste provando que o herói volta ao
    estado anterior.
    """
    buffs = getattr(hero, "active_buffs", None)
    if buffs is None or not stat:
        return {}
    chave = f"__sonda__{rotulo}"
    try:
        buffs[chave] = {
            "stat": stat,
            "value": fx.buff_value(hero, stat, int(valor)),
            "duration": 1,
        }
        return {
            "entrando": _dano_basico_esperado(monstro, hero),
            "saindo": _dano_basico_esperado(hero, monstro),
            "age_antes": _age_antes(hero, monstro),
        }
    finally:
        buffs.pop(chave, None)


def _consequencias_do_buff(hero, monstro, stat: str, valor: int, rotulo: str) -> dict:
    """Os campos do view que a sonda preenche, só quando MUDAM algo."""
    antes_entrando = _dano_basico_esperado(monstro, hero)
    antes_saindo = _dano_basico_esperado(hero, monstro)
    antes_ordem = _age_antes(hero, monstro)
    depois = _sonda_de_buff(hero, monstro, stat, valor, rotulo)
    if not depois:
        return {}
    campos: dict = {}
    if depois["entrando"] < antes_entrando:
        campos["incoming_damage_after"] = depois["entrando"]
    if depois["saindo"] > antes_saindo:
        campos["outgoing_damage_after"] = depois["saindo"]
    if depois["age_antes"] != antes_ordem:
        campos["acts_before_enemy"] = antes_ordem
        campos["acts_before_enemy_after"] = depois["age_antes"]
    return campos


def _sonda_de_status(hero, monstro, efeito: str) -> dict:
    """Levanta o STATUS de verdade NO ALVO, mede, e desfaz.

    Gêmea de `_sonda_de_buff`, apontada para o outro lado. Existe porque status
    de ATRIBUTO — `weakened` (ST), `hexed` (MG), `slowed` (AG), `vulnerable`
    (DF), `clouded` (MP) — são 15 cartas acessíveis ao jogador de hoje e
    chegavam ao cérebro como "custa um turno e não faz nada": o nome do efeito e
    a chance, sem consequência nenhuma.

    Escreve a `EffectInstance` DIRETO no estado ativo, no formato canônico
    (`core.instance_key`, intensidade e duração do catálogo), em vez de chamar
    `core.apply`: aplicar de verdade dispara `after_apply`, que MUTA — stack,
    refresh e interações. Observar não pode cobrar o preço da ação.

    Mede com as MESMAS funções canônicas do resto do módulo e remove no
    `finally`. Há teste provando que o monstro volta ao estado anterior e teste
    de paridade provando que o declarado é o que um `core.apply` real produz.
    """
    definicao = core.definition(efeito)
    if definicao is None or definicao.family != core.FAMILY_ATTRIBUTE:
        return {}
    ativos = getattr(monstro, "active_effects", None)
    if ativos is None:
        return {}
    chave = core.instance_key(efeito, "__sonda__")
    anterior = ativos.get(chave)
    try:
        ativos[chave] = core.EffectInstance(
            effect=efeito,
            source_id="__sonda__",
            intensity=definicao.default_intensity,
            duration=definicao.default_duration,
        )
        return {
            "entrando": _dano_basico_esperado(monstro, hero),
            "saindo": _dano_basico_esperado(hero, monstro),
            "age_antes": _age_antes(hero, monstro),
        }
    finally:
        ativos.pop(chave, None)
        if anterior is not None:
            ativos[chave] = anterior


def _consequencias_do_status(hero, monstro, efeito: str) -> dict:
    """Os campos do view que a sonda de status preenche, só quando MUDAM algo.

    Simétrica à do buff, e nos DOIS sentidos: um status que baixa a Força do
    alvo diminui o golpe que entra, um que baixa a Defesa dele aumenta o golpe
    que sai, e `slowed` mexe nos dois mais a ordem de turno.
    """
    antes_entrando = _dano_basico_esperado(monstro, hero)
    antes_saindo = _dano_basico_esperado(hero, monstro)
    antes_ordem = _age_antes(hero, monstro)
    depois = _sonda_de_status(hero, monstro, efeito)
    if not depois:
        return {}
    campos: dict = {}
    if depois["entrando"] != antes_entrando:
        campos["incoming_damage_after"] = depois["entrando"]
    if depois["saindo"] != antes_saindo:
        campos["outgoing_damage_after"] = depois["saindo"]
    if depois["age_antes"] != antes_ordem:
        campos["acts_before_enemy"] = antes_ordem
        campos["acts_before_enemy_after"] = depois["age_antes"]
    return campos


def _custo_da_ocultacao_perdida(hero, monstro, views: tuple[InteractionView, ...]) -> dict:
    """O golpe que passo a tomar quando a ação GASTA um efeito meu.

    Emboscada consome a invisibilidade do atacante, e a invisibilidade é o que
    está segurando a mira do monstro (`core.concealment_penalty` dentro de
    `combat.hit_chance`). O benefício do ×1,20 já está dentro do dano declarado;
    o preço não estava em lugar nenhum.

    Mesma técnica das outras sondas: tira o efeito de verdade, mede pela função
    canônica, devolve no `finally`.
    """
    consumidos = [v.consumes_status for v in views if v.consumes_status and v.consumes_from_self]
    if not consumidos:
        return {}
    ativos = getattr(hero, "active_effects", None)
    if not ativos:
        return {}
    antes = _dano_basico_esperado(monstro, hero)
    removidos = {}
    try:
        for efeito in consumidos:
            for chave in [k for k in ativos if str(k).split("#")[0] == efeito]:
                removidos[chave] = ativos.pop(chave)
        if not removidos:
            return {}
        depois = _dano_basico_esperado(monstro, hero)
    finally:
        ativos.update(removidos)
    return {"incoming_damage_after": depois} if depois != antes else {}


def _turnos_de_controle_perdidos(
    monstro,
    views: tuple[InteractionView, ...],
    quebrados: tuple[str, ...],
    *,
    hit_chance: float = 1.0,
    crit_chance: float = 0.0,
) -> float:
    """Turnos de controle que esta ação abre mão, em VALOR ESPERADO.

    Duas fontes, e elas NÃO têm a mesma condição — tratá-las como certas cobrava
    de todo golpe contra alvo controlado um preço que o motor só cobra às vezes:

    - o que a LEI consome do alvo (Quebra Gélida gasta o gelo) só acontece se o
      golpe ACERTAR, e só se for CRÍTICO quando a lei exige crítico;
    - o que o DANO quebra (acordar quem dorme) só acontece se a ação de fato
      causar dano, isto é, se ela acertar.

    A condição vem dos fatos, não de peso inventado: `hit_chance` e `crit_chance`
    já são fatos do próprio view, e `requires_critical` é o fato que a FASE B
    derivou comparando `strike_interactions` nos dois valores de crítico.

    Não entra aqui o que sai de MIM: `invisible` é removido NA TENTATIVA,
    inclusive no erro, então é custo CERTO — e ocultação não rouba turno, então
    o preço dela é o golpe que passo a tomar (`incoming_damage_after`).
    """
    # efeito -> probabilidade de ele ser perdido por esta ação, a maior delas
    # quando mais de uma condição alcança o mesmo efeito.
    risco: dict[str, float] = {}
    for view in views:
        if not view.consumes_status or view.consumes_from_self:
            continue
        p = hit_chance * (crit_chance if view.requires_critical else 1.0)
        risco[view.consumes_status] = max(risco.get(view.consumes_status, 0.0), p)
    for efeito in quebrados:
        risco[efeito] = max(risco.get(efeito, 0.0), hit_chance)

    total = 0.0
    for instancia in core.instances(monstro):
        if instancia.effect not in TURN_SKIPPING_STATUSES:
            continue
        total += max(0, int(instancia.duration)) * risco.get(instancia.effect, 0.0)
    return total


def _dreno_declarado(efeito: str, monstro, duracao_da_carta: int) -> int:
    """Quanto MP esta ação tira do alvo, pelo catálogo canônico.

    `mana_burn` é família DRAIN: `tick_effects` reduz `intensity × stacks` do MP
    ATUAL a cada turno, pela duração do efeito. O teto é o MP que o alvo tem —
    e o MP do alvo é o que a ficha do confronto mostra, então não há informação
    escondida nesta conta.

    O fator de `Colapso Mental` entra pela função canônica `ix.drain_scale`, a
    mesma que `tick_effects` consulta.
    """
    definicao = core.definition(efeito)
    if definicao is None or definicao.family != core.FAMILY_DRAIN:
        return 0
    fator, _leis = ix.drain_scale(monstro, efeito)
    duracao = int(duracao_da_carta or definicao.default_duration)
    por_turno = int(definicao.default_intensity * fator)
    mp = int(getattr(monstro, "get_mp", lambda: 0)())
    return max(0, min(mp, por_turno * max(0, duracao)))


def _dot_declarado(efeito: str, hero, duracao_da_carta: int) -> tuple[int, int]:
    """Dano por turno e duração de um DoT que ESTA ação aplicaria.

    Usa o catálogo canônico (`effect_core.definition`): família, intensidade
    padrão por stack e duração padrão. O dano é `% do HP máximo`, a mesma regra
    de `effect_core.dot_damage`.
    """
    definicao = core.definition(efeito)
    if definicao is None or definicao.family != core.FAMILY_DOT:
        return 0, 0
    max_hp = int(getattr(hero, "base_hp", 1) or 1)
    por_turno = int(max_hp * definicao.default_intensity / 100)
    return max(0, por_turno), int(duracao_da_carta or definicao.default_duration)


# Mirror mínimo de `interactions.consume_strike`. Protegido por teste que EXECUTA
# a função real e exige que o declarado seja exatamente o que sumiu.
#
# Existe porque `consume_strike` MUTA — ela é o preço cobrado DEPOIS do golpe, e
# observar não pode gastar o gelo nem a invisibilidade de ninguém. Não há leitura
# canônica do custo.
#
# DÍVIDA REGISTRADA, junto com os mirrors de crítico e Égide da FASE A: promover
# a leitura a função pública do engine em rodada estrutural própria.
CONSUMO_DA_LEI: dict[str, tuple[str, bool]] = {
    # id -> (efeito consumido, sai de quem ATACA?)
    "emboscada": ("invisible", True),
    "quebra_gelida": ("frozen", False),
}


def _leis_de_golpe_por_critico(hero, monstro) -> dict[str, bool]:
    """Quais leis de golpe disparam, e quais delas DEPENDEM do crítico.

    Duas chamadas à mesma função canônica, e a diferença entre elas responde a
    pergunta. Nenhum branching de `interactions.py` é reproduzido aqui.
    """
    sem_crit = set(ix.strike_interactions(hero, monstro, is_critical=False))
    com_crit = set(ix.strike_interactions(hero, monstro, is_critical=True))
    return {lei: lei not in sem_crit for lei in sem_crit | com_crit}


def _view_da_lei(lei_id: str, *, exige_critico: bool, bonus_de_duracao: int = 0) -> InteractionView:
    lei = ix.CATALOG.get(lei_id)
    fatores = ix.strike_xmult((lei_id,))
    consome, do_atacante = CONSUMO_DA_LEI.get(lei_id, ("", False))
    return InteractionView(
        interaction_id=lei_id,
        label=ix.label(lei_id),
        kind=str(getattr(lei, "kind", "")),
        trigger=str(getattr(lei, "trigger", "")),
        requires_critical=exige_critico,
        # Neutro é 1.0: quem não mexe em dano não multiplica nada.
        damage_xmult=fatores[0] if fatores else 1.0,
        duration_bonus=bonus_de_duracao,
        consumes_status=consome,
        consumes_from_self=do_atacante,
    )


def _bonus_de_duracao(monstro, skill) -> dict[str, int]:
    """Quantos turnos a mais cada lei de APLICAÇÃO dá, pela função canônica.

    `duration_before_apply` é pura e devolve a duração com que a peça entraria e
    quais leis a mudaram. Chamando com 1 turno, a diferença É o bônus.
    """
    bonus: dict[str, int] = {}
    for efeito in ix.applicable_effects(skill):
        duracao, disparadas = ix.duration_before_apply(monstro, efeito, 1)
        for lei in disparadas:
            bonus[lei] = duracao - 1
    return bonus


def _interacoes_da_skill(hero, monstro, skill) -> tuple[InteractionView, ...]:
    """As leis que ESTA carta destrava contra ESTE alvo, agora.

    `interactions.opportunities` é a função canônica da pergunta — pública,
    pura, e já conhecendo todas as condições. O adaptador transporta o resultado
    e enriquece com os fatos que outras funções canônicas dão.

    NÃO usa `opportunity_weight`: aquele carrega `OPPORTUNITY_BONUS`, que é
    ESTRATÉGIA. Quanto uma oportunidade vale é pergunta da policy.
    """
    exige_critico = _leis_de_golpe_por_critico(hero, monstro)
    bonus = _bonus_de_duracao(monstro, skill)
    return tuple(
        _view_da_lei(
            lei,
            exige_critico=exige_critico.get(lei, False),
            bonus_de_duracao=bonus.get(lei, 0),
        )
        for lei in ix.opportunities(hero, monstro, skill)
    )


def _interacoes_do_ataque(hero, monstro) -> tuple[InteractionView, ...]:
    """As leis de golpe do ataque básico.

    `opportunities` pede uma carta, e o ataque básico não tem uma — então aqui
    a fonte é `strike_interactions`, que é a mesma função que o motor consulta
    dentro de `damage_modifiers`.
    """
    exige_critico = _leis_de_golpe_por_critico(hero, monstro)
    return tuple(
        _view_da_lei(lei, exige_critico=exige) for lei, exige in sorted(exige_critico.items())
    )


def _quebra_ao_dar_dano(monstro) -> tuple[str, ...]:
    """Os efeitos do alvo que o DANO desta ação quebraria.

    É a lei `sleep_damage` do catálogo, resolvida por
    `effect_core.break_on_damage` e declarada no catálogo de efeitos em
    `breaks_on_damage`. Não é interação que o bot ativa: é custo da ação
    escolhida — quem ataca um alvo dormindo acorda o alvo.
    """
    ativos = getattr(monstro, "active_effects", {}) or {}
    quebram = []
    for efeito in sorted(ativos):
        definicao = core.definition(str(efeito))
        if definicao is not None and definicao.breaks_on_damage:
            quebram.append(str(efeito))
    return tuple(quebram)


def _mecanica_de_skill(hero, monstro, skill) -> ActionMechanicsView:
    """O que esta skill FAZ. Fatos, pelas funções canônicas do jogo."""
    familia = str(skill.effect_type)
    nome = str(skill.name)
    custo = combat_mech.skill_mana_cost(hero, skill)
    duracao = int(getattr(skill, "duration", 0) or 0)
    mira = int(getattr(skill, "accuracy_modifier", 0) or 0)

    campos: dict = {
        "mana_cost": custo,
        "cooldown": int(getattr(skill, "cooldown", 0) or 0),
        "duration": duracao,
        "hit_chance": _chance_de_acerto(hero, monstro, mira),
        "crit_chance": _chance_de_critico(hero, nome),
        "acts_before_enemy": _age_antes(hero, monstro),
        "interactions": _interacoes_da_skill(hero, monstro, skill),
    }

    if familia == "damage":
        base = combat_mech.skill_damage_base(hero, skill, monstro)
        # `_golpe_esperado` já embute acerto; o view separa os dois, então aqui
        # entra o golpe POR ACERTO e a chance viaja no seu próprio campo.
        p_crit = _chance_de_critico(hero, nome)
        normal = _dano_do_funil(hero, monstro, base, critico=False)
        critico = _dano_do_funil(hero, monstro, base, critico=True)
        campos["expected_strike_damage"] = max(1, int(normal * (1 - p_crit) + critico * p_crit))
        # As duas pontas, sem a média: é o que separa "mata" de "deve matar".
        campos["strike_damage_no_crit"] = max(1, int(normal))
        campos["strike_damage_on_crit"] = max(1, int(critico))
        campos["breaks_statuses"] = _quebra_ao_dar_dano(monstro)
        campos["forfeited_control_turns"] = _turnos_de_controle_perdidos(
            monstro,
            campos["interactions"],
            campos["breaks_statuses"],
            hit_chance=campos["hit_chance"],
            crit_chance=campos["crit_chance"],
        )
        campos.update(_custo_da_ocultacao_perdida(hero, monstro, campos["interactions"]))

    elif familia == "heal":
        # Percentual do HP máximo, MAIS `potion_heal_bonus` — a mesma ordem de
        # `apply_skill`, que aplica o bônus sobre o valor já calculado.
        bruto = int(hero.base_hp * float(getattr(skill, "effect_value", 0) or 0) / 100)
        campos["healing"] = bruto + int(bruto * fx.combat_modifier(hero, "potion_heal_bonus") / 100)

    elif familia in ("buff", "damage_reduction"):
        stat = str(getattr(skill, "effect_stat", "") or "")
        if familia == "damage_reduction":
            stat = "damage_reduction"
        valor = getattr(skill, "effect_value", 0)
        campos["buff_stat"] = stat
        campos["buff_value"] = float(valor) if isinstance(valor, int | float) else 0.0
        campos["already_active"] = nome in (getattr(hero, "active_buffs", {}) or {})
        if not campos["already_active"] and isinstance(valor, int | float):
            campos.update(_consequencias_do_buff(hero, monstro, stat, int(valor), nome))

    # Principal e `secondary` saem do MESMO construtor, porque no motor eles
    # passam pelo mesmo `apply_effect`. Vale para a carta de dano com secundário
    # e para a de status que aplica dois efeitos.
    campos["statuses"] = _statuses_da_skill(hero, monstro, skill)
    return ActionMechanicsView(**campos)


def _status_declarado(hero, monstro, efeito: str, chance_base: float, duracao: int) -> StatusView:
    """UM efeito aplicado no alvo, com a consequência inteira.

    Ponto ÚNICO de construção, e é isso que o torna importante: principal e
    `secondary` passam pelas mesmas linhas, porque no motor eles passam pelo
    mesmo `apply_effect`. Antes o secundário chegava com nome e chance e sem
    consequência, e o bot valorava `vulnerable` de uma carta de status diferente
    do `vulnerable` da mesma família vindo no campo `secondary` — duas notas para
    a mesma peça do jogo.
    """
    if not efeito:
        return StatusView(effect="")
    por_turno, dur_dot = _dot_declarado(efeito, monstro, duracao)
    campos: dict = {
        "effect": efeito,
        "chance": _chance_efetiva(monstro, efeito, chance_base),
        "duration": int(duracao or 0),
        "skips_turn": efeito in TURN_SKIPPING_STATUSES,
        "already_active": efeito in (getattr(monstro, "active_effects", {}) or {}),
        "dot_damage_per_turn": por_turno,
        "dot_duration": dur_dot,
        "target_mp_drained": _dreno_declarado(efeito, monstro, duracao),
    }
    if not campos["already_active"]:
        consequencias = _consequencias_do_status(hero, monstro, efeito)
        campos["incoming_damage_after"] = consequencias.get("incoming_damage_after", 0)
        campos["outgoing_damage_after"] = consequencias.get("outgoing_damage_after", 0)
        campos["acts_before_enemy_after"] = consequencias.get("acts_before_enemy_after")
    return StatusView(**campos)


def _statuses_da_skill(hero, monstro, skill) -> tuple[StatusView, ...]:
    """Todos os efeitos que a carta aplica no alvo: o próprio e o `secondary`.

    A carta de DANO não tem efeito próprio — o dano é o efeito dela —, então só o
    `secondary` entra. A de STATUS tem os dois, e os dois contam.
    """
    declarados: list[StatusView] = []
    if str(skill.effect_type) == "status":
        declarados.append(
            _status_declarado(
                hero,
                monstro,
                str(getattr(skill, "effect_value", "") or ""),
                float(getattr(skill, "chance", 100) or 100),
                int(getattr(skill, "duration", 0) or 0),
            )
        )
    sec = getattr(skill, "secondary", None)
    if sec is not None:
        declarados.append(
            _status_declarado(
                hero,
                monstro,
                str(sec.effect),
                float(sec.chance),
                int(sec.duration or 0),
            )
        )
    return tuple(d for d in declarados if d.effect)


def _chance_efetiva(alvo, efeito: str, base: float) -> float:
    """A chance que o status REALMENTE tem, já descontada a resistência do alvo.

    Duas funções canônicas, zero conta nova: `fx.status_resistance` e
    `fx.effective_status_chance`. Antes o adaptador entregava a chance da carta,
    e um alvo imune parecia tão atordoável quanto qualquer outro.
    """
    if not efeito:
        return 0.0
    return fx.effective_status_chance(base, fx.status_resistance(alvo, efeito)) / 100


def acoes_do_combate(hero, monstro, state: CombatState) -> tuple[tuple[ActionOption, ...], dict]:
    """As ações LEGAIS deste turno, com os fatos de cada uma.

    Legalidade é regra do jogo: `_usable_skills` já cobre MP, recarga e
    requisito de equipamento, e `_consumables` cobre a existência do item. Uma
    ação indisponível não entra como candidata — não é avaliada e descartada,
    ela não existe.
    """
    opcoes: list[ActionOption] = []
    reais: dict[str, Any] = {}
    age_antes = _age_antes(hero, monstro)

    def egide(custo: int = 0, reposto: int = 0) -> int:
        """A Égide que sobra DEPOIS do que esta ação gasta ou repõe."""
        return _egide_absorve(hero, state.alvo_dano, mp=state.mp - custo + reposto)

    base = combat_mech.basic_attack_power(hero)
    p_crit = _chance_de_critico(hero)
    normal = _dano_do_funil(hero, monstro, base, critico=False)
    critico = _dano_do_funil(hero, monstro, base, critico=True)
    leis_do_ataque = _interacoes_do_ataque(hero, monstro)
    quebras_do_ataque = _quebra_ao_dar_dano(monstro)
    ataque: dict = {
        "expected_strike_damage": max(1, int(normal * (1 - p_crit) + critico * p_crit)),
        "strike_damage_no_crit": max(1, int(normal)),
        "strike_damage_on_crit": max(1, int(critico)),
        "hit_chance": _chance_de_acerto(hero, monstro),
        "crit_chance": p_crit,
        "acts_before_enemy": age_antes,
        "aegis_absorbable_damage": egide(),
        "interactions": leis_do_ataque,
        "breaks_statuses": quebras_do_ataque,
        "forfeited_control_turns": _turnos_de_controle_perdidos(
            monstro,
            leis_do_ataque,
            quebras_do_ataque,
            hit_chance=_chance_de_acerto(hero, monstro),
            crit_chance=p_crit,
        ),
    }
    ataque.update(_custo_da_ocultacao_perdida(hero, monstro, leis_do_ataque))
    opcoes.append(
        ActionOption(
            action_id="attack",
            family="attack",
            label="ataque básico",
            mechanics=ActionMechanicsView(**ataque),
        )
    )

    for skill in _usable_skills(hero, FAMILIAS_DE_SKILL):
        action_id = f"skill:{skill.id}"
        mecanica = _mecanica_de_skill(hero, monstro, skill)
        opcoes.append(
            ActionOption(
                action_id=action_id,
                family=str(skill.effect_type),
                label=str(skill.name),
                mechanics=replace(
                    mecanica, aegis_absorbable_damage=egide(custo=mecanica.mana_cost)
                ),
            )
        )
        reais[action_id] = skill

    for item in _consumables(hero, CURA + MANA + ELIXIR):
        tipo = str(getattr(item, "effect_type", ""))
        action_id = f"item:{getattr(item, 'id', item.name)}"
        valor = float(getattr(item, "effect_value", 0) or 0)
        restantes = sum(
            1 for i in hero.inventory if getattr(i, "id", None) == getattr(item, "id", None)
        )
        campos: dict = {
            "duration": int(getattr(item, "duration", 1) or 1),
            "acts_before_enemy": age_antes,
            # Recurso finito: sem este número a policy não sabe que está
            # gastando o último frasco.
            "uses_left": max(1, restantes),
        }
        campos["aegis_absorbable_damage"] = egide(
            reposto=int(hero.base_mp * valor / 100) if tipo in MANA else 0
        )
        if tipo in CURA:
            bruto = int(hero.base_hp * valor / 100)
            campos["healing"] = bruto + int(
                bruto * fx.combat_modifier(hero, "potion_heal_bonus") / 100
            )
            familia = "heal"
        elif tipo in MANA:
            campos["mana_restored"] = int(hero.base_mp * valor / 100)
            familia = "mana"
        else:
            familia = "buff"
            stat = POTION_BUFFS.get(tipo, ("", ""))[0]
            campos["buff_stat"] = stat
            campos["buff_value"] = valor
            # A MESMA sonda das skills. Antes ela não rodava para item, e todo
            # elixir chegava ao evaluator como "custa um turno e não faz nada".
            campos.update(_consequencias_do_buff(hero, monstro, stat, int(valor), str(item.name)))
        opcoes.append(
            ActionOption(
                action_id=action_id,
                family=familia,
                label=str(item.name),
                mechanics=ActionMechanicsView(**campos),
            )
        )
        reais[action_id] = item

    opcoes.append(
        ActionOption(
            action_id="flee",
            family="flee",
            label="fugir",
            mechanics=ActionMechanicsView(
                flee_chance=CHANCE_DE_FUGA,
                acts_before_enemy=age_antes,
                aegis_absorbable_damage=egide(),
            ),
        )
    )
    return tuple(opcoes), reais


def action_de(action_id: str, reais: dict, monstro) -> Action:
    """`action_id` -> `battle.Action`. A tradução é daqui, não do cérebro."""
    if action_id == "attack":
        return Action(kind="attack", target=monstro)
    if action_id == "flee":
        return Action(kind="flee")
    objeto = reais.get(action_id)
    if action_id.startswith("skill:"):
        alvo = monstro if str(getattr(objeto, "target", "enemy")) != "self" else None
        if str(objeto.effect_type) in ("heal", "buff", "damage_reduction"):
            alvo = None
        return Action(kind="skill", target=alvo, skill=objeto)
    if action_id.startswith("item:"):
        return Action(kind="item", item=objeto)
    raise ValueError(f"action_id desconhecido: {action_id!r}")


# --- observação do mapa ----------------------------------------------------


def rota_para(bot, casa, *, lutar: bool):
    """A rota canônica até `casa`. UMA regra, usada pelos DOIS lados.

    O driver ia lutar pelo caminho mais CURTO e o adaptador declarava pelo
    caminho que EVITA luta. Medido em 366 alvos: 12 divergências, e em todas o
    executado lutava MAIS que o declarado — o `-extras` que a policy subtraía era
    ficção. A regra em si (luta vai pelo curto, serviço vai pelo que evita)
    continua a mesma; o que muda é que agora existe um lugar só onde ela mora.

    PURA: lê `enemies_pos` como o mapa está agora e roda Dijkstra. Não sorteia,
    não antecipa e não consome RNG — quem rola dado é o engine, quando a ação
    acontecer.
    """
    por_combate = not lutar
    campo = campo_de_custo(bot.mapa, bot.posicao, por_combate=por_combate)
    return rota_do_campo(campo, casa, por_combate)


def encontros_do_caminho(mapa, caminho) -> set:
    """As casas de monstro que ESTE caminho obriga a encarar.

    CONJUNTO, e não contador, porque é assim que o custo se soma sem mentir: um
    monstro que aparece em duas pernas da mesma viagem é UM combate, já que
    depois do primeiro ele não existe mais. Somar `ida.combates + volta.combates`
    contaria duas vezes.
    """
    inimigos = mapa.enemies_pos
    return {casa for casa in caminho if casa in inimigos}


def _evento_declarado(bot, desvio: int, lutas: int) -> EventoView:
    """O `?` como o jogador o vê: onde está, e os desfechos que a REGRA permite.

    Nada aqui olha `mapa.event_type`. As duas frações saem de constantes
    canônicas, e `altar_mataria` é um fato sobre o HP de agora.
    """
    custo = altar_hp_cost(bot.hero)
    return EventoView(
        desvio=desvio,
        lutas_no_desvio=lutas,
        cura_da_fonte=RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT / 100,
        custo_do_altar=RANDOM_EVENT_ALTAR_HP_COST_PERCENT / 100,
        altar_mataria=custo >= bot.hero.get_hp(),
        desfechos=len(RANDOM_EVENT_TYPES),
    )


def _pecas_para_o_ferreiro(hero) -> int:
    """Quantas peças o Ferreiro pode mexer, pelas funções canônicas do jogo."""
    elegiveis = {id(i) for i in forge.enhanceable(hero)}
    elegiveis.update(id(i) for i in forge.socketable(hero))
    return len(elegiveis)


def _perda_de_essencia(hero, rolada: float = 1.0) -> float:
    """Quanto a PRÓXIMA saída não paga tiraria do multiplicador do andar.

    `use_exit` não tem pagamento parcial nem recusa voluntária: ou paga inteiro e
    zera o streak, ou cobra zero e incrementa. O preço aparece na Essência do
    andar seguinte, e `essence_after_penalty` tem piso — então a perda REAL é a
    diferença entre os dois multiplicadores, não o `-0,5` que o evaluator usava.
    """
    streak = unpaid_streak(hero)
    return max(
        0.0,
        essence_after_penalty(rolada, streak) - essence_after_penalty(rolada, streak + 1),
    )


def _dano_por_luta(bot) -> float:
    """Dano REAL recebido por encontro, em fração do teto de HP.

    O driver soma `Observador.recebido_no_encontro` — golpes e ticks de DoT que
    de fato acertaram o herói — e normaliza cada encontro pelo teto DAQUELE
    momento. Não é `HP de entrada - HP de saída`: o delta líquido é contaminado
    por cura, Égide e regeneração, e diria que uma luta cara foi barata só porque
    o herói bebeu no meio dela.

    Zero quando ainda não houve encontro medido. Sem evidência não se inventa
    média — quem trata o caso é o evaluator, com regra própria.
    """
    medidos = int(getattr(bot, "encontros_medidos", 0) or 0)
    if medidos <= 0:
        return 0.0
    return float(getattr(bot, "dano_recebido_frac", 0.0) or 0.0) / medidos


def _lutas_por_andar(bot) -> float:
    """Quantas lutas custou um andar, pelos andares já CONCLUÍDOS.

    É a taxa que converte "lutas que ainda absorvo" em "andares que ainda
    aguento", e ela vem da própria run — não de constante. Andar em curso não
    entra: ele ainda não terminou, e dividir por ele daria uma taxa parcial.
    """
    andares = int(getattr(bot, "andares_concluidos", 0) or 0)
    if andares <= 0:
        return 0.0
    return float(getattr(bot, "combates_na_run", 0) or 0) / andares


def _cura_garantida(hero) -> float:
    """Cura que já está na mão, em fração do teto de HP.

    Só o que é CONHECIDO e DETERMINÍSTICO: poção que o herói já carrega, cujo
    percentual está na carta do item. Fica de fora tudo que depende de sorte ou
    de chegar em algum lugar — o `?` que talvez seja Fonte, o drop que talvez
    caia, o preço que a Loja talvez tenha, o descanso do próximo andar.

    Limitada pelo que falta de vida: cura que transborda não é capacidade.
    """
    teto = max(1, int(getattr(hero, "base_hp", 1) or 1))
    falta = max(0, teto - int(hero.get_hp())) / teto
    total = sum(
        float(getattr(i, "effect_value", 0) or 0) / 100
        for i in hero.inventory
        if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
    )
    return min(total, falta)


def estado_do_mapa(bot) -> tuple[MapState, ProgressionState]:
    """O andar e a run, como o jogador os vê.

    `TargetView` tem quatro campos e nenhum identifica o monstro: `draw_map`
    desenha `&`, ou `B` se for chefe. Nome e nível só existem depois da colisão.
    """
    hero = bot.hero

    alvos = []
    for casa, monstro in bot.mapa.enemies_pos.items():
        # MESMA rota que `_ir_ate` vai andar para lutar. Declarar por uma e
        # caminhar por outra era a divergência medida.
        rota, caminho = rota_para(bot, casa, lutar=True)
        if not rota.alcancavel:
            continue
        # Os OUTROS monstros do caminho, por casa única e sem o próprio alvo.
        pelo_caminho = encontros_do_caminho(bot.mapa, caminho) - {casa}
        alvos.append(
            TargetView(
                casa=casa,
                passos=rota.passos,
                extras=len(pelo_caminho),
                chefe=bool(getattr(monstro, "is_boss", False)),
            )
        )

    servicos = []
    for casa, tipo in bot.mapa.features.items():
        desvio = bot._desvio(casa)
        if desvio is not None:
            servicos.append(ServiceView(tipo=tipo, desvio=desvio[0], lutas_no_desvio=desvio[1]))

    evento_casa = bot.mapa.event_pos
    desvio_evento = bot._desvio(evento_casa) if evento_casa is not None else None
    extracao = bot._casa_de(feat.EXTRACTION)
    desvio_extracao = bot._desvio(extracao) if extracao is not None else None
    # A rota até o `E` TERMINA nele: extrair encerra a run, e não há volta para a
    # saída. Por isso o custo é o da ida, medido pela mesma rota canônica que o
    # driver vai andar — e não pela fórmula de desvio, que assume passagem.
    lutas_ate_extracao = 0
    if extracao is not None:
        rota_e, caminho_e = rota_para(bot, extracao, lutar=False)
        if rota_e.alcancavel:
            lutas_ate_extracao = len(encontros_do_caminho(bot.mapa, caminho_e))

    alcance = bot._alcance(bot.saida)
    mapa = MapState(
        andar=bot.andar,
        posicao=bot.posicao,
        passos_ate_saida=alcance[0] if alcance else None,
        alvos=tuple(alvos),
        monstros_no_andar=len(bot.mapa.enemies_pos),
        servicos=tuple(servicos),
        # `tem_evento` é o que o mapa mostra: um `?`. O TIPO não atravessa.
        tem_evento=evento_casa is not None,
        evento=(
            _evento_declarado(bot, desvio_evento[0], desvio_evento[1])
            if desvio_evento is not None
            else None
        ),
        desvio_extracao=desvio_extracao[0] if desvio_extracao is not None else None,
        lutas_ate_extracao=lutas_ate_extracao,
    )
    prog = ProgressionState(
        nivel=hero.get_level(),
        hp=hero.get_hp(),
        hp_max=hero.base_hp,
        mp=hero.get_mp(),
        mp_max=hero.base_mp,
        ouro=hero.coins,
        taxa_de_saida=exit_fee(bot.andar),
        streak_nao_pagas=bot._streak(),
        pocoes_de_cura=bot._pocoes(),
        passivas=len(hero.passives),
        pecas_equipadas=sum(1 for i in hero.equipment.values() if i),
        pecas_para_o_ferreiro=_pecas_para_o_ferreiro(hero),
        tem_chave=extraction.has_key(hero),
        dano_por_luta=_dano_por_luta(bot),
        combates_observados=int(getattr(bot, "encontros_medidos", 0) or 0),
        lutas_por_andar=_lutas_por_andar(bot),
        andares_concluidos=int(getattr(bot, "andares_concluidos", 0) or 0),
        cura_garantida=_cura_garantida(hero),
        perda_de_essencia=_perda_de_essencia(hero),
    )
    return mapa, prog


def acoes_do_mapa(
    bot, mapa: MapState, prog: ProgressionState
) -> tuple[tuple[ActionOption, ...], dict]:
    """As ações LEGAIS no andar. Só entra o que dá para fazer agora."""
    opcoes: list[ActionOption] = []
    destinos: dict[str, Any] = {}

    for alvo in mapa.alvos:
        action_id = f"lutar:{alvo.casa[0]},{alvo.casa[1]}"
        opcoes.append(
            ActionOption(
                action_id=action_id,
                family="lutar",
                label="& no mapa" if not alvo.chefe else "B no mapa (chefe)",
                target=alvo,
            )
        )
        destinos[action_id] = alvo.casa

    if prog.pocoes_de_cura > 0:
        maior = bot._maior_pocao_percentual()
        opcoes.append(
            ActionOption(
                action_id="pocao",
                family="pocao",
                label="beber poção no mapa",
                mechanics=ActionMechanicsView(healing=int(prog.hp_max * maior / 100)),
            )
        )
        destinos["pocao"] = None

    for servico in mapa.servicos:
        # A Extração já é candidata própria (`extrair`), com avaliador próprio.
        # Enumerá-la também como serviço a fazia cair no ramo genérico de
        # investimento e ganhar por "folga de ouro" — o bot ia até a casa de
        # extração para investir nela.
        #
        # LEGALIDADE é o único filtro: entra tudo que é ALCANÇÁVEL. Antes um
        # `DESVIO_ACEITAVEL = 10` apagava a opção da mesa (7 de 45 serviços
        # medidos), e "vale a pena andar até lá" é pergunta da policy, não do
        # adaptador.
        if servico.tipo == feat.EXTRACTION:
            continue
        action_id = servico.tipo
        opcoes.append(ActionOption(action_id=action_id, family=servico.tipo, label=servico.tipo))
        destinos[action_id] = bot._casa_de(servico.tipo)

    if mapa.tem_evento and mapa.evento is not None:
        # UMA família, `evento`, porque o mapa mostra UM símbolo: `?`.
        opcoes.append(ActionOption(action_id="evento", family="evento", label="? no mapa (evento)"))
        destinos["evento"] = bot.mapa.event_pos

    # LEGALIDADE, não estratégia: sem a Chave de Extração a casa `E` não deixa
    # encerrar a run, então extrair não é uma ação possível e não entra como
    # candidata. Quanto ela VALE continua sendo pergunta de `_avaliar_extracao`.
    if mapa.desvio_extracao is not None and prog.tem_chave:
        opcoes.append(ActionOption(action_id="extrair", family="extrair", label="extração"))
        destinos["extrair"] = bot._casa_de(feat.EXTRACTION)

    opcoes.append(ActionOption(action_id="saida", family="saida", label="saída do andar"))
    destinos["saida"] = bot.saida
    return tuple(opcoes), destinos
