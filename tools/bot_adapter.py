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

from src.content.economy import exit_fee
from src.content.factories import features as feat
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
)
from src.shared.effects import TURN_SKIPPING_STATUSES
from src.sim.bot import (
    ActionMechanicsView,
    ActionOption,
    CombatState,
    InteractionView,
    MapState,
    ProgressionState,
    ServiceView,
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


def _egide_absorve(defensor, dano_de_entrada: int) -> int:
    """Quanto a Égide absorve do próximo golpe, com o MP ATUAL.

    Leitura NÃO-MUTANTE: não gasta mana, não simula ataque, não reproduz a
    execução. Só a capacidade, a partir do estado real e de
    `MAGIC_SHIELD_DAMAGE_PER_MP`.

    Mesma dívida registrada de `_chance_de_critico`: `_absorve_com_egide` é
    privada E muta, então não há leitura canônica para reutilizar.
    """
    fracao = int(getattr(defensor, "magic_shield_percent", 0) or 0)
    mana = int(getattr(defensor, "get_mp", lambda: 0)())
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
        campos["breaks_statuses"] = _quebra_ao_dar_dano(monstro)
        # O secundário da carta é um status de verdade, com chance própria.
        sec = getattr(skill, "secondary", None)
        if sec is not None:
            campos["status_effect"] = str(sec.effect)
            campos["status_chance"] = _chance_efetiva(monstro, str(sec.effect), float(sec.chance))
            campos["status_skips_turn"] = str(sec.effect) in TURN_SKIPPING_STATUSES
            por_turno, dur = _dot_declarado(str(sec.effect), monstro, int(sec.duration or 0))
            campos["dot_damage_per_turn"] = por_turno
            campos["dot_duration"] = dur

    elif familia == "heal":
        # Percentual do HP máximo, MAIS `potion_heal_bonus` — a mesma ordem de
        # `apply_skill`, que aplica o bônus sobre o valor já calculado.
        bruto = int(hero.base_hp * float(getattr(skill, "effect_value", 0) or 0) / 100)
        campos["healing"] = bruto + int(bruto * fx.combat_modifier(hero, "potion_heal_bonus") / 100)

    elif familia == "status":
        # `effect_value` de uma skill de status é o NOME do efeito, não um
        # número. Tratá-lo como número levantava `ValueError` e derrubava a run
        # na primeira skill de status que o herói recebesse — 37 são acessíveis.
        efeito = str(getattr(skill, "effect_value", "") or "")
        campos["status_effect"] = efeito
        campos["status_chance"] = _chance_efetiva(
            monstro, efeito, float(getattr(skill, "chance", 100) or 100)
        )
        campos["status_skips_turn"] = efeito in TURN_SKIPPING_STATUSES
        campos["already_active"] = efeito in (getattr(monstro, "active_effects", {}) or {})
        por_turno, dur = _dot_declarado(efeito, monstro, duracao)
        campos["dot_damage_per_turn"] = por_turno
        campos["dot_duration"] = dur

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

    return ActionMechanicsView(**campos)


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
    absorvivel = _egide_absorve(hero, state.alvo_dano)
    age_antes = _age_antes(hero, monstro)

    base = combat_mech.basic_attack_power(hero)
    p_crit = _chance_de_critico(hero)
    normal = _dano_do_funil(hero, monstro, base, critico=False)
    critico = _dano_do_funil(hero, monstro, base, critico=True)
    opcoes.append(
        ActionOption(
            action_id="attack",
            family="attack",
            label="ataque básico",
            mechanics=ActionMechanicsView(
                expected_strike_damage=max(1, int(normal * (1 - p_crit) + critico * p_crit)),
                hit_chance=_chance_de_acerto(hero, monstro),
                crit_chance=p_crit,
                acts_before_enemy=age_antes,
                aegis_absorbable_damage=absorvivel,
                interactions=_interacoes_do_ataque(hero, monstro),
                breaks_statuses=_quebra_ao_dar_dano(monstro),
            ),
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
                mechanics=replace(mecanica, aegis_absorbable_damage=absorvivel),
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
            "aegis_absorbable_damage": absorvivel,
            # Recurso finito: sem este número a policy não sabe que está
            # gastando o último frasco.
            "uses_left": max(1, restantes),
        }
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
                aegis_absorbable_damage=absorvivel,
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


def estado_do_mapa(bot) -> tuple[MapState, ProgressionState]:
    """O andar e a run, como o jogador os vê.

    `TargetView` tem quatro campos e nenhum identifica o monstro: `draw_map`
    desenha `&`, ou `B` se for chefe. Nome e nível só existem depois da colisão.
    """
    hero = bot.hero
    campo = bot._campo(por_combate=True)
    from src.engine.map_analysis import rota_do_campo

    alvos = []
    for casa, monstro in bot.mapa.enemies_pos.items():
        rota, _ = rota_do_campo(campo, casa, True)
        if not rota.alcancavel:
            continue
        alvos.append(
            TargetView(
                casa=casa,
                passos=rota.passos,
                extras=max(0, rota.combates - 1),
                chefe=bool(getattr(monstro, "is_boss", False)),
            )
        )

    servicos = []
    for casa, tipo in bot.mapa.features.items():
        desvio = bot._desvio(casa)
        if desvio is not None:
            servicos.append(ServiceView(tipo=tipo, desvio=desvio))

    evento_casa = bot.mapa.event_pos
    desvio_evento = bot._desvio(evento_casa) if evento_casa is not None else None
    extracao = bot._casa_de(feat.EXTRACTION)

    alcance = bot._alcance(bot.saida)
    mapa = MapState(
        andar=bot.andar,
        posicao=bot.posicao,
        passos_ate_saida=alcance[0] if alcance else None,
        alvos=tuple(alvos),
        monstros_no_andar=len(bot.mapa.enemies_pos),
        servicos=tuple(servicos),
        evento=bot.mapa.event_type,
        desvio_evento=desvio_evento,
        desvio_extracao=bot._desvio(extracao) if extracao is not None else None,
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
        sinais_de_risco=tuple(bot._sinais_de_risco()),
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
        if servico.tipo == feat.EXTRACTION or servico.desvio > bot.DESVIO_ACEITAVEL:
            continue
        action_id = servico.tipo
        opcoes.append(ActionOption(action_id=action_id, family=servico.tipo, label=servico.tipo))
        destinos[action_id] = bot._casa_de(servico.tipo)

    if (
        mapa.evento
        and mapa.desvio_evento is not None
        and mapa.desvio_evento <= bot.DESVIO_ACEITAVEL
    ):
        action_id = mapa.evento
        opcoes.append(
            ActionOption(action_id=action_id, family=mapa.evento, label=f"evento {mapa.evento}")
        )
        destinos[action_id] = bot.mapa.event_pos

    if mapa.desvio_extracao is not None:
        opcoes.append(ActionOption(action_id="extrair", family="extrair", label="extração"))
        destinos["extrair"] = bot._casa_de(feat.EXTRACTION)

    opcoes.append(ActionOption(action_id="saida", family="saida", label="saída do andar"))
    destinos["saida"] = bot.saida
    return tuple(opcoes), destinos
