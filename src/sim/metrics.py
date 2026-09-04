"""Agregação e intervalos de confiança para os resultados da simulação.

Uma taxa de vitória sem intervalo de confiança convida a perseguir ruído: com
500 iterações, 61% e 64% são o mesmo número. O intervalo de Wilson diz quando
uma diferença é real e quando é a semente.
"""

from __future__ import annotations

import math


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson para uma proporção.

    Preferido ao intervalo normal porque continua correto perto de 0% e de 100%,
    que é exatamente onde as taxas de vitória deste jogo vivem.
    """
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denom
    margin = z * math.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def spread(values: list[float]) -> float:
    """Distância entre o maior e o menor valor. Mede dominância entre classes."""
    return (max(values) - min(values)) if values else 0.0


def skill_gap(smart_win_rate: float, greedy_win_rate: float) -> float:
    """Vantagem do jogador competente sobre o que só ataca.

    É a métrica central do balanceamento: se ela for pequena, o jogo virou uma
    barreira de HP em vez de um desafio, por mais alto que estejam os números.
    """
    return smart_win_rate - greedy_win_rate


def curve_deltas(survival_by_floor: dict[int, float]) -> list[tuple[int, float]]:
    """Queda de sobrevivência entre andares consecutivos.

    Um delta grande é uma parede; um delta zero por vários andares é um platô.
    Ambos são defeitos de curva, e nenhum aparece na média.
    """
    floors = sorted(survival_by_floor)
    return [
        (floors[i + 1], survival_by_floor[floors[i]] - survival_by_floor[floors[i + 1]])
        for i in range(len(floors) - 1)
    ]
