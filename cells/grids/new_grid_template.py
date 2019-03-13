from cells.base_models import MasterGrid, Cell
from pygame import Color


DEFAULT_CUSTOM_OPTION = False
DEFAULT_ALTERNATIVE_OPTION = 0


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
        # call super if you want to include the default options for grid / cell size
        options = super().get_options()
        # currently only accepts int or bool options
        other_options = [
            {
                'key': 'custom_option',  # the key will map to grid attributes i.e. `grid.custom_option` on init
                'question': 'Hey user, do you want this custom option',
                'default': DEFAULT_CUSTOM_OPTION  # the default will be displayed to the user.
            },
            {
                'key': 'alternative_option',
                'question': ['Hey user,', 'do you want this alternative option'],  # question can be a list of strings. Each will print to their own line
                'default': DEFAULT_ALTERNATIVE_OPTION,
                'valid_anwers': ['0', '1', '2']  # Optional, will only accept answers that appear in this list
            },
        ]
        options.extend(other_options)
        return options

    @classmethod
    def get_int_options(self):
        # this and the following method are used to validate the questions. They'll convert the strings returned by input() into the datatype you want.
        options = MasterGrid.get_int_options()
        options.extend(['alternative_option', ])
        return options

    @classmethod
    def get_truthy_options(self):
        options = MasterGrid.get_truthy_options()
        options.extend(['custom_option'])
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
