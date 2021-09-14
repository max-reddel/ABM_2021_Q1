from mesa import Agent
from PathFinding import a_star_search
from enum import Enum
import random


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class Movement(Enum):
    RUNNING = 1
    WALKING = 2
    STANDING = 3


class Person(Agent):

    def __init__(self, unique_id, model, gender):
        super().__init__(unique_id, model)

        # Constant attributes # TODO: Transform into Constants?
        # self.pos = pos
        self.gender = gender
        self.age = random.randint(13, 100)  # only for potential extension
        self.busy = False  # interacting with another object (Desk, Shelf, etc.)

        # Walking related (TODO: create object)
        self.default_walking_speed = self.get_default_speed(Movement.WALKING)
        self.default_running_speed = self.get_default_speed(Movement.RUNNING)
        self.entered_via = self.sample_entrance()  # from which entrance/exit they entered the building

        self.path_to_current_dest = []  # First element is current position.
        # Later: get this from pathfinding-dict (also using self.tasks)

        # Evacuation related (TODO: create object)
        self.had_safety_training = False
        self.knows_exits = False  # knows all exits?
        self.exit_time = None
        self.exit_location = None
        self.heard_alarm = False  # self.model.alarm_rang()  # Later: implement this in model class.
        # Currently: alarm goes off --> all agents hear it. Thus, boolean depends on whether it rang already or not.

        self.current_task = CompositeTask(self, self.model)  # CompositeTask object

    def step(self):

        # if task done:             # check this in self.current_task attributes
        #   sample_new_task()
        # continue task

        # self.walk()
        self.current_task.do()

    def get_default_speed(self, movement):
        """
        Returns the default speed of a person. I.e., the speed before any adjustments due to crowds or slopes.
        :param movement:    Element of Movement-Enum
        :return:            float, default speed of the person
        """
        # Specifying speeds
        male_dict = {Movement.RUNNING: 0.1,  # original 1.5
                     Movement.WALKING: 0.1}  # original 1.0
        female_dict = {Movement.RUNNING: 0.1,  # original 1.4
                       Movement.WALKING: 0.1}  # origional 0.9

        # Read movement-speed from the right dictionary & return it.
        speed = 0.0  # Heads-up: If gender would be sth else than MALE/FEMALE, speed would always be 0.
        if self.gender == Gender.MALE:
            speed = male_dict[movement]
        elif self.gender == Gender.FEMALE:
            speed = female_dict[movement]
        return speed

    def sample_entrance(self):
        """
        Samples an entrance for a person.
        :return:        Enum of possible Entrances/Exits
        """
        entrance = "main entrance"  # Later: create Entrance Enum, actually sample from it
        return entrance

    def sample_safety_training(self, probability=0.1):
        """
        Samples whether a person had safety training. They had it with a probability of 'probability'.
        :param probability:     float, between 0.0 and 1.0
        :return:                boolean, whether the person had safety training
        """
        if random.random() <= probability:
            self.had_safety_training = True

    def get_knows_exits(self, probability=0.1):
        """
        Samples whether a person knows the exits. They know it with a probability of 'probability'.

        :param probability:     float, between 0.0 and 1.0
        :return:                boolean, whether the person knows the exits
        """
        knows_exits = False  # default
        # everyone who had safety training, knows all exits
        if self.had_safety_training:
            knows_exits = True
        # people without safety training know the exits with a probability of 0.1 ('probability')
        else:
            if random.random() <= probability:
                knows_exits = True
        return knows_exits

    def walk(self, destination):
        """
        Makes the agent walk. By moving it from its current position, into the direction of their current destination,
        with its speed being adjusted to whether it is an emergency (i.e., adjusted the Movement mode)
        and the amount of people nearby.

        Disclaimer: Currently still basic version. Only walking into right direction.
        """
        self.path_to_current_dest = a_star_search(self.model.grid, self.pos, destination)

        # Calculate how many cells you can travel

        stride_length = int(self.default_walking_speed * 10)

        try:
            # Find cell you should move to
            new_pos = self.path_to_current_dest[stride_length]
            # Adjust remaining path
            self.path_to_current_dest = self.path_to_current_dest[stride_length:]
        except:
            # Find cell you should move to (if stride is overreaching destination)
            new_pos = self.path_to_current_dest[-1]
            # Adjust remaining path
            self.path_to_current_dest = [self.path_to_current_dest[-1]]

        # Adjust agent-placement on grid
        self.model.grid.move_agent(agent=self, pos=new_pos)

        print(f"Agent walked to position: {new_pos}")

    def stay(self):
        """
        """
        # TODO: Maybe engage with the object in place?
        self.busy = True


