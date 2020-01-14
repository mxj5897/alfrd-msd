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
        self.current_pose = {
                0 : None,
                1 : None,
                2: None,
                3: None,
                4: None,
                5: None,
                6: None,
                7:  None,
                8:  None,
                9:  None,
                10: None,
            }
        self.sensor =Sensors()

    # TODO:: Implement function, uses kinect depth information to return 3d function.
    def get_user_3d_position(self):
        # Uses kinect 3D information to find users the position of humans in the environment
        return 1
