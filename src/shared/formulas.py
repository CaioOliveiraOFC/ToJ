"""Fórmulas de escalonamento e progressão.

Vive em `shared/` porque `entities/`, `mechanics/` e `content/` precisam todas
da mesma curva, e `shared/` é a única camada que qualquer uma pode importar.
Manter a fórmula em um lugar só é a razão de o herói e o monstro não voltarem a
crescer por curvas diferentes — que era o defeito estrutural do balanceamento
anterior.

Este módulo não depende de nada, nem de outros módulos do projeto.
"""

from __future__ import annotations

from src.shared.constants import GROWTH_RATE, XP_BASE_COST, XP_LEVEL_RATIO


def geometric(base: float, level: int, rate: float = GROWTH_RATE) -> int:
    """Valor de um atributo no nível dado, a partir do valor do nível 1.

    Derivar do nível, em vez de acumular a cada level up, evita dois problemas:
    a divergência entre curvas de formas diferentes, e o erro de arredondamento
    que congelaria um atributo pequeno — `int(8 * 1.12)` é 8, então uma
    agilidade base de 8 nunca sairia do lugar se o valor fosse acumulado.

    Args:
        base: Valor do atributo no nível 1.
        level: Nível desejado (mínimo 1).
        rate: Razão de crescimento por nível.

    Returns:
        Valor do atributo no nível pedido, arredondado.
    """
    return int(round(base * (rate ** (max(1, level) - 1))))


def xp_for_level(level: int) -> int:
    """XP necessária para sair de `level` para o próximo.

    A razão é maior que `GROWTH_RATE` de propósito: o número de combates por
    nível sobe ao longo da run, então o herói fica progressivamente atrás do
    andar. É essa defasagem que cria dificuldade crescente, em vez de inflar os
    números do monstro.

    Args:
        level: Nível atual.

    Returns:
        XP total necessária para o próximo nível.
    """
    return int(XP_BASE_COST * (XP_LEVEL_RATIO ** (max(1, level) - 1)))
