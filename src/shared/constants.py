"""Constantes globais do jogo — eliminam números mágicos."""

# Dimensões base do mapa
BASE_MAP_HEIGHT = 12
BASE_MAP_WIDTH = 25

# Incrementos por nível de masmorra
MAP_HEIGHT_INCREMENT_PER_5_LEVELS = 2
MAP_WIDTH_INCREMENT_PER_5_LEVELS = 4

# Configuração de paredes (geração de mapa)
MIN_WALL_PERCENT = 0.05
MAX_WALL_PERCENT = 0.20
WALL_PERCENT_PER_LEVEL = 0.01
MAX_WALL_PERCENT_CAP = 0.15  # Limite máximo de paredes por nível

# Intervalos de tempo (UX)
SLEEP_AFTER_SAVE = 0.5
SLEEP_SHORT_PAUSE = 0.3
SLEEP_MENU_REFRESH = 0.5
SLEEP_GAME_OVER = 0.8

# --- Estatísticas de Monstros ---
MONSTER_BASE_HP = 100
MONSTER_HP_SCALING_PER_LEVEL = 20
MONSTER_BASE_STRENGTH = 25
MONSTER_STRENGTH_SCALING_PER_LEVEL = 15
MONSTER_BASE_DEFENSE = 20
MONSTER_DEFENSE_SCALING_PER_LEVEL = 8
MONSTER_BASE_MAGIC = 40
MONSTER_MAGIC_SCALING_PER_LEVEL = 12

# Stats base para instanciamento de monstros
MONSTER_BASE_ST = 55
MONSTER_BASE_MP = 40
MONSTER_BASE_AG = 3
MONSTER_BASE_MG = 50
MONSTER_BASE_DF = 30

# --- Sistema de XP e Moedas ---
XP_INITIAL_COST = 3000
XP_GROWTH_PER_LEVEL = 750
MONSTER_BASE_XP_REWARD = 50
MONSTER_XP_SCALING_PER_LEVEL = 20
MONSTER_BASE_COIN_REWARD = 30
MONSTER_COIN_SCALING_PER_LEVEL = 10
MINI_BOSS_COIN_MULTIPLIER = 3

# --- Mini-Bosses ---
MINI_BOSS_LEVEL_BONUS = 2
MINI_BOSS_BASE_HP = 150
MINI_BOSS_HP_SCALING_PER_LEVEL = 40
MINI_BOSS_BASE_STRENGTH = 80
MINI_BOSS_STRENGTH_SCALING_PER_LEVEL = 30
MINI_BOSS_BASE_DEFENSE = 45
MINI_BOSS_DEFENSE_SCALING_PER_LEVEL = 10
MINI_BOSS_BASE_MAGIC = 75
MINI_BOSS_MAGIC_SCALING_PER_LEVEL = 18
MINI_BOSS_BASE_XP_REWARD = 120
MINI_BOSS_XP_SCALING_PER_LEVEL = 25

# --- Sistema de Raridade ---
RARITY_MULTIPLIERS = {
    "Common": 1.0,
    "Rare": 1.15,
    "Epic": 1.32,  # ~1.15 * 1.15
    "Legendary": 1.52,  # ~1.15 * 1.15 * 1.15
}

# --- Sistema de Economia (Loja) ---
BASE_SHOP_PRICE = 10
POTION_PRICE_MULTIPLIER = 2
WEAPON_PRICE_MULTIPLIER = 10
ARMOR_PRICE_MULTIPLIER = 10
SHOP_DUNGEON_LEVEL_SCALING_DIVISOR = 20
SELL_PRICE_FACTOR = 0.5

# --- Mecânicas de Combate ---
CRIT_CHANCE_HIGH = 25  # Para Rogue com Ataque Furtivo
CRIT_CHANCE_DEFAULT = 10
BASE_HIT_CHANCE = 85
POISON_DAMAGE_PER_TICK = 5

# Ranges e cálculos de combate
PERCENTAGE_RANGE_MIN = 1
PERCENTAGE_RANGE_MAX = 101  # randrange(1, 101) = 1-100
FLEE_RANGE_MAX = 2  # randrange(0, 2) = 0 ou 1 (50% chance)

# --- COMBAT_DESIGN.md: Constantes de Calibração ---
DEFENSE_K = 100  # Curva de mitigação: k/(k+defense)
XMULT_CAP = 5.0  # Teto de multiplicadores puros
CRIT_CHANCE_CAP = 75  # % máximo de chance crítica
CRIT_DAMAGE_BASE = 1.5  # Multiplicador padrão de crítico

