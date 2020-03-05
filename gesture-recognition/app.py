########################################################################################################################
#
# Main application with GUI.
#
########################################################################################################################

import cv2
import os
import csv
import time
import ast
import shutil
import constants
import numpy as np
from faceRecognition import faceRecognition
from gestureSensor import Sensors
from posePrediction import Poses
from kivy.core.window import Window

from gestureClassification import Classify
from kivy.config import Config

# Config.set('graphics', 'resizable', 0)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty

# TODO:: Sanitize all text inputs

class AutoCaptureFacesPopup(BoxLayout):
    
    # Automatically adds users to the set of recognized users
    def __init__(self, **kwargs):
        super(AutoCaptureFacesPopup, self).__init__(**kwargs)
        self.faces = faceRecognition()
        self.sensor = Sensors()
        self.sensor_method = self.sensor.get_method()
        self.img_count = 0
        self.counter = 0
        self.interval = 8
        self.image = None
        self.instrDict = {
            0 : "up",
            2 : "up and to the right",
            4 : "right",
            6 : "down and to the right",
            8 : "down",
            10 : "down and to the left",
            12 : "left",
            14 : "up and to the left",
        }
        if self.sensor_method is not None:
            Clock.schedule_interval(self.liveFeed, 0.1)
        else:
            message = MessagePopup(str("Not connected to sensor"))
            message.open()

    def liveFeed(self, btn):
        image = self.sensor.get_sensor_information(self.sensor_method)
        if image is not None:               
            cv2.imwrite(constants.IMAGE_PATH+'addUser.png', image)
            self.ids.addUser.reload()
        
    def start_recording(self):
        # Starts the recording process and adds folderfor user
        if self.ids.start_recording.text == "Stop Recording":
            self.ids.start_recording.text = "Start Recording"
            self.ids.start_recording.background_color = [1,1,1,1]
        else:
            # Set some button properties
            if self.ids.addUserLabel.text == "": # requires user name
                message = MessagePopup(str("Please add user name"))
                message.open()
            else:
                # check if there is already a folder with user images
                if os.path.exists(constants.FACE_DATASET_PATH+self.ids.addUserLabel.text):
                    message = MessagePopup(str("User with that name already exist. \n Please enter a different name"))
                    message.open()
                else:
                    self.ids.start_recording.text = "Stop Recording"
                    self.ids.start_recording.disabled = True
                    self.ids.start_recording.background_color = [0,1,1,1]

                    # creates directory to store user photos
                    os.makedirs( constants.FACE_DATASET_PATH+self.ids.addUserLabel.text)

                    if self.sensor_method is None:
                        self.sensor_method = self.sensor.get_method()

                    if self.sensor_method is not None:
                        Clock.unschedule(self.liveFeed)
                        Clock.schedule_interval(self.autoCaptureFace, 0.1)
                    else:
                        message = MessagePopup(str("Not connected to sensor"))
                        message.open()

    def autoCaptureFace(self, btn):
        # Captures and writes facial files to disk
        if self.img_count >= constants.AVG_IMG_NUM_PER_USER:
            self.img_count = 0
            self.ids.addUserIntr.text = "Done taking photos - creating user embeddings"
            self.ids.start_recording.background_color = [1,1,1,1]
            self.faces.make_dataset_embeddings()
            message = MessagePopup(str("Done adding new users"))
            message.open()
            return False

        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:

            face_locations = self.faces.find_faces(image)
            face_names = ['Unknown'] * len(face_locations) # required for draw_faces function
            disp = self.faces.draw_faces(image, face_locations, face_names)
         
            if self.counter == 0:
                self.ids.addUserIntr.text = "Tilt head " + self.instrDict[self.img_count] + ": 3 "
            elif self.counter  == self.interval:
                self.ids.addUserIntr.text = "Tilt head " + self.instrDict[self.img_count] + ": 2 "
            elif self.counter  == self.interval*2:
                self.ids.addUserIntr.text = "Tilt head " + self.instrDict[self.img_count] + ": 1 "
            elif self.counter  == self.interval*3:
                self.ids.addUserIntr.text = "Tilt head " + self.instrDict[self.img_count]
            elif self.counter  == self.interval*3+3:
                cv2.imwrite(constants.FACE_DATASET_PATH+self.ids.addUserLabel.text+'/'+self.ids.addUserLabel.text+str(self.img_count)+'.png', image)
                cv2.imwrite(constants.FACE_DATASET_PATH+self.ids.addUserLabel.text+'/'+self.ids.addUserLabel.text+str(self.img_count+1)+'.png', image)
                self.img_count += 2
                self.counter = -1
               
            cv2.imwrite(constants.IMAGE_PATH+'addUser.png', disp)
            self.ids.addUser.reload()
            self.counter += 1


