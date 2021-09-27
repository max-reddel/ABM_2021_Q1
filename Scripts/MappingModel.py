from PIL import Image
import numpy as np
import pandas as pd
from ast import literal_eval
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

import Scripts.InanimateAgents as IA
from Scripts.AnimateAgents import *
from Enums import *

def nprgb_to_hex(row):
    """
    Returns colour in hex from RGB numpy row
    :param row:
    :return:
    """
    return str('%02x%02x%02x' % (row[0] ,row[1], row[2]))

class MapModel(Model):
    """
    Instantiates Mesa grid and schedule objects.
    Converts pixels on given map image into Mesa grid entities.
    Populates Mesa grid with visitors and office staff as well.
    (Requires external txt file detailing the colours to agents)
    """

    def __init__(self, img_path='../Images/Library_NewPlan2_map.png',
                 color_path='../Images/object_colours.tsv', n_vistors=50):
        super().__init__()
        self.id_counter = 0
        self.destinations = {Destination.DESK:[],
                             Destination.SHELF:[],
                             Destination.EXIT:[],
                             Destination.HELPDESK: []}
        # self.alarm = IA.Alarm(self.next_id(), self)
        # self.grid.place_agent(self.alarm)

        im = Image.open(img_path)
        im_np = np.array(im)
        self.gridsize = im_np.shape[:-1]     # pixel size of map (incl. out of bounds area)
        self.grid = MultiGrid(width=self.gridsize[1], height=self.gridsize[0], torus=False)
        self.schedule = RandomActivation(self)

        try:
            if np.all(im_np[:, :, 3].flatten(order='C') == 255):  # checks if transparencies present in image
                im_np = np.delete(im_np, 3, 2)
        except:
            print('MapModel: (minor issue) Transparency check failed, proceeding.')

        # convert 2d rgb coords to 1d (even though ndarray is 3d, incl. RGB dimension)
        self.rgbcoords_1d = im_np.reshape((im_np.shape[0] * im_np.shape[1], im_np.shape[2]))
        # retrieve colour palettes in map
        self.c_unique, c_occurrence = np.unique(self.rgbcoords_1d, return_counts=True, axis=0)

        self.colour_to_grid_object = pd.read_csv(color_path, sep='\t', header=0,
                                                 index_col=2,
                                                 comment='#')
        # for obj in self.colour_to_grid_object.index:
        self.colours = np.array([np.array(literal_eval(self.colour_to_grid_object.loc[colour,'RGB'])) for colour in self.colour_to_grid_object.index])
        index_map = list(zip(self.colour_to_grid_object.index, self.colours))
        self.indices = index_map

        # check for membership between image and defined colour set, sanity check
        # below: finds the indices where RGB in one array is found in another, returns 2 arrays of indices
        membership_check = np.where((self.colours==self.c_unique[:,None]).all(-1))
        # print((sorted(membership_check[1]) == list(range(len(self.colour_to_grid_object.index)))))
        if len(membership_check[1]) != len(self.colour_to_grid_object.index):
            excluded = list(set(list(range(len(self.colour_to_grid_object.index)))) - set(membership_check[1]))
            raise ValueError(f"Membership check failed: defined colour set item index/indices {excluded} not in image")


        # detect outlier colours from set exclusion
        # below: finds non-matching colours based on defined set
        self.outliers = np.where((self.c_unique[:,None] != self.colours).any(-1).all(1))[0]

        self.correction_map = []    # for diagnostic
        # find difference vector of outlier colours to main colour.  Minimal difference = closest colour
        # easy alg: subtract outlier colour from defined set array, sum RGB values, find minimum, match index
        for idx in self.outliers:
            c = self.c_unique[idx,:]
            c_delta = np.abs(np.sum(np.array(self.colours) - c, axis=1))
            parent = self.colours[np.argmin(c_delta, axis=0)]
            self.correction_map.append((c, parent, np.min(c_delta)))

            # find indices of all pixels with matching colour
            outlier_pixels = self.find_colour_coords(c)

            # replace outlier colour to main colour
            for idx in outlier_pixels:
                self.rgbcoords_1d[idx, :] = parent

        if len(np.unique(self.rgbcoords_1d, axis=0)) != len(self.colours):
            raise ValueError('RGB correction issue, colours in corrected array not the same as defined set.')

        # ToyModel-like grid entity populating and visitor spawning
        self.fill_grid(index_map)
        self.not_spawnable_objects = [IA.Wall, IA.Obstacle,
                                      IA.Desk, IA.OutOfBounds,
                                      IA.ExitA, IA.ExitB, IA.ExitC,
                                      IA.HelpDesk,
                                      IA.Shelf, IA.DeskInteractive,
                                      IA.HelpDeskInteractiveForHelpee,
                                      IA.HelpDeskInteractiveForHelper,
                                      IA.ShelfInteractive]
        self.spawn_visitors(n=n_vistors)

    def next_id(self):
        """
        Returns current id and increments the id_counter such that each agent has a unique identifier
        :return:
        """
        self.id_counter += 1
        return self.id_counter - 1

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

    def fill_grid(self,index_map):
        """
        Iterates through colour list, finds pixels matching said colour,
        Saves spawnable tiles and destination tiles in respective data types
        Loads library objects (walls, desks) and office staff (in specific seats)
        :param index_map: list of tuples with Dataframe indices and associated colours
        """
        # stores spawnable points in list
        self.spawnable_positions = []

        # Office entities
        staff_types = ('Office','HelpDeskInteractiveForHelper')

        # iterate through object_colours.tsv's entity names & colours
        for obj, c in index_map:
            idxs = self.find_colour_coords(c)[0]
            x = idxs // self.gridsize[0]
            y = idxs % self.gridsize[0]
            coords = zip(x,y)
            # save spawnable items into list
            if bool(self.colour_to_grid_object.loc[obj,'Spawnable']):
                self.spawnable_positions.extend(coords)

            # save destinations to dict as defined in init, used for pathfinding
            try:
                entity_type = self.colour_to_grid_object.loc[obj,'Entity_category']
                user_destination = None
                if 'exit' in entity_type.lower():
                    # TODO: 3 EXITs are currently merged into one type
                    user_destination = Destination.EXIT
                elif 'DeskInteractive' in entity_type:
                    user_destination = Destination.DESK
                elif 'ShelfInteractive' in entity_type:
                    user_destination = Destination.SHELF
                elif 'HelpDeskInteractiveForHelpee' in entity_type:
                    user_destination = Destination.HELPDESK

                if user_destination is not None:
                    self.destinations[user_destination].extend(zip(x, y))

            except AttributeError:  # catches NaNs being floats
                continue

            # iterates through coords of the same colour
            for pos in coords:
                try:
                    # below: use Entity_category string from object_colours.tsv to match
                    # with the classes from inanimate agents (hence alias IA)
                    # parentheses after: initiate the matched inanimate class with its associated args
                    if self.colour_to_grid_object.loc[obj,'Entity_category'] not in staff_types:
                        agent_class = getattr(IA, self.colour_to_grid_object.loc[obj, 'Entity_category'])(self.next_id(), self)
                    else:   # staff is in animate class
                        agent_class = Staff(self.next_id(),self)
                    self.grid.place_agent(agent=agent_class, pos=pos)
                    self.schedule.add(agent_class)

                except TypeError:
                    # Catches TypeError for walkable tiles (since only unwalkables are placed)
                    continue
        print("MappingModel.py: all grid objects transferred to MESA grid entities.")

    def spawn_visitors(self,n=50):
        """
        Spawns n visitors randomly on the grid, avoiding cells that are off limits for visitors
        :param n: number of visitors to spawn
        :return:
        """
        for i in range(n):
            visitor = Visitor(self.next_id(),self)

            pos = random.choice(self.spawnable_positions)

            self.grid.place_agent(agent=visitor, pos=pos)
            self.schedule.add(visitor)



# test = MapModel()
# if __name__ ==  "__main__ ":
#     test_item = MapModel()