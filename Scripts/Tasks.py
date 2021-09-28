from PathFinding import a_star_search
import random
from Enums import *


class CompositeTask:

    def __init__(self, person, model):
        """
        :param person: Person: person that holds this composite task
        :param model: Model
        """

        self.person = person
        self.model = model
        self.destinations = model.destinations

        self.remaining_subtasks = self.generate_sub_tasks()

    def generate_sub_tasks(self):
        """
        This function randomly generates a list of sub-tasks for visitors or staff.
        :return: remaining_tasks: list with sub-tasks
        """

        remaining_subtasks = []

        # Sample a random task
        all_possible_visitor_tasks = [VisitorTasks.STUDY, VisitorTasks.GET_BOOK, VisitorTasks.GET_HELP]
        all_possible_staff_tasks = [StaffTasks.PROVIDE_HELP, StaffTasks.WORK_IN_OFFICE]

        # Prepare composite task for the visitor
        if self.person.__class__.__name__ == "Visitor":
            remaining_subtasks = self.generate_visitor_sub_tasks(all_possible_visitor_tasks)

        # # Prepare composite task for staff
        elif self.person.__class__.__name__ == "Staff":
            self.generate_staff_sub_tasks(all_possible_staff_tasks)

        return remaining_subtasks

    def generate_staff_sub_tasks(self, all_possible_staff_tasks):
        """
        This function randomly generates a list of sub-tasks for staff.

        :param: all_possible_staff_tasks: list with all StaffTasks in it.
        :return: remaining_tasks: list with sub-tasks
        """

        remaining_subtasks = []

        weights = self.get_weights(all_possible_staff_tasks)
        random_task = random.choices(all_possible_staff_tasks, weights)[0]

        if random_task == StaffTasks.PROVIDE_HELP:
            remaining_subtasks = [Stay(self.person)]  # Helping could be more complex (interaction with visitor?)
        elif random_task == StaffTasks.WORK_IN_OFFICE:
            remaining_subtasks = [Stay(self.person)]

        return remaining_subtasks

    def generate_visitor_sub_tasks(self, all_possible_visitor_tasks):
        """
        This function randomly generates a list of sub-tasks for visitors.

        :param: all_possible_staff_tasks: list with all VisitorTasks in it.
        :return: remaining_tasks: list with sub-tasks
        """

        remaining_subtasks = []

        weights = self.get_weights(all_possible_visitor_tasks)
        random_task = random.choices(all_possible_visitor_tasks, weights)[0]

        if random_task == VisitorTasks.STUDY:
            remaining_subtasks = [Walk(self.person, self.destinations, Destination.DESK), Stay(self.person)]
            self.person.emergency_knowledge.stopping_time = VisitorTasks.STUDY.value

        elif random_task == VisitorTasks.GET_BOOK:
            remaining_subtasks = [Walk(self.person, self.destinations, Destination.SHELF), Stay(self.person)]
            self.person.emergency_knowledge.stopping_time = VisitorTasks.GET_BOOK.value

        elif random_task == VisitorTasks.GET_HELP:
            remaining_subtasks = [Walk(self.person, self.destinations, Destination.HELPDESK), Stay(self.person)]
            self.person.emergency_knowledge.stopping_time = VisitorTasks.GET_HELP.value

        return remaining_subtasks

    def get_weights(self, tasks):
        """
        This function returns weights for random.choices depending on how many desk, shelf, and help desk destinations there are.
        :return: weights: list with floats adding to up 1
        """

        weights = []
        w = 1

        for task in tasks:
            if task == VisitorTasks.STUDY:
                w = len(self.destinations[Destination.DESK])
            elif task == VisitorTasks.GET_BOOK:
                w = len(self.destinations[Destination.SHELF])
            elif task == VisitorTasks.GET_HELP:
                w = len(self.destinations[Destination.HELPDESK])
            weights.append(w)

        # norammlize weights
        weights = [i/sum(weights) for i in weights]

        return weights

    def do(self):

        # In normal situation
        if not self.person.emergency_knowledge.is_evacuating:

            # If all tasks are done
            if not self.remaining_subtasks:
                self.remaining_subtasks = self.generate_sub_tasks()

            # if current subtask should still run
            elif not self.remaining_subtasks[0].is_done():
                self.do_current_sub_task()

        # In emergency situation
        else:

            if not self.person.emergency_knowledge.left:
                # Old version of evacuating
                # exit_destination = self.person.emergency_knowledge.entered_via
                # self.remaining_subtasks = [Walk(self.person, self.destinations, destination=exit_destination)]

                # new version of evacuating
                if self.person.__class__.__name__ == "Visitor":
                    self.remaining_subtasks = [VisitorEvacuation(self.person)]
                elif self.person.__class__.__name__ == "Staff":
                    self.remaining_subtasks = [StaffEvacuation(self.person)]

            # If already in exit posiiton, remove from model
            if self.person.pos == self.person.emergency_knowledge.closest_exit:

                self.model.grid.remove_agent(self.person)
                self.model.schedule.remove(self.person)
                self.person.emergency_knowledge.left = True

            # if current subtask should still run
            elif not self.remaining_subtasks[0].is_done():

                self.do_current_sub_task()

    def do_current_sub_task(self):
        """
        Execute the current subtask for the current tick and update all correpsonding datastructures.
        """

        current_subtask = self.remaining_subtasks[0]
        current_subtask.do()
        current_subtask.update()

        # remove finished subtask from remaining substasks
        if current_subtask.is_done():
            self.remaining_subtasks = self.remaining_subtasks[1:]


