from enum import Enum
from Scripts.AnimateAgents import Visitor, Staff


class CompositeTask:
    # Same for each instance
    class VisitorTasks(Enum):
        STUDY = 1
        GET_HELP = 2
        GET_BOOK = 3

    class StaffTasks(Enum):
        PROVIDE_HELP = 1
        WORK_IN_OFFICE = 2

    # class BasicTasks(Enum):  # TODO: Not sure whether this works. --> functions below
    #     WALK = 1  # TODO: Needs DESTINATION attribute/parameter/sth
    #     STAY = 2  # TODO: Needs TICK attribute/parameter/sth
    #     # CHECK_ENV_PEOPLE_LEAVING = 3  # For evacuation decision of Visitor
    #     # CHECK_ENV_EVERYONE_LEFT = 4   # For evacuation procedure of Staff

    # # Mapping component-tasks to basic sub-tasks
    # subtasks_visitor = {VisitorTasks.STUDY: [],
    #                     VisitorTasks.GET_HELP: [],
    #                     VisitorTasks.GET_BOOK: []}
    #
    # subtasks_staff = {StaffTasks.PROVIDE_HELP: [],
    #                   StaffTasks.WORK_IN_OFFICE: []}

    # Mapping component-tasks to basic sub-tasks
    subtasks_visitor = {"study": [self.walk(tableX), self.stay(50)],  # TODO: Doesn't like '.self'. Use (enum, param) instead?
                        "study_": [("walk", location), ("stay", duration)],  # location: InanimateAgent.Table, duration: int
                        "get help": [],  # TODO: need to sample location and duration
                        "get book": []}

    subtasks_staff = {"provide help": [],
                      "work in office": []}

    # Can differ for different instances
    def __init__(self, task_name, person):
        self.task_name = task_name
        self.remaining_subtasks = []
        self.fill_subtasks(task_name, person)
        self.task_done_at_tick = 100

    def fill_subtasks(self, task_name, person):
        if person is isinstance(Visitor):
            self.remaining_subtasks = self.subtasks_visitor[task_name]
        elif person is isinstance(Staff):
            self.remaining_subtasks = self.subtasks_staff[task_name]
        else:
            print("The agent is not a Visitor, nor Staff. Please make sure they are.")


    # Basic task functions
    def walk(self, location):
        pass

    def stay(self, duration):
        pass
