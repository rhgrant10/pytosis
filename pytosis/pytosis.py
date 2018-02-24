# -*- coding: utf-8 -*-
import time
import random
from itertools import combinations

import pymunk
from pyglet import gl

from . import utils
from . import settings


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
        gl.glColor3f(1, self.shape.friction / 2, 1)
        utils.draw_circle(*self.body.position, self.shape.radius, self.resolution)


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
        gl.glLineWidth(self.constraint.stiffness)
        gl.glColor3f(self.constraint.damping, 1, 1)
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
        for obj in self.muscles + self.nodes:
            obj.draw()

    def move(self, x, y):
        for node in self.nodes:
            node.body.position += x, y

    @classmethod
    def from_random(cls, max_nodes=None):
        max_nodes = max_nodes or settings.MAX_NODES
        num_nodes = random.randint(3, max_nodes)
        num_muscles = random.randint(num_nodes, sum(range(num_nodes)))

        nodes = [Node.from_random() for _ in range(num_nodes)]
        muscle_pairs = list(combinations(nodes, 2))

        muscles = []
        for a, b in random.sample(muscle_pairs, num_muscles):
            muscles.append(Muscle.from_random(a, b))
        return cls(nodes, muscles)
