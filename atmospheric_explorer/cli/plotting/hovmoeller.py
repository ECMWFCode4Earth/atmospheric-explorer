"""\
Hovmoeller plot CLI.
"""
import click

from atmospheric_explorer.api.data_interface.eac4.eac4_config import EAC4Config
from atmospheric_explorer.api.plotting.hovmoller import eac4_hovmoeller_plot
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection


@click.command()
@click.option("--data-variable", required=True, type=str, help="Data variable")
@click.option("--dates-range", required=True, type=str, help="Date range")
@click.option("--time-values", required=True, type=str, help="Time values")
@click.option("--title", required=True, type=str, help="Plot title")
@click.option(
    "--output-file", required=True, type=str, help="Absolute path of the image file"
)
@click.option(
    "--pressure-levels",
    required=False,
    default="",
    type=str,
    help="Comma separated list of pressure levels to plot. Cannot be provided together with model_levels",
)
@click.option(
    "--model-levels",
    required=False,
    default="",
    type=str,
    help="Comma separated list of model levels to plot. Cannot be provided together with pressure_levels",
)
@click.option(
    "--entities",
    required=False,
    default="",
    type=str,
    help="List of entities to select. Provide a comma separated list like Italy,Spain,Germany",
)
@click.option(
    "--selection-level",
    required=False,
    default=None,
    type=click.Choice(SelectionLevel, case_sensitive=False),
    help="Selection level",
)
@click.option(
    "--resampling", required=False, default="1MS", type=str, help="Resampling"
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
    fig.write_image(output_file, format="png", height=fig.layout["height"], scale=2)
