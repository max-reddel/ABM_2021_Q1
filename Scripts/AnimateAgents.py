import math

from mesa import Agent
import random
from Tasks import CompositeTask
from Enums import *
from PathFinding import a_star_search


class Person(Agent):

    def __init__(self, unique_id, model, female_ratio=0.5, adult_ratio=0.7):

        super().__init__(unique_id, model)

        self.assign_gender(female_ratio)
        self.assign_age(adult_ratio)

        self.busy = False

        self.move_data = MovementData(self.gender)
        self.emergency_knowledge = EmergencyKnowledge(self)
        self.current_task = CompositeTask(self, self.model)

    def step(self):
        pass

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

    def scan_environment_for_evacuation(self, agent_type, radius=50):
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
        evacuating_neighbors = [x for x in animate_agents if x.emergency_knowledge.is_evacuating]

        if nr_of_neighbors == 0:
            return 0
        else:
            evacuating_ratio = float(len(evacuating_neighbors) / nr_of_neighbors)
            return evacuating_ratio

    def check_alarm(self):
        if self.model.alarm.is_activated:
            self.emergency_knowledge.is_evacuating = True

    def is_staff_close_by(self, radius=50):
        """
        Return True if at least one staff member is in the proximity with a specific radius. The default radius is 5m.
        :return: Boolean
        """
        if self.get_nr_of_neighbors(agent_type=Staff, radius=radius) > 0:
            return True
        else:
            return False

    def are_visitors_close_by(self, radius=50):
        """
        Return True if at least one staff member is in the proximity with a specific radius. The default radius is 5m.
        :return: Boolean
        """
        if self.get_nr_of_neighbors(agent_type=Visitor, radius=radius) > 0:
            return True
        else:
            return False

    def get_closest_exit(self):

        return self.emergency_knowledge.closest_exit

    def get_closest_exit_from_closest_staff_member(self, radius=50):

        closest_exit = None

        # get all neighbors (including inanimate agents
        all_agents = self.model.grid.get_neighbors(pos=self.pos, moore=True, include_center=False, radius=radius)

        # filter out all inanimate agents
        staff_neighbors = [x for x in all_agents if isinstance(x, Staff)]

        if staff_neighbors:
            closest_staff = staff_neighbors[0]
            closest_exit = closest_staff.get_closest_exit()

        return closest_exit

    def update_exit_information_from_staff(self, radius=50):

        closest_exit = self.get_closest_exit_from_closest_staff_member(radius=radius)

        if closest_exit is not None:

            self.emergency_knowledge.closest_exit = closest_exit

    def set_closest_exit(self, closest_exit):

        self.emergency_knowledge.closest_exit = closest_exit

    def update_exit_information_of_surrounding_visitors(self, radius=50):

        persons = self.get_sourrounding_visitors(radius=radius)
        own_exit = self.emergency_knowledge.closest_exit

        for person in persons:
            if not person.emergency_knowledge.informed_by_staff:
                person.emergency_knowledge.is_evacuating = True
                person.emergency_knowledge.closest_exit = own_exit
                person.emergency_knowledge.informed_by_staff = True

    def get_sourrounding_visitors(self, radius=50):

        # get all neighbors (including inanimate agents
        all_agents = self.model.grid.get_neighbors(pos=self.pos, moore=True, include_center=False, radius=radius)

        # filter out all inanimate agents
        visitor_neighbors = [x for x in all_agents if isinstance(x, Visitor)]

        return visitor_neighbors

    def get_current_speed(self):

        if self.emergency_knowledge.is_evacuating:
            return self.move_data.running_speed
        else:
            return self.move_data.walking_speed

    def assign_gender(self, female_ratio):

        if random.random() <= female_ratio:
            self.gender = Gender.FEMALE
        else:
            self.gender = Gender.MALE

    def assign_age(self, adult_ratio):

        if random.random() <= adult_ratio:
            self.age = Age.ADULT
        else:
            self.age = Age.CHILD


class Visitor(Person):

    def __init__(self, unique_id, model, female_ratio=0.5, adult_ratio=0.7, familiarity=0.1):

        super().__init__(unique_id, model, female_ratio, adult_ratio)

        self.emergency_knowledge.sample_safety_training(probability=familiarity)  # Few visitors had safety training
        self.emergency_knowledge.knows_exits = self.emergency_knowledge.get_knows_exits(probability=0.1)

    def step(self):

        # Adjust speed given how many people are close by
        self.move_data.update_speed(self)

        if self.model.alarm.is_activated and \
                not self.emergency_knowledge.informed_by_staff and \
                self.emergency_knowledge.stopping_time > 0 and \
                not self.emergency_knowledge.had_safety_training:
            self.emergency_knowledge.stopping_time -= 1

        else:

            # Leave immediately when e.g. staff told visitor to leave if you had safety training
            if self.model.alarm.is_activated:
                self.emergency_knowledge.alarm_timer += 1

            # Check whether other persons in proximity are evacuating
            evacuating_ratio = self.scan_environment_for_evacuation(agent_type=Visitor, radius=50)
            if evacuating_ratio >= 0.5 or self.emergency_knowledge.should_leave():
                self.emergency_knowledge.is_evacuating = True

        self.current_task.do()


