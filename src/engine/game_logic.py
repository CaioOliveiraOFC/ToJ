#!/usr/bin/env python3
"""Lógica de criação de personagem e inicialização do jogo."""

from src.content.skills_loader import get_initial_skills
from src.entities.heroes import Mage, Rogue, Warrior

CLASS_MAP = {
    "warrior": (Warrior, "Warrior"),
    "mage": (Mage, "Mage"),
    "rogue": (Rogue, "Rogue"),
}


def create_player_from_data(class_key: str, player_name: str) -> Warrior | Mage | Rogue | None:
    """
    Cria o personagem do jogador a partir dos dados fornecidos.

    Esta é uma função pura da camada de engine - não interage com UI.

    Args:
        class_key: Chave da classe ("warrior", "mage", "rogue")
        player_name: Nome do personagem

    Returns:
        Instância do herói criado ou None se parâmetros inválidos
    """
    if class_key not in CLASS_MAP:
        return None

    if not player_name or not player_name.strip():
        return None

    class_constructor, class_name = CLASS_MAP[class_key]
    player = class_constructor(player_name.strip())
    # Aprende a primeira skill inicial (nível 1)
    initial_skills = get_initial_skills(class_name)
    if initial_skills:
        player.skills[1] = initial_skills[0]
        player.initial_skills_learned = 1
    return player
