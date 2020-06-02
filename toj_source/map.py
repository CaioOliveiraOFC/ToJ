#!/usr/bin/env python3

import random as rd

class MapOFGame:
    def __init__(self, height, width):
        self.height = height
        self.width = width


def draw_square(height, width, percent_of_walls):
    free_areas = [ 1 for x in range(100) if x != 0 and x != 4 * 3]
    map_in_list = free_areas
    for y in range(height):
        for x in range(width):
            if map_in_list[y] == 1:
                print('.', end=' ')
            else:
                print('#', end=' ')
        print() 


if __name__=='__main__':
    grid = MapOFGame(30, 30)
    draw_square(grid.height, grid.width, 0.03)

