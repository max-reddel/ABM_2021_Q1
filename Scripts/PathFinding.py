from Scripts.ToyModel import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from queue import PriorityQueue


def get_all_paths(grid):
    """
    This functions takes in the model and calculates the ideal path from each cell to the closest and the main exit.
    This will return a dictionary with these paths.
    This will be calculated at the initiation of the model.
    """

    print("Calculating all possible paths ... ")
    all_paths = {}

    origins = init_origins(grid)  # all not wall and obstacle cells
    destinations = init_destinations(grid)  # exits, desks, shelves, and helpDesks

    for d in destinations:
        for o in origins:
            path = a_star_search(grid, o, d)
            all_paths[(o, d)] = path

    print('All paths have been calculated!')
    return all_paths


def a_star_search(grid, origin, destination):
    """
    This function returns the shortest path between pos1 and pos2 on a grid.
    Inspiration from: https://www.redblobgames.com/pathfinding/a-star/implementation.html

    :param grid: MultiGrid
    :param origin: Tuple
    :param destination: Tuple

    :return: path : list
    """

    frontier = PriorityQueue()
    frontier.put(origin, 0)
    path = {}  # This will be sth like a linked list
    cost_so_far = {}
    path[origin] = None
    cost_so_far[origin] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == destination:
            break

        for next_pos in get_valid_neighbors(grid, current):
            new_cost = cost_so_far[current] + 1
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + get_heuristic_val(next_pos, destination)
                frontier.put(next_pos, priority)
                path[next_pos] = current

    # Convert path from a linked list to proper list
    pos = destination
    path_list = []

    try:
        while pos is not origin:
            path_list.append(pos)
            pos = path[pos]
    except:
        pass

    path_list.reverse()
    return path_list


def get_valid_neighbors(grid, pos):
    """
    This function returns the adjacent cells of some position on the grid, excluding all cells that contain walls and
    obstacles.

    :param grid: MultiGrid
    :param pos: Tuple
    :return: list with positions (tuples)
    """
    valid_neighbors = set()

    neighbor_positions = grid.iter_neighborhood(pos, moore=False, include_center=False, radius=1)

    for neighbor_pos in neighbor_positions:

        n_list = grid.get_cell_list_contents([neighbor_pos])

        if not n_list:  # if there no other agents in that list
            valid_neighbors.add(neighbor_pos)
        else:
            n = n_list[0]  # if there are agents on this list
            if not isinstance(n, Wall) and not isinstance(n, Obstacle):
                valid_neighbors.add(neighbor_pos)

    valid_neighbors = list(valid_neighbors)
    return valid_neighbors


def get_heuristic_val(origin, destination):
    """
    Returns the heuristic value for the a_star algorithm. In this case, it's just the Manhattan distance.
    :param origin: Tuple: origin
    :param destination: Tuple: destination

    :return: h: heuristic value
    """
    delta_x = abs(origin[0] - destination[0])
    delta_y = abs(origin[1] - destination[1])

    return delta_x + delta_y


def init_origins(grid):
    """
    This function provides a list with all positions on the grid that are not walls or obstacles.
    :param grid: MultiGrid
    :return: list: list of positions (tuples)
    """

    origin_list = []

    for w in range(grid.width):
        for h in range(grid.height):
            pos = (w, h)
            n_list = grid.get_cell_list_contents([pos])

            if not n_list:
                origin_list.append(pos)
            else:
                n = n_list[0]  # if there are agents on this list
                if not isinstance(n, Wall) and not isinstance(n, Obstacle):
                    origin_list.append(pos)

    return origin_list


def init_destinations(grid):
    """
    This function provides a list with all positions on the grid that are exits, shelves, helpDesks, or desks.
    :param grid: MultiGrid
    :return: list: list of positions (tuples)
    """

    destinations_list = []

    for w in range(grid.width):
        for h in range(grid.height):
            pos = (w, h)
            n_list = grid.get_cell_list_contents([pos])

            if n_list:
                n = n_list[0]
                if isinstance(n, Exit) or \
                        isinstance(n, HelpDesk) or \
                        isinstance(n, Desk) or \
                        isinstance(n, Shelf):
                    destinations_list.append(pos)

    return destinations_list


def create_toy_space(visalize=False):
    """
    This function creates a multi-grid space and fills it with some inanimate agents.
    """
    model = ToyModel(width=20, height=15)
    if visalize:
        show_visualization(ToyModel)

    return model.grid


def show_visualization(model):
    """
    Creates an animation, given a model type (e.g. EvacuationModel)
    """

    def agent_portrayal(agent):
        """
        This function determines how agents should look like (color, shape, etc.)
        """

        portrayal = {"Filled": "true",
                     "Layer": 0}

        if isinstance(agent, Wall):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "gray"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, Exit):
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "red"
            portrayal["h"] = 1
            portrayal["w"] = 1

        if isinstance(agent, Visitor):
            portrayal["Shape"] = "circle"
            portrayal["Color"] = "blue"
            portrayal["r"] = 0.5

        # More agents would be necessary to check for here

        return portrayal

    # Parameters
    width = 20
    height = 15
    size = 20

    canvas = CanvasGrid(agent_portrayal, width, height, size * width, size * height)

    server = ModularServer(model,
                           [canvas],
                           "Evacuation Model",
                           {"width": width, "height": height})
    server.port = 8521  # The default
    server.launch()


if __name__ == "__main__":
    toy_grid = create_toy_space(visalize=False)
    # start = (1, 13)  # upper left corner
    # end = (5, 11)  # 4 cells further to the right
    # final_path = a_star_search(toy_grid, start, end)
    # print(final_path)

    paths = get_all_paths(toy_grid)
    print(f'Number of paths: {len(paths)}')
