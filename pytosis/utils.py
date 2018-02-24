# -*- coding: utf-8 -*-
from math import pi, cos, sin
import itertools

import pymunk
import pyglet
from pyglet import gl, clock
from pyglet.window import key


class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = pymunk.Space()
        self.space.gravity = 0, -90
        self.objects = []
        self.label = pyglet.text.Label('Press [Q] to exit', x=10, y=10,
                                       color=(0, 0, 0, 255))
        gl.glClearColor(0, 0, 0, 1)

    def add_object(self, *objects):
        w, h = self.get_size()
        dx = w // 2
        dy = h
        self.objects.extend(objects)
        for obj in objects:
            obj.move(dx, dy)
            obj.build(self.space)

    def on_draw(self):
        self.clear()
        self.draw_ground()
        for obj in self.objects:
            obj.draw()
        self.label.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self.close()

    def update(self, dt):
        self.space.step(dt)

    def draw_ground(self):
        width, height = self.get_size()
        gl.glColor4f(.3, .3, .3, 1)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(0, 0)
        gl.glVertex2f(0, 100)
        gl.glVertex2f(width, 100)
        gl.glVertex2f(width, 0)
        gl.glEnd()


def fill_circle(x, y, r, num_points=None):
    points = num_points or int(r * 1.6)
    step = 2 * pi / points
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    for theta in [i * step for i in range(points + 1)]:
        gl.glVertex2f(x + r * cos(theta),
                      y + r * sin(theta))
    gl.glEnd()


def stroke_circle(x, y, r, num_points=None):
    points = num_points or int(r * 1.6)
    step = 2 * pi / points
    angles = [i * step for i in range(points)]
    points = [(x + r * cos(t), y + r * sin(t)) for t in angles]

    gl.glBegin(gl.GL_LINE_LOOP)
    for x, y in points:
        gl.glVertex2f(x, y)
    gl.glEnd()


def draw_circle(*args, fill=True, **kwargs):
    if fill:
        return fill_circle(*args, **kwargs)
    else:
        return stroke_circle(*args, **kwargs)


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)


def add_creature(huh, window, creatures):
    try:
        creature = creatures.pop(0)
        window.add_object(creature)
    except Exception:
        print(f'Failed to add a creature: {creature}')


def create_simulation(creatures, fullscreen=True):
    config = gl.Config(alpha_size=8, double_buffer=True)
    window = SimulationWindow(fullscreen=fullscreen, config=config)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    add_creature(None, window, creatures)
    clock.schedule_interval(add_creature, 2, window, creatures)
    clock.schedule(window.update)
