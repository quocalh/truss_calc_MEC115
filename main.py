import pygame as pg
from pygame.locals import *

from vector import *
from components import *
from setting import *
from gui import *
from solver import *

import math

# class 
"""
hold j and press to add joints
    ensure x and y is 0
    can't generate force

hold p and press to add points
    joints just ensure x and y is 0
    can generate force

hold r and press to add roller
    roller ensures y is 0

right click to attach string to the nearest point 

left click to find the closest point + attach a force to it, with x^3 exponential value
based on relative distance


we will extend it into frame later
    now only 2 force member

"""
   
class Linker:
    def __init__(self, pt1: Support):
        self.pt1: Support = pt1
        self.pt2: Support = None
        self.done = False

WIDTH, HEIGHT = 800, 800
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

def get_closest_point(points: list[Support], anchor: Support) -> Support:

    if (len(points) < 1):
        return None

    # find the closest point
    closest_relative = [anchor[0] - points[0].point[0], anchor[1] - points[0].point[1]]
    sqr_closest_dist = closest_relative[0] * closest_relative[0] + closest_relative[1] * closest_relative[1]
    closest = points[0]

    for i in range(1, len(points)):
        point = points[i] 
        relative = [anchor[0] - point.point[0], anchor[1] - point.point[1]]
        sqr_dist = relative[0] * relative[0] + relative[1] * relative[1]

        if (sqr_dist < sqr_closest_dist):
            sqr_closest_dist = sqr_dist
            closest = point

    if sqr_closest_dist > ISSUE_SENSITIVITY_SQR_DIST:
        print(sqr_closest_dist)
        return None

    return closest


supports: list[Support] = []
members: list[Member] = []
forces: list[Force] = []

solver = Solver()

string_issue_member: Linker = None
string_issue_force: Linker = None

running = True
while (running):

    LEFT_CLICKED = False
    RIGHT_CLICKED = False
    MIDDLE_CLICKED = False

    MOUSE_POS = list(pg.mouse.get_pos())

    screen.fill((255 * 0.1, 255 * 0.2, 255 * 0.3))

    events = pg.event.get()
    for event in events:
        if (event.type == pg.QUIT):
            running = False

        if (event.type == pg.MOUSEBUTTONDOWN):
            if (event.button == BUTTON_LEFT):
                LEFT_CLICKED = True 
            if (event.button == BUTTON_RIGHT):
                RIGHT_CLICKED = True
            if (event.button == BUTTON_MIDDLE):
                MIDDLE_CLICKED = True

        if (event.type == pg.KEYDOWN):
            if (event.key == pg.K_ESCAPE):
                print("bye bye")
                running = False

            if (event.key == pg.K_RETURN):
                print("solving...")
                solver.solve_truss(members, supports, forces)

            key_comb = event.key 
            if ((key_comb == pg.K_LCTRL and key_comb == pg.K_s) or (key_comb == pg.K_s and key_comb == pg.K_LCTRL) ):
                if (event.key == pg.K_s):
                    print("saving...")
                


    """
    # feature: magnetic row col
    if keys[K_LSHIFT] and string_issue_cur:
        
        relative = [string_issue_cur.pt1.point[0] - MOUSE_POS[0], string_issue_cur.pt1.point[1] - MOUSE_POS[1]]
        if (abs(relative[0]) > abs(relative[1])): # x dominant
            MOUSE_POS[0] = string_issue_cur.pt1.point[0]
        else:
            MOUSE_POS[1] = string_issue_cur.pt1.point[1]

        pg.draw.line(screen, "green", string_issue_cur.pt1.point, MOUSE_POS)
    """

    keys = pg.key.get_pressed()
    if keys[K_LSHIFT]:
        render_magnetic_grid(screen, WIDTH, HEIGHT)
        magnetic = magnetic_mouse_pos_closest(
            MOUSE_POS, 
            WIDTH / X_GRID_DIVISOR, 
            HEIGHT / Y_GRID_DIVISOR
        )
        pg.draw.circle(screen, "green", magnetic, 5)
        MOUSE_POS = magnetic

    if keys[K_p]:
        if LEFT_CLICKED:
            supports.append(
                Pin(MOUSE_POS)  
            )

    elif keys[K_r]:
        if LEFT_CLICKED:
            supports.append(
                Roller(MOUSE_POS)
            )

    elif keys[K_j]:
        if LEFT_CLICKED:
            supports.append(
                Joint(MOUSE_POS)
            )

    elif keys[K_f]:
        pass

    elif keys[K_LCTRL]:
        for event in events:
            if event.type == KEYDOWN and event.key == K_s:
                print("saved")

    if RIGHT_CLICKED:
        if len(supports) < 2:
            pass

        elif string_issue_member:
            magnetic = get_closest_point(supports, MOUSE_POS)
            if (not magnetic): pass

            elif (magnetic is string_issue_member.pt1):
                print("can't link between it and itself, no? -> destroy link...")  
                string_issue_member = None

            else:
                string_issue_member.pt2 = magnetic
                members.append(
                    Member(
                        string_issue_member.pt1, 
                        string_issue_member.pt2, 
                        COMPONENT_TYPE.TRUSS
                    )
                ) 
                string_issue_member = None

        else:
            magnetic = get_closest_point(supports, MOUSE_POS)
            if (not magnetic): pass
            else:
                string_issue_member = Linker(magnetic)

    if MIDDLE_CLICKED:
        if len(supports) < 1:
            pass

        elif string_issue_force:
            relative = [MOUSE_POS[0] - string_issue_force.pt1.point[0], 
                        MOUSE_POS[1] - string_issue_force.pt1.point[1]]
            strength = Force.evaluate_strength(relative)
            mag = vector2_mag(relative)

            if mag != 0:
                forces.append(
                    Force(
                        vector2_scale(relative, 1 / vector2_mag(relative)),
                        string_issue_force.pt1, 
                        strength, MOUSE_POS
                    )
                )

            string_issue_force = None

        else:
            magnetic = get_closest_point(supports, MOUSE_POS)
            if (not magnetic): pass
            else:
                string_issue_force = Linker(magnetic)


    for point in supports:
        point.render(screen)

    for bone in members:
        pg.draw.line(screen, "white", bone.p1.point, bone.p2.point, 2)

    for force in forces:
        force.render(screen)


    if string_issue_member:
        pg.draw.line(screen, "white", string_issue_member.pt1.point, MOUSE_POS, 2)

    if string_issue_force:
        pg.draw.line(screen, "magenta", string_issue_force.pt1.point, MOUSE_POS, 2)
        strength = Force.evaluate_strength(vector2_relative(
            string_issue_force.pt1.point, MOUSE_POS
            )
        )
        relative = vector2_relative(string_issue_force.pt1.point, MOUSE_POS)
        screen.blit(
            primitive_font_render(str(strength), "magenta"),
            vector2_add(
                string_issue_force.pt1.point,
                vector2_scale(relative, 1/2)
            ),
        )
        
    screen.blit(
        primitive_font_render(
            str(int(clock.get_fps())), 
            "white"
        ),
        (0, 0) 
    )

    pg.display.flip()
    clock.tick(400)


# main phase

# the running command
# __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python main.py

