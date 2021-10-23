import os
from Scripts.Experiment import *
from Scripts.MappingModel import *
import sys
import nest_asyncio
nest_asyncio.apply()


os.chdir('..')
sys.path.append('./Scripts')

exp = Experiment()

# exp.run(model=MapModel, map_img_path='Images/Library_ToyPlan2_v1.png', visualize=True, n_replications=1)
# exp.run(model=MapModel, map_img_path='Images/Library_ToyPlan2_map.png', visualize=True, n_replications=1)
exp.run(model=ToyModel, visualize=False, n_replications=1)
