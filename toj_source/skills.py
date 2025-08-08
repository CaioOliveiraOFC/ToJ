#!/usr/bin/env python3

class Skill:
    """
    Classe base para todas as habilidades, agora com nível requerido.
    """
    def __init__(self, name, damage, mana_cost, level_required, description):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.level_required = level_required
        self.description = description

# --- Habilidades de Guerreiro ---
# Um dicionário para guardar todas as habilidades que um Guerreiro pode aprender.
# A chave é o nível em que a habilidade é aprendida.
warrior_skills = {
    1: Skill("Golpe Poderoso", 25, 15, 1, "Um ataque devastador que consome mana."),
    10: Skill("Grito de Guerra", 0, 20, 10, "Aumenta o seu ataque no próximo turno."),
    20: Skill("Frenesi", 0, 30, 20, "Aumenta sua velocidade, permitindo atacar duas vezes."),
    35: Skill("Golpe Sísmico", 70, 40, 35, "Atinge o chão, causando dano a todos os inimigos (efeito futuro)."),
    50: Skill("Executar", 150, 60, 50, "Um golpe finalizador massivo.")
}

# --- Habilidades de Mago ---
mage_skills = {
    1: Skill("Bola de Fogo", 40, 25, 1, "Lança uma bola de fogo que causa dano mágico massivo."),
    10: Skill("Raio Congelante", 30, 20, 10, "Atinge o inimigo com gelo, reduzindo sua velocidade."),
    20: Skill("Cura Menor", -50, 35, 20, "Recupera uma porção da sua vida (-50 de dano = 50 de cura)."),
    35: Skill("Tempestade de Raios", 90, 50, 35, "Invoca uma tempestade que atinge todos os inimigos."),
    50: Skill("Meteoro", 200, 80, 50, "Chama um meteoro dos céus para aniquilar o alvo.")
}

# --- Habilidades de Ladino ---
rogue_skills = {
    1: Skill("Ataque Furtivo", 20, 10, 1, "Um ataque rápido que ignora parte da defesa."),
    10: Skill("Lançar Adaga", 30, 15, 10, "Lança uma adaga envenenada no inimigo."),
    20: Skill("Cortina de Fumaça", 0, 25, 20, "Aumenta sua chance de esquivar no próximo turno."),
    35: Skill("Apunhalar", 80, 40, 35, "Um ataque preciso em um ponto vital do inimigo."),
    50: Skill("Chuva de Lâminas", 120, 55, 50, "Lança múltiplas lâminas em todos os inimigos.")
}