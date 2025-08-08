import json
import os
from .classes import Warrior, Mage, Rogue
from .items import ALL_ITEMS # Dicionário central de itens

SAVE_FILE = "savegame.json"

def save_game(player, dungeon_level):
    """Salva o estado atual do jogo num ficheiro JSON."""
    
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
        "dungeon_level": dungeon_level
    }

    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f, indent=4)
        print("\nJogo salvo com sucesso!")
    except Exception as e:
        print(f"\nOcorreu um erro ao salvar o jogo: {e}")

def load_game():
    """Carrega o estado do jogo a partir de um ficheiro JSON."""
    if not os.path.exists(SAVE_FILE):
        return None, None

    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)

        # Cria a instância do jogador com base na classe guardada
        player_class_name = save_data["player_class"]
        player_name = save_data["player_name"]
        
        if player_class_name == "Warrior":
            player = Warrior(player_name)
        elif player_class_name == "Mage":
            player = Mage(player_name)
        elif player_class_name == "Rogue":
            player = Rogue(player_name)
        else:
            return None, None # Classe desconhecida

        # Define o nível e os status do jogador
        player.set_level(save_data["level"])
        player.xp_points = save_data["xp"]
        player.coins = save_data["coins"]

        # Reconstrói o inventário e o equipamento a partir dos nomes
        player.inventory = [ALL_ITEMS[name] for name in save_data["inventory"]]
        
        for slot, item_name in save_data["equipment"].items():
            if item_name:
                item_to_equip = ALL_ITEMS[item_name]
                # Remove o item do inventário antes de equipar para evitar duplicados
                if item_to_equip in player.inventory:
                    player.inventory.remove(item_to_equip)
                player.equip(item_to_equip)
        
        dungeon_level = save_data["dungeon_level"]
        
        print("\nJogo carregado com sucesso!")
        return player, dungeon_level

    except Exception as e:
        print(f"\nOcorreu um erro ao carregar o jogo: {e}")
        return None, None

def check_save_file():
    """Verifica se o ficheiro de save existe."""
    return os.path.exists(SAVE_FILE)