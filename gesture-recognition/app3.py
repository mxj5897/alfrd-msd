########################################################################################################################
#
# Main application with GUI. The GUI will not be used in the final version of the project, but will be helpful for
# debugging.
#
########################################################################################################################

# For Will
RUNNING_IN_PYCHARM = False

import cv2
import os
import csv
import shutil
import constants
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
from kivy.uix.widget import  Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
aux_info = False

class AddGesturePopUp(BoxLayout):
    def __init__( self, **kwargs ):
        super(AddGesturePopUp, self).__init__(**kwargs)
        self.pose = Poses()
        self.classify = Classify()
        self.sensor = Sensors()
        self.temp_queue = []
        self.sensor_method = None
        self.pose_model = None

    def addGesture(self):
        # Determines save gesture button behavior
        self.classify.add_to_dictionary(self.temp_queue, self.ids.gestureLabel.text)

    def start_recording(self):
        # Determines start recording button behavior
        if self.ids.start_recording.text == "Stop Recording":
            self.ids.start_recording.text = "Start Recording"
            self.sensor.__del__()
            Clock.unschedule(self.update_recording)
        else:
            self.temp_queue = []
            self.ids.start_recording.text = "Stop Recording"
            self.pose_model = self.pose.get_model()
            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()

            if self.sensor_method is not None:
                Clock.schedule_interval(self.update_recording, 0.1)
            else:
                self.dismiss()

    def update_recording(self, btn):
        # Main loop for the adding gesture
        # Determines key points and saves them to the temp queue
        if len(self.temp_queue) >= constants.QUEUE_MAX_SIZE:
            return False
        
        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            points = self.pose.get_points(self.pose_model,image)

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
        #self.aux_info = False
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
        box = BoxLayout(orientation='vertical')
        label = Label(text=helpInfo)
        box.add_widget(label)
        cancel_btn = Button(text='Close', bold=True)
        cancel_btn.bind(on_press=self.closePopup1)
        box.add_widget(cancel_btn)

        self.popup1 = Popup(title='Help Menu', content=box, size_hint=(.6,.4))
        self.popup1.open()

    def gestureList(self):
        # Displays popup of the list of available gestures from
        # dictionary_labels.csv file
        box = GridLayout(cols=2)
        with open('dictionary_labels.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                text_box = Label(text=row)
                box.add_widget(text_box)

        close_btn = Button(text='Close', bold=True)
        close_btn.bind(on_press=self.closePopup1)
        box.add_widget(close_btn)

        self.popup1 = Popup(title='Gesture List', content=box, size_hint=(.6,.4))
        self.popup1.open()

    # def switchSensor(self, btn):
    #     # Switches sensor
    #     self.sensor_method = self.sensor.switch_method(self.sensor_method)

    def displayInfo(self):
        # Displays pose information
        if self.ids.aux_info.text == "Display Auxilary Info: False":
            self.ids.aux_info.text = 'Display Auxilary Info: True'
            aux_info = True
        else:
            self.ids.aux_info.text = 'Display Auxilary Info: False'
            aux_info = False

    def closePopup1(self, btn):
        # Closes secondary popup
        self.popup1.dismiss()


class gestureWidget(Widget):
    # Main App Widget
    def __init__( self, **kwargs ):
        super(gestureWidget, self).__init__(**kwargs)

        self.ipAddress = None
        self.port = None
        self.play = False
        self.skip = False
        self.sensor = Sensors()
        self.pose = Poses()
        self.faces = faceRecognition()
        self.classify = Classify()
        self.pose_model = None
        self.humans_in_environment = 0
        self.sensor_method = None
        self.aux_info = False
        self.humans = []

    def update(self, sensor):
        # Main loop of the code - finds individuals, and identifies gestures
        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            points = self.pose.get_points(self.pose_model,image)

            if points is not None:

                if self.skip:
                    face_locations, face_names = self.faces.identify_faces(image)
                    self.humans = self.pose.assign_face_to_pose(points, face_locations, face_names)
                    self.humans_in_environment = len(points)
                    self.skip = not self.skip


                # # Get user information if their is a change in the number of humans
                # # in the environment
                # if self.humans_in_environment != len(points):
                #     face_locations, face_names = self.faces.identify_faces(image)
                #     self.humans = self.pose.assign_face_to_pose(points, face_locations, face_names)
                #     self.humans_in_environment = len(points)
                # else:
                    # # Update the poses of each individual human in frame
                    # self.humans = self.pose.update_human_poses(points, self.humans)

                # Only display pose info if option selected in settings
                #if aux_info:
                if False:
                    image = self.pose.plot_pose(image, self.humans) # Plot all pose info
                image = self.pose.plot_faces(image, self.humans) # Just plot identities

                for i in range(self.humans_in_environment):
                    self.humans[i].classify.add_to_queue(self.humans[i].current_pose)
                    self.humans[i].prediction = self.humans[i].classify.classify_gesture()

                #Print Out prediction / calls to robot.py

            cv2.imwrite('foo.png', image)
            self.ids.image_source.reload()

    def playPause(self):
        # Defines behavior for play / pause button
        if self.ids.status.text == "Stop":
            self.ids.status.text = "Play"
            self.sensor.__del__()
            Clock.unschedule(self.update)
        else:
            self.ids.status.text = "Stop"
            self.pose_model = self.pose.get_model()
            if self.sensor_method is None:
                self.sensor_method = self.sensor.get_method()

            if self.sensor_method is not None:
                Clock.schedule_interval(self.update, 0.1)
            else:
                self.close()

    def close(self):
        # close app
        App.get_running_app().stop()
        if os.path.isfile('foo.png'):
            os.remove("foo.png")
        shutil.copy('foo1.png', 'foo.png')

    def setting(self):
        # Display settings popup window
        settings = SettingsPopUp()
        self.popup = Popup(title='Settings', content=settings, size_hint=(.6, .4))
        self.popup.open()

    def displayInfo(self,btn):
        self.aux_info = not self.aux_info
        self.closePopup(btn)

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
