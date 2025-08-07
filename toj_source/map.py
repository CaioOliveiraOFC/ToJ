#!/usr/bin/env python3.10

import random
import os
import sys

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios

class MapGameWithPhases:
    def __init__(self, height=20, width=40, wall_density=0.1):
        self.height = height
        self.width = width
        self.wall_density = wall_density
        self.phase = 1
        self.grid = []
        self.player_pos = None
        self.goal_pos = None
        self._generate_phase()

    def _generate_phase(self):
        """
        Gera uma nova fase com mapa, jogador e objetivo.
        """
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    row.append('#')  # Borda sempre fechada
                else:
                    row.append('#' if random.random() < self.wall_density else '.')
            self.grid.append(row)

        self.player_pos = self._place_random('.', avoid_border=True)
        self.goal_pos = self._place_random('.', only_border=True)
        self._set_tile(self.goal_pos, 'X')

    def _place_random(self, target_char, only_border=False, avoid_border=False):
        attempts = 0
        while attempts < 10000:
            y = random.randint(0, self.height - 1)
            x = random.randint(0, self.width - 1)

            if only_border and not (x == 1 or y == 1 or x == self.width - 2 or y == self.height - 2):
                attempts += 1
                continue
            if avoid_border and (x <= 1 or y <= 1 or x >= self.width - 2 or y >= self.height - 2):
                attempts += 1
                continue

            if self.grid[y][x] == target_char:
                return (y, x)
            attempts += 1
        return (1, 1)  # fallback

    def _get_tile(self, pos):
        y, x = pos
        return self.grid[y][x]

    def _set_tile(self, pos, value):
        y, x = pos
        self.grid[y][x] = value

    def move_player(self, direction):
        dyx = {
            'W': (-1, 0),
            'S': (1, 0),
            'A': (0, -1),
            'D': (0, 1)
        }
        direction = direction.upper()
        if direction not in dyx:
            return
        dy, dx = dyx[direction]
        new_y = self.player_pos[0] + dy
        new_x = self.player_pos[1] + dx

        if self.grid[new_y][new_x] in ['.', 'X']:
            if (new_y, new_x) == self.goal_pos:
                self.phase += 1
                self._generate_phase()
                return
            self.player_pos = (new_y, new_x)

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                if (y, x) == self.player_pos:
                    row += '@ '
                else:
                    row += self.grid[y][x] + ' '
            print(row)
        print(f"\nFase: {self.phase} | Use W A S D para mover. Q para sair.")


def get_key():
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8').upper()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1).upper()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def main():
    game = MapGameWithPhases()
    while True:
        game.draw()
        key = get_key()
        if key == 'Q':
            print("Jogo encerrado.")
            break
        game.move_player(key)


if __name__ == '__main__':
    main()
