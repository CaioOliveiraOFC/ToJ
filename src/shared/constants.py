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
SLEEP_AFTER_SAVE = 1.5
SLEEP_SHORT_PAUSE = 1.0
SLEEP_MENU_REFRESH = 1.5
SLEEP_GAME_OVER = 2.0
