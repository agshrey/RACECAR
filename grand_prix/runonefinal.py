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

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Put any global variables here
speed = 0
angle = 0

contour_center = None
contour_area = 0

BLUE = ((90,50,100),(120,255,255))
MIN_CONTOUR_AREA = 30
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))
########################################################################################
# Functions
########################################################################################

def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    rc.drive.stop()
    
    print(">> Grand Prix - Run One")
    MAX_SPEED = 0.35
    rc.drive.set_max_speed(MAX_SPEED)



def update():
    global contour_center
    global contour_area
    global angle
    global speed
    
    speed = 1

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        largest_contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

    if largest_contour is not None:
        contour_center = rc_utils.get_contour_center(largest_contour)
        contour_area = rc_utils.get_contour_area(largest_contour)

        rc_utils.draw_contour(image, largest_contour)
        rc_utils.draw_circle(image, contour_center)

        scale = 1 / (rc.camera.get_width() / 2)
        error = (contour_center[1] - (rc.camera.get_width() / 2)) * scale
        angle = error
        angle = rc_utils.clamp(angle, -1, 1)
    else:
        contour_center = None
        contour_area = 0
        if angle < 0:
            angle = -1
        elif angle > 0:
            angle = 1
    
    rc.display.show_color_image(image)
    rc.drive.set_speed_angle(speed, angle)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
