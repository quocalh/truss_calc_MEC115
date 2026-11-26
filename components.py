from enum import Enum, auto
import pygame as pg


from vector import *
from misc import *
from setting import *

class COMPONENT_TYPE(Enum):
    COMPONENT = auto()

    JOINT = auto()
    PIN = auto()
    ROLLER = auto()

    FORCE = auto()

    TRUSS = auto()
    FRAME = auto()

"""
component
    support
        joint
        pin
        roller
    member
        truss
        frame
    force
        raw force
        distributed force (idk man)

"""

class Component:
    def __init__(self, type = COMPONENT_TYPE.COMPONENT):
        self.name = None
        self.type = type

class Support(Component):
    def __init__(self, point, type):
        super().__init__(type)
        self.name: str = get_alpha_name()
        self.point: list[float] = point
        self.owning_member: Member = None

    def render(self, surface: pg.surface.Surface):
        print("not yet implemented")
        assert(0)

class Joint(Support):
    def __init__(self, point):
        super().__init__(point, COMPONENT_TYPE.JOINT)

    def render(self, surface: pg.surface.Surface):
        pg.draw.circle(surface, "red", self.point, 5)
        surface.blit(
            primitive_font_render(self.name, "red"), 
            [TEXT_RENDER_OFFSET_X + self.point[0], 
             TEXT_RENDER_OFFSET_Y + self.point[1]]
        )

class Pin(Support):  
    def __init__(self, point):
        super().__init__(point, COMPONENT_TYPE.PIN)
        self.rX = 0
        self.rY = 0
        self.rX_name = self.name + "x"
        self.rY_name = self.name + "y"

    def render(self, surface: pg.surface.Surface):
        pg.draw.circle(surface, "blue", self.point, 5)
        surface.blit(
            primitive_font_render(self.name, "blue"), 
            [TEXT_RENDER_OFFSET_X + self.point[0], 
             TEXT_RENDER_OFFSET_Y + self.point[1]]
        )

class Roller(Support):
    def __init__(self, point):
        super().__init__(point, COMPONENT_TYPE.ROLLER)
        self.rY = 0
        self.rY_name = self.name + "y"

        # self.normal: list[float, float] = None
        print(
        """
Note: Pin can have a custom normal
    It is just that the engine GUI is now 
    still insufficient to perform such task

    can be considered in the future  
        """
        )

    def render(self, surface: pg.surface.Surface):
        pg.draw.circle(surface, "yellow", self.point, 5)
        surface.blit(
            primitive_font_render(self.name, "yellow"), 
            [TEXT_RENDER_OFFSET_X + self.point[0], 
             TEXT_RENDER_OFFSET_Y + self.point[1]]
        )

class Force(Component):
    def __init__(self, unit: list[float, float], pos: list[float, float], 
                 force: float, graphical_tip: list[float, float] = None):
        super().__init__(COMPONENT_TYPE.FORCE)
        self.name = get_force_name()
        self.unit: list[float, float] = unit
        self.support: Support = pos
        self.strength: float = force

        if graphical_tip is not None:
            self.graphical_tip: list[float, float] = graphical_tip
        else:
            self.graphical_tip: list[float, float] = vector2_add(
                pos,
                vector2_scale(
                    unit, force
                )
            )

    @staticmethod
    def evaluate_strength(relative: list[float, float]):
        # return  relative[0] * relative[0] + relative[1] * relative[1] 
        return vector2_mag(relative)

    def render(self, surface: pg.surface.Surface):
        pg.draw.line(surface, "magenta", self.support.point, self.graphical_tip, 2)
        pg.draw.circle(surface, "magenta", self.graphical_tip, 5)
        
        relative = vector2_relative(self.support.point, self.graphical_tip)
        surface.blit(
            primitive_font_render(str(self.strength), "magenta"),
            vector2_add(
                self.support.point,
                vector2_scale(relative, 1/2)
            ),
        )

        surface.blit(
            primitive_font_render(str(self.name), "magenta"),
            vector2_add(
                self.graphical_tip, 
                [TEXT_RENDER_OFFSET_X, TEXT_RENDER_OFFSET_Y]
            )
        )

    @property
    def vector(self):
        return vector2_scale(self.unit, self.strength)

class Member(Component):
    def __init__(self, p1: Support, p2: Support, type: COMPONENT_TYPE):
        super().__init__(type)
        self.p1: Support = p1
        self.p2: Support = p2
        self.name = self.get_member_name()
        self.unit: list[float, float] = None

    def get_member_name(self):
        if (len(self.p1.name) + len(self.p2.name) == 2):
            return self.p1.name + self.p2.name
        return self.p1.name + "_" + self.p2.name

    def render(self, surface: pg.surface.Surface):
        print("not yet implemented")
        assert(False)

class Truss(Member):
    def __init__(self, p1: Support, p2: Support):
        super().__init__(p1, p2, COMPONENT_TYPE.TRUSS)
        self.tension: float = 0

    @staticmethod
    def frame_transform(truss)->Frame:
        # frame = Frame(truss.p1, truss.p2)
        # Frame.__init__(truss, truss.p1, truss.p2)
        truss.__class__ = Frame
        Frame.__init__(truss, truss.p1, truss.p2)
        return truss

    def render(self, surface: pg.surface.Surface):
        pg.draw.line(surface, "white", self.p1.point, self.p2.point, 2)

class Frame(Member):
    def __init__(self, p1: Support, p2: Support):
        super().__init__(p1, p2, COMPONENT_TYPE.FRAME)
        self.binds: list[Support] = []

    def render(self, surface: pg.surface.Surface):
        pg.draw.line(surface, "cyan", self.p1.point, self.p2.point, 2)

    def declare_ownership(self, joint1: Support):
        self.binds.append(joint1)
        """
        print(self.name)
        print(self.binds, joint1.name)
        print([bind.name for bind in self.binds])
        print()
        """
        joint1.owning_member = self