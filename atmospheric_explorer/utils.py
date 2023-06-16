"""\
Module to gather all utility functions and classes.
"""

import os
import platform


def get_local_folder():
    """Returns the folder where to put local files based on the user's OS."""
    # Create logs directory based on OS
    if "windows" in platform.system().lower():
        main_dir = os.path.join(os.getenv("LOCALAPPDATA") or ".", "AtmosphericExplorer")
    else:
        main_dir = os.path.join(os.getenv("HOME") or ".", ".atmospheric_explorer")
    if not os.path.exists(main_dir):
        os.makedirs(main_dir)
    return main_dir