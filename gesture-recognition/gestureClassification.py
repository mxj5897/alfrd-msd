########################################################################################################################
#
# Class for handling all task related to gesture classification.
# Each unique user should have their own gesture queue => there need to be as many instances of this class as their are
# end users in the environment
#
########################################################################################################################
import numpy as np
import constants
import logging


classification_logger = logging.getLogger(__name__)
classification_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

classification_logger.addHandler(file_handler)


class classify():
    # Handles all gesutre classification tasks
    # Has attribute gesture_queue, each unique user should have their own gesture queue,
    # Therefore need as many instances of the class as there are users in the main script
    gesture_queue = []

    def add_to_queue(self, item):
        # Takes in an element and adds it to the gesuture queue
        try:
            if len(self.gesture_queue) >= constants.QUEUE_MAX_SIZE:
                self.delete_from_quue()
            self.gesture_queue.append(item)
        except:
            classification_logger.warning("Could not add element to the gesture queue")

    def delete_from_quue(self):
        # Deletes the first element in the gesture queue
        try:
            self.gesture_queue.pop(0)
        except:
            classification_logger.warning("Could not delete element from the gesture queue")

    #TODO:: Implement this function
    def classify_gesture(self):
        # Returns a prediction of the gesture based on the current contents of the queue
        preditction = 1
        return preditction

    def determine_robot_response(self, user, prediction):
        # Returns / Potentially outputs robot response based on user and gesture predition
        return 1
