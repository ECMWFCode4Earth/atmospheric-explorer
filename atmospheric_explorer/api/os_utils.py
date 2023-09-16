"""\
Module to gather all utility functions and classes.
"""

import os
import shutil

from atmospheric_explorer.api.loggers import atm_exp_logger


def create_folder(folder: str) -> None:
    """Create folder if it doesn't exists"""
    if not os.path.exists(folder):
        atm_exp_logger.debug("Creating folder %s", folder)
        os.makedirs(folder)


def remove_folder(folder: str) -> None:
    """Remove folder if exists"""
    if os.path.exists(folder):
        atm_exp_logger.debug("Removing folder %s", folder)
        shutil.rmtree(folder)
