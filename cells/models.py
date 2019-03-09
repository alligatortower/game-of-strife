import pygame

from . import constants as c


class Grid(list):
    state_0_cells = []
    state_1_cells = []
    state_2_cells = []
    state_3_cells = []

    def __init__(self, screen):
        self.screen = screen

    def update_state_lists_for_cell(self, cell):
        remove_list = 'state_{}_cells'.format(cell.state)
        try:
            getattr(self, remove_list).remove(cell)
        except ValueError:
            print('{} not in {}'.format(cell, remove_list))

        append_list = 'state_{}_cells'.format(cell.next_state)
        try:
            getattr(self, append_list).append(cell)
        except ValueError:
            print('{} not in {}'.format(cell, append_list))


class Cell():
    width = c.CELL_WIDTH
    height = c.CELL_HEIGHT
    margin = c.CELL_MARGIN
    rounds_since_state_change = 0
    next_state = None

    def __init__(self, row, column, grid, starting_state=0):
        self.row = row
        self.column = column
        self.grid = grid
        self.state = starting_state

    def __str__(self):
        return 'cell row-{} column-{}'.format(self.row, self.column)

    @property
    def color(self):
        return c.COLOR_MAP[self.state]

    def get_next_state(self):
        self.get_neighbors()

        if self.get_neighbor_state(directions=['top'], state=1) and self.state == 0:
            self.next_state = 1

        elif self.get_neighbor_state(directions=['top'], state=1) and self.get_neighbor_state(directions=['bottom'], state=1) and self.state == 1:
            self.next_state = 2

        elif self.get_neighbor_state(directions=['left'], state=2) \
           and self.state == 0:
                self.next_state = 1

        elif self.rounds_since_state_change > 3 and self.state != 0:
            if self.state == 1:
                self.next_state = 2
            elif self.state == 2:
                self.next_state = 1

        elif self.get_neighbor_state(count=2, state=1) and self.get_neighbor_state(count=2, state=2):
            self.next_state = 3

    def get_neighbor_state(self, count=None, directions=None, state=None):
        if not directions:
            directions = ['top', 'right', 'bottom', 'left']

        matches = 0
        for direction in directions:
            if self.neighbors[direction] and self.neighbors[direction].state == state:
                matches += 1

        if not count:
            return bool(matches)
        else:
            return matches >= count

    def update_state(self, next_state=None):
        if next_state:
            self.next_state = next_state
        if self.next_state is not None:
            self.grid.update_state_lists_for_cell(self)
            self.state = self.next_state
            self.next_state = None
            self.rounds_since_state_change = 0
        else:
            self.rounds_since_state_change += 1
        self.draw()

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
