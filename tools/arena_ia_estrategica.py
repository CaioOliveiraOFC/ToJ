"""A IA estratégica da Arena: utilidade estimada por simulação curta.

Controlador EXPERIMENTAL, de ferramenta (Copa Arena 03 v2). Nada aqui é regra
de jogo e nada aqui muda o motor: a IA só escolhe entre as ações que
`DuelView.legal_actions` oferece.

Como decide
-----------
Para cada ação legal (a rendição fica de fora: vale zero), a IA joga
`ROLLOUTS` continuações de `HORIZONTE` rodadas no PRÓPRIO MOTOR —
`Duel.play_round` sobre cópias, nunca sobre o duelo em curso —, com a ação
candidata na primeira rodada e a política base (`politica_base`) depois. O
estado em que cada continuação para é avaliado por `probabilidade_de_vitoria`,
uma corrida "quem derruba quem primeiro" montada com as funções canônicas de
dano (`hit_chance`, `crit_chance`, `damage_modifiers`, `_calculate_damage`,
`basic_attack_power`, `skill_damage_base`). Uma continuação que termina o
duelo vale 1 ou 0. A ação escolhida é a de maior média.

Não existe segundo motor: o que acontece dentro do horizonte (acerto, crítico,
status, DoT, controle, buffs, recargas, reserva de MP, iniciativa) é o motor
de verdade, e o que fica depois dele é estimado com as mesmas fórmulas que o
motor aplica.

As sementes das continuações são as MESMAS para todas as candidatas (números
aleatórios comuns): a diferença entre duas ações não se confunde com sorte. E
são derivadas do próprio estado visível, então a escolha é determinística — a
mesma visão dá a mesma ação, com ou sem auditoria.

O que ela sabe
--------------
- De si: a ficha e o estado do próprio herói, que o duelo entrega a cada
  controlador. Só leitura, e só o que o jogador vê da própria personagem.
- Do adversário: SÓ a `FighterView` (classe, nível, HP e MP atuais e máximos,
  nomes dos efeitos e dos buffs) e a história dessas leituras. Atributos, deck,
  equipamento e passivas do outro não são lidos: são MODELADOS
  (`ModeloDoAdversario`) a partir do herói canônico da mesma classe e nível com
  o loadout esperado (`sim.harness.make_hero`), com os tetos de HP/MP da tela e
  ajustado pelo que se observou rodada a rodada — dano recebido e causado, MP
  gasto (o custo identifica a carta no catálogo público), buffs que aparecem
  pelo nome.

O adversário das simulações escolhe AO MESMO TEMPO, sem ver a ação candidata:
a escolha dele na primeira rodada sai do estado anterior à rodada e é a mesma
para todas as candidatas.
"""

from __future__ import annotations

import copy
import dataclasses
import math
import random
import sys
import zlib
from dataclasses import dataclass, field

from src.content.gladiator import Gladiator
from src.content.skills_loader import get_offer_pool
from src.mechanics import combat
from src.mechanics.pvp_duel import Duel, DuelAction, opponent_of
from src.mechanics.pvp_initiative import FOUNDATION_REFERENCES, read_initiative
from src.shared import effect_core as core
from src.shared import effects as fx
from src.shared.constants import (
    CLASS_WEIGHTS,
    DEFENSE_K,
    MP_REGEN_PERCENT_PER_TURN,
    SKILL_BONUS_HEALTHY_RATIO,
    SKILL_BONUS_WOUNDED_RATIO,
)
from src.sim.harness import make_hero
from tools.arena_copa_teste import PoliticaCopa

# --- orçamento ---------------------------------------------------------------

# Rodadas jogadas no motor depois da escolha. Três cobrem a vida inteira de um
# buff de duração 3 (ele age em duas oportunidades depois de lançado) e o
# combo de duas rodadas status → dano.
HORIZONTE = 3
# Continuações por ação. Nos momentos críticos — alguém ao alcance de um golpe
# letal — a estimativa vale mais e o orçamento sobe.
ROLLOUTS = 10
ROLLOUTS_CRITICOS = 20
# Chance de o adversário simulado fugir da política base: a IA não sabe como o
# outro decide, e não pode planejar contra um adversário previsível demais.
EPSILON_ADVERSARIO = 0.25
# Pseudo-observações da priori do modelo, em rodadas: com poucas rodadas
# vistas, o modelo canônico pesa mais que a amostra.
PESO_DA_PRIORI = 4.0
# Os ajustes do modelo ficam presos numa faixa plausível: uma rodada estranha
# não pode transformar o adversário num monstro.
FAIXA_DE_AJUSTE = (0.5, 2.0)
# A política base cura abaixo desta fração de HP.
LIMIAR_DE_CURA_BASE = 0.45
# Erro relativo do ritmo de dano que o modelo estima, para cada lado. Sem ele a
# corrida trata a estimativa como exata, e 10% de erro no dano de uma luta de
# 50 rodadas viram certeza de vitória ou de derrota. Começa alto — no início o
# adversário é só a priori — e encolhe com as rodadas observadas:
# `κ(n) = final + (inicial − final)·w/(w + n)`. Os três números saem de uma
# calibração por log-loss em duelos IA × IA (`tools/arena_copa_03_ia.py`).
INCERTEZA_INICIAL = 2.0
INCERTEZA_FINAL = 0.5
RODADAS_DE_MEIA_INCERTEZA = 1.0
# Modificadores do adversário que a tela permite inferir, e quanto da minha
# própria ficha entra como priori deles (o resto vem da priori canônica).
MODIFICADORES_INFERIDOS = (
    "life_steal",
    "mana_regen",
    "bleed_chance",
    "poison_chance",
    "stun_chance",
    "fear_chance",
)
ENCOLHIMENTO_DA_REFERENCIA = 0.5


@dataclass(frozen=True)
class Configuracao:
    """O orçamento e as escolhas de modelo da IA. O padrão é o da Copa 03 v2.

    Existe para medir uma variante contra a outra com o resto igual — e para os
    testes rodarem com menos continuações.
    """

    horizonte: int = HORIZONTE
    rollouts: int = ROLLOUTS
    rollouts_criticos: int = ROLLOUTS_CRITICOS
    epsilon: float = EPSILON_ADVERSARIO
    incerteza_inicial: float = INCERTEZA_INICIAL
    incerteza_final: float = INCERTEZA_FINAL
    # Procs do acerto e roubo de vida na corrida do rodapé.
    procs_na_corrida: bool = True
    # Roubo de vida, regeneração e procs do adversário: priori-espelho + tela.
    inferir_modificadores: bool = True

    def incerteza(self, rodadas_observadas: int) -> float:
        w = RODADAS_DE_MEIA_INCERTEZA
        inicial, final = self.incerteza_inicial, self.incerteza_final
        return final + (inicial - final) * w / (w + rodadas_observadas)


# Passos da bisseção que acha a duração prevista da luta (ver `corrida`).
ITERACOES_DA_DURACAO = 14
# Preferência por vencer antes (ver `Leitura`): o peso, e a duração em que ela
# vale metade. 30 rodadas é a duração típica de um duelo da Copa 03.
PESO_DO_TEMPO = 0.05
RODADAS_DE_REFERENCIA = 30.0
# Impasse: nenhum dos dois bate o próprio recorde de HP mais baixo (por
# `PROGRESSO_MINIMO` do teto) há `JANELA_SEM_PROGRESSO` rodadas. Entre builds
# de sustento a cura por MP rende quatro vezes o dano por MP, e duas IAs que
# curam bem podem não sair do lugar. A partir daí um custo linear no tempo sobe
# até `PESO_DO_IMPASSE` em mais uma janela: a IA passa a preferir encerrar a luta
# a prolongá-la, e larga a cura que só a mantém onde está (ver `Leitura`).
JANELA_SEM_PROGRESSO = 20
PROGRESSO_MINIMO = 0.02
# E a duração por si: o recorde de HP baixo ainda cai de vez em quando numa
# luta que quase não anda, e zera a janela. A partir do dobro da duração típica
# a urgência sobe com a própria rodada — que é pública — e não volta.
INICIO_DA_LUTA_LONGA = 60
PESO_DO_IMPASSE = 1.0
TETO_DO_IMPASSE = 90.0


