from AnimateAgents import *
from InanimateAgents import *
from Scripts.ToyModel import *
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
    show_visualization()

    return model.grid



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


if __name__ == "__main__":
    create_toy_space()
