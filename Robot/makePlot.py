import matplotlib.pyplot as plt 
import numpy as np
import time
import random

def makeScatter(y):
    # x-axis values 
    x = np.arange(0, 9, 1)
    
    # plotting points as a scatter plot 
    plt.scatter(x, y, label="Distance in CM ", color= "blue", s=30)
    plt.ylim([0,150])

    # x-axis label 
    plt.xlabel('Ultrasonic #') 
    # frequency label 
    plt.ylabel('Distance (cm)') 
    # plot title 
    plt.title('Visual of Ultrasonic Feedback') 
    # showing legend 
    plt.legend() 

    # function to show the plot 
    plt.plot()
    plt.draw()
    plt.pause(0.0001)
    plt.clf()

def main():
    for i in range(10):
        y = [random.randrange(10, 100, 1) for _ in range(7)]
        makeScatter(y)
        time.sleep(1)

