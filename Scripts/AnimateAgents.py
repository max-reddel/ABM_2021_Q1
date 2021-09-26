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
        self.emergency_knowledge = EmergencyKnowledge()
        self.current_task = CompositeTask(self, self.model)  # CompositeTask object

    def step(self):

        self.current_task.do()


class Visitor(Person):

    def __init__(self, unique_id, model, gender=Gender.FEMALE):

        super().__init__(unique_id, model, gender)

        self.emergency_knowledge.sample_safety_training(probability=0.1)  # Few visitors had safety training
        self.emergency_knowledge.knows_exits = self.emergency_knowledge.get_knows_exits(probability=0.1)


class Staff(Person):

    def __init__(self, unique_id, model, gender=Gender.FEMALE):

        super().__init__(unique_id, model, gender)

        self.had_safety_training = True  # All staff had safety training
        self.knows_exits = True


class EmergencyKnowledge:

    def __init__(self):

        self.had_safety_training = False
        self.knows_exits = False  # knows all exits?
        self.exit_time = None
        self.exit_location = None
        self.heard_alarm = False  # self.model.alarm_rang()  # Later: implement this in model class.
        # Currently: alarm goes off --> all agents hear it. Thus, boolean depends on whether it rang already or not.

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


class MovementData:

    def __init__(self, gender):

        self.gender = gender

        self.default_walking_speed = self.get_default_speed(Movement.WALKING)
        self.default_running_speed = self.get_default_speed(Movement.RUNNING)
        self.entered_via = self.sample_entrance()  # from which entrance/exit they entered the building
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

    def sample_entrance(self):
        """
        Samples an entrance for a person.
        :return:        Enum of possible Entrances/Exits
        """
        entrance = "main entrance"  # Later: create Entrance Enum, actually sample from it
        return entrance