class Staff(Person):

    def __init__(self, unique_id, model, female_ratio=0.5, adult_ratio=0.7):

        super().__init__(unique_id, model, female_ratio, adult_ratio)

        self.had_safety_training = True  # All staff had safety training
        self.exit_location = None

    def step(self):

        self.move_data.update_speed(self)

        # Super simple version of knowing about the alarm
        if self.model.alarm.is_activated:
            self.emergency_knowledge.is_evacuating = True
        self.current_task.do()


class EmergencyKnowledge:

    def __init__(self, person):

        self.person = person
        self.had_safety_training = False
        self.exit_time = None
        self.exit_location = None
        self.entered_via = self.sample_entrance()  # from which entrance/exit they entered the building
        self.closest_exit = self.entered_via
        self.heard_alarm = False
        self.alarm_timer = 0
        self.alarm_timer_max = 30  # Maximum number of seconds before latest starting to leave the building
        self.stopping_time = 0  # Time to stop a current task in emergency situation
        self.is_evacuating = False
        self.left = False
        self.informed_by_staff = False

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

    def compute_closest_exit(self):
        """
        Return the closest exit.
        :return: closest_exit: Destination.EXIT
        """

        all_exits = self.person.model.destinations[Destination.EXIT]
        grid = self.person.model.grid
        origin = self.person.pos

        path_lengths = [len(a_star_search(grid, origin, x)) for x in all_exits]

        # Get index of shortest path
        idx = path_lengths.index(min(path_lengths))

        closest_exit = all_exits[idx]

        return closest_exit

    def sample_entrance(self):
        """
        Samples an entrance/exit for a person.
        :return: random_exit: pos
        """
        exits = self.person.model.destinations[Destination.EXIT]
        random_exit = random.choice(exits)

        return random_exit

    def should_leave(self):
        return self.alarm_timer >= self.alarm_timer_max


class MovementData:

    def __init__(self, gender):

        self.gender = gender

        self.default_walking_speed = self.get_default_speed(Movement.WALKING)
        self.default_running_speed = self.get_default_speed(Movement.RUNNING)
        self.walking_speed = self.default_walking_speed
        self.running_speed = self.default_running_speed
        self.path_to_current_dest = []  # First element is current position.

    def get_default_speed(self, movement):
        """
        Returns the default speed of a person. I.e., the speed before any adjustments due to crowds or slopes.
        :param movement:    Element of Movement-Enum
        :return:            float, default speed of the person
        """
        # Specifying speeds
        male_dict = {Movement.RUNNING: 1.5,  # original 1.5
                     Movement.WALKING: 1.0}  # original 1.0
        female_dict = {Movement.RUNNING: 1.4,  # original 1.4
                       Movement.WALKING: 0.9}  # origional 0.9
        # male_dict = {Movement.RUNNING: 0.1,  # original 1.5
        #              Movement.WALKING: 0.1}  # original 1.0
        # female_dict = {Movement.RUNNING: 0.1,  # original 1.4
        #                Movement.WALKING: 0.1}  # origional 0.9

        # Read movement-speed from the right dictionary & return it.
        speed = 1.0  # Heads-up: If gender would be sth else than MALE/FEMALE, speed would always be 1.
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
            self.running_speed = self.default_running_speed
        elif nr_of_neighbors >= 8:
            self.walking_speed = 1.0
            self.running_speed = 1.0
        else:
            self.walking_speed = self.default_walking_speed / float(nr_of_neighbors)
            self.walking_speed = self.convert_to_suitable_speed_format(self.walking_speed)
            self.running_speed = self.default_running_speed / float(nr_of_neighbors)
            self.running_speed = self.convert_to_suitable_speed_format(self.running_speed)

    @staticmethod
    def convert_to_suitable_speed_format(val):
        """
        Takes a float and returns it with one digit after the point, ceiled.
        E.g.    0.23 --> 0.3
                1.88 --> 1.9
        :param val: float
        :return: float
        """

        val1 = val * 10
        val2 = math.ceil(val1)
        val3 = val2 / 10

        return val3
