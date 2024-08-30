"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3C - Depth Camera Wall Parking
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

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here
from enum import IntEnum
class State (IntEnum):
    move = 0
    back = 1
    stop = 2

cur_state = State.move

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
    print(">> Lab 3C - Depth Camera Wall Parking")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 20 cm away from the closest wall with the car directly facing
    # the wall
    global cur_state

    


    depth_image = rc.camera.get_depth_image()
    depth_image = rc_utils.crop(depth_image, (0,0), (rc.camera.get_height() // 2, rc.camera.get_width()))
    # depth_image = rc_utils.crop(depth_image, (0,0), (rc.camera.get_height() // 2, rc.camera.get_width()))
    depth_image = (depth_image - 0.01) % 10000
    closest_pixel = rc_utils.get_closest_pixel(depth_image)

    dist = depth_image[closest_pixel[0], closest_pixel[1]]

    # left_x = rc_utils.clamp(closest_pixel[1] - 40, 0, rc.camera.get_width() - 1)
    # right_x = rc_utils.clamp(closest_pixel[1] + 40, 0, rc.camera.get_width() - 1)

    # left_distance = depth_image[y, left_x]
    # right_distance = depth_image[y, right_x]

    print(dist)
    print(closest_pixel)
    print("angle_centered", abs(closest_pixel[1]-rc.camera.get_width()//2))

    # def angle_controller():
    #     kP = 1.4
    #     angle = 0
        
    #     if depth_image is not None : 
    #         error = closest_pixel[1] - rc.camera.get_width() / 2
    #         angle = kP * error / (rc.camera.get_width() / 2)
    #     return rc_utils.clamp(angle, -1, 1)

    if cur_state == State.move:
        # if closest_pixel[1] > 300 or closest_pixel[1]<200:
        #     angle = rc_utils.remap_range(closest_pixel[1], 0, rc.camera.get_width(), -1, 1, True)
        # else:
        #     angle = 0
        angle = rc_utils.remap_range(closest_pixel[1], 0, rc.camera.get_width(), -1, 1)
        # multiplier = rc_utils.remap_range(dist, 20, 150, 3, 1)
        # new_angle = rc_utils.clamp(angle * multiplier, -1, 1)

        speed = rc_utils.remap_range(dist, 20, 100, 0, 0.4, True)
        if dist<40 and abs(closest_pixel[1]-rc.camera.get_width()//2)>250:
            cur_state = State.back
        elif dist<21:
            cur_state = State.stop
    elif cur_state == State.back:
        speed = rc_utils.remap_range(dist, 20, 100, -0.4, 0, True)
        angle = -rc_utils.remap_range(closest_pixel[1], 0, rc.camera.get_width(), -1, 1)
        if dist > 100:
            cur_state = State.move

    elif cur_state == State.stop:
        speed = 0
        angle = 0
        if dist>21:
            cur_state = State.move
        elif dist<21:
            cur_state= State.back
    print(cur_state)
    rc.drive.set_speed_angle(speed, angle)
    rc.display.show_depth_image(depth_image, points=[closest_pixel])

    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)
        print("dist", dist)
    


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
