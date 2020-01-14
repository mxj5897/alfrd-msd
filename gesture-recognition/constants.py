########################################################################################################################
#
# Constants file.
#
########################################################################################################################

# Location where the facial images used to create embeddings are stored
FACE_DATASET_PATH = 'dataset/'
# Saved location for embedding information
FACE_ENCODINGS_PATH = 'encodings.npy'
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
# Gesture Classification constants
QUEUE_MAX_SIZE = 50
GESTURE_THRESHOLD = 10
