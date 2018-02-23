# -*- coding: utf-8 -*-
import math

from pyglet import gl


def draw_circle(x, y, r, points=16):
    step = 2 * math.pi / points
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    for theta in [i * step for i in range(points + 1)]:
        gl.glVertex2f(x + r * math.cos(theta),
                      y + r * math.sin(theta))
    gl.glEnd()
