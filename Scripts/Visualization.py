from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *
from Scripts.ToyModel import *


def show_visualization(model):
    """
    Creates an animation, given a model type (e.g. EvacuationModel)
    """

    def agent_portrayal(agent):
        """
        This function determines how agents should look like (color, shape, etc.)
        """

        portrayal = {"Filled": "true",
                     "Layer": 0}

        if isinstance(agent, Wall) or isinstance(agent, Obstacle):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "gray"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, ExitA) or isinstance(agent, ExitB) or isinstance(agent, ExitC):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "red"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, Visitor):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "blue"
            portrayal["r"] = 0.5
            portrayal["Layer"]: 1

        if isinstance(agent, Staff):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "green"
            portrayal["r"] = 0.5
            portrayal["Layer"]: 1

        # TODO: More checks for agents would be necessary here

        return portrayal

    # Parameters
    width = 20
    height = 15
    size = 20

    canvas = CanvasGrid(agent_portrayal, width, height, size * width, size * height)

    server = ModularServer(model,
                           [canvas],
                           "Evacuation Model",
                           {"width": width, "height": height})

    server.port = 8521  # The default
    server.launch()
