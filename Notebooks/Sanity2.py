import os
from Scripts.Experiment import *
from Scripts.MappingModel import *
import sys
import nest_asyncio
nest_asyncio.apply()


os.chdir('..')
sys.path.append('./Scripts')

exp = Experiment()

exp.run(model=EvacuationModel, map_img_path='Images/Library_NewPlan2.png', visualize=False, n_replications=1, valid_exits=[ExitType.ABC, ExitType.AB])
# exp.run(model=MapModel, map_img_path='Images/Library_ToyPlan2_map.png', visualize=True, n_replications=1)
# exp.run(model=ToyModel, visualize=False, n_replications=1)

# Save the data
# the modifier just states who is saving what.
#       E.g.    modifier=1 --> exit types A, B, C
#               modifier=2 --> exit types AB, BC
#               modifier=2 --> exit types AC, ABC
#               (modifier=0 is just for testing purposes)
exp.save_data_to_pickle(modifier=0)

# Load the data
evac_times, average_evac_times = exp.load_pickled_data(modifier=0)
evac_times1, average_evac_times1 = exp.load_pickled_data(modifier=1)
evac_times2, average_evac_times2 = exp.load_pickled_data(modifier=2)
evac_times3, average_evac_times3 = exp.load_pickled_data(modifier=3)

# Combine corresponding dictionaries
exp.combine_results(evac_times1, evac_times2, evac_times3, average_evac_times1, average_evac_times2, average_evac_times3)

# Do all kind of data visualization.
exp.show_execution_times()
