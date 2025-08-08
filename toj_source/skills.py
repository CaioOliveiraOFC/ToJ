#!/usr/bin/env python3

class Skill:
    """
    Classe base para habilidades, agora com tipos de efeito, alvos e durações.
    effect_type: 'damage', 'heal', 'status', 'buff'
    target: 'enemy', 'self'
    """
    def __init__(self, name, mana_cost, level_required, description, 
                 effect_type, target, value=0, duration=0, chance=100):
        self.name = name
        self.mana_cost = mana_cost
        self.level_required = level_required
        self.description = description
        self.effect_type = effect_type
        self.target = target
        self.value = value      # Para dano, cura ou aumento de status
        self.duration = duration  # Para efeitos que duram vários turnos
        self.chance = chance      # Chance de aplicar um efeito de status (ex: 80 para 80%)

# --- Habilidades de Guerreiro ---
warrior_skills = {
    1: Skill("Golpe Poderoso", 15, 1, "Um ataque focado que causa dano extra.",
             'damage', 'enemy', value=25),
    10: Skill("Grito de Guerra", 20, 10, "Aumenta seu dano de ataque por 3 turnos.",
              'buff', 'self', value=10, duration=3) # value = +10 de dano
}

# --- Habilidades de Mago ---
mage_skills = {
    1: Skill("Bola de Fogo", 25, 1, "Lança uma bola de fogo que causa dano mágico.",
             'damage', 'enemy', value=40),
    10: Skill("Raio Congelante", 20, 10, "50% de chance de congelar o inimigo por 1 turno.",
              'status', 'enemy', value='frozen', duration=2, chance=50), # Duração 2 para garantir 1 turno perdido
    20: Skill("Cura Menor", 35, 20, "Recupera uma porção da sua vida.",
              'heal', 'self', value=50)
}

# --- Habilidades de Ladino ---
rogue_skills = {
    1: Skill("Ataque Furtivo", 10, 1, "Um ataque rápido com alta chance de crítico.",
             'damage', 'enemy', value=20), # Dano base, mas terá bónus de crítico
    10: Skill("Lançar Adaga", 15, 10, "Lança uma adaga que envenena o inimigo por 3 turnos.",
              'status', 'enemy', value='poison', duration=3),
    20: Skill("Cortina de Fumaça", 25, 20, "Aumenta sua esquiva por 3 turnos.",
              'buff', 'self', value=20, duration=3) # value = +20 de agilidade para esquiva
}
