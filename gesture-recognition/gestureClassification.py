import numpy as np
import constants
import logging


classification_logger = logging.getLogger(__name__)
classification_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

classification_logger.addHandler(file_handler)


class gestureClassification():
    gesture_queue = []
    size_limit = constants.QUEUE_MAX_SIZE

    # TODO:: Implement Functions
    def add_to_queue(self, item):
        print("Hello World")

    def delete_from_quue(self):
        print("Hello World")

    def classify_gesture(self):
        print("Hello WOrld")
