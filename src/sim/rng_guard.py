"""Isolamento do gerador global do módulo `random`.

Existe como módulo próprio porque duas camadas precisam do MESMO invariante por
motivos diferentes: a simulação de balanceamento precisa que uma `--seed`
produza sempre o mesmo resultado, e a medição de poder do personagem precisa não
CONSUMIR o sorteio que a run em andamento ainda vai usar. Uma cópia do
`getstate`/`setstate` em cada lugar seria duas promessas separadas sobre o mesmo
gerador, e a segunda a envelhecer passaria despercebida.
"""

from __future__ import annotations

import functools
import random
from contextlib import contextmanager


@contextmanager
def rng_isolado():
    """Devolve o gerador global ao estado anterior ao sair do bloco.

    A camada de conteúdo não sorteia pelo `rng` que a simulação injeta: a oferta
    de passiva e de skill, o nível do monstro, o spawn de elite, o drop de loot,
    o estoque da loja e o multiplicador de Essência saem todos de
    `random.<função>` em `content/` e `mechanics/math_operations.py`.

    Enquanto só o `rng` local era semeado, duas execuções com a mesma `--seed`
    davam resultados diferentes — no scout, 7.0 contra 7.8 de andar médio nas
    mesmas 20 runs. Essa oscilação é maior que quase todo delta que o scout
    reporta, então achado nenhum era distinguível de ruído e nenhuma regressão
    de balanceamento era bissetável.

    O estado anterior é restaurado ao sair: nem a simulação nem a medição podem
    deixar o gerador do processo preso numa sequência fixa para quem rodar
    depois, ou um teste posterior passaria a esconder justamente a instabilidade
    que ele existe para pegar. E, na run de verdade, uma medição que consumisse
    sorteio mudaria o mapa e o loot que o jogador ainda vai receber — medir o
    personagem não pode alterar o jogo que ele está jogando.
    """
    estado = random.getstate()
    try:
        yield
    finally:
        random.setstate(estado)


def isola_rng_global(func):
    """A forma DECORADOR do mesmo invariante, para funções inteiras."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with rng_isolado():
            return func(*args, **kwargs)

    return wrapper
