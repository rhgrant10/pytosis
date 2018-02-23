# -*- coding: utf-8 -*-

"""Console script for pytosis."""
import itertools

import click
import pyglet

from .pytosis import Creature, SimulationWindow


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)


def create_simulation(n, fullscreen=True):
    config = pyglet.gl.Config(double_buffer=True)
    window = SimulationWindow(fullscreen=fullscreen, config=config)

    creatures = [Creature.from_random() for _ in range(n)]

    window.add_object(*creatures)
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
def make_creature(count):
    """Simple demo to show pytosis in action."""
    for _ in range(count):
        click.echo(dict(Creature.from_random()))


if __name__ == "__main__":
    import sys

    sys.exit(main())
