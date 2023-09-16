"""\
Module to define the main logger and a few logging utils.
"""
import os
import shutil
from glob import glob

from atmospheric_explorer.api.loggers.loggers import Logger


def list_logs() -> list:
    """List all log files."""
    return glob(os.path.join(Logger.logs_root_dir, "**"), recursive=True)


def clear_logs() -> list:
    """Clear all log files."""
    if os.path.exists(Logger.logs_root_dir):
        shutil.rmtree(Logger.logs_root_dir)
