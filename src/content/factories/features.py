"""O que o andar oferece: Loja, Ferreiro e Extração como CASAS do mapa.

Os três eram garantidos — a loja e o ferreiro abriam sozinhos ao concluir o
andar, e a extração era um prompt automático. Nenhum deles era uma decisão
espacial: o jogador recebia os três, todo andar, sem andar até lugar nenhum.

Agora cada um tem chance própria. E cada um tem PITY: a chance sobe a cada andar
em que ele não apareceu, até forçar o encontro. O pity existe para o jogador não
ficar refém da moeda — uma seca longa de Loja não pode ser o que encerra a run,
porque isso não é dificuldade, é azar.

O streak mora no JOGADOR, não no mapa: o mapa do andar 7 não tem como saber que
a Loja falhou no 4, no 5 e no 6.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.shared.constants import (
    EXTRACTION_MIN_FLOOR,
    EXTRACTION_PITY_INCREMENT,
    EXTRACTION_SPAWN_CHANCE,
    FORGE_PITY_INCREMENT,
    FORGE_SPAWN_CHANCE,
    SHOP_PITY_INCREMENT,
    SHOP_SPAWN_CHANCE,
)

SHOP = "shop"
FORGE = "forge"
EXTRACTION = "extraction"


@dataclass(frozen=True)
class SpawnRule:
    """Chance base, quanto o pity acrescenta por falha, e o andar mínimo."""

    feature: str
    base_chance: float
    pity_increment: float
    min_floor: int = 1
    streak_field: str = ""

    def chance(self, floor: int, misses: int) -> float:
        """A chance REAL desta tentativa, já com o pity acumulado."""
        if floor < self.min_floor:
            return 0.0
        return min(1.0, self.base_chance + self.pity_increment * max(0, int(misses)))


RULES: tuple[SpawnRule, ...] = (
    SpawnRule(SHOP, SHOP_SPAWN_CHANCE, SHOP_PITY_INCREMENT, 1, "shop_miss_streak"),
    SpawnRule(FORGE, FORGE_SPAWN_CHANCE, FORGE_PITY_INCREMENT, 1, "forge_miss_streak"),
    SpawnRule(
        EXTRACTION,
        EXTRACTION_SPAWN_CHANCE,
        EXTRACTION_PITY_INCREMENT,
        EXTRACTION_MIN_FLOOR,
        "extraction_miss_streak",
    ),
)


def roll_features(player, floor: int, rng=None) -> list[str]:
    """Quais serviços este andar oferece, e atualiza o pity de cada um.

    Independentes: um andar pode ter os três, um só, ou nenhum. Eles não
    disputam um slot — disputam o TEMPO do jogador, que é outra coisa.

    Muta os streaks do jogador de propósito. A alternativa seria o chamador
    lembrar de atualizá-los, e o dia em que um chamador esquecer é o dia em que
    o pity para de existir em silêncio.
    """
    r = rng if rng is not None else random
    presentes: list[str] = []
    for regra in RULES:
        faltas = int(getattr(player, regra.streak_field, 0) or 0)
        if r.random() < regra.chance(floor, faltas):
            presentes.append(regra.feature)
            setattr(player, regra.streak_field, 0)
        elif floor >= regra.min_floor:
            # Só conta falta onde o serviço PODIA ter aparecido: andar 1 sem
            # Extração não é seca, é regra.
            setattr(player, regra.streak_field, faltas + 1)
    return presentes