# --- estimativas canônicas -----------------------------------------------------


@dataclass(frozen=True)
class Golpe:
    """A distribuição de UM golpe, pelas fórmulas do motor."""

    acerto: float  # 0..1
    critico: float  # 0..1
    normal: int  # dano de um acerto sem crítico
    forte: int  # dano de um acerto crítico

    @property
    def media(self) -> float:
        return self.acerto * ((1 - self.critico) * self.normal + self.critico * self.forte)

    @property
    def variancia(self) -> float:
        quadrado = self.acerto * (
            (1 - self.critico) * self.normal**2 + self.critico * self.forte**2
        )
        return max(0.0, quadrado - self.media**2)

    def chance_de_derrubar(self, hp: int) -> float:
        if hp <= 0:
            return 1.0
        p = 0.0
        if self.normal >= hp:
            p += 1 - self.critico
        if self.forte >= hp:
            p += self.critico
        return self.acerto * p


def golpe_esperado(atacante, defensor, skill=None) -> Golpe:
    """O golpe de `atacante` em `defensor` agora: básico, ou a skill de dano.

    As mesmas chamadas que `resolve_physical_attack` faz — sem sortear e sem
    aplicar nada. `ix.strike_interactions` é leitura pura, então as leis do
    golpe (Quebra Gélida, Emboscada) entram sem gastar o gelo de ninguém. A
    Égide de Mana fica de fora: é estado, não fórmula, e nenhum Guerreiro a
    carrega.
    """
    if skill is None:
        base = combat.basic_attack_power(atacante)
        mira = 0
    else:
        base = combat.skill_damage_base(atacante, skill, defensor)
        mira = int(getattr(skill, "accuracy_modifier", 0) or 0)
    danos = []
    for critico in (False, True):
        mods = combat.damage_modifiers(atacante, defensor, is_critical=critico, skill=skill)
        danos.append(
            combat._calculate_damage(
                base_power=float(base),
                mult_mods=mods.mult,
                xmult_mods=mods.xmult,
                defense_target=defensor.get_df(),
                mitigation=mods.mitigation,
            )
        )
    return Golpe(
        acerto=combat.hit_chance(atacante, defensor, mira) / 100,
        critico=combat.crit_chance(atacante, skill) / 100,
        normal=danos[0],
        forte=danos[1],
    )


def cura_esperada(heroi, skill) -> int:
    """Quanto a skill de cura devolve a `heroi`. A conta de `apply_skill`.

    `apply_skill` cura e não devolve prévia, então a expressão é a mesma de lá —
    e `tests/test_arena_ia_estrategica.py` confere as duas contra o motor.
    """
    teto = int(getattr(heroi, "base_hp", heroi.get_hp()))
    cura = max(1, int(teto * int(skill.effect_value) / 100))
    return cura + int(cura * fx.combat_modifier(heroi, "potion_heal_bonus") / 100)


def regeneracao(heroi) -> int:
    """MP que o turno devolve: a conta de `process_turn_start_effects`."""
    teto = int(getattr(heroi, "base_mp", heroi.get_mp()))
    extra = fx.combat_modifier(heroi, "mana_regen")
    return int(extra + max(1, teto * MP_REGEN_PERCENT_PER_TURN / 100))


# Leituras que só dependem da ficha — nível, equipamento, gemas, passivas —, que
# não mudam durante um duelo. Nas cópias de simulação elas são lembradas: são a
# maior parte do custo de cada getter de atributo, e a simulação faz milhares.
LEITURAS_DA_FICHA = (
    "equipment_percent",
    "get_equipment_bonus",
    "get_passive_bonus",
    "weapon_percent",
    "can_use_skill",
)


class _Lembrada:
    __slots__ = ("_fn", "_memo")

    def __init__(self, fn) -> None:
        self._fn = fn
        self._memo: dict = {}

    def __call__(self, *args):
        try:
            return self._memo[args]
        except KeyError:
            valor = self._memo[args] = self._fn(*args)
            return valor


def lembrar_ficha(heroi):
    """Instala as leituras lembradas da ficha num herói de simulação."""
    for nome in LEITURAS_DA_FICHA:
        metodo = getattr(heroi, nome, None)
        if callable(metodo) and not isinstance(metodo, _Lembrada):
            setattr(heroi, nome, _Lembrada(metodo))
    return heroi


def para_simulacao(heroi):
    """Uma cópia INTEGRAL do herói, com as leituras da ficha lembradas.

    É a raiz das simulações de uma decisão. O herói do duelo nunca é tocado.
    """
    return lembrar_ficha(copy.deepcopy(heroi))


def copia_de_combate(heroi):
    """Uma cópia que só separa o estado que o combate muda.

    O duelo mexe em HP, MP, vida, efeitos ativos, buffs, recargas e na marca de
    `death_ignore` — e em nada mais do herói. O resto (ficha, equipamento,
    deck, passivas) é compartilhado com a raiz, que já é uma cópia: é o que
    torna barata cada continuação. `tests/test_arena_ia_estrategica.py` confere
    que o motor joga exatamente igual sobre esta cópia e sobre um `deepcopy`.
    """
    novo = copy.copy(heroi)
    novo.active_effects = {
        k: (
            core.EffectInstance(v.effect, v.source_id, v.intensity, v.duration, v.stacks)
            if isinstance(v, core.EffectInstance)
            else copy.deepcopy(v)
        )
        for k, v in heroi.active_effects.items()
    }
    novo.active_buffs = {
        k: dict(v) if isinstance(v, dict) else v for k, v in heroi.active_buffs.items()
    }
    novo.skill_cooldowns = dict(heroi.skill_cooldowns)
    return novo


def utilizavel(heroi, skill) -> bool:
    verificador = getattr(heroi, "can_use_skill", None)
    return not callable(verificador) or bool(verificador(skill))


class _SemTemporarios:
    """Tira buffs e efeitos dos heróis enquanto o bloco roda. Restaura no fim."""

    def __init__(self, *herois) -> None:
        self._herois = herois
        self._guardado: list = []

    def __enter__(self):
        self._guardado = [(h, h.active_buffs, h.active_effects) for h in self._herois]
        for h in self._herois:
            h.active_buffs = {}
            h.active_effects = {}

    def __exit__(self, *_):
        for h, buffs, efeitos in self._guardado:
            h.active_buffs = buffs
            h.active_effects = efeitos


_FAMILIAS_DE_MODIFICADOR = (core.FAMILY_ATTRIBUTE, core.FAMILY_ACCURACY, core.FAMILY_CONCEALMENT)


def _duracao_media_temporarios(*herois) -> float:
    """Quantas oportunidades, em média, os temporários ativos ainda valem."""
    duracoes = [int(d.get("duration", 0)) for h in herois for d in h.active_buffs.values()]
    duracoes += [
        i.duration
        for h in herois
        for i in core.instances(h)
        if i.definition is not None and i.definition.family in _FAMILIAS_DE_MODIFICADOR
    ]
    if not duracoes:
        return 0.0
    return max(0.0, sum(duracoes) / len(duracoes) - 0.5)


def controle_restante(heroi) -> int:
    """Oportunidades que o controle ativo ainda rouba (o tick pula enquanto houver)."""
    return max((i.duration for i in core.instances(heroi, core.FAMILY_CONTROL)), default=0)


def dot_por_tick(heroi) -> int:
    teto = int(heroi.base_hp)
    return sum(core.dot_damage(heroi, e, teto) for e in core.effects_of_family(core.FAMILY_DOT))


def _dot_restante(heroi) -> int:
    teto = int(heroi.base_hp)
    total = 0
    for efeito in core.effects_of_family(core.FAMILY_DOT):
        por_tick = core.dot_damage(heroi, efeito, teto)
        if por_tick <= 0:
            continue
        duracao = max(
            i.duration for i in core.instances(heroi, core.FAMILY_DOT) if i.effect == efeito
        )
        total += por_tick * duracao
    return total


