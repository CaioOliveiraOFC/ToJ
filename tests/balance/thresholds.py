"""Limiares da suíte de balanceamento.

Todo número aqui saiu de medição, não de escolha. A referência é
`reports/baseline_20260904.json` (o estado anterior) e as execuções de
`python -m src.sim.runner run --iterations 500` sobre o estado atual.

A run simulada roda os mesmos sistemas do jogo: escolha de passiva por nível,
escolha de skill nos níveis ímpares a partir do 5, drop de item, loja entre
andares, evento aleatório e multiplicador de Essência. Uma calibração anterior
mediu um herói sem passiva nenhuma e com o equipamento do andar 1 — os números
dela não valem para o jogo que existe.

Valores medidos no estado atual (250 runs por classe, política competente,
equipamento típico) — `reports/validation_20260904.json`:

    classe    andar médio  mediano  chega ao 20  passivas ao fim  bot que só ataca
    Guerreiro      8.1        4        26,0%          9.6          andar médio 1.0
    Mago           5.8        2        17,6%          6.9          andar médio 0.3
    Ladino         8.1        4        23,6%          9.8          andar médio 1.0

A distribuição é bimodal: a maioria das runs termina nos primeiros andares, e as
que passam do andar 5 com passivas empilhadas tendem a chegar ao 20. Por isso a
média fica bem abaixo da taxa de conclusão, e por isso os limiares de paridade
usam o andar médio, que é estável, e não a taxa de conclusão, que é cauda.

Duração de combate no nível 12, em turnos, da classe mais lenta:
    trash 3.4 · bruiser 11.6 · tank 19.1 · elite 17.3 · chefe 23.5

As bandas abaixo têm folga sobre esses valores para não quebrarem com ruído
estatístico. Elas existem para pegar regressão estrutural — uma classe que
desaba, um encontro que vira trivial, o atrito que some — não para congelar o
balanceamento no ponto exato de hoje.
"""

# --- Paridade entre classes ---
# Nenhuma classe pode virar a escolha óbvia nem a escolha inútil.
MIN_CLASS_MEAN_FLOOR = 3.0
MAX_CLASS_MEAN_FLOOR = 14.0
# Distância máxima, em andares, entre a melhor e a pior classe.
MAX_CLASS_MEAN_FLOOR_SPREAD = 4.0

# --- Skill gap ---
# A métrica central: quanto jogar bem vale. Medido em andares de profundidade,
# porque a taxa de chegar ao andar 20 é um evento de cauda e varia demais.
MIN_SKILL_GAP_FLOORS = 3.0

# --- Dificuldade global ---
# O bot que só ataca não deve terminar a masmorra. Paciência não substitui
# competência: era exatamente esse o problema do balanceamento anterior.
MAX_GREEDY_REACH_20 = 0.02
# O jogador competente deve conseguir, mas não com folga.
MIN_SMART_REACH_20 = 0.05
MAX_SMART_REACH_20 = 0.45

# --- Duração de combate por arquétipo ---
# Um combate de 1 a 2 turnos não tem espaço para decisão nenhuma; era a duração
# de todo combate do jogo antes do rebalanceamento.
TTK_BANDS = {
    "trash_solo": (2.5, 8.0),
    "bruiser_solo": (4.0, 16.0),
    "tank_solo": (8.0, 28.0),
    "elite_solo": (7.0, 26.0),
    "boss_solo": (10.0, 34.0),
}
MIN_TTK_ANY_ENCOUNTER = 2.0

# --- Encontros ---
# Um encontro isolado, começado com a vida cheia, NÃO deve matar: a dificuldade
# do jogo mora na sequência, não em cada luta. O que mede se um encontro importa
# é quanto ele custa, não se ele é vencido. Um marco de andar (elite, chefe,
# composição) precisa levar pelo menos esta fatia da vida de quem o vence.
MIN_HP_COST_MILESTONE = 0.15
# Nenhum encontro pode ser intransponível para todas as classes.
IMPOSSIBLE_WIN_RATE = 0.10

# --- Acerto ---
# Ninguém fica imune nem infalível, por maior que seja a diferença de agilidade.
HIT_FLOOR = 20
HIT_CEIL = 95

# --- Atrito ---
# HP médio ao vencer um combate de rotina. Acima disto, o combate não custou
# nada e o andar volta a ser uma sequência de eventos independentes — que era
# exatamente o efeito do `rest()` automático depois de cada vitória.
MAX_HP_LEFT_ON_WIN = 0.95

# --- Escalonamento ---
# Razão poder-do-herói / HP-do-monstro ao longo dos 20 níveis. Constante por
# construção; a tolerância cobre só o arredondamento.
MAX_SCALING_DRIFT = 0.25

# A run precisa entregar ao herói o que o jogo entrega. Zero passivas ao fim de
# vinte andares significa que a simulação parou de rodar a progressão — foi
# exatamente o que aconteceu quando `while level_up(show=False)` nunca iterava.
MIN_PASSIVES_AT_END = 3.0

# Iterações por cenário nos testes rápidos. Suficiente para pegar regressão
# estrutural sem transformar a suíte em algo que ninguém roda.
FAST_ITERATIONS = 120

# A run completa precisa de muito mais amostra que um combate isolado. A
# profundidade alcançada é bimodal — a maioria das runs morre cedo e as
# sobreviventes chegam ao fim —, então a média carrega erro amostral grande.
#
# Medido em cinco seeds, o andar médio do Warrior varia assim:
#
#     60 runs  ->  10.4  6.9  8.9  10.5  7.7   (desvio 1.44)
#    250 runs  ->   9.3  8.9  8.4   9.1  8.4   (desvio 0.35)
#
# Com 60 runs a distância entre a melhor e a pior classe deu de 2.4 a 4.9
# andares conforme a seed, contra um limite de 4.0: o teste aprovava ou
# reprovava o mesmo jogo, medindo o próprio ruído. Com 250 a mesma distância
# fica entre 3.0 e 3.7, e o veredito passa a ser sobre o jogo.
FAST_RUN_ITERATIONS = 250
