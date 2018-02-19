# -*- coding: utf-8 -*-
import time

import pymunk


class Node:
    def __init__(self, position, mass, radius, friction):
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = friction

    def build(self, space):
        space.add(self.body, self.shape)


class Muscle:
    def __init__(self, a, b, period, stiffness, damping=0):
        rest_length = a.position.get_distance(b.position)
        self.constraint = pymunk.DampedSpring(a, b, (0, 0), (0, 0),
                                              rest_length, stiffness, damping)

    def build(self, space):
        space.add(self.constraint)

    @property
    def ideal_length(self):
        return 0 if self.is_contracting() else self.rest_length

    def is_contracting(self):
        return (time.time() % self.period) / self.period < .5


class Creature:
    def __init__(self, nodes, muscles):
        self.nodes = nodes
        self.muscles = muscles


def main():
    space = pymunk.Space()
    space.gravity = (0, -900)
