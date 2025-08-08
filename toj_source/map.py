#!/usr/bin/env python3.10

import random

# Dicionário com códigos de cores ANSI para o terminal
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "reset": "\033[0m"
}

class MapOfGame:
    """
    Esta classe gere a criação, exibição e interação com o mapa do jogo,
    incluindo jogador, inimigos e a saída da masmorra.
    """
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid = []
        self.player_pos = {'y': 0, 'x': 0}
        self.exit_pos = {'y': 0, 'x': 0}
        self.enemies_pos = {}

    def _get_random_empty_spot(self):
        """Encontra e retorna uma posição vazia aleatória ('.') no mapa."""
        while True:
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)
            if self.grid[y][x] == '.':
                return y, x

    def generate_map(self, percent_of_walls=0.2):
        """Gera uma nova grade de mapa com paredes e espaços vazios."""
        self.grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    self.grid[y][x] = '#'  # Paredes nas bordas
                elif random.random() < percent_of_walls:
                    self.grid[y][x] = '#'  # Paredes internas

    def place_player(self):
        """Coloca o jogador em um local aleatório no mapa."""
        y, x = self._get_random_empty_spot()
        self.player_pos['y'], self.player_pos['x'] = y, x

    def place_exit(self):
        """Coloca a saída 'X' no canto mais distante do jogador."""
        player_y, player_x = self.player_pos['y'], self.player_pos['x']
        
        # Determina o canto oposto
        exit_y = self.height - 2 if player_y < self.height / 2 else 1
        exit_x = self.width - 2 if player_x < self.width / 2 else 1
        
        self.grid[exit_y][exit_x] = 'X'
        self.exit_pos = {'y': exit_y, 'x': exit_x}

    def place_enemy(self, enemy_obj):
        """Coloca um inimigo em um local aleatório."""
        y, x = self._get_random_empty_spot()
        self.enemies_pos[(y, x)] = enemy_obj

    def draw_map(self):
        """Desenha o mapa no console com cores."""
        for y, row in enumerate(self.grid):
            display_row = []
            for x, tile in enumerate(row):
                char = tile
                if y == self.player_pos['y'] and x == self.player_pos['x']:
                    char = f"{COLORS['green']}@{COLORS['reset']}"
                elif (y, x) in self.enemies_pos:
                    char = f"{COLORS['red']}&{COLORS['reset']}"
                elif tile == 'X':
                    char = f"{COLORS['yellow']}X{COLORS['reset']}"
                display_row.append(char)
            print(' '.join(display_row))

    def move_player(self, direction):
        """
        Move o jogador, verifica colisões e retorna o resultado da ação.
        Retorna: 'level_complete', um objeto Monstro, ou None.
        """
        py, px = self.player_pos['y'], self.player_pos['x']
        ny, nx = py, px

        if direction == 'w': ny -= 1
        elif direction == 's': ny += 1
        elif direction == 'a': nx -= 1
        elif direction == 'd': nx += 1

        # Verifica colisão com parede
        if self.grid[ny][nx] == '#':
            return None

        # Verifica se chegou na saída
        if ny == self.exit_pos['y'] and nx == self.exit_pos['x']:
            return 'level_complete'

        # Verifica colisão com inimigo
        if (ny, nx) in self.enemies_pos:
            enemy_collided = self.enemies_pos.pop((ny, nx))
            self.player_pos = {'y': ny, 'x': nx}
            return enemy_collided

        # Move o jogador
        self.player_pos = {'y': ny, 'x': nx}
        return None
