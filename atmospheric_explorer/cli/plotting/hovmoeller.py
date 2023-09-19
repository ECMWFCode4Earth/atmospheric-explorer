"""\
Hovmoeller plot CLI.
"""
from textwrap import dedent

import click

from atmospheric_explorer.api.data_interface.eac4.eac4_config import EAC4Config
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.hovmoeller import eac4_hovmoeller_plot
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.cli.plotting.utils import comma_separated_list

logger = get_logger("atmexp")


@click.command()
@click.option("--data-variable", "-v", required=True, type=str, help="Data variable")
@click.option(
    "--dates-range",
    "-r",
    required=True,
    type=str,
    help="Start/End dates of range, using format YYYY-MM-DD",
)
@click.option(
    "--time-value",
    "-t",
    required=True,
    type=click.Choice(EAC4Config.get_config()["time_values"]),
    help="Time value",
)
@click.option("--title", required=True, type=str, help="Plot title")
@click.option(
    "--output-file",
    required=True,
    type=str,
    help="Absolute path of the resulting image",
)
@click.option(
    "--pressure-levels",
    "-p",
    required=False,
    multiple=True,
    type=click.Choice([str(pl) for pl in EAC4Config.get_config()["pressure_levels"]]),
    help="""\
    Pressure levels. Multiple values can be chosen calling this option multiple times, e.g. -p 1 -p 2.
    Cannot be provided together with model_levels\
    """,
)
@click.option(
    "--model-levels",
    "-m",
    required=False,
    multiple=True,
    type=click.Choice([str(pl) for pl in EAC4Config.get_config()["model_levels"]]),
    help="""\
    Model levels. Multiple values can be chosen calling this option multiple times, e.g. -m 1 -m 2.
    Cannot be provided together with pressure_levels\
    """,
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
@click.option(
    "--resampling",
    required=False,
    default="1MS",
    type=click.Choice(["1MS", "YS"]),
    help="Month/year resampling",
)
@click.option("--width", required=False, default=None, type=int, help="Image width")
@click.option("--height", required=False, default=None, type=int, help="Image height")
@click.option(
    "--scale",
    required=False,
    default=1,
    type=float,
    help="Image scale. A number larger than 1 will upscale the image resolution.",
)
def hovmoeller(
    data_variable,
    dates_range,
    time_value,
    title,
    output_file,
    pressure_levels,
    model_levels,
    entities,
    selection_level,
    resampling,
    width,
    height,
    scale,
):
    # pylint: disable=too-many-arguments
    """CLI command to generate hovmoeller plot."""
    if entities and selection_level is None:
        raise ValueError(
            f"When specifying a selection,\
        --selection_level must be specified. Possible valiues are {SelectionLevel}"
        )
    if pressure_levels and model_levels:
        raise ValueError("Cannot provide both pressure_levels and model_levels")
    entities = EntitySelection.from_entities_list(entities, level=selection_level)
    var_name = EAC4Config.get_config()["variables"][data_variable]["var_name"]
    logger.debug(
        dedent(
            """\
            Called hovmoeller CLI with parameters
            data_variable: %s
            dates_range: %s
            time_values: %s
            title: %s
            output_file: %s
            pressure_levels: %s
            model_levels: %s
            entities: %s
            selection_level: %s
            resampling: %s
            width: %s
            height: %s
            scale: %s\
        """
        ),
        data_variable,
        dates_range,
        time_value,
        title,
        output_file,
        pressure_levels,
        model_levels,
        entities,
        selection_level,
        resampling,
        width,
        height,
        scale,
    )
    logger.debug("Selected variable %s", var_name)
    fig = eac4_hovmoeller_plot(
        data_variable=data_variable,
        var_name=var_name,
        dates_range=dates_range,
        time_values=time_value,
        title=title,
        pressure_level=pressure_levels if pressure_levels else None,
        model_level=model_levels if model_levels else None,
        shapes=entities,
        resampling=resampling,
    )
    if width is None:
        width = fig.layout["width"]
    if height is None:
        height = fig.layout["height"]
    fig.write_image(output_file, format="png", width=width, height=height, scale=scale)
