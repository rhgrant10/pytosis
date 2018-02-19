# -*- coding: utf-8 -*-
import time
import random
import math

import pymunk
import pyglet
from pyglet import gl
from pyglet.window import key


def draw_cirlce(x, y, r, points=16):
    step = 2 * math.pi / points
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    for theta in [i * step for i in range(points)]:
        gl.glVertex2f(x + r * math.cos(theta),
                      y + r * math.sin(theta))
    gl.glEnd()


class Node:
    resolution = 16

    def __init__(self, position, mass, radius, friction):
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = friction

    @classmethod
    def from_random(cls, max_x=100, max_y=100, max_r=15, max_m=100, max_f=2):
        x = random.random() * max_x + 100
        y = random.random() * max_y + 100
        r = random.random() * max_r
        m = random.random() * max_m
        f = random.random() * max_f
        return cls(position=(x, y), mass=m, radius=r, friction=f)

    def build(self, space):
        space.add(self.body, self.shape)

    def draw(self):
        draw_cirlce(*self.body.position, self.shape.radius, self.resolution)


class Muscle:
    def __init__(self, a, b, period, stiffness, damping):
        rest_length = a.position.get_distance(b.position)
        self.constraint = pymunk.DampedSpring(a, b, (0, 0), (0, 0),
                                              rest_length, stiffness, damping)

    @classmethod
    def from_random(cls, a, b, max_p=60, max_s=10, max_d=1):
        p = random.random() * max_p
        s = random.random() * max_s
        d = random.random() * max_d
        return cls(a=a.body, b=b.body, period=p, stiffness=s, damping=d)

    def build(self, space):
        space.add(self.constraint)

    @property
    def ideal_length(self):
        return 0 if self.is_contracting() else self.rest_length

    def is_contracting(self):
        return (time.time() % self.period) / self.period < .5

    def draw(self):
        start = self.constraint.a.position + self.constraint.anchor_a
        end = self.constraint.b.position + self.constraint.anchor_b
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(*start)
        gl.glVertex2f(*end)
        gl.glEnd()


class Creature:
    def __init__(self, nodes, muscles):
        self.nodes = nodes
        self.muscles = muscles

    def build(self, space):
        for node in self.nodes:
            node.build(space)
        for muscle in self.muscles:
            muscle.build(space)

    def draw(self):
        for obj in self.nodes + self.muscles:
            obj.draw()


class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # kwargs['fullscreen'] = True
        super().__init__(*args, **kwargs)
        self.space = pymunk.Space()
        self.space.gravity = 0, -900
        self.objects = []
        gl.glClearColor(1, 0, 0, 1)

    def add_object(self, *objects):
        self.objects.extend(objects)
        for obj in objects:
            obj.build(self.space)

    def on_draw(self):
        self.clear()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        width, height = self.get_size()
        draw_cirlce(width // 2, height // 2, r=min(width, height) // 4)
        self.draw_ground()
        for obj in self.objects:
            obj.draw()

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
