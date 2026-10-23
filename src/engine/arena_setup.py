"""Entrada da Arena pelo snapshot salvo do personagem.

O personagem extraído vive no save (`storage.save_manager.to_save_data`). O
gladiador nasce dele pelo caminho canônico de reconstrução
(`player_from_save_data`) — o mesmo do jogo e do benchmark —, e não por uma
cópia campo a campo que envelheceria no primeiro campo novo do save.

Mora em `engine/` porque é a única camada que junta `storage/` (reconstrução) e
`content/` (preparação). A regra da preparação não está aqui: está em
`content/gladiator.py`.
"""

from __future__ import annotations

import copy

from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator
from src.content.items import get_all_items
from src.engine.game_logic import CLASS_MAP
from src.mechanics.pvp_duel import Gladiator
from src.storage.save_manager import player_from_save_data

# O registro de classes do save ("Warrior" -> Warrior), derivado do mapa da
# criação de personagem para não existir uma segunda lista de classes.
_FABRICA = {nome: classe for classe, nome in CLASS_MAP.values()}


def gladiator_from_snapshot(snapshot: dict) -> Gladiator:
    """O gladiador de um snapshot de save. Não altera o snapshot.

    A reconstrução recebe uma CÓPIA profunda: `player_from_save_data` adota os
    dicionários de estado do save como estão, e a preparação os limparia —
    dentro do snapshot de quem chamou.
    """
    heroi, _, _ = player_from_save_data(copy.deepcopy(snapshot), get_all_items(), _FABRICA)
    if heroi is None:
        raise GladiatorNotEligibleError(
            f"Snapshot ilegível para a Arena: classe {snapshot.get('player_class')!r}."
        )
    return prepare_gladiator(heroi)
