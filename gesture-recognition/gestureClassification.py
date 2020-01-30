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
import ast
from fastdtw import fastdtw
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
        # Load in csv files
        with open(path) as file:
            reader = csv.reader(file, delimiter=';')
            file_array = [row for row in reader]
            if path == 'dictionary_labels.csv':
                return file_array
        file_array = [ast.literal_eval(fil_arr[0]) for fil_arr in file_array]
        array = []
        for arr in file_array:
            temp_arr = []
            for i in range(15):
                temp = np.array(list(arr[i][0].items()))
                temp = [tp[1] for tp in temp]
                temp_arr.append(temp)
            array.append(temp_arr)
        return array

    def update_dictionary(self):
        # Upload the contents of the csv files into memory
        try:
            print("dldldl===================================================")
            self.dictionary_gestures = self.read_in_file('dictionary_gestures.csv')
            self.dictionary_labels = self.read_in_file('dictionary_labels.csv')
        except:
            classification_logger.warning('Could not update the dictionary')

    def clear_dictionary(self, btn):
        # Clears dictionary by deleting csv files
        try:
            if os.path.isfile('./dictionary_gestures.csv') and os.path.isfile('./dictionary_labels.csv'):
                os.remove('./dictionary_gestures.csv')
                os.remove('./dictionary_labels.csv')
        except:
            classification_logger.warning('Could not erase dictionary files.')

    def add_to_dictionary(self, gesture, label):
        # Add label and gesture to dictionary to two separate csv files
        try:
            with open('./dictionary_gestures.csv', 'a') as g_file:
                g_writer = csv.writer(g_file, delimiter=';')
                g_writer.writerow([gesture])
            with open('./dictionary_labels.csv', 'a') as l_file:
                l_writer = csv.writer(l_file, delimiter=';')
                l_writer.writerow([label])
        except:
            classification_logger.warning('Could not add element to dictionary')


    def add_to_queue(self, item):
        # Takes in an element and adds it to the gesuture queue
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

            if self.dictionary_gestures is None and self.dictionary_labels is None:
                self.update_dictionary()

            print(np.shape(self.dictionary_gestures))
            for pred, gesture in zip(self.dictionary_labels, self.dictionary_gestures):
                print("Here")
                print(np.shape(self.gesture_queue))
                print(np.shape(gesture))
                distance, path = fastdtw(self.gesture_queue, gesture)
                print(distance)
                if best_distance < distance or best_distance == -1:
                    best_distance = distance
                    prediction = pred

            if best_distance >= constants.GESTURE_THRESHOLD:
                prediction = "Unknown"

            return prediction
        except:
            classification_logger.warning("Could not classify prediction")
            return "Unknown"
