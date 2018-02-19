# -*- coding: utf-8 -*-

"""Console script for pytosis."""

import click

from pytosis.pytosis import Gene, Creature, Swimmer


@click.group()
def main():
    """Console script for pytosis."""
    click.echo("Starting Pytosis")
    click.echo("See documentation at https://github.com/rhgrant10/pytosis/")


@main.command()
@click.option('--count', default=1, help='Number of creatures to make.')
@click.option('--codon-width', type=int, default=4, help='How many bits long the smallest codon is.')
def demo(count, codon_width):
    """Simple demo to show pytosis in action."""
    for x in range(count):
        click.echo(dict(Gene.from_random(unit_size=codon_width).to_creature()))


if __name__ == "__main__":
    import sys
    sys.exit(main())
