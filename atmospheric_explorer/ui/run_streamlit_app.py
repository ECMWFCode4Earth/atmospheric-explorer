"""\
Module for building the UI
"""
from pathlib import Path

# pylint: disable=invalid-name
import click
from streamlit.web.bootstrap import run


@click.command()
def run_streamlit_app():
    """Run this app from a simple cli command"""
    run(f"{Path(__file__).resolve().parent.joinpath('Home.py')}", "", [], {})


if __name__ == "__main__":
    run_streamlit_app()
