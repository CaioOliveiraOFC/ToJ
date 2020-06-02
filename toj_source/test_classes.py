#!/usr/bin/env python3

from toj_source.classes import *

print('Stats of player 1')
p1 = Mage('Player1')
p1.show_attributes()

print('Monster creation')
name_monsters = {1:'Bear', 2: 'Weak wolf'}
m1 = Monster(name_monsters[1])
p1.show_attributes()
m2 = Monster(name_monsters[2])
p1.show_attributes()
print(f'{m1.name}')
print(f'{m2.name}')
