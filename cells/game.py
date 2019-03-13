import os
import pygame

from .main_loop import main_loop
from . import constants as c


class Game():
    grid_class = None
    customize_answers = {}

    def __init__(self, grid_choices):
        self.grid_choices = grid_choices
        self.pygame = pygame
        self.pygame.init()
        self.clock = self.pygame.time.Clock()

        self.print_heading()
        self.choose_grid()
        self.customize_grid()
        self.start_main_loop()

    def clear_shell(self):
        os.system('cls')
        os.system('clear')

    def print_heading(self):
        self.clear_shell()
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
        print('For any question, leave it blank to use the default')
        print('\n')

    def choose_grid(self):
        self.print_grid_options()
        while not self.grid_class:
            grid_choice = input('---> ')
            if grid_choice == '':
                grid_choice = c.DEFAULT_GRID_CHOICE
            try:
                self.grid_class = self.grid_choices[int(grid_choice)]
            except:
                print('Not a valid Option')
        print('\n')

    def print_grid_options(self):
        print('First, choose your grid. A grid determines all of the rules the cells must abide by')
        print('\n')
        for index, grid in enumerate(self.grid_choices):
            string = '({}: {}) -- {}'.format(index, grid.name, grid.description)
            if index == c.DEFAULT_GRID_CHOICE:
                print('DEFAULT: {}'.format(string))
            else:
                print(string)

    def customize_grid(self):
        print('Do you want to customize the grid?')
        if input('y/N ---> ') in c.AFFIRMATIVE_ANSWERS:
            options = self.grid_class.get_options()
            self.int_options = self.grid_class.get_int_options()
            self.truthy_options = self.grid_class.get_truthy_options()
            for option in options:
                self.get_answer_for_option(option)

    def get_answer_for_option(self, option):
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
            if key in self.truthy_options:
                if option.get('default'):
                    answer = input('Y/n ---> ')
                else:
                    answer = input('y/N ---> ')
            else:
                answer = input('---> ')
            if answer == '':
                break
            try:
                if key in self.int_options:
                    answer = int(answer)
                if key in self.truthy_options:
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
            self.customize_answers[key] = answer

    def start_main_loop(self):
        main_loop(self.pygame, self.clock, self.grid_class, self.customize_answers)
