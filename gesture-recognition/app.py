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
from gestureClassification import Classify
from kivy.config import Config

Config.set('graphics', 'resizable', 0)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import  Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty


class AddGesturePopUp(BoxLayout):
    def __init__( self, **kwargs ):
        super(AddGesturePopUp, self).__init__(**kwargs)
        self.pose = Poses()
        self.classify = Classify()
        self.sensor = Sensors()
        self.temp_queue = []
        self.Count = 6
        self.sensor_method = None
        self.pose_model = None

    def addGesture(self):
        # Determines save gesture button behavior
        #TODO:: Sanitize inputs
        self.classify.add_to_dictionary([self.temp_queue], self.ids.gestureLabel.text)

    def set_count(self, btn):
        font = cv2.FONT_HERSHEY_SIMPLEX
        if self.Count > 0:
            self.Count = self.Count - 1
            image = cv2.imread('temp1.png')
            height, width = image.shape[:2]
            image = cv2.putText(image, str(self.Count), (int(width/2)-20, int(height/2)), font, 7, (22, 22,205), 10, cv2.LINE_AA)
            cv2.imwrite('temp.png', image)
            self.ids.add_source.reload()
        else:
            Clock.schedule_interval(self.update_recording, 0.1)
            return False

    def start_recording(self):
        # Determines start recording button behavior
        if self.ids.start_recording.text == "Stop Recording":
            self.ids.start_recording.text = "Start Recording"
            self.ids.start_recording.background_color = [1,1,1,1]
            self.sensor.__del__()
            if os.path.isfile('temp.png'):
                os.remove('temp.png')
            shutil.copy('temp1.png', 'temp.png')
            self.ids.add_source.reload()
            Clock.unschedule(self.update_recording)
        else:
            self.temp_queue = []
            self.ids.start_recording.text = "Stop Recording"
            self.ids.start_recording.background_color = [0,1,1,1]
            self.pose_model = self.pose.get_model()
            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()

            if self.sensor_method is not None:
                Clock.schedule_interval(self.set_count, 1)
            else:
                self.dismiss()

    def update_recording(self, btn):
        # Main loop for the adding gesture
        # Determines key points and saves them to the temp queue
        if len(self.temp_queue) >= constants.QUEUE_MAX_SIZE:
            self.ids.start_recording.background_color = [1,1,1,1]
            if os.path.isfile('temp.png'):
                os.remove('temp.png')
            shutil.copy('temp1.png', 'temp.png')
            return False

        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            im_height, im_width = image.shape[:2]
            points = self.pose.get_points(self.pose_model,image)

            # plot points for user feedback
            humans = self.pose.assign_face_to_pose(points, [], [])
            image = self.pose.plot_pose(image,humans, im_height, im_width)

            if points is not None:
                self.temp_queue.append(points)

            cv2.imwrite('temp.png', image)
            self.ids.add_source.reload()


