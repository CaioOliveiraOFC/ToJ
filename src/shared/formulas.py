"""Fórmulas de escalonamento e progressão.

Vive em `shared/` porque `entities/`, `mechanics/` e `content/` precisam todas
da mesma curva, e `shared/` é a única camada que qualquer uma pode importar.
Manter a fórmula em um lugar só é a razão de o herói e o monstro não voltarem a
crescer por curvas diferentes — que era o defeito estrutural do balanceamento
anterior.

Este módulo não depende de nada, nem de outros módulos do projeto.
"""

from __future__ import annotations

from src.shared.constants import GROWTH_RATE, XP_BASE_COST, XP_LEVEL_SOFTENER


def geometric(base: float, level: int, rate: float = GROWTH_RATE) -> int:
    """Valor de um atributo no nível dado, a partir do valor do nível 1.

    Derivado do nível, nunca acumulado: acumular divergiria entre curvas de
    formas diferentes e congelaria atributos pequenos no arredondamento
    (`int(8 * 1.12)` é 8).

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

    `nível × GROWTH_RATE^(nível-1)`: a mesma forma da produção de XP de um andar,
    que é `andar × GROWTH_RATE^andar` porque o andar cresce em número de monstros
    e em valor de cada um. Igualar as duas formas é o que mantém constante a
    diferença entre o nível do herói e o nível do encontro em qualquer
    profundidade — nenhuma razão puramente exponencial fecha essa conta.

    O número de combates por nível continua subindo, agora linearmente:
    `custo/recompensa` é proporcional a `nível + XP_LEVEL_SOFTENER`.

    Args:
        level: Nível atual.

    Returns:
        XP total necessária para o próximo nível.
    """
    nivel = max(1, level)
    amortecedor = (nivel + XP_LEVEL_SOFTENER) / (1 + XP_LEVEL_SOFTENER)
    return int(XP_BASE_COST * amortecedor * GROWTH_RATE ** (nivel - 1))
