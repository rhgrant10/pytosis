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
        return cls(bin(random.randint(2 ** 31, 2 ** 64))[2:])

    @classmethod
    def from_creature(cls, creature):
        return [feature.to_codon for feature in creature.features]

    def to_creature(self):
        return Creature(self)


class CodonsToValuesMixin:
    @staticmethod
    def codons_to_values(codons, num_vals):
        size = len(codons) // num_vals
        for i in range(num_vals):
            yield int(codons[i * size:size * (i + 1)], 2) + 1


class Node(CodonsToValuesMixin):
    """
    Nodes have radius, weight and friction.
    """
    def __init__(self, radius, weight, friction):
        self.radius = radius
        self.weight = weight
        self.friction = friction

    def to_codon(self):
        pass

    @classmethod
    def from_codons(cls, codons):
        print(f"Node <{codons}>")
        radius, weight, friction = cls.codons_to_values(codons, 3)
        print(f"radius {radius}, weight: {weight}, friction: {friction}")
        return cls(radius, weight, friction)


class Muscle(CodonsToValuesMixin):
    """

    """

    def __init__(self, strength, length, group):
        self.strength = strength
        self.length = length
        self.group = group

    @classmethod
    def from_codons(cls, codons):
        print(f"Muscle <{codons}>")
        strength, length, group = cls.codons_to_values(codons, 3)
        print(f"strength {strength}, length: {length}, group: {group}")
        return cls(strength, length, group)


class Creature:
    """
    These creatures are assumed (for now) to follow the structure
    Node-Muscle-Node-Muscle...

    """
    features = [Node, Muscle]

    def __init__(self, gene):
        self.genes = gene
        self.parts = []
        cycle_features = cycle(self.features)
        codons = []
        for i, codon in enumerate(self.genes):
            codons.append(codon)

            # If the codon ends with a one, read the next one
            if codon[-1] != '1':
                cls = next(cycle_features)
                self.parts.append(cls.from_codons(''.join(codons)))
                codons = []

    @classmethod
    def from_random(cls):
        return cls(Gene.from_random())


if __name__ == "__main__":
    Creature.from_random()
