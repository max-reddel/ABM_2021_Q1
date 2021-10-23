from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *
from Scripts.Enums import *


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width=20, height=15, n_visitors=10, female_ratio=0.5, adult_ratio=0.5, familiarity=0.1,
                 valid_exits=ExitType.ABC):

        super().__init__()

        self.female_ratio = female_ratio
        self.adult_ratio = adult_ratio
        self.familiarity = familiarity
        self.valid_exits = valid_exits

        self.id_counter = 0

        self.n_staff = 0
        self.n_visitors = n_visitors
        self.safe_agents = set()


        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.schedule = RandomActivation(self)
        self.destinations = {Destination.DESK: [],
                             Destination.SHELF: [],
                             Destination.EXIT: [],
                             Destination.EXITA: [],
                             Destination.EXITB: [],
                             Destination.EXITC: [],
                             Destination.HELPDESK: []}

        self.alarm = Alarm(self.next_id(), self)

        self.end_time = - self.alarm.starting_time

        self.grid.place_agent(self.alarm, (2, 6))

        # Create and add agents to the grid and schedule
        self.fill_grid()
        self.set_up_exits()

        self.not_spawnable_objects = [Wall, Obstacle, Desk, OutOfBounds, Exit, HelpDesk, Shelf, DeskInteractive,
                                      HelpDeskInteractiveForHelpee, HelpDeskInteractiveForHelper, ShelfInteractive]
        self.spawn_visitors(n=self.n_visitors)
        self.spawn_staff()

        self.datacollector = DataCollector(model_reporters={"safe_agents": self.get_nr_of_safe_agents})

    def is_done(self):
        return len(self.safe_agents) >= self.n_staff + self.n_visitors

    def next_id(self):
        """
        Returns current id and increments the id_counter such that each agent can have a unique id.
        :return:
        """
        self.id_counter += 1
        return self.id_counter - 1

    def set_up_exits(self):

        if self.valid_exits == ExitType.ABC:
            pass
        elif self.valid_exits == ExitType.A:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA]
        elif self.valid_exits == ExitType.B:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITB]
        elif self.valid_exits == ExitType.C:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITC]
        elif self.valid_exits == ExitType.AB:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA] + self.destinations[Destination.EXITB]
        elif self.valid_exits == ExitType.BC:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITB] + self.destinations[Destination.EXITC]
        elif self.valid_exits == ExitType.AC:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA] + self.destinations[Destination.EXITC]

    def get_total_evacuation_time(self):
        return self.end_time

    def get_nr_of_safe_agents(self, dummy=1):
        return len(self.safe_agents)

    def step(self):

        self.end_time += 1
        self.schedule.step()
        self.datacollector.collect(self)
        # print('step')

    def add_exit_to_correct_keys(self, exit_agent, pos):

        self.destinations[Destination.EXIT].append(pos)

        if isinstance(exit_agent, ExitA):
            self.destinations[Destination.EXITA].append(pos)

        elif isinstance(exit_agent, ExitB):
            self.destinations[Destination.EXITB].append(pos)

        elif isinstance(exit_agent, ExitC):
            self.destinations[Destination.EXITC].append(pos)

    def fill_grid(self):

        """Place outer walls"""

        for i in range(self.grid.width):
            # lowest row
            if i != 16 and i != 17:  # space for exit
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(i, 0))
            # highest row
            self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(i, self.grid.height - 1))

        for i in range(self.grid.height):
            # left col
            if i != 4 and i != 5:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(0, i))
            # right col
            if i != 12 and i != 13:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(self.grid.width - 1, i))

        """Place exits"""

        # left exit
        pos = (0, 4)
        ex = ExitA(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        pos = (0, 5)
        ex = ExitA(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        # right exit
        pos = (self.grid.width - 1, 12)
        ex = ExitB(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        pos = (self.grid.width - 1, 13)
        ex = ExitB(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        # lower exit
        pos = (16, 0)
        ex = ExitC(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        pos = (17, 0)
        ex = ExitA(self.next_id(), self)
        self.grid.place_agent(agent=ex, pos=pos)
        # self.destinations[Destination.EXIT].append(pos)
        self.add_exit_to_correct_keys(ex, pos)

        """Place inner walls"""

        # horizontal walls
        for i in range(self.grid.width):
            if i < 9:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(i, 10))
            if i > 7:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(i, 3))

        # vertical walls
        for i in range(self.grid.height):
            if i < 8:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(5, i))
            if i > 5:
                self.grid.place_agent(agent=Wall(self.next_id(), self), pos=(11, i))

        # desks
        for i in range(self.grid.width):
            if 12 <= i <= 16:
                self.grid.place_agent(agent=Desk(self.next_id(), self), pos=(i, 13))
                self.grid.place_agent(agent=Desk(self.next_id(), self), pos=(i, 12))

            if 1 <= i <= 4:
                self.grid.place_agent(agent=Desk(self.next_id(), self), pos=(i, 1))
                self.grid.place_agent(agent=Desk(self.next_id(), self), pos=(i, 2))

        # desk interactive (aka chair)
        pos = (14, 11)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (4, 3)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (9, 1)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (18, 2)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (18, 4)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (1, 13)
        self.grid.place_agent(agent=DeskInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        # shelves interactive
        pos = (12, 11)
        self.grid.place_agent(agent=ShelfInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        pos = (7, 3)
        self.grid.place_agent(agent=ShelfInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        pos = (9, 4)
        self.grid.place_agent(agent=ShelfInteractive(self.next_id(), self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        # HelpDesk interactive
        pos = (8, 8)
        self.grid.place_agent(agent=HelpDeskInteractiveForHelpee(self.next_id(), self), pos=pos)
        self.destinations[Destination.HELPDESK].append(pos)

        pos = (3, 13)
        self.grid.place_agent(agent=HelpDeskInteractiveForHelpee(self.next_id(), self), pos=pos)
        self.destinations[Destination.HELPDESK].append(pos)

        # HelpDesk Helper interactive
        pos = (3, 13)
        self.grid.place_agent(agent=HelpDeskInteractiveForHelper(self.next_id(), self), pos=pos)

        # Place some staff members
        # One that is in the office
        pos = (10, 13)
        office1 = Staff(self.next_id(), self)
        self.grid.place_agent(agent=office1, pos=pos)
        self.schedule.add(office1)

        # One that is at the help desk
        pos = (3, 13)
        office2 = Staff(self.next_id(), self)
        self.grid.place_agent(agent=office2, pos=pos)
        self.schedule.add(office2)

        # One that is at the help desk
        pos = (8, 8)
        office3 = Staff(self.next_id(), self)
        self.grid.place_agent(agent=office3, pos=pos)
        self.schedule.add(office3)

    def get_all_spawnable_cells(self):
        """
        This function finds all cells that are valid spawning points for visitors.
        """
        spawnable_positions = []

        for i in range(self.grid.width):
            for j in range(self.grid.height):
                n_list = self.grid.get_cell_list_contents([(i, j)])

                if len(n_list) <= 0:
                    spawnable_positions.append((i, j))
                elif len(n_list) > 0:
                    n = n_list[0]
                    if not any(map(lambda t: isinstance(n, t), self.not_spawnable_objects)):
                        spawnable_positions.append((i, j))

        return spawnable_positions

    def spawn_visitors(self, n):
        """
        This function spawns n visitors randomly on the grid avoiding cells with objects that off limit for visitors.
        :param n: int: number of visitors to spawn
        """
        spawnable_positions = self.get_all_spawnable_cells()
        for _ in range(n):

            visitor = Visitor(self.next_id(), self, female_ratio=self.female_ratio, adult_ratio=self.adult_ratio,
                              familiarity=self.familiarity)

            pos = random.choice(spawnable_positions)

            self.grid.place_agent(agent=visitor, pos=pos)
            self.schedule.add(visitor)

    def spawn_staff(self):
        """
        Place staff at all office and help desk interactive helper points.
        :return:
        """

        for i in range(self.grid.width):
            for j in range(self.grid.height):
                n_list = self.grid.get_cell_list_contents([(i, j)])

                if len(n_list) > 0:

                    for n in n_list:
                        if isinstance(n, Office) or isinstance(n, HelpDeskInteractiveForHelper):
                            staff = Staff(self.next_id(), self, female_ratio=self.female_ratio, adult_ratio=self.adult_ratio)
                            self.grid.place_agent(agent=staff, pos=(i, j))
                            self.schedule.add(staff)
                            staff.emergency_knowledge.compute_closest_exit()
                            self.n_staff += 1
