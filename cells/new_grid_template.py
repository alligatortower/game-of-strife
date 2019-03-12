from .base_models import MasterGrid, Cell
from pygame import Color


DEFAULT_WANTS_OPTIONS = False


class NewGrid(MasterGrid):
    # add custom global grid vars

    def __init__(self, **kwargs):
        # add custom startup logic before grid is set up
        super().__init__(**kwargs)
        # add custom startup logic after grid is set up

    @property
    def state_map(self):
        # must return an array of cell classes. The index of each cell is it's state
        return [
            CustomCell1,
            CustomCell2,
        ]

    def get_starting_cell_class(self):
        # must return a cell class. The entire grid will be set as this type of cell to start
        # OR remove the super call in __init__ and set up the grid some other way
        return CustomCell1

    def pre_flip(self, iteration):
        super().pre_flip(iteration)
        # things to do / values to update update before the screen flips

    def post_flip(self, iteration):
        # generally for printing debug information to the console
        pass

    @classmethod
    def get_options(self):
        options = super().get_options()
        other_options = {}
        other_options['other'] = input('do you want your grid to have custom options? {} -- '.format(DEFAULT_WANTS_OPTIONS))
        # input() will return a str, make sure you convert that into whatever value you actually want, probably an int
        for key, value in other_options.items():
            if value:
                other_options[key] = int(value)
        options.update(other_options)
        return options


class NewCell(Cell):
    # add variables shared by all cells in your grid
    # overwrite base cell methods for all of your cells
    pass


class CustomCell1(NewCell):
    # subclass all of your actual cells from your base cell

    # its state should match its index in the grids state map
    state = 0
    # add the color they begin as (if not stay as the whole time)
    origin_color = Color(255, 0, 0, 255)
    # add the rules they follow, this is an array with string versions of methods
    # rules shared by multiple cells can be placed on the NewCell equivalent
    rules = ['first_rule']

    def first_rule(self):
        if hasattr(self, 'have_fun'):
            self.next_state = 1


class CustomCell2(NewCell):
    # you can create as many cells as you want
    state = 1
    origin_color = Color(0, 255, 0, 255)
    rules = ['other_rule']

    def other_rule(self):
        pass
