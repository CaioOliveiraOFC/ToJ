from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from src.content.passives import get_passive_by_id
from src.content.skills_loader import get_skill_by_id

if TYPE_CHECKING:
    from src.entities.heroes import Player

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saves")
SAVE_FILE = "savegame.json"
TROPHY_FILE = "trophies.json"
SLOT_COUNT = 10

# Type aliases
ItemRegistry = dict[str, object]
PlayerFactory = type["Player"]
SaveResult = dict[str, bool | str]


def _ensure_save_dir() -> None:
    """Garante que o diretório de saves existe."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def get_slot_file(slot: int) -> str:
    """Retorna o nome do arquivo para o slot."""
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")


def list_slots() -> list[dict]:
    """Lista todos os slots, indicando quais estão ocupados."""
    _ensure_save_dir()
    slots = []
    for i in range(1, SLOT_COUNT + 1):
        filepath = get_slot_file(i)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    slots.append({
                        "slot": i,
                        "occupied": True,
                        "name": data.get("player_name", "?"),
                        "class": data.get("player_class", "?"),
                        "level": data.get("level", 0),
                        "floor": data.get("dungeon_level", 0)
                    })
            except Exception:
                slots.append({"slot": i, "occupied": False})
        else:
            slots.append({"slot": i, "occupied": False})
    return slots


def save_game(
    player: "Player",
    dungeon_level: int,
    map_state: dict | None = None,
    slot: int = 1
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
        _ensure_save_dir()
        filepath = get_slot_file(slot)
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=4)
        return {"success": True, "message": f"Jogo salvo no slot {slot}!"}
    except Exception as e:
        return {"success": False, "message": f"Ocorreu um erro ao salvar: {e}"}


def load_game(
    item_registry: ItemRegistry,
    player_factory: dict[str, PlayerFactory],
    slot: int = 1
) -> tuple["Player" | None, int | None, dict | None]:
    """Carrega o estado do jogo a partir de um ficheiro JSON."""
    filepath = get_slot_file(slot)
    if not os.path.exists(filepath):
        return None, None, None

    try:
        with open(filepath, 'r') as f:
            save_data = json.load(f)

        player_class_name = save_data["player_class"]
        player_name = save_data["player_name"]

        player_class = player_factory.get(player_class_name)
        if not player_class:
            return None, None, None

        player = player_class(player_name)

        # Carrega skills do novo formato (por id)
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
            pass  # Aviso: Save incompatível - skills não puderam ser carregadas.

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

        # Reconstrói o inventário (pula itens que não existem mais no registro)
        player.inventory = []
        for name in save_data["inventory"]:
            item = item_registry.get(name)
            if item:
                player.inventory.append(item)

        for slot, item_name in save_data["equipment"].items():
            if item_name:
                item_to_equip = item_registry.get(item_name)
                if item_to_equip is None:
                    continue
                if item_to_equip in player.inventory:
                    player.inventory.remove(item_to_equip)
                player.equip(item_to_equip)

        player.active_buffs = save_data.get("active_buffs", {})
        player.active_effects = save_data.get("active_effects", {})

        passive_ids = save_data.get("passives", [])
        if passive_ids:
            for pid in passive_ids:
                passive = get_passive_by_id(pid)
                if passive:
                    player.add_passive_load(passive)

        dungeon_level = save_data["dungeon_level"]
        map_state = save_data.get("map_state", None)

        return player, dungeon_level, map_state

    except Exception:
        return None, None, None


def check_save_file(slot: int = 1) -> bool:
    """Verifica se o ficheiro de save existe."""
    return os.path.exists(get_slot_file(slot))


def delete_save(slot: int) -> bool:
    """Deleta o save do slot especificado."""
    filepath = get_slot_file(slot)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
    return False


def add_trophy(
    player_name: str,
    player_class: str,
    level: int,
    floor_reached: int,
    cause: str = "Derrotado"
) -> bool:
    """Adiciona uma entrada ao livro de troféus (personagens que morreram)."""
    _ensure_save_dir()
    filepath = os.path.join(SAVE_DIR, TROPHY_FILE)

    trophies = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                trophies = json.load(f)
        except Exception:
            trophies = []

    trophy = {
        "name": player_name,
        "class": player_class,
        "level": level,
        "floor": floor_reached,
        "cause": cause,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    trophies.append(trophy)

    try:
        with open(filepath, 'w') as f:
            json.dump(trophies, f, indent=4)
        return True
    except Exception:
        return False


def get_trophies() -> list[dict]:
    """Retorna a lista de troféus (personagens que morreram)."""
    _ensure_save_dir()
    filepath = os.path.join(SAVE_DIR, TROPHY_FILE)

    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return []