class BasicTask:

    def __init__(self, person):

        self.person = person
        self.type = None
        self.busy = False

    def is_done(self):
        pass

    def update(self):
        pass

    def do(self):
        pass


class Walk(BasicTask):

    def __init__(self, person, destinations, destination_type=None, destination=None):

        super().__init__(person)

        self.type = BasicTaskName.WALK
        self.destinations = destinations

        if destination_type is not None:
            self.destination_type = destination_type
        else:
            self.destination_type = Destination.DESK

        if destination is None:
            self.destination = self.get_random_destination()
        else:
            self.destination = destination

    def do(self):
        """
        Makes the agent walk. By moving it from its current position, into the direction of their current destination,
        with its speed being adjusted to whether it is an emergency (i.e., adjusted the Movement mode)
        and the amount of people nearby.

        Disclaimer: Currently still basic version. Only walking into right direction.
        """
        self.person.move_data.path_to_current_dest = a_star_search(self.person.model.grid, self.person.pos, self.destination)

        # Calculate how many cells you can travel
        # stride_length = int(self.person.move_data.walking_speed * 10)
        stride_length = int(self.person.get_current_speed() * 10)


        try:
            # Find cell you should move to
            new_pos = self.person.move_data.path_to_current_dest[stride_length]
            # Adjust remaining path
            self.person.move_data.path_to_current_dest = self.person.move_data.path_to_current_dest[stride_length:]
        except:
            # Find cell you should move to (if stride is overreaching destination)
            new_pos = self.person.move_data.path_to_current_dest[-1]
            # Adjust remaining path
            self.person.move_data.path_to_current_dest = [self.person.move_data.path_to_current_dest[-1]]

        # Adjust agent-placement on grid
        self.person.model.grid.move_agent(agent=self.person, pos=new_pos)

    def get_random_destination(self):
        """
        Returns a random destination as a position (tuple) given the specified destination_type.
        E.g. if destination_type is STUDY, this functions returns a random chair position.
        :return: position
        """

        relevant_destinations = self.destinations[self.destination_type]

        # Avoid to get the same destination as you are in at the moment
        if not self.person.move_data.path_to_current_dest:
            destination = ()
        else:
            destination = self.person.move_data.path_to_current_dest[-1]
        random_destination = random.choice(relevant_destinations)

        while destination == random_destination:
            random_destination = random.choice(relevant_destinations)

        return random_destination

    def is_done(self):
        """
        Returns True if the person reached the final destination.
        :return: boolean
        """

        return self.person.pos == self.destination

    def update(self):
        pass


class Stay(BasicTask):

    def __init__(self, person, duration=None):

        super().__init__(person)
        self.type = BasicTaskName.STAY

        if duration is not None:
            self.remaining_duration = duration
        else:
            self.remaining_duration = random.uniform(5, 20)

    def is_done(self):
        self.person.busy = False
        return self.remaining_duration <= 0

    def update(self):
        self.remaining_duration -= 1

    def do(self):
        """
        Stay.
        """
        self.busy = True


class EvacuationTask:

    def __init__(self, person):

        self.person = person
        self.type = None
        self.busy = False

    def do(self):
        pass

    def is_done(self):
        """
        Returns True if the person reached the final destination.
        :return: boolean
        """

        return self.person.pos == self.person.emergency_knowledge.closest_exit

    def update(self):
        pass


class VisitorEvacuation(EvacuationTask):

    def __init__(self, person):

        super().__init__(person)
        self.destinations = self.person.model.destinations

    def do(self):

        exit_destination = self.person.emergency_knowledge.closest_exit
        walk = Walk(self.person, self.destinations, destination=exit_destination)
        walk.do()


class StaffEvacuation(EvacuationTask):

    def __init__(self, person):

        super().__init__(person)
        self.destinations = self.person.model.destinations

    def do(self):

        # Inform surrounding visitors about the closest exit
        self.person.update_exit_information_of_surrounding_visitors(radius=5)

        # Wait for visitors to leave the area
        if self.person.are_visitors_close_by(radius=5):
            stay = Stay(self.person)
            stay.do()
        else:
            # Go to exit
            exit_destination = self.person.emergency_knowledge.closest_exit
            walk = Walk(self.person, self.destinations, destination=exit_destination)
            walk.do()
