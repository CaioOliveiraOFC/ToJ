"""Catálogo de encontros nomeados.

Um encontro é uma composição, não um monstro. Um monstro isolado pode estar
equilibrado e a combinação estar quebrada — um tank que protege um glass cannon é
um problema diferente de qualquer um dos dois sozinho. Por isso a unidade de
medida do balanceamento é o encontro, e ele precisa de nome estável para
comparar resultados entre iterações.
"""

from __future__ import annotations

from collections.abc import Callable

from src.content.factories.archetypes import spawn_by_role
from src.content.factories.monsters import create_boss_for_level, create_monster

# Cada entrada devolve a lista de monstros do encontro para um dado nível.
EncounterFactory = Callable[[int], list]


def _legacy_monster(level: int) -> list:
    """O monstro genérico do jogo antes do rebalanceamento. Usado na baseline."""
    return [create_monster(f"Monstro Nv.{level}", level)]


def _legacy_boss(level: int) -> list:
    """O mini-chefe do jogo antes do rebalanceamento. Usado na baseline."""
    return [create_boss_for_level(level)]


def _solo(role: str) -> EncounterFactory:
    return lambda level: [spawn_by_role(role, level)]


def _group(*roles: str) -> EncounterFactory:
    return lambda level: [spawn_by_role(role, level) for role in roles]


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
    # Composições: onde a combinação vale mais que a soma das partes.
    "trash_pair": _group("trash", "trash"),
    "trash_trio": _group("trash", "trash", "trash"),
    "tank_plus_glass": _group("tank", "glass_cannon"),
    "controller_plus_bruiser": _group("controller", "bruiser"),
    "skirmisher_pair": _group("skirmisher", "skirmisher"),
    "support_plus_bruiser": _group("support", "bruiser"),
    "elite_plus_2_trash": _group("elite", "trash", "trash"),
}

# Conjuntos usados pelos testes e pelo runner.
SOLO_ENCOUNTERS = [name for name in ENCOUNTERS if name.endswith("_solo") and not name.startswith("legacy")]
GROUP_ENCOUNTERS = ["trash_pair", "trash_trio", "tank_plus_glass", "controller_plus_bruiser",
                    "skirmisher_pair", "support_plus_bruiser", "elite_plus_2_trash"]
MATRIX_ENCOUNTERS = SOLO_ENCOUNTERS + GROUP_ENCOUNTERS
# Encontros que representam o andar comum. Boss e elite ficam de fora: eles são
# marcos, e misturá-los na média esconde o que o andar comum está fazendo.
ROUTINE_ENCOUNTERS = ["trash_solo", "trash_pair", "trash_trio", "bruiser_solo",
                      "tank_solo", "glass_solo", "skirmisher_solo", "controller_solo"]


def build_encounter(name: str, level: int) -> list:
    """Instancia um encontro do catálogo para o nível dado."""
    if name not in ENCOUNTERS:
        raise ValueError(f"Encontro desconhecido: {name!r}. Use um de {sorted(ENCOUNTERS)}.")
    return ENCOUNTERS[name](level)
