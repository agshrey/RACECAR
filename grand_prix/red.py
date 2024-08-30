
import sys
import cv2 as cv
import numpy as np

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils
from enum import IntEnum

rc = racecar_core.create_racecar()

class State(IntEnum):
    line_following = 0
    elevator = 1
    stop = 2
    search = 3
    wall_following = 4
    find_line = 5

class Color(IntEnum):
    green = 0
    red = 1
    blue = 2

# potential_colors = [
#     ((60, 50, 50), (80, 255, 255), "green"),
#     ((90, 50, 50), (110, 255, 255), "blue"),
#     ((0, 50, 50), (20, 255, 255), "red")
# ]
potential_colors = [
    ((60, 50, 50), (80, 255, 255), "green"),
    ((90, 100, 100), (110, 255, 255), "blue"),
    ((0, 50, 50), (20, 255, 255), "red")
]

cur_state = State.search
speed = 0
angle = 0

color = ""
color_image = None
cropped_image = None

CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

CROP_FLOOR2 = ((300, 200), (rc.camera.get_height(), rc.camera.get_width()))
# LEFT_WINDOW = (-45, -30)
# RIGHT_WINDOW = (30, 45)
LEFT_WINDOW = (-60, -45)
RIGHT_WINDOW = (45, 60)
FRONT_WINDOW = (-10, 10)
# RIGHT_WINDOW = (40, 50)
# LEFT_WINDOW = (-40, -50)

left_dist = 0
right_dist = 0

markers = []
counter = 0
def start():
    # rc.drive.set_max_speed(0.45) and 1
    rc.drive.set_max_speed(0.5)
    rc.drive.stop()

def detected_color_line_contour_center():
    cropped_image = rc_utils.crop(color_image, CROP_FLOOR[0], CROP_FLOOR[1])
    red_contours = rc_utils.find_contours(cropped_image,potential_colors[2][0], potential_colors[2][1])
    
    red_largest_contour = rc_utils.get_largest_contour(red_contours, 30)

    green_contours = rc_utils.find_contours(cropped_image, potential_colors[0][0], potential_colors[0][1])
    green_largest_contour = rc_utils.get_largest_contour(green_contours, 1000)

    # blue_contours = rc_utils.find_contours(cropped_image, potential_colors[1][0], potential_colors[1][1])
    # blue_largest_contour = rc_utils.get_largest_contour(blue_contours, 1000)
    
    # rc.display.show_color_image(cropped_image)
    if red_largest_contour is not None:
        print("red-area:", rc_utils.get_contour_area(red_largest_contour))
        return rc_utils.get_contour_center(red_largest_contour), Color.red
    elif green_largest_contour is not None:
        print("green-area:", rc_utils.get_contour_area(green_largest_contour))
        return rc_utils.get_contour_center(green_largest_contour), Color.green
    # elif blue_largest_contour is not None:
    #     return rc_utils.get_contour_center(blue_largest_contour), Color.blue
    else:
        return None, None

    

alreadyGotEelevator = False

isFoundRed = False
times = 0
isInsideEelevator = False
def line_following():
    global color
    global angle
    global speed
    global color_image

    global isFoundRed
    global alreadyGotEelevator

    global times

    global counter


    contour_center, detectedColor = detected_color_line_contour_center()
    if (detectedColor==Color.green or detectedColor==Color.blue)and alreadyGotEelevator:
        return
    if isInsideEelevator:
        c2_image = rc_utils.crop(color_image, CROP_FLOOR2[0], CROP_FLOOR2[1])
        red_contours = rc_utils.find_contours(c2_image,potential_colors[2][0], potential_colors[2][1])
        red_largest_contour = rc_utils.get_largest_contour(red_contours, 30)
        print("contour:", red_largest_contour)
        if red_largest_contour is not None:
            contour_center = rc_utils.get_contour_center(red_largest_contour)
            rc_utils.draw_contour(c2_image, red_largest_contour)
            print("area", rc_utils.get_contour_area(red_largest_contour))

        # rc.display.show_color_image(c2_image)
        print("weddddddddddddddddddddddddddddd")

        counter += rc.get_delta_time()
        print("counter:", counter)
        if counter<1.8:
            speed = 0.6
            angle = 0.01
        elif counter <2.7:
            speed = 0.6
            angle = -0.95
        elif counter < 4.3:
            speed = 0.6
            angle = 0
        elif counter < 4.7:
            angle = 1
            speed = 0.6
        elif counter < 5.6:
            speed = 1
            angle = -0.01
        else:
            cur_state = State.elevator


    
    if contour_center is not None:
        angle = rc_utils.remap_range(contour_center[1], 0, rc.camera.get_width(), -1, 1, True)
        speed = 0.6