@dataclass
class Ritmo:
    """O que um lado faz contra o outro, por oportunidade, neste estado."""

    basico: float  # dano médio do básico, sem temporários
    variancia: float  # variância desse golpe
    acerto: float  # chance de o básico acertar
    temporario: float  # dano a mais (ou a menos) que os temporários ativos ainda rendem
    mp: float
    regen: float
    dot: float = 0.0  # DoT que os procs do acerto põem no outro, por oportunidade
    controle: float = 0.0  # fração das oportunidades do OUTRO que os procs roubam
    medo: float = 0.0  # fração do tempo em que o OUTRO está com medo pelos procs
    roubo: float = 0.0  # roubo de vida, em fração do dano causado
    # [ganho por uso, custo, usos por rodada de luta, tipo, oportunidades até a recarga liberar]
    usos: list = field(default_factory=list)
    cura_por_uso: dict = field(default_factory=dict)  # índice em `usos` -> HP devolvido


def _procs(x, y, acerto: float) -> tuple[float, float, float]:
    """O que os procs do acerto de `x` (passiva e equipamento) fazem em `y`.

    A chance de cada um é a de `combat.ONHIT_PROCS`, com a resistência de `y`
    pela regra do núcleo (`effective_status_chance`); o efeito é o do catálogo.
    Devolve, por oportunidade de `x`: DoT esperado (uma aplicação rende a
    duração inteira; o empilhamento fica de fora, a favor da cautela), a fração
    das oportunidades de `y` que o controle rouba e a fração do tempo de `y` sob
    medo.
    """
    dot = controle = medo = 0.0
    teto = int(y.base_hp)
    for efeito, modificador in combat.ONHIT_PROCS.items():
        chance = fx.combat_modifier(x, modificador)
        definicao = core.definition(efeito)
        if chance <= 0 or definicao is None:
            continue
        pega = acerto * fx.effective_status_chance(chance, fx.status_resistance(y, efeito)) / 100
        if definicao.family == core.FAMILY_DOT:
            dot += pega * definicao.default_intensity / 100 * teto * definicao.default_duration
        elif definicao.family == core.FAMILY_CONTROL:
            controle += pega * definicao.default_duration
        elif efeito == "fear":
            medo += pega * definicao.default_duration
    return dot, min(0.9, controle), min(1.0, medo)


def _parte_da_luta_com_bonus(x, y, condicao: str) -> float:
    """Que fração do resto da luta a condição de bônus da carta vai valer.

    As de HP mudam com a luta: "alvo saudável" vale até o alvo cair abaixo de
    `SKILL_BONUS_HEALTHY_RATIO`, "ferido" só depois de `SKILL_BONUS_WOUNDED_RATIO`.
    Com o HP caindo em ritmo constante até zero, a fração é a parte da barra que
    ainda está na faixa. As de efeito (afetado, controlado) ficam de fora: o
    rodapé não supõe efeitos futuros, e dentro do horizonte quem joga é o motor.
    """

    def faixa(heroi, minimo: float, maximo: float) -> float:
        hp, teto = heroi.get_hp(), max(1, int(heroi.base_hp))
        if hp <= 0:
            return 0.0
        dentro = max(0.0, min(hp, maximo * teto) - minimo * teto)
        return min(1.0, dentro / hp)

    if condicao == "target_healthy":
        return faixa(y, SKILL_BONUS_HEALTHY_RATIO, 1.0)
    if condicao == "target_wounded":
        return faixa(y, 0.0, SKILL_BONUS_WOUNDED_RATIO)
    if condicao == "caster_wounded":
        return faixa(x, 0.0, SKILL_BONUS_WOUNDED_RATIO)
    return 0.0


def _dano_ao_longo_da_luta(x, y, skill) -> float:
    """O dano médio da skill pelo resto da luta, com o bônus situacional na medida.

    O golpe sem o bônus sai do funil; o bônus é o termo que `damage_modifiers`
    somaria ao `+MULT` (`additive_multiplier`), pesado pela fração da luta em
    que a condição vale. Medir a skill só no estado de agora creditaria o "alvo
    saudável" do primeiro golpe em todos os usos da luta.
    """
    bonus = int(getattr(skill, "bonus_percent", 0) or 0)
    condicao = str(getattr(skill, "bonus_condition", "") or "")
    if not bonus or not condicao:
        return golpe_esperado(x, y, skill).media
    pura = dataclasses.replace(skill, bonus_percent=0)
    sem = golpe_esperado(x, y, pura).media
    soma = combat.damage_modifiers(x, y, is_critical=False, skill=pura).mult
    fator = combat.additive_multiplier(soma + [bonus / 100]) / combat.additive_multiplier(soma)
    return sem * (1 + (fator - 1) * _parte_da_luta_com_bonus(x, y, condicao))


def _ritmo(x, y, procs: bool = True) -> Ritmo:
    """As taxas de `x` contra `y`, com as fórmulas do motor.

    Tudo é medido SEM os temporários (buffs, efeitos de atributo, de acerto e
    de ocultação, e as condições de bônus que dependem deles): são as taxas da
    luta inteira. O que os temporários ainda rendem entra à parte — a diferença
    que fazem no básico, pela duração média que lhes resta. Medir as skills com
    um buff ativo creditaria o buff em cada uso da luta toda.
    """
    basico = golpe_esperado(x, y)
    with _SemTemporarios(x, y):
        basico_sem = golpe_esperado(x, y)
        ganhos = {
            s.id: _dano_ao_longo_da_luta(x, y, s) - basico_sem.media
            for s in x.skills.values()
            if s.effect_type == "damage"
        }
        dot, controle, medo = _procs(x, y, basico_sem.acerto) if procs else (0.0, 0.0, 0.0)
    ritmo = Ritmo(
        basico=max(1.0, basico_sem.media),
        variancia=basico_sem.variancia,
        acerto=max(0.01, basico_sem.acerto),
        temporario=(basico.media - basico_sem.media) * _duracao_media_temporarios(x, y),
        mp=float(x.get_mp()),
        regen=float(regeneracao(x)),
        dot=dot,
        controle=controle,
        medo=medo,
        roubo=max(0.0, fx.combat_modifier(x, "life_steal")) / 100 if procs else 0.0,
    )
    for skill in x.skills.values():
        if not utilizavel(x, skill) or skill.effect_type not in ("damage", "heal"):
            continue
        custo = max(1, combat.skill_mana_cost(x, skill))
        por_rodada = 1 / (int(skill.cooldown or 0) + 1)
        # A recarga que já corre adia o próximo uso: sem isto, a carta lançada
        # dentro do horizonte seria creditada de novo no rodapé, como se não
        # tivesse sido gasta — e a cura que o outro acabou de usar, duas vezes.
        espera = max(0, int(x.skill_cooldowns.get(skill.id, 0)) - 1)
        if skill.effect_type == "damage":
            if ganhos[skill.id] > 0:
                ritmo.usos.append([ganhos[skill.id], custo, por_rodada, "dano", espera])
        else:
            ritmo.cura_por_uso[len(ritmo.usos)] = cura_esperada(x, skill)
            ritmo.usos.append([0.0, custo, por_rodada, "cura", espera])
    return ritmo


def _taxa(meu: Ritmo, dele: Ritmo) -> float:
    """O dano que eu tiro dele por oportunidade, líquido do roubo de vida dele.

    O controle e o medo que os procs dele põem em mim reduzem o que eu faço; o
    roubo de vida dele devolve parte do que ele me tira. A taxa líquida não cai
    abaixo de um décimo da bruta: o roubo é limitado pelo HP que falta a ele.
    """
    medo = 1 - dele.medo * min(1.0, core.FEAR_ACCURACY_PENALTY / 100 / meu.acerto)
    bruta = (meu.basico + meu.dot) * (1 - dele.controle) * medo
    roubo_dele = dele.roubo * dele.basico * (1 - meu.controle)
    return max(0.1 * bruta, bruta - roubo_dele)


