from Scripts.Visualization import *
from Scripts.EvacuationModel import *
from Scripts.Enums import *
import seaborn as sns
import pandas as pd
import time
import pickle


class Experiment:

    def __init__(self):

        print('Setting up the experiment ...\n')
        self.start_time = time.time()
        self.execution_times = []
        self.cum_time = [self.start_time]

        # Evacuation times per exit type (including all single evacuation times for each replication)
        self.evacuation_times = {ExitType.A: [], ExitType.B: [], ExitType.C: [], ExitType.AB: [],
                                 ExitType.BC: [], ExitType.AC: [], ExitType.ABC: []}

        # Average evacuation time per exit
        self.average_evacuation_times = {ExitType.A: 0, ExitType.B: 0, ExitType.C: 0, ExitType.AB: 0,
                                         ExitType.BC: 0, ExitType.AC: 0, ExitType.ABC: 0}

    def run(self, model, n_replications=10, visualize=False, max_run_length=1000, n_visitors=50, n_officestaff=10, female_ratio=0.5,
            adult_ratio=0.5, familiarity=0.1, map_img_path=None, valid_exits=None):
        """
        This function runs the entire experiment with all its variations.
        """
        self.display_inputs(n_replications, max_run_length, n_visitors, female_ratio, adult_ratio, familiarity)
        self.model = model
        self.map_path = map_img_path
        print(f"\nSet Map object currently {self.map_path}.")

        if valid_exits is None:
            valid_exits = [x for x in ExitType]

        for ex in valid_exits:
            message = f"\nRunning replications for exit type: {ex}" if not visualize else "\nRunning visualization."
            print(f"{message}")
            self.evacuation_times[ex] = self.run_n_replications(n_replications=n_replications, visualize=visualize,
                                                                max_run_length=max_run_length, n_visitors=n_visitors,
                                                                n_officestaff=n_officestaff,
                                                                female_ratio=female_ratio, adult_ratio=adult_ratio,
                                                                familiarity=familiarity, valid_exits=ex)

            self.average_evacuation_times[ex] = sum(self.evacuation_times[ex]) / len(self.evacuation_times[ex])

            if visualize:
                break

        run_time = round(time.time() - self.start_time, 2)
        print(f'Run time: {run_time} seconds')

    def run_n_replications(self, n_replications=10, visualize=False, max_run_length=1000, n_visitors=10,
                           n_officestaff=10,female_ratio=0.5,
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
        message = f'\tRunning {n_replications} replications:' if not visualize else ""
        print(message)
        for i in range(n_replications):

            evac_time = self.run_one_replication(visualize=visualize, max_run_length=max_run_length, n_visitors=n_visitors,
                                                 n_officestaff=n_officestaff,
                                                 female_ratio=female_ratio, adult_ratio=adult_ratio, familiarity=familiarity,
                                                 valid_exits=valid_exits, model=self.model, map_img_path=self.map_path)

            if visualize:
                break
            total_evacuation_times_per_replication.append(evac_time)
            print(f'\t\treplication #{i+1}/{n_replications}')

        return total_evacuation_times_per_replication

    def run_one_replication(self, visualize=False, max_run_length=1000, n_officestaff=10, n_visitors=10, female_ratio=0.5, adult_ratio=0.5,
                            familiarity=0.1, valid_exits=ExitType.ABC, model=EvacuationModel, map_img_path=None):
        """
        Runs one simulation, either with a visualization or without. It returns the evacuation time for this run.
        :param map_img_path:
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
            show_visualization(model, map_img_path)

        else:

            # Init model
            # model = MapModel(n_visitors=n_visitors,  female_ratio=female_ratio, adult_ratio=adult_ratio,
            #                  familiarity=familiarity, valid_exits=valid_exits)
            model = model(n_visitors=n_visitors, female_ratio=female_ratio, adult_ratio=adult_ratio,
                             familiarity=familiarity,n_officestaff=n_officestaff, valid_exits=valid_exits)

            # Run model
            for i in range(max_run_length):
                model.step()

                if model.is_done():
                    break

            # Save data
            evac_time = model.get_total_evacuation_time()

            # Save time
            run_time = round(time.time() - self.cum_time[-1], 2)
            self.execution_times.append(run_time)
            self.cum_time.append(time.time())
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

    def show_execution_times(self):

        print(f'Execution times per replication: {self.execution_times}')

    def save_data_to_pickle(self, folder='./OutputData/', modifier=0):
        """
        Saves the data of your current data in two pickles.
        :param folder:
        :param modifier:    modifier=1 --> exit types A, B, C
                            modifier=2 --> exit types AB, BC
                            modifier=3 --> exit types AC, ABC
        """

        evac_times = self.evacuation_times
        average_evac_times = self.average_evacuation_times

        with open(f'{folder}evac_times_{modifier}.pickle', 'wb') as handle:
            pickle.dump(evac_times, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(f'{folder}average_evac_times_{modifier}.pickle', 'wb') as handle:
            pickle.dump(average_evac_times, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_pickled_data(folder='./OutputData/', modifier='0'):
        """
        Loads the data of two pickles and returns them.
        :param folder:
        :param modifier:    modifier=1 --> exit types A, B, C
                            modifier=2 --> exit types AB, BC
                            modifier=3 --> exit types AC, ABC
        :return evac_times: dictionary
                average_evac_times: dictionary
        """

        with open(f'{folder}evac_times_{modifier}.pickle', 'rb') as handle:
            evac_times = pickle.load(handle)

        with open(f'{folder}average_evac_times_{modifier}.pickle', 'rb') as handle:
            average_evac_times = pickle.load(handle)

        return evac_times, average_evac_times

    def combine_results(self, to_include):
        """
        This function takes the individual dictionaries and overwrites the current experiment's data.
        Like this, the data visualization methods can be used again after distributed computation.
        :param to_include: list of all evac time run objects
        """

        def safe_overwrite(items_to_merge):
            target = {}
            for d in items_to_merge:
                intersect = list(set(d.keys())& set(target.keys()))
                for k,v in d.items():
                    if len(v)>0:
                        if k in intersect:
                            target[k] = target[k]+v
                        else:
                            target[k] = v
            return target

        self.evacuation_times = safe_overwrite(to_include)

        self.average_evacuation_times = {}
        for k,v in self.evacuation_times.items():
            self.average_evacuation_times[k] = sum(v) / len(v)
