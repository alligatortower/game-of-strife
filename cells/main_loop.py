import sys

from . import constants as c


def main_loop(pygame, clock, GridClass, choices):
    grid = GridClass(**choices)
    grid.create_screen()
    current_iteration = 0

    while current_iteration < c.MAX_ITERATIONS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     grid.add_random_cell_to_grid()

        grid.screen.fill(c.BLACK)

        grid.pre_flip(current_iteration)
        pygame.display.flip()
        clock.tick(grid.tick_speed)

        print('--------- TICK {} ----------'.format(current_iteration))
        grid.post_flip(current_iteration)

        current_iteration += 1
