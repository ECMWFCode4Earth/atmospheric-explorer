"""\
Yearly flux plot CLI.
"""
from textwrap import dedent

import click

from atmospheric_explorer.api.data_interface.ghg.ghg_config import GHGConfig
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.yearly_flux import (
    ghg_surface_satellite_yearly_plot,
)
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.cli.plotting.utils import comma_separated_list

logger = get_logger("atmexp")


def command_change_options():
    """Function needed to change behaviour of the click option var_name."""

    class CommandOptionRequiredClass(click.Command):
        """Class to override typical command behaviour in click."""

        def invoke(self, ctx):
            """Add dynamical check on parameter var_name based on parameter data_variable."""
            data_variable = ctx.params["data_variable"]
            var_name = ctx.params["var_name"]
            var_names = GHGConfig.get_var_names(
                data_variable=data_variable,
                quantity="surface_flux",
                time_aggregation="monthly_mean",
            )
            if var_name not in var_names:
                raise click.ClickException(
                    f"Var name '{var_name}' not present in the dataset, please select one of {var_names}"
                )
            super().invoke(ctx)

    return CommandOptionRequiredClass


@click.command(cls=command_change_options())
@click.option(
    "--data-variable",
    "-v",
    required=True,
    type=click.Choice(GHGConfig.get_config()["variables"].keys()),
    help="Data variable",
    is_eager=True,
)
@click.option(
    "--years",
    "-y",
    required=True,
    type=str,
    help="Comma separated list of years, e.g. 2019,2020,2021",
    callback=comma_separated_list,
)
@click.option(
    "--months",
    "-m",
    required=True,
    multiple=True,
    type=click.Choice(GHGConfig.get_config()["months"]),
    help="""\
    Month. Multiple values can be chosen calling this option multiple times, e.g. -m 01 -m 02
    """,
)
@click.option("--title", required=True, type=str, help="Plot title")
@click.option("--var-name", required=True, type=str, help="Column name")
@click.option(
    "--output-file", required=True, type=str, help="Absolute path of the image file"
)
@click.option(
    "--entities",
    required=False,
    default="",
    type=str,
    help=dedent(
        """\
    Comma separated list of entities to select, e.g. Italy,Spain,Germany or Europe,Africa
    """
    ),
    callback=comma_separated_list,
)
@click.option(
    "--selection-level",
    required=False,
    default=None,
    type=click.Choice(SelectionLevel, case_sensitive=False),
    help=dedent(
        """\
    Selection level. Mandatory if --entities is specified, must match entities level.\n
    E.g. --entities Europe,Africa --selection-level Continents\
    """
    ),
)
@click.option("--satellite", is_flag=True, help="Add satellite observations")
@click.option("--width", required=False, default=None, type=int, help="Image width")
@click.option("--height", required=False, default=None, type=int, help="Image height")
@click.option(
    "--scale",
    required=False,
    default=1,
    type=float,
    help="Image scale. A number larger than 1 will upscale the image resolution.",
)
def yearly_flux(
    data_variable,
    years,
    months,
    title,
    var_name,
    output_file,
    entities,
    selection_level,
    satellite,
    width,
    height,
    scale,
):
    # pylint: disable=too-many-arguments
    """CLI command to generate yearly flux plot."""
    if entities and selection_level is None:
        raise ValueError(
            dedent(
                f"When specifying a selection,\
                --selection_level must be specified. Possible valiues are {SelectionLevel}"
            )
        )
    entities = EntitySelection.from_entities_list(entities, level=selection_level)
    logger.debug(
        dedent(
            """\
            Called yearly flux CLI with parameters
            data_variable: %s
            years: %s
            months: %s
            title: %s
            var_name: %s
            output_file: %s
            entities: %s
            selection_level: %s
            satellite: %s
            width: %s
            height: %s
            scale: %s\
        """
        ),
        data_variable,
        years,
        months,
        title,
        var_name,
        output_file,
        entities,
        selection_level,
        satellite,
        width,
        height,
        scale,
    )
    fig = ghg_surface_satellite_yearly_plot(
        data_variable=data_variable,
        years=years,
        months=months,
        title=title,
        var_name=var_name,
        shapes=entities,
        add_satellite_observations=satellite,
    )
    if width is None:
        width = fig.layout["width"]
    if height is None:
        height = fig.layout["height"]
    fig.write_image(output_file, format="png", width=width, height=height, scale=scale)
