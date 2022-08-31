import logging

import click

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("name")
def hello(name):
    logging.info(f"Hello, {name}!")


if __name__ == "__main__":
    hello()