isGotEelevator = False


def elevator():
    global speed
    global angle
    global color
    global markers


    global isGotEelevator
    global isInsideEelevator

    global left_dist
    global right_dist


    print("color", color)

    if color == "not detected":
        speed = 0
        angle = 0
        isGotEelevator = True
    elif color == "blue" and isGotEelevator:
        speed = 1
        angle = -0.1

    if left_dist<35 and right_dist<35:
        isInsideEelevator = True
    


    
        
    


def wall_following():
    global left_dist
    global right_dist
    global angle
    global speed

    angle = rc_utils.clamp((right_dist - left_dist)/50, -1.0, 1.0)
    speed = 0.8





def update():
    global cur_state, speed, angle
    global color
    global color_image

    

    global isGotEelevator
    global isFoundRed
    global alreadyGotEelevator

    global left_dist
    global right_dist



    color_image = rc.camera.get_color_image()
    h = rc.camera.get_height()
    w = rc.camera.get_width()
    c_image = rc_utils.crop(color_image, (h//6, w//6), (h*4//6, w*4//6))
    markers = rc_utils.get_ar_markers(c_image)
    # rc_utils.draw_ar_markers(color_image, markers)

    scan = rc.lidar.get_samples()
    _, forward_dist = rc_utils.get_lidar_closest_point(scan, FRONT_WINDOW)
    _, left_dist = rc_utils.get_lidar_closest_point(scan, LEFT_WINDOW)
    _, right_dist = rc_utils.get_lidar_closest_point(scan, RIGHT_WINDOW)


    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = rt - lt
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    
    
    _, detectedColor = detected_color_line_contour_center()


    print("---------------------test----------------------")
    print("cur_state", cur_state)
    print("left", left_dist)
    print("right", right_dist)
    print("detected:", detectedColor)


    

    

    if cur_state == State.search:
        speed = 0.5
        angle = -0.25

        if detectedColor is not None:
            cur_state = State.line_following
    elif cur_state == State.line_following:
        line_following()

        if detectedColor is None and not isInsideEelevator:
            cur_state = State.find_line
    elif cur_state == State.stop:
        angle = 0
        speed = 0
    elif cur_state == State.elevator:
        if len(markers):
            markers[0].detect_colors(c_image, potential_colors)
            color = markers[0].get_color()
        alreadyGotEelevator = True

        elevator()

        if forward_dist>190 and isInsideEelevator:
            cur_state = State.wall_following
            isGotEelevator = False

        if detectedColor is not None:
            cur_state = State.line_following

    elif cur_state == State.wall_following:
        wall_following()
        print("detectedcolor", detectedColor)
        if detectedColor is not None or (left_dist>650 or right_dist>650):
            cur_state = State.line_following
    elif cur_state == State.find_line:
        angle = 1
        speed = -1
        if len(markers):
            if markers[0].get_id()==0:
                cur_state = State.elevator
        
        if detectedColor == Color.red:
            cur_state = State.line_following
            isFoundRed = True

        


    rc.drive.set_speed_angle(speed, angle)
    c2_image = rc_utils.crop(color_image, CROP_FLOOR2[0], CROP_FLOOR2[1])

    rc.display.show_color_image(c2_image)
    







if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