def _vantagem_do_mp(meu: Ritmo, dele: Ritmo, duracao: float, dano_que_levo: float) -> tuple:
    """Quanto o MP de um lado compra até o fim previsto da luta.

    Dano e cura disputam o mesmo caixa — MP atual mais a regeneração da luta —
    na mesma moeda: oportunidades de vantagem. Uma skill de dano economiza
    `ganho / básico` das minhas; uma cura me dá `cura / básico_dele` das dele,
    menos a minha que ela gasta. A cura total não passa do dano que a luta vai
    me tirar. Gasto guloso pela vantagem por ponto de MP, no ritmo que a
    recarga permite. Devolve (dano extra, cura útil).
    """
    caixa = meu.mp + meu.regen * duracao
    opcoes = []
    for i, (ganho, custo, por_rodada, tipo, espera) in enumerate(meu.usos):
        if tipo == "dano":
            valor = ganho / meu.basico
        else:
            valor = meu.cura_por_uso[i] / dele.basico - 1
        if valor > 0:
            opcoes.append((valor / custo, i, custo, por_rodada * max(0.0, duracao - espera)))
    dano = cura = 0.0
    teto_de_cura = max(0.0, dano_que_levo)
    for _, i, custo, usos in sorted(opcoes, reverse=True):
        n = min(usos, caixa / custo)
        if meu.usos[i][3] == "cura":
            n = min(n, (teto_de_cura - cura) / meu.cura_por_uso[i])
        if n <= 0:
            continue
        caixa -= n * custo
        if meu.usos[i][3] == "dano":
            dano += n * meu.usos[i][0]
        else:
            cura += n * meu.cura_por_uso[i]
    return dano, cura


@dataclass(frozen=True)
class Leitura:
    """O valor de um estado para mim: chance de vitória e quanto falta para vencer."""

    vitoria: float
    rodadas: float  # oportunidades que eu ainda preciso para derrubar o outro

    def utilidade(self, impasse: float = 0.0) -> float:
        """P(vitória) menos o custo do tempo que ainda falta para vencer.

        Fora do impasse o tempo só desempata: quando a vitória já está decidida
        para um lado, é ele que ainda separa a ação que encerra a luta da que a
        arrasta — buff com o alvo a um golpe da morte. `t / (t + T)` satura, e
        perder é sempre o pior valor. No impasse (`impasse` de 0 a 1) entra um
        custo LINEAR no tempo, que não satura em luta longa: cada oportunidade a
        mais pesa o mesmo, e a cura que só mantém tudo onde está deixa de valer.
        Ele tem teto (`TETO_DO_IMPASSE`), e por isso perder continua o pior.
        """
        if math.isinf(self.rodadas):
            fracao, linear = 1.0, TETO_DO_IMPASSE
        else:
            fracao = self.rodadas / (self.rodadas + RODADAS_DE_REFERENCIA)
            linear = min(self.rodadas, TETO_DO_IMPASSE)
        return (
            self.vitoria
            - PESO_DO_TEMPO * fracao
            - impasse * PESO_DO_IMPASSE * linear / RODADAS_DE_REFERENCIA
        )


VITORIA = Leitura(1.0, 0.0)
DERROTA = Leitura(0.0, math.inf)


def corrida(eu, outro, incerteza: float = INCERTEZA_FINAL, procs: bool = True) -> dict:
    """A corrida das duas barras de HP a partir deste estado (os dois vivos).

    `T_eu` é quantas oportunidades eu preciso para derrubar o outro; `T_outro`,
    o contrário. A taxa de cada lado é o básico mais o DoT dos procs, menos o
    que o controle e o medo do outro tiram e o que o roubo de vida do outro
    devolve (`_taxa`). O HP a derrubar desconta o DoT que já está no alvo, o
    que os temporários ainda rendem e o que o MP compra em dano; soma o que o
    MP do outro compra em cura (`_vantagem_do_mp`, até o fim previsto: a menor
    das duas corridas). Controle ativo soma as oportunidades perdidas, e
    `death_ignore` não usado, um golpe. Quem tem a iniciativa leva meio turno.

    O desvio soma duas incertezas: a do dado (acerto, erro e crítico, que crescem
    com √T) e a do modelo (`incerteza`: o ritmo estimado erra em proporção).
    """
    meu, dele = _ritmo(eu, outro, procs), _ritmo(outro, eu, procs)
    minha_taxa, taxa_dele = _taxa(meu, dele), _taxa(dele, meu)
    hp_dele = outro.get_hp() - _dot_restante(outro) - meu.temporario
    hp_meu = eu.get_hp() - _dot_restante(eu) - dele.temporario

    def tempos(duracao: float) -> tuple[float, float]:
        meu_dano, minha_cura = _vantagem_do_mp(meu, dele, duracao, taxa_dele * duracao)
        dano_dele, cura_dele = _vantagem_do_mp(dele, meu, duracao, minha_taxa * duracao)
        return (
            max(0.0, hp_dele + cura_dele - meu_dano) / minha_taxa,
            max(0.0, hp_meu + minha_cura - dano_dele) / taxa_dele,
        )

    # A duração da luta é o ponto fixo `d = min(T_eu(d), T_outro(d))`: o MP
    # que cada um gasta depende de quanto a luta dura, e a luta dura menos
    # quanto mais MP se gasta. `min(T(d)) − d` é estritamente decrescente, então
    # a raiz é única e a bisseção a acha. Iterar `d ← min(T(d))` direto oscila
    # quando o MP sobra: ora a luta acaba já, ora dura o básico inteiro.
    baixo, alto = 0.0, max(1.0, min(tempos(0.0)))
    for _ in range(ITERACOES_DA_DURACAO):
        meio = (baixo + alto) / 2
        if min(tempos(meio)) > meio:
            baixo = meio
        else:
            alto = meio
    t_eu, t_outro = tempos(alto)
    t_eu += controle_restante(eu) + vidas_extras(outro)
    t_outro += controle_restante(outro) + vidas_extras(eu)
    vantagem = t_outro - t_eu + 0.5 * sinal_da_iniciativa(eu, outro)
    do_dado = t_eu * meu.variancia / meu.basico**2 + t_outro * dele.variancia / dele.basico**2
    return {
        "t_eu": t_eu,
        "t_outro": t_outro,
        "vantagem": vantagem,
        "desvio": math.sqrt(do_dado + (incerteza * t_eu) ** 2 + (incerteza * t_outro) ** 2 + 0.25),
        # O desvio só do dado, sem a incerteza do modelo: é o que a calibração
        # da incerteza precisa para refazer a conta com outro valor.
        "desvio_do_dado": math.sqrt(do_dado + 0.25),
    }


def avaliar_estado(eu, outro, incerteza: float = INCERTEZA_FINAL, procs: bool = True) -> Leitura:
    """A corrida (`corrida`) vira probabilidade pela normal."""
    if not outro.get_isalive() or outro.get_hp() <= 0:
        return VITORIA
    if not eu.get_isalive() or eu.get_hp() <= 0:
        return DERROTA
    c = corrida(eu, outro, incerteza, procs)
    vitoria = 0.5 * (1 + math.erf(c["vantagem"] / (c["desvio"] * math.sqrt(2))))
    return Leitura(vitoria, c["t_eu"])


def probabilidade_de_vitoria(eu, outro) -> float:
    return avaliar_estado(eu, outro).vitoria


def vidas_extras(heroi) -> int:
    """`death_ignore` ainda não usado: o golpe letal vira 1 de HP, uma vez."""
    if fx.combat_modifier(heroi, "death_ignore") <= 0:
        return 0
    return 0 if getattr(heroi, "_death_ignore_used", False) else 1


def sinal_da_iniciativa(eu, outro) -> int:
    """+1 se eu ajo primeiro na próxima rodada, −1 se não, 0 no empate absoluto."""
    a = read_initiative("eu", eu, outro, FOUNDATION_REFERENCES)
    b = read_initiative("outro", outro, eu, FOUNDATION_REFERENCES)
    if a.score != b.score:
        return 1 if a.score > b.score else -1
    if a.relative_ag != b.relative_ag:
        return 1 if a.relative_ag > b.relative_ag else -1
    return 0


# --- o gerador das simulações -------------------------------------------------------


