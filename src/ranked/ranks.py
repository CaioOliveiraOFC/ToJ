"""Os 12 ranks da Ranked, por percentil da população competitiva, e os Definitive Masters.

O percentil de um gladiador é a posição dele na população competitiva, de 0 (o
último) a 100 (o primeiro): `100·(total − posição)/(total − 1)`. Rank é faixa de
percentil, não de rating: a mesma régua vale com 186 gladiadores ou com 5.000, e
o rating absoluto não precisa ter significado fora da Ladder.

Os cinco primeiros da classificação recebem a distinção Definitive Masters, por
cima do rank que o percentil dá.

Os limites estão em `LIMITES`, propostos a partir da população calibrada (ver
`reports/ranked/`). Cada limite é o percentil mínimo do rank.
"""

from __future__ import annotations

RANKS = (
    "Iron",
    "Bronze",
    "Silver",
    "Gold",
    "Platinum",
    "Emerald",
    "Sapphire",
    "Diamond",
    "Obsidian",
    "Master",
    "International Master",
    "Distinguished Master",
)
DEFINITIVE_MASTERS = 5
TITULO_DEFINITIVO = "Definitive Master"

# Percentil mínimo de cada rank, de Iron a Distinguished Master. Proposta da
# Fase 6 sobre os 186 calibrados: faixas largas embaixo e no meio (onde a
# incerteza do rating é maior que a diferença entre vizinhos) e estreitas em
# cima, sem nenhuma vazia com 186.
LIMITES = (0.0, 10.0, 22.0, 35.0, 48.0, 60.0, 70.0, 79.0, 86.0, 92.0, 96.0, 98.5)

assert len(LIMITES) == len(RANKS)
assert all(a < b for a, b in zip(LIMITES, LIMITES[1:]))


def percentil(posicao: int, total: int) -> float:
    """De 0 (o último) a 100 (o primeiro). Sozinho na população, 100."""
    if total <= 0 or not 1 <= posicao <= total:
        raise ValueError(f"posição {posicao} fora de 1–{total}")
    if total == 1:
        return 100.0
    return 100.0 * (total - posicao) / (total - 1)


def rank_do_percentil(valor: float, limites: tuple[float, ...] = LIMITES) -> str:
    """O rank cujo limite mínimo é o maior que não passa do percentil."""
    escolhido = RANKS[0]
    for nome, minimo in zip(RANKS, limites):
        if valor >= minimo:
            escolhido = nome
    return escolhido


def titulo(posicao: int) -> str | None:
    """`Definitive Master` para os cinco primeiros; `None` para o resto."""
    return TITULO_DEFINITIVO if 1 <= posicao <= DEFINITIVE_MASTERS else None
