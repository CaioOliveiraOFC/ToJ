"""A saída do andar: taxa em ouro, e o preço de não conseguir pagá-la.

Sair custa. É isso que dá preço a atravessar o andar sem lutar — contornar todo
mundo continua possível, e continua pagando a conta com capital que o combate
não repôs.

Quem não tem o valor inteiro **sobe do mesmo jeito**. Não existe dívida, não
existe bloqueio e não existe softlock: a run continua, e vai ficando menos
eficiente. Cada saída não paga consecutiva tira um pedaço da Essência do andar
seguinte, até o piso — e pagar UMA saída inteira encerra a punição na hora.

A punição é exclusivamente de Essência, e mora inteira aqui e em
`essence_after_penalty`. Duas implementações da mesma regra seriam duas
economias, e é assim que o simulador acaba medindo um jogo que não existe.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.content.economy import exit_fee
from src.shared.economy import essence_after_penalty, essence_penalty

if TYPE_CHECKING:
    from src.entities.heroes import Player


@dataclass(frozen=True)
class ExitAttempt:
    """O que aconteceu ao usar a saída. Subir sempre acontece."""

    fee: int
    paid: int
    streak: int

    @property
    def was_paid(self) -> bool:
        return self.paid >= self.fee


def can_afford_exit(player: "Player", dungeon_level: int) -> bool:
    """O jogador paga a taxa inteira agora?"""
    return int(getattr(player, "coins", 0)) >= exit_fee(dungeon_level)


def unpaid_streak(player: "Player") -> int:
    return int(getattr(player, "unpaid_exit_streak", 0) or 0)


def current_penalty(player: "Player") -> float:
    """Quanto a sequência atual tira da Essência do próximo andar."""
    return essence_penalty(unpaid_streak(player))


def use_exit(player: "Player", dungeon_level: int) -> ExitAttempt:
    """Cobra a saída e sobe. Dois desfechos, e nenhum deles é uma recusa.

    1. **Pagou** — a taxa sai inteira e a sequência zera na hora. "Consegui
       reorganizar a run e pagar" encerra a punição, sem carência.
    2. **Não pagou** — nada é cobrado. Cobrar o que tem seria pagamento parcial,
       e pagamento parcial é dívida disfarçada: o jogador ficaria sem ouro E com
       a punição. A sequência sobe um, e o preço aparece na Essência do andar
       seguinte.

    A sequência não tem teto de propósito. O que tem piso é o RESULTADO —
    `essence_after_penalty` nunca devolve menos que `ESSENCE_PENALTY_FLOOR`. Sem
    teto no contador dá para medir quantos andares o jogador atravessou sem
    pagar, sem inventar uma regra de bloqueio para isso.
    """
    taxa = exit_fee(dungeon_level)

    if int(getattr(player, "coins", 0)) >= taxa:
        player.spend_coins(taxa, source="exit_fee")
        player.unpaid_exit_streak = 0
        player.ledger["paid_exits"] = player.ledger.get("paid_exits", 0) + 1
        return ExitAttempt(fee=taxa, paid=taxa, streak=0)

    player.unpaid_exit_streak = unpaid_streak(player) + 1
    player.ledger["unpaid_exits"] = player.ledger.get("unpaid_exits", 0) + 1
    player.ledger["max_unpaid_exit_streak"] = max(
        player.ledger.get("max_unpaid_exit_streak", 0), player.unpaid_exit_streak
    )
    return ExitAttempt(fee=taxa, paid=0, streak=player.unpaid_exit_streak)


def effective_essence(player: "Player", rolled: float) -> float:
    """O multiplicador que o andar REALMENTE paga, já com a penalidade.

    Ponto único de resolução. Todo consumidor de Essência recebe este valor, e
    ninguém multiplica `-0,2 × streak` por conta própria — espalhar isso seria o
    mesmo defeito que a fórmula de preço teve em quatro arquivos.
    """
    return essence_after_penalty(rolled, unpaid_streak(player))
