import os

import pygame

from cells.main_loop import main_loop
from cells.bloom import BloomGrid
from cells.war import WarGrid
from cells import constants as c


# init
pygame.init()
clock = pygame.time.Clock()


os.system('cls')
os.system('clear')
print('----------------------------')
print('Game')
print('        of')
print('                 Strife')
print('\n')
print('(Better name later)')
print('\n')
print('Cellular Automata Simulation')
print('----------------------------')
print('\n')
print('\n')

# choose grid
# print gird options
grid_choices = [BloomGrid, WarGrid]
DEFAULT_GRID_CHOICE = 0
print('For any question, leave it blank to use the default')
print('\n')
print('First, choose your grid. A grid determines all of the rules the cells must abide by')
print('\n')
for index, grid in enumerate(grid_choices):
    string = '({}: {}) -- {}'.format(index, grid.name, grid.description)
    if index == DEFAULT_GRID_CHOICE:
        print('DEFAULT: {}'.format(string))
    else:
        print(string)

GridClass = None
while not GridClass:
    grid_choice = input('---> ')
    if grid_choice == '':
        grid_choice = DEFAULT_GRID_CHOICE
    try:
        GridClass = grid_choices[int(grid_choice)]
    except:
        print('Not a valid Option')


# take custom options
answers = {}
print('\n')
print('Do you want to customize the grid?')
if input('y/N ---> ') in c.AFFIRMATIVE_ANSWERS:
    options = grid.get_options()
    int_options = grid.get_int_options()
    truthy_options = grid.get_truthy_options()
    for option in options:
        while True:
            key = option.get('key')
            print('\n')
            question = option.get('question')
            if isinstance(question, list):
                for part in question:
                    print(part)
            else:
                print(question)
            print('Blank for default ({})'.format(option.get('default')))
            if key in truthy_options:
                if option.get('default'):
                    answer = input('Y/n ---> ')
                else:
                    answer = input('y/N ---> ')
            else:
                answer = input('---> ')
            if answer == '':
                break
            try:
                if key in int_options:
                    answer = int(answer)
                if key in truthy_options:
                    answer = True if answer in c.AFFIRMATIVE_ANSWERS else False
            except:
                print('Invalid answer')

            valid_answers = option.get('valid_answers')
            if valid_answers and answer not in valid_answers:
                print('Answer invalid. Can only be one of: ')
                for valid in valid_answers:
                    print(valid)
                    continue
            break

        if answer:
            answers[key] = answer


main_loop(pygame, clock, GridClass, answers)
