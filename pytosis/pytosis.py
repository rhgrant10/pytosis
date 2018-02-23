# -*- coding: utf-8 -*-
import time
import random
from itertools import cycle

import pymunk
from pyglet import gl


from . import settings
from . import utils


class InsufficientEntropyError(ValueError):
    pass


class Rna:
    """
    Each bit represents a base. Thus DNA is a sequence of
    bits, together taken as an integer. Every 4 bits
    is a codon, where a codon can come in 2 types:

      1. numeric codon (nibble values 0 - 9)
      2. separator codon (nibble values 10-15)

    There is a special type of separator codon known as
    the stop codon, which has nibble value 15. Finding
    3 stop codons in a row signifies the end of the DNA
    sequence.

    """
    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        """
        Shortcut to read codons.

        """
        for codon in self.read():
            yield codon

    @classmethod
    def _find_start(cls, sequence):
        starts = 0
        for index, gene in enumerate(sequence):
            if cls.is_separator(gene):
                starts += 1
            else:
                starts = 0
            if starts > 2:
                return index

    @classmethod
    def read_to_stop(cls, sequence):
        values = []
        stops = 0
        for gene in sequence:
            if cls.is_separator(gene):
                if values:
                    yield int(''.join(values))
                    values = []
                    stops = 0
                elif cls.is_stop(gene):
                    # stop when more than 2 stops consecutively
                    stops += 1
                    if stops == settings.STOPS_NEEDED:
                        print('STOP found')
                        return
            else:
                stops = 0
                values.append(str(gene))
        print('No stop found!')

    def get_start(self):
        return self.__class__._find_start(iter(self.sequence))

    def read(self):
        sequence = iter(self.sequence)
        self.__class__._find_start(sequence)
        return self.__class__.read_to_stop(sequence)

    @classmethod
    def is_separator(cls, codon):
        return codon > settings.MAX_CODON

    @classmethod
    def is_stop(cls, codon):
        return codon == settings.STOP_CODON

    @classmethod
    def from_random(cls):
        sequence = []
        for __ in range(settings.GENE_COUNT):
            sequence.append(random.getrandbits(settings.CODON_WIDTH))
        r = random.randint(10, 20)
        sequence[-r:] = [settings.STOP_CODON] * r

        return cls(sequence)


class Feature:
    """
    Base class for all organism features like nodes and muscles.
    Who knows what features may be invented later?

    """
    parameters = {}

    def __init__(self, codon, *args):
        self.codon = codon
        self.parameters = dict(zip(self.parameters, args))

    def __iter__(self):
        yield self.__class__.__name__, self.parameters

    def to_codon(self):
        """
        Fixed ;)
        """
        return self.codon

    @staticmethod
    def codon_to_values(codon, num_vals):
        """
        Takes an int and converts it to a binary string and returns a
        generator of int values based on an even-ish division of the bits.

        :param codon: int
        :param num_vals: how many values to unpack
        :return: a generator of ints num_vals in length
        """
        codon = bin(codon)[2:]
        size = len(codon) // num_vals
        for i in range(num_vals):
            try:
                yield int(codon[i * size:size * (i + 1)], 2) + 1
            except ValueError as e:
                print(f'Codon {codon} lacks sufficient '
                      f'entropy ({num_vals}) for feature - dropping.')
                raise InsufficientEntropyError()

    @classmethod
    def from_codon(cls, codon, count):
        print(f"{cls.__name__} from {codon}")
        values = list(cls.codon_to_values(codon, count))
        print(", ".join(f"{k}: {v}" for k, v in zip(cls.parameters, values)))
        return cls(codon, *values)


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
        self.body.position = self.parameters['x'] + 250, self.parameters['y'] + 250
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
        time_slice = time.time() % self.parameters['period']
        alpha = time_slice / self.parameters['period']
        return alpha < .5

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
    def from_random(cls):
        return cls(Rna.from_random())

    def _from_gene(self, gene):
        if type(gene) == Rna:
            self.gene = gene
        else:
            self.gene = Rna(sequence=gene)

        self.features = []
        self._cycle_features = cycle(self.possible_features)
        for codon in self.gene:
            try:
                self.make_feature(codon)
            except InsufficientEntropyError:
                continue

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
        nodes = [f for f in self.features if type(f) == Node]
        muscles = [f for f in self.features if type(f) == Muscle]
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
