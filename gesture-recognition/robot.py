########################################################################################################################
#
# Class for handling Batcave (terminal) - robot (raspberry pi) interactions
#
########################################################################################################################

import logging

robot_logger = logging.getLogger(__name__)
robot_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

robot_logger.addHandler(file_handler)


class Robot():

    def __init__(self):
        # TODO:: Interface this with the Navigation System to get all possible actions
        # these will be in the form of color mappings
        possible_actions = ["Red", "Blue"]
        self.action_mapping = dict.fromkeys(possible_actions)
    

    def set_mapping(self, temp_mappings):
        # Sets the action mapping
        if temp_mappings is None:
            return None

        for key, val in temp_mappings.items():
            if key not in self.action_mapping.keys():
                continue

            self.action_mapping[key] = val

        return 1
    
    def determine_robot_response(self, user, prediction):
        # Returns / Potentially outputs robot response based on user and gesture predition
        action = [val for key, val in self.action_mapping.items() if val == prediction]

        # TODO:: send action to robot / raspberry pi (planned to do over wifi)