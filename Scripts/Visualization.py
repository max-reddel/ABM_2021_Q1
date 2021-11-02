from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
# from Scripts.ToyModel import *    # TODO S: temporary switch off
from Scripts.AnimateAgents import *
from Scripts.InanimateAgents import *
from Scripts.EvacuationModel import get_border_dims

def show_visualization(model, img_map_path, n_visitors, female_ratio, adult_ratio,
                       familiarity, n_officestaff, valid_exits):
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
            portrayal["Color"] = "Black"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'desk'

        # if isinstance(agent, DeskInteractive):
        #     portrayal["Shape"] = "rect"
        #     portrayal["Color"] = "orange"
        #     portrayal["h"] = 1
        #     portrayal["w"] = 1
        #     portrayal["Name"] = 'chair'

        if isinstance(agent, Shelf):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "green"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'shelf'

        if isinstance(agent, HelpDesk):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "purple"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'Helpdesk'

        if isinstance(agent, ExitA) or isinstance(agent, ExitB) or isinstance(agent, ExitC):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "red"
            portrayal["h"] = 1
            portrayal["w"] = 1
            portrayal["Name"] = 'exit'

        if isinstance(agent, Visitor):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "red"
            portrayal["r"] = 15
            portrayal["Layer"] = 2
            portrayal["Name"] = 'visitor'

        if isinstance(agent, Staff):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "green"
            portrayal["r"] = 15
            portrayal["Layer"] = 2
            portrayal["Name"] = 'staff'

        if isinstance(agent, Alarm):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "yellow"
            portrayal["r"] = 50
            portrayal["Layer"]: 0
            portrayal["Name"] = 'alarm'
            if agent.is_activated and agent.model.schedule.time % 2 == 0:
                portrayal["Color"] = "red"
                portrayal["r"] = 50

        # TODO: More checks for agents would be necessary here

        return portrayal

    chart = ChartModule([{"Label": "safe_agents", "Color": "blue"}], data_collector_name="datacollector")

    # Parameters

    if img_map_path is not None:
        height, width = get_border_dims(img_map_path)
        px_rep = 3
        canvas = CanvasGrid(agent_portrayal, width, height, int(round(width*px_rep,0)), int(round(height*px_rep,0)))
        server = ModularServer(model,
                               [canvas, chart],
                               "Evacuation Model",
                               {"img_path": img_map_path,"familiarity":familiarity, "n_officestaff":n_officestaff,
                                "n_visitors":n_visitors, "valid_exits":valid_exits, "female_ratio": female_ratio,
                                "adult_ratio":adult_ratio})
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
