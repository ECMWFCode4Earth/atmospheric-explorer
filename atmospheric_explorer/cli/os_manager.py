"""\
Functionalities to manage files and local filesystem.
"""
from pprint import pprint

import click

from atmospheric_explorer.api.data_interface import CAMSDataInterface


@click.group()
def data():
    # pylint: disable=unnecessary-pass
    """Command to interact with downloaded data"""
    pass


@data.command("clear")
def _():
    """Clear all downloaded data"""
    CAMSDataInterface.clear_data_files()


@data.command("list")
def _():
    """List all downloaded data files"""
    pprint(CAMSDataInterface.list_data_files())
