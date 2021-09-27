from Scripts.Visualization import *
from Scripts.MappingModel import *


def run_simulation(visualize=False, run_length=1000):
    """
    Runs the simulation, either with a visualization or without.
    :param visualize: Boolean
    :param run_length: int
    """

    if visualize:
        show_visualization(MapModel)

    else:
        # model = ToyModel()
        model = MapModel()
        for i in range(run_length):
            model.step()
        print('done')
