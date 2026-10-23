"""Duelo da Arena: dois heróis, decisões simultâneas, resolução sequencial.

`battle.run_battle` continua sendo o combate do PvE — herói contra monstro,
ordem fixa por AG, teto de turnos — e não é tocado. O duelo é uma orquestração
PRÓPRIA por cima das MESMAS regras: o golpe é `combat.resolve_physical_attack`,
a skill é `combat.apply_skill` e o começo da oportunidade é
`combat.process_turn_start_effects`. Não existe segundo resolvedor de dano, de
efeito, de recarga ou de mana.

Uma rodada:

    P1 escolhe ── P2 escolhe          (nenhum vê a escolha do outro)
          VALIDAÇÃO das duas          (nada muda se uma for ilegal)
          RENDIÇÃO                    (derrota imediata, antes de qualquer golpe)
          RESERVA de MP               (o custo da skill sai do MP livre)
          LOCK
          INICIATIVA → ORDEM TRAVADA  (recalculada a cada rodada)
          para cada lado, na ordem:
              início da oportunidade  (recarga, regeneração, DoT, dreno,
                                       controle e buffs: o mesmo do PvE)
              morto?        → a ação é cancelada e o duelo acaba
              controlado?   → a ação é cancelada; a reserva volta
              senão         → a ação resolve contra o estado ATUAL
          primeira morte → fim imediato; a ação pendente do outro não acontece

Duas decisões de modelagem que valem para todo o resto:

- **Durações contam oportunidades do PORTADOR**, como no PvE: o começo da
  oportunidade é o mesmo `process_turn_start_effects`. Um `stun` de duração 1
  rouba exatamente uma oportunidade — a desta rodada, se chegou antes da ação
  pendente; a da próxima, se o portador já tinha agido.
- **A reserva é MP fora do caixa.** No lock o custo sai de `_mp` e fica
  guardado no duelo. Tudo que lê ou drena mana no meio da rodada — `mana_burn`,
  Égide — só alcança o MP livre. Na execução a reserva volta ao caixa no
  instante em que `apply_skill` a cobra: uma cobrança só, pelo caminho de
  sempre. Ação cancelada devolve a reserva (sem penalidade extra).

O motor não tem laço interno nem teto de rodadas: `play_round` resolve UMA
rodada, e quem conduz o duelo (UI, rede, bot, teste) decide quando chamar a
próxima. Também não conhece teclado, rede, relógio nem interface: timeout e
desconexão chegam por `forfeit`.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from src.mechanics import combat as combat_mech
from src.mechanics.pvp_initiative import (
    InitiativeOrder,
    InitiativeReading,
    InitiativeReferences,
    TieBreakPolicy,
    order_by_initiative,
    read_initiative,
)
from src.shared import effect_core as core

SIDES = ("p1", "p2")

DuelActionKind = Literal["attack", "skill", "surrender"]
DUEL_ACTION_KINDS = ("attack", "skill", "surrender")

EndReason = Literal["ko", "surrender", "timeout", "disconnect"]
# Os desfechos que chegam de FORA do motor: o relógio e a conexão são da camada
# de cima. Rendição é ação do duelo, e KO é o próprio combate.
EXTERNAL_END_REASONS = ("timeout", "disconnect")

StepOutcome = Literal["executed", "cancelled_control", "cancelled_death", "not_reached"]


class InvalidDuelActionError(ValueError):
    """A ação não pode ser travada. Nada no duelo mudou."""


class DuelFinishedError(RuntimeError):
    """O duelo já tem resultado: não há rodada nem desfecho novo."""


def opponent_of(side: str) -> str:
    if side not in SIDES:
        raise ValueError(f"Lado desconhecido: {side!r}")
    return SIDES[1] if side == SIDES[0] else SIDES[0]


@dataclass(frozen=True, slots=True)
class DuelAction:
    """A decisão de um lado numa rodada.

    A skill é nomeada pelo `id`, e não pelo objeto: um controlador remoto manda
    texto, e o motor resolve o id contra o deck do PRÓPRIO gladiador.
    Consumível e fuga não existem aqui — não há como pedi-los.
    """

    kind: DuelActionKind
    skill_id: str | None = None

    @classmethod
    def attack(cls) -> "DuelAction":
        return cls("attack")

    @classmethod
    def use_skill(cls, skill_id: str) -> "DuelAction":
        return cls("skill", str(skill_id))

    @classmethod
    def surrender(cls) -> "DuelAction":
        return cls("surrender")


@dataclass(frozen=True)
class Gladiator:
    """Um herói pronto para o duelo: instância própria, que o duelo pode ferir.

    Quem cria é a preparação (`content/gladiator.prepare_gladiator`), que parte
    de uma extração válida e devolve uma cópia normalizada. O snapshot salvo
    nunca entra no duelo.
    """

    hero: Any

    @property
    def name(self) -> str:
        return str(self.hero.get_nick_name())


@dataclass(frozen=True)
class FighterView:
    """O que se vê de um gladiador entre rodadas."""

    name: str
    class_name: str
    level: int
    hp: int
    hp_max: int
    mp: int
    mp_max: int
    effects: tuple[str, ...]
    buffs: tuple[str, ...]


@dataclass(frozen=True)
class DuelView:
    """Tudo o que um controlador recebe para decidir.

    Montada ANTES de qualquer escolha da rodada, e imutável: não carrega o
    duelo, o adversário nem a ação dele. A iniciativa também não está aqui —
    ela fica fora da UI normal.

    `cooldowns` são as oportunidades que cada carta ainda espera, contadas a
    partir da próxima oportunidade deste lado.
    """

    round_number: int
    side: str
    me: FighterView
    opponent: FighterView
    legal_actions: tuple[DuelAction, ...]
    cooldowns: tuple[tuple[str, int], ...]


class DuelController(Protocol):
    """Quem decide por um lado: humano remoto, bot ou script de teste."""

    def choose(self, view: DuelView) -> DuelAction: ...


@dataclass(frozen=True)
class DuelEvent:
    """Um fato do duelo, em dado puro, para observabilidade e replay."""

    round_number: int
    name: str
    side: str | None = None
    detail: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class StepRecord:
    """O que aconteceu com a ação de um lado dentro da rodada."""

    side: str
    action: DuelAction
    outcome: StepOutcome
    mp_reserved: int = 0
    mp_spent: int = 0
    damage_to_opponent: int = 0


@dataclass(frozen=True)
class RoundRecord:
    """Uma rodada resolvida: ações travadas, ordem, passos e o estado final.

    `initiative` é registro de auditoria, não informação de tela.
    """

    number: int
    actions: tuple[tuple[str, DuelAction], ...]
    initiative: tuple[InitiativeReading, InitiativeReading]
    order: InitiativeOrder
    steps: tuple[StepRecord, ...]
    hp_end: tuple[tuple[str, int], ...]
    mp_end: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class DuelResult:
    """O desfecho do duelo. MD1: não há empate nem segunda partida."""

    winner: str
    loser: str
    winner_name: str
    loser_name: str
    reason: EndReason
    rounds: int
    history: tuple[RoundRecord, ...] = field(default=(), repr=False)


def _deck_skill(hero, skill_id: str | None):
    for skill in getattr(hero, "skills", {}).values():
        if getattr(skill, "id", None) == skill_id:
            return skill
    return None


def _cooldown_at_next_opportunity(hero, skill_id: str) -> int:
    """Oportunidades que a carta ainda espera, vistas do lock.

    A recarga é decrementada no começo da oportunidade, antes de agir — a regra
    do PvE (`process_turn_start_effects`). Por isso, no lock, a carta com 1 de
    recarga restante já estará livre quando a ação dela resolver.
    """
    return max(0, int(getattr(hero, "skill_cooldowns", {}).get(skill_id, 0)) - 1)


def _dead(hero) -> bool:
    return not hero.get_isalive() or hero.get_hp() <= 0


def _fighter_view(hero) -> FighterView:
    return FighterView(
        name=str(hero.get_nick_name()),
        class_name=str(hero.get_classname()),
        level=int(hero.get_level()),
        hp=int(hero.get_hp()),
        hp_max=int(hero.base_hp),
        mp=int(hero.get_mp()),
        mp_max=int(hero.base_mp),
        effects=tuple(sorted(i.effect for i in core.instances(hero))),
        buffs=tuple(sorted(str(nome) for nome in getattr(hero, "active_buffs", {}))),
    )


class Duel:
    """Um duelo MD1 entre dois gladiadores preparados.

    `references` e `tie_break` são obrigatórios e injetados: os valores das
    referências de iniciativa e a regra do empate absoluto ainda não foram
    aprovados, e o motor não escolhe nenhum dos dois por conta própria.

    `rng` é o gerador do duelo inteiro — acerto, crítico, status e desempate.
    Passe `random.Random(seed)` para reproduzir um duelo.
    """

    def __init__(
        self,
        p1: Gladiator,
        p2: Gladiator,
        *,
        references: InitiativeReferences,
        tie_break: TieBreakPolicy,
        rng: random.Random | None = None,
        publish: Callable | None = None,
    ) -> None:
        if not isinstance(p1, Gladiator) or not isinstance(p2, Gladiator):
            raise TypeError("O duelo recebe gladiadores preparados (`Gladiator`).")
        if p1.hero is p2.hero:
            raise ValueError("Os dois lados apontam para a MESMA instância de herói.")
        for gladiador in (p1, p2):
            if _dead(gladiador.hero):
                raise ValueError(f"{gladiador.name} não está em condição de lutar.")

        self._heroes = {SIDES[0]: p1.hero, SIDES[1]: p2.hero}
        self._references = references
        self._tie_break = tie_break
        self._rng = rng if rng is not None else random.Random()
        self._publish = publish
        self._round = 1
        self._history: list[RoundRecord] = []
        self._events: list[DuelEvent] = []
        self._result: DuelResult | None = None

        # `death_ignore` vale uma vez por COMBATE: a marca é zerada na entrada,
        # como `run_battle` faz no PvE.
        for heroi in self._heroes.values():
            heroi._death_ignore_used = False

    # --- leitura -----------------------------------------------------------

    @property
    def round_number(self) -> int:
        """A rodada que será jogada a seguir (ou a última, se acabou)."""
        return self._round

    @property
    def finished(self) -> bool:
        return self._result is not None

    @property
    def result(self) -> DuelResult | None:
        return self._result

    @property
    def history(self) -> tuple[RoundRecord, ...]:
        return tuple(self._history)

    @property
    def events(self) -> tuple[DuelEvent, ...]:
        return tuple(self._events)

    def hero(self, side: str):
        """A instância de duelo de um lado. Para inspeção; não é o snapshot."""
        opponent_of(side)
        return self._heroes[side]

    def legal_actions(self, side: str) -> tuple[DuelAction, ...]:
        """As ações que este lado pode travar na próxima rodada."""
        self._ensure_running()
        heroi = self.hero(side)
        acoes = [DuelAction.attack()]
        for skill in heroi.skills.values():
            if self._skill_problem(heroi, skill) is None:
                acoes.append(DuelAction.use_skill(skill.id))
        acoes.append(DuelAction.surrender())
        return tuple(acoes)

    def view(self, side: str) -> DuelView:
        """A visão deste lado, montada sem nada da escolha do outro."""
        heroi = self.hero(side)
        recargas = tuple(
            (skill.id, _cooldown_at_next_opportunity(heroi, skill.id))
            for skill in heroi.skills.values()
        )
        return DuelView(
            round_number=self._round,
            side=side,
            me=_fighter_view(heroi),
            opponent=_fighter_view(self.hero(opponent_of(side))),
            legal_actions=self.legal_actions(side),
            cooldowns=recargas,
        )

    # --- desfechos externos ------------------------------------------------

    def forfeit(self, side: str, reason: EndReason) -> DuelResult:
        """Derrota decidida fora do combate: timeout ou desconexão."""
        self._ensure_running()
        if reason not in EXTERNAL_END_REASONS:
            raise ValueError(f"Desfecho externo desconhecido: {reason!r}")
        return self._finish(winner=opponent_of(side), reason=reason)

    # --- a rodada ----------------------------------------------------------

    def play_round(self, actions: Mapping[str, DuelAction]) -> RoundRecord:
        """Resolve UMA rodada com as ações dos dois lados.

        Valida as duas antes de mudar qualquer coisa: uma ação ilegal levanta
        `InvalidDuelActionError` e o duelo continua exatamente como estava.
        """
        self._ensure_running()
        if set(actions) != set(SIDES):
            raise InvalidDuelActionError(f"A rodada exige uma ação de cada lado: {SIDES}.")
        travadas = {lado: actions[lado] for lado in SIDES}
        for lado in SIDES:
            self._validate(lado, travadas[lado])

        numero = self._round
        if any(travadas[lado].kind == "surrender" for lado in SIDES):
            return self._resolve_surrender(numero, travadas)

        reservas = {lado: self._reserve(lado, travadas[lado]) for lado in SIDES}
        self._event(
            numero,
            "actions_locked",
            detail=tuple((lado, travadas[lado]) for lado in SIDES),
        )
        leituras, ordem = self._initiative()
        sequencia = (ordem.first, ordem.second)
        self._event(numero, "order_locked", detail=(("order", sequencia), ("by", ordem.decided_by)))

        passos: list[StepRecord] = []
        for lado in sequencia:
            if self._result is not None:
                # A primeira morte encerrou o duelo: a ação pendente não acontece.
                # Se quem morreu foi o dono dela, ela foi cancelada pela morte;
                # se foi o outro, o duelo simplesmente acabou antes da vez dela.
                reservado = reservas[lado]
                self._refund(lado, reservas, numero)
                desfecho: StepOutcome = (
                    "cancelled_death" if _dead(self.hero(lado)) else "not_reached"
                )
                if desfecho == "cancelled_death":
                    self._event(numero, "action_cancelled", lado, (("cause", "death"),))
                passos.append(StepRecord(lado, travadas[lado], desfecho, reservado))
                continue
            passos.append(self._opportunity(numero, lado, travadas[lado], reservas))

        registro = self._record(numero, travadas, leituras, ordem, passos)
        if self._result is None:
            self._round += 1
        return registro

    def _initiative(self) -> tuple[tuple[InitiativeReading, InitiativeReading], InitiativeOrder]:
        """Lê a iniciativa dos dois lados AGORA e trava a ordem da rodada.

        No início da resolução, antes de qualquer oportunidade: o que a rodada
        mudar só vale para a ordem da próxima.
        """
        leituras = tuple(
            read_initiative(lado, self.hero(lado), self.hero(opponent_of(lado)), self._references)
            for lado in SIDES
        )
        ordem = order_by_initiative(leituras[0], leituras[1], self._tie_break, self._rng)
        return leituras, ordem

    # --- validação e reserva -----------------------------------------------

    def _skill_problem(self, heroi, skill) -> str | None:
        """Por que a carta não pode ser travada agora; `None` se pode."""
        verificador = getattr(heroi, "can_use_skill", None)
        if callable(verificador) and not verificador(skill):
            return "requisito de equipamento não atendido"
        if _cooldown_at_next_opportunity(heroi, skill.id) > 0:
            return "em recarga"
        if combat_mech.skill_mana_cost(heroi, skill) > heroi.get_mp():
            return "MP livre insuficiente"
        return None

    def _validate(self, lado: str, acao) -> None:
        if not isinstance(acao, DuelAction) or acao.kind not in DUEL_ACTION_KINDS:
            raise InvalidDuelActionError(
                f"{lado}: ação fora do duelo ({acao!r}). Na Arena só existem ataque "
                "básico, skill do deck e rendição — sem consumível e sem fuga."
            )
        if acao.kind != "skill":
            return
        skill = _deck_skill(self.hero(lado), acao.skill_id)
        if skill is None:
            raise InvalidDuelActionError(f"{lado}: {acao.skill_id!r} não está no deck.")
        problema = self._skill_problem(self.hero(lado), skill)
        if problema is not None:
            raise InvalidDuelActionError(f"{lado}: {acao.skill_id!r} — {problema}.")

    def _reserve(self, lado: str, acao: DuelAction) -> int:
        if acao.kind != "skill":
            return 0
        heroi = self.hero(lado)
        custo = combat_mech.skill_mana_cost(heroi, _deck_skill(heroi, acao.skill_id))
        heroi._mp = heroi.get_mp() - custo
        self._event(self._round, "mp_reserved", lado, (("amount", custo),))
        return custo

    def _refund(self, lado: str, reservas: dict[str, int], numero: int) -> None:
        quanto = reservas.get(lado, 0)
        if quanto <= 0:
            return
        heroi = self.hero(lado)
        heroi._mp = min(int(heroi.base_mp), heroi.get_mp() + quanto)
        reservas[lado] = 0
        self._event(numero, "mp_refunded", lado, (("amount", quanto),))

    @staticmethod
    def _clamp_free_mp(heroi, reservado: int) -> None:
        """A regeneração enche o caixa até o teto MENOS o que está reservado.

        `process_turn_start_effects` corta a mana em `base_mp` sem saber da
        reserva. Sem este corte, regenerar com a barra cheia valeria mana
        acima do teto assim que a reserva voltasse.
        """
        teto_livre = max(0, int(heroi.base_mp) - reservado)
        if heroi.get_mp() > teto_livre:
            heroi._mp = teto_livre

    # --- a oportunidade ----------------------------------------------------

    def _opportunity(
        self, numero: int, lado: str, acao: DuelAction, reservas: dict[str, int]
    ) -> StepRecord:
        heroi = self.hero(lado)
        adversario = self.hero(opponent_of(lado))
        reservado = reservas[lado]

        controlado = combat_mech.process_turn_start_effects(
            heroi, rng=self._rng, publish=self._publish
        )
        self._clamp_free_mp(heroi, reservado)

        if _dead(heroi):
            heroi.set_isalive(False)
            self._refund(lado, reservas, numero)
            self._event(numero, "action_cancelled", lado, (("cause", "death"),))
            self._finish(winner=opponent_of(lado), reason="ko")
            return StepRecord(lado, acao, "cancelled_death", reservado)

        if controlado:
            self._refund(lado, reservas, numero)
            self._event(numero, "action_cancelled", lado, (("cause", "control"),))
            return StepRecord(lado, acao, "cancelled_control", reservado)

        # Libera a reserva no instante da cobrança: `apply_skill` debita o
        # custo pelo caminho de sempre, e a mana é cobrada uma única vez.
        heroi._mp = heroi.get_mp() + reservado
        reservas[lado] = 0
        mp_antes = heroi.get_mp()
        hp_antes = adversario.get_hp()

        if acao.kind == "skill":
            combat_mech.apply_skill(
                heroi,
                adversario,
                _deck_skill(heroi, acao.skill_id),
                rng=self._rng,
                publish=self._publish,
            )
        else:
            combat_mech.resolve_physical_attack(
                heroi,
                adversario,
                combat_mech.basic_attack_power(heroi),
                rng=self._rng,
                publish=self._publish,
            )

        gasto = max(0, mp_antes - heroi.get_mp())
        dano = max(0, hp_antes - adversario.get_hp())
        self._event(
            numero,
            "action_executed",
            lado,
            (("action", acao), ("mp_spent", gasto), ("damage", dano)),
        )

        if _dead(adversario):
            adversario.set_isalive(False)
            self._finish(winner=lado, reason="ko")
        elif _dead(heroi):
            heroi.set_isalive(False)
            self._finish(winner=opponent_of(lado), reason="ko")
        return StepRecord(lado, acao, "executed", reservado, gasto, dano)

    # --- rendição ----------------------------------------------------------

    def _resolve_surrender(self, numero: int, travadas: dict[str, DuelAction]) -> RoundRecord:
        """Rendição é derrota imediata: resolve no lock, antes de qualquer golpe.

        Não passa pela oportunidade — um gladiador atordoado também pode se
        render. Nenhuma ação da rodada é executada, e nada é reservado.

        Se os DOIS se renderem na mesma rodada, a rendição de quem está na
        frente da ordem travada resolve primeiro. É o que mantém o motor total;
        a regra competitiva desse caso é decisão pendente.
        """
        leituras, ordem = self._initiative()
        rendidos = [
            lado for lado in (ordem.first, ordem.second) if travadas[lado].kind == "surrender"
        ]
        perdedor = rendidos[0]
        self._event(
            numero,
            "surrender",
            perdedor,
            (("simultaneous", len(rendidos) > 1),),
        )
        self._finish(winner=opponent_of(perdedor), reason="surrender")
        passos = [
            StepRecord(lado, travadas[lado], "not_reached") for lado in (ordem.first, ordem.second)
        ]
        return self._record(numero, travadas, leituras, ordem, passos)

    # --- fechamento --------------------------------------------------------

    def _record(self, numero, travadas, leituras, ordem, passos) -> RoundRecord:
        registro = RoundRecord(
            number=numero,
            actions=tuple((lado, travadas[lado]) for lado in SIDES),
            initiative=leituras,
            order=ordem,
            steps=tuple(passos),
            hp_end=tuple((lado, int(self.hero(lado).get_hp())) for lado in SIDES),
            mp_end=tuple((lado, int(self.hero(lado).get_mp())) for lado in SIDES),
        )
        self._history.append(registro)
        if self._result is not None:
            self._result = DuelResult(
                winner=self._result.winner,
                loser=self._result.loser,
                winner_name=self._result.winner_name,
                loser_name=self._result.loser_name,
                reason=self._result.reason,
                rounds=len(self._history),
                history=tuple(self._history),
            )
        return registro

    def _finish(self, *, winner: str, reason: EndReason) -> DuelResult:
        if self._result is not None:
            raise DuelFinishedError("O duelo já terminou.")
        perdedor = opponent_of(winner)
        self._result = DuelResult(
            winner=winner,
            loser=perdedor,
            winner_name=str(self.hero(winner).get_nick_name()),
            loser_name=str(self.hero(perdedor).get_nick_name()),
            reason=reason,
            rounds=len(self._history),
            history=tuple(self._history),
        )
        self._event(self._round, "duel_finished", winner, (("reason", reason),))
        return self._result

    def _ensure_running(self) -> None:
        if self._result is not None:
            raise DuelFinishedError("O duelo já terminou.")

    def _event(self, numero: int, name: str, side: str | None = None, detail=()) -> None:
        self._events.append(DuelEvent(numero, name, side, tuple(detail)))


def run_round(duel: Duel, controllers: Mapping[str, DuelController]) -> RoundRecord:
    """Pede uma ação a cada controlador e resolve a rodada.

    As duas visões são montadas ANTES da primeira escolha, então a escolha de
    um lado não tem por onde chegar à visão do outro. Um controlador recebe só
    a própria `DuelView` — nunca o duelo nem o outro controlador.
    """
    visoes = {lado: duel.view(lado) for lado in SIDES}
    escolhas = {lado: controllers[lado].choose(visoes[lado]) for lado in SIDES}
    return duel.play_round(escolhas)
