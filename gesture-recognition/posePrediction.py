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

" tf-openpose/tf_pose/"
import logging
import constants
from tf_openpose.tf_pose.estimator import TfPoseEstimator
from tf_openpose.tf_pose.networks import get_graph_path, model_wh


pose_logger = logging.getLogger(__name__)
pose_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

pose_logger.addHandler(file_handler)


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

    def get_points(self, model, image, smooth=False):
        # Makes an inference of the model and optionally applies smoothing. Returns points object of the predicted pose
        try:
            if image is None:
                pose_logger.warning("No image passed into the openpose model")
                return None
            humans = model.infernce(image, resize_to_default=(self.w > 0 and self.h > 0),
                                    upsample_size=constants.RESIZE_OUT_OPTION)

            if smooth:
                #TODO Apply smoothing filter to the human data points
                humans = humans

            return humans
        except:
            pose_logger.warning("Error finding pose points")
            return None

    #TODO:: Change so that the function also graphs the identity of the end user
    def plot_pose(self, image, points):
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

    #TODO:: Consider abstracting this out to a general humans class which has properties:
    # pose, gesture gueue, identity
    def assign_face_to_pose(self,points, face_locations, face_names):
        # This function should only be called when the number of skeletons in the image changes
        # Assumes that that number of skeletons in the frame will always
        # be greater than or equal to the number of faces

        if points == []:
            return points


        for person in points:
            person.identity = lambda: None
            setattr(points.identity)

            for i in range(18):
                if i not in person.body_parts.keys():
                    continue

                target_body_part = person.body_parts[i]
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    if target_body_part.x > left*4 and target_body_part.x < right*4:
                        if target_body_part.y >= bottom*4 and target_body_part.y < top*4:
                            person.identity = name
                            continue
                        else:
                            person.identity = "Unknown"
        return points

