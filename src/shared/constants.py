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


# --- Estatísticas de Monstros ---
MONSTER_BASE_HP = 100

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
MINI_BOSS_BASE_XP_REWARD = 120

# --- Sistema de Raridade ---
# Quanto cada rank de aprimoramento (+N) vale. Entra numa raiz quadrada, e não
# numa razão: `1 + taxa * sqrt(N)` cresce para sempre, mas cada rank rende menos
# que o anterior, então +1000 é forte sem ser absurdo (5,7x a base).
#
# Raiz e não logaritmo porque o log entrega quase tudo no primeiro rank — o +1
# valeria mais que os ranks 10 a 100 somados, e uma escada de upgrade em que o
# primeiro degrau é o melhor negócio é uma escada quebrada.
ENHANCEMENT_RATE = 0.15

# Quantos sockets um EXEMPLAR recebe ao nascer, por raridade. Cada tupla é a
# distribuição de 0, 1, 2 e 3 sockets, em pontos percentuais somando 100.
#
# É sorteio do exemplar, e não propriedade do item-base: duas Espadas Rare podem
# nascer com 1 e com 3 encaixes, e é isso que faz um drop valer mais que outro
# drop da mesma peça. Sem isso, "melhor item" seria só uma questão de raridade.
#
# A filosofia importa mais que os números, e é ela que deve sobreviver a um
# rebalanceamento: em Rare, 3 sockets é excepcional; em Epic, 2 é o caso comum e
# 3 já aparece; em Legendary, 3 é o esperado.
SOCKET_WEIGHTS_BY_RARITY: dict[str, tuple[int, int, int, int]] = {
    "Common": (100, 0, 0, 0),
    "Rare": (0, 70, 25, 5),
    "Epic": (0, 30, 50, 20),
    "Legendary": (0, 10, 30, 60),
}

# Teto de encaixes. Um quarto socket é decisão de conteúdo, não de código.
MAX_SOCKETS = 3

# Quanto o nível de uma gema vale, em pontos percentuais do atributo.
#
# Entra num logaritmo, e NÃO na mesma raiz que `+N` usa: os dois sistemas são
# independentes, e a forma de cada um segue de como o jogador o obtém. Rank de
# item se compra um degrau por vez, então precisa de passos parecidos — daí a
# raiz. Nível de gema se ENCONTRA: a gema inteira é substituída por outra
# melhor, e nunca se paga do Nv.7 para o Nv.8. Aí o salto grande no começo é
# virtude: achar o primeiro Rubi tem que ser um acontecimento.
GEM_RATE = 6.0

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
# Não mora mais aqui. Eram três constantes de uma RETA ajustada à mão, com platô
# em 14 unidades a partir do andar 16 — calibrada contra um plano de andar do
# simulador que levava 14 lutas ao andar 20 contra os 10 monstros que o jogo
# gera. Hoje as unidades vêm da população real (`content/economy.py`, a partir de
# `content/factories/monsters.py`), e não há número a calibrar: se o gerador
# mudar, a renda segue junto. O platô era o pior deles — no andar 50 a reta
# pagava 24% a MENOS que o andar, porque o jogo continuava crescendo e ela não.

# --- Reroll ---
# Comprar outra amostra do RNG: loja, oferta de skill e oferta de passiva usam
# esta mesma curva. O primeiro reroll custa uma fração da renda do andar e cada
# um seguinte DOBRA.
#
# Não existe teto de tentativas, e é de propósito: o jogador que está numa run
# ruim pode tentar mais uma, e mais uma, e a essa altura já investiu demais para
# parar. Quem segura não é uma regra, é o próprio custo — no quinto reroll ele
# já paga 2,4 andares inteiros. Um teto artificial tiraria a decisão; o custo
# exponencial a devolve, e o preço dela é o capital que iria para equipamento,
# consumível ou recuperação.
REROLL_FIRST_INCOME_RATIO = 0.15
REROLL_COST_GROWTH = 2.0

# --- Saída do andar e penalidade de Essência ---
# Sair custa. É o que dá preço a atravessar o andar sem lutar: contornar todo
# mundo continua possível, e continua pagando a taxa com capital que o combate
# não repôs.
EXIT_FEE_INCOME_RATIO = 0.30

