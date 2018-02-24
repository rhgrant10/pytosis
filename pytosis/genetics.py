# -*- coding: utf-8 -*-
import random

from . import settings


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
