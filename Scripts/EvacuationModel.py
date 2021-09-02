from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from Scripts.PathFinding import a_star


class EvacuationModel(Model):

    def __init__(self, num_staff, num_visitors, female_ratio=0.5):
        super().__init__()
        self.num_staff = num_staff
        self.num_visitors = num_visitors
        self.female_ratio = female_ratio

        self.grid = MultiGrid(width=200, height=200, torus=False)  # values for width and height have to be changed
        self.schedule = RandomActivation(self)

        self.place_items_onto_grid()  # see description below
        self.place_persons_onto_grid()  # see description below

        self.all_paths = a_star(self.grid)

    def step(self):
        print(f'Doing model step #{self.schedule.time}!')
        self.schedule.step()

    def place_items_onto_grid(self):
        """
        This function positions all items (desks, exits, walls, etc.) onto the grid. The result will be an
        approximation of the TU Delft library's blue print.
        """
        pass

    def place_persons_onto_grid(self):
        """
        This function positions all staff members and visitors onto the grid. A basic version of this function
        should position the visitors and the staff in random positions of the grid.
        """
