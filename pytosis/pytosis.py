# -*- coding: utf-8 -*-
import time
import random
from itertools import zip_longest, cycle

import pymunk
import pyglet
from pyglet import gl
from pyglet.window import key

from . import utils


CODON_WIDTH = 8
LOWER_BOUND_ORDER = 64
UPPER_BOUND_ORDER = 128


class Gene:
    """
    Sequence is expected to be a sequence of ones and zeros as a string.
    Makes it easier for coding for now.
    Genetic sequences go in even rotation for now. Node-Muscle-Node

    """

    def __init__(self, sequence, codon_width=CODON_WIDTH):
        self.sequence = sequence
        self.codon_width = codon_width

    def __iter__(self):
        """
        Iterating a Gene yields its codons.
        FIXME: Should this be zero-filled at the end? Cuz it is.

        """
        seq = [self.sequence[x::self.codon_width]
               for x in range(self.codon_width)]
        for codon in zip_longest(*seq, fillvalue="0"):
            yield ''.join(codon)

    @classmethod
    def from_random(cls, codon_width=CODON_WIDTH,
                    lower=LOWER_BOUND_ORDER, upper=UPPER_BOUND_ORDER):
        number = random.randint(2 ** lower, 2 ** upper)
        sequence = bin(number)[2:]
        print(f"Making Gene from random number {number}")
        print(f"Sequence: {sequence}")
        return cls(sequence, codon_width=codon_width)

    @classmethod
    def from_creature(cls, creature):
        return [feature.to_codon() for feature in creature.features]

    def to_creature(self):
        return Creature(self)


class Feature:
    """
    Base class for all organism features like nodes and muscles.
    Who knows what features may be invented later?

    """
    parameters = {}

    def __init__(self, *args):
        self.parameters = dict(zip(self.parameters, args))

    def __iter__(self):
        yield self.__class__.__name__, self.parameters

    def to_codon(self):
        """
        FIXME: The algo for doing this is hard if possible...
        :return:
        """
        pass

    @staticmethod
    def codon_to_values(codon, num_vals):
        """
        Takes any length binary string and returns a generator of int
        values based on an even division of the bits, omitting

        :param codon: a sequence of 1s and 0s
        :param num_vals: how many values to unpack
        :return: a generator of ints num_vals in length
        """
        size = len(codon) // num_vals
        for i in range(num_vals):
            yield int(codon[i * size:size * (i + 1)], 2) + 1

    @classmethod
    def from_codon(cls, codon, count):
        print(f"{cls.__name__} from {codon}")
        values = list(cls.codon_to_values(codon, count))
        print(", ".join(f"{k}: {v}" for k, v in zip(cls.parameters, values)))
        return cls(*values)


class Node(Feature):
    """
    Nodes have radius, weight and friction.

    """
    resolution = 16
    parameters = {
        "x": None,
        "y": None,
        "radius": None,
        "mass": None,
        "friction": None
    }

    def __init__(self, *args):
        super().__init__(*args)
        moment = pymunk.moment_for_circle(self.parameters['mass'], 0,
                                          self.parameters['radius'])
        self.body = pymunk.Body(self.parameters['mass'], moment)
        self.body.position = self.parameters['x'], self.parameters['y']
        self.shape = pymunk.Circle(self.body, self.parameters['radius'])
        self.shape.friction = self.parameters['friction']

    def build(self, space):
        space.add(self.body, self.shape)

    def draw(self):
        x, y = self.body.position
        utils.draw_circle(x, y, self.shape.radius, self.resolution)


class Muscle(Feature):
    """
    Muscles have strength, length and a group they belong to.

    """
    parameters = {
        "a": None,
        "b": None,
        "period": None,
        "stiffness": None,
        "damping": None
    }

    def build(self, space):
        space.add(self.constraint)

    @property
    def ideal_length(self):
        return 0 if self.is_contracting() else self.rest_length

    def is_contracting(self):
        return (time.time() % self.parameters['period']) / \
               self.parameters['period'] < .5

    def draw(self):
        start = self.constraint.a.position + self.constraint.anchor_a
        end = self.constraint.b.position + self.constraint.anchor_b
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(*start)
        gl.glVertex2f(*end)
        gl.glEnd()


class Flagellum(Feature):
    """
    Flagella have strength and length

    """
    parameters = {
        "strength": None,
        "length": None
    }


class Creature:
    """
    These creatures are assumed (for now) to follow the structure
    Node-Muscle-Node-Muscle...

    """
    possible_features = [Node, Muscle]

    def __init__(self, gene=None, features=None):
        """
        When a creature is initialized with a Gene object, the codons are
        iterated, and if a codon ends with a 1, it is assumed to extend
        to the next nibble, yielding a longer "codon" (getting flexible
        with the terminology at this point).

        So, if your creature's genetic seqeunce is:
        0110 1110 1111 0011 1010 1100, what you would get is:
        0110 1110 111100111010 1100. The trailing 1 on the codons,
        1111 and 0011, cause the interpreter to to read those codons
        as a larger number. Admittedly, this could be smarter.

        :param gene:
        """
        if gene:
            self._from_gene(gene)
        elif features:
            self._from_features(features)
        else:
            raise Exception("No gene or features specified.")

    def __iter__(self):
        keys = "features", "gene"
        features = [dict(feature) for feature in self.features]
        gene = self.gene.sequence
        for k, v in zip(keys, (features, gene)):
            yield k, v

    @classmethod
    def from_random(cls, codon_width=CODON_WIDTH):
        return cls(Gene.from_random(codon_width=codon_width))

    def _from_gene(self, gene):
        if type(gene) == Gene:
            self.gene = gene
        else:
            self.gene = Gene(sequence=gene)

        self.features = []
        self._cycle_features = cycle(self.possible_features)
        codon = ''
        for unit in self.gene:
            codon += unit
            if unit[-1] != '1':
                self.make_feature(codon)
                codon = ''

        if codon:
            self.make_feature(codon)

    def _from_features(self, features):
        self.features = features

    def make_feature(self, codon):
        feature = next(self._cycle_features)
        self.features.append(
            feature.from_codon(codon, len(feature.parameters)))

    def build(self, space):
        self.connect_muscles()
        for feature in self.features:
            feature.build(space)

    def connect_muscles(self):
        nodes = self.features[::2]
        muscles = self.features[1::2]
        for muscle in muscles:
            a = nodes[muscle.parameters['a'] % len(nodes)].body
            b = nodes[muscle.parameters['b'] % len(nodes)].body
            muscle.rest_length = a.position.get_distance(b.position)
            muscle.constraint = pymunk.DampedSpring(a, b, (0, 0), (0, 0),
                                                    muscle.rest_length,
                                                    muscle.parameters['stiffness'],
                                                    muscle.parameters['damping'])

    def draw(self):
        gl.glColor4f(0, 0, 0, 1)
        for obj in self.features:
            obj.draw()


class Swimmer(Creature):
    """
    This is how an organism with Flagella might look.

    """
    possible_features = [Node, Flagellum, Muscle]


class SimulationWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = pymunk.Space()
        self.space.gravity = 0, -900
        self.objects = []
        self.label = pyglet.text.Label('Press [X] to exit', x=10, y=10,
                                       color=(0, 0, 0, 255))
        gl.glClearColor(1, 0, 0, 1)

    def add_object(self, *objects):
        self.objects.extend(objects)
        for obj in objects:
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
