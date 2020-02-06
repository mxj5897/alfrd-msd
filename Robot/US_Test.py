#Libraries
import RPi.GPIO as GPIO
import time
import US_Array as UA
import makePlot

#GPIO.setmode(GPIO.BOARD)

if __name__ == '__main__':
    GPIO.setwarnings(False)
    try:
        usArr = UA.US_Array()
        while True:
            distArr = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(len(usArr.arr)-2): # TODO: GET RID OF -2 WHEN WE CONNECT ALL ULTRASONICS (7 AND 8)
                usArr.arr[i].GetDistance()
                distArr[i] = usArr.arr[i].dist
                print("US", i, ": distance", distArr[i])
                time.sleep(0.05)
                
            makePlot.makeScatter(distArr)
            
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

