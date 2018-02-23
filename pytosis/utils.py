# -*- coding: utf-8 -*-
import math
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
        self.label = pyglet.text.Label('Press [X] to exit', x=10, y=10,
                                       color=(0, 0, 0, 255))
        gl.glClearColor(1, 0, 0, 1)

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
        if symbol == key.X:
            self.close()

    def update(self, dt):
        self.space.step(dt)

    def draw_ground(self):
        width, height = self.get_size()
        gl.glColor4f(0, 1, 0, 1)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(0, 0)
        gl.glVertex2f(0, 100)
        gl.glVertex2f(width, 100)
        gl.glVertex2f(width, 0)
        gl.glEnd()
        gl.glColor4f(1, 1, 1, 1)


def draw_circle(x, y, r, points=16):
    step = 2 * math.pi / points
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    for theta in [i * step for i in range(points + 1)]:
        gl.glVertex2f(x + r * math.cos(theta),
                      y + r * math.sin(theta))
    gl.glEnd()


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)


def add_creature(huh, window, creatures):
    print('Creatures left: ', len(creatures))
    creature = creatures.pop(0)
    window.add_object(creature)
    print('Creature {} added'.format(creature))


def create_simulation(creatures, fullscreen=True):
    config = gl.Config(double_buffer=True)
    window = SimulationWindow(fullscreen=fullscreen, config=config)
    add_creature(None, window, creatures)
    clock.schedule_interval(add_creature, .5, window, creatures)
    clock.schedule(window.update)
