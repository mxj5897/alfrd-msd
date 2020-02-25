########################################################################################################################
#
# Constants file.
#
########################################################################################################################

# Face Recognition Constants
FACE_DATASET_PATH = 'face_data/'
GESTURE_DATASET_PATH = 'gesture_data/'
FACE_ENCODINGS_PATH = FACE_DATASET_PATH+'encodings.npy'
FACE_NAMES_PATH = FACE_DATASET_PATH+'names.npy'
AVG_IMG_NUM_PER_USER = 15

# Pose Prediction constants
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
GESTURE_DATASET_PATH = 'gesture_data/'
GESTURE_DICTIONARY = GESTURE_DATASET_PATH + 'dictionary_gestures.csv'
GESTURE_LABELS = GESTURE_DATASET_PATH + 'dictionary_labels.csv'
QUEUE_MAX_SIZE = 15
GESTURE_THRESHOLD = 10

# GUI Related Constants
COUNTDOWN = 6 # Should be 1 more than desired countdown length
ASSETS_PATH = './assets/'
IMAGE_PATH = ASSETS_PATH + 'images/'