#Libraries
import RPi.GPIO as GPIO
import time

# Ultrasonic Pins
US0_Trigger = 3
US0_Echo    = 5
US1_Trigger = 7
US1_Echo    = 8
US2_Trigger = 10
US2_Echo    = 12
US3_Trigger = 11
US3_Echo    = 13
US4_Trigger = 3
US4_Echo    = 15
US5_Trigger = 7
US5_Echo    = 16
US6_Trigger = 10
US6_Echo    = 18
US7_Trigger = 11
US7_Echo    = 19
US8_Trigger = 3
US8_Echo    = 21

# IR Sensor Pins
IR0 = 23
IR1 = 24
IR2 = 26
IR3 = 29

# Motor Control Pins
M1_IN1 = 31 
M1_IN2 = 32
M1_EN  = 33
M2_IN3 = 35
M2_IN4 = 36
M2_EN  = 37

# Motor Encoder Pins
M1_CHA = 38
M1_CHB = 0 # Ignore for now 
M2_CHA = 40
M2_CHB = 0 # Ignore for now

# LED Pins
LED_Data = 22