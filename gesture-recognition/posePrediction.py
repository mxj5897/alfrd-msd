########################################################################################################################
#
# Class for performing pose predicition in an image
#
#
########################################################################################################################
import argparse
import time

import cv2
import numpy as np
from human import Humans
import logging
import constants
from human import Humans
from pose.tf_pose.estimator import TfPoseEstimator
from pose.tf_pose.networks import get_graph_path, model_wh


pose_logger = logging.getLogger(__name__)
pose_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

pose_logger.addHandler(file_handler)
# Mapping of points returned by openpose
#  point_ordering = {
#     0:"Nose", 1:"Neck", 2:"RShoulder", 3:"RElbow",
#     4:"RWrist", 5:"LShoulder", 6:"LElbow",  7:"LWrist",
#     8:"MidHip", 9: "RHip", 10: "RKnee", 11: "RAnkle",
#     12: "LHip", 3: "LKnee", 14: "LAnkle", 15: "REye",
#     16: "LEye", 17: "REar", 18: "LEar", 19: "LBigToe", 20: "LSmallToe",
#     21: "LHeel", 22: "RBigToe", 23: "RSmallToe", 24: "RHeel", 25: "Background"}

class Poses():
    w,h = None, None
    CocoPairs = [
        (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
        (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17), (2, 16), (5, 17)
    ]  # = 19
    CocoPairsRender = CocoPairs[:-2]

    # Colors for plotting the skeletons on frame
    CocoColors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
                  [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255],
                  [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]

    def get_model(self):
        # Returns the appropriate model used for pose detection. For realtime use "mobilenet_thin"
        try:
            self.w,self.h = model_wh(constants.POSE_RESIZE_OPTION)

            if self.w > 0 and self.h > 0:
                model = TfPoseEstimator(get_graph_path(constants.POSE_MODEL_NAME),
                                        target_size=(self.w, self.h), trt_bool=False)
            else:
                model = TfPoseEstimator(get_graph_path(constants.POSE_MODEL_NAME),
                                        target_size=(432, 368), trt_bool=False)
            return model
        except:
            pose_logger.fatal("Could not find pose estimation model")
            return None

    def get_points(self, model, image):
        # Makes an inference of the model. Returns points object of the predicted pose
        try:
            if image is None:
                pose_logger.warning("No image passed into the openpose model")
                return None
            people = model.inference(image, resize_to_default=(self.w > 0 and self.h > 0),
                                 upsample_size=constants.RESIZE_OUT_OPTION)
            points = []

            if people is not None:
                for person in people:
             
                    for i in constants.POINTS:
                        if i not in person.body_parts.keys():
                            continue
                        points.append([person.body_parts[i].x, person.body_parts[i].y])

                return points
            else:
                return None
        except:
            pose_logger.warning("Error finding pose points")
            return None

    def plot_faces(self, image, humans):
        identities = [human.identity for human in humans]
        heads = [[human.current_pose[:][0].x, human.current_pose[:][0].y] for human in humans]
        font = cv2.FONT_HERSHEY_DUPLEX

        for iden, head in zip(identities, heads):
            cv2.putText(image, iden, (head[0] + 6, head[1] + 6), font, 1.0, (0, 255, 255), 1)

        return image

    def plot_pose(self, image, points):
        #TODO:: Change so that it uses the human object
        # Takes in points object and plots the human skeleton on the input image
        try:
            if image is None or points is None:
                pose_logger.warning("No image or points passed in to draw skeletal frame")
                return None

            image_h, image_w = image.shape[:2]
            centers = {}
            for point in points:
                #draw points
                for i in range(18):
                    if i not in point.body_parts.key():
                        continue

                    body_part = point.body_parts[i]
                    center = (int(body_part.x*image_w+0.5), int(body_part.y*image_h+0.5))
                    centers[i] = center
                    cv2.circle(image, center, 2, self.CocoColors[i], thickness=3, lineType=8, shift=0)

                for pair_order, pair in enumerate(self.CocoPairsRender):
                    if pair[0] not in point.body_parts.keys() or pair[1] not in point.body_parts.keys():
                        continue

                    cv2.line(image, centers[pair[0]], centers[pair[1]], self.CocoColors[pair_order], 3)

            return image
        except:
            pose_logger.warning("Error plotting human skeleton")
            return None

    def assign_face_to_pose(self,points, face_locations, face_names):
        # This function should only be called when the number of skeletons in the image changes
        # Assumes that that number of skeletons in the frame will always
        # be greater than or equal to the number of faces

        if points == []:
            return points

        humans = []
        for person in points:
            human = Humans()
            human.current_pose = person
            # Change so that only looking for the face
            for i in range(18):
                if i not in person.body_parts.keys():
                    continue

                target_body_part = person.body_parts[i]
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    if target_body_part.x > left*4 and target_body_part.x < right*4:
                        if target_body_part.y >= bottom*4 and target_body_part.y < top*4:
                            human.identity = name
                            continue
                        else:
                            human.identity = "Unknown"

                humans.append(human)
        # return humans
        return humans

    # Note think that the best way to do this may be to have human 1 always correspond to the
    # leftmost human, => update function is no longer going to be on change in the human count
    #TODO:: Implement this function
    def update_human_poses(self, points, humans):
        pass
