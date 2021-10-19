from Scripts.Visualization import *
from Scripts.ToyModel import *
from Scripts.MappingModel import *
from Enums import *
import seaborn as sns
import pandas as pd


class Experiment:

    def __init__(self):

        print('Setting up the experiment ...\n')

        # Evacuation times per exit type (including all single evacuation times for each replication)
        self.evacuation_times = {ExitType.A: [], ExitType.B: [], ExitType.C: [], ExitType.AB: [],
                                 ExitType.BC: [], ExitType.AC: [], ExitType.ABC: []}

        # Average evacuation time per exit
        self.average_evacuation_times = {ExitType.A: 0, ExitType.B: 0, ExitType.C: 0, ExitType.AB: 0,
                                         ExitType.BC: 0, ExitType.AC: 0, ExitType.ABC: 0}

    def run(self, n_replications=10, visualize=False, max_run_length=1000, n_visitors=10, female_ratio=0.5, adult_ratio=0.5,
            familiarity=0.1, model=ToyModel):
        """
        This function runs the entire experiment with all its variations.
        """
        self.display_inputs(n_replications, max_run_length, n_visitors, female_ratio, adult_ratio, familiarity)
        self.model = model

        for ex in ExitType:
            print(f"\nRunning replications for exit type: {ex}")
            self.evacuation_times[ex] = self.run_n_replications(n_replications=n_replications, visualize=visualize,
                                                                max_run_length=max_run_length, n_visitors=n_visitors,
                                                                female_ratio=female_ratio, adult_ratio=adult_ratio,
                                                                familiarity=familiarity, valid_exits=ex)

            self.average_evacuation_times[ex] = sum(self.evacuation_times[ex]) / len(self.evacuation_times[ex])

    def run_n_replications(self, n_replications=10, visualize=False, max_run_length=1000, n_visitors=10, female_ratio=0.5,
                           adult_ratio=0.5, familiarity=0.1, valid_exits=ExitType.ABC):

        """
        This function runs n_replications of the model for a specific exit type.
        :param n_replications: int
        :param visualize: Boolean
        :param max_run_length: int
        :param n_visitors: int
        :param female_ratio: float
        :param adult_ratio: float
        :param familiarity: float
        :param valid_exits: ExitType
        :return: total_evacuation_times_per_replication: list
        """
        total_evacuation_times_per_replication = []
        print(f'\tRunning {n_replications} replications:')
        for i in range(n_replications):

            evac_time = self.run_one_replication(visualize=visualize, max_run_length=max_run_length, n_visitors=n_visitors,
                                                 female_ratio=female_ratio, adult_ratio=adult_ratio, familiarity=familiarity,
                                                 valid_exits=valid_exits, model=self.model)

            total_evacuation_times_per_replication.append(evac_time)
            print(f'\t\treplication #{i+1}/{n_replications}')

        return total_evacuation_times_per_replication

    @staticmethod
    def run_one_replication(visualize=False, max_run_length=1000, n_visitors=10, female_ratio=0.5, adult_ratio=0.5,
                            familiarity=0.1, valid_exits=ExitType.ABC, model=ToyModel):
        """
        Runs one simulation, either with a visualization or without. It returns the evacuation time for this run.
        :param visualize: Boolean
        :param max_run_length: int
        :param n_visitors: int
        :param female_ratio: float [0,1]
        :param adult_ratio: float [0,1]
        :param familiarity: float [0,1]
        :param valid_exits: ExitType
        :param model: func, either ToyModel or MapModel
        :return evac_time: int
        """

        if visualize:
            # show_visualization(MapModel)
            show_visualization(model)

        else:

            # Init model
            # model = MapModel(n_visitors=n_visitors,  female_ratio=female_ratio, adult_ratio=adult_ratio,
            #                  familiarity=familiarity, valid_exits=valid_exits)
            model = model(n_visitors=n_visitors, female_ratio=female_ratio, adult_ratio=adult_ratio,
                             familiarity=familiarity, valid_exits=valid_exits)

            # Run model
            for i in range(max_run_length):
                model.step()

                if model.is_done():
                    break

            # Save data
            evac_time = model.get_total_evacuation_time()
            return evac_time

    def show_evacuation_time_averages(self):
        """
        Show the mean evacuation time per exit type.
        """

        print("Average evacuation times per exit type:\n")
        for k, v in self.average_evacuation_times.items():
            print(f'{k}: {v}')

    def show_boxplot_evacuation_times(self, outliers=False):
        """
        Show boxplots of average evacuation times for all exit types.
        :param outliers: Boolean
        """

        sns.set_theme(style="whitegrid")
        frame = pd.DataFrame.from_dict(self.evacuation_times)
        frame.columns = [str(x)[9:] for x in frame.columns]
        sns.set(rc={'figure.figsize': (11.7, 8.27)})
        ax = sns.boxplot(data=frame, showfliers=outliers)
        outlier = 'w/' if outliers else 'w/o'
        ax.set_title(f'Boxplots for average evacuation times {outlier} outliers', fontsize=40, y=1.15)
        ax.set_ylabel('Time in seconds', fontsize=25)
        ax.set_xlabel('Exit Type', fontsize=25)
        ax.yaxis.labelpad = 25
        ax.xaxis.labelpad = 25
        ax.tick_params(labelsize=20)

    @staticmethod
    def display_inputs(n_replications, max_run_length, n_visitors, female_ratio, adult_ratio, familiarity):
        """
        Show all inputs for this experiment.
        :param n_replications: int
        :param max_run_length: int
        :param n_visitors: int
        :param female_ratio: float
        :param adult_ratio: float
        :param familiarity: float
        """

        print("Running the experiment with inputs:")
        print(f'\t- n_replications: \t{n_replications}')
        print(f'\t- max_run_length: \t{max_run_length}')
        print(f'\t- n_visitors: \t\t{n_visitors}')
        print(f'\t- female_ratio: \t{female_ratio}')
        print(f'\t- adult_ratio: \t\t{adult_ratio}')
        print(f'\t- familiarity: \t\t{familiarity}')

    def show_all_times(self):
        """
        Show all raw data.
        """
        print("\nShow all data on the evacuation times:\n")
        ts = self.evacuation_times
        for k, v in ts.items():
            print(k, v)
