from mesa import Agent


class Item(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Desk(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class DeskInteractive(Item):
    """
    That's basically the chair now.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class HelpDesk(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class HelpdeskInteractiveForHelper(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class HelpdeskInteractiveForHelpee(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Office(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Shelf(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ShelfInteractive(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Exit(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitA(Exit):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitB(Exit):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitC(Exit):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Wall(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Obstacle(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class WalkableFloor(Item):
    # useful to note: can spawn people on these spaces
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class OutOfBounds(Item):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Alarm(Agent):

    def __init__(self, unique_id, model, timer=30):

        super().__init__(unique_id, model)

        self.is_activated = False
        self.starting_time = timer
        self.timer = timer

        self.model.schedule.add(self)

    def step(self):

        self.timer -= 1
        if self.timer <= 0:
            self.is_activated = True
            self.model.schedule.remove(self)

