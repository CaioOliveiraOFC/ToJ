"""O sistema de rating da Ranked e a priori pela força de referência.

A escolha do algoritmo e dos parâmetros saiu da comparação com confrontos
reais (`tools/ranked_experimentos.py comparar`, `reports/ranked/comparacao.md`).

A força de referência (o OP medido na geração da população) entra só como
estimativa inicial FRACA: o rating inicial anda `PESO_DO_OP` do que o OP prevê,
com a incerteza inicial cheia. Quem não tem OP começa no centro.
"""

from __future__ import annotations

from src.ranked.glicko2 import CENTRO, ESCALA, Glicko2
from src.ranked.trueskill import TrueSkill

ALGORITMO = "glicko2"
PARAMETROS = {"tau": 0.6}
# P(a vence b) ≈ σ(K_OP · (OP_a − OP_b)): o logit por ponto de OP, ajustado por
# máxima verossimilhança nos 396 confrontos reais de treino da amostra
# (`reports/ranked/comparacao.json`). O OP de referência é a mediana da
# população. A priori anda só `PESO_DO_OP` disso e fica presa a ±`LOGIT_MAXIMO`:
# sem o teto, um OP 4,3 começaria 3.000 pontos abaixo do centro.
K_OP = 1.4241
OP_CENTRO = 29.98
PESO_DO_OP = 0.5
LOGIT_MAXIMO = 3.0


def criar(algoritmo: str = ALGORITMO, parametros: dict | None = None):
    parametros = PARAMETROS if parametros is None else parametros
    if algoritmo == "glicko2":
        return Glicko2(**parametros)
    if algoritmo == "trueskill":
        return TrueSkill(**parametros)
    raise ValueError(f"algoritmo desconhecido: {algoritmo}")


def inicial(sistema, forca: float | None = None):
    """O rating de quem chega. Com força de referência, a priori fraca; sem ela, o centro."""
    if forca is None:
        return sistema.novo()
    logit = max(-LOGIT_MAXIMO, min(LOGIT_MAXIMO, K_OP * PESO_DO_OP * (forca - OP_CENTRO)))
    if isinstance(sistema, Glicko2):
        return sistema.novo(CENTRO + ESCALA * logit)
    escala = (2.0**0.5) * sistema.beta / 1.702
    return sistema.novo(sistema.mu + escala * logit)
