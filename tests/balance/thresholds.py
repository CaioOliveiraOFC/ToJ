"""Limiares da suíte de balanceamento.

Todo número aqui saiu de medição, não de escolha. A referência é
`reports/baseline_20260904.json` (o estado anterior) e as execuções de
`python -m src.sim.runner run --iterations 500` sobre o estado atual.

Valores medidos no estado atual (400 runs por classe, política competente,
equipamento típico) — `reports/validation_20260904.json`:

    classe      andar médio   chega ao 20   andar médio do bot que só ataca
    Guerreiro       13.9          12,2%                  2.3
    Mago            11.6          16,0%                  2.0
    Ladino          13.2           1,5%                  3.4

Duração de combate no nível 12, em turnos, da classe mais lenta:
    trash 5.3 · bruiser 11.1 · tank 22.9 · elite 18.3 · chefe 28.8

Custo de um encontro, em HP perdido por quem vence (nível 12):
    trash 3% · bruiser 13-18% · elite 25-35% · chefe 39% · skirmishers 42%

As bandas abaixo têm folga sobre esses valores para não quebrarem com ruído
estatístico. Elas existem para pegar regressão estrutural — uma classe que
desaba, um encontro que vira trivial, o atrito que some — não para congelar o
balanceamento no ponto exato de hoje.
"""

# --- Paridade entre classes ---
# Nenhuma classe pode virar a escolha óbvia nem a escolha inútil.
MIN_CLASS_MEAN_FLOOR = 7.0
MAX_CLASS_MEAN_FLOOR = 18.0
# Distância máxima, em andares, entre a melhor e a pior classe.
MAX_CLASS_MEAN_FLOOR_SPREAD = 4.0

# --- Skill gap ---
# A métrica central: quanto jogar bem vale. Medido em andares de profundidade,
# porque a taxa de chegar ao andar 20 é um evento de cauda e varia demais.
MIN_SKILL_GAP_FLOORS = 4.0

# --- Dificuldade global ---
# O bot que só ataca não deve terminar a masmorra. Paciência não substitui
# competência: era exatamente esse o problema do balanceamento anterior.
MAX_GREEDY_REACH_20 = 0.02
# O jogador competente deve conseguir, mas não com folga.
MIN_SMART_REACH_20 = 0.02
MAX_SMART_REACH_20 = 0.45

# --- Duração de combate por arquétipo ---
# Um combate de 1 a 2 turnos não tem espaço para decisão nenhuma; era a duração
# de todo combate do jogo antes do rebalanceamento.
TTK_BANDS = {
    "trash_solo": (2.5, 8.0),
    "bruiser_solo": (4.0, 14.0),
    "tank_solo": (8.0, 28.0),
    "elite_solo": (7.0, 24.0),
    "boss_solo": (10.0, 36.0),
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

# Iterações por cenário nos testes rápidos. Suficiente para pegar regressão
# estrutural sem transformar a suíte em algo que ninguém roda.
FAST_ITERATIONS = 120
FAST_RUN_ITERATIONS = 60
