########################################################################################################################
#
# Class for performing pose predicition in an image
#
#
########################################################################################################################
import argparse
import time
import sys, os
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
    def __init__(self):
        self.w,self.h = None, None
        self.Pairs = [
            (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
            (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17), (2, 16), (5, 17)
        ]
        self.PairsRender = self.Pairs[:-2]

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
                    ind_point = dict.fromkeys(constants.POINTS)
                    for i in constants.POINTS:
                        if i not in person.body_parts.keys():
                            ind_point[i] = [0,0]
                            continue
                        ind_point[i] = [person.body_parts[i].x, person.body_parts[i].y]
                    points.append(ind_point)
                return points
            else:
                return None
        except:
            pose_logger.warning("Error finding pose points")
            return None

    def plot_faces(self, image, humans,image_h, image_w):
        font = cv2.FONT_HERSHEY_DUPLEX

        image = cv2.putText(image, "Users in Environment", (10, 30), font, 0.5, (0,0,0),1)
        y0, dt = 45, 15
        for i, human in enumerate(humans):
            if 0 in human.current_pose.keys():

                head = [human.current_pose[0][0]*image_w, human.current_pose[0][1]*image_h]
                image = cv2.putText(image, human.identity, (int(head[0]) + 6, int(head[1]) + 6), font, 1.0, (0, 255, 255), 1)
            y = y0 + dt * i
            image = cv2.putText(image, human.identity,(10,y), font, 0.5, (0,0,0),1)
        return image

    def plot_pose(self, image, humans,image_h, image_w):
        # Takes in points object and plots the human skeleton on the input image
        try:
            if image is None:
                pose_logger.warning("No image or points passed in to draw skeletal frame")
                return None
            if humans is None:
                return image
            
            centers = {}
            for human in humans:
                #draw points
                for i in constants.POINTS:
                    if human.current_pose[i] == [0,0]:
                        continue
                    center = (int(human.current_pose[i][0]*image_w+0.5), int(human.current_pose[i][1]*image_h+0.5))
                    centers[i] = center
                    image = cv2.circle(image, center, 2, (0, 0, 255), thickness=20, lineType=8, shift=0)

                for pair in self.PairsRender:
                    if pair[0] not in centers.keys() or pair[1] not in centers.keys():
                        continue

                    image = cv2.line(image, centers[pair[0]], centers[pair[1]], (0,0,255), 3)

            return image
        except:
            pose_logger.warning("Error plotting human skeleton")
            return None

    def assign_face_to_pose(self, points ,humans ,face_locations, face_names, height, width):
        try:
            # Assigns faces and skeletons to human objects
            if points is None or face_locations is None or face_names is None:
                return []
            points_to_add = []
            flag, indices = self.update_human_poses(points, face_locations, face_names, humans, width, height)
            if list(indices.values()) == [] and flag != "add":
                return []
            new_points = [item[0] for item in list(indices.values())]
            new_humans = [item[1] for item in list(indices.values())]

            if flag == "add":
                for point in points:
                    if point not in new_points:
                        points_to_add.append(point)

                humans = self.create_users(points_to_add, face_locations, face_names, new_humans, height, width)
            elif flag == "remove":             
                humans = self.remove_users(new_humans, new_points)
            elif flag == "constant":
                humans = new_humans

            return humans
        except Exception as e:
            pose_logger.warning("Could not create humans object")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return []


    def remove_users(self, humans, points):
        # Deletes users who have left the frame
        for i, human in enumerate(humans):
            if points[i] is None:
                del humans[i]
        
        return humans


    def create_users(self, points, face_locations, face_names, humans, height, width):
        # Adds users who enter the frame
        try:
            
            for person in points:
                human = Humans()
                human.identity = "Unknown"
                human.current_pose = person
                for i in [0,15,16]: # the points on the skeleton corresponding to the face
                    if i not in person.keys():
                        continue

                    target_body_part = person[i]
        
                    for (top, right, bottom, left), name in zip(face_locations, face_names):
                        if target_body_part[0]*width >= left*4 and target_body_part[0]*width <= right*4:
                            if target_body_part[1]*height <= bottom*4 and target_body_part[1]*height >= top*4:
                                human.identity = name

                humans.append(human)
            return humans
        except Exception as e:
            # pose_logger.warning("Could not create humans object")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return []

    def update_human_poses(self, points, face_locs, face_names, humans, width, height):
        # Minimizes the distance between the poses of each human between frames
        # Does not account for overlapping humans in frames
	    #TODO:: Add proximity test to determine how close humans are in environment??
        try:
            if points is None or humans is None:
                return None, {}
            # Index of human points haven't been identified
            pnt_used = {}

            # Set flag
            if  len(points) > len(humans):
                flag = "add"
            elif len(points) < len(humans):
                flag = "remove"
            else:
                flag = "constant"

            # Cost function mapping  humans
            for a, human in enumerate(humans):
                min_dist_cost = 0
       
                pnt_used[a] = [None, human]
                for pnt in points:
                    dist_cost = 0
                    for i in constants.POINTS:
                        if human.current_pose[i] != [0,0] and pnt[i] != [0,0]:
                            dist_cost += ((human.current_pose[i][0] - pnt[i][0]))**2 + ((human.current_pose[i][1] - pnt[i][1]))**2
                            
                        elif(human.current_pose[i] == [0,0] and pnt[i] == [0,0]):
                            dist_cost += 0
                        else:
                            dist_cost += .1
                    
                    if (min_dist_cost == 0 or min_dist_cost > dist_cost) and dist_cost < 1: 
                        min_dist_cost = dist_cost
                        best_pnt = pnt
                        pnt_used[a] = [pnt, human]
                pose_logger.warning(min_dist_cost)
                human.current_pose = best_pnt
            

                # Continuously scan for face identities
                for ind in [0, 15, 16]:
                    if ind not in human.current_pose.keys() or human.identity != "Unknown":
                        continue
                    
                    target_body_part = human.current_pose[ind]

                    for (top, right, bottom, left), name in zip(face_locs, face_names):
                        if target_body_part[0]*width >= left*4 and target_body_part[0]*width <= right*4:
                            if target_body_part[1]*height <= bottom*4 and target_body_part[1]*height >= top*4:
                                human.identity = name

            return flag, pnt_used
        except Exception as e:
            pose_logger.warning("Could not create humans object")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return []
