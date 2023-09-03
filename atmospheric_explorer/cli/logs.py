"""\
Functionalities to manage logs.
"""
from pprint import pprint

import click

from atmospheric_explorer.api.loggers import Loggers


@click.group()
def logs():
    # pylint: disable=unnecessary-pass
    """Command to interact with logs"""
    pass


@logs.command("list")
def _():
    """List all logs"""
    pprint(Loggers.list_logs())


@logs.command("clear")
def _():
    """Clear all logs"""
    Loggers.clear_logs()
