"""Políticas de decisão do herói para simulação.

A razão de existirem duas políticas sérias — uma gananciosa e uma competente — é
medir o *skill gap*: a diferença de resultado entre apertar sempre "atacar" e
jogar bem. Se as duas empatam, o jogo não tem decisão, e nenhum ajuste de número
conserta isso. Toda a suíte de balanceamento gira em torno dessa diferença.
"""

from __future__ import annotations

import random

from src.mechanics import combat as combat_mech
from src.mechanics.battle import Action, alive
from src.shared.effects import TURN_SKIPPING_STATUSES

# Um combate que o herói vai perder de qualquer jeito vale mais como fuga do que
# como morte. Abaixo deste percentual de HP, e sem cura na mão, o bot esperto foge.
FLEE_HP_RATIO = 0.12
# Abaixo deste percentual o bot esperto gasta poção ou skill de cura.
HEAL_HP_RATIO = 0.35
# Abaixo desta fração de mana, o bot bebe poção de mana se tiver uma.
MANA_POTION_RATIO = 0.25
# Efeitos de consumível que valem um turno no começo de um combate longo.
COMBAT_ELIXIR_EFFECTS = (
    "strength",
    "defense",
    "agility",
    "crit_chance",
    "damage_reduction",
    "life_steal",
    "evasion",
)
# A partir de quantos turnos estimados vale gastar um turno preparando buff.
LONG_FIGHT_TURNS = 5
# Quantos turnos contam como abertura do combate. Preparação (buff, elixir,
# status que só enfraquece) só vale aqui. Sem esse limite o bot reaplica o buff
# assim que ele expira e nunca ataca: como o inimigo continua com a vida cheia,
# qualquer teste baseado na vida acha que o combate ainda está começando. O laço
# inflava o combate do Ladino de 6 para 50 turnos.
OPENING_TURNS = 2


def _melhor(candidatos: list, valor) -> object:
    """O melhor candidato por `valor`, com a ordem do deck como desempate.

    Existe porque a política pegava `lista[0]` em toda decisão que tinha mais de
    uma opção — buff, controle, cura, poção. `lista[0]` é a ordem de inserção do
    deck, não uma preferência: a segunda skill de cura que o herói aprendesse
    jamais seria lançada, e uma carta aprendida tarde aparecia no relatório como
    "escolhida mas nunca usada". `Cortina de Fumaça` foi escolhida 75 vezes e
    lançada zero.
    """
    return max(candidatos, key=valor)


def _valor_de_cura(skill) -> float:
    """Cura em percentual do HP máximo — é assim que o motor a aplica."""
    return _numero(getattr(skill, "effect_value", 0))


def _valor_de_buff(skill) -> float:
    """Quanto o buff entrega, descontado o tempo que ele dura.

    Um buff de +30 por 2 turnos vale menos que um de +20 por 5. Sem a duração,
    a comparação premia o número grande e curto.
    """
    return _numero(getattr(skill, "effect_value", 0)) * max(1, int(getattr(skill, "duration", 1)))


def _valor_de_controle(skill) -> float:
    """Controle que rouba turno vale mais que o que só enfraquece."""
    from src.shared.effects import control_weight

    efeito = str(getattr(skill, "effect_value", ""))
    duracao = max(1, int(getattr(skill, "duration", 1)))
    chance = _numero(getattr(skill, "chance", 100)) / 100
    return control_weight(efeito) * duracao * chance


def _valor_de_item(item) -> float:
    return _numero(getattr(item, "effect_value", 0))


def _numero(valor) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def _hp_ratio(entity) -> float:
    return entity.get_hp() / max(1, int(getattr(entity, "base_hp", 1)))


def _usable_skills(hero, kinds: tuple[str, ...]) -> list:
    """As cartas que o herói pode lançar AGORA.

    `can_use_skill` entra na mesma lista que MP e recarga porque um requisito de
    equipamento não atendido é a mesma coisa das outras duas: a carta está no
    deck e não é jogável neste turno. Sem ele, o bot escolheria a melhor carta
    do deck, o motor recusaria o lançamento, e a run perderia o turno medindo
    uma decisão que o jogador nunca tomaria.
    """
    cooldowns = getattr(hero, "skill_cooldowns", {})
    return [
        s
        for s in hero.skills.values()
        if s.effect_type in kinds
        and hero.get_mp() >= hero.skill_mana_cost(s)
        and cooldowns.get(s.id, 0) <= 0
        and hero.can_use_skill(s)
    ]


def _consumables(hero, effect_types: tuple[str, ...]) -> list:
    """Consumíveis do inventário cujo efeito está na lista pedida."""
    return [
        item
        for item in hero.inventory
        if getattr(item, "consumable", False)
        and getattr(item, "effect_type", None) in effect_types
        and getattr(item, "effect_value", 0) > 0
    ]


