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


# class Color(IntEnum):
#     RED = 1
#     BlUE = 2
#     GREEN = 3
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

#LIDAR
left_angle = 0
left_distance = 0
right_angle = 0
right_distance = 0
LEFT_WINDOW = (-45, -30)
RIGHT_WINDOW = (30, 45)

#COLOR
WHITE = (( 90, 20, 200), (115, 60, 255))
RED = ((170, 50, 50), (10, 255, 255))
GREEN = ((40, 50, 50), (80, 255, 255))
BLUE = ((90, 50, 100), (120, 255, 255))
MIN_CONTOUR_AREA = 30
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

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
    # rc.drive.set_max_speed(0.35)


def update():
    global cur_state
    global speed
    global angle
    global left_angle
    global left_distance
    global right_angle
    global right_distance
    global color_image
    global line_image
    global cropped_image
    global markers
    global image
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    color_image = rc.camera.get_color_image()
    cropped_image = rc_utils.crop(color_image, CROP_FLOOR[0], CROP_FLOOR[1])

    image = rc_utils.crop(color_image, CROP_FLOOR[0], CROP_FLOOR[1])
    rc.display.show_color_image(image)
    markers = rc_utils.get_ar_markers(color_image)
    rc_utils.draw_ar_markers(color_image, markers)

    # rc.display.show_color_image(color_image)
    # rc.display.show_color_image(cropped_image)

    scan = rc.lidar.get_samples()
    left_angle, left_distance = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    right_angle, right_distance = rc_utils.get_lidar_closest_point(scan, RIGHT_WINDOW)

    # TODO: Turn left if we see a marker with ID 0 and right for ID 1

    # TODO: If we see a marker with ID 199, turn left if the marker faces left and right
    # if the marker faces right

    # TODO: If we see a marker with ID 2, follow the color line which matches the color
    # border surrounding the marker (either blue or red). If neither color is found but
    # we see a green line, follow that instead.

    
    update_contour()
    if cur_state != State.followLine:
        if len(markers) == 0:
            speed = 0.75
            cur_state = State.followWall
        else:
            marker = markers[0]
            # if marker.get_id() == 2:
            #         cur_state = State.followLine
            # else:
            if contour_area < 13000:
                speed = 0.75
                cur_state = State.followWall
            else:
                marker = markers[0]
                if marker.get_id() == 0:
                    speed = 0.75
                    cur_state = State.turnLeft
                elif marker.get_id() == 1:
                    speed = 0.75
                    cur_state = State.turnRight
                elif marker.get_id() == 2:
                    # speed = 0.2
                    cur_state = State.followLine
                elif marker.get_id() == 199:
                    if marker.get_orientation() == marker.get_orientation().LEFT:
                        speed = 0.75
                        cur_state = State.turnLeft
                    elif marker.get_orientation() == marker.get_orientation().RIGHT:
                        speed = 0.75
                        cur_state = State.turnRight
                else:
                    speed = 0.75
                    cur_state = State.followWall

    if cur_state == State.followWall:
        rc.drive.set_max_speed(0.3)
        followWall()
    elif cur_state == State.followLine:
        rc.drive.set_max_speed(0.40)
        followLine()
    elif cur_state == State.turnLeft:
        rc.drive.set_max_speed(0.3)
        turnLeft()
    elif cur_state == State.turnRight:
        rc.drive.set_max_speed(0.3)
        turnRight()
    print("cur state", cur_state)
    print(speed)
    rc.drive.set_speed_angle(speed, angle)

def turnRight():
    global angle
    angle = 1


def turnLeft():
    global angle
    angle = -1


def followWall():
    global left_angle
    global left_distance
    global right_angle
    global right_distance
    global angle
    global speed

    if right_distance > 70 or left_distance > 70:
        if right_distance > left_distance:
            speed = 0.5
        else:
            speed = 0.5
    angle = rc_utils.clamp((right_distance - left_distance)/25, -1.0, 1.0)
            
def followLine():
    global angle
    global color_image
    global cropped_image
    global markers
    global left_distance
    global right_distance
    global speed
    global color
    global image

    
    # print("got here -----> ", markers[0].get_color())
    speed = 1
    if color == None:
        markers[0].detect_colors(color_image, potential_colors)
        color = markers[0].get_color()

    if color == "red":
        print("red path")
        image = rc_utils.crop(color_image, CROP_FLOOR[0], CROP_FLOOR[1])
        contour = rc_utils.find_contours(image, RED[0], RED[1])
        contour = rc_utils.get_largest_contour(contour, 30)
        contour_center = rc_utils.get_contour_center(contour)
        green_contour = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        green_contour = rc_utils.get_largest_contour(green_contour, 30)
        green_contour_center = rc_utils.get_contour_center(green_contour)
        if green_contour_center is not None:
            speed = 1
            print("going green")
            rc_utils.draw_contour(image, green_contour)
            rc_utils.draw_circle(image, green_contour_center)
            scale = 1 / (rc.camera.get_width() / 2)
            error = (green_contour_center[1] - (rc.camera.get_width() /2 )) * scale
            angle = error
        elif contour_center is not None:
            
            print("going red")
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)
            # angle = rc_utils.remap_range(contour_center[0], 0, rc.camera.get_width()-1,-1, 1, True)
            scale = 1 / (rc.camera.get_width() / 2)
            error = (contour_center[1] - (rc.camera.get_width() /2 )) * scale
            angle = error

    elif color == "blue":
        print("blue path")
        image = rc_utils.crop(color_image, CROP_FLOOR[0], CROP_FLOOR[1])
        contour = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        contour = rc_utils.get_largest_contour(contour, 30)
        contour_center = rc_utils.get_contour_center(contour)
        green_contour = rc_utils.find_contours(image, GREEN[0], GREEN[1])
        green_contour = rc_utils.get_largest_contour(green_contour, 30)
        green_contour_center = rc_utils.get_contour_center(green_contour)
        if green_contour_center is not None:
            
            print("going green")
            rc_utils.draw_contour(image, green_contour)
            rc_utils.draw_circle(image, green_contour_center)
            scale = 1 / (rc.camera.get_width() / 2)
            error = (green_contour_center[1] - (rc.camera.get_width() /2 )) * scale
            angle = error
        elif contour_center is not None:
            
            print("going blue")
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)
            # angle = rc_utils.remap_range(contour_center[0], 0, rc.camera.get_width()-1,-1, 1, True)
            scale = 1 / (rc.camera.get_width() / 2)
            error = (contour_center[1] - (rc.camera.get_width() /2 )) * scale
            angle = error
    
    rc.display.show_color_image(image)



def update_contour():
    global contour_center
    global contour_area
    global MIN_CONTOUR_AREA
    image = rc.camera.get_color_image()
    if image is None:
        contour_center = None
        contour_area = 0
    else:
        contours = rc_utils.find_contours(image, WHITE[0], WHITE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
        if contour is not None:
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)

            # rc_utils.draw_contour(image, contour)
            # rc_utils.draw_circle(image, contour_center)

            # rc.display.show_color_image(image)
        
        else:
            contour_center = None
            contour_area = 0

    

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()