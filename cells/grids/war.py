from random import randint
from random import choice as randchoice
from pygame import Color

from cells.base_models import MasterGrid, Cell
from cells import constants as c

DEFAULT_MINIMUM_DECAY = 20
DEFAULT_CHANCE_FOR_RANDOM = 0
DEFAULT_AMOUNT_TO_START = 2
DEFAULT_SURROUND_PROCREATES = False
DEFAULT_CANNOT_BE_KILLED_UNTIL = 0
DEFAULT_CANNOT_KILL_AFTER = 0
DEFAULT_YOUNG_EAT_OLD = 1  # 0 off, 1 young eat old, 2 old eat young


class WarGrid(MasterGrid):
    ''' Based on BloomGrid '''
    name = 'War Grid'
    description = 'Colored cells fight for supremecy'
    oldest_gen_since_start = 0
    oldest_gen_past_rounds = []
    oldest_gen_this_round = 0
    rounds_remembered = 50
    family_count = 0
    minimum_decay = DEFAULT_MINIMUM_DECAY
    chance_for_random_ever_x_turns = DEFAULT_CHANCE_FOR_RANDOM
    amount_to_start = DEFAULT_AMOUNT_TO_START
    surround_procreates = DEFAULT_SURROUND_PROCREATES
    cannot_be_killed_until = DEFAULT_CANNOT_BE_KILLED_UNTIL
    cannot_kill_after = DEFAULT_CANNOT_KILL_AFTER
    young_eat_old = DEFAULT_YOUNG_EAT_OLD

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for i in range(self.rounds_remembered):
            self.oldest_gen_past_rounds.append(0)

        for i in range(self.amount_to_start):
            self.add_random_cell_to_grid()

    def get_starting_cell_class(self):
        return EmptyCell

    def add_random_cell_to_grid(self):
        row = randint(0, self.rows_per_screen - 1)
        column = randint(0, self.cells_per_row - 1)
        random_cell = self.grid[row][column]
        if random_cell.type in [0, 3]:
            self.grid[row][column] = RandomCell(row, column, self, family=self.get_next_family())

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

    def get_next_family(self):
        family = self.family_count
        self.family_count += 1
        return family

    def pre_flip(self, iteration):
        if self.chance_for_random_ever_x_turns != 0 and not (iteration % self.chance_for_random_ever_x_turns):
            self.add_random_cell_to_grid()
        super().pre_flip(iteration)

    def post_flip(self, iteration):
        print('oldest generation this round: {}'.format(self.oldest_gen_this_round))
        self.update_oldest_gen_since_start()
        print('oldest generation since start: {}'.format(self.oldest_gen_since_start))
        print('average gen past rounds: {}'.format(self.averaged_oldest_gen_this_round))
        print('families created: {}'.format(self.family_count))

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
                'question': 'Every __ turns chance for new random cell to appear',
                'default': DEFAULT_CHANCE_FOR_RANDOM
            },
            {
                'key': 'amount_to_start',
                'question': 'How many cells to start?',
                'default': DEFAULT_AMOUNT_TO_START
            },
            {
                'key': 'surround_procreates',
                'question': 'If empty cells are surrounded, they have a chance to spawn a new family?',
                'default': DEFAULT_SURROUND_PROCREATES
            },
            {
                'key': 'cannot_be_killed_until',
                'question': 'A cell cannot be killed until it is this many rounds old?',
                'default': DEFAULT_CANNOT_BE_KILLED_UNTIL
            },
            {
                'key': 'young_eat_old',
                'question': ['0 --> Do not compare ages.', '1 --> Younger cells win.', '2 --> Older cells win'],
                'default': DEFAULT_YOUNG_EAT_OLD,
                'valid_anwers': ['0', '1', '2']
            },
        ]
        options.extend(other_options)
        return options

    @classmethod
    def get_int_options(self):
        options = MasterGrid.get_int_options()
        options.extend([
            'minimum_decay', 'chance_for_random_every_x_turns',
            'amount_to_start', 'cannot_be_killed_until', 'young_eat_old'
        ])
        return options

    @classmethod
    def get_truthy_options(self):
        options = MasterGrid.get_truthy_options()
        options.extend(['surround_procreates'])
        return options


class BloomCell(Cell):
    gen = 0
    almost_White_decay_rounds = 1


class EmptyCell(BloomCell):
    origin_color = Color(0, 0, 0, 255)
    type = 0

    @property
    def rules(self):
        if self.mg.surround_procreates:
            return ['rule_procreate']
        return []

    def rule_procreate(self):
        neighbors = self.get_neighbor_type(1, count=4)
        if neighbors:
            if randint(0, 2):
                return
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

            self.hereditary_attrs['origin_color'] = Color(int(red), int(green), int(blue))
            self.hereditary_attrs['gen'] = highest_gen + 1
            self.hereditary_attrs['family'] = self.mg.get_next_family()
            self.next_type = RandomCell
            return True


