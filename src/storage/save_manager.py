from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.heroes import Player

SAVE_FILE = "savegame.json"

# Type aliases
ItemRegistry = dict[str, object]
PlayerFactory = type["Player"]
SaveResult = dict[str, bool | str]


def save_game(
    player: "Player",
    dungeon_level: int,
    map_state: dict | None = None
) -> SaveResult:
    """Salva o estado atual do jogo num ficheiro JSON."""
    inventory_names = [item.name for item in player.inventory]
    equipment_names = {slot: item.name if item else None for slot, item in player.equipment.items()}
    passive_ids = [p.id for p in player.passives]
    skills_data = {str(k): v.id for k, v in player.skills.items()}

    save_data = {
        "player_class": player.get_classname(),
        "player_name": player.get_nick_name(),
        "level": player.get_level(),
        "xp": player.xp_points,
        "coins": player.coins,
        "inventory": inventory_names,
        "equipment": equipment_names,
        "passives": passive_ids,
        "skills": skills_data,
        "initial_skills_learned": player.initial_skills_learned,
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
) -> tuple["Player" | None, int | None, dict | None]:
    """Carrega o estado do jogo a partir de um ficheiro JSON."""
    if not os.path.exists(SAVE_FILE):
        return None, None, None

    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)

        player_class_name = save_data["player_class"]
        player_name = save_data["player_name"]

        player_class = player_factory.get(player_class_name)
        if not player_class:
            return None, None, None

        player = player_class(player_name)

        # Carrega skills do novo formato (por id)
        from src.content.skills_loader import get_skill_by_id

        skills_loaded = True
        skills_data = save_data.get("skills", {})
        if skills_data:
            for key_str, skill_id in skills_data.items():
                skill = get_skill_by_id(skill_id)
                if skill:
                    player.skills[int(key_str)] = skill
                else:
                    skills_loaded = False
        else:
            skills_loaded = False

        if not skills_loaded:
            print("Aviso: Save incompatível - skills não puderam ser carregadas.")

        player.initial_skills_learned = save_data.get("initial_skills_learned", len(player.skills))

        # Define o nível (isso vai disparar aprendizado de skills iniciais)
        saved_level = save_data["level"]
        player.set_level(saved_level)

        # Restaurar skills salvas (set_level limpa as skills)
        if skills_data:
            player.skills.clear()
            for key_str, skill_id in skills_data.items():
                skill = get_skill_by_id(skill_id)
                if skill:
                    player.skills[int(key_str)] = skill

        player.xp_points = save_data["xp"]
        player.coins = save_data["coins"]

        # Reconstrói o inventário
        player.inventory = [item_registry[name] for name in save_data["inventory"]]

        for slot, item_name in save_data["equipment"].items():
            if item_name:
                item_to_equip = item_registry[item_name]
                if item_to_equip in player.inventory:
                    player.inventory.remove(item_to_equip)
                player.equip(item_to_equip)

        player.active_buffs = save_data.get("active_buffs", {})
        player.active_effects = save_data.get("active_effects", {})

        passive_ids = save_data.get("passives", [])
        if passive_ids:
            from src.content.passives import get_passive_by_id
            for pid in passive_ids:
                passive = get_passive_by_id(pid)
                if passive:
                    player.add_passive_load(passive)

        dungeon_level = save_data["dungeon_level"]
        map_state = save_data.get("map_state", None)

        return player, dungeon_level, map_state

    except Exception as e:
        print(f"Erro ao carregar save: {e}")
        return None, None, None


def check_save_file() -> bool:
    """Verifica se o ficheiro de save existe."""
    return os.path.exists(SAVE_FILE)
