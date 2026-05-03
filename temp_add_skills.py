import json

# Lê o JSON atual
with open("src/data/skills.json", "r") as f:
    data = json.load(f)

# Novas skills para Warrior
new_warrior = [
    {"id": "cutelada", "name": "Cutelada", "skill_class": "Warrior", "level_required": 5, "mana_cost": 20, "effect_type": "damage", "effect_value": 35, "description": "Golpe amplo que atinge com força.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "provocacao", "name": "Provocação", "skill_class": "Warrior", "level_required": 5, "mana_cost": 15, "effect_type": "status", "effect_value": "taunt", "description": "Provoca inimigo (taunt) por 2 turnos.", "target": "enemy", "duration": 2, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "fortalecimento", "name": "Fortalecimento", "skill_class": "Warrior", "level_required": 7, "mana_cost": 25, "effect_type": "buff", "effect_value": 15, "description": "+15 Força por 4 turnos.", "target": "self", "duration": 4, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "golpe_duplo", "name": "Golpe Duplo", "skill_class": "Warrior", "level_required": 9, "mana_cost": 35, "effect_type": "damage", "effect_value": 45, "description": "Dois golpes rápidos.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "resistencia_heroica", "name": "Resistência Heróica", "skill_class": "Warrior", "level_required": 11, "mana_cost": 30, "effect_type": "buff", "effect_value": 10, "description": "+10% redução dano por 3 turnos.", "target": "self", "duration": 3, "chance": 100, "rarity": "Epic", "is_initial": False},
    {"id": "furia", "name": "Fúria", "skill_class": "Warrior", "level_required": 13, "mana_cost": 40, "effect_type": "buff", "effect_value": 20, "description": "+20 Força + crítico por 2 turnos.", "target": "self", "duration": 2, "chance": 100, "rarity": "Epic", "is_initial": False},
    {"id": "esmagar", "name": "Esmagar", "skill_class": "Warrior", "level_required": 15, "mana_cost": 50, "effect_type": "damage", "effect_value": 80, "description": "Golpe devastador com chance de atordoar.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Legendary", "is_initial": False},
    {"id": "imortal", "name": "Imortal", "skill_class": "Warrior", "level_required": 20, "mana_cost": 60, "effect_type": "buff", "effect_value": 1, "description": "Ignora morte 1 vez (1 turno).", "target": "self", "duration": 1, "chance": 100, "rarity": "Legendary", "is_initial": False},
]

# Novas skills para Mage
new_mage = [
    {"id": "relampago", "name": "Relâmpago", "skill_class": "Mage", "level_required": 5, "mana_cost": 30, "effect_type": "damage", "effect_value": 45, "description": "Raio elétrico que causa dano.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "barreira_arcana", "name": "Barreira Arcana", "skill_class": "Mage", "level_required": 5, "mana_cost": 25, "effect_type": "buff", "effect_value": 8, "description": "+8 redução dano por 3 turnos.", "target": "self", "duration": 3, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "explosao_arcana", "name": "Explosão Arcana", "skill_class": "Mage", "level_required": 7, "mana_cost": 40, "effect_type": "damage", "effect_value": 60, "description": "Explosão mágica em área.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "dreno_mana", "name": "Dreno de Mana", "skill_class": "Mage", "level_required": 9, "mana_cost": 30, "effect_type": "status", "effect_value": "mana_burn", "description": "Queima mana do inimigo.", "target": "enemy", "duration": 2, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "sono_profundo", "name": "Sono Profundo", "skill_class": "Mage", "level_required": 11, "mana_cost": 35, "effect_type": "status", "effect_value": "sleep", "description": "Adormece inimigo (70% chance).", "target": "enemy", "duration": 3, "chance": 70, "rarity": "Epic", "is_initial": False},
    {"id": "tempestade", "name": "Tempestade", "skill_class": "Mage", "level_required": 13, "mana_cost": 50, "effect_type": "damage", "effect_value": 75, "description": "Tormenta mágica devastadora.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Epic", "is_initial": False},
    {"id": "ressurgir", "name": "Ressurgir", "skill_class": "Mage", "level_required": 15, "mana_cost": 60, "effect_type": "heal", "effect_value": 100, "description": "Cura completa + revives.", "target": "self", "duration": 0, "chance": 100, "rarity": "Legendary", "is_initial": False},
    {"id": "apocalipse", "name": "Apocalipse", "skill_class": "Mage", "level_required": 20, "mana_cost": 70, "effect_type": "damage", "effect_value": 120, "description": "O fim de tudo.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Legendary", "is_initial": False},
]

# Novas skills para Rogue
new_rogue = [
    {"id": "golpe_sombras", "name": "Golpe nas Sombras", "skill_class": "Rogue", "level_required": 5, "mana_cost": 15, "effect_type": "damage", "effect_value": 30, "description": "Ataque furtivo das sombras.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "envenenar", "name": "Envenenar", "skill_class": "Rogue", "level_required": 5, "mana_cost": 20, "effect_type": "status", "effect_value": "poison", "description": "Veneno por 4 turnos.", "target": "enemy", "duration": 4, "chance": 100, "rarity": "Common", "is_initial": False},
    {"id": "passo_felino", "name": "Passo Felino", "skill_class": "Rogue", "level_required": 7, "mana_cost": 25, "effect_type": "buff", "effect_value": 20, "description": "+20 esquiva por 3 turnos.", "target": "self", "duration": 3, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "assassinato", "name": "Assassinato", "skill_class": "Rogue", "level_required": 9, "mana_cost": 40, "effect_type": "damage", "effect_value": 60, "description": "Golpe crítico (80% chance).", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Rare", "is_initial": False},
    {"id": "evasao_perfeita", "name": "Evasão Perfeita", "skill_class": "Rogue", "level_required": 11, "mana_cost": 30, "effect_type": "buff", "effect_value": 30, "description": "+30 esquiva por 2 turnos.", "target": "self", "duration": 2, "chance": 100, "rarity": "Epic", "is_initial": False},
    {"id": "danca_laminas", "name": "Dança das Lâminas", "skill_class": "Rogue", "level_required": 13, "mana_cost": 45, "effect_type": "damage", "effect_value": 70, "description": "Múltiplos golpes rápidos.", "target": "enemy", "duration": 0, "chance": 100, "rarity": "Epic", "is_initial": False},
    {"id": "fantasma", "name": "Fantasma", "skill_class": "Rogue", "level_required": 15, "mana_cost": 50, "effect_type": "buff", "effect_value": "invisible", "description": "Invisibilidade por 2 turnos.", "target": "self", "duration": 2, "chance": 100, "rarity": "Legendary", "is_initial": False},
    {"id": "morte_subita", "name": "Morte Súbita", "skill_class": "Rogue", "level_required": 20, "mana_cost": 80, "effect_type": "damage", "effect_value": 150, "description": "Chance de insta-kill (50%).", "target": "enemy", "duration": 0, "chance": 50, "rarity": "Legendary", "is_initial": False},
]

# Adiciona todas as novas skills
data["skills"].extend(new_warrior + new_mage + new_rogue)

# Escreve de volta
with open("src/data/skills.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Adicionadas {len(new_warrior + new_mage + new_rogue)} novas skills.")
print(f"Total de skills: {len(data['skills'])}")