class AddGesturePopUp(BoxLayout):
    # Adds gesture to gesture dictionary
    def __init__( self, **kwargs ):
        super(AddGesturePopUp, self).__init__(**kwargs)
        self.pose = Poses()
        self.classify = Classify()
        self.sensor = Sensors()
        self.temp_queue = []
        self.Count = constants.COUNTDOWN
        self.sensor_method = self.sensor.get_method()
        self.pose_model = None

        if self.sensor_method is not None:
            Clock.schedule_interval(self.liveFeed, 0.1)
        else:
            message = MessagePopup(str("Not connected to sensor"))
            message.open()
        
    def liveFeed(self, btn):
        image = self.sensor.get_sensor_information(self.sensor_method)
        if image is not None:               
            cv2.imwrite(constants.IMAGE_PATH+'temp.png', image)
            self.ids.add_source.reload()

    def addGesture(self):
        # Determines save gesture button behavior
        #TODO:: Sanitize inputs
        self.classify.add_to_dictionary([self.temp_queue], self.ids.gestureLabel.text)

    def set_count(self, btn):
        # Sets and displays the countdown
        font = cv2.FONT_HERSHEY_SIMPLEX
        if self.Count > 0:
            self.Count = self.Count - 1
            image = cv2.imread(constants.IMAGE_PATH+'temp1.png')
            height, width = image.shape[:2]
            image = cv2.putText(image, str(self.Count), (int(width/2)-30, int(height/2)), font, 7, (22, 22,205), 10, cv2.LINE_AA)
            cv2.imwrite( constants.IMAGE_PATH+'temp.png', image)
            self.ids.add_source.reload()
        else:
            Clock.schedule_interval(self.update_recording, 0.1)
            self.Count = constants.COUNTDOWN
            return False

    def start_recording(self):
        # Determines start recording button behavior
        if self.ids.start_recording.text == "Stop Recording":
            self.ids.start_recording.text = "Start Recording"
            self.ids.start_recording.background_color = [1,1,1,1]
            self.sensor.__del__()
            self.ids.add_source.reload()
            # Clock.unschedule(self.update_recording)
        else:
            self.temp_queue = []
            self.ids.start_recording.text = "Stop Recording"
            self.ids.start_recording.disabled = True
            self.ids.start_recording.background_color = [0,1,1,1]
            self.pose_model = self.pose.get_model()

            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()
            if self.sensor_method is not None:
                Clock.unschedule(self.liveFeed)
                Clock.schedule_interval(self.set_count, 1)
            else:
                message = MessagePopup(str("Not connected to the sensor"))
                message.open()
                self.ids.start_recording.disabled = False
                self.ids.start_recording.background_color = [1,1,1,1]

    def update_recording(self, btn):
        # Main loop for the adding gesture
        # Determines key points and saves them to the temp queue
        if len(self.temp_queue) >= constants.QUEUE_MAX_SIZE:
            self.ids.start_recording.background_color = [1,1,1,1]
            self.ids.start_recording.disabled = False
            Clock.schedule_interval(self.liveFeed, 0.1)
            return False

        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            im_height, im_width = image.shape[:2]
            points = self.pose.get_points(self.pose_model,image)

            # plot points for user feedback
            humans = self.pose.assign_face_to_pose(points, [], [], im_height, im_width)
            image = self.pose.plot_pose(image,humans, im_height, im_width)

            if points is not None:
                self.temp_queue.append(points)

            cv2.imwrite(constants.IMAGE_PATH+'temp.png', image)
            self.ids.add_source.reload()

class helpMenu(ScrollView):
    # Defines help menu
    text = StringProperty('')

class MessagePopup(Popup):
    # Defines Windows Popup
    errorMess = StringProperty()

    def __init__(self, stri, **kwargs):
        super(MessagePopup, self).__init__(**kwargs)
        self.errorMess = stri

    def build(self):
        return MessagePopup

