"""\
Module for building the UI and running the app
"""
from pathlib import Path

# pylint: disable=invalid-name
import click
from streamlit.web.bootstrap import run

from atmospheric_explorer.cli.os_manager import data, logs
from atmospheric_explorer.cli.plotting.plots import plot


@click.group()
def main():
    # pylint: disable=unnecessary-pass
    """Main entry point"""
    pass


@main.command("run")
def run_app():
    """Run this app"""
    run(
        f"{Path(__file__).resolve().parent.parent.joinpath('ui', 'Home.py')}",
        "",
        [],
        {},
    )


main.add_command(data)
main.add_command(logs)
main.add_command(plot)