class GeradorAlinhado:
    """O gerador de uma continuação: um fluxo por ORIGEM do sorteio.

    Com um gerador só, o que cada número sorteia depende da ordem das chamadas,
    e a ordem muda com a ação candidata — um buff não rola acerto, um golpe
    rola —, então o acerto do adversário na rodada 1 vira outro sorteio em cada
    candidata. Aqui cada sorteio vem do fluxo de (função do motor que sorteou,
    lado envolvido, rodada): o golpe do adversário na rodada 1 usa o MESMO
    número em todas as candidatas, e a diferença entre elas deixa de ser sorte.

    Só a origem muda; os números continuam uniformes e o motor é o mesmo. Os
    métodos são os que o duelo usa (`randrange`, `random`); qualquer outro
    levanta erro, como em `arena_auditoria.RngGravado`.
    """

    __slots__ = ("_semente", "_lados", "_fluxos", "rodada")

    def __init__(self, semente: int, lados: dict) -> None:
        self._semente = semente
        self._lados = lados  # id(herói) -> lado
        self._fluxos: dict = {}
        self.rodada = 0

    def _fluxo(self):
        quadro = sys._getframe(2)
        locais = quadro.f_locals
        quem = locais.get("attacker") or locais.get("target")
        chave = (quadro.f_code.co_name, self._lados.get(id(quem)), self.rodada)
        fluxo = self._fluxos.get(chave)
        if fluxo is None:
            fluxo = self._fluxos[chave] = random.Random(_semente(self._semente, *chave))
        return fluxo

    def randrange(self, *argumentos):
        return self._fluxo().randrange(*argumentos)

    def random(self):
        return self._fluxo().random()

    def __getattr__(self, nome):
        raise AttributeError(f"GeradorAlinhado não conhece {nome!r}")


# --- a política base (dentro das simulações) ------------------------------------


@dataclass
class PerfilDeAcoes:
    """O que a política base sabe de um lado, medido uma vez por decisão."""

    basico: float
    dano: dict = field(default_factory=dict)  # skill_id -> (média sem bônus, média com bônus)
    cura: dict = field(default_factory=dict)  # skill_id -> HP devolvido
    cartas: dict = field(default_factory=dict)  # skill_id -> carta


def perfil_de_acoes(heroi, outro) -> PerfilDeAcoes:
    perfil = PerfilDeAcoes(basico=golpe_esperado(heroi, outro).media)
    for skill in heroi.skills.values():
        perfil.cartas[skill.id] = skill
        if skill.effect_type == "damage":
            agora = golpe_esperado(heroi, outro, skill).media
            fator = 1 + int(getattr(skill, "bonus_percent", 0) or 0) / 100
            if combat.bonus_condition_met(heroi, skill, outro):
                perfil.dano[skill.id] = (agora / fator, agora)
            else:
                perfil.dano[skill.id] = (agora, agora * fator)
        elif skill.effect_type == "heal":
            perfil.cura[skill.id] = cura_esperada(heroi, skill)
    return perfil


def politica_base(duelo: Duel, lado: str, perfil: PerfilDeAcoes, rng, epsilon: float):
    """A política das simulações: cura quando aperta, senão o maior dano esperado.

    Barata de propósito — é chamada milhares de vezes por decisão. Não lança
    buff nem status: o valor dessas cartas é medido na raiz, onde a ação
    candidata é jogada no motor e o efeito dela aparece no estado. O bônus
    situacional da skill é conferido AGORA, contra o estado simulado: é o que
    deixa a simulação enxergar o combo status → dano.
    """
    legais = [a for a in duelo.legal_actions(lado) if a.kind != "surrender"]
    if epsilon and len(legais) > 1 and rng.random() < epsilon:
        return legais[rng.randrange(len(legais))]
    heroi = duelo.hero(lado)
    outro = duelo.hero(opponent_of(lado))
    skills = {a.skill_id: a for a in legais if a.kind == "skill"}
    if heroi.get_hp() / max(1, int(heroi.base_hp)) <= LIMIAR_DE_CURA_BASE:
        curas = [(perfil.cura[s], s) for s in skills if s in perfil.cura]
        if curas:
            return skills[max(curas)[1]]
    melhor, valor = DuelAction.attack(), perfil.basico
    for sid, acao in skills.items():
        if sid not in perfil.dano:
            continue
        sem, com = perfil.dano[sid]
        estimado = com if combat.bonus_condition_met(heroi, perfil.cartas[sid], outro) else sem
        if estimado > valor:
            melhor, valor = acao, estimado
    return melhor


# --- o modelo do adversário -------------------------------------------------------


@dataclass(frozen=True)
class PassivaInferida:
    """Um modificador que o modelo atribui ao adversário. Só existe na simulação."""

    effect_type: str
    effect_value: float
    id: str = "inferida"
    name: str = "inferida"


@dataclass
class _Rastro:
    """Um efeito ou buff visível no adversário: quanto ainda deve durar."""

    restante: float
    stacks: float = 1.0
    carta: object = None


def familia(efeito: str) -> str | None:
    definicao = core.definition(efeito)
    return None if definicao is None else definicao.family


