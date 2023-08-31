"""\
Module to gather all utility functions and classes.
"""

import os
import platform
import shutil


def get_local_folder():
    """Returns the folder where to put local files based on the user's OS"""
    if "windows" in platform.system().lower():
        main_dir = os.path.join(os.getenv("LOCALAPPDATA") or ".", "AtmosphericExplorer")
    else:
        main_dir = os.path.join(os.getenv("HOME") or ".", ".atmospheric_explorer")
    create_folder(main_dir)
    return main_dir


def create_folder(folder: str) -> None:
    """Create folder if it doesn't exists"""
    if not os.path.exists(folder):
        os.makedirs(folder)


def remove_folder(folder: str) -> None:
    """Remove folder if it doesn't exists"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
