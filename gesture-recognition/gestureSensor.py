########################################################################################################################
#
# Class for connecting to and extracting features from the gesture recognition sensor. If the remote_servers option is
#  not true, The default will be to establish  a connection with the kinect. Next the algorithm will attem to connect
#  to a camera onboard the device. If the REMOTE_SERVER option is true, the device will attempt to connect to a remote
#  device and stream images from sensors on that device. If no sensor is connected, then a None type object will be
#  returned which will error upstream in the program flow.
#
########################################################################################################################

import cv2
import constants
import freenect
import logging
import numpy as np


sensor_logger = logging.getLogger(__name__)
sensor_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('gestureRecognition.log')
file_handler.setFormatter(formatter)

sensor_logger.addHandler(file_handler)


class Sensors():
    video = None
    method = "unkonwn"

    def get_method(self):
        # Checks to determine what sensor are availble. Returns a string listing the appropriate option
        try:
            if not constants.REMOTE_SENSOR:
                kinect_video = self.get_kinect_video()
                if kinect_video is not None:
                    return "kinect"
                else:
                    self.set_camera(0)
                    camera_video = self.get_camera_video()
                    if camera_video is not None:
                        return "camera"
            else:
                # TODO:: Implement remote server option
                sensor_logger.fatal("No available sensors detected, terminating application")
                return None
        except:
            print(3)
            sensor_logger.fatal('No available sensors detected, terminating application')
            return None

    def get_sensor_information(self, method):
        # Takes in sensor method (string) and returns output for that sensor if it exist
        try:
            sensor_switch = {
                "kinect": self.get_kinect_video,
                "camera": self.get_camera_video
            }
            func = sensor_switch.get(method, lambda: None)

            return func()

        except:
            sensor_logger.fatal('No available sensors detected, terminating application')
            return None


    def get_kinect_depth(self):
        # Returns depth information for kinect sensor
        try:
            return self.convert_kinect_depth(freenect.sync_get_depth()[0])
        except:
            sensor_logger.warning('Not connected to Kinect, No depth information')
            return None

    def get_kinect_video(self,):
        # Returns video information for kinect sensor
        try:
            return self.convert_kinect_video(freenect.sync_get_video()[0])
        except:
            sensor_logger.warning('Not connected to Kinect, No video information.')
            return None


    def convert_kinect_depth(self, depth):
        # Necessary pre-processing for kinect data
        np.clip(depth, 0, 2 ** 10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8)
        return depth

    def convert_kinect_video(self, video):
        # Convert color channels for kinect sensor
        return video[:, :, ::-1]  # RGB -> BGR

    def __del__(self):
        # Release cv2 object
        if self.video is not None:
            self.video.release()

    def set_camera(self, source):
        # Sets the camera for cv2 video capture
        try:
            self.video = cv2.VideoCapture(0)
            if self.video is None:
                sensor_logger.warning('Set Camera - No camera available')
        except:
            sensor_logger.warning("Set Camera - No camera available")


    def get_camera_video(self):
        # Returns image information from a cv2 camera
        try:
            # Convert to jpeg
            if self.video.isOpened():
                success, image = self.video.read()
                # ret, jpeg = cv2.imencode('.jpg', image) # May need for streaming

            return image
        except:
            sensor_logger.warning('Get Camera - No camera available')
        return None

