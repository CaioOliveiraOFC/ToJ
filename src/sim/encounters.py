"""Catálogo de encontros nomeados.

Um encontro é UM DUELO: um herói contra um monstro. Houve uma fase em que o
catálogo tinha composições — `tank_plus_glass`, `trash_trio` —, e ela foi um
erro de direção: o jogo é 1x1 e o simulador precisa medir o jogo que existe, não
um que nunca existiu.

O arquétipo continua sendo a unidade de medida, porque é ele que decide o TIPO
de duelo: o tank é a luta longa, o glass cannon é a corrida para matar antes de
morrer, o controller é a luta contra status. Cada um precisa de nome estável
para comparar resultados entre iterações.
"""

from __future__ import annotations

from collections.abc import Callable

from src.content.factories.archetypes import spawn_by_role
from src.content.factories.monsters import create_boss_for_level, create_monster

# Cada entrada devolve a lista de monstros do encontro para um dado nível.
# `level_fn` é opcional: quando dado, sorteia o nível de CADA monstro. A matriz
# de encontros não passa nada, porque comparar arquétipos exige nível fixo; a
# simulação de run passa, porque o jogo real sorteia (ver `build_encounter`).
LevelFn = Callable[[], int]
EncounterFactory = Callable[..., list]

# O chefe não sorteia nível: `create_boss_for_level` amarra o chefe ao andar, e
# é assim que o jogo real gera o marco de cada cinco andares.
FIXED_LEVEL_ROLES = ("boss",)


def _nivel(level: int, role: str, level_fn: LevelFn | None) -> int:
    if level_fn is None or role in FIXED_LEVEL_ROLES:
        return level
    return level_fn()


def _legacy_monster(level: int, level_fn: LevelFn | None = None) -> list:
    """O monstro genérico do jogo antes do rebalanceamento. Usado na baseline."""
    return [create_monster(f"Monstro Nv.{level}", level)]


def _legacy_boss(level: int, level_fn: LevelFn | None = None) -> list:
    """O mini-chefe do jogo antes do rebalanceamento. Usado na baseline."""
    return [create_boss_for_level(level)]


def _solo(role: str) -> EncounterFactory:
    def factory(level: int, level_fn: LevelFn | None = None) -> list:
        return [spawn_by_role(role, _nivel(level, role, level_fn))]

    return factory


ENCOUNTERS: dict[str, EncounterFactory] = {
    # Legado — o que existia antes. Mantido para a baseline continuar comparável.
    "legacy_monster": _legacy_monster,
    "legacy_boss": _legacy_boss,
    # Solos: um arquétipo por vez, para isolar a contribuição de cada papel.
    "trash_solo": _solo("trash"),
    "bruiser_solo": _solo("bruiser"),
    "tank_solo": _solo("tank"),
    "glass_solo": _solo("glass_cannon"),
    "skirmisher_solo": _solo("skirmisher"),
    "controller_solo": _solo("controller"),
    "support_solo": _solo("support"),
    "elite_solo": _solo("elite"),
    "boss_solo": _solo("boss"),
}

# Conjuntos usados pelos testes e pelo runner.
SOLO_ENCOUNTERS = [
    name for name in ENCOUNTERS if name.endswith("_solo") and not name.startswith("legacy")
]
# A matriz mede duelos, porque o jogo só tem duelos.
MATRIX_ENCOUNTERS = SOLO_ENCOUNTERS
# Encontros que representam o andar comum. Boss e elite ficam de fora: eles são
# marcos, e misturá-los na média esconde o que o andar comum está fazendo.
ROUTINE_ENCOUNTERS = [
    "trash_solo",
    "bruiser_solo",
    "tank_solo",
    "glass_solo",
    "skirmisher_solo",
    "controller_solo",
]


def build_encounter(name: str, level: int, level_fn: LevelFn | None = None) -> list:
    """Instancia um encontro do catálogo para o nível dado.

    Args:
        name: Chave do catálogo.
        level: Andar (ou nível) de referência do encontro.
        level_fn: Sorteador de nível por monstro. Sem ele, todo monstro nasce
            exatamente no `level` — o que a matriz de encontros quer, e o que a
            simulação de run NÃO quer: o jogo real sorteia +0/+1/+2 níveis por
            monstro (`generation.level_variation`), com peso 70/25/5. Fixar o
            nível no andar apagava esses monstros acima do andar e o custo de
            recurso que eles impõem, então a run simulada media uma masmorra
            mais fraca que a de produção.
    """
    if name not in ENCOUNTERS:
        raise ValueError(f"Encontro desconhecido: {name!r}. Use um de {sorted(ENCOUNTERS)}.")
    return ENCOUNTERS[name](level, level_fn)
