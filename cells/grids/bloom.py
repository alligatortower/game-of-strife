from random import randint
from random import choice as randchoice
from pygame import Color

from cells.base_models import MasterGrid, Cell
from cells import constants as c

DEFAULT_MINIMUM_DECAY = 20
DEFAULT_CHANCE_FOR_RANDOM = 10


class BloomGrid(MasterGrid):
    name = 'Bloom Grid'
    description = 'Colored cells spread to empty space and slowly decay'
    oldest_gen_since_start = 0
    oldest_gen_past_rounds = []
    oldest_gen_this_round = 0
    rounds_remembered = 50
    minimum_decay = DEFAULT_MINIMUM_DECAY
    chance_for_random_ever_x_turns = DEFAULT_CHANCE_FOR_RANDOM

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for i in range(self.rounds_remembered):
            self.oldest_gen_past_rounds.append(0)

        for i in range(randint(1, 100)):
            self.add_random_cell_to_grid()

    @property
    def state_map(self):
        return [
            EmptyCell,
            RandomCell,
            AlmostEmptyCell,
        ]

    def get_starting_cell_class(self):
        return EmptyCell

    def add_random_cell_to_grid(self):
        row = randint(0, self.rows_per_screen - 1)
        column = randint(0, self.cells_per_row - 1)
        random_cell = self.grid[row][column]
        if random_cell.state in [0, 3]:
            self.grid[row][column] = RandomCell(row, column, self)

    def update_gen_this_round(self, gen):
        self.oldest_gen_this_round = max(self.oldest_gen_this_round, gen)

    def update_oldest_gen_since_start(self):
        self.oldest_gen_since_start = max(self.oldest_gen_since_start, self.oldest_gen_this_round)
        self.oldest_gen_past_rounds.pop()
        self.oldest_gen_past_rounds.insert(0, self.oldest_gen_this_round)
        self.oldest_gen_this_round = 0

    @property
    def averaged_oldest_gen_this_round(self):
        average = 0
        for val in self.oldest_gen_past_rounds:
            average += val
        return int(average / len(self.oldest_gen_past_rounds))

    def pre_flip(self, iteration):
        if not iteration % self.chance_for_random_ever_x_turns:
            self.add_random_cell_to_grid()
        super().pre_flip(iteration)

    def post_flip(self, iteration):
        print('oldest generation this round: {}'.format(self.oldest_gen_this_round))
        self.update_oldest_gen_since_start()
        print('oldest generation since start: {}'.format(self.oldest_gen_since_start))
        print('oldest gen past rounds:\n{}'.format(self.oldest_gen_past_rounds))
        print('average gen past rounds: {}'.format(self.averaged_oldest_gen_this_round))

    @classmethod
    def get_options(self):
        options = super().get_options()
        other_options = [
            {
                'key': 'minimum_decay',
                'question': 'Minimum number of ticks before a dead cell can decay into an empty cell?',
                'default': DEFAULT_MINIMUM_DECAY
            },
            {
                'key': 'chance_for_random_ever_x_turns',
                'question': 'Every __ turns, chance for new random cell to appear',
                'default': DEFAULT_CHANCE_FOR_RANDOM
            },
        ]
        options.extend(other_options)
        return options

    @classmethod
    def get_int_options(self):
        options = MasterGrid().get_int_options()
        options.extend(['minimum_decay', 'chance_for_random_every_x_turns'])
        return options


class BloomCell(Cell):
    gen = 0
    parent_gen = None
    almost_White_decay_rounds = 1

    def set_new_state(self):
        next_cell = self.mg.state_map[self.next_state](self.row, self.column, self.mg, parent_color=self.parent_color)
        if self.parent_gen is not None:
            next_cell.gen = self.parent_gen + 1
            self.mg.update_gen_this_round(next_cell.gen)
        self.mg.grid[self.row][self.column] = next_cell


class EmptyCell(BloomCell):
    rules = ['rule_1']
    origin_color = Color(0, 0, 0, 255)
    state = 0

    def rule_1(self):
        neighbors = self.get_neighbor_state(count=3, state=1)
        if neighbors:
            highest_gen = 0
            reds = []
            greens = []
            blues = []
            red = 0
            green = 0
            blue = 0

            for neighbor in neighbors:
                reds.append(neighbor.color.r)
                greens.append(neighbor.color.g)
                blues.append(neighbor.color.b)
                highest_gen = max(highest_gen, neighbor.gen)

            for value in reds:
                red += value / len(reds)
            for value in greens:
                green += value / len(greens)
            for value in blues:
                blue += value / len(blues)

            self.parent_color = Color(int(red), int(green), int(blue))
            self.parent_gen = highest_gen
            self.next_state = 1
            self.booped = True
            return True


class AlmostEmptyCell(BloomCell):
    rules = ['rule_reborn']
    origin_color = Color(240, 240, 240, 255)
    state = 2
    oldest_round_when_created = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldest_round_when_created = max(self.mg.averaged_oldest_gen_this_round, 1)

    @property
    def decay_rounds(self):
        return max(self.oldest_round_when_created * 2, self.mg.minimum_decay)

    def rule_reborn(self):
        if self.rounds_since_state_change > self.decay_rounds:
            self.next_state = 0
            return True

    def iterate_color(self):
        fraction = self.rounds_since_state_change / self.decay_rounds
        color_val = int(255 * fraction)
        color_val = 255 - color_val
        color_val = self.normalize_color_val(color_val)
        self.color.r = color_val
        self.color.g = color_val
        self.color.b = color_val


class RandomCell(BloomCell):
    decay_rate = 24
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
        starting_int = 0 + (int((self.rounds_since_state_change / self.decay_rate)) * self.color_decay_direction)
        min_int = -5 + starting_int
        max_int = 5 + starting_int
        ran_red = randint(min_int, max_int)
        ran_green = randint(min_int, max_int)
        ran_blue = randint(min_int, max_int)
        new_red = self.color.r + ran_red
        new_green = self.color.g + ran_green
        new_blue = self.color.b + ran_blue
        self.color.r = self.normalize_color_val(new_red)
        self.color.g = self.normalize_color_val(new_green)
        self.color.b = self.normalize_color_val(new_blue)

    def rule_0(self):
        skip = randint(0, 2)
        if skip:
            return
        choice = randchoice(c.DIRECTIONS)
        neighbor = self.neighbors[choice]
        if neighbor and not neighbor.next_state and neighbor.state not in [1, 2]:
            neighbor.parent_color = self.color
            neighbor.parent_gen = self.gen
            neighbor.color_decay_direction = self.color_decay_direction
            neighbor.update_state(next_state=1)
            return True

    def rule_2(self):
        if self.color.r > 240 and self.color.g > 240 and self.color.b > 240:
            self.next_state = 2
            self.gen = 0
            return True
