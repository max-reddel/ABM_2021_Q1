from mesa import Agent


class Item(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Desk(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class HelpDesk(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Office(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Shelf(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Exit(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Wall(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Obstacle(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
