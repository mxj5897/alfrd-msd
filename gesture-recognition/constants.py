########################################################################################################################
#
# Constants file.
#
########################################################################################################################

# Location where the facial images used to create embeddings are stored
FACE_DATASET_PATH = 'face_data/'
# Saved location for embedding information
FACE_ENCODINGS_PATH = 'encodings.npy'
AVG_IMG_NUM_PER_USER = 15
# Saved location for the names of users corresponding to user information
FACE_NAMES_PATH = 'names.npy'
# Variables related to Remote Server option. If REMOTE SERVER is true, the terminal running the main application, is not
# the terminal coonnected to the kinect, and images will need to be streamed between the two terminals. Must also select
# whether the terminal is the sensor (kinect terminal) or the compute (main application file) terminal
REMOTE_COMPUTE = False
REMOTE_SENSOR = False
# Pose prediction constants
POSE_MODEL_NAME = 'mobilenet_thin'
POSE_RESIZE_OPTION = "432x368"
POINTS = [0, 1, 2, 3, 4, 5, 6, 7, 15, 16, 18]
RESIZE_OUT_OPTION = 4.0
Pairs = [
    (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
    (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17), (2, 16), (5, 17)
]  # = 19
PairsRender = Pairs[:-2]
# Gesture Classification constants
QUEUE_MAX_SIZE = 15
GESTURE_THRESHOLD = 10
# GUI Related Constants
COUNTDOWN = 6 # Should be 1 more than desired countdown length