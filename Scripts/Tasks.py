# from enum import Enum
# from Scripts.AnimateAgents import Visitor, Staff
# import random
#
#
# class CompositeTask:
#
#     def __init__(self, person, model, task_name=None):
#         """
#         :param person: Person: person that holds this composite task
#         :param task_name:
#         """
#
#         if task_name is None:
#             # atm STUDY, should become randomly sampled
#             task_name = VisitorTasks.STUDY
#         else:
#             self.task_name = task_name
#
#         self.person = person
#         self.model = model
#         self.destinations = model.destinations
#         self.remaining_subtasks = self.generate_sub_tasks()
#
#     def generate_sub_tasks(self):
#
#         remaining_subtasks = []
#
#         if isinstance(self.person, Visitor):
#
#             # TODO: Currently hardcoded to STUDY, should generalize to many tasks
#             remaining_subtasks = [Walk(self.person, self.destinations, Destination.DESK), Stay(self.person)]
#
#         return remaining_subtasks
#
#     def do(self):
#         # TODO: continue here #########################################################################################
#         # Check self.remaining_tasks
#         # if current task is not done, continue with it
#         # if it's done, kick it out of the list and continue
#         # probably by calling AnimateAgents/Person/... their behavior
#
#         try:
#             current_subtask = self.remaining_subtasks[0]
#         except:
#             pass
#
#         # If all tasks are done
#         if not self.remaining_subtasks:
#             self.remaining_subtasks = self.generate_sub_tasks()
#
#         # if current subtask should still run
#         elif not current_subtask.is_done():
#             if isinstance(current_subtask, Walk):
#                 self.person.walk()
#             elif isinstance(current_subtask, Stay):
#                 self.person.stay()
#
#             current_subtask.update()
#
#             # remove finished subtask from remaining substasks
#             if current_subtask.is_done():
#                 self.remaining_subtasks = self.remaining_subtasks[1:]
#
#
#
#
#
#
#
# class BasicTaskName(Enum):
#     WALK = 1
#     STAY = 2
#
#
# class Destination(Enum):
#     """
#     This enum contains all kinds of walking destinations.
#     """
#
#     EXIT = 0
#     DESK = 1
#     SHELF = 2
#     HELPDESK = 3
#
#
# class BasicTask:
#
#     def __init__(self, person):
#
#         self.person = person
#         self.type = None
#
#     def is_done(self):
#         pass
#
#     def update(self):
#         pass
#
#
# class Walk(BasicTask):
#
#     def __init__(self, person, destinations, destination_type=None):
#
#         super().__init__(person)
#
#         self.type = BasicTaskName.WALK
#         self.destinations = destinations
#
#         if destination_type is not None:
#             self.destination_type = destination_type
#         else:
#             self.destination_type = Destination.DESK  # TODO: This might be different, dependent on what the destination_type really is
#
#         self.destination = self.get_random_destination()
#
#     def get_random_destination(self):
#         """
#         Returns a random destination as a position (tuple) given the specified destination_type.
#         E.g. if destination_type is STUDY, this functions returns a random chair position.
#         :return: position
#         """
#
#         relevant_destinations = self.destinations[self.destination_type]
#
#         random_destination = random.choice(relevant_destinations)  # Later: Probably rather with some passed seed
#
#         return random_destination
#
#     def is_done(self):
#         """
#         Returns True if the person reached the final destination.
#         :return: boolean
#         """
#
#         return self.person.pos == self.destination
#
#     def update(self):
#         pass
#
#
# class Stay(BasicTask):
#
#     def __init__(self, person, duration=None):
#
#         super().__init__(person)
#         self.type = BasicTaskName.STAY
#
#         if duration is not None:
#             self.remaining_duration = duration
#         else:
#             self.remaining_duration = random.uniform(3, 8)  # TODO: other numbers are needed
#
#     def is_done(self):
#
#         return self.remaining_duration <= 0
#
#     def update(self):
#         self.remaining_duration -= 1
#
# class VisitorTasks(Enum):
#     # TODO: Continue here: Where do I get the destinations from without circular dependencies?
#     STUDY = 1
#     GET_HELP = 2
#     GET_BOOK = 3
#
#
# class StaffTasks(Enum):
#     PROVIDE_HELP = 1
#     WORK_IN_OFFICE = 2
#
#
