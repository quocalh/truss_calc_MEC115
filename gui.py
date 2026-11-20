import pygame as pg

from components import *
from setting import *

def magnetic_mouse_pos_closest( mouse_pos: list[float, float], grid_x: float, grid_y: float):
    corner = (
        (mouse_pos[0] // grid_x) * grid_x,
        (mouse_pos[1] // grid_y) * grid_y,
    )

    offset = (
        (0, 0),
        (grid_x, 0),
        (0, grid_y),
        (grid_x, grid_y),
    )

    closest = None
    closest_sqr_dist = float("inf")

    for v in offset:
        point = vector2_add(corner, v)

        dist = vector2_sqr_mag(
            vector2_relative(
                mouse_pos, point
            )
        )

        if dist < closest_sqr_dist:
            closest_sqr_dist = dist
            closest = point

    return closest

def render_magnetic_grid(surface: pg.surface.Surface, width: float, height: float):
    x_unit = width / X_GRID_DIVISOR
    y_unit = height / Y_GRID_DIVISOR
    for x in range(X_GRID_DIVISOR):
        pg.draw.line(
            surface, "white", 
            (x * x_unit, 0),
            (x * x_unit, height), 1
        )
    for y in range(Y_GRID_DIVISOR):
        pg.draw.line(
            surface, "white",
            (0, y * y_unit),
            (width, y * y_unit), 1
        )
