from Scripts.Visualization import *


class Experiment:

    def __init__(self):

        self.data_dict = {}

        self.data_dict['Only Closest Exit'] = []

        self.data_dict['Only ExitA'] = []
        self.data_dict['Only ExitB'] = []
        self.data_dict['Only ExitC'] = []

        self.data_dict['ExitA or ExitB'] = []
        self.data_dict['ExitB or ExitC'] = []
        self.data_dict['ExitA or ExitC'] = []

        self.data_dict['Any Exit'] = []

    def run(self):
        """
        This function runs the entire experiment with all its variations.
        """

    def run_one_simulation(self, visualize=False, run_length=1000, n_visitors=10, valid_exits=('Any Exit')):
        """
        Runs one simulation, either with a visualization or without.
        :param visualize: Boolean
        :param run_length: int
        :param n_visitors: int
        :param valid_exits: tuple of strings containing one or more keys of the data_dict
        """

        if visualize:
            show_visualization(ToyModel)

        else:
            model = ToyModel(n_visitors=n_visitors, valid_exits=valid_exits)
            for i in range(run_length):
                model.step()
            print(f'total evacuation time: {model.get_total_evacuation_time()}')

            nr_safe_agents = model.datacollector.get_model_vars_dataframe()
            nr_safe_agents.plot()

            print('done')
