"""Preparação do gladiador: do personagem extraído à instância de duelo.

A Arena só recebe quem saiu vivo da dungeon pela Extração. O que entra no duelo
é uma CÓPIA: o personagem salvo — e o snapshot de onde ele veio — não é tocado
pela luta, e dois duelos do mesmo gladiador nunca dividem estado.

A cópia leva o que é permanente e larga o que era da run:

- fica: classe, nível, atributos, equipamento, deck, passivas;
- volta ao máximo: HP e MP;
- sai: buff e efeito temporário que vieram da dungeon, recarga de skill, a
  marca de `death_ignore` já gasto;
- sai: todo consumível. Na Arena não se bebe poção, e a classificação é a
  canônica (`Item.is_potion`), nunca uma lista de nomes.

Reorganizar equipamento é coisa de ANTES da fila, sobre o personagem salvo. O
duelo não oferece ação de equipar, nem de trocar skill, passiva ou atributo.
"""

from __future__ import annotations

import copy

from src.content.extraction import was_extracted
from src.mechanics.pvp_duel import Gladiator


class GladiatorNotEligibleError(ValueError):
    """O personagem não pode entrar na Arena."""


def prepare_gladiator(player) -> Gladiator:
    """Uma instância de duelo, normalizada, a partir de um personagem extraído.

    Nunca altera `player`.
    """
    if not was_extracted(player):
        raise GladiatorNotEligibleError(
            f"{player.get_nick_name()} não veio de uma extração: a Arena só recebe "
            "personagens que encerraram a run pela Extração."
        )

    heroi = copy.deepcopy(player)
    # Efeitos saem ANTES de restaurar: um efeito de recurso (`vitality`,
    # `clouded`) mexe no teto de HP/MP, e restaurar sob ele deixaria a barra
    # acima ou abaixo do teto verdadeiro depois que ele sai.
    heroi.active_effects.clear()
    heroi.active_buffs.clear()
    heroi.rest()
    heroi.skill_cooldowns.clear()
    heroi._death_ignore_used = False
    heroi.inventory = [item for item in heroi.inventory if not getattr(item, "is_potion", False)]
    return Gladiator(hero=heroi)
