from mesa import Model
from mesa.time import RandomActivation
from AnimateAgents import *
from InanimateAgents import *
from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def a_star(grid):
    """
    This functions takes in the model and calculates the ideal path from each cell to the closest and the main exit.
    This will return a dictionary with these paths.
    This will be calculated at the initiation of the model.
    """
    print(f'Grid: {grid}')
    pass


def create_toy_space():
    """
    This function creates a multi-grid space and fills it with some inanimate agents.
    """
    model = ToyModel(width=20, height=15)
    # show_visualization()

    return model



def show_visualization():
    """
    Creates an animation.
    """

    def agent_portrayal(agent):
        """
        This function determines how agents should look like (color, shape, etc.)
        """

        portrayal = {"Filled": "true",
                     "Layer": 0}

        if isinstance(agent, Wall):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "gray"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, Exit):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "red"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, Visitor):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "blue"
            portrayal["r"] = 0.5

        return portrayal


    # Parameters
    width = 20
    height = 15
    size = 20

    canvas = CanvasGrid(agent_portrayal, width, height, size * width, size * height)

    server = ModularServer(ToyModel,
                           [canvas],
                           "Toy Model",
                           {"width": width, "height": height})
    server.port = 8521  # The default
    server.launch()
    server.model


class ToyModel(Model):
    """
    This is just a toy model to set up the grid and visualize it.
    """

    def __init__(self, width, height):

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


if __name__ == "__main__":
    create_toy_space()