def _healing_potions(hero) -> list:
    return _consumables(hero, ("max_hp",))


def _mana_potions(hero) -> list:
    return _consumables(hero, ("max_mp",))


def _combat_elixirs(hero) -> list:
    """Elixires que valem a pena antes de um combate longo."""
    return _consumables(hero, COMBAT_ELIXIR_EFFECTS)


def _active_buff_stats(hero) -> set[str]:
    """Atributos que já estão sob efeito de buff, para não empilhar o mesmo."""
    from src.shared.effects import buff_stat

    return {
        buff_stat(name, data)
        for name, data in getattr(hero, "active_buffs", {}).items()
        if isinstance(data, dict)
    }


def greedy_policy(hero, monsters: list, turn: int = 0) -> Action:
    """Sempre ataque básico, sempre no primeiro alvo vivo.

    É o piso de referência: o jogador que nunca aprende nada. Se este bot chega
    ao nível 20, o jogo recompensa paciência em vez de competência.
    """
    living = alive(monsters)
    return Action(kind="attack", target=living[0] if living else None)


def random_policy(hero, monsters: list, turn: int = 0, rng: random.Random | None = None) -> Action:
    """Ações aleatórias entre as legais. Serve para separar sorte de decisão."""
    r = rng or random
    living = alive(monsters)
    if not living:
        return Action(kind="attack")
    target = r.choice(living)
    options = ["attack"]
    if _usable_skills(hero, ("damage", "status", "buff", "heal", "damage_reduction")):
        options.append("skill")
    if _healing_potions(hero):
        options.append("item")
    kind = r.choice(options)
    if kind == "skill":
        return Action(
            kind="skill",
            target=target,
            skill=r.choice(
                _usable_skills(hero, ("damage", "status", "buff", "heal", "damage_reduction"))
            ),
        )
    if kind == "item":
        return Action(kind="item", item=r.choice(_healing_potions(hero)))
    return Action(kind="attack", target=target)


def smart_policy(hero, monsters: list, turn: int = 0, rng: random.Random | None = None) -> Action:
    """Heurística de jogador competente.

    A ordem das verificações é a própria tese do que "jogar bem" significa aqui:
    não morrer, escolher o alvo certo, preparar o combate longo, e só então
    otimizar dano. Uma política que só ataca e cura mede um jogo em que buff,
    controle e elixir não existem — e o balanceamento sai calibrado para esse
    jogo, não para o que está no código.
    """
    living = alive(monsters)
    if not living:
        return Action(kind="attack")

    ratio = _hp_ratio(hero)
    heal_skills = _usable_skills(hero, ("heal",))
    potions = _healing_potions(hero)
    letal = _golpe_letal(hero, living)

    # 1. Sobreviver — mas matar vem antes de curar quando o golpe é letal.
    #
    #    Sem essa checagem o bot cura sempre que cai abaixo do limiar, mesmo com
    #    o inimigo a um golpe da morte. Contra um alvo de dano alto isso vira
    #    espiral: cura, toma dano, cura de novo. O Mago gastava 231 dos 840
    #    turnos de skill curando na luta contra o glass cannon do andar 3, e
    #    levava 5,0 turnos onde o Ladino levava 2,7 — daí uma taxa de vitória de
    #    44,8% contra 99,8%. Não era fraqueza da classe: era o bot medindo mal o
    #    próprio jogo, e a calibração saiu em cima disso.
    if ratio < HEAL_HP_RATIO and letal is None:
        if heal_skills:
            return Action(kind="skill", target=hero, skill=_melhor(heal_skills, _valor_de_cura))
        if potions:
            return Action(kind="item", item=_melhor(potions, _valor_de_item))

    if letal is not None:
        alvo, skill = letal
        return Action(kind="skill" if skill else "attack", target=alvo, skill=skill)

    # 2. Fugir de combate perdido em vez de morrer nele.
    if ratio < FLEE_HP_RATIO and not heal_skills and not potions:
        return Action(kind="flee")

    # 3. O alvo. Há um só — a batalha é 1x1, e escolher alvo era regra de grupo.
    target = living[0]
    basic = _estimate_basic_damage(hero, target)
    turnos_estimados = _estimated_turns(target, basic)
    combate_longo = turnos_estimados >= LONG_FIGHT_TURNS

    # 4. Preparar o combate longo. Um buff de defesa no primeiro turno de uma
    #    luta de dez turnos rende mais que o dano daquele turno; num combate de
    #    três, é turno perdido.
    if combate_longo and turn < OPENING_TURNS:
        ativos = _active_buff_stats(hero)
        buffs = [
            s
            for s in _usable_skills(hero, ("buff", "damage_reduction"))
            if getattr(s, "effect_stat", "") not in ativos
        ]
        if buffs:
            return Action(kind="skill", target=hero, skill=_melhor(buffs, _valor_de_buff))

        elixires = [i for i in _combat_elixirs(hero) if _elixir_stat(i) not in ativos]
        if elixires:
            return Action(kind="item", item=_melhor(elixires, _valor_de_item))

    # 5. Repor mana quando ela é o gargalo e há poção em mãos.
    if _mp_ratio(hero) < MANA_POTION_RATIO and hero.skills:
        mana = _mana_potions(hero)
        if mana:
            return Action(kind="item", item=_melhor(mana, _valor_de_item))

    # 6. Controle. Atordoar um alvo economiza mais vida do que qualquer skill de
    #    dano gasta em MP, e vale sempre que o efeito não estiver ativo. Já um
    #    status que só enfraquece não encurta a luta: reaplicá-lo a cada expiração
    #    é um turno perdido por rodada, e era o que inflava o combate do Ladino
    #    de 11 para 50 turnos. Esse tipo entra só na abertura.
    if len(living) > 1 or combate_longo:
        ativos_no_alvo = getattr(target, "active_effects", {})
        control = [
            s
            for s in _usable_skills(hero, ("status",))
            if str(s.effect_value) not in ativos_no_alvo
            and (str(s.effect_value) in TURN_SKIPPING_STATUSES or turn < OPENING_TURNS)
        ]
        if control:
            return Action(kind="skill", target=target, skill=_melhor(control, _valor_de_controle))

    # 7. Otimizar dano: usar a skill só quando ela bate mais que o ataque básico,
    #    que é gratuito. Skill que não supera o básico é MP jogado fora.
    best_skill, best_damage = None, basic
    for skill in _usable_skills(hero, ("damage",)):
        estimate = _estimate_skill_damage(hero, skill, target)
        if estimate > best_damage:
            best_skill, best_damage = skill, estimate

    if best_skill is not None:
        return Action(kind="skill", target=target, skill=best_skill)

    return Action(kind="attack", target=target)


