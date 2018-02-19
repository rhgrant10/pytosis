# -*- coding: utf-8 -*-

"""Console script for pytosis."""
import itertools

import click
import pyglet

from .pytosis import Node, Muscle, Creature, SimulationWindow


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)


def create_simulation(n, fullscreen=True):
    config = pyglet.gl.Config(double_buffer=True)
    window = SimulationWindow(fullscreen=fullscreen, config=config)
    w, h = window.get_size()

    nodes = [Node.from_random(max_x=w // 2, max_y=h // 2) for __ in range(n)]
    muscles = [Muscle.from_random(a, b) for a, b in pairwise(nodes)]
    creature = Creature(nodes=nodes, muscles=muscles)

    window.add_object(creature)
    pyglet.clock.schedule(window.update)


@click.command()
@click.option('--fullscreen/--no-fullscreen', default=True)
@click.option('--n', default=5)
def main(n, fullscreen):
    create_simulation(n, fullscreen)
    pyglet.app.run()


if __name__ == "__main__":
    import sys
    sys.exit(main())
