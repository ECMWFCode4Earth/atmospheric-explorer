import os
from glob import glob
from pprint import pprint

import click

from atmospheric_explorer.api.data_interface import CAMSDataInterface
from atmospheric_explorer.api.loggers import Loggers
from atmospheric_explorer.api.os_manager import remove_folder


@click.group()
def data():
    """Command to interact with downloaded data"""
    pass


@data.command("clear")
def _():
    """Clear all downloaded data"""
    remove_folder(CAMSDataInterface._data_folder)


@data.command("list")
def _():
    """List all downloaded data files"""
    pprint(glob(os.path.join(CAMSDataInterface._data_folder, "**"), recursive=True))


@click.group()
def logs():
    """Command to interact with logs"""
    pass


@logs.command("list")
def _():
    """List all logs"""
    pprint(glob(os.path.join(Loggers._logs_root_dir, "**"), recursive=True))


@logs.command("clear")
def _():
    """Clear all logs"""
    remove_folder(Loggers._logs_root_dir)
