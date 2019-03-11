import pygame

from cells.main_loop import main_loop
from cells import constants as c


pygame.init()
clock = pygame.time.Clock()

choices = {}

if input('Custom settings? y/n: ') in ['y', 'Y', 'yes', 'Yes', 'YES']:
    print('Leave blank for default')
    choices['cells_per_row'] = input('How many cells wide? (Default: {}) -- '.format(c.DEFAULT_CELLS_PER_ROW))
    choices['rows_per_screen'] = input('How many cells high? (Default: {}) -- '.format(c.DEFAULT_ROWS_PER_SCREEN))
    choices['cell_width'] = input('How many pixels wide is each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_WIDTH))
    choices['cell_height'] = input('How many pixels high is each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_HEIGHT))
    choices['cell_margin'] = input('How many between each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_MARGIN))
    choices['tick_speed'] = input('Tick speed? (Default: {}) -- '.format(c.DEFAULT_TICK_SPEED))
    for key, value in choices.items():
        if value:
            choices[key] = int(value)

    choices['wrap'] = not bool(input('Wrap at edges? (Default: True) "n" for False -- '))

main_loop(pygame, clock, choices)
