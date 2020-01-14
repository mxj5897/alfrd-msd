########################################################################################################################
#
# Class for handling the Batcave response to the robot
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
        pass

    # TODO:: Check with Soren and Nate about what responses they want. This may need to be its own class.
    def determine_robot_response(self, user, prediction):
        # Returns / Potentially outputs robot response based on user and gesture predition
        return 1