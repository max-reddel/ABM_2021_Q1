from PIL import Image
import numpy as np
import pandas as pd
import time, pickle, os
from ast import literal_eval
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import Scripts.InanimateAgents as IA
from Scripts.AnimateAgents import *
from Scripts.Enums import *
from Scripts.PathFinding import a_star_search

# current_img_path = 'Images/Library_ToyPlan2_v1.png'
current_img_path = 'Images/Library_NewPlan2_map.png'


def nprgb_to_hex(row):
    """
    Returns colour in hex from RGB numpy row
    :param row:
    :return:
    """
    return str('%02x%02x%02x' % (row[0], row[1], row[2]))


def get_border_dims(img_path=current_img_path):
    """
    Returns height and width values of an image. Used for creating a canvas before the model call. Hacky.
    :param img_path: image file path
    :return: tuple(height,width)
    """
    im = np.array(Image.open(img_path))
    return im.shape[:-1]


class MapModel(Model):
    """
    Instantiates Mesa grid and schedule objects.
    Converts pixels on given map image into Mesa grid entities.
    Populates Mesa grid with visitors and office staff as well.
    (Requires external txt file detailing the colours to agents)
    img_path='Images/Library_NewPlan2_map.png'
    img_path='Images/Library_ToyPlan2_v1.png'
    """

    def __init__(self, img_path=current_img_path,
                 color_path='Images/object_colours.tsv', n_visitors=50, n_officestaff=10, female_ratio=0.5,
                 adult_ratio=0.5, familiarity=0.1, valid_exits=ExitType.ABC):
        super().__init__()
        self.female_ratio = female_ratio
        self.adult_ratio = adult_ratio
        self.familiarity = familiarity
        self.valid_exits = valid_exits

        self.id_counter = 0
        self.n_staff = 0
        self.n_visitors = n_visitors
        self.n_officestaff = n_officestaff
        self.safe_agents = set()

        # stores spawnable points in list
        self.spawnable_positions = []
        self.office_positions = []
        self.helpdesk_positions = []
        self.staff_agents = []
        self.all_paths = {}     # dict of all paths from office spots to all exits.

        self.destinations = {Destination.DESK: [],
                             Destination.SHELF: [],
                             Destination.EXIT: [],
                             Destination.EXITA: [],
                             Destination.EXITB: [],
                             Destination.EXITC: [],
                             Destination.HELPDESK: []}

        im = Image.open(img_path)
        im_np = np.array(im)
        self.gridsize = im_np.shape[:-1]  # pixel size of map (incl. out of bounds area)
        self.grid = MultiGrid(width=self.gridsize[1], height=self.gridsize[0], torus=False)
        self.schedule = RandomActivation(self)

        self.alarm = IA.Alarm(self.next_id(), self)
        self.end_time = - self.alarm.starting_time
        self.grid.place_agent(self.alarm, (100, 100))
        try:
            if np.all(im_np[:, :, 3].flatten(order='C') == 255):  # checks if transparencies present in image
                im_np = np.delete(im_np, 3, 2)
        except:
            print('MapModel: (minor issue) Transparency check failed, proceeding.')

        # convert 2d rgb coords to 1d (even though ndarray is 3d, incl. RGB dimension)
        self.rgbcoords_1d = im_np.reshape((im_np.shape[0] * im_np.shape[1], im_np.shape[2]))
        # retrieve colour palettes in map
        self.c_unique, c_occurrence = np.unique(self.rgbcoords_1d, return_counts=True, axis=0)

        self.colour_to_grid_object = pd.read_csv(color_path, sep='\t',
                                                 index_col=2)
        self.colours = np.array([np.array(literal_eval(self.colour_to_grid_object.loc[colour, 'RGB'])) for colour in
                                 self.colour_to_grid_object.index])
        index_map = list(zip(self.colour_to_grid_object.index, self.colours))
        self.indices = index_map

        # check for membership between image and defined colour set, sanity check
        # below: finds the indices where RGB in one array is found in another, returns 2 arrays of indices
        membership_check = np.where((self.colours == self.c_unique[:, None]).all(-1))
        if len(membership_check[1]) != len(self.colour_to_grid_object.index):
            excluded = list(set(list(range(len(self.colour_to_grid_object.index)))) - set(membership_check[1]))
            excluded_name = [self.colour_to_grid_object.iloc[color,1] for color in excluded]
            raise ValueError(f"Membership check failed: defined colour set item index/indices {excluded_name} "
                             f"not in image")

        # detect outlier colours from set exclusion
        # below: finds non-matching colours based on defined set
        self.outliers = np.where((self.c_unique[:, None] != self.colours).any(-1).all(1))[0]

        # self.correction_map = []    # for diagnostic
        self.limbo_map = []
        # find difference vector of outlier colours to main colour.  Minimal difference = closest colour
        # easy alg: subtract outlier colour from defined set array, sum RGB values, find minimum, match index
        for idx in self.outliers:
            in_limbo = False
            c = self.c_unique[idx, :]
            c_delta = np.sum(np.abs(np.array(self.colours) - c), axis=1)
            # additional check: if c_delta higher than condition, default to black
            if np.amin(c_delta) > 70:
                parent = (0, 0, 0)
                in_limbo = True
            else:
                parent = self.colours[np.argmin(c_delta, axis=0)]

            # self.correction_map.append((c, parent, np.min(c_delta))) # diagnostic

            # find indices of all pixels with matching colour
            outlier_pixels = self.find_colour_coords(c)
            if in_limbo:
                self.limbo_map.append(
                    [(c, list(zip(idx % self.gridsize[1], idx // self.gridsize[1]))) for idx in outlier_pixels])
            # replace outlier colour to main colour
            for idx in outlier_pixels:
                self.rgbcoords_1d[idx, :] = parent

        if len(np.unique(self.rgbcoords_1d, axis=0)) != len(self.colours):
            raise ValueError('RGB correction issue, colours in corrected array not the same as defined set.')

        # ToyModel-like grid entity populating and visitor spawning
        self.fill_grid(index_map)
        self.not_spawnable_objects = [IA.Wall, IA.Obstacle,
                                      IA.Desk, IA.OutOfBounds, IA.Exit,
                                      IA.ExitA, IA.ExitB, IA.ExitC,
                                      IA.HelpDesk,
                                      IA.Shelf, IA.DeskInteractive,
                                      IA.HelpDeskInteractiveForHelpee,
                                      IA.HelpDeskInteractiveForHelper,
                                      IA.ShelfInteractive]
        self.set_up_exits()
        # self.batchcompute_all_exits(overwrite=True, test=False) # batchcompute must come after exit setup
        # self.spawn_visitors(n=self.n_visitors)
        # self.spawn_staff_and_get_exits_paths(n=self.n_officestaff)

        # self.batchcompute_closest_exit()

        self.datacollector = DataCollector(model_reporters={"safe_agents": self.get_nr_of_safe_agents})

    def is_done(self):
        return len(self.safe_agents) >= self.n_staff + self.n_visitors

    def next_id(self):
        """
        Returns current id and increments the id_counter such that each agent has a unique identifier
        :return:
        """
        self.id_counter += 1
        return self.id_counter - 1

    def step(self):
        self.end_time += 1
        self.schedule.step()
        self.datacollector.collect(self)

        # print(self.end_time)

    def set_up_exits(self):

        if self.valid_exits == ExitType.ABC:
            pass
        elif self.valid_exits == ExitType.A:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA]
        elif self.valid_exits == ExitType.B:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITB]
        elif self.valid_exits == ExitType.C:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITC]
        elif self.valid_exits == ExitType.AB:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA] + self.destinations[
                Destination.EXITB]
        elif self.valid_exits == ExitType.BC:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITB] + self.destinations[
                Destination.EXITC]
        elif self.valid_exits == ExitType.AC:
            self.destinations[Destination.EXIT] = self.destinations[Destination.EXITA] + self.destinations[
                Destination.EXITC]

    def get_total_evacuation_time(self):
        return self.end_time

    def get_nr_of_safe_agents(self, dummy=1):
        return len(self.safe_agents)

    def find_colour_coords(self, RGB_value):
        """
        With given RGB values, return an array of all found coordinates
        :return:
        """
        return np.where((self.rgbcoords_1d[:, 0] == RGB_value[0]) &
                        (self.rgbcoords_1d[:, 1] == RGB_value[1]) &
                        (self.rgbcoords_1d[:, 2] == RGB_value[2]))

    def fill_grid(self, index_map):
        """
        Iterates through colour list, finds pixels matching said colour,
        Saves spawnable tiles and destination tiles in respective data types
        Loads library objects (walls, desks) and office staff (in specific seats)
        In terms of functionality to ToyModel methods, it does:
            * fill_grid() {the ToyModel version}
            * add_exit_to_correct_keys()
            * get_all_spawnable_cells()
            * spawn_staff()
        :param index_map: list of tuples with Dataframe indices and associated colours
        """
        # iterate through object_colours.tsv's entity names & colours
        for obj, c in index_map:
            idxs = self.find_colour_coords(c)[0]
            y = idxs // self.gridsize[1]  # converts 1D coords to 2D
            x = idxs % self.gridsize[1]
            coords = zip([int(ix) for ix in x], [int(iy) for iy in y])
            # save spawnable items into list
            if bool(int(self.colour_to_grid_object.loc[obj, 'Spawnable'])):
                self.spawnable_positions.extend(coords)

            # save destinations to dict as defined in init, used for pathfinding
            try:
                entity_type = self.colour_to_grid_object.loc[obj, 'Entity_category']
                user_destination = None
                sub_destination = None
                if 'exit' in entity_type.lower():
                    user_destination = Destination.EXIT
                    if entity_type == "ExitA":
                        sub_destination = Destination.EXITA
                    elif entity_type == "ExitB":
                        sub_destination = Destination.EXITB
                    elif entity_type == "ExitC":
                        sub_destination = Destination.EXITC
                    elif entity_type == "Exit":
                        # hacky way of catching generic Exit tiles, while still accounting for other exit classes
                        # print("MapModel: generic Exit object detected, these tiles won't be considered in pathfinding")
                        user_destination = None
                    else:
                        raise ValueError("Exit Does not exist")
                elif 'DeskInteractive' in entity_type:
                    user_destination = Destination.DESK
                elif 'ShelfInteractive' in entity_type:
                    user_destination = Destination.SHELF
                elif 'helpdeskhelpee' in entity_type.lower():
                    user_destination = Destination.HELPDESK
                elif 'office' in entity_type.lower():
                    self.office_positions.extend(coords)
                elif 'helpdeskhelper' in entity_type.lower():
                    self.helpdesk_positions.extend(coords)

                if user_destination is not None:
                    self.destinations[user_destination].extend(coords)

                if user_destination is Destination.EXIT:
                    self.destinations[sub_destination].extend(coords)

            except AttributeError:  # catches NaNs being floats
                continue

            # Office entities
            staff_types = ('Office', 'HelpDeskInteractiveForHelper')

            # iterates through coords of the same colour
            for x, y in coords:
                try:
                    # disaggregating x and y to force typecasting to int (TEMP. DEACTIVATED)
                    # x = int(x)
                    # y = int(y)
                    # below: use Entity_category string from object_colours.tsv to match
                    # with the classes from inanimate agents (hence alias IA)
                    # parentheses after: initiate the matched inanimate class with its associated args
                    if self.colour_to_grid_object.loc[obj, 'Entity_category'] not in staff_types:
                        object = getattr(IA, self.colour_to_grid_object.loc[obj, 'Entity_category'])(self.next_id(),
                                                                                                     self)
                        self.grid.place_agent(object, pos=(x, y))
                    # else:  # entities from animate class go here (helpdesk staff and office staff)
                    #     # only insert helpdesk staff for now
                    #     if self.colour_to_grid_object.loc[obj, 'Entity_category'] == 'Office':
                    #         self.office_positions.append((x, y))
                    #     elif self.colour_to_grid_object.loc[obj, 'Entity_category'] == 'HelpDeskInteractiveForHelper':
                    #         self.helpdesk_positions.append((x,y))
                    #         agent_class = Staff(self.next_id(), self, female_ratio=self.female_ratio,
                    #                             adult_ratio=self.adult_ratio)
                    #         self.grid.place_agent(agent=agent_class, pos=(x, y))
                    #         self.schedule.add(agent_class)
                    #         self.staff_agents.append(agent_class)
                    #         self.n_staff += 1


                except TypeError:
                    # Catches TypeError for walkable tiles (since only unwalkables are placed)
                    continue
        # print("\tMappingModel.py: all grid objects transferred to MESA grid entities.")

    def spawn_visitors(self, n):
        """
        Spawns n visitors randomly on the grid, avoiding cells that are off limits for visitors
        :param n: number of visitors to spawn
        :return:
        """

        positions = random.sample(self.spawnable_positions, k=n)
        for pos in positions:
            visitor = Visitor(self.next_id(), self, female_ratio=self.female_ratio,
                              adult_ratio=self.adult_ratio, familiarity=self.familiarity)

            self.grid.place_agent(agent=visitor, pos=pos)
            self.schedule.add(visitor)

    def spawn_staff_and_get_exits_paths(self, n=3):
        """
        Does the following:
        * spawns n staff randomly amongst the defined Office spots on the map.
        * Finds shortest route to eligible/valid exits, based on precalculated routes
        * Encodes shortest destination (not route, since it's already a lookup)

        :param n: number of staff members
        :return: None
        """
        positions = random.sample(self.office_positions, k=n)
        positions.extend(self.helpdesk_positions) # addition of fixed/constant helpdesk locations
        valid_exits = self.destinations[Destination.EXIT]

        for pos in positions:
            staffpax = Staff(self.next_id(), self, female_ratio=self.female_ratio,
                              adult_ratio=self.adult_ratio)
            self.grid.place_agent(agent=staffpax, pos=pos)
            self.schedule.add(staffpax)
            self.staff_agents.append(staffpax)
            routes = [self.all_paths[(pos,dest)] for dest in valid_exits]
            lengths = [len(route) for route in routes]
            staffpax.emergency_knowledge.closest_exit = routes[lengths.index(min(lengths))][-1]
            self.n_staff += 1
        print(f"MapModel: all {n} Staff entities' destinations encoded.")


    def batchcompute_closest_exit(self):
        """
        conducts the agent_class.emergency_knowledge.compute_closest_exit() for agent classes in one printed wrapper
        :return: None
        """
        print(f"\t>Pre-calculating exit paths for staff, total count: {self.n_staff}.\n"
              f"\t>Estimated time per staff: ~1min. Make yourself comfortable")
        for n, staff in enumerate(self.staff_agents):
            staff.emergency_knowledge.compute_closest_exit()
            print(f'\t\t>>progress: {n + 1}/{self.n_staff}')
        print("\t\t>>All staff agents' exit paths pre-calculated.")


    def batchcompute_all_exits(self, overwrite=False, save_name='office_to_exit_paths', test=False):
        """
        For all exits, compute the shortest path from all office spots to said exits.
        BatchCompute must be called after self.set_exits()
        :overwrite: bool for overwriting current pre-saved map
        :return: None
        """
        # check if file exists, if not then run, if overwrite=True, then go
        construct = False
        if test:    # test overrides all, but doesn't save
            construct = True
        else:
            if os.path.isfile(f'{save_name}.pickle'):
                print("> Paths file available.")
                if overwrite:
                    print('> Overwriting Paths file, constructing...' )
                    construct = True
                else:
                    with open(f"{save_name}.pickle",'rb') as read:
                        self.all_paths = pickle.load(read)
                    print(">> Paths file loaded!")
            else:
                print("> Paths file not found. Constructing paths file...")
                construct = True

        if construct:
            all_exits = self.destinations[Destination.EXIT]
            all_sources = self.office_positions + self.helpdesk_positions
            print(all_sources)
            self.timer = []
            print(f"\n> Calculating all paths for all exits (for office spots), total: {len(self.office_positions)}."
                  "\n> Average time per epoch: <1 min. Make yourself comfortable.")
            for epoch, pos in enumerate(all_sources):
                start_t = time.time()
                print(f'\t>> Epoch: {epoch+1}/{len(all_sources)}')
                # iterate through exits
                for idx, exit in enumerate(all_exits):
                    paths = [a_star_search(self.grid, pos, exit)]
                    lengths = [len(a) for a in paths]
                    shortest_path = paths[lengths.index(min(lengths))]
                    self.all_paths[(pos, exit)] = shortest_path
                self.timer.append(round(time.time() - start_t, 1))
                if test:    # for diagnostic
                    if epoch + 1 == 2:
                        break

            print("\t>>All paths to all exits calculated.")
            with open(f'{save_name}.pickle', 'wb') as handle:
                pickle.dump(self.all_paths, handle, protocol=pickle.HIGHEST_PROTOCOL)

# test = MapModel()
# if __name__ ==  "__main__ ":
#     test_item = MapModel()