class RandomCell(BloomCell):
    decay_rate = 40
    color_decay_direction = 1
    color_offset = 3
    origin_color = None
    type = 1
    rules = ['rule_eat', 'rule_social', 'rule_die']

    def __init__(self, row, column, grid, **kwargs):
        new_gen = kwargs.get('gen')
        if new_gen:
            grid.update_gen_this_round(new_gen)
        super().__init__(row, column, grid, **kwargs)

    def set_color(self):
        if not hasattr(self, 'color') and self.origin_color:
            self.color = Color(self.origin_color.r, self.origin_color.g, self.origin_color.b)
            return
        self.color = Color(randint(0, 255), randint(0, 255), randint(0, 255))

    def iterate_color(self):
        starting_int = 0 + (int((self.rounds_since_type_change / self.decay_rate)) * self.color_decay_direction)
        min_int = (-1 * self.color_offset) + starting_int
        max_int = self.color_offset + starting_int
        ran_red = randint(min_int, max_int)
        ran_green = randint(min_int, max_int)
        ran_blue = randint(min_int, max_int)
        new_red = self.color.r + ran_red
        new_green = self.color.g + ran_green
        new_blue = self.color.b + ran_blue
        self.color.r = self.normalize_color_val(new_red)
        self.color.g = self.normalize_color_val(new_green)
        self.color.b = self.normalize_color_val(new_blue)

    def choose_random_neighbor(self, directions=c.DIRECTIONS):
        choice = randchoice(directions)
        return self.neighbors[choice]

    def rule_eat(self):
        neighbor = self.choose_random_neighbor()
        if not neighbor or neighbor.next_type:
            return
        eat_rules = ['eat_if_blank', 'eat_if_not_family']
        for rule in eat_rules:
            eaten = getattr(self, rule)(neighbor)
            if eaten:
                break

    def eat_neighbor(self, neighbor):
        neighbor.hereditary_attrs['family'] = self.family
        neighbor.hereditary_attrs['origin_color'] = self.color
        neighbor.hereditary_attrs['gen'] = self.gen + 1
        neighbor.update_type(next_type=RandomCell)

    def eat_if_blank(self, neighbor):
        if neighbor.type != 0:
            return
        self.eat_neighbor(neighbor)
        return True

    def eat_if_not_family(self, neighbor):
        if neighbor.type != 1 or neighbor.family == self.family:
            return
        # skip = randint(0, 2)
        # if skip:
        #     return

        if self.mg.cannot_be_killed_until != 0 \
                and neighbor.rounds_since_type_change <= self.mg.cannot_be_killed_until:
            return
        elif self.mg.cannot_kill_after != 0 and self.rounds_since_type_change > self.mg.cannot_kill_after:
            return
        elif self.mg.young_eat_old == 1 \
                and self.rounds_since_type_change >= neighbor.rounds_since_type_change:
            return
        elif self.mg.young_eat_old == 2 \
                and self.rounds_since_type_change <= neighbor.rounds_since_type_change:
            return

        if max(self.color.r, max(self.color.g, self.color.b)) > 200:
            self.color.r = self.normalize_color_val(self.color.r - 5)
            self.color.g = self.normalize_color_val(self.color.g - 5)
            self.color.b = self.normalize_color_val(self.color.b - 5)

        self.eat_neighbor(neighbor)
        return True

    def rule_social(self):
        neighbors_4 = self.get_neighbor_type(1, count=4)
        if neighbors_4:
            my_family = True
            for neighbor in neighbors_4:
                if neighbor.family != self.family:
                    my_family = False
            if my_family:
                self.rounds_since_type_change = 0
        neighbors_3 = self.get_neighbor_type(1, count=4)
        if neighbors_3:
            my_family = True
            for neighbor in neighbors_3:
                if neighbor.family != self.family:
                    my_family = False
            if my_family:
                self.rounds_since_type_change -= 1

    def rule_die(self):
        if self.color.r > 240 and self.color.g > 240 and self.color.b > 240:
            self.next_type = DeadCell
            self.gen = 0
            return True


class DeadCell(BloomCell):
    rules = ['rule_reborn']
    origin_color = Color(240, 240, 240, 255)
    type = 2
    oldest_round_when_created = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldest_round_when_created = max(self.mg.averaged_oldest_gen_this_round, 1)

    @property
    def decay_rounds(self):
        return max(self.oldest_round_when_created * 2, self.mg.minimum_decay)

    def rule_reborn(self):
        if self.rounds_since_type_change > self.decay_rounds:
            self.next_type = EmptyCell
            return True

    def iterate_color(self):
        fraction = max(self.rounds_since_type_change, 1) / self.decay_rounds
        color_val = int(255 * fraction)
        color_val = 255 - color_val
        color_val = self.normalize_color_val(color_val)
        self.color.r = color_val
        self.color.g = color_val
        self.color.b = color_val
