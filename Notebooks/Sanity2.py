import os

os.chdir('..')
import sys

sys.path.append('./Scripts')
import nest_asyncio

nest_asyncio.apply()

from Scripts.Experiment import *
from Scripts.MappingModel import *

exp = Experiment()

exp.run(model=MapModel, map_img_path='Images/Library_ToyPlan2_v1.png', visualize=True, n_replications=1)
# exp.run(model=MapModel, visualize=True, n_replications=1)
