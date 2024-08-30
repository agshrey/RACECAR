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
from turtle import width
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
timer = 5

c_height = rc.camera.get_height()
c_width = rc.camera.get_width()

MIN_CONTOUR_AREA = 100

turn = ""

# Crops sky out of image
CROP_CONES = ((200, 0), (c_height, c_width))

# Colors, stored as a pair (hsv_min, hsv_max)
BLUE = ((90, 100, 100), (120, 255, 255))  # The HSV range for the color blue
# TODO (challenge 1): add HSV ranges for other colors
RED = ((170, 100, 100), (179, 255, 255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels

red_contour_center = None  # The (pixel row, pixel column) of contour
red_contour_area = 0  # The area of contour
blue_contour_center = None
blue_contour_area = 0
isTurn = False

pause_time = 0.2
turn_time = 0.8
timer_search = 0
timer_all = 0
counter = 0


left_angle = 0
left_distance = 0
LEFT_WINDOW = (-60,-30)

from enum import IntEnum

class State(IntEnum):
    search = 1
    red = 2
    blue = 3
    back_up = 4
    stop = 5
    turn = 6
    dash = 7
cur_state = State.search
########################################################################################
# Functions
########################################################################################

def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global red_contour_center
    global red_contour_area
    global blue_contour_center
    global blue_contour_area

    color_image = rc.camera.get_color_image()

    if color_image is None:
        red_contour_center = None  # The (pixel row, pixel column) of contour
        red_contour_area = 0  # The area of contour
        blue_contour_center = None
        blue_contour_area = 0
    else:
        # TODO (challenge 1): Search for multiple tape colors with a priority order (red, green ,blue)
        # (currently we only search for blue)

        # Crop the image to the floor directly in front of the car
        image = rc_utils.crop(color_image, CROP_CONES[0], CROP_CONES[1])

        # Find all of the red contours
        red_contours = rc_utils.find_contours(image, RED[0], RED[1])
        blue_contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])

        red_contour = rc_utils.get_largest_contour(red_contours, MIN_CONTOUR_AREA)
        blue_contour = rc_utils.get_largest_contour(blue_contours, MIN_CONTOUR_AREA)

        # Select the largest contour
        
        if red_contour is not None:
            # Calculate contour information
            red_contour_center = rc_utils.get_contour_center(red_contour)
            red_contour_area = rc_utils.get_contour_area(red_contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, red_contour)
            rc_utils.draw_circle(image, red_contour_center)

        else:
            red_contour_center = None
            red_contour_area = 0

        if blue_contour is not None:
            # Calculate contour information
            blue_contour_center = rc_utils.get_contour_center(blue_contour)
            blue_contour_area = rc_utils.get_contour_area(blue_contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, blue_contour)
            rc_utils.draw_circle(image, blue_contour_center)

        else:
            blue_contour_center = None
            blue_contour_area = 0

        # Display the image to the screen
        markers = rc_utils.get_ar_markers(color_image)
        rc_utils.draw_ar_markers(color_image, markers)
        rc.display.show_color_image(color_image)


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()
    counter = 0

    global speed
    global angle
    global max_speed

    speed = 0
    angle = 0

    max_speed = 0.3 # Default max speed is 0.25
    rc.drive.set_max_speed(max_speed)

    # Print start message
    print(">> Phase 1 Challenge: Cone Slaloming")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Slalom between red and blue cones.  The car should pass to the right of
    # each red cone and the left of each blue cone.

    global cur_state

    global RED
    global BLUE
    global red_contour_area
    global red_contour_center
    global blue_contour_area
    global blue_contour_center

    global turn_time
    global pause_time
    global timer_all
    global counter

    global speed
    global angle

    global turn

    global width
    global closest_contour_area
    global height

    global timer
    global timer_search
    
    color_image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(color_image)
    rc_utils.draw_ar_markers(color_image, markers)
    
    # rc.display.show_color_image(color_image)
    depth_image = rc.camera.get_depth_image()
    depth_image = rc_utils.crop(depth_image, CROP_CONES[0], CROP_CONES[1])
    depth_image = (depth_image-0.01) % 10000
    
    update_contour()
    
    if blue_contour_center is None and red_contour_center is None:
        closest_contour_center = None
        closest_contour_area = 0
        closest_contour_color = None
    elif red_contour_center is None:
        closest_contour_color = 'Blue'
        closest_contour_area = blue_contour_area
        closest_contour_center = blue_contour_center
    elif blue_contour_center is None:
        closest_contour_color = 'Red'
        closest_contour_area = red_contour_area
        closest_contour_center = red_contour_center          
    elif depth_image[red_contour_center[0]][red_contour_center[1]] > depth_image[blue_contour_center[0]][blue_contour_center[1]]:
        closest_contour_color = 'Blue'
        closest_contour_area = blue_contour_area
        closest_contour_center = blue_contour_center
    else:
        closest_contour_color = 'Red'
        closest_contour_area = red_contour_area
        closest_contour_center = red_contour_center



    if closest_contour_center is not None:
        closest_distance = depth_image[closest_contour_center[0]][closest_contour_center[1]]

    else: 
        closest_distance = 9999

    if blue_contour_center is not None:
        blue_distance = depth_image[blue_contour_center[0]][blue_contour_center[1]]
    
    if red_contour_center is not None:
        red_distance = depth_image[red_contour_center[0]][red_contour_center[1]]
    
    #State machine
    timer_search += rc.get_delta_time()
    if cur_state == State.search:
        angle = 0
        if len(markers)!= 0:
            marker = markers[0]
            if marker.get_id() == 5:
                cur_state = State.dash
        if closest_contour_center is not None and closest_distance < 150:
        
            if closest_contour_color == 'Blue':
                cur_state = State.blue
            elif closest_contour_color == 'Red':
                cur_state = State.red
        if timer_search > 1.5:
            cur_state = State.turn


    elif cur_state == State.blue:
        timer_search = 0
        if timer > turn_time:
            if blue_contour_center is not None:

                print('Blue Cone Detected')

                safe_distance = 25*(1.006**(c_width - blue_contour_center[1]))

                angle = rc_utils.remap_range(closest_distance, safe_distance, safe_distance+40, -0.5, 0.5)
                angle = rc_utils.clamp(angle, -0.6, 0.6)


            if closest_contour_color == 'Red' and closest_distance > 80:
                timer = 0
                turn = 'Right'
                cur_state = State.red
            

            if closest_contour_color is None:
                timer = 0
                turn = 'Right'
                cur_state = State.search


    elif cur_state == State.red:
        timer_search = 0
        if timer > turn_time:    
            if red_contour_center is not None:

                print('Red Cone Detected')
                print("timer", timer)

                safe_distance = 25*(1.006**(red_contour_center[1]))

                angle = rc_utils.remap_range(closest_distance, safe_distance+40, safe_distance, -0.5, 0.5)
                angle = rc_utils.clamp(angle, -0.6, 0.6)



            if closest_contour_color == 'Blue' and closest_distance > 80:
                timer = 0
                turn = 'Left'
                cur_state = State.blue
            

            if closest_contour_color is None:
                timer = 0
                turn = 'Left'
                cur_state = State.search
    elif cur_state == State.turn:
        angle = -1
        if closest_contour_color == 'Red' and closest_distance > 80:
                timer = 0
                turn = 'Right'
                cur_state = State.red
        elif closest_contour_color == 'Blue' and closest_distance > 80:
                timer = 0
                turn = 'Left'
                cur_state = State.blue
    elif cur_state == State.dash:
        dash()
        # elif closest_contour_color is None:
        #         timer = 0
        #         turn = 'Right'
        #         cur_state = State.search

    speed = 1

    if blue_contour_center is not None and red_contour_center is not None:

        if blue_distance + red_distance < 200:
            speed = 0.2

    pause_time = 0.2
    turn_time = 0.6

    # if closest_contour_color is None:
    #     angle = 0

    timer += rc.get_delta_time()
    timer_all += rc.get_delta_time()

    if timer < pause_time:
        # print('Pausing')
        
        angle = 0

    elif timer < turn_time:
        # print('turning back')

        if turn == 'Left':
            
            if blue_contour_center is None:
                timer = 0.55
                angle = -1
            elif blue_distance > 25*(1.006**(c_width - blue_contour_center[1])) - 10 and blue_distance < 150:
                angle = 0
                print("Safely Past blue Cone!!", blue_distance)
            else: 
                timer = 0.55
                angle = -1


            
        elif turn == 'Right':

            if red_contour_center is None:
                timer = 0.5
                angle = 1
            elif red_distance > 25 * (1.006 ** red_contour_center[1]) - 10 and red_distance < 150:
                angle = 0
                print("Safely Past red Cone!!")
            else: 
                timer = 0.55
                angle = 1





    # angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    print("State", cur_state)
    print("counter", counter)
    print("timer_search", timer_search)
    counter += rc.get_delta_time()
    if counter > 46:
        speed = 1
        angle = 0
    
    rc.drive.set_speed_angle(speed, angle)

def dash():
    global left_angle
    global left_distance
    global angle
    global speed
    global max_speed

    scan = rc.lidar.get_samples()
    __, left_distance = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    
    angle = rc_utils.clamp((75-left_distance)/50, -1, 1)
    print("angle:", angle, "left_distance:", left_distance)
    speed = 1
    max_speed = 1
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()