class ModeloDoAdversario:
    """O adversário como a IA o imagina: priori canônica + o que a tela mostrou.

    A priori é o herói canônico da classe e do nível visíveis, com o loadout
    esperado. Ela é ajustada por três leituras, cada uma com pseudo-observações
    da priori (`PESO_DA_PRIORI`):

    - ofensa: o HP que eu perdi nas rodadas em que o outro NÃO gastou MP (logo,
      atacou no básico ou ficou parado), contra o que a priori previa;
    - defesa: o HP que ele perdeu para o meu golpe, contra o previsto;
    - cartas: quando o MP dele cai além da regeneração, o custo identifica as
      candidatas no catálogo público da classe; o desfecho da rodada (buff novo
      pelo nome, efeito novo em mim, HP dele subindo, meu HP caindo acima do
      básico) escolhe entre elas.
    """

    def __init__(
        self,
        classe: str,
        nivel: int,
        deck_de_referencia=(),
        modificadores_de_referencia=None,
        *,
        inferir: bool = True,
    ) -> None:
        # `make_hero` monta o herói pela camada de conteúdo, que pode sortear
        # pelo gerador global; o estado dele é devolvido intacto.
        estado = random.getstate()
        try:
            self.priori = make_hero(classe, nivel, "expected")
        finally:
            random.setstate(estado)
        self.priori.nick_name = "Modelo"
        self.pool = get_offer_pool(classe)
        pesos = CLASS_WEIGHTS.get(classe, {"st": 1.0, "mg": 0.0})
        self._peso_st = float(pesos.get("st", 1.0)) or 1.0
        self._peso_mg = float(pesos.get("mg", 0.0))
        # As cartas dele, antes de aparecerem, são SUPOSTAS: as da minha ficha
        # quando a classe é a mesma (o único deck de gladiador desta Arena que eu
        # conheço), senão a carta inicial da classe. Sem suposição nenhuma, ele
        # lutaria só de básico no modelo enquanto eu gasto quatro cartas, e a
        # corrida me daria vantagem que não existe. Cada carta revelada toma o
        # lugar de uma suposta, de preferência do mesmo tipo.
        referencia = list(deck_de_referencia) or list(self.priori.skills.values())
        self.deck = {s.id: s for s in referencia}
        self.supostas: set[str] = set(self.deck)
        self.reveladas: dict[str, str] = {}
        self.ultimo_uso: dict[str, int] = {}
        self.efeitos: dict[str, _Rastro] = {}
        self.buffs: dict[str, _Rastro] = {}
        self.inferir = inferir
        self.ofensa = [0.0, 0.0]  # Σ observado, Σ previsto pela priori
        self.defesa = [0.0, 0.0]
        # Roubo de vida, procs e regeneração: priori = o maior entre o canônico e
        # metade do meu; depois, o que a tela mostra.
        referencia_mod = modificadores_de_referencia or {}
        self.modificadores_priori = {
            m: max(
                fx.combat_modifier(self.priori, m),
                ENCOLHIMENTO_DA_REFERENCIA * float(referencia_mod.get(m, 0.0)),
            )
            for m in MODIFICADORES_INFERIDOS
        }
        self.procs_vistos: dict[str, list] = {e: [0, 0] for e in combat.ONHIT_PROCS}
        self.roubo_visto = [0.0, 0.0]  # Σ HP que ele ganhou batendo, Σ HP que eu perdi
        self.regen_vista: float | None = None

    # -- ajustes --

    @staticmethod
    def _razao(par, referencia: float) -> float:
        peso = PESO_DA_PRIORI * max(1.0, referencia)
        razao = (par[0] + peso) / (par[1] + peso)
        return max(FAIXA_DE_AJUSTE[0], min(FAIXA_DE_AJUSTE[1], razao))

    def fator_de_ofensa(self, referencia: float) -> float:
        return self._razao(self.ofensa, referencia)

    def fator_de_defesa(self, referencia: float) -> float:
        return self._razao(self.defesa, referencia)

    def regen_base(self, mp_max: int) -> int:
        return max(1, int(mp_max * MP_REGEN_PERCENT_PER_TURN / 100))

    def modificadores(self, eu, mp_max: int) -> dict[str, float]:
        """Roubo de vida, regeneração e procs estimados: priori + observação."""
        saida = dict(self.modificadores_priori)
        if self.regen_vista is not None:
            saida["mana_regen"] = max(0.0, self.regen_vista - self.regen_base(mp_max))
        for efeito, modificador in combat.ONHIT_PROCS.items():
            vistos, chances = self.procs_vistos[efeito]
            passa = max(0.01, 1 - fx.status_resistance(eu, efeito) / 100)
            priori = self.modificadores_priori[modificador] / 100 * passa
            pega = (vistos + PESO_DA_PRIORI * priori) / (chances + PESO_DA_PRIORI)
            saida[modificador] = 100 * pega / passa
        ganho, perdido = self.roubo_visto
        peso = PESO_DA_PRIORI * 100.0
        saida["life_steal"] = 100 * (
            (ganho + peso * self.modificadores_priori["life_steal"] / 100) / (perdido + peso)
        )
        return saida

    # -- leitura das cartas --

    def custo(self, skill) -> int:
        return combat.skill_mana_cost(self.priori, skill)

    def revelar(self, skill, como: str, rodada: int) -> None:
        if skill.id in self.supostas:
            self.supostas.discard(skill.id)
            self.reveladas[skill.id] = como
        elif skill.id not in self.deck:
            if self.supostas:
                mesmo_tipo = sorted(
                    s for s in self.supostas if self.deck[s].effect_type == skill.effect_type
                )
                saiu = mesmo_tipo[0] if mesmo_tipo else sorted(self.supostas)[0]
                self.supostas.discard(saiu)
                del self.deck[saiu]
                self.ultimo_uso.pop(saiu, None)
            self.deck[skill.id] = skill
            self.reveladas[skill.id] = como
        self.ultimo_uso[skill.id] = rodada

    def inferir_carta(self, custo: int, sinais: dict, rodada: int) -> str | None:
        """Qual carta custa `custo` e explica o que a rodada mostrou."""
        candidatas = [s for s in self.pool if self.custo(s) == custo]
        if not candidatas:
            return None
        for nome in sinais.get("buffs_novos", ()):
            carta = next((s for s in candidatas if s.name == nome), None)
            if carta is not None:
                self.revelar(carta, f"buff {nome} apareceu e o MP caiu {custo}", rodada)
                return carta.id
        filtradas: list = []
        for efeito in sinais.get("efeitos_novos_em_mim", ()):
            filtradas = [
                s
                for s in candidatas
                if (s.effect_type == "status" and str(s.effect_value) == efeito)
                or (getattr(s, "secondary", None) is not None and s.secondary.effect == efeito)
            ]
            if filtradas:
                break
        if not filtradas and sinais.get("curou"):
            filtradas = [s for s in candidatas if s.effect_type == "heal"]
        if not filtradas and sinais.get("golpe_forte"):
            filtradas = [s for s in candidatas if s.effect_type == "damage"]
        if not filtradas and len({s.effect_type for s in candidatas}) == 1:
            filtradas = candidatas
        if not filtradas:
            return None
        carta = sorted(filtradas, key=lambda s: s.id)[0]
        self.revelar(carta, f"MP caiu {custo}: {len(filtradas)} candidata(s) no catálogo", rodada)
        return carta.id

    # -- efeitos e buffs visíveis --

    def atualizar_visiveis(self, view, aplicados_por_mim: dict) -> None:
        """Rastreia duração e stacks do que está na tela do adversário."""
        visiveis = set(view.opponent.effects)
        for nome in list(self.efeitos):
            if nome not in visiveis:
                del self.efeitos[nome]
            else:
                self.efeitos[nome].restante -= 1
        for nome in visiveis:
            definicao = core.definition(nome)
            if definicao is None:
                continue
            if nome in aplicados_por_mim:
                duracao, chance = aplicados_por_mim[nome]
                rastro = self.efeitos.get(nome)
                if rastro is None:
                    self.efeitos[nome] = _Rastro(restante=duracao)
                else:
                    rastro.restante = max(rastro.restante, duracao)
                    if definicao.stack_rule == core.STACK_COUNT:
                        rastro.stacks = min(definicao.max_stacks, rastro.stacks + chance)
            elif nome not in self.efeitos:
                self.efeitos[nome] = _Rastro(restante=definicao.default_duration)
            self.efeitos[nome].restante = max(1.0, self.efeitos[nome].restante)

        buffs = set(view.opponent.buffs)
        for nome in list(self.buffs):
            if nome not in buffs:
                del self.buffs[nome]
            else:
                self.buffs[nome].restante -= 1
        for nome in buffs:
            if nome not in self.buffs:
                carta = next((s for s in self.pool if s.name == nome), None)
                duracao = int(getattr(carta, "duration", 0) or 3)
                self.buffs[nome] = _Rastro(restante=duracao, carta=carta)
            self.buffs[nome].restante = max(1.0, self.buffs[nome].restante)

    # -- o herói das simulações --

    def materializar(self, view, ofensa: float = 1.0, defesa: float = 1.0, eu=None):
        """Um herói de simulação com o que a tela mostra e o que se inferiu.

        `ofensa` e `defesa` são os fatores de ajuste; 1,0 é a priori pura. Os
        modificadores inferidos (`modificadores`) entram como passivas da
        simulação, pela mesma porta que o motor lê (`get_passive_bonus`).
        """
        outro = copy.deepcopy(self.priori)
        if eu is not None and self.inferir:
            outro.passives = list(outro.passives)
            for modificador, alvo in self.modificadores(eu, view.opponent.mp_max).items():
                falta = alvo - fx.combat_modifier(outro, modificador)
                if abs(falta) > 1e-9:
                    outro.passives.append(PassivaInferida(modificador, falta))
        visto = view.opponent
        outro.base_hp = visto.hp_max
        outro.base_mp = visto.mp_max
        st, mg = self.priori.base_st, self.priori.base_mg
        # O poder do Guerreiro é `1,6·ST + 0,4·MG`: para multiplicá-lo por `k`
        # mexendo só na Força, a Força leva também a parte da Magia.
        parte_da_magia = (ofensa - 1) * mg * self._peso_mg / self._peso_st
        outro.base_st = max(1, round(ofensa * st + parte_da_magia))
        alvo = DEFENSE_K / (DEFENSE_K + max(0, self.priori.base_df)) * defesa
        outro.base_df = max(0, round(DEFENSE_K / max(1e-6, alvo) - DEFENSE_K))
        outro._hp = int(visto.hp)
        outro._mp = int(visto.mp)
        outro.set_isalive(True)
        ordenadas = sorted(self.deck.values(), key=lambda s: s.id)
        outro.skills = {i: s for i, s in enumerate(ordenadas, 1)}
        outro.skill_cooldowns = {}
        for sid, rodada in self.ultimo_uso.items():
            carta = self.deck.get(sid)
            espera = int(getattr(carta, "cooldown", 0) or 0) + 1 - (view.round_number - 1 - rodada)
            if carta is not None and espera > 0:
                outro.skill_cooldowns[sid] = espera
        outro.active_effects = {}
        for nome, rastro in self.efeitos.items():
            duracao = max(1, round(rastro.restante))
            for _ in range(max(1, round(rastro.stacks))):
                core.apply_effect(outro, nome, source_id="ia", duration=duracao)
        outro.active_buffs = {}
        for nome, rastro in self.buffs.items():
            carta = rastro.carta
            if carta is None:
                continue
            if carta.effect_type == "damage_reduction":
                stat, valor = "damage_reduction", int(carta.effect_value)
            else:
                stat = str(carta.effect_stat or "")
                valor = fx.buff_value(outro, stat, int(carta.effect_value))
            duracao = max(1, round(rastro.restante))
            outro.active_buffs[nome] = {"stat": stat, "value": valor, "duration": duracao}
        outro._death_ignore_used = False
        return lembrar_ficha(outro)


