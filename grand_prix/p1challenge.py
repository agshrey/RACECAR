"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020
Phase 1 Challenge - Cone Slaloming
"""

########################################################################################
# Imports
########################################################################################

import sys
from typing import Tuple
import cv2 as cv
import numpy as np
from numpy.testing._private.utils import jiffies

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils
from enum import IntEnum

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

class State(IntEnum) :
    turn_right = 0 # Go around red cone
    turn_left = 1 # Go around blue cone
    done = 2 # Finish line
    search = 3 # Manual control until we re-aquire
    backup = 4

class Cone(IntEnum) :
    red = 0
    blue = 1

cur_State = State.turn_right
coneVisible = None
coneturn_right = None

# The HSV ranges (min, max)
RED = ((165, 50, 50), (179, 255, 255))
BLUE = ((95, 150, 150), (120, 255, 255))
# FINALS

MIN_CONTOUR_AREA = 600

depthImage = None
colorImage = None
targetCenter = (0,0)
coneCenter = None
speed = 0
angle = 0
counter = 0
coneCounter = 0
distanceToCone = 0

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the star*t button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(">> Phase 1 Challenge: Cone Slaloming")

def findCone():
    global colorImage, depthImage, targetCenter, coneCenter, coneVisible, closestCone
    
    if colorImage is None and depthImage is None:
        coneCenter = None
    else:
        blueContours = rc_utils.find_contours(colorImage, BLUE[0], BLUE[1])
        redContours = rc_utils.find_contours(colorImage, RED[0], RED[1])  
        blueLargestContour = rc_utils.get_largest_contour(blueContours, MIN_CONTOUR_AREA)      
        redLargestContour = rc_utils.get_largest_contour(redContours, MIN_CONTOUR_AREA)

        if blueLargestContour is None : blueArea = 0
        else : blueArea = rc_utils.get_contour_area(blueLargestContour)
        if redLargestContour is None : redArea = 0
        else: redArea = rc_utils.get_contour_area(redLargestContour)

        if blueArea > redArea:
            closestCone = blueLargestContour
            coneVisible = Cone.blue
        else :
            closestCone = redLargestContour
            coneVisible = Cone.red

        coneCenter = rc_utils.get_contour_center(closestCone) # None when redArea, blueArea are 0
        
def calculatetarget():
    global colorImage, depthImage, targetCenter, coneCenter, coneVisible, counter, distanceToCone
    if coneCenter is not None : 
        distanceToCone = depthImage[coneCenter[0]][coneCenter[1]]
        point = (5550/distanceToCone) * 3.25


        pointDirection = 1
        if coneVisible == Cone.blue : pointDirection = -1

        
        targetCenter = (rc_utils.clamp(coneCenter[0], 0, rc.camera.get_height() - 1), rc_utils.clamp(int(rc_utils.clamp(coneCenter[1] + (pointDirection * point), 0, sys.maxsize)), 0, rc.camera.get_width() - 1))

        
def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global colorImage, depthImage, speed, angle, coneCenter, targetCenter, cur_State, closestCone
    colorImage = rc.camera.get_color_image()
    depthImage = rc.camera.get_depth_image()
    
    findCone()
    calculatetarget()

    if cur_State == cur_State.turn_right :
        turn_right()
    if cur_State == cur_State.turn_left :
        turn_left()
    elif cur_State == cur_State.done :
        done()
    elif cur_State == cur_State.search:
        search()

    speed = rc_utils.clamp(speed, -0.95, 0.95)
    print("speed:", speed, "|| angle:", angle)
    rc.drive.set_speed_angle(speed, angle)
    
    if coneCenter is not None:
        rc_utils.draw_contour(colorImage, closestCone)
        rc_utils.draw_circle(colorImage, coneCenter)
    # if targetCenter is not None:
    #     rc_utils.draw_circle(colorImage, targetCenter)

    rc.display.show_color_image(colorImage) 

def turn_right():
    global speed, angle, counter, coneturn_right, coneVisible, cur_State, coneCounter, depthImage, coneCenter
    angle = angleController()
    speed = 1.0

    if counter == 0 :
        coneturn_right = coneVisible
        counter += rc.get_delta_time()
        
    if coneturn_right != coneVisible or coneCenter is None :
        cur_State = State.turn_left
        coneCounter += 1
        counter = 0

def turn_left():
    global speed, angle, counter, coneVisible, cur_State, coneturn_right, distanceToCone, depthImage, coneCenter

    counter += rc.get_delta_time()

    if counter < 0.35 :
        speed = 1.0
        angle = 0.025 if coneturn_right == Cone.blue else -0.025
    elif (counter < 2.35 and coneturn_right == coneVisible) or coneCenter is None:
        speed = 0.6
        angle = 0.8 if coneturn_right == Cone.blue else -0.8
    else :
        if coneturn_right != coneVisible:
            cur_State = State.turn_right
            counter = 0 

def search():
    global speed, angle
    speed = 0.1
    angle = -1

def done(): 
    global speed, angle
    speed = 0
    angle = 0 


def angleController():
    global targetCenter
    k = 0.8
    e = targetCenter[1] - rc.camera.get_width() / 2
    angle =  k * e / (rc.camera.get_width() / 2)
    return rc_utils.clamp(angle, -1, 1)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
