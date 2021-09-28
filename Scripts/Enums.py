from enum import Enum


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
    EXITA = 4
    EXITB = 5
    EXITC = 6


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class Movement(Enum):
    RUNNING = 1
    WALKING = 2
    STANDING = 3


class VisitorTasks(Enum):
    """
    The values represent the stopping times for a task in an emergency situation.
    """
    STUDY = 20
    GET_HELP = 0
    GET_BOOK = 25
    EVACUATE = 0


class StaffTasks(Enum):
    PROVIDE_HELP = 1
    WORK_IN_OFFICE = 2
    EVACUATE = 3


class Age(Enum):

    CHILD = 0
    ADULT = 1
