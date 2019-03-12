import sys

from .models import GridMaster
from . import constants as c


def main_loop(pygame, clock, choices):

    grid = GridMaster(**choices)
    grid.create_screen()
    current_iteration = 0

    while current_iteration < c.MAX_ITERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                grid.add_random_cell_to_grid()
                current_iteration = 0
                # pos = pygame.mouse.get_pos()
                # column = pos[0] // (c.CELL_WIDTH + c.CELL_MARGIN)
                # row = pos[1] // (c.CELL_HEIGHT + c.CELL_MARGIN)
                # grid[row][column].next_state = 1
                # print("Click ", pos, "Grid coordinates: ", row, column)

        if not current_iteration % 10:
            grid.add_random_cell_to_grid()

        grid.screen.fill(c.BLACK)
        grid.get_next_cell_states()
        grid.update_cell_states()

        pygame.display.flip()
        clock.tick(grid.tick_speed)
        print('--------- TICK {} ----------'.format(current_iteration))
        print('oldest generation this round: {}'.format(grid.oldest_gen_this_round))
        grid.update_oldest_gen_since_start()
        print('oldest generation since start: {}'.format(grid.oldest_gen_since_start))
        print('oldest gen past rounds:\n{}'.format(grid.oldest_gen_past_rounds))
        print('average gen past rounds: {}'.format(grid.averaged_oldest_gen_this_round))
        # print(grid[1][5].rounds_since_state_change)
        # for cell in grid.state_1_cells:
        #     print(str(cell))

        current_iteration += 1
