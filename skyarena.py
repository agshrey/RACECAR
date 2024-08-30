"""
Copyright Harvey Mudd College
MIT License
Spring 2020

Demo RACECAR program
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

sys.path.insert(0, '../../library')
import racecar_core
import racecar_utils as rc_utils
########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Declare any global variables here
left_angle = 0
left_distance = 0
LEFT_WINDOW = (-60,-30)
speed = 0
angle = 0
########################################################################################
# Functions
########################################################################################

def start():
    rc.drive.stop()

    print(">> Grand Prix -- Sky Arena")
    rc.drive.set_max_speed(0.52)

def update():
    global left_angle
    global left_distance
    global angle
    global speed

    scan = rc.lidar.get_samples()
    __, left_distance = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    
    angle = rc_utils.clamp((75-left_distance)/50, -1, 1)
    print("angle:", angle, "left_distance:", left_distance)
    speed = 1
    rc.drive.set_speed_angle(speed, angle)


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
