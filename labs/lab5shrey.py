"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 5 - AR Markers
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

from enum import IntEnum
########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here

#STATE MACHINES


class Color(IntEnum):
    RED = 1
    BlUE = 2
    GREEN = 3
class State(IntEnum):
    moveForward = 0
    turnRight = 1
    turnLeft = 2
    followWall = 3
    followLine = 4

cur_state = State.followWall

#RACECAR
speed = 0.0
angle = 0.0
MIN_CONTOUR_AREA = 30

# A crop window for the floor directly in front of the car
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

#LIDAR
left_angle = 0
left_distance = 0
right_angle = 0
right_distance = 0

#COLOR
WHITE = (( 90, 20, 200), (115, 60, 255))
RED = ((170, 50, 50), (10, 255, 255))
GREEN = ((40, 50, 50), (80, 255, 255))
BLUE = ((90, 50, 50), (120, 255, 255))  

contour_center = None
contour_area = 0


########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(">> Lab 5 - AR Markers")


def update():
    global cur_state
    global speed
    global angle
    global counter
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    color_image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(color_image)

    rc_utils.draw_ar_markers(color_image, markers)
    rc.display.show_color_image(color_image)

    # TODO: Turn left if we see a marker with ID 0 and right for ID 1

    # TODO: If we see a marker with ID 199, turn left if the marker faces left and right
    # if the marker faces right

    # TODO: If we see a marker with ID 2, follow the color line which matches the color
    # border surrounding the marker (either blue or red). If neither color is found but
    # we see a green line, follow that instead.

    speed = 1
    
    print(cur_state)
    if len(markers) == 0:
        cur_state = State.followWall
    else:
        marker = markers[0]
        if marker.get_id() == 0:
            cur_state = State.turnLeft
        elif marker.get_id() == 1:
            cur_state = State.turnRight
        elif marker.get_id() == 199:
            if marker.get_orientation() == marker.get_orientation().LEFT:
                cur_state = State.turnLeft
            elif marker.get_orientation() == marker.get_orientation().RIGHT:
                cur_state = State.turnRight
        elif marker.get_id() == 2:
            cur_state = State.followLine
        else:
            cur_state = State.followWall

    if cur_state == State.followWall:
        followWall()
    elif cur_state == State.followLine:
        followLine(marker.get_color())
    elif cur_state == State.turnLeft:
        turnLeft()
    elif cur_state == State.turnRight:
        turnRight()

    rc.drive.set_speed_angle(speed, angle)

def turnRight():
    rc.drive.set_speed_angle(0.8, rc_utils.clamp(rc_utils.remap_range(rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 60, 20) - rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 300, 20), -15, 15, -1, 1), -1, 1))


def turnLeft():
    rc.drive.set_speed_angle(0.8, rc_utils.clamp(rc_utils.remap_range(rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 60, 20) - rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 300, 20), -15, 15, -1, 1), -1, 1))


def followWall():
    rc.drive.set_speed_angle(0.8, rc_utils.clamp(rc_utils.remap_range(rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 60, 20) - rc_utils.get_lidar_average_distance(rc.lidar.get_samples(), 300, 20), -15, 15, -1, 1), -1, 1))

def followLine(color):
    
    global markers
    global cur_state
    global speed
    global angle
    
    # TODO: If we see a marker with ID 2, follow the color line which matches the color
    # border surrounding the marker (either blue or red). If neither color is found but
    # we see a green line, follow that instead.

    image = rc.camera.get_color_image()
    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # TODO (challenge 1): Search for multiple tape colors with a priority order
        # (currently we only search for blue)

        # Crop the image to the floor directly in front of the car
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        # Find all of the blue contours
        blue_contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        red_contours = rc_utils.find_contours(image, RED[0], RED[1])
        green_contours = rc_utils.find_contours(image,GREEN[0], GREEN[1])

        # Select the largest contour
        blue_largest_contour = rc_utils.get_largest_contour(blue_contours, MIN_CONTOUR_AREA)
        red_largest_contour = rc_utils.get_largest_contour(red_contours, MIN_CONTOUR_AREA)
        green_largest_contour = rc_utils.get_largest_contour(green_contours, MIN_CONTOUR_AREA)
    if color == "red":
    elif color == "blue":
    elif color == 
    

def updateContour():
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()
    if image is None:
        contour_center = None
        contour_area = 0
    else:
        contours = rc_utils.find_contours(image, WHITE[0], WHITE[1])
        contour = rc_utils.get_largest_contour(contours, MIN)
        



########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
