


# """
# Copyright MIT and Harvey Mudd College
# MIT License
# Summer 2020

# Lab 3A - Depth Camera Safety Stop
# """

# ########################################################################################
# # Imports
# ########################################################################################

# import sys
# import cv2 as cv
# import numpy as np

# sys.path.insert(0, "../../library")
# import racecar_core
# import racecar_utils as rc_utils

# ########################################################################################
# # Global variables
# ########################################################################################

# rc = racecar_core.create_racecar()

# # Add any global variables here
# from enum import IntEnum
# class State(IntEnum):
#     search = 0
#     ramp = 1
#     obstacle = 2
#     stop = 3

# cur_state = State.search
# ########################################################################################
# # Functions
# ########################################################################################


# def start():
#     """
#     This function is run once every time the start button is pressed
#     """
#     # Have the car begin at a stop
#     rc.drive.stop()

#     # Print start message
#     print(
#         ">> Lab 3A - Depth Camera Safety Stop\n"
#         "\n"
#         "Controls:\n"
#         "    Right trigger = accelerate forward\n"
#         "    Right bumper = override safety stop\n"
#         "    Left trigger = accelerate backward\n"
#         "    Left joystick = turn front wheels\n"
#         "    A button = print current speed and angle\n"
#         "    B button = print the distance at the center of the depth image"
#     )


# def update():
#     """
#     After start() is run, this function is run every frame until the back button
#     is pressed
#     """
#     global cur_state
#     global speed
#     global angle
#     # Use the triggers to control the car's speed
#     # if not (cur_state == State.stop):
#     rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
#     lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
#     speed = rt - lt

#     # Calculate the distance of the object directly in front of the car
#     depth_image = rc.camera.get_depth_image()
    
#     kernel_size = 11
#     blurred_image = cv.GaussianBlur(depth_image, (kernel_size, kernel_size), 0)
#     depth_image_crop = rc_utils.crop(depth_image, (0,0), (rc.camera.get_height()*2//3, rc.camera.get_width()))
#     closest = rc_utils.get_closest_pixel(blurred_image)
#     center_distance = rc_utils.get_depth_image_center_distance(blurred_image)
    

#     # TODO (warmup): Prevent forward movement if the car is about to hit something.
#     # Allow the user to override safety stop by holding the right bumper.
#     # if center_distance < 100:
#     #     print(center_distance)
#     #     speed = 0
#     #     angle = 0
#     if cur_state == State.search:
#         # if center_distance != 0:
#         #     cur_state = State.obstacle
#         if center_distance<50  and center_distance>0:
#             cur_state = State.stop
#         elif center_distance <110:
#             cur_state = State.obstacle
#         elif center_distance == 0 and closest == (0,0):
#             cur_state = State.ramp
#     elif cur_state == State.obstacle:
#         if center_distance < 60:
#             cur_state = State.stop
        
#         speed = 1
#         # speed = rc_utils.remap_range(center_distance, 30, 550, 0, 1)
#         # speed = rc_utils.clamp(speed, -1, 1)
#     elif cur_state == State.ramp:
#         speed = 1

#     elif cur_state == State.stop:
#         speed = 1
#         if center_distance >65 or (closest != (0,0) and center_distance == 0):
#             cur_state = State.search

#     # Use the left joystick to control the angle of the front wheels
#     angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

#     rc.drive.set_speed_angle(speed, angle)

#     # Print the current speed and angle when the A button is held down
#     if rc.controller.is_down(rc.controller.Button.A):
#         print("Speed:", speed, "Angle:", angle)
#         print("distance", center_distance)
#         print("closest", rc_utils.get_closest_pixel(depth_image_crop))
#         print("state", cur_state)

#     # Print the depth image center distance when the B button is held down
#     if rc.controller.is_down(rc.controller.Button.B):
#         print("Center distance:", center_distance)

#     # Display the current depth image
    
#     rc.display.show_depth_image(depth_image_crop)

#     # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
#     # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.
    




#     # TODO (stretch goal): Tune safety stop so that the car is still able to drive up
#     # and down gentle ramps.
#     # Hint: You may need to check distance at multiple points.


# ########################################################################################
# # DO NOT MODIFY: Register start and update and begin execution
# ########################################################################################

# if __name__ == "__main__":
#     rc.set_start_update(start, update, None)
#     rc.go()

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

########################################################################################
# Functions
########################################################################################


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

safety = True
########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    global safety
    # Have the car begin at a stop
    rc.drive.stop()
    safety = True
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
    global safety

    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt

    # Calculate the distance of the object directly in front of the car
    depth_image = rc.camera.get_depth_image()
    depth_image_adjust = (depth_image - 0.01) % 9999
    depth_image_adjust_blur = cv.GaussianBlur(depth_image_adjust, (11,11), 0)
    center_distance = rc_utils.get_depth_image_center_distance(depth_image_adjust_blur)

    # TODO (warmup): Prevent forward movement if the car is about to hit something.
    # Allow the user to override safety stop by holding the right bumper.
    

    if center_distance <= 30 and safety is True:
        speed = -1
        angle = 0
        print(center_distance)
    elif center_distance <= 120 and safety is True:
        speed = 0
        angle = 0
        print(center_distance)

    if rc.controller.is_down(rc.controller.Button.RB):
        safety = False
    else:
        safety = True

    # Use the left joystick to control the angle of the front wheels
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]



    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the depth image center distance when the B button is held down
    if rc.controller.is_down(rc.controller.Button.B):
        print("Center distance:", center_distance)

    # Display the current depth image
    rc.display.show_depth_image(depth_image)

    # TODO (stretch goal): Prevent forward movement if the car is about to drive off a
    # ledge.  ONLY TEST THIS IN THE SIMULATION, DO NOT TEST THIS WITH A REAL CAR.


    # TODO (stretch goal): Tune safety stop so that the car is still able to drive up
    # and down gentle ramps.
    # Hint: You may need to check distance at multiple points.


    rc.drive.set_speed_angle(speed, angle)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################


if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
