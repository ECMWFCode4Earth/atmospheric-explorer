"""\
Functionalities to manage logs.
"""
from pprint import pprint

import click

from atmospheric_explorer.api.loggers.loggers_utils import clear_logs, list_logs


@click.group()
def logs():
    # pylint: disable=unnecessary-pass
    """Command to interact with logs"""
    pass


@logs.command("list")
def _():
    """List all logs"""
    pprint(list_logs())


@logs.command("clear")
def _():
    """Clear all logs"""
    clear_logs()
