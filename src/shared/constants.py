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

# =====================================================================
# ECONOMIA
# =====================================================================
# "Ouro compra opções." O dinheiro do jogo precisa produzir decisão recorrente
# entre gastar para sobreviver, gastar para ficar mais forte, e guardar capital.
#
# O defeito que estas constantes corrigem era estrutural, não de valor: a renda
# crescia geometricamente (×1,12 por nível do monstro, e mais monstros por andar)
# e o preço crescia linearmente (+5% por andar). No andar 15 o jogador comprava a
# loja inteira, e a partir dali o ouro não comprava opção nenhuma.
#
# A âncora agora é uma só — a renda esperada do andar — e todo preço é proporção
# dela. As cinco constantes mortas que moravam aqui (`BASE_SHOP_PRICE`,
# `POTION/WEAPON/ARMOR_PRICE_MULTIPLIER`, `SHOP_DUNGEON_LEVEL_SCALING_DIVISOR`)
# foram removidas: nenhuma tinha um único leitor, e constante morta em arquivo de
# balanceamento é convite a calibrar o que não está ligado em lugar nenhum.

# --- Renda esperada do andar ---
# Medido no gerador real de andares: a renda de um andar, dividida pelo valor de
# um monstro do nível dele, vale 3,1 no andar 1, 9,2 no 10, 13,4 no 15 e para de
# crescer em ~14 do 16 em diante — é onde o plano de andar deixa de ganhar
# encontros. A reta abaixo reproduz a curva com erro < 8%.
FLOOR_INCOME_BASE_UNITS = 3.0
FLOOR_INCOME_UNITS_PER_FLOOR = 0.75
FLOOR_INCOME_MAX_UNITS = 14.0

# --- Juros ---
# Pagos ao concluir o andar, sobre o ouro que sobrou depois da loja. O cap é uma
# fração da renda do andar: rendimento nunca compete com jogar o andar, e como o
# cap cresce na curva da renda enquanto o juro composto cresceria mais rápido, a
# fortuna grande rende em linha reta e perde peso relativo. Não é dinheiro
# infinito; é a decisão "gasto agora ou mantenho capital?".
INTEREST_RATE_PERCENT = 5
INTEREST_CAP_INCOME_RATIO = 0.25

# --- Preço, em proporção à renda esperada do andar ---
# O `price` do JSON passa a ser o valor RELATIVO dentro da raridade; a escala
# absoluta vem daqui. O alvo de design é que o jogador encontre, no mesmo andar,
# coisas que consegue comprar, coisas que compraria sacrificando outra decisão, e
# coisas que ainda não alcança.
GEAR_PRICE_INCOME_RATIO = {
    "Common": 0.75,
    "Rare": 1.40,
    "Epic": 2.40,
    "Legendary": 5.00,
}
# Consumível tem tabela própria: pela raridade, uma poção pequena seria um
# equipamento Common, e ninguém compra três equipamentos Common por andar.
CONSUMABLE_PRICE_INCOME_RATIO = {
    "Common": 0.18,
    "Rare": 0.32,
    "Epic": 0.55,
    "Legendary": 0.90,
}

# --- Venda ---
# Era 0,5, e três chamadores nem liam a constante: usavam um `0.5` escrito à mão.
# A 50% o loot virava renda principal e acumular para revender era a estratégia
# dominante. Entre 20% e 25% a venda vira o que deve ser: válvula de descarte e
# recuperação parcial de valor. A variação dentro da faixa é derivada do id do
# item (ver `shared/economy.sell_factor`), não sorteada — o preço na tela e o
# preço pago têm de ser o mesmo número.
SELL_PRICE_MIN_FACTOR = 0.20
SELL_PRICE_MAX_FACTOR = 0.25