class SettingsPopUp(BoxLayout):
    # Defines Windows Popup
    def __init__(self, **kwargs):
        super(SettingsPopUp, self).__init__(**kwargs)
        self.faces = faceRecognition()
        self.sensor = Sensors()
        self.classify = Classify()
        self.gesture = None
        self.index = 0
        self.sensor_method = None

    def makeFaceEmbeddings(self):
        # Creates facial embeddings from ./dataset
        self.disabled = True
        self.faces.make_dataset_embeddings()
        self.disabled = False
        self.closePopup()

    def displayHelp(self):
        # Displays popup of the help page using help.txt file
        with open('./helpPage.txt', 'r') as file:
            helpInfo = file.read()
        scroll = ScrollView()
        box = GridLayout(cols=1)
        label = Label(text=helpInfo)
        box.add_widget(label)
        cancel_btn = Button(text='Close', bold=True, size_hint=(1,.2))
        cancel_btn.bind(on_press=self.closePopup1)
        box.add_widget(cancel_btn)
        scroll.add_widget(box)

        self.popup1 = Popup(title='Help Menu', content=scroll, size_hint=(.8,.8))
        self.popup1.open()

    def gestureList(self):
        # Displays popup of the list of available gestures from
        # dictionary_labels.csv file
        if os.path.isfile('dictionary_labels.csv'):
            box = GridLayout(cols=2)
            with open('dictionary_labels.csv') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    text_box = Label(text=row[0])
                    box.add_widget(text_box)
                    play_btn = Button(text='Play', bold=True, id=str(i))
                    play_btn.bind(on_press=self.playBackGesture)
                    box.add_widget(play_btn)

            clear_btn = Button(text='Clear', bold=True)
            clear_btn.bind(on_press=self.classify.clear_dictionary)
            box.add_widget(clear_btn)
            close_btn = Button(text='Close', bold=True)
            close_btn.bind(on_press=self.closePopup1)
            box.add_widget(close_btn)

            self.popup1 = Popup(title='Gesture List', content=box, size_hint=(.6,.4))
            self.popup1.open()
        else:
            print("Please add gesture to dictionary")

    # def switchSensor(self, btn):
    #     # Switches sensor
    #     self.sensor_method = self.sensor.switch_method(self.sensor_method)

    def playBackGesture(self, btn):
        # Gets gesture from dictionary and schedules dictionary function
        if not os.path.isfile('dictionary_gestures.csv'):
            return

        with open('dictionary_gestures.csv') as file:
            reader = csv.reader(file, delimiter=';')
            self.gesture=[row for idx, row in enumerate(reader) if idx == int(btn.id)]
            self.gesture = ast.literal_eval(self.gesture[0][0])

        # Open popup
        blank_image = np.zeros((480,480,3), np.uint8)
        cv2.imwrite('playback.png', blank_image)

        box = BoxLayout(orientation='vertical')
        self.Img = Image(id='playback', source='playback.png')
        box.add_widget(self.Img)
        self.popup2 = Popup(title='Playback Gesture', content=box,size_hint=(.8,.8))
        self.popup2.open()

        # Play Video
        Clock.schedule_interval(self.replay_gestures, .5)

    def replay_gestures(self, btn):
        # Loops and replays gesture (Revise)
        centers = {}
        if self.index <= (len(self.gesture)-2):
            image = np.zeros((480,480,3), np.uint8)
            for i in range(18):
                if i not in self.gesture[self.index][0].keys():
                    continue
                center = (int(self.gesture[self.index][0][i][0]*480), int(self.gesture[self.index][0][i][1]*480))
                centers[i] = center
                image = cv2.circle(image, center, 2, (0, 0, 255), thickness=20, lineType=8, shift=0)

            for pair in constants.PairsRender:
                if pair[0] not in self.gesture[self.index][0].keys() or pair[1] not in self.gesture[self.index][0].keys():
                    continue

                image = cv2.line(image, centers[pair[0]], centers[pair[1]], (0,0,255), 3)
            cv2.imwrite('playback.png', image)

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

    def closePopup1(self, btn):
        # Closes secondary popup
        self.popup1.dismiss()


class gestureWidget(Widget):
    # Main App Widget
    def __init__( self, **kwargs ):
        super(gestureWidget, self).__init__(**kwargs)

        #self.ipAddress = None
        #self.port = None
        self.play = False
        self.sensor = Sensors()
        self.pose = Poses()
        self.faces = faceRecognition()
        self.classify = Classify()
        self.pose_model = self.pose.get_model()
        self.humans_in_environment = 0
        self.sensor_method = None #self.sensor.get_method()
        self.aux_info = False
        self.humans = []
        self.settings = SettingsPopUp()

        # resets image
        if os.path.isfile('foo.png'):
            os.remove("foo.png")
        shutil.copy('foo1.png', 'foo.png')

    def update(self, sensor):
        # Main loop of the code - finds individuals, and identifies gestures
        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            points = self.pose.get_points(self.pose_model,image)

            if points is not None:
                im_height, im_width = image.shape[:2]

                # Get identities if change in the number of humans (points) frame
                if self.humans_in_environment != len(points):
                   face_locations, face_names = self.faces.identify_faces(image)
                   self.humans = self.pose.assign_face_to_pose(points, face_locations, face_names)
                   self.humans_in_environment = len(points)
                else:
                # Update the poses of each individual human in frame
                    self.humans = self.pose.update_human_poses(points, self.humans)

                # Plot user identities and (optional) poses
                image = self.pose.plot_faces(image, self.humans, im_height, im_width)
                if self.settings.ids.aux_info.text == 'Display Auxilary Info: True':
                    image = self.pose.plot_pose(image, self.humans, im_height, im_width)

                # Update each respective queue and classify gestures
                for human in self.humans:
                    if human.identity == "Unknown":
                         continue

                    human.classify.add_to_queue(human.current_pose.items())
                    # self.humans[i].prediction = self.humans[i].classify.classify_gesture()
                    #TODO:: Add printout / popup of valid prediction
                    #TODO:: Calls to Robot.py

            cv2.imwrite('foo.png', image)
            self.ids.image_source.reload()

    def playPause(self):
        # Defines behavior for play / pause button
        if self.ids.status.text == "Stop":
            self.ids.status.text = "Play"
            self.ids.status.background_color = [1,1,1,1]
            self.sensor.__del__()
            Clock.unschedule(self.update)
        else:
            self.ids.status.text = "Stop"
            self.ids.status.background_color = [0,1,1,1]
            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()

            if self.sensor_method is not None:
                Clock.schedule_interval(self.update, 0.1)
            else:
                #TODO:: Write popup for error message
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
