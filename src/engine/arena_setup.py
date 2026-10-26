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
from dataclasses import dataclass

from src.content.extraction import was_extracted
from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator
from src.content.items import get_all_items
from src.engine.game_logic import CLASS_MAP
from src.mechanics.pvp_duel import Gladiator
from src.storage.save_manager import (
    list_slots,
    load_save_data,
    player_from_save_data,
    save_loadout,
)

# O registro de classes do save ("Warrior" -> Warrior), derivado do mapa da
# criação de personagem para não existir uma segunda lista de classes.
_FABRICA = {nome: classe for classe, nome in CLASS_MAP.values()}


@dataclass(frozen=True)
class ArenaEntry:
    """Um gladiador disponível: o slot de um personagem extraído."""

    slot: int
    name: str
    class_name: str
    level: int
    floor: int


def list_gladiators() -> list[ArenaEntry]:
    """Os personagens salvos com extração registrada, na ordem dos slots.

    Só o que existe em save: nenhum personagem é gerado para completar a lista.
    """
    return [
        ArenaEntry(
            slot=int(s["slot"]),
            name=str(s.get("name", "?")),
            class_name=str(s.get("class", "?")),
            level=int(s.get("level", 0) or 0),
            floor=int(s.get("floor", 0) or 0),
        )
        for s in list_slots()
        if s.get("occupied") and s.get("extracted")
    ]


def _reconstruir(snapshot: dict):
    """O personagem do snapshot, reconstruído sobre uma CÓPIA profunda.

    `player_from_save_data` adota os dicionários de estado do save como estão; a
    cópia é o que impede qualquer mudança no personagem de voltar ao snapshot de
    quem chamou.
    """
    heroi, _, _ = player_from_save_data(copy.deepcopy(snapshot), get_all_items(), _FABRICA)
    if heroi is None:
        raise GladiatorNotEligibleError(
            f"Snapshot ilegível para a Arena: classe {snapshot.get('player_class')!r}."
        )
    return heroi


def character_from_snapshot(snapshot: dict):
    """O personagem do snapshot, reconstruído pelo caminho canônico e ainda NÃO preparado.

    Para quem precisa conferir a reconstrução antes da preparação (a validação
    do gladiador no multiplayer). Não altera o snapshot.
    """
    return _reconstruir(snapshot)


def _snapshot_do_slot(slot: int) -> dict:
    dados = load_save_data(slot)
    if dados is None:
        raise GladiatorNotEligibleError(f"O slot {slot} não tem save legível.")
    return dados


def gladiator_from_snapshot(snapshot: dict) -> Gladiator:
    """O gladiador de um snapshot de save. Não altera o snapshot."""
    return prepare_gladiator(_reconstruir(snapshot))


def gladiator_from_slot(slot: int) -> Gladiator:
    """O gladiador salvo no slot, pronto para o duelo. O arquivo não muda."""
    return gladiator_from_snapshot(_snapshot_do_slot(slot))


def load_character(slot: int):
    """O personagem extraído do slot, para a preparação antes do duelo.

    É o personagem salvo, com a mochila, o HP e o MP do save — não a instância
    do duelo. A preparação mexe nele; o duelo recebe `prepare_gladiator` dele.
    """
    heroi = _reconstruir(_snapshot_do_slot(slot))
    if not was_extracted(heroi):
        raise GladiatorNotEligibleError(
            f"{heroi.get_nick_name()} não veio de uma extração e não entra na Arena."
        )
    return heroi


def store_loadout(slot: int, player) -> dict:
    """Grava no slot o equipamento escolhido na preparação, e só ele.

    Recusa se o save do slot não for de um personagem extraído — a Arena não
    escreve em run viva — ou se o personagem não for o do slot: equipamento não
    passa de um gladiador para outro.
    """
    dados = _snapshot_do_slot(slot)
    if not was_extracted(_reconstruir(dados)):
        raise GladiatorNotEligibleError(f"O slot {slot} não guarda um gladiador extraído.")
    if (dados.get("player_name"), dados.get("player_class")) != (
        player.get_nick_name(),
        player.get_classname(),
    ):
        raise GladiatorNotEligibleError(
            f"O equipamento de {player.get_nick_name()} não pode ir para o slot {slot}."
        )
    return save_loadout(slot, player)
