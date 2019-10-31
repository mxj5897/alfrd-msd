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

    def get_model(self):
        try:
            self.w,self.h = model_wh(constants.POSE_RESIZE_OPTION)

            if self.w > 0 and self.h > 0:
                model = TfPoseEstimator(get_graph_path(constants.POSE_MODEL_NAME), target_size=(self.w, self.h), trt_bool=False)
            else:
                model = TfPoseEstimator(get_graph_path(constants.POSE_MODEL_NAME), target_size=(432, 368), trt_bool=False)
            print(model)
            return model
        except:
            pose_logger.fatal("Could not find pose estimation model")
            return None

    def get_points(self, model, image):
        try:
            return model.inference(image, resize_to_default=(self.w > 0 and self.h > 0), upsample_size=constants.RESIZE_OUT_OPTION)
        except:
            pose_logger.warning("Error finding pose points")
            return None

    def plot_pose(self, image, points):
        try:
            return TfPoseEstimator.draw_humans(image, points, imgcopy=False)
        except:
            pose_logger.warning("Error plotting human skeleton")
            return None