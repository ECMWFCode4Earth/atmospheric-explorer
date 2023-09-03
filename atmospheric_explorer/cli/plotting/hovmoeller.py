"""\
Hovmoeller plot CLI.
"""
from textwrap import dedent

import click

from atmospheric_explorer.api.data_interface.eac4.eac4_config import EAC4Config
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.hovmoller import eac4_hovmoeller_plot
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection

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
    "--time-values",
    "-t",
    required=True,
    type=click.Choice([f"{h:02}:00" for h in range(0, 24, 3)]),
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
    required=False,
    default="",
    type=str,
    help="Comma separated list of pressure levels. Cannot be provided together with model_levels",
)
@click.option(
    "--model-levels",
    required=False,
    default="",
    type=str,
    help="Comma separated list of model levels. Cannot be provided together with pressure_levels",
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
    time_values,
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
    entities = entities.strip().split(",") if len(entities) > 1 else []
    pressure_levels = (
        pressure_levels.strip().split(",") if len(pressure_levels) > 1 else None
    )
    model_levels = model_levels.strip().split(",") if len(model_levels) > 1 else None
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
            Called yearly flux CLI with parameters
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
        time_values,
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
        time_values=time_values,
        title=title,
        pressure_level=pressure_levels,
        model_level=model_levels,
        shapes=entities,
        resampling=resampling,
    )
    if width is None:
        width = fig.layout["width"]
    if height is None:
        height = fig.layout["height"]
    fig.write_image(output_file, format="png", width=width, height=height, scale=scale)
