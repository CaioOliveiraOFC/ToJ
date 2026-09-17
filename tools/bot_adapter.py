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

from typing import Any

from src.content.economy import exit_fee
from src.content.factories import features as feat
from src.mechanics import combat as combat_mech
from src.mechanics.battle import Action
from src.shared import effects as fx
from src.shared.constants import FLEE_RANGE_MAX
from src.shared.effects import TURN_SKIPPING_STATUSES
from src.sim.bot import (
    ActionMechanicsView,
    ActionOption,
    CombatState,
    MapState,
    ProgressionState,
    ServiceView,
    TargetView,
)
from src.sim.policies import (
    _consumables,
    _estimate_basic_damage,
    _estimate_skill_damage,
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


def _dano_esperado(atacante, defensor) -> int:
    """Dano por turno ESPERADO: a estimativa canônica vezes a chance de acerto.

    As duas contas são do jogo (`sim/policies._estimate_basic_damage` e
    `mechanics.combat.hit_chance`); aqui elas só se encontram, e o resultado é um
    FATO que a policy compara.
    """
    bruto = _estimate_basic_damage(atacante, defensor)
    return max(1, int(bruto * combat_mech.hit_chance(atacante, defensor) / 100))


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
        dano_basico=_dano_esperado(hero, monstro),
        alvo_nivel=int(getattr(monstro, "level", 0)),
        alvo_hp=monstro.get_hp(),
        alvo_hp_max=int(getattr(monstro, "base_hp", monstro.get_hp())),
        alvo_dano=_dano_esperado(monstro, hero),
        alvo_efeitos=tuple(sorted(getattr(monstro, "active_effects", {}) or {})),
        meus_efeitos=tuple(sorted(getattr(hero, "active_effects", {}) or {})),
    )


def _mecanica_de_skill(hero, monstro, skill, dano_basico_recebido: int) -> ActionMechanicsView:
    """O que esta skill FAZ. Fatos, pelas funções canônicas do jogo."""
    familia = str(skill.effect_type)
    custo = combat_mech.skill_mana_cost(hero, skill)
    duracao = int(getattr(skill, "duration", 0) or 0)
    efeito = str(getattr(skill, "effect_value", "") or "")
    ja_ativo = False
    dano = cura = 0
    entrando = 0
    chance_status = 0.0

    if familia == "damage":
        dano = _estimate_skill_damage(hero, skill, monstro)
    elif familia == "heal":
        # O motor aplica cura como percentual do HP máximo.
        cura = int(hero.base_hp * float(getattr(skill, "effect_value", 0)) / 100)
    elif familia == "status":
        chance_status = float(getattr(skill, "chance", 100) or 100) / 100
        ja_ativo = efeito in (getattr(monstro, "active_effects", {}) or {})
    elif familia in ("buff", "damage_reduction"):
        ja_ativo = str(skill.name) in (getattr(hero, "active_buffs", {}) or {})
        if not ja_ativo:
            entrando = _dano_recebido_com_buff(hero, monstro, skill, dano_basico_recebido)

    return ActionMechanicsView(
        estimated_damage=dano,
        hit_chance=combat_mech.hit_chance(hero, monstro) / 100,
        crit_chance=fx.combat_modifier(hero, "crit_chance") / 100,
        healing=cura,
        mana_cost=custo,
        cooldown=int(getattr(skill, "cooldown", 0) or 0),
        duration=duracao,
        status_chance=chance_status,
        status_effect=efeito if familia == "status" else "",
        status_skips_turn=efeito in TURN_SKIPPING_STATUSES,
        buff_stat=str(getattr(skill, "effect_stat", "") or ""),
        buff_value=float(getattr(skill, "effect_value", 0) or 0),
        already_active=ja_ativo,
        incoming_damage_after=entrando,
    )


def _dano_recebido_com_buff(hero, monstro, skill, dano_atual: int) -> int:
    """Quanto o golpe dele passa a doer se eu levantar este buff.

    Medido, não deduzido: escreve o buff no MESMO formato que
    `combat.apply_skill` usa, chama o estimador canônico, e desfaz. É o que
    evita reimplementar a curva de defesa ou o teto de redução — a resposta vem
    de quem é dono dela.

    Não toca RNG e desfaz no `finally`; há teste provando que o herói volta
    exatamente ao estado anterior.
    """
    stat = str(getattr(skill, "effect_stat", "") or "")
    if skill.effect_type == "damage_reduction":
        stat = "damage_reduction"
    if not stat:
        return 0
    chave = f"__sonda__{skill.name}"
    buffs = getattr(hero, "active_buffs", None)
    if buffs is None:
        return 0
    try:
        buffs[chave] = {
            "stat": stat,
            "value": fx.buff_value(hero, stat, int(getattr(skill, "effect_value", 0) or 0)),
            "duration": int(getattr(skill, "duration", 1) or 1),
        }
        depois = _estimate_basic_damage(monstro, hero)
    finally:
        buffs.pop(chave, None)
    return depois if depois < dano_atual else 0


def acoes_do_combate(hero, monstro, state: CombatState) -> tuple[tuple[ActionOption, ...], dict]:
    """As ações LEGAIS deste turno, com os fatos de cada uma.

    Legalidade é regra do jogo: `_usable_skills` já cobre MP, recarga e
    requisito de equipamento, e `_consumables` cobre a existência do item. Uma
    ação indisponível não entra como candidata — não é avaliada e descartada,
    ela não existe.
    """
    opcoes: list[ActionOption] = []
    reais: dict[str, Any] = {}

    opcoes.append(
        ActionOption(
            action_id="attack",
            family="attack",
            label="ataque básico",
            mechanics=ActionMechanicsView(
                # BRUTO, porque a policy multiplica por `hit_chance`. Passar o
                # esperado aqui descontava a chance de acerto duas vezes, e o
                # ataque básico aparecia com duração negativa — pior que ele
                # mesmo, que é a linha de base contra a qual tudo é medido.
                estimated_damage=_estimate_basic_damage(hero, monstro),
                hit_chance=combat_mech.hit_chance(hero, monstro) / 100,
                crit_chance=fx.combat_modifier(hero, "crit_chance") / 100,
            ),
        )
    )

    for skill in _usable_skills(hero, FAMILIAS_DE_SKILL):
        action_id = f"skill:{skill.id}"
        opcoes.append(
            ActionOption(
                action_id=action_id,
                family=str(skill.effect_type),
                label=str(skill.name),
                mechanics=_mecanica_de_skill(hero, monstro, skill, state.alvo_dano),
            )
        )
        reais[action_id] = skill

    for item in _consumables(hero, CURA + MANA + ELIXIR):
        tipo = str(getattr(item, "effect_type", ""))
        action_id = f"item:{getattr(item, 'id', item.name)}"
        valor = float(getattr(item, "effect_value", 0) or 0)
        opcoes.append(
            ActionOption(
                action_id=action_id,
                family="heal" if tipo in CURA else ("mana" if tipo in MANA else "buff"),
                label=str(item.name),
                mechanics=ActionMechanicsView(
                    healing=int(hero.base_hp * valor / 100) if tipo in CURA else 0,
                    mana_restored=int(hero.base_mp * valor / 100) if tipo in MANA else 0,
                    buff_stat=tipo if tipo in ELIXIR else "",
                    buff_value=valor,
                    duration=int(getattr(item, "duration", 1) or 1),
                ),
            )
        )
        reais[action_id] = item

    opcoes.append(
        ActionOption(
            action_id="flee",
            family="flee",
            label="fugir",
            mechanics=ActionMechanicsView(flee_chance=CHANCE_DE_FUGA),
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