class SettingsPopUp(BoxLayout):
    # Defines Windows Popup
    def __init__(self, **kwargs):
        super(SettingsPopUp, self).__init__(**kwargs)
        self.faces = faceRecognition()
        self.sensor = Sensors()
        self.classify = Classify()
        self.gesture = None
        self.index = 0
        self.skip = True
        self.sensor_method = None
        self.faceCount = 0

    def makeFaceEmbeddings(self):
        # Creates facial embeddings from ./dataset
        self.disabled = True
        self.faces.make_dataset_embeddings()
        self.disabled = False
        message = MessagePopup(str("Done adding new users"))
        message.open()

    def displayHelp(self):
        # Displays popup of the help page using help.txt file
        with open(constants.ASSETS_PATH+'helpPage.txt', 'r') as file:
            helpInfo = file.read()

        scroll = helpMenu(text=helpInfo)
        self.popup1 = Popup(title='Help Menu', content=scroll, size_hint=(.8,.8))
        self.popup1.open()

    def autoFaceEmbeddings(self):
        box = AutoCaptureFacesPopup()
        self.popup1 = Popup(title='Add Gesture', content=box, size_hint=(.8,.8))
        self.popup1.open()

    def userlist(self):
        # Displays list of users that the system should recognize
        if os.path.isfile(constants.FACE_DATASET_PATH+'names.npy'):
            faces_names = np.load(constants.FACE_DATASET_PATH+'names.npy')

            box = GridLayout(cols=3)
            for i, name in enumerate(faces_names):
                if i == 0 or faces_names[i] != faces_names[i-1]:
                    text_box = Label(text=name)
                    box.add_widget(text_box)
                    view_btn = Button(text='View User', bold=True, id=name)
                    view_btn.bind(on_press=self.viewUser)
                    box.add_widget(view_btn)
                    clear_btn = Button(text="Clear", bold=True, id=name)
                    clear_btn.bind(on_press=self.clearUser)
                    box.add_widget(clear_btn)

            close_btn = Button(text='Close', bold=True)
            close_btn.bind(on_press=self.closePopup1)
            box.add_widget(close_btn)

            self.popup1 = Popup(title='User List', content=box, size_hint=(.6,.4))
            self.popup1.open()

    def viewUser(self, btn):
        # Creates popup window of the user
        box = BoxLayout(orientation='vertical')
        dirPath = constants.FACE_DATASET_PATH+btn.id+'/'
        if os.path.exists(dirPath) and os.path.isdir(dirPath):
            for filename in os.listdir(dirPath):
                image_name = constants.FACE_DATASET_PATH+btn.id+'/'+filename
                self.Img = Image(id='User', source=image_name)
                break

            box.add_widget(self.Img)
            self.popup2 = Popup(title='User: ' + btn.id, content=box,size_hint=(.8,.8))
            self.popup2.open()

    def clearUser(self, btn):
        faces_encodings = np.load(constants.FACE_DATASET_PATH+'encodings.npy')
        faces_names = np.load(constants.FACE_DATASET_PATH+'names.npy')

        indices = []
        for i, name in  enumerate(faces_names):
            if name == btn.id:
                indices.append(i)

        faces_encodings = np.delete(faces_encodings, indices)
        faces_names = np.delete(faces_names, indices)
        
        np.save(constants.FACE_DATASET_PATH+'encodings', faces_encodings)
        np.save(constants.FACE_DATASET_PATH+'names', faces_names)

        dirPath = constants.FACE_DATASET_PATH+btn.id+'/'
        if os.path.exists(dirPath) and os.path.isdir(dirPath):
            shutil.rmtree(dirPath)

        self.closePopup1(btn)
        self.userlist()

    def gestureList(self):
        # Displays popup of the list of available gestures from dictionary_labels.csv file
        # Dynamic widget defined in python not kv
        if os.path.isfile(constants.GESTURE_LABELS):
            box = GridLayout(cols=3)
            with open(constants.GESTURE_LABELS) as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    text_box = Label(text=row[0])
                    box.add_widget(text_box)
                    play_btn = Button(text='Play', bold=True, id=str(i))
                    play_btn.bind(on_press=self.playBackGesture)
                    box.add_widget(play_btn)
                    clear_btn = Button(text="Clear", bold=True, id="clear"+str(i))
                    clear_btn.bind(on_press=self.clearGesture)
                    box.add_widget(clear_btn)

            close_btn = Button(text='Close', bold=True)
            close_btn.bind(on_press=self.closePopup1)
            box.add_widget(close_btn)

            self.popup1 = Popup(title='Gesture List', content=box, size_hint=(.6,.4))
            self.popup1.open()
        else:
            message = MessagePopup(str("No gestures in dictionary. \n Please add gesture to dictionary"))
            message.open()

    def clearGesture(self, btn):
        if not os.path.isfile(constants.GESTURE_DICTIONARY) or not os.path.isfile(constants.GESTURE_DICTIONARY):
            return

        self.clearFromCSV(btn.id[-1], constants.GESTURE_DICTIONARY)
        self.clearFromCSV(btn.id[-1], constants.GESTURE_LABELS)

        self.closePopup1(btn)
        self.gestureList()

    def clearFromCSV(self, id_val, fileName):
        lines = list()        
        with open(fileName, 'r') as g_file:
            g_reader = csv.reader(g_file, delimiter=';')
            for i,row in enumerate(g_reader):
                if int(i) != int(id_val):
                    lines.append(row)

        with open(fileName, 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)

    def playBackGesture(self, btn):
        # Gets gesture from dictionary and schedules dictionary function
        if not os.path.isfile(constants.GESTURE_DICTIONARY):
            return

        with open(constants.GESTURE_DICTIONARY) as file:
            reader = csv.reader(file, delimiter=';')
            self.gesture=[row for idx, row in enumerate(reader) if idx == int(btn.id)]
            self.gesture = ast.literal_eval(self.gesture[0][0])[0]

        # Open popup
        blank_image = np.zeros((480,480,3), np.uint8)
        cv2.imwrite(constants.IMAGE_PATH+'playback.png', blank_image)

        box = BoxLayout(orientation='vertical')
        self.Img = Image(id='playback', source=constants.IMAGE_PATH+'playback.png')
        box.add_widget(self.Img)
        self.popup2 = Popup(title='Playback Gesture', content=box,size_hint=(.8,.8))
        self.popup2.open()

        # Play Video
        Clock.schedule_interval(self.replay_gestures, .5)

    def replay_gestures(self, btn):
        # Loops and replays gesture (Revise)
        centers = {}
        point_ordering = {
        0:"Nose", 1:"Neck", 2:"R. Shoulder", 3:"R. Elbow",
        4:"R. Wrist", 5:"L. Shoulder", 6:"L. Elbow",  7:"L. Wrist",
        15: "R. Eye",16: "L. Eye", 17: "R. Ear", 18: "L. Ear"}


        if self.index <= (len(self.gesture)-2):
            image = cv2.imread('./images/empty_room.jpg')
            im_h, im_w = image.shape[:2]

            # Setup image
            font = cv2.FONT_HERSHEY_DUPLEX
            image = cv2.putText(image, 'Right', (10, 30), font, 0.5, (0,0,0), 1)
            image = cv2.putText(image, 'Left', (im_w-50, 30), font, 0.5, (0,0,0), 1)

            # Plot the points
            for i in range(18):
                if i not in self.gesture[self.index][0].keys():
                    continue
                if int(self.gesture[self.index][0][i][0]*im_w) == 0 or int(self.gesture[self.index][0][i][1]*im_w) == 0:
                    continue
                center = (int(self.gesture[self.index][0][i][0]*(im_w)), int(self.gesture[self.index][0][i][1]*(im_h)))
                centers[i] = center
                image = cv2.circle(image, center, 2, (0, 0, 0), thickness=20, lineType=8, shift=0)

            # Plot the connections between points
            for pair in constants.PairsRender:
                if pair[0] not in centers.keys() or pair[1] not in centers.keys():
                    continue
                image = cv2.line(image, centers[pair[0]], centers[pair[1]], (0,0,0), 3)

            # Plot labels. Needs to be added last for visualization. 
            for i in centers.keys():
                image = cv2.putText(image, point_ordering[i], (centers[i][0]+10, centers[i][1]-10), font, 0.3, (0,0,255), 1)

            cv2.imwrite(constants.IMAGE_PATH+'playback.png', image)

            self.Img.reload()
            self.index += 1
        else:
            self.index = 0
            self.popup2.dismiss()
            return False

    def displayInfo(self):
        # Displays pose information
        if self.ids.aux_info.text == "Display Auxilary Info: False":
            self.ids.aux_info.text = 'Display Auxilary Info: True'
            self.ids.aux_info.background_color = [0, 1, 1, 1]
        else:
            self.ids.aux_info.text = 'Display Auxilary Info: False'
            self.ids.aux_info.background_color = [1, 1, 1, 1]
    
    def recordSession(self):
        # Record Session
        if self.ids.record_session.text == "Record Session: False":
            self.ids.record_session.text = 'Record Session: True'
            self.ids.record_session.background_color = [0, 1, 1, 1]
        else:
            self.ids.record_session.text = 'Record Session: False'
            self.ids.record_session.background_color = [1, 1, 1, 1]

    def closePopup1(self, btn):
        # Closes secondary popup
        self.popup1.dismiss()


