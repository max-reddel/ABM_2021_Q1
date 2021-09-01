from mesa import Agent


class Person(Agent):

    def __init__(self, unique_id, model, gender):
        super().__init__(unique_id, model)
        self.gender = gender
        # and more to follow

    def step(self):
        pass


class Visitor(Person):
    pass


class Staff(Person):
    pass
