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
    wrap = True
    grid = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value not in [None, '']:
                setattr(self, key, value)

        StartingCellClass = self.get_starting_cell_class()

        for row in range(self.rows_per_screen):
            self.grid.append([])
            for column in range(self.cells_per_row):
                self.grid[row].append(StartingCellClass(row, column, self))

    @property
    def state_map(self):
        raise NotImplementedError

    def get_starting_cell_class(self):
        raise NotImplementedError

    def create_screen(self):
        width = (self.cell_width * self.cells_per_row) + (self.cell_margin * self.cells_per_row) + self.cell_margin
        height = (self.cell_height * self.rows_per_screen) + (self.cell_margin * self.rows_per_screen) + self.cell_margin
        self.screen = pygame.display.set_mode((width, height))
        return self.screen

    def get_next_cell_states(self):
        self.call_method_on_each_cell('get_next_state')

    def update_cell_states(self):
        self.call_method_on_each_cell('update_state')

    def call_method_on_each_cell(self, method_name):
        for row in range(self.rows_per_screen):
            for column in range(self.cells_per_row):
                cell = self.grid[row][column]
                getattr(cell, method_name)()

    def pre_flip(self, iteration):
        self.get_next_cell_states()
        self.update_cell_states()

    def post_flip(self, iteration):
        pass

    @classmethod
    def get_options(self):
        options = {}
        if input('Custom grid options? y/N') in c.AFFIRMATIVE_ANSWERS:
            options['cells_per_row'] = input('How many cells wide? (Default: {}) -- '.format(c.DEFAULT_CELLS_PER_ROW))
            options['rows_per_screen'] = input('How many cells high? (Default: {}) -- '.format(c.DEFAULT_ROWS_PER_SCREEN))
            options['cell_width'] = input('How many pixels wide is each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_WIDTH))
            options['cell_height'] = input('How many pixels high is each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_HEIGHT))
            options['cell_margin'] = input('How many pixels between each cell? (Default: {}) -- '.format(c.DEFAULT_CELL_MARGIN))
            options['tick_speed'] = input('Tick speed? (Default: {}) -- '.format(c.DEFAULT_TICK_SPEED))
            for key, value in options.items():
                if value:
                    options[key] = int(value)

            options['wrap'] = not bool(input('Wrap at edges? (Default: True) "n" for False -- '))
        return options


class Cell():
    next_state = None
    rounds_since_state_change = 0
    state = 0

    def __init__(self, row, column, grid, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.row = row
        self.column = column
        self.mg = grid
        self.width = self.mg.cell_width
        self.height = self.mg.cell_height
        self.margin = self.mg.cell_margin
        self.set_color()

    def __str__(self):
        return 'cell row-{} column-{}'.format(self.row, self.column)

    def __repr__(self):
        return self.__str__()

    def set_color(self):
        color = self.origin_color
        self.color = Color(color.r, color.g, color.b)

    def iterate_color(self):
        pass

    def get_next_state(self):
        self.get_neighbors()
        for rule in self.rules:
            applied = getattr(self, rule)()
            if applied:
                break

    def update_state(self, next_state=None):
        if next_state is not None:
            self.next_state = next_state
        if self.next_state is not None:
            self.set_new_state()
        self.rounds_since_state_change += 1
        self.iterate_color()
        self.draw()

    def set_new_state(self):
        next_cell = self.mg.state_map[self.next_state](self.row, self.column, self.mg, parent_color=self.parent_color)
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
            row = self.row if self.row != 0 else self.mg.rows_per_screen - 1
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

    def get_neighbor_state(self, count=None, directions=None, state=None):
        if not directions:
            directions = ['top', 'right', 'bottom', 'left']

        matches = []
        for direction in directions:
            neighbor = self.neighbors[direction]
            if neighbor and neighbor.state == state:
                matches.append(neighbor)

        if not count:
            return matches
        elif len(matches) >= count:
            return matches
        return None