# --- o controlador ---------------------------------------------------------------


def _semente(*partes) -> int:
    return zlib.crc32("|".join(str(p) for p in partes).encode("utf-8"))


def rotulo(acao: DuelAction, deck: dict) -> str:
    if acao.kind == "attack":
        return "ataque básico"
    if acao.kind == "surrender":
        return "rendição"
    carta = deck.get(acao.skill_id)
    return carta.name if carta is not None else str(acao.skill_id)


@dataclass
class Avaliacao:
    acao: DuelAction
    rotulo: str
    valor: float  # utilidade média (ver `Leitura`)
    erro: float  # erro-padrão dessa média
    custo: int
    vitoria: float = float("nan")  # P(vitória) média
    dano_medio: float = 0.0
    chance_letal: float = 0.0


def motivos_de_bloqueio(heroi, view) -> dict[str, str]:
    """Por que cada carta do deck NÃO está entre as ações legais desta visão.

    `requisito` (equipamento), `recarga` ou `mp` — a mesma ordem de
    `Duel._skill_problem`, lida só da visão e da ficha do próprio herói.
    """
    legais = {a.skill_id for a in view.legal_actions if a.kind == "skill"}
    recargas = dict(view.cooldowns)
    motivos = {}
    for skill in heroi.skills.values():
        if skill.id in legais:
            continue
        if not utilizavel(heroi, skill):
            motivos[skill.id] = "requisito"
        elif recargas.get(skill.id, 0) > 0:
            motivos[skill.id] = "recarga"
        else:
            motivos[skill.id] = "mp"
    return motivos


