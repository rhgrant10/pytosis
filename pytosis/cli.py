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


if __name__ == "__main__":
    import sys

    sys.exit(main())
