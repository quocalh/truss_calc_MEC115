import math

def vector2_relative(p1: list[float], p2: list[float]) -> list[float]:
    return [p2[0] - p1[0], p2[1] - p1[1]]

def vector2_sub(p1: list[float], p2: list[float]) -> list[float]:
    return [p1[0] - p2[0], p1[1] - p2[1]]

def vector2_scale(v: list[float], scale: float) -> list[float]:
    return [v[0] * scale, v[1] * scale]

def vector2_add(p1: list[float], p2: list[float]) -> list[float]:
    return [p1[0] + p2[0], p1[1] + p2[1]]

def vector2_mag(v: list[float, float]):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def vector2_sqr_mag(v: list[float, float]):
    return v[0] * v[0] + v[1] * v[1]

def vector2_unit(v: list[float, float]):
    l = vector2_mag(v) 
    return [v[0] / l, v[1] / l]

