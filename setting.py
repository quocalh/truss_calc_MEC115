import math
import pygame as pg

is_ce = getattr(pg, "IS_CE", False)
print("Is pygame-ce:", is_ce)

# text render offset
TEXT_RENDER_OFFSET_X = -16
TEXT_RENDER_OFFSET_Y = 5

ISSUE_SENSITIVITY_SQR_DIST = 250

MAGNETIC_CURSOR_PROJECTION_DIST_SENSITIVITY = 50

# triangle mesh
TRIANGLE_MESH_EDGE_LENGTH = 5
s = TRIANGLE_MESH_EDGE_LENGTH
h = s * math.sqrt(3) / 2
TRIANGLE_MESH = [
    [-s / 2, -h / 3],
    [s / 2, -h / 3],
    [0, 2 * h / 3],
]

# square mesh
SQUARE_MESH_EDGE_LENGTH = 5
s = SQUARE_MESH_EDGE_LENGTH
half = s / 2
SQUARE_MESH = [
    [-half, -half],
    [half, -half],
    [half, half],
    [-half, half],
]

# font
pg.init()
font = pg.font.init()
gui_font = pg.font.Font('cour.ttf', 24)

def primitive_font_render(text: str, color: any):
    global gui_font
    return gui_font.render(text, True, color, None)

X_GRID_DIVISOR = 20
Y_GRID_DIVISOR = X_GRID_DIVISOR

