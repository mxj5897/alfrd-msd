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
# from posePrediction import Poses
from kivy.config import Config

Config.set('graphics', 'resizable', 0)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import socket
from threading import *
from kivy.uix.image import Image
from kivy.cache import Cache
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
    faces = faceRecognition()
    sensor_method = None

    def update(self, sensor):
        image = self.sensor.get_sensor_information(self.sensor_method)

        if image is not None:

            face_locations, face_names = self.faces.identify_faces()
            #TODO Add pose processing algorithms. Make sure to pass in the image before drawing on it
            image = self.faces.draw_faces(image, face_locations, face_names)

            cv2.imwrite('foo.png', image)
            self.ids.image_source.reload()

    def playPause(self):
        if self.ids.status.text == "Stop":self.stop()
        else:
            self.ids.status.text = "Stop"
            self.sensor_method = self.sensor.get_method()
            print(self.sensor_method)
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
        make_embeddings_btn.bind(on_press=self.makeFaceEmbeddings())
        box.add_widget(make_embeddings_btn)

        self.popup = Popup(title='Settings', content=box, size_hint=(.6, .4))
        self.popup.open()

    def makeFaceEmbeddings(self):
        self.disabled = True
        self.faces.make_dataset_embeddings()
        print("Done")
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



