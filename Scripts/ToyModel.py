from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from AnimateAgents import *
from InanimateAgents import *


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width, height):

        super().__init__()
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.schedule = RandomActivation(self)

        self.fill_grid()

    def step(self):
        print(f'Doing model step #{self.schedule.time}!')
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

        # horizonal walls
        for i in range(self.grid.width):
            if i < 8:
                self.grid.place_agent(agent=Wall(0, self), pos=(i, 10))

            if i > 8:
                self.grid.place_agent(agent=Wall(0, self), pos=(i, 3))

        # vertical walls
        for i in range(self.grid.height):
            if i < 8:
                self.grid.place_agent(agent=Wall(0, self), pos=(5, i))
            if i > 5:
                self.grid.place_agent(agent=Wall(0, self), pos=(11, i))

        """Place a visitor"""
        self.grid.place_agent(agent=Visitor(0, self, gender='female'), pos=(1, self.grid.height-2))
