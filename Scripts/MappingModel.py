from PIL import Image
import numpy as np
import pandas as pd
from ast import literal_eval
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

import Scripts.InanimateAgents as ia

def nprgb_to_hex(row):
    """
    Returns colour in hex from RGB numpy row
    :param row:
    :return:
    """
    return str('%02x%02x%02x' % (row[0] ,row[1], row[2]))

class MapModel(Model):
    """
    Converts pixels on given map image into Mesa grid. Requires external txt file detailing  the colours to agents.
    """

    def __init__(self, img_path='../Images/coloured_plan.png',
                 color_path='../Images/object_colours.tsv'):
        super().__init__()
        im = Image.open(img_path)
        im_np = np.array(im)
        self.gridsize = im_np.shape[:-1]     # pixel size of map (incl. out of bounds area)
        self.grid = MultiGrid(width=self.gridsize[1], height=self.gridsize[0], torus=False)
        self.schedule = RandomActivation(self)

        try:
            if np.all(im_np[:, :, 3].flatten(order='C') == 255):  # checks if transparencies present in image
                im_np = np.delete(im_np, 3, 2)
        except:
            print('MappingModel.py: Transparency check failed, proceeding.')

        # convert 2d rgb coords to 1d (even though ndarray is 3d, incl. RGB dimension)
        self.rgbcoords_1d = im_np.reshape((im_np.shape[0] * im_np.shape[1], im_np.shape[2]))
        # retrieve colour palettes in map
        c_unique, c_occurrence = np.unique(self.rgbcoords_1d, return_counts=True, axis=0)
        # detect outlier colours from low occurrence numbers (<=10 occurrences) and search for nearest 'main' colour
        self.colours = []
        c_outliers = []
        for idx, occurrence in enumerate(c_occurrence):
            colour = c_unique[idx, :]
            if occurrence <= 10:
                c_outliers.append((occurrence, colour))
            else:
                self.colours.append(colour)

        # find difference vector of outlier colours to main colour.  Minimal difference = closest colour
        for n, c in c_outliers:
            parent = self.colours[np.argmin(np.sum(np.array(self.colours) - c, axis=1), axis=0)]

            # find indices where matching
            mask = self.find_colour_coords(c)

            # replace outlier colour to main colour
            for idx in mask:
                self.rgbcoords_1d[idx, :] = parent

        # read colour ids
        self.colour_to_object = pd.read_csv(color_path, sep='\t', header=0,
                                            index_col=2,
                                            comment='#')

        self.fill_grid()

    def step(self):
        self.schedule.step()

    def find_colour_coords(self, RGB_value):
        """
        With given RGB values, return an array of all found coordinates
        :return:
        """
        return np.where((self.rgbcoords_1d[:,0] == RGB_value[0]) &
                        (self.rgbcoords_1d[:,1] == RGB_value[1]) &
                        (self.rgbcoords_1d[:,2] == RGB_value[2]))

    def fill_grid(self):
        # identify pixels and populate
        for obj in self.colour_to_object.index:
            # convert RGBvalues from string to numpy array
            colour = np.array(literal_eval(self.colour_to_object.loc[obj,'RGB']))
            if colour not in np.array(self.colours):    # sanity check
                raise ValueError(f'{colour} not in colours array' )
            # place agents based on their object category (wall, door, etc)
            # then input them as inanimate agents with ids
            for idx, coord in enumerate(self.find_colour_coords(colour)[0]):
                agent_class = getattr(ia, self.colour_to_object.loc[obj, 'Entity_category'], lambda:None)(self.colour_to_object.loc[obj,'ID_category'] + idx, self)
                self.grid.place_agent(agent=agent_class, pos=(coord // self.gridsize[0], coord % self.gridsize[0]))


test = MapModel()
# if __name__ ==  "__main__ ":
#     test_item = MapModel()