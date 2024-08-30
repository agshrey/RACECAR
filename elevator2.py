"""
Copyright Harvey Mudd College
MIT License
Fall 2019
Bonus 1B - IMU: Driving in Shapes
"""

################################################################################
# Imports
################################################################################

from curses.ascii import CR
from enum import IntEnum
import sys

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

import cv2 as cv
import numpy as np
import math


################################################################################
# Global variables
################################################################################

rc = racecar_core.create_racecar()

speed = 0
angle = 0

#State machine
class State(IntEnum):
    wall = 0
    line = 1
    wait = 2
    go = 3

cur_state = State.wall

#line following
GREEN = ((60, 50, 50), (80, 255, 255))
RED = ((0, 50, 50), (20, 255, 255))
RED_2 = ((170, 50, 50), (10, 255, 255))
MIN_CONTOUR_AREA = 30
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))
contour_center = 0
contour_area = 0
color = None
potential_colors = [
    ((60, 50, 50), (80, 255, 255), "green"),
    ((90, 100, 100), (110, 255, 255), "blue"),
    ((170, 50, 50), (10, 255, 255), "red")
]


#wall following
left_angle = 0
left_distance = 0
right_angle = 0
right_distance = 0
front_angle = 0
front_distance = 0
LEFT_WINDOW = (-45, -30)
RIGHT_WINDOW = (30, 45)
FRONT_WINDOW = (-10, 10)

#AR
markers = None
color_image = None
################################################################################
# Functions
################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    rc.drive.stop()


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global contour_center
    global contour_area
    global color
    
    global angle
    global speed
    global cur_state

    global left_angle
    global left_distance

    global right_angle
    global right_distance

    global front_angle
    global front_distance

    global markers
    global color_image

    scan = rc.lidar.get_samples()
    left_angle, left_distance = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    right_angle, right_distance = rc_utils.get_lidar_closest_point(scan, RIGHT_WINDOW)
    front_angle, front_distance = rc_utils.get_lidar_closest_point(scan, FRONT_WINDOW)

    color_image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(color_image)
    rc_utils.draw_ar_markers(color_image, markers)

    # update_contours()
    print("contour", contour_center)

    if cur_state == State.line:
        followLine()
    elif cur_state == State.wall:
        followWall()
    elif cur_state == State.go:
        go()
    elif cur_state == State.wait:
        wait()
    
    if cur_state == State.wall and contour_area != 0:
        cur_state = State.line

    if cur_state != State.go:
        if cur_state != State.line:
            if len(markers) != 0:
                markers[0].detect_colors(color_image, potential_colors)
                if markers[0].get_color == "blue" and markers[0].get_id() == 0:
                    cur_state = State.go
                elif markers[0].get_color != "blue" and markers[0].get_id() == 0:
                    cur_state = State.wait
            else:
                cur_state = State.wall
    
            

    print(cur_state)
    rc.drive.set_speed_angle(speed, angle)

def followLine():
    global contour_center
    global contour_area
    global angle
    global speed
    global markers
    global cur_state

    speed = 1
    
    if contour_center is not None:
        scale = 1 / (rc.camera.get_width() / 2)
        error = (contour_center[1] - (rc.camera.get_width() / 2)) * scale
        angle = error
        angle = rc_utils.clamp(angle, -1, 1)

    else:
        if len(markers) != 0:
            markers[0].detect_colors(color_image, potential_colors)
            if markers[0].get_id() == 0 and markers[0].get_color() == "blue":
                cur_state = State.go
            elif markers[0].get_id() == 0 and markers[0].get_color() != "blue":
                cur_state = State.wait
        else:
            angle = 1
            speed = -1

    update_contours()

def followWall():
    global left_angle
    global left_distance
    global right_angle
    global right_distance
    global angle
    global speed

    speed = 1
    angle = rc_utils.clamp((right_distance - left_distance)/50, -1.0, 1.0)

    update_contours()

def update_contours():
    global contour_center
    global contour_area
    global color

    image = rc.camera.get_color_image()
    image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

    if image is None:
        contour_center = None
        contour_area = 0
        color = "none"

    else:
        red_contours = rc_utils.find_contours(image, RED[0], RED[1])
        red_largest_contour = rc_utils.get_largest_contour(red_contours, MIN_CONTOUR_AREA)

        green_contours = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        green_largest_contour = rc_utils.get_largest_contour(green_contours, 5000)

        red_2_contours = rc_utils.find_contours(image, RED_2[0], RED_2[1])
        red_2_largest_contour = rc_utils.get_largest_contour(red_2_contours, MIN_CONTOUR_AREA)

        if red_largest_contour is not None:
            contour_center = rc_utils.get_contour_center(red_largest_contour)
            contour_area = rc_utils.get_contour_area(red_largest_contour)
            color = "red"
        
        elif red_2_largest_contour is not None:
            contour_center = rc_utils.get_contour_center(red_2_largest_contour)
            contour_area = rc_utils.get_contour_area(red_2_largest_contour)
            color = "red_2"

        elif green_largest_contour is not None:
            contour_center = rc_utils.get_contour_center(green_largest_contour)
            contour_area = rc_utils.get_contour_area(green_largest_contour)
            color = "green"
        
        else:
            contour_center = None
            contour_area = 0
            color = "none"

def go():
    global speed
    global angle
    global front_distance
    global cur_state

    print("front distance", front_distance)
    # rc.drive.set_max_speed(0.5)
    speed = 0.8
    angle = 0

    if front_distance < 80:
        speed = 0
    
    if front_distance > 200:
        cur_state = State.wall
        

def wait():
    global speed
    global angle
    global markers
    global cur_state
    global color_image

    speed = 0
    angle = 0

    if len(markers) != 0:
        markers[0].detect_colors(color_image, potential_colors)
        if markers[0].get_id() == 0 and markers[0].get_color() == "blue":
            print("time to go")
            cur_state = State.go



################################################################################
# Do not modify any code beyond this point
################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
