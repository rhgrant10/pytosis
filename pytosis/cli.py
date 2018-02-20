# -*- coding: utf-8 -*-

"""Console script for pytosis."""
import itertools

import click
import pyglet

from .pytosis import Gene, Node, Muscle, Creature, SimulationWindow


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)


def create_simulation(n, fullscreen=True):
    config = pyglet.gl.Config(double_buffer=True)
    window = SimulationWindow(fullscreen=fullscreen, config=config)
    w, h = window.get_size()

    # nodes = [Node.from_random(max_x=w // 2, max_y=h // 2) for __ in range(n)]
    # muscles = [Muscle.from_random(a, b) for a, b in pairwise(nodes)]
    # creature = Creature(nodes=nodes, muscles=muscles)

    creature = Gene.from_random().to_creature()

    window.add_object(creature)
    pyglet.clock.schedule(window.update)


@click.group()
def main():
    """Console script for pytosis."""
    click.echo("Starting Pytosis")
    click.echo("See documentation at https://github.com/rhgrant10/pytosis/")


@main.command()
@click.option('--fullscreen/--no-fullscreen', default=True)
@click.option('--n', default=5)
def make_simulation(n, fullscreen):
    create_simulation(n, fullscreen)
    pyglet.app.run()


@main.command()
@click.option('--count', default=1, help='Number of creatures to make.')
@click.option('--codon-width', type=int, default=8,
              help='How many bits long the smallest codon is.')
def make_creature(count, codon_width):
    """Simple demo to show pytosis in action."""
    for x in range(count):
        click.echo(dict(Gene.from_random(unit_size=codon_width).to_creature()))


if __name__ == "__main__":
    import sys

    sys.exit(main())
