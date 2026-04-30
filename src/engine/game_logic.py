#!/usr/bin/env python3
"""Lógica de criação de personagem e inicialização do jogo."""

from src.content.skills import mage_skills, rogue_skills, warrior_skills
from src.entities.heroes import Mage, Rogue, Warrior


CLASS_MAP = {
    "warrior": (Warrior, warrior_skills),
    "mage": (Mage, mage_skills),
    "rogue": (Rogue, rogue_skills),
}


def create_player_from_data(class_key: str, player_name: str) -> Warrior | Mage | Rogue | None:
    """
    Cria o personagem do jogador a partir dos dados fornecidos.
    
    Esta é uma função pura da camada de engine - não interage com UI.
    A coleta de dados (classe e nome) deve ser feita pela camada UI.
    
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
    
    class_constructor, skills = CLASS_MAP[class_key]
    player = class_constructor(player_name.strip())
    player.learnable_skills = skills
    player.learn_new_skills(show=False)
    return player