# Quem não consegue pagar sobe do mesmo jeito. Não há dívida, não há bloqueio e
# não há softlock: a run continua, e vai ficando menos eficiente. Cada saída
# NÃO PAGA consecutiva tira isto do multiplicador de Essência do andar seguinte.
ESSENCE_UNPAID_EXIT_PENALTY = 0.20
# E o piso é absoluto: por maior que seja a sequência, a Essência efetiva nunca
# cai abaixo disto. É o que impede a punição de virar espiral sem volta — quem
# está em 0,5x continua ganhando o suficiente para voltar a lutar e pagar.
ESSENCE_PENALTY_FLOOR = 0.5

# --- Features do mapa ---
# Loja, Ferreiro e Extração deixaram de ser garantidos e viraram casas do mapa.
# Cada um tem chance própria e um "pity" que sobe a cada andar sem aparecer, até
# forçar o encontro. O pity existe para o jogador não ficar refém da moeda: uma
# seca longa de Loja não pode ser o que encerra a run.
SHOP_SPAWN_CHANCE = 0.35
SHOP_PITY_INCREMENT = 0.15
FORGE_SPAWN_CHANCE = 0.30
FORGE_PITY_INCREMENT = 0.15
# Extração é a saída de emergência da run, e não existe nos primeiros andares:
# antes disso não há o que preservar.
EXTRACTION_MIN_FLOOR = 3
EXTRACTION_SPAWN_CHANCE = 0.15
EXTRACTION_PITY_INCREMENT = 0.10

# --- Chave de Extração ---
# A casa `E` deixou de ser suficiente por si. Antes desta regra, extrair era
# grátis, repetível e nem sequer encerrava a run: o laço não tratava o desfecho,
# a casa não era consumida, e ir até o `E` era estritamente dominante sempre que
# ele aparecesse. Não havia decisão a tomar — só a sorte de o `E` nascer.
#
# A CHAVE é o que devolve a decisão ao jogador. Ela cai de monstro derrotado, e
# só de lá: não se compra, não se vende, nenhum serviço a oferece. Quem quer a
# saída de emergência precisa ter LUTADO por ela.
#
# Teto de UMA. Sem teto, a chave viraria estoque e a extração voltaria a ser
# garantida para quem lutou bastante — exatamente o que esta regra remove.
#
# Os 15% são valor INICIAL, para a mecânica ser jogável. Não são balanceamento:
# a medição vem na rodada global.
EXTRACTION_KEY_DROP_CHANCE = 0.15
EXTRACTION_KEY_MAX = 1

# --- Ferreiro ---
# Três serviços, três curvas, e todas ancoradas na renda do andar ou no preço da
# peça. Nenhuma tem teto: o soft cap é o próprio custo.
#
# `+N` cobra sobre o PREÇO DO ITEM, e não sobre a renda do andar, porque
# aprimorar uma Espada Épica não pode custar o mesmo que aprimorar uma Adaga
# Comum — o que se está comprando é uma fração do valor daquela peça.
ENHANCEMENT_COST_ITEM_RATIO = 0.35
ENHANCEMENT_COST_GROWTH = 1.50

# Gema entra e sai por uma fração da renda do andar. Retirar custa metade de
# engastar, e a pedra nunca quebra: a troca é uma decisão de build, não uma
# aposta. Quem aposta é o encantamento.
SOCKET_COST_INCOME_RATIO = 0.10
UNSOCKET_COST_INCOME_RATIO = 0.05

# Encantar é caro desde o primeiro e dobra por camada: 50%, 100%, 200%, 400%,
# 800% da renda do andar. Reencantar paga o custo da POSIÇÃO, e é gamble puro —
# não garante efeito diferente nem valor maior.
ENCHANT_FIRST_INCOME_RATIO = 0.50
ENCHANT_COST_GROWTH = 2.0

# Chance de uma gema cair numa vitória. Rolagem INDEPENDENTE do loot de item: o
# monstro pode dropar os dois na mesma morte, e a gema não ocupa o lugar do item.
GEM_DROP_CHANCE = 0.05
# Teto de nível da gema encontrada, por profundidade: `1 + andar // 5`. Bem mais
# lento que o andar, e de propósito — com `1..andar` o andar 20 já entregaria uma
# pedra Nv.20 e o sistema entraria no jogo com poder que ninguém mediu.
GEM_LEVEL_FLOORS_PER_RANK = 5

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

