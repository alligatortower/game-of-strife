import sys
from random import randint


from .models import EmptyCell, RandomCell
from . import constants as c


def init_grid(screen, grid):
    for row in range(c.CELLS_PER_ROW):
        grid.append([])
        for column in range(c.ROWS_PER_SCREEN):
            grid[row].append(EmptyCell(row, column, grid))

    for i in range(randint(1, 100)):
        add_random_cell_to_grid(grid)


def add_random_cell_to_grid(grid):
    row = randint(0, c.ROWS_PER_SCREEN - 1)
    column = randint(0, c.CELLS_PER_ROW - 1)
    random_cell = grid[row][column]
    if random_cell.state in [0, 3]:
        grid[row][column] = RandomCell(row, column, grid)


def main_loop(pygame, screen, grid, clock):
    current_iteration = 0

    while current_iteration < c.MAX_ITERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                add_random_cell_to_grid(grid)
                current_iteration = 0
                # pos = pygame.mouse.get_pos()
                # column = pos[0] // (c.CELL_WIDTH + c.CELL_MARGIN)
                # row = pos[1] // (c.CELL_HEIGHT + c.CELL_MARGIN)
                # grid[row][column].next_state = 1
                # print("Click ", pos, "Grid coordinates: ", row, column)

        if not current_iteration % 10:
            add_random_cell_to_grid(grid)

        screen.fill(c.BLACK)

        for row in range(c.CELLS_PER_ROW):
            for column in range(c.ROWS_PER_SCREEN):
                grid[row][column].get_next_state()

        for row in range(c.CELLS_PER_ROW):
            for column in range(c.ROWS_PER_SCREEN):
                cell = grid[row][column]
                cell.update_state()

        pygame.display.flip()
        clock.tick(c.SPEED)
        print('--------- TICK {} ----------'.format(current_iteration))
        print('oldest generation this round: {}'.format(grid.oldest_gen_this_round))
        grid.update_oldest_gen_since_start()
        print('oldest generation since start: {}'.format(grid.oldest_gen_since_start))
        # print(grid[1][5].rounds_since_state_change)
        # for cell in grid.state_1_cells:
        #     print(str(cell))

        current_iteration += 1
