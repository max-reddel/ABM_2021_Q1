from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
# from Scripts.ToyModel import *    # TODO S: temporary switch off
from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *
from Scripts.MappingModel import get_border_dims

def show_visualization(model, img_map_path):
    """
    Creates an animation, given a model type (e.g. EvacuationModel)
    """

    def agent_portrayal(agent):
        """
        This function determines how agents should look like (color, shape, etc.)
        """

        portrayal = {"Filled": "true",
                     "Layer": 1}

        if isinstance(agent, Wall) or isinstance(agent, Obstacle):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "gray"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'wall'

        if isinstance(agent, Desk):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "brown"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'desk'

        # if isinstance(agent, DeskInteractive):
        #     portrayal["Shape"] = "rect"
        #     portrayal["Color"] = "orange"
        #     portrayal["h"] = 1
        #     portrayal["w"] = 1
        #     portrayal["Name"] = 'chair'
        #
        # if isinstance(agent, ShelfInteractive):
        #     portrayal["Shape"] = "rect"
        #     portrayal["Color"] = "green"
        #     portrayal["h"] = 1
        #     portrayal["w"] = 1
        #     portrayal["Name"] = 'shelf'
        #
        # if isinstance(agent, HelpDeskInteractiveForHelpee):
        #     portrayal["Shape"] = "rect"
        #     portrayal["Color"] = "purple"
        #     portrayal["h"] = 1
        #     portrayal["w"] = 1
        #     portrayal["Name"] = 'help desk'

        if isinstance(agent, ExitA) or isinstance(agent, ExitB) or isinstance(agent, ExitC):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "red"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'exit'

        if isinstance(agent, Visitor):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "blue"
            portrayal["r"] = 0.8
            portrayal["Layer"] = 0
            portrayal["Name"] = 'visitor'

        if isinstance(agent, Staff):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "green"
            portrayal["r"] = 0.8
            portrayal["Layer"] = 0
            portrayal["Name"] = 'staff'

        if isinstance(agent, Alarm):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "blue"
            portrayal["r"] = 1.5
            portrayal["Layer"]: 0
            portrayal["Name"] = 'alarm'
            if agent.is_activated and agent.model.schedule.time % 2 == 0:
                portrayal["Color"] = "red"
                portrayal["r"] = 2

        # TODO: More checks for agents would be necessary here

        return portrayal

    chart = ChartModule([{"Label": "safe_agents", "Color": "blue"}], data_collector_name="datacollector")

    # Parameters

    if img_map_path is not None:
        height, width = get_border_dims(img_map_path)
        px_rep = 2
        canvas = CanvasGrid(agent_portrayal, width, height, width*px_rep, height*px_rep)
        server = ModularServer(model,
                               [canvas, chart],
                               "Evacuation Model",
                               {"img_path": img_map_path})
    else:
        width = 20
        height = 15
        size = 20
        canvas = CanvasGrid(agent_portrayal, width, height, size * width, size * height)
        server = ModularServer(model,
                               [canvas, chart],
                               "Evacuation Model",
                               {"width":width, "height":height})


    server.port = 8521  # The default
    server.launch()
