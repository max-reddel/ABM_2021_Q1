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

        # More agents would be necessary to check for here

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
