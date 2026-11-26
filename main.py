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

to join two truss:
    press ALT to inspect the closest?
        nah press ALT to start do the linking

    upon pressing ALT (or F)?, 
        the MOUSE POS move to to the nearest member 
        a frame linker will be created (holding the parent)

        upon a left click, 
            create a string frame issue (2)
                save pt1, the parent truss (the closest one)

            if string frame issued, 
                if the parent member (the closest) is the same as the first node (1)
                    destroy the link
                frame add the support point (into the binding list)
                    a support will be created
                    the parent member (the closest) 
                        turning into a frame
            

(1) ownership problem
    add "parent_member" to the support
        add and destroy using interface (on sync with the parent member)

(2) we really have to?
    just create that point
        declare the relationship between the point and that frame 
            (transform from truss to frame if needed to)

"""
   
class Linker:
    def __init__(self, pt1: Support):
        self.pt1: Support = pt1
        self.pt2: Support = None

    def render(self, surface: pg.surface.Surface, pos: list[float], color: pg.Color = "white"):
        pg.draw.line(surface, color, self.pt1.point, pos, 2) 

class FrameLinker(Linker):
    def __init__(self, joint1: Support, member1: Member):
        super().__init__(joint1)
        self.member1: Member = member1
        self.member2: Member = None

    """
    def render(self, surface: pg.surface.Surface, pos: list[float], color: pg.Color = "white"):
        super().render(surface, pos, color)
        self.pt1_parent.render(surface)
        # self.pt2_parent.render(surface)
    """

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
        return None

    return closest

supports: list[Support] = []
members: list[Member] = []
forces: list[Force] = []
# frame_map: dict[str: Frame] = {}

solver = Solver()

string_issue_member: Linker = None
string_issue_force: Linker = None
string_issue_frame: Linker = None

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
                print("solving truss...")
                solver.solve_truss(members, supports, forces)
                print("solving frame...")
                solver.solve_frame(members, supports, forces)

            key_comb = event.key 
            if ((key_comb == pg.K_LCTRL and key_comb == pg.K_s) or (key_comb == pg.K_s and key_comb == pg.K_LCTRL) ):
                if (event.key == pg.K_s):
                    print("saving...")

    keys = pg.key.get_pressed()

    if keys[K_LSHIFT]:
        render_magnetic_grid(screen, WIDTH, HEIGHT)
        point = magnetic_mouse_pos_closest(
            MOUSE_POS, 
            WIDTH / X_GRID_DIVISOR, 
            HEIGHT / Y_GRID_DIVISOR
        )
        pg.draw.circle(screen, "green", point, 5)
        MOUSE_POS = point

    # boss im tired
    if keys[K_p] or keys[K_q]:
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

    if keys[K_LCTRL]:
        for event in events:
            if event.type == KEYDOWN and event.key == K_s:
                print("saved")

    if keys[K_LALT]:
        if (len(supports) < 2):
            pass
        else: 
            # get the closest point, get the closest member
            closest_member = None
            closest_point = None
            closest_dist = float("inf")

            for member in members:
                p1 = member.p1.point
                p2 = member.p2.point

                vector = vector2_relative(p1, MOUSE_POS)
                base = vector2_relative(p1, p2)
                base_dist = vector2_mag(base)
                normalized_product = dot(base, vector) / base_dist / base_dist

                if normalized_product > 1:
                    dist = vector2_mag(vector2_relative(p2, MOUSE_POS)) 
                    point = p2
                elif normalized_product < 0:
                    dist = vector2_mag(vector)
                    point = p1
                else:
                    dist = abs(cross(vector, base)) / base_dist
                    point = vector2_add(
                        p1, vector2_scale(base, normalized_product)
                    )

                if (dist < closest_dist):
                    closest_point = point
                    closest_dist = dist
                    closest_member = member

            # if any member exists at all
            if closest_point:
                pg.draw.line(screen, "cyan", 
                            closest_point, 
                            MOUSE_POS, 5)

                pg.draw.line(screen, "cyan", 
                            closest_member.p1.point, 
                            closest_member.p2.point, 5)

                pg.draw.circle(screen, "yellow", closest_point, 10)

                if LEFT_CLICKED:
                    if len(supports) < 2:
                        pass                
                    else:
                        joint = Joint(closest_point)

                        if closest_member.type is COMPONENT_TYPE.TRUSS:
                            closest_member = Truss.frame_transform(closest_member)

                        # ownership declare
                        closest_member.declare_ownership(joint)

                        # append new support
                        supports.append(joint)

                    """
                    elif string_issue_frame:

                        # if same member parent -> cancel
                        if string_issue_frame.member1 is closest_member:
                            print("same parent member -> destroy frame linker")
                            string_issue_frame = None

                        else:

                            supports.append(
                                string_issue_frame.pt1
                            )
                            supports.append(
                                string_issue_frame.pt2
                            )

                            frame = Frame(
                                string_issue_frame.pt1, string_issue_frame.pt2 
                            )
                            members.append(
                                frame
                            )

                            #   transform the member 
                            #   from truss to frame
                            #   from frame to frame

                            # declare ownership
                            Frame.declare_ownership

                            

                    else:
                        if (closest_dist > ISSUE_SENSITIVITY_SQR_DIST):
                            pass
                        else:
                            support = Joint(closest_point)
                            string_issue_frame = FrameLinker(support, closest_member) 
                    """

    if RIGHT_CLICKED:
        if len(supports) < 2:
            pass

        elif string_issue_member:
            point = get_closest_point(supports, MOUSE_POS)
            if (not point): pass

            elif (point is string_issue_member.pt1):
                print("can't link between it and itself, no? -> destroy link...")  
                string_issue_member = None

            else:
                string_issue_member.pt2 = point
                members.append(
                    Truss(
                        string_issue_member.pt1, 
                        string_issue_member.pt2, 
                    )
                ) 
                string_issue_member = None

        else:
            point = get_closest_point(supports, MOUSE_POS)
            if (not point): pass
            else:
                string_issue_member = Linker(point)

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
            point = get_closest_point(supports, MOUSE_POS)
            if (not point): pass
            else:
                string_issue_force = Linker(point)

                """
                # if is owned then the force is belonged to the member
                if (point.owning_member is not None):
                    owner = point.owning_member
                    if (owner.type == COMPONENT_TYPE.FRAME):
                        pass
                    else:
                        print("who are you")
                        assert(0)
                """

    """
    if string_issue_frame:
        pg.draw.circle(screen, "red", 
                       string_issue_frame.pt1.point, 5)

        p1 = string_issue_frame.pt1.point
        pg.draw.line(screen, "cyan", p1, MOUSE_POS, 2)
    """

    for point in supports:
        point.render(screen)

    for member in members:
        member.render(screen)

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

