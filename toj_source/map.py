#!/usr/bin/env python3.10

import random as rd

class MapOFGame:
    # This class is used to create a map of the game
    def __init__(self, height, width):
        # This is the constructor of the class
        # The map has a height and a width
        self.height = height
        self.width = width


def draw_square(height, width, percent_of_walls):
    # This function is used to draw a square
    free_areas = [ 1 for x in range(100) if x != 0 and x != 4 * 3]
    # This list contains the free areas of the map 
    # (the areas that are not walls)
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