# --- Constantes de calibração de combate (ver GAME_DESIGN.md) ---
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
# =====================================================================
# SKILLS V2
# =====================================================================

# Quantas skills ativas o personagem carrega. Quatro, como um time de Pokémon:
# o limite é o que transforma "aprendi mais uma" em "abri mão de qual?".
MAX_ACTIVE_SKILLS = 4

# De quantos em quantos níveis o jogo oferece uma escolha de skill. O nível 1
# não entra: ele é a assinatura fixa da classe, não um sorteio.
SKILL_OFFER_LEVEL_INTERVAL = 3

# Quantas cartas por oferta.
SKILL_OFFER_SIZE = 3

# Atributos que uma skill pode usar como escala, e o teto de quantos.
SKILL_SCALING_STATS = ("st", "mg", "ag", "df", "hp", "mp")
MAX_SCALING_STATS = 2

# Faixa segura do modificador de acerto da própria ação. Fora dela, uma carta
# sozinha decidiria o acerto do jogo inteiro — e o clamp global viraria fachada.
SKILL_ACCURACY_RANGE = (-30, 20)

# Personagem de REFERÊNCIA do validador: atributos resolvidos de cada classe no
# nível 12 com o loadout `expected`, medidos uma vez.
#
# Existe porque o orçamento precisa ser comparável entre classes, e `power`
# sozinho não é: a Agilidade do Ladino vale 92 onde a Força do Guerreiro vale
# 191, então a mesma "pancada pesada" exige `power` quase o dobro nele. Sem uma
# referência comum, o validador puniria o Ladino por um detalhe da planilha.
#
# São dados de calibração, não de gameplay: nada no combate lê isto.
SKILL_REFERENCE_STATS: dict[str, dict[str, int]] = {
    "Warrior": {"st": 191, "mg": 116, "ag": 38, "df": 144, "hp": 1586, "mp": 318, "avg": 411},
    "Mage": {"st": 107, "mg": 202, "ag": 34, "df": 117, "hp": 1342, "mp": 674, "avg": 482},
    "Rogue": {"st": 170, "mg": 111, "ag": 92, "df": 111, "hp": 1342, "mp": 451, "avg": 394},
}
# Skill Neutral é avaliada contra a MÉDIA das classes: ela não pertence a
# nenhuma, e medi-la contra a mais fraca seria dar-lhe teto de graça.
SKILL_REFERENCE_NEUTRAL = {
    stat: sum(r[stat] for r in SKILL_REFERENCE_STATS.values()) // len(SKILL_REFERENCE_STATS)
    for stat in ("st", "mg", "ag", "df", "hp", "mp", "avg")
}

# Teto de orçamento, medido em % do ataque básico da referência da classe.
#
# DERIVADO do catálogo, não escolhido: as cartas existentes vão de -60 (utilidade
# pura) a 373, e as duas mais caras são as capstones Legendary — Morte Súbita e
# Apocalipse. 400 acomoda o que o jogo já tem com ~7% de folga e ainda recusa o
# absurdo, que é o serviço que um guardrail presta. Um teto que reprovasse as
# capstones existentes seria balancear pelo validador, e isto não é balanceamento.
#
# Neutral tem teto menor de propósito, e o número também sai do catálogo: 250
# fica abaixo das seis cartas de classe mais caras, então uma ferramenta
# universal nunca é a melhor opção ofensiva de ninguém — que é o que a impede de
# virar uma quarta classe.
MAX_OFFENSIVE_BUDGET = 400
MAX_OFFENSIVE_BUDGET_NEUTRAL = 250

# Nível em que o monstro de referência é medido pelo validador. O mesmo 12 do
# herói, e pelo mesmo motivo: o meio da curva, onde os atributos já se
# diferenciaram e nenhum arredondamento de nível 1 distorce a proporção.
#
# Não existe uma tabela de referência de monstro ao lado de
# `SKILL_REFERENCE_STATS`: os atributos dele são DERIVADOS de `spawn_by_role`
# neste nível. Congelar uma cópia aqui criaria uma segunda verdade sobre o
# orçamento de arquétipo, e ela envelheceria em silêncio.
MONSTER_REFERENCE_LEVEL = 12

