from mesa import Agent
import random
from enum import Enum
from PathFinding import a_star_search


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
        self.gender = gender
        self.age = random.randint(13, 100)  # only for potential extension

        # Walking related (TODO: create object)
        self.default_walking_speed = self.get_default_speed(Movement.WALKING)
        self.default_running_speed = self.get_default_speed(Movement.RUNNING)
        self.entered_via = self.sample_entrance()  # from which entrance/exit they entered the building

        # This is just an example path
        start = (1, 12)  # upper left corner
        end = (16, 0)  # 4 cells further to the right
        path = a_star_search(self.model.grid, start, end)

        self.path_to_current_dest = path  # First element is current position.
        # Later: get this from pathfinding-dict (also using self.tasks)

        # Evacuation related (TODO: create object)
        self.had_safety_training = False
        self.knows_exits = False  # knows all exits?
        self.exit_time = None
        self.exit_location = None
        self.heard_alarm = False  # self.model.alarm_rang()  # Later: implement this in model class.
        # Currently: alarm goes off --> all agents hear it. Thus, boolean depends on whether it rang already or not.

        self.current_task = []  # CompositeTask object


    def step(self):

        # if task done:             # check this in self.current_task attributes
        #   sample_new_task()
        # continue task

        self.walk()

    def get_default_speed(self, movement):
        """
        Returns the default speed of a person. I.e., the speed before any adjustments due to crowds or slopes.
        :param movement:    Element of Movement-Enum
        :return:            float, default speed of the person
        """
        # Specifying speeds
        male_dict = {Movement.RUNNING: 0.1,  # orig: 1.5
                     Movement.WALKING: 0.1}  # orig; 1.0
        female_dict = {Movement.RUNNING: 1.4,
                       Movement.WALKING: 0.9}

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

    def walk(self):
        """
        Makes the agent walk. By moving it from its current position, into the direction of their current destination,
        with its speed being adjusted to whether it is an emergency (i.e., adjusted the Movement mode)
        and the amount of people nearby.

        Disclaimer: Currently still basic version. Only walking into right direction.

        :return:    nothing?
        """


        # while len(self.path_to_current_dest) >1:
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
        # print(f'self.path_to_current_dest = {self.path_to_current_dest}')
        # print(f'Agent wants to walk to {new_pos}')
        self.model.grid.move_agent(agent=self, pos=new_pos)

        # print(f"Agent walked to position: {new_pos}")





    # def adjust_speed(self):





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
