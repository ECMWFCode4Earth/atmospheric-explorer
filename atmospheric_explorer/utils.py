"""\
Module to gather all utility functions and classes.
"""

import os
import platform

import plotly.graph_objects as go


def get_local_folder():
    """Returns the folder where to put local files based on the user's OS"""
    if "windows" in platform.system().lower():
        main_dir = os.path.join(os.getenv("LOCALAPPDATA") or ".", "AtmosphericExplorer")
    else:
        main_dir = os.path.join(os.getenv("HOME") or ".", ".atmospheric_explorer")
    if not os.path.exists(main_dir):
        os.makedirs(main_dir)
    return main_dir


def create_folder(folder: str) -> None:
    """Create data folder if it doensn't exists"""
    if not os.path.exists(folder):
        os.makedirs(folder)


def hex_to_rgb(hex_color: str) -> tuple:
    """\
    Converts an hex color to a rgb tuple.
    If an rgba color is provided, this function will return its rgb tuple and ignore the alpha channel.
    """
    if hex_color.startswith("#"):
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = hex_color * 2
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return tuple(hex_color.strip("rgba()").split(",")[:3])


def save_plotly_to_image(fig: go.Figure, path: str, img_format: str = "png") -> None:
    """Save plotly plot to static image"""
    fig.to_image(path, format=img_format)
