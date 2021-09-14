from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *
from Scripts.Tasks import *


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width=20, height=15):

        super().__init__()
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.schedule = RandomActivation(self)
        self.destinations = {Destination.DESK: [],
                             Destination.SHELF: [],
                             Destination.EXIT: [],
                             Destination.HELPDESK: []}

        # Create and add agents to the grid and schedule
        self.fill_grid()
        print(self.destinations[Destination.DESK])

    def step(self):

        # pos = self.schedule.agents[0].pos
        # print(f'old position: {pos}')

        self.schedule.step()

        # pos = self.schedule.agents[0].pos
        # print(f'new position: {pos}')

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
        self.grid.place_agent(agent=DeskInteractive(0, self), pos=pos)
        self.destinations[Destination.DESK].append(pos)

        """Place a visitor"""

        # Create first composite task

        # 1st visitor
        pos = (1, self.grid.height-2)
        visitor1 = Visitor(0, self, gender=Gender.MALE)
        self.grid.place_agent(agent=visitor1, pos=pos)
        self.schedule.add(visitor1)

        # 2nd visitor
        start = (18, 12)  # lower left corner
        visitor2 = Visitor(1, self, gender=Gender.FEMALE)
        end = (4, 3)  # chair
        path = a_star_search(self.grid, start, end)
        visitor2.path_to_current_dest = path
        self.grid.place_agent(agent=visitor2, pos=start)
        self.schedule.add(visitor2)