class Visitor(Person):

    def __init__(self, unique_id, model, gender):
        super().__init__(unique_id, model, gender)
        self.sample_safety_training(probability=0.1)  # Few visitors had safety training
        self.knows_exits = self.get_knows_exits(probability=0.1)  # knows all exits?
        self.tasks = []  # list of planned tasks (destination & end-time). First task is current task.
        # Later: add/sample this list. Could also have only current_task instead
        # & sample new task when current_task is done.

    # def step(self):
    #     task = self.current_task.get_current_sub_task(agent)
    #     do_task(task)
    #     pass


class Staff(Person):

    def __init__(self, unique_id, model, gender):
        super().__init__(unique_id, model, gender)
        self.had_safety_training = True  # All staff had safety training
        self.knows_exits = True
        self.tasks = []  # list of planned tasks (destination & end-time). First task is current task.
        # Later: add/sample this list

    # def step(self):
    #     pass


###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class CompositeTask:

    def __init__(self, person, model, task_name=None):
        """
        :param person: Person: person that holds this composite task
        :param task_name:
        """

        if task_name is None:
            # atm STUDY, should become randomly sampled
            task_name = VisitorTasks.STUDY
        else:
            self.task_name = task_name

        self.person = person
        self.model = model
        self.destinations = model.destinations
        self.remaining_subtasks = self.generate_sub_tasks()

    def generate_sub_tasks(self):

        remaining_subtasks = []

        if isinstance(self.person, Visitor):

            # TODO: Currently hardcoded to STUDY, should generalize to many tasks
            remaining_subtasks = [Walk(self.person, self.destinations, Destination.DESK),
                                  Stay(self.person)]

        return remaining_subtasks

    def do(self):

        try:
            current_subtask = self.remaining_subtasks[0]
        except:
            pass

        # If all tasks are done
        if not self.remaining_subtasks:
            self.remaining_subtasks = self.generate_sub_tasks()
            print('all tasks are done!')
            print(f'new destination: {self.remaining_subtasks[0].destination}')

        # if current subtask should still run
        elif not current_subtask.is_done():
            if isinstance(current_subtask, Walk):
                # print(f'agent position: \t{self.person.pos}')
                # print(f'current path: \t{self.person.path_to_current_dest}')
                picked_destination = current_subtask.destination
                self.person.walk(picked_destination)
            elif isinstance(current_subtask, Stay):
                self.person.stay()

            current_subtask.update()

            # remove finished subtask from remaining substasks
            if current_subtask.is_done():
                self.remaining_subtasks = self.remaining_subtasks[1:]







class BasicTaskName(Enum):
    WALK = 1
    STAY = 2


class Destination(Enum):
    """
    This enum contains all kinds of walking destinations.
    """

    EXIT = 0
    DESK = 1
    SHELF = 2
    HELPDESK = 3


class BasicTask:

    def __init__(self, person):

        self.person = person
        self.type = None

    def is_done(self):
        pass

    def update(self):
        pass


class Walk(BasicTask):

    def __init__(self, person, destinations, destination_type=None):

        super().__init__(person)

        self.type = BasicTaskName.WALK
        self.destinations = destinations

        if destination_type is not None:
            self.destination_type = destination_type
        else:
            self.destination_type = Destination.DESK  # TODO: This might be different, dependent on what the destination_type really is

        self.destination = self.get_random_destination()
        # print('new destination in Walk object')

    def get_random_destination(self):
        """
        Returns a random destination as a position (tuple) given the specified destination_type.
        E.g. if destination_type is STUDY, this functions returns a random chair position.
        :return: position
        """

        relevant_destinations = self.destinations[self.destination_type]

        # Avoid to get the same destination as you are in at the moment
        if not self.person.path_to_current_dest:
            destination = ()
        else:
            destination = self.person.path_to_current_dest[-1]
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
            self.remaining_duration = random.uniform(3, 8)  # TODO: other numbers are needed

    def is_done(self):
        self.person.busy = False
        return self.remaining_duration <= 0

    def update(self):
        self.remaining_duration -= 1


class VisitorTasks(Enum):
    # TODO: Continue here: Where do I get the destinations from without circular dependencies?
    STUDY = 1
    GET_HELP = 2
    GET_BOOK = 3


class StaffTasks(Enum):
    PROVIDE_HELP = 1
    WORK_IN_OFFICE = 2
