########################################################################################################################
#
# Class for performing facial recognition. Will create embeddings for all potential end users and, given an image match
# users find and identify all faces in the image.
#
########################################################################################################################

import face_recognition
import numpy as np
import os
import cv2
import constants
import logging


face_logger = logging.getLogger(__name__)
face_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

face_logger.addHandler(file_handler)

class faceRecognition():

    def create_embedding(self, image):
        load_image = face_recognition.load_image_file(image)
        encoding = face_recognition.face_encodings(load_image)[0]
        return encoding

    def load_user(self, directory):
        faces = list()
        for filename in os.listdir(directory):
            path = directory + filename
            face = self.create_embedding(path)
            faces.append(face)
        return (faces)

    def load_dataset(self, directory):
        x, y = list(), list()

        for subdir in os.listdir(directory):
            path = directory + subdir + '/'

            if not os.path.isdir(path):
                continue

            faces = self.load_user(path)
            labels = [subdir for _ in range(len(faces))]
            x.extend(faces)
            y.extend(labels)
        return x, y

    def make_dataset_embeddings(self, ret):
        try:

            # Need to create new embeddings for users
            encodings, names = self.load_dataset(constants.FACE_DATASET_PATH)

            # Save out facial ecnoding date for future use
            np.save('encodings', encodings)
            np.save('names', names)
            print("Done")
        except:
            face_logger.error('Could not create facial encodings. Check to ensure face dataset is in the correct location')

    def identify_faces(self, image):
        try:
            if os.path.isfile(constants.FACE_ENCODINGS_PATH) and os.path.isfile(constants.FACE_NAMES_PATH):
                known_face_encodings = np.load(constants.FACE_ENCODINGS_PATH)
                known_face_names = np.load(constants.FACE_NAMES_PATH)
            else:
                self.make_dataset_embeddings()
                known_face_encodings = np.load(constants.FACE_ENCODINGS_PATH)
                known_face_names = np.load(constants.FACE_NAMES_PATH)

            small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []

            for face_encodings in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encodings)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encodings)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)

            return(face_locations, face_names)
        except:
            face_logger.error('Error in facial identification process')
        return None

    def draw_faces(self, image, face_locations, face_names):
        try:
            scale_constant = 4
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= scale_constant
                right *= scale_constant
                bottom *= scale_constant
                left *= scale_constant

                cv2.rectangle(image, (left, top), (right, bottom), (0,0,255), 2)

                cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0,0,255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(image, name, (left+6, bottom -6), font, 1.0, (255,255,255),1)
            return image

        except:
            face_logger.error('Could not draw faces')
            return None

    def face_tracking(self):
        # TODO:: Implement object tracking algorithm to be used after the face is initially detected in the image
        print("Hello World")