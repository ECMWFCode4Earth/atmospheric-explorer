"""\
Yearly flux plot CLI.
"""
from textwrap import dedent

import click

from atmospheric_explorer.api.data_interface.ghg.ghg_config import GHGConfig
from atmospheric_explorer.api.plotting.yearly_flux import (
    ghg_surface_satellite_yearly_plot,
)
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection


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
    required=True,
    type=click.Choice(GHGConfig.get_config()["variables"].keys()),
    help="Data variable",
    is_eager=True,
)
@click.option(
    "--years",
    required=True,
    type=str,
    help="Comma separated list of years, e.g. 2019,2020,2021",
)
@click.option(
    "--months",
    required=True,
    type=str,
    help="Comma separated list of months, e.g. 01,02,03",
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
    help="List of entities to select. Provide a comma separated list like Italy,Spain,Germany",
)
@click.option(
    "--selection-level",
    required=False,
    default=None,
    type=click.Choice(SelectionLevel, case_sensitive=False),
    help="Selection level",
)
@click.option("--satellite", is_flag=True, help="Add satellite observations")
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
):
    # pylint: disable=too-many-arguments
    """CLI command to generate yearly flux plot."""
    entities = entities.strip().split(",") if len(entities) > 1 else []
    years = years.strip().split(",") if len(years) > 1 else []
    months = months.strip().split(",") if len(months) > 1 else []
    if entities and selection_level is None:
        raise ValueError(
            dedent(
                f"When specifying a selection,\
                --selection_level must be specified. Possible valiues are {SelectionLevel}"
            )
        )
    entities = EntitySelection.from_entities_list(entities, level=selection_level)
    fig = ghg_surface_satellite_yearly_plot(
        data_variable=data_variable,
        years=years,
        months=months,
        title=title,
        var_name=var_name,
        shapes=entities,
        add_satellite_observations=satellite,
    )
    fig.write_image(output_file, format="png", height=fig.layout["height"], scale=2)
