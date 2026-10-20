#!/usr/bin/env python3
"""Lógica de criação de personagem e inicialização do jogo."""

from src.content.skills_loader import get_initial_skills
from src.content.starter_kit import grant_starter
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


def create_player_for_new_run(
    class_key: str, player_name: str, rng=None
) -> Warrior | Mage | Rogue | None:
    """O personagem de uma NOVA JORNADA: o herói neutro mais o Starter Kit.

    É o único caminho de largada real — a tela do jogador e o `BotPadrao` passam
    por aqui. `create_player_from_data` continua sendo o herói puro, para quem
    precisa medir sem a sorte da largada (testes, benchmark, paridade).

    Ordem: cria o herói, entrega exatamente um starter e o equipa. O descanso no
    fim é o da CONSTRUÇÃO do personagem: se o starter subir o teto de HP ou MP, a
    jornada começa com o teto novo cheio, e não com um buraco que ninguém causou.

    `rng` é o gerador da jornada; sem ele, o `random` global do jogo.
    """
    player = create_player_from_data(class_key, player_name)
    if player is None:
        return None
    grant_starter(player, rng)
    player.rest()
    return player
