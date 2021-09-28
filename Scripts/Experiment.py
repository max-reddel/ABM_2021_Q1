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
        print(f'total evacuation time: {model.get_total_evacuation_time()}')

        nr_safe_agents = model.datacollector.get_model_vars_dataframe()
        nr_safe_agents.plot()

        print('done')
