"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 2A - Color Image Line Following
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################
from enum import IntEnum
class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3



rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# A crop window for the floor directly in front of the car
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

# Colors, stored as a pair (hsv_min, hsv_max)
BLUE = ((90, 50, 50), (120, 255, 255))  # The HSV range for the color blue
# TODO (challenge 1): add HSV ranges for other colors
RED = ((0,50,50), (20,255,255))
GREEN = ((60,50,50), (80,255,200))
# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour






white_cone = {Color.RED: 1, Color.GREEN:2, Color.BLUE: 3}
yellow_cone = {Color.RED: 1, Color.BLUE: 2, Color.GREEN: 3}
pink_cone = {Color.GREEN: 1, Color.BLUE: 2, Color.RED: 3}
black_cone = {Color.GREEN: 1, Color.RED: 2, Color.BLUE: 3}
purple_cone = {Color.BLUE:1,Color.RED:2, Color.GREEN:3}
orange_cone = {Color.BLUE:1,Color.GREEN:2, Color.RED:3}
current_see_colors = []

current_cone = white_cone

buttonTimes = 0


########################################################################################
# Functions
########################################################################################

def get_key(dict, value):
     for k, v in dict.items():
        if v==value:
            return k



def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_center
    global contour_area
    
    global current_see_colors
    global current_cone
    global white_cone
    global pink_cone
    global black_cone
    global purple_cone
    global yellow_cone
    global orange_cone

    global buttonTimes

    if rc.controller.was_pressed(rc.controller.Button.A):
        buttonTimes += 1

    tempArr = [
        white_cone,
        pink_cone,
        black_cone,
        purple_cone,
        orange_cone,
        yellow_cone
    ]

    current_cone = tempArr[buttonTimes % len(tempArr)]
    
    if current_cone == white_cone:
        print("white cone...")
    elif current_cone == black_cone:
        print("black cone...")
    elif current_cone == purple_cone:
        print("purple cone...")
    elif current_cone == pink_cone:
        print("pink cone...")
    elif current_cone == orange_cone:
            print("orange cone...")
    elif current_cone == yellow_cone:
            print("yellow cone...")

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
        green_contours = rc_utils.find_contours(image, GREEN[0], GREEN[1])

        # Select the largest contour
        blue_largest_contour = rc_utils.get_largest_contour(blue_contours, MIN_CONTOUR_AREA)
        red_largest_contour = rc_utils.get_largest_contour(red_contours, MIN_CONTOUR_AREA)
        green_largest_contour = rc_utils.get_largest_contour(green_contours, MIN_CONTOUR_AREA)



        # 注释
        # if red_largest_contour is not None:
        #     # Calculate contour information
        #     contour_center = rc_utils.get_contour_center(red_largest_contour)
        #     contour_area = rc_utils.get_contour_area(red_largest_contour)

        #     # Draw contour onto the image
        #     rc_utils.draw_contour(image, red_largest_contour)
        #     rc_utils.draw_circle(image, contour_center)
        # elif green_largest_contour is not None:
        #     # Calculate contour information
        #     contour_center = rc_utils.get_contour_center(green_largest_contour)
        #     contour_area = rc_utils.get_contour_area(green_largest_contour)

        #     # Draw contour onto the image
        #     rc_utils.draw_contour(image, green_largest_contour)
        #     rc_utils.draw_circle(image, contour_center)
        # elif blue_largest_contour is not None:
        #     # Calculate contour information
        #     contour_center = rc_utils.get_contour_center(blue_largest_contour)
        #     contour_area = rc_utils.get_contour_area(blue_largest_contour)

        #     # Draw contour onto the image
        #     rc_utils.draw_contour(image, blue_largest_contour)
        #     rc_utils.draw_circle(image, contour_center)
        # else:
        #     contour_center = None
        #     contour_area = 0

        current_see_colors = []


        if red_largest_contour is not None:
            current_see_colors.append(Color.RED)
            
        if blue_largest_contour is not None:
            current_see_colors.append(Color.BLUE)
            
        if green_largest_contour is not None:
            current_see_colors.append(Color.GREEN)


        minValue = 10000
        for v in current_see_colors:
            if current_cone[v]<minValue:
                minValue = current_cone[v]

        color_should_follow = get_key(current_cone, minValue)
        

        if color_should_follow == Color.RED:
            contour_center = rc_utils.get_contour_center(red_largest_contour)
            contour_area = rc_utils.get_contour_area(red_largest_contour)
            rc_utils.draw_contour(image, red_largest_contour)
            rc_utils.draw_circle(image, contour_center)
        elif color_should_follow == Color.BLUE:
            contour_center = rc_utils.get_contour_center(blue_largest_contour)
            contour_area = rc_utils.get_contour_area(blue_largest_contour)
            rc_utils.draw_contour(image, blue_largest_contour)
            rc_utils.draw_circle(image, contour_center)
        elif color_should_follow == Color.GREEN:
            contour_center = rc_utils.get_contour_center(green_largest_contour)
            contour_area = rc_utils.get_contour_area(green_largest_contour)
            rc_utils.draw_contour(image, green_largest_contour)
            rc_utils.draw_circle(image, contour_center)
        else:
            contour_center = None
            contour_area = 0

        # Display the image to the screen
        rc.display.show_color_image(image)


def start():
    """
    This function is run once every time the start button is pressed
    """
    global speed
    global angle

    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # rc.drive.set_max_speed(0.5)
    # Print start message
    print(
        ">> Lab 2A - Color Image Line Following\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Left trigger = accelerate backward\n"
        "    A button = print current speed and angle\n"
        "    B button = print contour center and area"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global speed
    global angle

    # Search for contours in the current color image
    update_contour()

    # Choose an angle based on contour_center
    # If we could not find a contour, keep the previous angle
    if contour_center is not None:
        # Current implementation: bang-bang control (very choppy)
        # TODO (warmup): Implement a smoother way to follow the line
        k = 1.0
        diff = 1 / (rc.camera.get_width() / 2)
        error = (contour_center[1] - (rc.camera.get_width() / 2)) * diff
        angle = k * error

        if angle > 1:
            angle = 1
        if angle < -1:
            angle = -1

    # Use the triggers to control the car's speed
    forwardSpeed = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    backSpeed = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = forwardSpeed - backSpeed

    if contour_area > 12000:
        rc.drive.stop()
    else:
        rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)


def update_slow():
    """
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """
    # Print a line of ascii text denoting the contour area and x-position
    if rc.camera.get_color_image() is None:
        # If no image is found, print all X's and don't display an image
        print("X" * 10 + " (No image) " + "X" * 10)
    else:
        # If an image is found but no contour is found, print all dashes
        if contour_center is None:
            print("-" * 32 + " : area = " + str(contour_area))

        # Otherwise, print a line of dashes with a | indicating the contour x-position
        else:
            s = ["-"] * 32
            s[int(contour_center[1] / 20)] = "|"
            print("".join(s) + " : area = " + str(contour_area))


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