CLASS_WEIGHTS = {
    "Warrior": {"st": 1.6, "mg": 0.4, "ag": 0.0},
    "Mage": {"st": 0.3, "mg": 1.9, "ag": 0.0},
    "Rogue": {"st": 0.8, "mg": 0.4, "ag": 1.7},
}

# --- Configurações de Mapa ---
DEFAULT_WALL_PERCENTAGE = 0.2
MAP_BORDER_OFFSET = 1  # Offset para evitar bordas

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


# Fórmulas
DAMAGE_FORMULA_DIVISOR = 3  # (ST + MG) // 3
# Custo de XP do nível 1 e razão de crescimento do custo. A razão é maior que
# GROWTH_RATE de propósito: o número de combates por nível sobe ao longo da run
# (cerca de 3 no nível 1, cerca de 14 no nível 19), então o herói fica
# progressivamente atrás do andar. É essa defasagem que cria dificuldade
# crescente, em vez de inflar os números do monstro.
XP_BASE_COST = 140
# Amortecedor do começo da curva de XP, não constante de balanceamento.
#
# O custo de nível tem a mesma forma da produção de XP de um andar —
# `nível × 1,12^nível` contra `andar × 1,12^andar` — e é essa igualdade de forma
# que impede o nível do herói de divergir do andar em profundidade.
#
# O amortecedor só faz o custo do nível 1 continuar valendo XP_BASE_COST. Ele
# desloca onde a defasagem se estabiliza; que ela se estabilize vem da forma.
# Ver `tests/test_progression_contract.py`.
XP_LEVEL_SOFTENER = 6

# O mini-chefe aparece a cada N andares. Lido por `engine/loop.py`,
# `sim/harness.py` e `sim/xp_model.py`, para os três concordarem.
BOSS_FLOOR_INTERVAL = 5

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

# --- Eventos Aleatórios de Masmorra ---
# Probabilidade de um evento especial ao entrar num andar (antes da extração)
RANDOM_EVENT_CHANCE = 0.25  # 25% — equilíbrio entre surpresa e previsibilidade
RANDOM_EVENT_MERCHANT_MIN_ITEMS = 1
RANDOM_EVENT_MERCHANT_MAX_ITEMS = 3
RANDOM_EVENT_ALTAR_HP_COST_PERCENT = 30  # % da vida máxima sacrificada
RANDOM_EVENT_ALTAR_BUFF_VALUE = 15
RANDOM_EVENT_ALTAR_BUFF_DURATION = 5  # turnos de combate
RANDOM_EVENT_FOUNTAIN_HEAL_PERCENT = 50  # % da vida máxima curada

# --- Novos sistemas de combate ---
STUN_DURATION = 1  # turnos perdidos quando atordoado
# Esmagar teve as suas duas constantes removidas: o motor a atordoava por nome,
# em cima do `stun_chance` que a própria skill já declara no JSON. Valor de skill
# é dado, e mora no JSON — o motor lê, não redeclara.
DAMAGE_REDUCTION_DURATION = 3  # turnos que dura a redução de dano
DAMAGE_REDUCTION_DEFAULT_PERCENT = 30  # % de dano reduzido

# --- Correção de balanceamento (auditoria PROMPT 3) ---
# Mini-boss coin agora tem base/escala dedicadas (antes reusava monster*3)
MINI_BOSS_BASE_COIN_REWARD = 80
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
# Cada classe tem a sua forma de não morrer: o Guerreiro absorve com HP e
# defesa, o Ladino evita com agilidade, e o Mago converte mana. É o que faz a
# reserva de mana dele pesar desde o primeiro andar, e não só em luta longa.
#
# Fração máxima de um golpe que a Égide absorve. Em 15% as três classes empatam
# dentro da margem de erro da simulação; é esse o alvo, não um número redondo.
# Não confundir com a skill `Barreira Arcana`, que é um buff de defesa lançado
# pelo jogador.
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

# --- Descanso entre andares ---
# Concluir um andar devolve parte dos recursos. Não tudo: a cura completa a cada
# andar era uma das cinco fontes de cura gratuita que tornavam cada combate
# independente do anterior. Não zero: uma run de 20 andares em uma única barra
# de vida não é difícil, é impossível. O andar é a unidade de risco, e o que
# sobra de vida no fim dele é o que dá peso à decisão de extrair.
# Mana devolvida por turno de combate, em % do MP máximo. Sem ela a mana é um
# estoque que se gasta uma vez e o combate vira ataque básico; com ela vira
# ritmo — dá para bater agora e pagar a skill grande dali a três turnos. Vale
# para o monstro também, e é o que sustenta um arquétipo em combate longo.
# A 3% a distância entre classes estoura o limite, por isso 2%.
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