def _golpe_letal(hero, living: list):
    """Se o inimigo morre neste turno, e com o quê. `None` se não morre.

    Devolve `(alvo, skill)`, com `skill=None` quando o ataque básico já basta —
    ele é gratuito, então nunca vale gastar mana para matar quem o básico mata.
    O último ponto de vida do inimigo vale o mesmo que o primeiro: um turno
    gasto curando com o alvo a um golpe da morte é um turno de dano recebido a
    troco de nada.
    """
    for alvo in living:
        if _estimate_basic_damage(hero, alvo) >= alvo.get_hp():
            return alvo, None
    for alvo in living:
        for skill in _usable_skills(hero, ("damage",)):
            if _estimate_skill_damage(hero, skill, alvo) >= alvo.get_hp():
                return alvo, skill
    return None


def _mp_ratio(hero) -> float:
    return hero.get_mp() / max(1, int(getattr(hero, "base_mp", 1)))


def _elixir_stat(item) -> str:
    """Atributo que um elixir modifica, para não empilhar o mesmo buff."""
    from src.entities.heroes import POTION_BUFFS

    entry = POTION_BUFFS.get(getattr(item, "effect_type", ""), None)
    return entry[0] if entry else ""


def _estimated_turns(target, damage_per_turn: int) -> int:
    """Quantos turnos o duelo deve durar no ritmo atual."""
    return max(1, target.get_hp() // max(1, damage_per_turn))


def _estimate_basic_damage(hero, target) -> int:
    mitigation = 100 / (100 + max(0, target.get_df()))
    return max(1, int(combat_mech.basic_attack_power(hero) * mitigation))


def _estimate_skill_damage(hero, skill, target) -> int:
    """Dano estimado da skill CONTRA ESTE ALVO, agora.

    O alvo entra na conta porque a skill pode ter condição situacional: um golpe
    de execução vale mais contra o inimigo ferido, e nada contra o inteiro.
    Estimar sem o alvo faria o bot escolher sempre a de maior valor nominal e
    nunca ler a situação — que é justamente o que a condição existe para criar.
    """
    mitigation = 100 / (100 + max(0, target.get_df()))
    return max(1, int(combat_mech.skill_damage_base(hero, skill, target) * mitigation))


POLICIES = {
    "greedy": greedy_policy,
    "smart": smart_policy,
    "random": random_policy,
}


def get_policy(name: str):
    """Resolve o nome da política. Erro explícito é melhor que cair no default."""
    if name not in POLICIES:
        raise ValueError(f"Política desconhecida: {name!r}. Use uma de {sorted(POLICIES)}.")
    return POLICIES[name]
