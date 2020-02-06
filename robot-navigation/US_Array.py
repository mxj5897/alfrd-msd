#Libraries
import RPi.GPIO as GPIO
import time
import Robot_Pinout as rpo
import US

class US_Array:
    StartTime0 = 0;
    def __init__(self):
        US_0 = US.Ultrasonic(0, rpo.US0_Trigger, rpo.US0_Echo, 0, 0, 0)
        US_1 = US.Ultrasonic(1, rpo.US1_Trigger, rpo.US1_Echo, 0, 0, 0)
        US_2 = US.Ultrasonic(2, rpo.US2_Trigger, rpo.US2_Echo, 0, 0, 0)
        US_3 = US.Ultrasonic(3, rpo.US3_Trigger, rpo.US3_Echo, 0, 0, 0)
        US_4 = US.Ultrasonic(4, rpo.US4_Trigger, rpo.US4_Echo, 0, 0, 0)
        US_5 = US.Ultrasonic(5, rpo.US5_Trigger, rpo.US5_Echo, 0, 0, 0)
        US_6 = US.Ultrasonic(6, rpo.US6_Trigger, rpo.US6_Echo, 0, 0, 0)
        US_7 = US.Ultrasonic(7, rpo.US7_Trigger, rpo.US7_Echo, 0, 0, 0)
        US_8 = US.Ultrasonic(8, rpo.US8_Trigger, rpo.US8_Echo, 0, 0, 0)
        
        self.arr = (US_0, US_1, US_2, US_3, US_4, US_5, US_6, US_7, US_8)
        self.initalize()
        
    def initalize(self):
        GPIO.setmode(GPIO.BOARD)
        
        # set GPIO direction (IN / OUT) for UltraSonic 0
        GPIO.setup(self.arr[0].trigger, GPIO.OUT)
        GPIO.setup(self.arr[0].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 1
        GPIO.setup(self.arr[1].trigger, GPIO.OUT)
        GPIO.setup(self.arr[1].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 2
        GPIO.setup(self.arr[2].trigger, GPIO.OUT)
        GPIO.setup(self.arr[2].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 3
        GPIO.setup(self.arr[3].trigger, GPIO.OUT)
        GPIO.setup(self.arr[3].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 4
        GPIO.setup(self.arr[4].trigger, GPIO.OUT)
        GPIO.setup(self.arr[4].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 5
        GPIO.setup(self.arr[5].trigger, GPIO.OUT)
        GPIO.setup(self.arr[5].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 6
        GPIO.setup(self.arr[6].trigger, GPIO.OUT)
        GPIO.setup(self.arr[6].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 7
        GPIO.setup(self.arr[7].trigger, GPIO.OUT)
        GPIO.setup(self.arr[7].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # set GPIO direction (IN / OUT) for UltraSonic 8
        GPIO.setup(self.arr[8].trigger, GPIO.OUT)
        GPIO.setup(self.arr[8].echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)