class IAEstrategica:
    """`DuelController` estratégico. Ver o docstring do módulo."""

    def __init__(self, heroi, config: Configuracao | None = None) -> None:
        self._heroi = heroi
        self._deck = {s.id: s for s in heroi.skills.values()}
        self.config = config or Configuracao()
        # A política antiga, só para registro: o que ela teria feito na mesma
        # visão. Ela não influencia a escolha.
        self._referencia = PoliticaCopa(heroi)
        self._modelo: ModeloDoAdversario | None = None
        self._incerteza = self.config.incerteza_inicial
        self._impasse = 0.0
        self._recordes: dict[str, float] = {}
        self._ultimo_progresso = 1
        self._anterior: dict | None = None
        self.last_reason = ""
        self.last_decision: dict = {}
        self.decisoes: list[dict] = []

    # -- a observação da rodada que passou --

    def _observar(self, view) -> None:
        if self._modelo is None:
            mesma_classe = view.opponent.class_name == view.me.class_name
            self._modelo = ModeloDoAdversario(
                view.opponent.class_name,
                view.opponent.level,
                list(self._deck.values()) if mesma_classe else (),
                {m: fx.combat_modifier(self._heroi, m) for m in MODIFICADORES_INFERIDOS}
                if mesma_classe
                else None,
                inferir=self.config.inferir_modificadores,
            )
        modelo = self._modelo
        antes = self._anterior
        modelo.atualizar_visiveis(view, antes["aplicaria"] if antes else {})
        if antes is None:
            return
        v0 = antes["view"]
        estimados = modelo.modificadores(self._heroi, v0.opponent.mp_max)
        regen = modelo.regen_base(v0.opponent.mp_max) + int(estimados["mana_regen"])
        gasto = min(v0.opponent.mp + regen, v0.opponent.mp_max) - view.opponent.mp
        perdi = max(0, v0.me.hp - view.me.hp + antes["minha_cura"] - antes["meu_dot"])
        perdeu = v0.opponent.hp - view.opponent.hp - antes["dot_dele"]
        sinais = {
            "buffs_novos": [b for b in view.opponent.buffs if b not in v0.opponent.buffs],
            "efeitos_novos_em_mim": [e for e in view.me.effects if e not in v0.me.effects],
            "curou": view.opponent.hp > v0.opponent.hp,
            "golpe_forte": perdi > 1.6 * max(1.0, antes["basico_dele"]),
        }
        dele_controlado = any(familia(e) == core.FAMILY_CONTROL for e in v0.opponent.effects)
        if gasto > 1:
            modelo.inferir_carta(int(gasto), sinais, v0.round_number)
        elif not dele_controlado:
            modelo.ofensa[0] += perdi
            modelo.ofensa[1] += antes["basico_dele"]
            # O que o MP dele sobe sem lançar nada é a regeneração inteira dele.
            subiu = view.opponent.mp - v0.opponent.mp
            if subiu > 0 and view.opponent.mp < view.opponent.mp_max:
                modelo.regen_vista = max(modelo.regen_vista or 0, subiu)
            if perdi > 0:
                # Ele me acertou sem carta: o que pegou em mim veio do acerto.
                for efeito in combat.ONHIT_PROCS:
                    if efeito not in v0.me.effects:
                        modelo.procs_vistos[efeito][1] += 1
                        modelo.procs_vistos[efeito][0] += efeito in view.me.effects
                if not antes["executei_dano"] and v0.opponent.hp < v0.opponent.hp_max:
                    ganhou = view.opponent.hp - v0.opponent.hp + antes["dot_dele"]
                    modelo.roubo_visto[0] += max(0, ganhou)
                    modelo.roubo_visto[1] += perdi
        if antes["executei_dano"] and not sinais["curou"]:
            modelo.defesa[0] += max(0, perdeu)
            modelo.defesa[1] += antes["meu_dano"]

    # -- a escolha --

    def choose(self, view):
        self._observar(view)
        legais = [a for a in view.legal_actions if a.kind != "surrender"]
        referencia = self._referencia.choose(view)
        eu = para_simulacao(self._heroi)
        modelo = self._modelo
        priori = modelo.materializar(view, eu=eu)
        basico_dele = golpe_esperado(priori, eu).media
        meu_dano = max(self._dano_da_acao(eu, priori, a) for a in legais)
        k_ofensa = modelo.fator_de_ofensa(basico_dele)
        k_defesa = modelo.fator_de_defesa(meu_dano)
        outro = modelo.materializar(view, k_ofensa, k_defesa, eu=eu)
        self._incerteza = self.config.incerteza(view.round_number - 1)
        self._impasse = self._medir_impasse(view)

        if len(legais) == 1:
            escolhida = Avaliacao(legais[0], rotulo(legais[0], self._deck), float("nan"), 0.0, 0)
            avaliacoes = [escolhida]
            bloqueios = motivos_de_bloqueio(self._heroi, view)
            self.last_reason = (
                "só o básico é legal ("
                + ", ".join(f"{self._deck[s].name}: {m}" for s, m in sorted(bloqueios.items()))
                + ")"
            )
        else:
            avaliacoes = self._avaliar(view, eu, outro, legais)
            escolhida = self._melhor(avaliacoes)
            self.last_reason = self._explicar(escolhida, avaliacoes)

        acao = escolhida.acao
        self.last_decision = {
            "rodada": view.round_number,
            "hp": [view.me.hp, view.me.hp_max],
            "mp": [view.me.mp, view.me.mp_max],
            "hp_dele": [view.opponent.hp, view.opponent.hp_max],
            "mp_dele": [view.opponent.mp, view.opponent.mp_max],
            "efeitos_dele": list(view.opponent.effects),
            "buffs": list(view.me.buffs),
            "acao": escolhida.rotulo,
            "motivo": self.last_reason,
            "avaliacoes": [
                {
                    "acao": a.rotulo,
                    "p": None if math.isnan(a.vitoria) else round(a.vitoria, 4),
                    "utilidade": None if math.isnan(a.valor) else round(a.valor, 4),
                    "erro": round(a.erro, 4),
                    "custo": a.custo,
                    "dano_medio": round(a.dano_medio, 1),
                    "chance_letal": round(a.chance_letal, 4),
                }
                for a in avaliacoes
            ],
            "corrida_na_raiz": {
                k: round(v, 4)
                for k, v in corrida(
                    eu, outro, self._incerteza, self.config.procs_na_corrida
                ).items()
            },
            "politica_copa": rotulo(referencia, self._deck),
            "motivo_politica_copa": self._referencia.last_reason,
            "modelo": {
                "fator_ofensa": round(k_ofensa, 3),
                "fator_defesa": round(k_defesa, 3),
                "st_estimada": outro.get_st(),
                "df_estimada": outro.get_df(),
                "cartas_reveladas": sorted(modelo.deck[s].name for s in modelo.reveladas),
                "modificadores": {
                    m: round(v, 2)
                    for m, v in modelo.modificadores(eu, view.opponent.mp_max).items()
                },
                "incerteza": round(self._incerteza, 3),
                "impasse": round(self._impasse, 3),
            },
        }
        self.decisoes.append(self.last_decision)
        self._lembrar(view, acao, eu, priori)
        return acao

    def _medir_impasse(self, view) -> float:
        """0 enquanto a luta anda; até 1 numa janela parada ou numa luta longa."""
        for quem, lutador in (("eu", view.me), ("ele", view.opponent)):
            fracao = lutador.hp / max(1, lutador.hp_max)
            if fracao < self._recordes.get(quem, 1.0) - PROGRESSO_MINIMO:
                self._recordes[quem] = fracao
                self._ultimo_progresso = view.round_number
        parado = (view.round_number - self._ultimo_progresso - JANELA_SEM_PROGRESSO) / (
            JANELA_SEM_PROGRESSO
        )
        longa = (view.round_number - INICIO_DA_LUTA_LONGA) / INICIO_DA_LUTA_LONGA
        return max(0.0, min(1.0, max(parado, longa)))

    def _dano_da_acao(self, eu, outro, acao) -> float:
        if acao.kind == "attack":
            return golpe_esperado(eu, outro).media
        carta = self._deck[acao.skill_id]
        if carta.effect_type == "damage":
            return golpe_esperado(eu, outro, carta).media
        return 0.0

    def _lembrar(self, view, acao, eu, priori) -> None:
        """O que a próxima observação precisa saber desta rodada.

        As previsões são feitas contra a PRIORI, não contra o modelo ajustado:
        é a razão observado/priori que o ajuste acumula.
        """
        carta = self._deck.get(acao.skill_id) if acao.kind == "skill" else None
        aplicaria = {}
        if carta is not None and carta.effect_type == "status":
            aplicaria[str(carta.effect_value)] = (int(carta.duration), int(carta.chance) / 100)
        secundario = getattr(carta, "secondary", None) if carta is not None else None
        if secundario is not None and core.definition(secundario.effect) is not None:
            duracao = secundario.duration or core.definition(secundario.effect).default_duration
            aplicaria[secundario.effect] = (duracao, secundario.chance / 100)
        cura = 0
        if carta is not None and carta.effect_type == "heal":
            cura = min(cura_esperada(eu, carta), int(eu.base_hp) - eu.get_hp())
        dano = acao.kind == "attack" or (carta is not None and carta.effect_type == "damage")
        self._anterior = {
            "view": view,
            "aplicaria": aplicaria,
            "minha_cura": cura,
            "meu_dot": dot_por_tick(eu),
            "dot_dele": dot_por_tick(priori),
            "basico_dele": golpe_esperado(priori, eu).media,
            "executei_dano": dano and controle_restante(eu) == 0,
            "meu_dano": self._dano_da_acao(eu, priori, acao),
        }

    def _avaliar(self, view, eu, outro, legais) -> list[Avaliacao]:
        cfg = self.config
        n = cfg.rollouts_criticos if self._momento_critico(eu, outro, legais) else cfg.rollouts
        sementes = [
            _semente(view.me.name, view.round_number, view.me.hp, view.opponent.hp, view.me.mp, i)
            for i in range(n)
        ]
        perfis = {"p1": perfil_de_acoes(eu, outro), "p2": perfil_de_acoes(outro, eu)}
        avaliacoes = []
        for acao in legais:
            leituras = [self._continuar(eu, outro, acao, s, perfis) for s in sementes]
            amostras = [x.utilidade(self._impasse) for x in leituras]
            media = sum(amostras) / n
            erro = math.sqrt(sum((x - media) ** 2 for x in amostras) / max(1, n - 1) / n)
            vitoria = sum(x.vitoria for x in leituras) / n
            carta = self._deck.get(acao.skill_id) if acao.kind == "skill" else None
            golpe = None
            if acao.kind == "attack":
                golpe = golpe_esperado(eu, outro)
            elif carta.effect_type == "damage":
                golpe = golpe_esperado(eu, outro, carta)
            avaliacoes.append(
                Avaliacao(
                    acao,
                    rotulo(acao, self._deck),
                    media,
                    erro,
                    combat.skill_mana_cost(eu, carta) if carta is not None else 0,
                    vitoria,
                    golpe.media if golpe else 0.0,
                    golpe.chance_de_derrubar(outro.get_hp()) if golpe else 0.0,
                )
            )
        return avaliacoes

    def _momento_critico(self, eu, outro, legais) -> bool:
        maior = golpe_esperado(eu, outro).forte
        for a in legais:
            carta = self._deck.get(a.skill_id) if a.kind == "skill" else None
            if carta is not None and carta.effect_type == "damage":
                maior = max(maior, golpe_esperado(eu, outro, carta).forte)
        return outro.get_hp() <= 1.5 * maior or eu.get_hp() <= 1.5 * golpe_esperado(outro, eu).forte

    def _continuar(self, eu, outro, acao, semente, perfis) -> Leitura:
        """Uma continuação no motor: a candidata agora, a política base depois."""
        a, b = copia_de_combate(eu), copia_de_combate(outro)
        marcas = (a._death_ignore_used, b._death_ignore_used)
        gerador = GeradorAlinhado(semente, {id(a): "p1", id(b): "p2"})
        duelo = Duel(Gladiator(a), Gladiator(b), rng=gerador)
        # O duelo zera `death_ignore` na entrada; a simulação continua o atual.
        a._death_ignore_used, b._death_ignore_used = marcas
        for passo in range(self.config.horizonte):
            if duelo.finished:
                break
            gerador.rodada = passo
            minha = acao
            if passo:
                politica = random.Random(_semente(semente, "politica", "p1", passo))
                minha = politica_base(duelo, "p1", perfis["p1"], politica, 0.0)
            politica = random.Random(_semente(semente, "politica", "p2", passo))
            dele = politica_base(duelo, "p2", perfis["p2"], politica, self.config.epsilon)
            duelo.play_round({"p1": minha, "p2": dele})
        if duelo.finished:
            return VITORIA if duelo.result.winner == "p1" else DERROTA
        return avaliar_estado(a, b, self._incerteza, self.config.procs_na_corrida)

    @staticmethod
    def _melhor(avaliacoes: list[Avaliacao]) -> Avaliacao:
        """A maior utilidade média. No empate exato, o básico, depois o deck.

        Custo NÃO desempata: o MP já está na utilidade, pelo que ele ainda
        compraria até o fim da luta. Preferir a ação mais barata sempre que a
        diferença é pequena faz exatamente o que não se quer — guardar MP que
        não vai faltar até ele bater no teto e a regeneração se perder.
        """
        return max(enumerate(avaliacoes), key=lambda par: (par[1].valor, -par[0]))[1]

    @staticmethod
    def _explicar(escolhida: Avaliacao, avaliacoes: list[Avaliacao]) -> str:
        outras = sorted((a for a in avaliacoes if a is not escolhida), key=lambda a: -a.valor)
        partes = [f"P(vitória) {escolhida.vitoria:.3f}±{escolhida.erro:.3f} com {escolhida.rotulo}"]
        if outras:
            partes.append("contra " + ", ".join(f"{a.rotulo} {a.vitoria:.3f}" for a in outras[:3]))
        if escolhida.dano_medio:
            partes.append(f"dano esperado {escolhida.dano_medio:.0f}")
        if escolhida.chance_letal:
            partes.append(f"chance de derrubar já {escolhida.chance_letal:.0%}")
        if escolhida.custo:
            partes.append(f"custa {escolhida.custo} MP")
        return "; ".join(partes)
