#!/usr/bin/env python3.10
"""Lógica de mapa, geração procedural e movimentação."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.content.factories.monsters import create_monster

if TYPE_CHECKING:
    pass

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
        """Gera o mapa usando Random Walk garantindo conectividade."""
        self.grid = [['#' for _ in range(self.width)] for _ in range(self.height)]

        target_empty = int((self.width - 2) * (self.height - 2) * (1.0 - percent_of_walls))

        y = self.height // 2
        x = self.width // 2
        self.grid[y][x] = '.'
        empty_count = 1

        while empty_count < target_empty:
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            ny = y + direction[0]
            nx = x + direction[1]

            if 1 <= ny < self.height - 1 and 1 <= nx < self.width - 1:
                y, x = ny, nx
                if self.grid[y][x] == '#':
                    self.grid[y][x] = '.'
                    empty_count += 1

    def place_player(self):
        """Coloca o jogador em um local aleatório no mapa."""
        y, x = self._get_random_empty_spot()
        self.player_pos['y'], self.player_pos['x'] = y, x

    def place_exit(self):
        """Coloca a saída 'X' no piso vazio mais distante do jogador."""
        player_y, player_x = self.player_pos['y'], self.player_pos['x']

        max_dist = -1
        best_pos = None

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.':
                    dist = abs(y - player_y) + abs(x - player_x)
                    if dist > max_dist:
                        max_dist = dist
                        best_pos = (y, x)

        if best_pos:
            exit_y, exit_x = best_pos
            self.grid[exit_y][exit_x] = 'X'
            self.exit_pos = {'y': exit_y, 'x': exit_x}

    def place_enemy(self, enemy_obj):
        """Coloca um inimigo em um local aleatório."""
        y, x = self._get_random_empty_spot()
        self.enemies_pos[(y, x)] = enemy_obj

    def draw_map(self) -> list[str]:
        """Gera representação do mapa como lista de strings para renderização pela UI.

        Retorna lista de strings onde cada string representa uma linha do mapa.
        A renderização visual é responsabilidade da camada UI (renderer/screens).
        """
        lines: list[str] = []
        for y, row in enumerate(self.grid):
            display_row: list[str] = []
            for x, tile in enumerate(row):
                char = tile
                if y == self.player_pos['y'] and x == self.player_pos['x']:
                    char = f"{COLORS['green']}@{COLORS['reset']}"
                elif (y, x) in self.enemies_pos:
                    enemy = self.enemies_pos[(y, x)]
                    if getattr(enemy, 'is_boss', False):
                        char = f"\033[95mB{COLORS['reset']}"
                    else:
                        char = f"{COLORS['red']}&{COLORS['reset']}"
                elif tile == 'X':
                    char = f"{COLORS['yellow']}X{COLORS['reset']}"
                elif tile == 'D':  # Adicionado para corpos de inimigos mortos
                    char = f"{COLORS['red']}D{COLORS['reset']}"
                display_row.append(char)
            lines.append(' '.join(display_row))
        return lines

    def move_player(self, direction):
        """
        Move o jogador, verifica colisões e retorna o resultado da ação.
        Retorna: 'level_complete', um objeto Monstro, ou None.
        """
        py, px = self.player_pos['y'], self.player_pos['x']
        ny, nx = py, px

        if direction == 'w':
            ny -= 1
        elif direction == 's':
            ny += 1
        elif direction == 'a':
            nx -= 1
        elif direction == 'd':
            nx += 1

        # Verifica colisão com parede ou limite do mapa
        if ny < 0 or ny >= self.height or nx < 0 or nx >= self.width:
            return None
        if self.grid[ny][nx] == '#':
            return None
        # Permite que o jogador passe por cima de corpos mortos
        if self.grid[ny][nx] == 'D':
            self.player_pos = {'y': ny, 'x': nx}
            return None # Não há colisão significativa, apenas move o jogador

        # Verifica se chegou na saída
        if ny == self.exit_pos['y'] and nx == self.exit_pos['x']:
            return 'level_complete'

        # Verifica colisão com inimigo
        if (ny, nx) in self.enemies_pos:
            enemy_collided = self.enemies_pos.pop((ny, nx))
            self.grid[ny][nx] = 'D'  # Marca a posição onde o inimigo morreu com um 'D'
            self.player_pos = {'y': ny, 'x': nx}
            return enemy_collided

        # Move o jogador se o caminho estiver livre ('.')
        if self.grid[ny][nx] == '.':
            self.player_pos = {'y': ny, 'x': nx}
        return None

    def get_map_state(self):
        """Retorna um dicionário com o estado atual do mapa para salvamento."""
        # Serializar enemies_pos para salvar. (y, x) -> {nick_name, level}
        enemies_serializable = {
            f"{y},{x}": {"nick_name": enemy.nick_name, "level": enemy.level}
            for (y, x), enemy in self.enemies_pos.items()
        }

        return {
            "height": self.height,
            "width": self.width,
            "grid": self.grid,
            "player_pos": self.player_pos,
            "exit_pos": self.exit_pos,
            "enemies_pos": enemies_serializable
        }

    def load_map_state(self, map_state: dict) -> None:
        """Carrega o estado do mapa a partir de um dicionário."""
        self.height = map_state["height"]
        self.width = map_state["width"]
        self.grid = map_state["grid"]
        self.player_pos = map_state["player_pos"]
        self.exit_pos = map_state["exit_pos"]

        self.enemies_pos = {}
        for pos_str, enemy_data in map_state["enemies_pos"].items():
            y, x = map(int, pos_str.split(','))
            monster = create_monster(enemy_data["nick_name"], enemy_data["level"])
            self.enemies_pos[(y, x)] = monster
