"""\
Module to define the main logger and a few logging utils.
"""
import os
from glob import glob

from atmospheric_explorer.api.loggers.loggers import Logger
from atmospheric_explorer.api.os_utils import remove_folder


def list_logs() -> list:
    """List all log files."""
    return glob(os.path.join(Logger.logs_root_dir, "**"), recursive=True)


def clear_logs() -> list:
    """Clear all log files."""
    remove_folder(Logger.logs_root_dir)
