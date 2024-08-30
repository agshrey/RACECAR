"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 1 - Driving in Shapes
"""

########################################################################################
# Imports
########################################################################################

from curses.ascii import CR
import sys
import cv2 as cv
import numpy as np
sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from enum import IntEnum

########################################################################################
# Global variables
########################################################################################
class State(IntEnum):
    lineFollow = 0
    wallFollow = 1
    straight = 2

cur_state = State.lineFollow
rc = racecar_core.create_racecar()

# Put any global variables here
speed = 0
angle = 0

#LIDAR
left_angle = 0
left_distance = 0
right_angle = 0
right_distance = 0
LEFT_WINDOW = (-45, -30)
RIGHT_WINDOW = (30, 45)

contour_center = None
contour_area = 0
line_image = None
cropped_image = None
color_image = None
potential_colors = [
    (( 90, 20, 200), (115, 60, 255), "white"),
    ((90, 50, 50), (120, 255, 255), "blue"),
    ((170, 50, 50), (10, 255, 255), "red")
]

#OTHER
markers = None
color = None
image = None
contour_center = None
contour_area = 0
ar_area = 0
ar_center = None
counter = 0

BLUE = ((90,50,100),(120,255,255))
GREEN = ((40, 50, 50), (80, 255, 255))
MIN_CONTOUR_AREA = 40
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))
WHITE = (( 90, 20, 200), (115, 60, 255))

########################################################################################
# Functions
########################################################################################

def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    rc.drive.stop()
    
    print(">> Grand Prix - Candy Valley")
    MAX_SPEED = 0.4
    rc.drive.set_max_speed(MAX_SPEED)



def update():
    global contour_center
    global contour_area
    global angle
    global speed
    global image
    global left_angle, left_distance, right_angle, right_distance, cur_state
    global markers
    global counter

    scan = rc.lidar.get_samples()
    left_angle, left_distance = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    right_angle, right_distance = rc_utils.get_lidar_closest_point(scan, RIGHT_WINDOW)

    color_image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(color_image)
    rc_utils.draw_ar_markers(color_image, markers)

    update_contour()

    # if len(markers) != 0:
    #     update_contour_ar()
    #     print(ar_area)
    #     if markers[0].get_id() == 20 and ar_area > 15000:
    #         turnLeft()
    # else:
    #     if contour_area != 0:
    #         linefollow()
    #     else:
    #         folllowwall()

    if contour_area != 0:
        linefollow()
    else:
        folllowwall()

    if len(markers) != 0:
        update_contour_ar()
        print(ar_area)
        if markers[0].get_id() == 20 and ar_area > 25000:
            turnLeft()

    if counter < 0.5 and counter > 0:
        print("using counter")
        turnLeft()

    rc.drive.set_speed_angle(speed, angle)


def update_contour():
    global contour_center
    global contour_area
    global image

    image = rc.camera.get_color_image()
    if image is None:
        contour_center = None
        contour_area = None
    else:
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        contours = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        largest_contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

    if largest_contour is not None:
        contour_center = rc_utils.get_contour_center(largest_contour)
        contour_area = rc_utils.get_contour_area(largest_contour)

        rc_utils.draw_contour(image, largest_contour)
        rc_utils.draw_circle(image, contour_center)

    else:
        contour_center = None
        contour_area = 0

    rc.display.show_color_image(image)

def update_contour_ar():
    global ar_center
    global ar_area
    global MIN_CONTOUR_AREA

    ar_image = rc.camera.get_color_image()

    if ar_image is None:
        ar_center = None
        ar_area = 0
    else:
        contours = rc_utils.find_contours(ar_image, WHITE[0], WHITE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            ar_center = rc_utils.get_contour_center(contour)
            ar_area = rc_utils.get_contour_area(contour)
        
        else:
            ar_center = None
            ar_area = 0

def linefollow():
    global contour_center
    global contour_area
    global angle
    global speed
    global image
    print("line following")
    speed = 1
    scale = 1 / (rc.camera.get_width() / 2)
    error = (contour_center[1] - (rc.camera.get_width() / 2)) * scale
    angle = error
    angle = rc_utils.clamp(angle, -1, 1)
    
def folllowwall():
    global left_angle
    global left_distance
    global right_angle
    global right_distance
    global angle
    global speed
    print("wall following")
    # if right_distance > 70 or left_distance > 70:
    #     if right_distance > left_distance:
    #         speed = 0.5
    #     else:
    #         speed = 0.5
    speed = 0.5
    angle = rc_utils.clamp((right_distance - left_distance)/25, -1.0, 1.0)

def turnLeft():
    global speed
    global angle
    global counter

    print("turning")
    angle = -0.5
    speed = 1
    counter += rc.get_delta_time()
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()