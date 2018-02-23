# -*- coding: utf-8 -*-

"""Console script for pytosis."""
import click
import pyglet

from .pytosis import Creature
from .utils import create_simulation


@click.group()
def main():
    """Console script for pytosis."""
    click.echo("Starting Pytosis")
    click.echo("See documentation at https://github.com/rhgrant10/pytosis/")


@main.command()
@click.option('--fullscreen/--no-fullscreen', default=True)
@click.option('--n', default=5)
def make_simulation(n, fullscreen):
    creatures = [Creature.from_random() for _ in range(n)]
    create_simulation(creatures, fullscreen)
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