# --- Recuperação paga (entre andares, na loja) ---
# Combate ruim passa a ter consequência econômica sem virar sentença de morte: o
# jogador não precisa morrer por ter terminado mal um combate, mas talvez precise
# gastar parte da recompensa para reparar o dano. Cobrado sobre o que é de fato
# restaurado — quem está a 90% paga por 10%, não por um passo inteiro.
RECOVERY_STEP_PERCENT = 25
RECOVERY_HP_STEP_INCOME_RATIO = 0.22
RECOVERY_MP_STEP_INCOME_RATIO = 0.18

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
# Fração do BASE_POWER que sai num ataque básico.
#
# Valia 1.0: o ataque básico é gratuito, não tem recarga e entregava o poder
# inteiro, enquanto a skill custa mana, tem recarga e paga apenas
# `1 + effect_value/100` em cima do MESMO número. A skill de dano mediana do
# jogo (65%) valia 1,65 ataque de graça.
#
# ATENÇÃO ao que a medição mostrou, porque é o contrário do que parece: mexer
# só neste número NÃO tira o jogo do ataque básico. Medido a 250 runs por
# classe, com a regeneração de mana em zero, baixar de 1,0 para 0,9 move a
# fatia do dano vinda do básico de 35,9% para 35,2% — ou seja, nada — e derruba
# o Guerreiro de 9,2 para 8,1 andares. O herói não spamava básico porque o
# básico era forte; spamava porque ficava sem mana no terceiro turno. Quem
# conserta o spam é MP_REGEN_PERCENT_PER_TURN.
#
# O papel deste número é outro, e é indispensável: a regeneração sozinha
# (1,0 / 2%) leva a distância entre classes de 3,9 para 4,7 andares, acima do
# limite de 4,0, porque Guerreiro e Ladino aproveitam a mana nova e o Mago quase
# não muda. Com 0.90 junto, a distância cai para 3,4 e o Guerreiro fica
# exatamente onde estava (9,2). É o nerf que paga a regeneração.
BASIC_ATTACK_POWER_MULT = 0.90
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
# O sorteio da Essência dos cinco primeiros andares explicava 38,7% da variância
# da profundidade final da run: os 25% mais azarados paravam no andar 3,8 e os
# 25% mais sortudos no 16,2, uma distância de 12,4 andares decidida por um
# número que o jogador não controla. Para comparação, escolher carta de
# propósito em vez de sortear vale 1,5 andar. A run era da moeda, não do
# jogador.
#
# O desvio caiu de 0.5 para 0.2. A média não mudou, então o ritmo do jogo não
# muda: o andar médio vai de 9,49 para 9,19. O que muda é o peso da sorte —
# a variância explicada cai para 12,6% e a distância entre azarado e sortudo,
# para 7,3 andares.
#
# Medido também um desvio que cresce com o andar (sorte só onde ela não decide
# mais). Perdeu para o desvio fixo nos três eixos: 14,7% de variância explicada
# contra 12,6%, mesma distância, e andar médio menor. A ideia era melhor que o
# resultado.
#
# 0.12 leva a variância a 8,2%, mas o andar médio cai para 8,95 e a distância só
# melhora de 7,3 para 6,9: retorno decrescente, e a Essência vira constante.
# 0.2 é o joelho da curva.
ESSENCE_MULT_NORMAL_MEAN = 1.2  # Centro da curva gaussiana
ESSENCE_MULT_NORMAL_STD = 0.2  # Desvio padrão (controla variação)
# Limites do sorteio, a três desvios da média mais baixa e da mais alta. Antes
# eram 0.5 e 3.0, faixa herdada de um desvio de 0.5: com 0.2 esses extremos
# ficariam a mais de oito desvios, ou seja, nunca sairiam — e a tela de
# extração prometeria ao jogador uma faixa que o sorteio não entrega.
ESSENCE_MULT_MIN = 0.6
ESSENCE_MULT_MAX = 2.2
# Faixas de leitura na tela: um desvio abaixo da média é andar ruim, um desvio
# acima é andar bom. Derivadas, e não digitadas, para que mexer no desvio não
# deixe a cor da tela mentindo sobre o sorteio.
ESSENCE_MULT_POOR = round(ESSENCE_MULT_NORMAL_MEAN - ESSENCE_MULT_NORMAL_STD, 2)
ESSENCE_MULT_GOOD = round(ESSENCE_MULT_NORMAL_MEAN + ESSENCE_MULT_NORMAL_STD, 2)

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
# Esmagar teve as suas duas constantes removidas: o motor a atordoava por nome,
# em cima do `stun_chance` que a própria skill já declara no JSON. Valor de skill
# é dado, e mora no JSON — o motor lê, não redeclara.
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
# Abaixo desta fração da vida, o monstro entra em desespero: gasta o que tiver
# para não morrer de graça — defesa se for tank, o maior dano se não for.
MONSTER_DESPERATE_HP_RATIO = 0.35
# Acima desta fração de vida do herói o monstro não tenta executar. Abaixo dela,
# qualquer arquétipo com dano guardado usa a maior skill que tiver, ignorando a
# rolagem de `skill_use_chance`: um golpe que mata vale mais que a média.
MONSTER_EXECUTE_HP_RATIO = 0.35
# Limiares das condições de bônus das skills de dano. O mesmo 0.35 do execute
# do monstro: a regra vale para os dois lados da luta, e o jogador que aprendeu
# a ler o momento de execução do inimigo já sabe ler o seu.
# Mana de referência no nível 1, usada para converter o custo percentual de uma
# skill em pontos de MP. É a média das três classes (60, 140, 90).
#
# O custo é percentual DESTA curva, e não da mana de quem lança. Cobrar uma
# fração da mana própria fazia toda classe lançar o mesmo número de skills — dez
# — e apagava a reserva do Mago, que é a identidade dele: antes ele lançava 31
# skills contra 16 do Guerreiro. Como o dano das duas classes é praticamente
# igual e o Mago tem menos HP e menos defesa, tirar a mana o deixou estritamente
# pior que o Guerreiro.
#
# Com a referência comum, quem tem mana acima dela lança mais vezes, e o custo
# continua acompanhando a progressão geométrica em vez de virar irrelevante no
# fim do jogo.
SKILL_COST_REFERENCE_MP = 97

