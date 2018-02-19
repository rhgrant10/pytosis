# -*- coding: utf-8 -*-
import random

from itertools import zip_longest, cycle


class Gene:
    """
    Sequence is expected to be a sequence of ones and zeros as a string.
    Makes it easier for coding for now.
    Genetic sequences go in even rotation for now. Node-Muscle-Node

    """

    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        """
        Iterating a Gene yields nibbles - 4 bit codons

        FIXME: Should this be zero-filled at the end? Cuz it is.

        """
        seq = [self.sequence[x::4] for x in range(4)]
        for codon in zip_longest(*seq, fillvalue="0"):
            yield ''.join(codon)

    @classmethod
    def from_random(cls):
        # Init the Gene with a random number 31 to 32 bits long
        number = random.randint(2 ** 31, 2 ** 64)
        sequence = bin(number)[2:]
        print(f"Making Gene from random number {number}")
        print(f"Sequence: {sequence}")

        return cls(sequence)

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

    def to_codon(self):
        """
        FIXME: The algo for doing this is hard if possible...
        :return:
        """
        pass

    @staticmethod
    def codons_to_values(codons, num_vals):
        size = len(codons) // num_vals
        for i in range(num_vals):
            yield int(codons[i * size:size * (i + 1)], 2) + 1

    @classmethod
    def from_codons(cls, codons, count):
        print(f"{cls.__name__} from {codons}")
        values = list(cls.codons_to_values(codons, count))
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

    def __init__(self, gene):
        self.genes = gene
        self.features = []
        cycle_features = cycle(self.possible_features)
        codons = []
        for i, codon in enumerate(self.genes):
            codons.append(codon)

            # If the codon ends with a one, read the next one.
            # Else, create the feature and add it to the organism.
            if codon[-1] != '1':
                cls = next(cycle_features)
                self.features.append(
                    cls.from_codons(''.join(codons), len(cls.parameters)))

                codons = []

    @classmethod
    def from_random(cls):
        return cls(Gene.from_random())


class Swimmer(Creature):
    """
    This is how an organism with Flagella might look.

    """
    possible_features = [Node, Flagellum, Muscle]


if __name__ == "__main__":
    Creature.from_random()
    Swimmer.from_random()