# Matriz de pesos por classe (Fórmula Universal de Dano)
CLASS_WEIGHTS = {
    "Warrior": {"st": 1.6, "mg": 0.4, "ag": 0.0},
    "Mage": {"st": 0.3, "mg": 1.9, "ag": 0.0},
    "Rogue": {"st": 0.8, "mg": 0.4, "ag": 1.7},
}

# --- Configurações de Mapa ---
DEFAULT_WALL_PERCENTAGE = 0.2
MAP_BORDER_OFFSET = 1  # Offset para evitar bordas
MIN_EMPTY_TILES_START = 1

# --- Stats Base de Heróis ---
# Balanceado: Mage buff minimo (96->99, 23->25) para corrigir 5 andares de gap
WARRIOR_BASE_HP = 104
WARRIOR_BASE_MP = 30
WARRIOR_BASE_ST = 104
WARRIOR_BASE_AG = 5
WARRIOR_BASE_MG = 30
WARRIOR_BASE_DF = 30

MAGE_BASE_HP = 99
MAGE_BASE_MP = 100
MAGE_BASE_ST = 32
MAGE_BASE_AG = 5
MAGE_BASE_MG = 100
MAGE_BASE_DF = 25

ROGUE_BASE_HP = 99
ROGUE_BASE_MP = 50
ROGUE_BASE_ST = 75
ROGUE_BASE_AG = 15
ROGUE_BASE_MG = 66
ROGUE_BASE_DF = 20

# --- Progressão de Level Up ---
# Balanceado: Mage ganha HP growth 8 (antes 0)
WARRIOR_HP_GROWTH_PERCENT = 20
WARRIOR_ST_GROWTH_PERCENT = 10

MAGE_HP_GROWTH_PERCENT = 8
MAGE_MP_GROWTH_PERCENT = 18
MAGE_MG_GROWTH_PERCENT = 18

ROGUE_ST_GROWTH_PERCENT = 16
ROGUE_AGILITY_GROWTH_PERCENT = 18
ROGUE_HP_GROWTH_PERCENT = 8
AGILITY_CAP = 95

# Fórmulas
DAMAGE_FORMULA_DIVISOR = 3  # (ST + MG) // 3
SKILL_LEVEL_SCALING = 0.08  # +8% dano de skill por nível
XP_BASE_COST = 100
XP_EXPONENT = 1.5  # level ** 1.5

# --- Multiplicador de Essência por Andar ---
ESSENCE_MULT_MIN = 0.5
ESSENCE_MULT_MAX = 3.0
ESSENCE_MULT_NORMAL_MEAN = 1.2   # Centro da curva gaussiana
ESSENCE_MULT_NORMAL_STD = 0.5    # Desvio padrão (controla variação)

# Pesos de raridade para sorteio de passivas
PASSIVE_COMMON_WEIGHT = 60
PASSIVE_RARE_WEIGHT = 28
PASSIVE_EPIC_WEIGHT = 10
PASSIVE_LEGENDARY_WEIGHT = 2

# --- Eventos Aleatórios de Masmorra (TASK-005) ---
# Probabilidade de um evento especial ao entrar num andar (antes da extração)
RANDOM_EVENT_CHANCE = 0.25  # 25% — equilíbrio entre surpresa e previsibilidade
RANDOM_EVENT_MERCHANT_MIN_ITEMS = 1
RANDOM_EVENT_MERCHANT_MAX_ITEMS = 3
RANDOM_EVENT_ALTAR_HP_COST_PERCENT = 30  # % da vida máxima sacrificada
RANDOM_EVENT_ALTAR_BUFF_VALUE = 15
RANDOM_EVENT_ALTAR_BUFF_DURATION = 5  # turnos de combate
RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT = 50  # % da vida máxima curada

# --- Novos sistemas de combate (TASK-006) ---
DEFAULT_SKILL_COOLDOWN = 0  # sem cooldown por padrão
STUN_DURATION = 1  # turnos perdidos quando atordoado
STUN_CHANCE_DEFAULT = 15  # % base para aplicar stun em ações com stun
DAMAGE_REDUCTION_DURATION = 3  # turnos que dura a redução de dano
DAMAGE_REDUCTION_DEFAULT_PERCENT = 30  # % de dano reduzido

# --- Correção de balanceamento (auditoria PROMPT 3) ---
# Mini-boss coin agora tem base/escala dedicadas (antes reusava monster*3)
MINI_BOSS_BASE_COIN_REWARD = 80
MINI_BOSS_COIN_SCALING_PER_LEVEL = 15
# Essência com progressão suave por andar
ESSENCE_MULT_LEVEL_BONUS = 0.02  # +0.02 de média por andar
ESSENCE_MULT_MAX_BONUS = 0.4  # teto do bônus acumulado
