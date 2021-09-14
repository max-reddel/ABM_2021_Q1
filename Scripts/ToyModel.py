from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width=20, height=15, n_visitors=10):

        super().__init__()
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.schedule = RandomActivation(self)
        self.destinations = {Destination.DESK: [],
                             Destination.SHELF: [],
                             Destination.EXIT: [],
                             Destination.HELPDESK: []}

        # Create and add agents to the grid and schedule
        self.fill_grid()
        self.not_spawnable_objects = [Wall, Obstacle, Desk, OutOfBounds, Exit, HelpDesk, Shelf, DeskInteractive,
                                      HelpDeskInteractiveForHelpee, HelpDeskInteractiveForHelper, ShelfInteractive]
        self.spawn_visitors(n=n_visitors)

    def step(self):

        self.schedule.step()

    def fill_grid(self):

        """Place outer walls"""

        for i in range(self.grid.width):
            # lowest row
            if i != 16 and i != 17:  # space for exit
                self.grid.place_agent(agent=Wall(0, self), pos=(i, 0))
            # highest row
            self.grid.place_agent(agent=Wall(0, self), pos=(i, self.grid.height - 1))

        for i in range(self.grid.height):
            # left col
            if i != 4 and i != 5:
                self.grid.place_agent(agent=Wall(0, self), pos=(0, i))
            # right col
            if i != 12 and i != 13:
                self.grid.place_agent(agent=Wall(0, self), pos=(self.grid.width - 1, i))

        """Place exits"""

        # left exit
        pos = (0, 4)
        self.grid.place_agent(agent=ExitA(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)
        pos = (0, 5)
        self.grid.place_agent(agent=ExitA(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)

        # right exit
        pos = (self.grid.width - 1, 12)
        self.grid.place_agent(agent=ExitB(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)

        pos = (self.grid.width - 1, 13)
        self.grid.place_agent(agent=ExitB(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)

        # lower exit
        pos = (16, 0)
        self.grid.place_agent(agent=ExitC(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)

        pos = (17, 0)
        self.grid.place_agent(agent=ExitC(0, self), pos=pos)
        self.destinations[Destination.EXIT].append(pos)

        """Place inner walls"""

        # horizontal walls
        for i in range(self.grid.width):
            if i < 9:
                self.grid.place_agent(agent=Wall(0, self), pos=(i, 10))
            if i > 7:
                self.grid.place_agent(agent=Wall(0, self), pos=(i, 3))

        # vertical walls
        for i in range(self.grid.height):
            if i < 8:
                self.grid.place_agent(agent=Wall(0, self), pos=(5, i))
            if i > 5:
                self.grid.place_agent(agent=Wall(0, self), pos=(11, i))

        # desks
        for i in range(self.grid.width):
            if 12 <= i <= 16:
                self.grid.place_agent(agent=Desk(0, self), pos=(i, 13))
                self.grid.place_agent(agent=Desk(0, self), pos=(i, 12))

            if 1 <= i <= 4:
                self.grid.place_agent(agent=Desk(0, self), pos=(i, 1))
                self.grid.place_agent(agent=Desk(0, self), pos=(i, 2))

        # desk interactive (aka chair)
        pos = (14, 11)
        self.grid.place_agent(agent=DeskInteractive(0, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (4, 3)
        self.grid.place_agent(agent=DeskInteractive(1, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (9, 1)
        self.grid.place_agent(agent=DeskInteractive(2, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (18, 2)
        self.grid.place_agent(agent=DeskInteractive(3, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (18, 4)
        self.grid.place_agent(agent=DeskInteractive(4, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        pos = (1, 13)
        self.grid.place_agent(agent=DeskInteractive(4, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        # shelves interactive
        pos = (12, 11)
        self.grid.place_agent(agent=ShelfInteractive(0, self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        pos = (8, 3)
        self.grid.place_agent(agent=ShelfInteractive(1, self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        pos = (9, 4)
        self.grid.place_agent(agent=ShelfInteractive(2, self), pos=pos)
        self.destinations[Destination.SHELF].append(pos)

        # HelpDesk interactive
        pos = (8, 8)
        self.grid.place_agent(agent=HelpDeskInteractiveForHelpee(0, self), pos=pos)
        self.destinations[Destination.HELPDESK].append(pos)

        pos = (3, 13)
        self.grid.place_agent(agent=HelpDeskInteractiveForHelpee(0, self), pos=pos)
        self.destinations[Destination.HELPDESK].append(pos)

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
        for i in range(n):
            visitor = Visitor(i, self)

            pos = random.choice(spawnable_positions)

            self.grid.place_agent(agent=visitor, pos=pos)
            self.schedule.add(visitor)
