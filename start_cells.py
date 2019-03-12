import pygame

from cells.main_loop import main_loop
from cells.bloom import BloomGrid
from cells.war import WarGrid
from cells import constants as c


pygame.init()
clock = pygame.time.Clock()

grid_choices = [BloomGrid, WarGrid]
DEFAULT_GRID_CHOICE = 0

for index, grid in enumerate(grid_choices):
    string = '({}: {}) -- {}'.format(index, grid.name, grid.description)
    if index == DEFAULT_GRID_CHOICE:
        print('DEFAULT: {}'.format(string))
    else:
        print(string)

GridClass = None

while not GridClass:
    grid_choice = input('Which grid?: ')
    if grid_choice == '':
        grid_choice = DEFAULT_GRID_CHOICE
    try:
        GridClass = grid_choices[int(grid_choice)]
    except:
        print('Not a valid Option')


options = {}
if input('Custom settings? y/N: ') in c.AFFIRMATIVE_ANSWERS:
    print('Leave blank for default')
    options = grid.get_options()

main_loop(pygame, clock, GridClass, options)
