########################################################################################################################
#
# Main application with GUI. The GUI will not be used in the final version of the project, but will be helpful for
# debugging.
#
########################################################################################################################

import cv2
import os
from faceRecognition import faceRecognition
from gestureSensor import Sensors
from posePrediction import Poses
from gestureClassification import classification
from kivy.config import Config

Config.set('graphics', 'resizable', 0)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

kv = '''
main:
    BoxLayout:
        orientation: 'vertical'
        padding: root.width * 0.05, root.height * .05
        spacing: '5dp'
        BoxLayout:
            size_hint: [1,.85]
            Image:
                id: image_source
                source: 'foo.png'
        BoxLayout:
            size_hint: [1,.15]
            GridLayout:
                cols: 3
                spacing: '10dp'
                Button:
                    id: status
                    text:'Play'
                    bold: True
                    on_press: root.playPause()
                Button:
                    text: 'Close'
                    bold: True
                    on_press: root.close()
                Button:
                    text: 'Setting'
                    bold: True
                    on_press: root.setting()
'''


class main(BoxLayout):
    ipAddress = None
    port = None
    play = False
    sensor = Sensors()
    pose = Poses()
    faces = faceRecognition()
    classify = classification()
    pose_model = None
    humans_in_environment = 0
    sensor_method = None

    def update(self, sensor):
        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:
            points = self.pose.get_points(self.model,image)

            if points is None:
                pass

            if self.humans_in_environment != len(points):
                face_locations, face_names = self.faces.identify_faces(image)
                points = self.pose.assign_face_to_pose(points, face_locations, face_names)
                self.humans_in_environment = len(points)

            image = self.pose.plot_pose(image, points)

            self.classify.add_to_queue(points)

            cv2.imwrite('foo.png', image)
            self.ids.image_source.reload()

    def playPause(self):
        if self.ids.status.text == "Stop":self.stop()
        else:
            self.ids.status.text = "Stop"
            self.sensor_method = self.sensor.get_method()
            self.pose_model = self.pose.get_model()
            if self.sensor_method is not None:
                Clock.schedule_interval(self.update, 0.1)
            else:
                self.close()

    def closePopup(self, btn):
        self.popup1.dismiss()

    def stop(self):
        self.ids.status.text = "Play"
        self.sensor.__del__()
        Clock.unschedule(self.update)

    def close(self):
        App.get_running_app().stop()
        os.remove("foo.png")

    def setting(self):
        # Update so that users can switch between kinect and camera
        box = GridLayout(cols=2)
        box.add_widget(Label(text="IpAddress: ", bold=True))
        self.st = TextInput(id="serverText")
        box.add_widget(self.st)
        box.add_widget(Label(text="Port: ", bold=True))
        self.pt = TextInput(id="portText")
        box.add_widget(self.pt)
        remote_btn = Button(text="Set", bold=True)
        remote_btn.bind(on_press=self.settingProcess)
        box.add_widget(remote_btn)

        make_embeddings_btn = Button(text="Make Facial Embeddings", bold=True)
        make_embeddings_btn.bind(on_press=self.makeFaceEmbeddings)
        box.add_widget(make_embeddings_btn)

        self.popup = Popup(title='Settings', content=box, size_hint=(.6, .4))
        self.popup.open()

    def makeFaceEmbeddings(self, btn):
        self.disabled = True
        self.faces.make_dataset_embeddings()
        self.disabled = False
        self.popup.dismiss()

    def settingProcess(self, btn):
        try:
            self.ipAddress = self.st.text
            self.port = int(self.pt.text)
        except:
            pass
        self.popup.dismiss()


class videoStreamApp(App):
    def build(self):
        return Builder.load_string(kv)


videoStreamApp().run()