class gestureWidget(Widget):
    # Main App Widget
    def __init__( self, **kwargs ):
        super(gestureWidget, self).__init__(**kwargs)

        self.play = False
        self.sensor = Sensors()
        self.pose = Poses()
        self.faces = faceRecognition()
        self.classify = Classify()
        self.pose_model = self.pose.get_model()
        self.humans_in_environment = 0
        self.sensor_method = None #self.sensor.get_method()
        self.aux_info = False
        self.skip = True
        self.face_locations = None
        self.face_names = None
        self.humans = []
        self.settings = SettingsPopUp()
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.VideoWriter = None

        # # resets image
        if os.path.isfile(constants.IMAGE_PATH+'foo.png') and os.path.isfile(constants.IMAGE_PATH+'foo1.png'):
            os.remove(constants.IMAGE_PATH+"foo.png")
            shutil.copy(constants.IMAGE_PATH+'foo1.png', constants.IMAGE_PATH+'foo.png')

    def update(self, sensor):
        # Main loop of the code - finds individuals, and identifies gestures
        # image = self.sensor.get_sensor_information(self.sensor_method)
        # image = cv2.imread(constants.IMAGE_PATH + 'two_people.jpg') # This works
        ret, image = self.cap.read()
        if image is not None:
            points = self.pose.get_points(self.pose_model,image)
            # print(points)
            if self.skip:
                self.face_locations, self.face_names = self.faces.identify_faces(image)
            self.skip = not self.skip

            if points is not None and self.face_names is not None and self.face_locations is not None:
                im_height, im_width = image.shape[:2]
      
                # Assigns identities and skeletons to human object
                self.humans = self.pose.assign_face_to_pose(points, self.humans, self.face_locations, self.face_names, im_height, im_width)
                if self.humans is not None:
                    # Plot user identities and (optional) poses
                    image = self.pose.plot_faces(image, self.humans, im_height, im_width)
                    if self.settings.ids.aux_info.text == 'Display Auxilary Info: True':
                        image = self.pose.plot_pose(image, self.humans, im_height, im_width)

                    # Update each respective queue and classify gestures
                    for human in self.humans:
                        if human.identity == "Unknown":
                             continue

                        # human.classify.add_to_queue(list(human.current_pose.items()))

                        # human.prediction = human.classify.classify_gesture()
                        # if human.prediction != "Unknown":
                        #     message = MessagePopup(str("Prediction is" + human.prediction))
                        #     message.open()
                        #TODO:: Calls to Robot.py
                        
            cv2.imwrite(constants.IMAGE_PATH+'foo.png', image) 
            self.ids.image_source.reload()

            if self.settings.ids.record_session.text == 'Display Auxilary Info: True':
                self.VideoWriter.write(image)

    def playPause(self):
        # Defines behavior for play / pause button

        if self.ids.status.text == "Stop":
            self.ids.status.text = "Play"
            self.ids.status.background_color = [1,1,1,1]
            self.sensor.__del__()
            self.sensor_method = None
            self.VideoWriter.release()
            Clock.unschedule(self.update)
        else:
            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()
            
            if self.sensor_method is not None:
                self.VideoWriter = cv2.VideoWriter('./tests/output.avi', self.fourcc, 5.0, (640,480))
                self.cap = cv2.VideoCapture('test_vid.mp4')
                self.ids.status.text = "Stop"
                self.ids.status.background_color = [0,1,1,1]
                self.skip = True
                Clock.schedule_interval(self.update, 0.1)
            else:
                #TODO:: Write popup for error message
                errorBox = MessagePopup(str("Could not find available sensor"))
                errorBox.open()
                print("Could not find available sensor")

    def close(self):
        # close app
        App.get_running_app().stop()

    def setting(self):
        # Display settings popup window
        self.settings = SettingsPopUp()
        self.popup = Popup(title='Settings', content=self.settings, size_hint=(.6, .4))
        self.popup.open()

    def addGesturePopup(self):
        # display addGesture popup window
        addGesture = AddGesturePopUp()
        self.popup = Popup(title='Add Gesture', content=addGesture, size_hint=(.6, .6))
        self.popup.open()

class gestureApp(App):
    def build(self):
        return gestureWidget()


if __name__ =='__main__':
    gestureApp().run()
