# -*- coding: utf-8 -*-
import json
import random

from itertools import zip_longest, cycle


class Gene:
    """
    Sequence is expected to be a sequence of ones and zeros as a string.
    Makes it easier for coding for now.
    Genetic sequences go in even rotation for now. Node-Muscle-Node

    """

    def __init__(self, sequence, unit_size=4):
        self.sequence = sequence
        self.unit_size = unit_size

    def __iter__(self):
        """
        Iterating a Gene yields its codons.
        FIXME: Should this be zero-filled at the end? Cuz it is.

        """
        seq = [self.sequence[x::self.unit_size] for x in range(self.unit_size)]
        for codon in zip_longest(*seq, fillvalue="0"):
            yield ''.join(codon)

    @classmethod
    def from_random(cls, unit_size=4):
        # Init the Gene with a random number 31 to 32 bits long
        number = random.randint(2 ** 31, 2 ** 64)
        sequence = bin(number)[2:]
        print(f"Making Gene from random number {number}")
        print(f"Sequence: {sequence}")
        return cls(sequence, unit_size=unit_size)

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
    parameters = {
        "radius": None,
        "weight": None,
        "friction": None
    }


class Muscle(Feature):
    """
    Muscles have strength, length and a group they belong to.

    """
    parameters = {
        "strength": None,
        "length": None,
        "group": None
    }


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
            self._from_gene(gene, features or [])
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
        return cls(Gene.from_random())

    def _from_gene(self, gene, features):
        self.gene = gene
        self.features = features
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


class Swimmer(Creature):
    """
    This is how an organism with Flagella might look.

    """
    possible_features = [Node, Flagellum, Muscle]

