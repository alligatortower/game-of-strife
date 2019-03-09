import pygame

from cells.main_loop import init_grid, main_loop
from cells import constants as c
from cells.models import Grid


pygame.init()
screen = pygame.display.set_mode(c.SCREEN_SIZE)
clock = pygame.time.Clock()
grid = Grid(screen)

init_grid(screen, grid)
main_loop(pygame, screen, grid, clock)
