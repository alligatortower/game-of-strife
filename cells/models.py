from random import randint
from random import choice as randchoice
import pygame
from pygame import Color

from . import constants as c


class Grid(list):
    oldest_gen_since_start = 0
    oldest_gen_this_round = 0

    def __init__(self, screen):
        self.screen = screen

    def update_gen_this_round(self, gen):
        self.oldest_gen_this_round = max(self.oldest_gen_this_round, gen)

    def update_oldest_gen_since_start(self):
        self.oldest_gen_since_start = max(self.oldest_gen_since_start, self.oldest_gen_this_round)
        self.oldest_gen_this_round = 0


class Cell():
    width = c.CELL_WIDTH
    height = c.CELL_HEIGHT
    margin = c.CELL_MARGIN
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
        self.set_color()

    def __str__(self):
        return 'cell row-{} column-{}'.format(self.row, self.column)

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
        self.grid[self.row][self.column] = next_cell

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
        neighbors = {'top': self.neighbor_top, 'right': self.neighbor_right, 'bottom': self.neighbor_bottom, 'left': self.neighbor_left}
        self.neighbors = neighbors
        return

    def get_neighbor_top(self):
        if self.row == 0:
            return None
        return self.grid[self.row - 1][self.column]

    def get_neighbor_right(self):
        if self.column == c.CELLS_PER_ROW - 1:
            return None
        return self.grid[self.row][self.column + 1]

    def get_neighbor_bottom(self):
        if self.row == c.ROWS_PER_SCREEN - 1:
            return None
        return self.grid[self.row + 1][self.column]

    def get_neighbor_left(self):
        if self.column == 0:
            return None
        return self.grid[self.row][self.column - 1]

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
    origin_color = Color(255, 255, 255, 255)
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
    origin_color = Color(15, 15, 15, 255)
    state = 2
    almost_White_decay_rounds = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.almost_White_decay_rounds = self.grid.oldest_gen_this_round

    def rule_reborn(self):
        if self.rounds_since_state_change > self.almost_White_decay_rounds * 2:
            self.next_state = 0
            return True

    def iterate_color(self):
        fraction = self.rounds_since_state_change / (self.almost_White_decay_rounds * 2)
        color_val = 255 * fraction
        self.color = Color(color_val, color_val, color_val)


class RandomCell(Cell):
    decay_rate = 20
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
        starting_int = 0 - (int((self.rounds_since_state_change / self.decay_rate)) * self.color_decay_direction)
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
        if self.color.r < 15 and self.color.g < 15 and self.color.b < 15:
            self.next_state = 2
            self.gen = 0
            return True


STATE_MAP = [
    EmptyCell,
    RandomCell,
    AlmostEmptyCell,
]
