from mesa import Agent
import random
from Tasks import CompositeTask
from Enums import *


class Person(Agent):

    def __init__(self, unique_id, model, gender=Gender.FEMALE):

        super().__init__(unique_id, model)

        self.gender = gender
        self.age = random.randint(13, 100)  # only for potential extension
        self.busy = False  # interacting with another object (Desk, Shelf, etc.)

        self.move_data = MovementData(self.gender)
        self.emergency_knowledge = EmergencyKnowledge(self)
        self.current_task = CompositeTask(self, self.model)

    def step(self):

        self.current_task.do()

    def get_nr_of_neighbors(self, agent_type, radius=6):
        """
        Check whether there are any specific types of agents around this agent and return how many. Radius is 6 dm
        because the speed will need to be adjusted. This adjustment is dependent on the square meter that an agent is
        in. So, if the area should be 1 m2, then the radius needs to be roughly 0.56 m. Rounding to 0.6.
        :param: radius: int
        :param: agent_type: Agent (Person, Staff, Visitor, or any other)
        :return: nr_of_neighbors: int
        """

        # get all neighbors (including inanimate agents
        all_agents = self.model.grid.get_neighbors(pos=self.pos, moore=True, include_center=False, radius=radius)

        # filter out all inanimate agents
        animate_agents = [x for x in all_agents if isinstance(x, agent_type)]
        nr_of_neighbors = len(animate_agents)

        return nr_of_neighbors

    def scan_environment_for_evacuation(self, agent_type, radius=500):
        """
        Check whether there are any specific types of agents around and how many seem to be evacuating.
        :param: radius: int
        :param: agent_type: Agent (Person, Staff, Visitor, or any other)
        :return: evacuating_ratio: float
        """

        # get all neighbors (including inanimate agents
        all_agents = self.model.grid.get_neighbors(pos=self.pos, moore=True, include_center=False, radius=radius)

        # filter out all inanimate agents
        animate_agents = [x for x in all_agents if isinstance(x, agent_type)]

        nr_of_neighbors = len(animate_agents)

        # Check how many neighbors are evacuating
        evacuating_neighbors = [x for x in animate_agents if x.emergency_knolwedge.is_evacuating]

        if nr_of_neighbors == 0:
            return 0
        else:
            evacuating_ratio = float(len(evacuating_neighbors) / nr_of_neighbors)
            return evacuating_ratio


class Visitor(Person):

    def __init__(self, unique_id, model, gender=Gender.FEMALE):

        super().__init__(unique_id, model, gender)

        self.emergency_knowledge.sample_safety_training(probability=0.1)  # Few visitors had safety training
        self.emergency_knowledge.knows_exits = self.emergency_knowledge.get_knows_exits(probability=0.1)

    def step(self):

        # self.move_data.update_speed(self)

        # Super simple version of knowing about the alarm
        if self.model.alarm.is_activated:
            self.emergency_knowledge.is_evacuating = True
        self.current_task.do()


class Staff(Person):

    def __init__(self, unique_id, model, gender=Gender.FEMALE):

        super().__init__(unique_id, model, gender)

        self.had_safety_training = True  # All staff had safety training
        self.knows_exits = True


class EmergencyKnowledge:

    def __init__(self, person):

        self.person = person
        self.had_safety_training = False
        self.knows_exits = False
        self.exit_time = None
        self.exit_location = None
        self.entered_via = self.sample_entrance()  # from which entrance/exit they entered the building
        self.heard_alarm = False
        self.is_evacuating = False
        self.left = False

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

    def sample_entrance(self):
        """
        Samples an entrance/exit for a person.
        :return: random_exit: pos
        """
        exits = self.person.model.destinations[Destination.EXIT]
        random_exit = random.choice(exits)

        return random_exit


class MovementData:

    def __init__(self, gender):

        self.gender = gender

        self.default_walking_speed = self.get_default_speed(Movement.WALKING)
        self.default_running_speed = self.get_default_speed(Movement.RUNNING)
        self.walking_speed = self.default_walking_speed
        self.path_to_current_dest = []  # First element is current position.

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

    def update_speed(self, person):
        """
        This function adjust the speed of an agent depending on how many neighbors an agent has in its 6 dm radius.
        :param person: Person
        """
        nr_of_neighbors = person.get_nr_of_neighbors(agent_type=Person, radius=6)

        if nr_of_neighbors <= 0:
            self.walking_speed = self.default_walking_speed
        elif nr_of_neighbors >= 8:
            self.walking_speed = 1
        else:
            self.walking_speed = self.default_walking_speed / nr_of_neighbors
