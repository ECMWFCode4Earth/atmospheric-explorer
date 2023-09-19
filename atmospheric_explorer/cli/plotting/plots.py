"""\
Plotting CLI entry point.
"""
import click

from atmospheric_explorer.cli.plotting.anomalies import anomalies
from atmospheric_explorer.cli.plotting.hovmoeller import hovmoeller
from atmospheric_explorer.cli.plotting.yearly_flux import yearly_flux


@click.group()
def plot():
    # pylint: disable=unnecessary-pass
    """Plotting CLI"""
    pass


plot.add_command(anomalies)
plot.add_command(hovmoeller)
plot.add_command(yearly_flux)
