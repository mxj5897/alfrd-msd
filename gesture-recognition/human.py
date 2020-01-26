########################################################################################################################
#
# Container for multiple properties:
#   Identity
#   Gesture Queue
#   Pose
#
########################################################################################################################
from gestureClassification import Classify
from gestureSensor import Sensors

class Humans():
    def __init__(self):
        self.identity = None
        self.prediction = None
        self.classify = Classify()
        self.current_pose = None


    # TODO:: Implement function, uses kinect depth information to return 3d function.
    def get_user_3d_position(self):
        # Uses kinect 3D information to find users the position of humans in the environment
        return 1
