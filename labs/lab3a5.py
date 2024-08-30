"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3A - Depth Camera Safety Stop
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
    search = 0
    obstacle = 1
    ledge = 2
    ramp = 3

cur_state = State.search
speed = 0
angle = 0


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
    print(
        ">> Lab 3A - Depth Camera Safety Stop\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Right bumper = override safety stop\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = print current speed and angle\n"
        "    B button = print the distance at the center of the depth image"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # Use the triggers to control the car's speed
    global cur_state
    global speed
    global angle

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    # depth_image = (depth_image - 0.01) % 10000
    center_distance = rc_utils.get_depth_image_center_distance(depth_image)

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.
    # print("Center distance:", center_distance)

    # Use the left joystick to control the angle of the front wheels


    cropped_image_height = rc.camera.get_height() * 2// 3
    top_left_inclusive = (0, rc.camera.get_width() // 4)
    bottom_right_exclusive = (cropped_image_height, rc.camera.get_width()* 3 // 4 )
    depth_image = rc_utils.crop(depth_image, top_left_inclusive, bottom_right_exclusive)


    closest_y, closest_x = rc_utils.get_closest_pixel(depth_image)
    dist = depth_image[closest_y, closest_x]
    further_y = rc_utils.clamp(closest_y - 30, 0, cropped_image_height)
    further_dist = depth_image[further_y, closest_x]

    print("current_dist:",dist, ":", further_dist)

    
    
    if dist == 0 and further_dist == 0:
        cur_state = State.ramp
    elif dist<50 and further_dist - dist < 5:
        cur_state = State.obstacle
    else:
        cur_state = State.search
    
    if cur_state == State.search or rc.controller.is_down(rc.controller.Button.RB):
        angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
        rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
        lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
        speed = rt - lt  
    elif cur_state == State.obstacle:
        # if rc.physics.get_angular_velocity()[2]>0.01:
        #     speed = -1
        #     angle = 0
        # else:
        #     speed = 0
        #     angle = 0
        speed = rc_utils.remap_range(rc.physics.get_angular_velocity()[2], 0, 1, -1, 0, True)
        if speed< 0:
            speed = 0
        print("obstacle!")
    elif cur_state == State.ramp:
        speed = 1
        angle = 0
    
    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    if rc.controller.is_down(rc.controller.Button.B):
        print("Center distance:", center_distance)

    # Display the current depth image
    

    # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
    # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.
    if further_dist - dist>150:
        speed = -1

    # TODO (stretch goal): Tune safety stop so that the car is still able to drive up
    # and down gentle ramps.
    # Hint: You may need to check distance at multiple points.
    
    rc.display.show_depth_image(depth_image, points=[(closest_y, closest_x), (further_y, closest_x)])

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
