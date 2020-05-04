#!/usr/bin/env python3

import random as rd

class MapOFGame:
    def __init__(self, height, width):
        self.height = height
        self.width = width


def draw_square(height, width, percent_of_walls):

    non_free = [ 0 for x in range(10)]
    free_areas = [ 1 for x in range(80)]
    map_in_list = non_free + free_areas
    rd.shuffle(map_in_list)
    print(non_free)
    print(free_areas)
    print(map_in_list)
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

