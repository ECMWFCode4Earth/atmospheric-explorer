"""\
Anomalies plot CLI.
"""
from textwrap import dedent

import click

from atmospheric_explorer.api.data_interface.eac4.eac4_config import EAC4Config
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.anomalies import eac4_anomalies_plot
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
    type=click.Choice(EAC4Config.get_config()["time_values"]),
    multiple=True,
    help="""\
    Time value. Multiple values can be chosen calling this option multiple times, e.g. -t 00:00 -t 03:00.
    """,
)
@click.option("--title", required=True, type=str, help="Plot title")
@click.option(
    "--output-file",
    required=True,
    type=str,
    help="Absolute path of the resulting image",
)
@click.option(
    "--reference-range",
    required=False,
    default=None,
    type=str,
    help="Start/End dates of reference range, using format YYYY-MM-DD",
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
    e.g. --entities Europe,Africa --selection-level Continents\
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
def anomalies(
    data_variable,
    dates_range,
    time_values,
    title,
    output_file,
    reference_range,
    entities,
    selection_level,
    resampling,
    width,
    height,
    scale,
):
    # pylint: disable=too-many-arguments
    """CLI command to generate anomalies plot."""
    entities = entities.strip().split(",") if len(entities) > 1 else []
    if entities and selection_level is None:
        raise ValueError(
            f"When specifying a selection,\
        --selection_level must be specified. Possible valiues are {SelectionLevel}"
        )
    entities = EntitySelection.from_entities_list(entities, level=selection_level)
    var_name = EAC4Config.get_config()["variables"][data_variable]["var_name"]
    logger.debug(
        dedent(
            """\
            Called anomalies CLI with parameters
            data_variable: %s
            dates_range: %s
            time_values: %s
            title: %s
            output_file: %s
            reference_range: %s
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
        reference_range,
        entities,
        selection_level,
        resampling,
        width,
        height,
        scale,
    )
    logger.debug("Selected variable %s", var_name)
    fig = eac4_anomalies_plot(
        data_variable=data_variable,
        var_name=var_name,
        dates_range=dates_range,
        time_values=time_values,
        title=title,
        reference_dates_range=reference_range,
        resampling=resampling,
        shapes=entities,
    )
    if width is None:
        width = fig.layout["width"]
    if height is None:
        height = fig.layout["height"]
    fig.write_image(output_file, format="png", width=width, height=height, scale=scale)
