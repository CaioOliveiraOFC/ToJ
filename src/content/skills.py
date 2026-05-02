#!/usr/bin/env python3

class Skill:
    """Classe base para habilidades com tipos de efeito, alvos e durações.

    Args:
        name: Nome da habilidade.
        mana_cost: Custo de mana para usar a habilidade.
        level_required: Nível necessário para aprender a habilidade.
        description: Descrição da habilidade.
        effect_type: Tipo de efeito ('damage', 'heal', 'status', 'buff').
        target: Alvo da habilidade ('enemy', 'self').
        value: Valor do efeito (dano, cura ou aumento de status).
        duration: Duração do efeito em turnos (0 para efeitos instantâneos).
        chance: Chance de aplicar efeito de status (0-100).

    Attributes:
        name: Nome da habilidade.
        mana_cost: Custo de mana.
        level_required: Nível necessário.
        description: Descrição da habilidade.
        effect_type: Tipo de efeito.
        target: Alvo da habilidade.
        value: Valor do efeito.
        duration: Duração em turnos.
        chance: Chance de aplicar efeito (%).
    """

    def __init__(
        self,
        name: str,
        mana_cost: int,
        level_required: int,
        description: str,
        effect_type: str,
        target: str,
        value: int | str = 0,
        duration: int = 0,
        chance: int = 100
    ) -> None:
        self.name: str = name
        self.mana_cost: int = mana_cost
        self.level_required: int = level_required
        self.description: str = description
        self.effect_type: str = effect_type
        self.target: str = target
        self.value: int | str = value
        self.duration: int = duration
        self.chance: int = chance

# --- Habilidades de Guerreiro ---
warrior_skills = {
    1: [
        Skill("Golpe Poderoso", 15, 1, "Um ataque focado que causa dano extra.",
              'damage', 'enemy', value=25),
        Skill("Investida", 20, 1, "Carrega contra o inimigo com força bruta.",
              'damage', 'enemy', value=30),
        Skill("Escudo Protetor", 25, 1, "Levanta um escudo que aumenta sua defesa por 3 turnos.",
              'buff', 'self', value=8, duration=3),
        Skill("Grito de Guerra", 20, 1, "Aumenta seu dano de ataque por 3 turnos.",
              'buff', 'self', value=10, duration=3),
    ],
    10: Skill("Golpe Devastador", 30, 10, "Um ataque extremamente poderoso que causa dano massivo.",
              'damage', 'enemy', value=50),
}

# --- Habilidades de Mago ---
mage_skills = {
    1: [
        Skill("Bola de Fogo", 25, 1, "Lança uma bola de fogo que causa dano mágico.",
              'damage', 'enemy', value=40),
        Skill("Míssil Mágico", 20, 1, "Lança um míssil de energia pura.",
              'damage', 'enemy', value=35),
        Skill("Drenar Vida", 30, 1, "Drena a vida do inimigo e recupera sua própria vida.",
              'heal', 'self', value=25),
        Skill("Escudo Mágico", 25, 1, "Cria um escudo mágico que reduz dano recebido por 3 turnos.",
              'buff', 'self', value=5, duration=3),
    ],
    10: Skill("Raio Congelante", 20, 10, "50% de chance de congelar o inimigo por 1 turno.",
              'status', 'enemy', value='frozen', duration=2, chance=50),
    20: Skill("Cura Menor", 35, 20, "Recupera uma porção da sua vida.",
              'heal', 'self', value=50)
}

# --- Habilidades de Ladino ---
rogue_skills = {
    1: [
        Skill("Ataque Furtivo", 10, 1, "Um ataque rápido com alta chance de crítico.",
              'damage', 'enemy', value=20),
        Skill("Golpe Baixo", 15, 1, "Um golpe sujo que reduz a defesa do inimigo por 2 turnos.",
              'status', 'enemy', value='weakened', duration=2),
        Skill("Evasão", 20, 1, "Aumenta sua agilidade e esquiva por 3 turnos.",
              'buff', 'self', value=15, duration=3),
        Skill("Sombra Rápida", 18, 1, "Desaparece nas sombras, aumentando sua chance de esquiva.",
              'buff', 'self', value=12, duration=2),
    ],
    10: Skill("Lançar Adaga", 15, 10, "Lança uma adaga que envenena o inimigo por 3 turnos.",
              'status', 'enemy', value='poison', duration=3),
    20: Skill("Cortina de Fumaça", 25, 20, "Aumenta sua esquiva por 3 turnos.",
              'buff', 'self', value=20, duration=3)
}
