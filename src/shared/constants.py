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
MONSTER_BASE_XP_REWARD = 45
MONSTER_BASE_COIN_REWARD = 30

# --- Mini-Bosses ---
# O chefe já custa 2,4x o orçamento do andar. Somar níveis a isso empilhava dois
# multiplicadores e transformava o andar 5 num muro, não num portão.
MINI_BOSS_LEVEL_BONUS = 1
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
# Divisor da agilidade no dano de veneno: quem é mais ágil sangra mais rápido.
POISON_AGILITY_DIVISOR = 5

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

# --- Stats Base de Heróis (nível 1) ---
# Os três perfis distribuem o mesmo orçamento de poder de ataque no nível 1
# (100 pontos, aplicando CLASS_WEIGHTS) de formas diferentes, e a diferença
# entre as classes está em HP, defesa e agilidade — não em quem bate mais.
# Antes, o Mago tinha 21,8x de crescimento de poder contra 5,6x do Guerreiro,
# porque o peso de classe alto dele multiplicava justamente o atributo que
# crescia mais rápido.
#
# O orçamento trocado entre os eixos é o que dá identidade: quem ganha em dano
# paga em sobrevivência, e o inverso. Poder de ataque no nível 1, aplicando
# CLASS_WEIGHTS, contra HP efetivo (HP vezes a mitigação da defesa):
#
#   Guerreiro:  54*1.6 + 30*0.4 =  98    EHP 440*1.32 = 581
#   Mago:       30*0.3 + 52*1.9 = 108    EHP 370*1.26 = 466
#   Ladino:     48*0.8 + 32*0.4 + 26*1.7 =  95   EHP 370*1.25 = 463 + esquiva
#
# A distância de HP efetivo entre a classe mais dura e a mais frágil é de 25%.
# Com 45%, que era a versão anterior destes números, o Guerreiro dominava a run:
# numa masmorra decidida por atrito, HP efetivo vale mais que pico de dano, e
# uma vantagem grande demais nesse eixo não é identidade, é dominância.
WARRIOR_BASE_HP = 440
WARRIOR_BASE_MP = 60
WARRIOR_BASE_ST = 54
WARRIOR_BASE_AG = 10
WARRIOR_BASE_MG = 30
WARRIOR_BASE_DF = 32

MAGE_BASE_HP = 370
MAGE_BASE_MP = 140
MAGE_BASE_ST = 30
MAGE_BASE_AG = 8
MAGE_BASE_MG = 52
MAGE_BASE_DF = 26

ROGUE_BASE_HP = 370
ROGUE_BASE_MP = 90
ROGUE_BASE_ST = 48
ROGUE_BASE_AG = 26
ROGUE_BASE_MG = 32
ROGUE_BASE_DF = 25

# --- Progressão de Level Up ---
# Todos os atributos de todas as classes crescem pela mesma razão GROWTH_RATE,
# a mesma que os monstros usam. As constantes por classe abaixo não são mais
# lidas pelo motor; ficam registradas porque documentam o modelo antigo, em que
# cada classe crescia a uma taxa própria e o herói divergia do monstro.
WARRIOR_HP_GROWTH_PERCENT = 20
WARRIOR_ST_GROWTH_PERCENT = 10

MAGE_HP_GROWTH_PERCENT = 8
MAGE_MP_GROWTH_PERCENT = 18
MAGE_MG_GROWTH_PERCENT = 18

ROGUE_ST_GROWTH_PERCENT = 16
ROGUE_AGILITY_GROWTH_PERCENT = 18
ROGUE_HP_GROWTH_PERCENT = 8
# Teto histórico de agilidade. Com a chance de acerto relativa ele deixou de ser
# necessário: a vantagem de agilidade é limitada pela própria fórmula, e travar
# o atributo no nível 12 congelava a identidade do Ladino.
AGILITY_CAP = 95

# Fórmulas
DAMAGE_FORMULA_DIVISOR = 3  # (ST + MG) // 3
SKILL_LEVEL_SCALING = 0.08  # +8% dano de skill por nível
# Custo de XP do nível 1 e razão de crescimento do custo. A razão é maior que
# GROWTH_RATE de propósito: o número de combates por nível sobe ao longo da run
# (cerca de 3 no nível 1, cerca de 14 no nível 19), então o herói fica
# progressivamente atrás do andar. É essa defasagem que cria dificuldade
# crescente, em vez de inflar os números do monstro.
XP_BASE_COST = 140
XP_LEVEL_RATIO = 1.195

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
# Chance de atordoar da skill Esmagar, nomeada porque o motor a aplica direto.
ESMAGAR_STUN_CHANCE = 30
# Nome da skill que carrega esse atordoamento embutido no motor.
ESMAGAR_SKILL_NAME = "Esmagar"
DAMAGE_REDUCTION_DURATION = 3  # turnos que dura a redução de dano
DAMAGE_REDUCTION_DEFAULT_PERCENT = 30  # % de dano reduzido

