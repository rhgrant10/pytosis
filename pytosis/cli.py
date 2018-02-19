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


def create_simulation(n):
    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()

    template = pyglet.gl.Config(alpha_size=8)
    config = screen.get_best_config(template)
    context = config.create_context(None)

    nodes = [Node.from_random() for __ in range(n)]
    muscles = [Muscle.from_random(a, b) for a, b in pairwise(nodes)]
    creature = Creature(nodes=nodes, muscles=muscles)

    window = SimulationWindow(fullscreen=False, context=context)
    window.add_object(creature)
    pyglet.clock.schedule(window.update)


@click.command()
@click.option('--n', default=5)
def main(n):
    create_simulation(n)
    pyglet.app.run()


if __name__ == "__main__":
    import sys
    sys.exit(main())
