from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width=20, height=15):

        super().__init__()
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.schedule = RandomActivation(self)

        self.fill_grid()

        # Create and add agents to the grid and schedule

    def step(self):
        # print(f'Doing model step #{self.schedule.time+1}!')
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
        self.grid.place_agent(agent=Exit(0, self), pos=(0, 4))
        self.grid.place_agent(agent=Exit(0, self), pos=(0, 5))

        # right exit
        self.grid.place_agent(agent=Exit(0, self), pos=(self.grid.width - 1, 12))
        self.grid.place_agent(agent=Exit(0, self), pos=(self.grid.width - 1, 13))

        # lower exit
        self.grid.place_agent(agent=Exit(0, self), pos=(16, 0))
        self.grid.place_agent(agent=Exit(0, self), pos=(17, 0))

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

        """Place a visitor"""
        visitor = Visitor(0, self, gender=Gender.MALE)

        # start = (1, 12)  # upper left corner
        # end = (16, 0)  # 4 cells further to the right
        # path = a_star_search(self.grid, start, end)
        path = [(1, 12), (1, 11), (2, 11), (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (9, 10), (9, 9), (8, 9), (7, 9), (7, 8), (7, 7), (7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (16, 0)]
        visitor.path_to_current_dest = path

        self.grid.place_agent(agent=visitor, pos=(1, self.grid.height-2))
        self.schedule.add(visitor)
