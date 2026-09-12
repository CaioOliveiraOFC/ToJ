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

    `nível × GROWTH_RATE^(nível-1)`: a mesma forma da produção de XP de um andar,
    que é `andar × GROWTH_RATE^andar` porque o andar cresce em número de monstros
    (linear, `3 + andar//3`) e em valor de cada monstro (geométrico).

    Igualar as duas formas é o que mantém constante a diferença entre o nível do
    herói e o nível esperado do encontro, em qualquer profundidade. Não é
    calibragem: é a única relação que não diverge. Uma razão exponencial acima de
    `GROWTH_RATE` faz o herói afundar linearmente (era o caso, com 1,195); uma
    abaixo ou igual o faz subir logaritmicamente. Nenhuma razão pura fecha a
    conta, porque nenhuma tem o fator linear que a produção tem.

    O número de combates por nível continua subindo — `custo/recompensa` é
    proporcional a `nível + XP_LEVEL_SOFTENER` —, só que linearmente em vez de
    exponencialmente. Subir de nível continua custando mais fundo; deixa de
    custar o impossível.

    Args:
        level: Nível atual.

    Returns:
        XP total necessária para o próximo nível.
    """
    nivel = max(1, level)
    amortecedor = (nivel + XP_LEVEL_SOFTENER) / (1 + XP_LEVEL_SOFTENER)
    return int(XP_BASE_COST * amortecedor * GROWTH_RATE ** (nivel - 1))
