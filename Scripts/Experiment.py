from Scripts.Visualization import *


def run_simulation(visualize=False, run_length=1000):
    """
    Runs the simulation, either with a visualization or without.
    :param visualize: Boolean
    :param run_length: int
    """

    if visualize:
        show_visualization(ToyModel)

    else:
        model = ToyModel()
        for i in range(run_length):
            model.step()
        print('done')
