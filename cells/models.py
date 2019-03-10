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
    rounds_since_state_change = 0
    next_state = None
    gen = 0
    color_decay_direction = 1
    parent_color = None
    parent_gen = None

    def __init__(self, row, column, grid, starting_state=0):
        self.row = row
        self.column = column
        self.grid = grid
        self.state = starting_state
        self.set_color()
        # if randint(0, 1):
        #     self.color_decay_direction = -1

    def __str__(self):
        return 'cell row-{} column-{}'.format(self.row, self.column)

    @property
    def rules(self):
        return c.RULES[self.state]

    def set_color(self):
        if self.parent_color:
            self.color = Color(self.parent_color.r, self.parent_color.g, self.parent_color.b)
            self.parent_color = None
            return
        elif self.state == 1:
            self.color = Color(randint(0, 255), randint(0, 255), randint(0, 255))
            return
        color = c.COLOR_MAP[self.state]
        self.color = Color(color.r, color.g, color.b)

    def get_next_state(self):
        self.get_neighbors()
        for rule in self.rules:
            applied = getattr(self, rule)()
            if applied:
                break

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

    def rule_1(self):
        neighbors = self.get_neighbor_state(count=2, state=1)
        if neighbors:
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
            for value in r:
                red += value / len(r)
            for value in g:
                green += value / len(g)
            for value in b:
                blue += value / len(b)

            self.parent_color = Color(int(red), int(green), int(blue))
            self.next_state = 1
            return True

    def rule_2(self):
        if self.color.r > 240 and self.color.g > 240 and self.color.b > 240:
            self.next_state = 2
            self.gen = 0
            return True
        elif self.color.r < 15 and self.color.g < 15 and self.color.b < 15:
            self.next_state = 4
            self.gen = 0
            return True

    def rule_3(self):
        if self.rounds_since_state_change > 40:
            self.next_state = 0
            return True

    def rule_4(self):
        if self.rounds_since_state_change > 31:
            self.next_state = 3
            return True

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

    def update_state(self, next_state=None):
        if next_state:
            self.next_state = next_state
        if self.next_state is not None:
            self.set_new_state()
        else:
            self.rounds_since_state_change += 1
            self.iterate_color()
        self.draw()

    def set_new_state(self):
        if self.parent_gen is not None:
            self.gen = self.parent_gen + 1
            self.parent_get = None
            self.grid.update_gen_this_round(self.gen)
        else:
            self.gen = 0
        self.state = self.next_state
        self.next_state = None
        self.rounds_since_state_change = 0
        self.set_color()

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

    def iterate_color(self):
        getattr(self, 'iterate_color_{}'.format(self.state))()

    def iterate_color_0(self):
        pass

    def iterate_color_1(self):
        starting_int = 0 + (int((self.rounds_since_state_change / 10)) * self.color_decay_direction)
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

    def iterate_color_2(self):
        pass

    def iterate_color_3(self):
        pass

    def iterate_color_4(self):
        pass

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