# --- Égide de Mana: a mitigação passiva do Mago ---
# Nome distinto da skill `Barreira Arcana`, que é um buff de defesa lançado pelo
# jogador. As duas são do Mago e as duas reduzem dano; o nome compartilhado só
# não confundia enquanto esta aqui era invisível.
# Cada classe tem a sua forma de não morrer. O Guerreiro absorve com HP e
# defesa; o Ladino evita com agilidade; o Mago não tinha nenhuma. Medido no
# nível 4: HP efetivo 760 contra 749 do Ladino, mas com agilidade 11 contra 38 —
# ou seja, a mesma vida sem a esquiva que a compensa, e apenas +5% de dano sobre
# o Guerreiro para pagar por 20% menos vida que ele. O resultado é que o Mago
# morria no andar 4 contra os encontros mais banais do jogo, enquanto as outras
# classes chegavam ao 6 e ao 7.
#
# A reserva de mana era a compensação escrita, e ela só paga em luta longa — o
# Mago morria antes de a reserva valer alguma coisa. A barreira converte mana em
# sobrevivência imediata e faz a reserva pesar desde o primeiro andar.
#
# Fração máxima de um golpe que a barreira pode absorver. Calibrada por
# varredura contra o espalhamento de profundidade entre as três classes, com
# 200 runs por ponto — o 35 que veio antes dela era chute e levava o Mago de
# último a primeiro, de 9,1 para 18,5 andares:
#
#      0%  Guerreiro 15,5  Mago  9,3  Ladino 14,6   espalhamento 6,20
#     10%                  Mago 14,5                espalhamento 1,07
#     15%                  Mago 15,2                espalhamento 0,98
#     20%                  Mago 17,3                espalhamento 2,69
#
# Em 15% o espalhamento fica abaixo da margem de erro da própria medição
# (±0,95 com essa amostra): as três classes empatam dentro do que a simulação
# consegue distinguir, que é o alvo — não um número redondo.
MAGIC_SHIELD_ABSORB_PERCENT = 15
# Dano absorvido por ponto de mana. É o preço da conversão, e é ele que cria a
# decisão: mana gasta aguentando não lança skill.
MAGIC_SHIELD_DAMAGE_PER_MP = 2.0

SKILL_BONUS_WOUNDED_RATIO = 0.35
SKILL_BONUS_HEALTHY_RATIO = 0.80
# Quantos turnos do início do combate contam como abertura. Um buff de defesa
# lançado no primeiro turno de uma luta de dez rende os três turnos inteiros;
# lançado no oitavo, rende um. Tank, elite, chefe e suporte abrem buffando.
MONSTER_OPENER_TURNS = 1
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
HIT_CHANCE_FLOOR = 20  # nenhum defensor fica imune
HIT_CHANCE_CEIL = 95  # nenhum atacante fica infalível

# --- Efeitos de status ---
MANA_BURN_PER_TICK = 12  # MP drenado por turno por "mana_burn"
BLEED_DAMAGE_PERCENT = 4  # % do HP máximo por turno por "bleed"
INVISIBLE_HIT_PENALTY = 45  # pontos percentuais de acerto perdidos contra alvo invisível

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
# Mana devolvida por turno de combate, em % do MP máximo.
#
# Valia 0: a única mana do combate era a do pool, e a única recarga era o
# descanso de fim de andar (FLOOR_CLEAR_RESTORE_PERCENT). O Guerreiro entra no
# nível 1 com 60 de MP e a Investida custa 20 — três usos e acabou. Medido: 2,2
# skills por combate de doze turnos, e 36% do dano do herói saindo do ataque
# básico. Isso não é o jogador escolhendo bater; é o jogador sem alternativa, e
# um combate cuja melhor jogada é sempre a mesma não admite adaptação.
#
# Com regeneração por turno, a mana deixa de ser um estoque que se gasta uma vez
# e vira ritmo: dá para bater agora e pagar a skill grande dali a três turnos.
# A 2%, o básico cai de 36% para 17% do dano, o herói passa a soltar 3,1 skills
# por combate, e o Mago passa a usar duas skills diferentes em vez de uma —
# o "spam de uma skill só" era, na origem, falta de recurso para uma segunda.
#
# 2% e não mais: a 3% o Guerreiro sobe para 11,3 andares e a distância entre
# classes vai a 5,6, acima do limite de 4,0. A regeneração é forte demais para
# ser dada sozinha; ela vem acompanhada do nerf em BASIC_ATTACK_POWER_MULT.
#
# Vale para monstro também, e é o que sustenta o arquétipo num combate longo:
# um tank sem mana no turno 8 volta a ser um saco de pancada.
MP_REGEN_PERCENT_PER_TURN = 2

# 29 → 25: o descanso gratuito continua existindo (uma run de 20 andares numa
# única barra de vida não é difícil, é impossível), mas perde força para abrir
# espaço à recuperação paga. Se o andar sempre devolvesse o suficiente, gastar
# ouro em cura nunca seria decisão — e "combate ruim custa dinheiro" é metade do
# que faz o ouro comprar opções.
FLOOR_CLEAR_RESTORE_PERCENT = 25

# --- Level up ---
# Subir de nível restaura parte dos recursos, não tudo. Cura completa a cada
# nível era uma das cinco fontes de cura gratuita que zeravam o atrito da run.
LEVEL_UP_RESTORE_PERCENT = 30
