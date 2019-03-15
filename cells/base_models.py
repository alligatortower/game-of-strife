import pygame
from pygame import Color

from . import constants as c


class MasterGrid():
    cells_per_row = c.DEFAULT_CELLS_PER_ROW
    rows_per_screen = c.DEFAULT_ROWS_PER_SCREEN
    cell_width = c.DEFAULT_CELL_WIDTH
    cell_height = c.DEFAULT_CELL_HEIGHT
    cell_margin = c.DEFAULT_CELL_MARGIN
    tick_speed = c.DEFAULT_TICK_SPEED
    wrap = c.DEFAULT_WRAP_AT_EDGES
    grid = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value not in [None, '']:
                setattr(self, key, value)

        StartingCellClass = self.get_starting_cell_class()

        for row in range(self.rows_per_screen):
            self.grid.append([])
            for column in range(self.cells_per_row):
                self.grid[row].append(StartingCellClass(row, column, self, initial_cell=True))

    def get_starting_cell_class(self):
        raise NotImplementedError

    def create_screen(self):
        width = (self.cell_width * self.cells_per_row) + (self.cell_margin * self.cells_per_row) + self.cell_margin
        height = (self.cell_height * self.rows_per_screen) + (self.cell_margin * self.rows_per_screen) + self.cell_margin
        self.screen = pygame.display.set_mode((width, height))
        return self.screen

    def get_next_cell_types(self):
        self.call_method_on_each_cell('apply_rules')

    def update_cell_types_and_draw(self):
        self.call_method_on_each_cell(['update_type', 'draw'])

    def call_method_on_each_cell(self, method_name):
        for row in range(self.rows_per_screen):
            for column in range(self.cells_per_row):
                if isinstance(method_name, list):
                    for name in method_name:
                        cell = self.grid[row][column]
                        getattr(cell, name)()
                else:
                    cell = self.grid[row][column]
                    getattr(cell, method_name)()

    def pre_flip(self, iteration):
        self.get_next_cell_types()
        self.update_cell_types_and_draw()

    def post_flip(self, iteration):
        pass

    @classmethod
    def get_options(self):
        print('\n')
        print('Do you want to customize the shape and appearance?')
        if input('y/N ---> ') in c.AFFIRMATIVE_ANSWERS:
            options = [
                {
                    'key': 'cells_per_row',
                    'question': 'How many cells wide?',
                    'default': c.DEFAULT_CELLS_PER_ROW
                },
                {
                    'key': 'rows_per_screen',
                    'question': 'How many cells high?',
                    'default': c.DEFAULT_ROWS_PER_SCREEN
                },
                {
                    'key': 'cell_width',
                    'question': 'How many pixels wide is each cell?',
                    'default': c.DEFAULT_CELL_WIDTH
                },
                {
                    'key': 'cell_height',
                    'question': 'How many pixels high is each cell?',
                    'default': c.DEFAULT_CELL_HEIGHT
                },
                {
                    'key': 'cell_margin',
                    'question': 'How many pixels between each cell?',
                    'default': c.DEFAULT_CELL_MARGIN
                },
                {
                    'key': 'tick_speed',
                    'question': 'Tick speed?',
                    'default': c.DEFAULT_TICK_SPEED
                },
                {
                    'key': 'wrap',
                    'question': 'Wrap at edges?',
                    'default': c.DEFAULT_WRAP_AT_EDGES
                },
            ]
        else:
            options = []
        return options

    @classmethod
    def get_int_options(self):
        return ['cells_per_row', 'rows_per_screen', 'cell_width', 'cell_height', 'cell_margin', 'tick_speed']

    @classmethod
    def get_truthy_options(self):
        return ['wrap']


class Cell():
    next_type = None
    rounds_since_type_change = 0
    type = 0
    initial_cell = False

    def __init__(self, row, column, grid, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.hereditary_attrs = dict()
        self.row = row
        self.column = column
        self.mg = grid
        self.width = self.mg.cell_width
        self.height = self.mg.cell_height
        self.margin = self.mg.cell_margin
        self.set_color()
        if not self.initial_cell:
            self.introduce_self_to_neighbors()

    def __str__(self):
        return 'cell row-{} column-{}'.format(self.row, self.column)

    def __repr__(self):
        return self.__str__()

    def normalize_color_val(self, val):
        return max(min(int(val), 255), 0)

    def set_color(self):
        color = self.origin_color
        self.color = Color(color.r, color.g, color.b)

    def iterate_color(self):
        pass

    def apply_rules(self):
        self.get_neighbors()
        for rule in self.rules:
            applied = getattr(self, rule)()
            if applied:
                break

    def update_type(self, next_type=None):
        if next_type is not None:
            self.next_type = next_type
        if self.next_type is not None:
            self.set_new_type()
            return
        self.rounds_since_type_change += 1
        self.iterate_color()

    def set_new_type(self):
        next_cell = self.next_type(self.row, self.column, self.mg, **self.hereditary_attrs)
        self.mg.grid[self.row][self.column] = next_cell

    def draw(self):
        pygame.draw.rect(
            self.mg.screen,
            self.color,
            [
                (self.width + self.margin) * self.column,
                (self.height + self.margin) * self.row,
                self.width,
                self.height,
            ]
        )

    def get_neighbors(self):
        if hasattr(self, 'neighbors'):
            return
        self.neighbor_top = self.get_neighbor_top()
        self.neighbor_right = self.get_neighbor_right()
        self.neighbor_bottom = self.get_neighbor_bottom()
        self.neighbor_left = self.get_neighbor_left()
        self.neighbors = {'top': self.neighbor_top, 'right': self.neighbor_right, 'bottom': self.neighbor_bottom, 'left': self.neighbor_left}

    def get_neighbor_top(self):
        if self.mg.wrap:
            row = self.row if self.row != 0 else self.mg.rows_per_screen
            return self.mg.grid[row - 1][self.column]
        elif self.row == 0:
            return None
        return self.mg.grid[self.row - 1][self.column]

    def get_neighbor_right(self):
        if self.mg.wrap:
            column = self.column + 1 if self.column != self.mg.cells_per_row - 1 else 0
            return self.mg.grid[self.row][column]
        if self.column == self.mg.cells_per_row - 1:
            return None
        return self.mg.grid[self.row][self.column + 1]

    def get_neighbor_bottom(self):
        if self.mg.wrap:
            row = self.row + 1 if self.row != self.mg.rows_per_screen - 1 else 0
            return self.mg.grid[row][self.column]
        if self.row == self.mg.rows_per_screen - 1:
            return None
        return self.mg.grid[self.row + 1][self.column]

    def get_neighbor_left(self):
        if self.mg.wrap:
            column = self.column if self.column != 0 else self.mg.cells_per_row
            return self.mg.grid[self.row][column - 1]
        elif self.column == 0:
            return None
        return self.mg.grid[self.row][self.column - 1]

    def get_neighbor_type(self, count=None, directions=None, type=None):
        if not directions:
            directions = c.DIRECTIONS

        matches = []
        for direction in directions:
            neighbor = self.neighbors[direction]
            if neighbor and neighbor.type == type:
                matches.append(neighbor)

        if not count:
            return matches
        elif len(matches) >= count:
            return matches
        return None

    def introduce_self_to_neighbors(self):
        self.get_neighbors()
        for direction in c.DIRECTIONS:
            self.neighbors[direction].accept_neighbor_introduction(self, direction)

    def accept_neighbor_introduction(self, neighbor, direction):
        self.get_neighbors()
        self.neighbors[direction] = neighbor
