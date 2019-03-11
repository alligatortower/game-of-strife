from random import randint
from random import choice as randchoice
import pygame
from pygame import Color

from . import constants as c


class GridMaster():
    cells_per_row = c.DEFAULT_CELLS_PER_ROW
    rows_per_screen = c.DEFAULT_ROWS_PER_SCREEN
    cell_width = c.DEFAULT_CELL_WIDTH
    cell_height = c.DEFAULT_CELL_HEIGHT
    cell_margin = c.DEFAULT_CELL_MARGIN
    tick_speed = c.DEFAULT_TICK_SPEED

    oldest_gen_since_start = 0
    oldest_gen_this_round = 0
    wrap = True
    grid = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value:
                setattr(self, key, value)

        for row in range(self.rows_per_screen):
            self.grid.append([])
            for column in range(self.cells_per_row):
                self.grid[row].append(EmptyCell(row, column, self))

        for i in range(randint(1, 100)):
            self.add_random_cell_to_grid()

    def add_random_cell_to_grid(self):
        row = randint(0, self.rows_per_screen - 1)
        column = randint(0, self.cells_per_row - 1)
        random_cell = self.grid[row][column]
        if random_cell.state in [0, 3]:
            self.grid[row][column] = RandomCell(row, column, self)

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

    def update_gen_this_round(self, gen):
        self.oldest_gen_this_round = max(self.oldest_gen_this_round, gen)

    def update_oldest_gen_since_start(self):
        self.oldest_gen_since_start = max(self.oldest_gen_since_start, self.oldest_gen_this_round)
        self.oldest_gen_this_round = 0


class Cell():
    next_state = None
    rounds_since_state_change = 0
    gen = 0
    parent_gen = None
    almost_White_decay_rounds = 1
    state = 0

    def __init__(self, row, column, grid, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.row = row
        self.column = column
        self.grid = grid
        self.width = self.grid.cell_width
        self.height = self.grid.cell_height
        self.margin = self.grid.cell_margin
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
        if next_state:
            self.next_state = next_state
        if self.next_state is not None:
            self.set_new_state()
        self.rounds_since_state_change += 1
        self.iterate_color()
        self.draw()

    def set_new_state(self):
        next_cell = STATE_MAP[self.next_state](self.row, self.column, self.grid, parent_color=self.parent_color)
        if self.parent_gen is not None:
            next_cell.gen = self.parent_gen + 1
            self.grid.update_gen_this_round(next_cell.gen)
        self.grid.grid[self.row][self.column] = next_cell

    def draw(self):
        pygame.draw.rect(
            self.grid.screen,
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
        if self.grid.wrap:
            row = self.row if self.row != 0 else self.grid.rows_per_screen - 1
            return self.grid.grid[row - 1][self.column]
        elif self.row == 0:
            return None
        return self.grid.grid[self.row - 1][self.column]

    def get_neighbor_right(self):
        if self.grid.wrap:
            column = self.column + 1 if self.column != self.grid.cells_per_row - 1 else 0
            return self.grid.grid[self.row][column]
        if self.column == self.grid.cells_per_row - 1:
            return None
        return self.grid.grid[self.row][self.column + 1]

    def get_neighbor_bottom(self):
        if self.grid.wrap:
            row = self.row + 1 if self.row != self.grid.rows_per_screen - 1 else 0
            return self.grid.grid[row][self.column]
        if self.row == self.grid.rows_per_screen - 1:
            return None
        return self.grid.grid[self.row + 1][self.column]

    def get_neighbor_left(self):
        if self.grid.wrap:
            column = self.column if self.column != 0 else self.grid.cells_per_row
            return self.grid.grid[self.row][column - 1]
        elif self.column == 0:
            return None
        return self.grid.grid[self.row][self.column - 1]

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


class EmptyCell(Cell):
    rules = ['rule_1']
    origin_color = Color(0, 0, 0, 255)
    state = 0

    def rule_1(self):
        neighbors = self.get_neighbor_state(count=2, state=1)
        if neighbors:
            highest_gen = 0
            r = []
            g = []
            b = []
            red = 0
            green = 0
            blue = 0

            for neighbor in neighbors:
                r.append(neighbor.color.r)
                g.append(neighbor.color.g)
                b.append(neighbor.color.b)
                highest_gen = max(highest_gen, neighbor.gen)

            for value in r:
                red += value / len(r)
            for value in g:
                green += value / len(g)
            for value in b:
                blue += value / len(b)

            self.parent_color = Color(int(red), int(green), int(blue))
            self.parent_gen = highest_gen
            self.next_state = 1
            return True


class AlmostEmptyCell(Cell):
    rules = ['rule_reborn']
    origin_color = Color(240, 240, 240, 255)
    state = 2
    oldest_round_when_created = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldest_round_when_created = max(self.grid.oldest_gen_this_round, 1)

    @property
    def decay_rounds(self):
        return max(self.oldest_round_when_created * 2, 5)

    def rule_reborn(self):
        if self.rounds_since_state_change > self.decay_rounds:
            self.next_state = 0
            return True

    def iterate_color(self):
        fraction = self.rounds_since_state_change / self.decay_rounds
        color_val = int(255 * fraction)
        color_val = 255 - color_val
        color_val = max(min(color_val, 255), 0)
        self.color.r = color_val
        self.color.g = color_val
        self.color.b = color_val


class RandomCell(Cell):
    decay_rate = 24
    color_decay_direction = 1
    parent_color = None
    state = 1
    rules = ['rule_0', 'rule_2']

    def set_color(self):
        if self.parent_color:
            self.color = Color(self.parent_color.r, self.parent_color.g, self.parent_color.b)
            self.parent_color = None
            return
        self.color = Color(randint(0, 255), randint(0, 255), randint(0, 255))

    def iterate_color(self):
        starting_int = 0 + (int((self.rounds_since_state_change / self.decay_rate)) * self.color_decay_direction)
        min_int = -5 + starting_int
        max_int = 5 + starting_int
        ran_red = randint(min_int, max_int)
        ran_green = randint(min_int, max_int)
        ran_blue = randint(min_int, max_int)
        new_red = self.color.r + ran_red
        new_green = self.color.g + ran_green
        new_blue = self.color.b + ran_blue
        self.color.r = max(min(new_red, 255), 0)
        self.color.g = max(min(new_green, 255), 0)
        self.color.b = max(min(new_blue, 255), 0)

    def rule_0(self):
        skip = randint(0, 2)
        if skip:
            return
        choice = randchoice(['top', 'right', 'bottom', 'left'])
        neighbor = self.neighbors[choice]
        if neighbor and neighbor.state not in [1, 2, 4]:
            neighbor.parent_color = self.color
            neighbor.parent_gen = self.gen
            neighbor.color_decay_direction = self.color_decay_direction
            neighbor.update_state(next_state=1)
            return True

    def rule_2(self):
        if self.color.r > 240 and self.color.g > 240 and self.color.b > 240:
            self.next_state = 2
            self.gen = 0
            return True


STATE_MAP = [
    EmptyCell,
    RandomCell,
    AlmostEmptyCell,
]
