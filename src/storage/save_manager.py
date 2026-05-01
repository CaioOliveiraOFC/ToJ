from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.heroes import Player

SAVE_FILE = "savegame.json"

# Type aliases para clareza
ItemRegistry = dict[str, object]
SkillRegistry = dict[int, object]
PlayerFactory = type["Player"]
SaveResult = dict[str, bool | str]

def save_game(
    player: "Player",
    dungeon_level: int,
    map_state: dict | None = None
) -> SaveResult:
    """Salva o estado atual do jogo num ficheiro JSON.

    Retorna dict com 'success': bool e 'message': str para exibição pela UI.
    """
    # Converte os objetos de item em nomes para poderem ser guardados
    inventory_names = [item.name for item in player.inventory]
    equipment_names = {slot: item.name if item else None for slot, item in player.equipment.items()}

    save_data = {
        "player_class": player.get_classname(),
        "player_name": player.get_nick_name(),
        "level": player.get_level(),
        "xp": player.xp_points,
        "coins": player.coins,
        "inventory": inventory_names,
        "equipment": equipment_names,
        "active_buffs": player.active_buffs,
        "active_effects": player.active_effects,
        "dungeon_level": dungeon_level,
        "map_state": map_state
    }

    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=4)
        return {"success": True, "message": "Jogo salvo com sucesso!"}
    except Exception as e:
        return {"success": False, "message": f"Ocorreu um erro ao salvar o jogo: {e}"}

def load_game(
    item_registry: ItemRegistry,
    player_factory: dict[str, PlayerFactory],
    skills_registry: dict[str, SkillRegistry]
) -> tuple["Player" | None, int | None, dict | None]:
    """Carrega o estado do jogo a partir de um ficheiro JSON.

    Args:
        item_registry: Dicionário mapeando nomes de itens para instâncias (ALL_ITEMS).
        player_factory: Dicionário mapeando nomes de classes para classes de heróis.
        skills_registry: Dicionário mapeando nomes de classes para registries de skills.

    Retorna (player, dungeon_level, map_state) ou (None, None, None) em caso de erro.
    A mensagem de status deve ser exibida pela UI chamadora.
    """
    if not os.path.exists(SAVE_FILE):
        return None, None, None

    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)

        # Cria a instância do jogador com base na classe guardada
        player_class_name = save_data["player_class"]
        player_name = save_data["player_name"]

        player_class = player_factory.get(player_class_name)
        if not player_class:
            return None, None, None  # Classe desconhecida

        player = player_class(player_name)
        player.learnable_skills = skills_registry.get(player_class_name, {})

        # Define o nível e os status do jogador
        player.set_level(save_data["level"])
        player.xp_points = save_data["xp"]
        player.coins = save_data["coins"]

        # Reconstrói o inventário e o equipamento a partir dos nomes
        player.inventory = [item_registry[name] for name in save_data["inventory"]]

        for slot, item_name in save_data["equipment"].items():
            if item_name:
                item_to_equip = item_registry[item_name]
                # Remove o item do inventário antes de equipar para evitar duplicados
                if item_to_equip in player.inventory:
                    player.inventory.remove(item_to_equip)
                player.equip(item_to_equip)

        # Carrega active_buffs e active_effects
        player.active_buffs = save_data.get("active_buffs", {})
        player.active_effects = save_data.get("active_effects", {})

        dungeon_level = save_data["dungeon_level"]
        map_state = save_data.get("map_state", None)

        return player, dungeon_level, map_state

    except Exception:
        return None, None, None

def check_save_file() -> bool:
    """Verifica se o ficheiro de save existe."""
    return os.path.exists(SAVE_FILE)
