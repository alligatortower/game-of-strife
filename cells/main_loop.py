import sys


from .models import Cell
from . import constants as c


def init_grid(screen, grid):
    for row in range(c.CELLS_PER_ROW):
        grid.append([])
        for column in range(c.ROWS_PER_SCREEN):
            grid[row].append(Cell(row, column, grid, starting_state=c.STARTING_STATE))

    grid[1][5].update_state(next_state=1)


def main_loop(pygame, screen, grid, clock):
    current_iteration = 0

    while current_iteration < c.MAX_ITERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                column = pos[0] // (c.CELL_WIDTH + c.CELL_MARGIN)
                row = pos[1] // (c.CELL_HEIGHT + c.CELL_MARGIN)
                grid[row][column].next_state = 1
                print("Click ", pos, "Grid coordinates: ", row, column)

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
        print(grid[1][5].rounds_since_state_change)
        # for cell in grid.state_1_cells:
        #     print(str(cell))

        current_iteration += 1