# --- Arena: poder geral do personagem ---
# `overall_power` responde uma pergunta só: contra um monstro de que nível este
# personagem fica em equilíbrio? A resposta sai na unidade que o jogo já tem —
# NÍVEL DE MONSTRO —, e por isso nenhum câmbio entre HP, dano, mana e status
# precisa ser inventado: quem converte é o duelo.
#
# O boneco é FIXO e neutro, pelo mesmo motivo que `MONSTER_REFERENCE_LEVEL`
# existe para as cartas: trocar a régua por caso faria dois personagens
# incomparáveis. Medido, trocar o arquétipo move `relative_power` em até ~4%.
ARENA_REFERENCE_ROLE = "bruiser"

# Equilíbrio é meio a meio. Não é peso: é a definição de empate.
ARENA_WIN_TARGET = 0.5

# Duelos por sondagem. Medido em 5 blocos de seed independentes: com 100, o piso
# de ruído fica em 0,0–1,6% do valor acima do nível 8 (4,7% no nível 5, onde o
# personagem tem pouco com que decidir a luta). Com 60 o piso chegava a 5,4% —
# do tamanho da banda de equivalência, o que tornaria o veredito ruído.
ARENA_DUELS_PER_PROBE = 100

# Precisão da bisseção, RELATIVA ao valor. Uma tolerância absoluta erraria por
# escala: 0,15 nível vale 1% em L=15 e 2,5% em L=6, e a segunda sozinha comeria
# metade da banda de equivalência.
ARENA_LEVEL_TOLERANCE = 0.006

# O piso da busca: o menor monstro que o jogo constrói. Abaixo dele não há curva
# de orçamento para ler, então quem perde para ele lê 1,0 — resposta honesta, e
# não teto, porque o jogo não tem monstro mais fraco para servir de régua.
ARENA_LEVEL_FLOOR = 1.0

# O PALPITE inicial do topo da busca, folgado de propósito: um personagem de
# nível 20 com equipamento de topo já empata perto de 31.
#
# NÃO é teto do resultado. A dungeon é infinita, então um teto fixo faria dois
# campeões diferentes saturarem no mesmo número, e `relative_power` entre eles
# daria 1,000 sem que nenhum dos dois tivesse sido medido. Quando o personagem
# ainda vence aqui, o bracket DOBRA e a busca continua — mecanismo de busca, não
# balanceamento: fórmula, piloto, amostra e banda seguem intactos.
ARENA_LEVEL_BRACKET = 60.0
ARENA_BRACKET_GROWTH = 2.0

# Trava técnica contra laço infinito, não resposta. Atingi-la levanta
# `PoderForaDeEscalaError`: um limite que vira resultado calado é exatamente o
# defeito que a expansão existe para corrigir. O valor é absurdo de propósito —
# um monstro de nível 10 mil tem HP na casa dos 10^54 —, então chegar lá
# significa bug, não campeão.
ARENA_LEVEL_HARD_LIMIT = 10_000.0

# Semente da medição. Fixa para que dois cálculos do mesmo personagem devolvam o
# mesmo número — a decisão de extrair não pode oscilar por sorteio. O gerador
# global é restaurado ao fim (`sim.rng_guard`), então a run não perde sorteio.
ARENA_MEASURE_SEED = 20260919

# Banda de equivalência: ±5%, decisão de design aprovada. Abaixo dela o
# personagem está ABAIXO do alvo da Arena; acima, SUPEROU.
#
# LIMITAÇÃO CONHECIDA DA V1, registrada e aceita: o resíduo de pilotagem medido
# na região de kit compatível tem mediana de 3,5% e MÁXIMO OBSERVADO DE 6,3% —
# ou seja, o máximo NÃO cabe dentro desta banda. A banda permanece em 5% por
# decisão de design. Fechar isso exige um segundo piloto competente de medição,
# que o repositório ainda não tem.
ARENA_EQUIVALENCE_BAND = 0.05
