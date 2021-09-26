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


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class Movement(Enum):
    RUNNING = 1
    WALKING = 2
    STANDING = 3


class VisitorTasks(Enum):
    STUDY = 1
    GET_HELP = 2
    GET_BOOK = 3


class StaffTasks(Enum):
    PROVIDE_HELP = 1
    WORK_IN_OFFICE = 2