# --- Correção de balanceamento (auditoria PROMPT 3) ---
# Mini-boss coin agora tem base/escala dedicadas (antes reusava monster*3)
MINI_BOSS_BASE_COIN_REWARD = 80
MINI_BOSS_COIN_SCALING_PER_LEVEL = 15
# Essência com progressão suave por andar
ESSENCE_MULT_LEVEL_BONUS = 0.02  # +0.02 de média por andar
ESSENCE_MULT_MAX_BONUS = 0.4  # teto do bônus acumulado

# --- Laço de batalha ---
# Teto de turnos por batalha. Existe só como rede de segurança contra um empate
# infinito (dois lados que não conseguem se matar); nenhum combate balanceado
# deve chegar perto disso.
MAX_BATTLE_TURNS = 200

# =====================================================================
# MODELO DE ORÇAMENTO (rebalanceamento)
# =====================================================================
# Uma única razão de crescimento para herói e monstro. Antes, o herói crescia em
# percentual composto e o monstro em soma fixa: uma curva geométrica contra uma
# aritmética, que divergem para sempre por construção. Com a mesma razão dos dois
# lados, a razão poder-do-herói / HP-do-monstro fica constante ao longo dos 20
# níveis, e a dificuldade passa a ser controlada de propósito, não por acidente.
GROWTH_RATE = 1.12

# --- Orçamento do monstro (perfil "bruiser" no nível 1) ---
# Os arquétipos em content/factories/archetypes.py multiplicam estes valores.
MONSTER_BUDGET_HP = 420
MONSTER_BUDGET_ATTACK = 88
MONSTER_BUDGET_DEFENSE = 20
MONSTER_BUDGET_AGILITY = 8
MONSTER_BUDGET_MP = 60
# `Monster.avg_damage` é derivado de (st + mg) // DAMAGE_FORMULA_DIVISOR. Para
# que o ataque do orçamento apareça exatamente nesse valor, st e mg recebem
# metade do divisor cada: 1.5 = DAMAGE_FORMULA_DIVISOR / 2.
MONSTER_ATTACK_TO_STAT_RATIO = 1.5
# Abaixo desta fração da vida, um monstro com cura prioriza se curar.
MONSTER_HEAL_HP_RATIO = 0.5
# Papel usado quando nada mais é indicado (carregamento de save antigo, por exemplo).
DEFAULT_MONSTER_ROLE = "bruiser"

# --- Composição de encontros por profundidade ---
# Andares rasos mantêm inimigos isolados, para ensinar; grupos aparecem a partir
# de ENCOUNTER_GROUP_MIN_FLOOR e ficam maiores conforme a profundidade. Elites e
# chefes nunca entram em grupo: eles já são o encontro.
ENCOUNTER_GROUP_MIN_FLOOR = 4
ENCOUNTER_LARGE_GROUP_MIN_FLOOR = 10
ENCOUNTER_MAX_SIZE_SHALLOW = 1
ENCOUNTER_MAX_SIZE_MID = 2
ENCOUNTER_MAX_SIZE_DEEP = 3

# --- Acerto relativo ---
# A chance de acerto usa a diferença *relativa* de agilidade, não a absoluta.
# Com a diferença absoluta, uma agilidade que cresce sem teto zera a chance de o
# monstro acertar e a classe fica imune. Com a relativa, a vantagem de quem
# investe em agilidade é grande mas permanente e limitada.
HIT_AGILITY_SWING = 30  # pontos percentuais máximos que a agilidade move
HIT_CHANCE_FLOOR = 20   # nenhum defensor fica imune
HIT_CHANCE_CEIL = 95    # nenhum atacante fica infalível

# --- Efeitos de status ---
MANA_BURN_PER_TICK = 12       # MP drenado por turno por "mana_burn"
BLEED_DAMAGE_PERCENT = 4      # % do HP máximo por turno por "bleed"
INVISIBLE_HIT_PENALTY = 45    # pontos percentuais de acerto perdidos contra alvo invisível

# Duração, em turnos, dos buffs vindos de consumíveis.
POTION_BUFF_DURATION = 3
# Níveis em que o herói aprende as skills iniciais da classe, uma por nível.
INITIAL_SKILL_LEVELS = 4

# --- Descanso entre andares ---
# Concluir um andar devolve parte dos recursos. Não tudo: a cura completa a cada
# andar era uma das cinco fontes de cura gratuita que tornavam cada combate
# independente do anterior. Não zero: uma run de 20 andares em uma única barra
# de vida não é difícil, é impossível. O andar é a unidade de risco, e o que
# sobra de vida no fim dele é o que dá peso à decisão de extrair.
FLOOR_CLEAR_RESTORE_PERCENT = 29

# --- Level up ---
# Subir de nível restaura parte dos recursos, não tudo. Cura completa a cada
# nível era uma das cinco fontes de cura gratuita que zeravam o atrito da run.
LEVEL_UP_RESTORE_PERCENT = 30
