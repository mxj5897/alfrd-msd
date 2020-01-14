########################################################################################################################
#
# Class for handling all task related to gesture classification.
# Each unique user should have their own gesture queue => there need to be as many instances of this class as their are
# end users in the environment
#
########################################################################################################################

import constants
import logging
import os
import csv
from fastdtw import fastdtw
import pandas as pd
import numpy as np



classification_logger = logging.getLogger(__name__)
classification_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

classification_logger.addHandler(file_handler)


class Classify():
    # Handles all gesutre classification tasks
    # Has attribute gesture_queue, each unique user should have their own gesture queue,
    # Therefore need as many instances of the class as there are users in the main script
    gesture_queue = []

    def __init__(self):
        self.gesture_queue = []
        self.dictionary_labels = None
        self.dictionary_gestures = None

    def read_in_file(self, path):
        file_df = pd.read_csv(path)
        file_array = file_df.to_numpy()
        file_array = np.nan_to_num(file_array)

        return file_array

    def update_dictionary(self):
        try:
            self.dictionary_gestures = self.read_in_file('dictionary_gestures.csv')
            self.dictionary_labels = self.read_in_file('dictionary_labels.csv')
        except:
            classification_logger.warning('Could not update the dictionary')

    def clear_dictionary(self):
        try:
            if os.path.isfile('./dictionary_gesture.csv') and os.path.isfile('./dictionary_labels.csv'):
                os.remove('dictionary_gestures.csv')
                os.remove('dictionary_labels.csv')
        except:
            classification_logger.warning('Could not erase dictionary files.')

    def add_to_dictionary(self, gesture, label):
        try:
            with open('./dictionary_gestures.csv') as g_file:
                g_writer = csv.writer(g_file, delimiter=';')
                g_writer.writerow(gesture)
            with open('./dictionary_labels.csv') as l_file:
                l_writer = csv.writer(l_file, delimiter=';')
                l_writer.writerow(gesture)
        except:
            classification_logger.warning('Could not add element to dictionary')


    def add_to_queue(self, item):
        # Takes in an element and adds it to the gesuture queue
        #TODO:: convert from x, y object to 2D time series
        try:
            if len(self.gesture_queue) >= constants.QUEUE_MAX_SIZE:
                self.delete_from_queue()
            self.gesture_queue.append(item)
        except:
            classification_logger.warning("Could not add element to the gesture queue")

    def delete_from_queue(self):
        # Deletes the first element in the gesture queue
        try:
            self.gesture_queue.pop(0)
        except:
            classification_logger.warning("Could not delete element from the gesture queue")

    def classify_gesture(self):
        # Returns a prediction of the gesture based on the current contents of the queue
        try:
            prediction = 'Unkonwn'
            best_distance = -1
            for pred, gesture in zip(self.dictionary_labels, self.dictionary_gestures):
                distance, path = fastdtw(self.gesture_queue, gesture)

                if best_distance < distance or best_distance == -1:
                    best_distance = distance
                    prediction = pred

            if best_distance >= constants.GESTURE_THRESHOLD:
                prediction = "Unknown"

            return prediction
        except:
            classification_logger.warning("Could not classify prediction")
            return "Unknown"
