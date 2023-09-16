"""APIs for generating GHG yearly flux time series plots."""
from __future__ import annotations

from textwrap import dedent

import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.api.data_interface.data_transformations import (
    clip_and_concat_shapes,
    confidence_interval,
)
from atmospheric_explorer.api.data_interface.ghg import (
    GHGConfig,
    InversionOptimisedGreenhouseGas,
)
from atmospheric_explorer.api.loggers import atm_exp_logger
from atmospheric_explorer.api.plotting.plot_utils import line_with_ci_subplots
from atmospheric_explorer.api.shape_selection.shape_selection import Selection


def _ghg_flux_over_full_area(dataset: xr.Dataset, var_name: str):
    dataset[var_name] = dataset[var_name] * dataset["area"]
    dataset[var_name].attrs["units"] = (
        dataset[var_name].attrs["units"].replace(" m-2", "")
    )
    return dataset


def _ghg_surface_satellite_yearly_data(
    data_variable: str,
    years: set[str] | list[str],
    months: set[str] | list[str],
    var_name: str,
    shapes: Selection = Selection(),
    add_satellite_observations: bool = False,
) -> xr.DataArray | xr.Dataset:
    # pylint: disable=too-many-arguments
    # pylint: disable=invalid-name
    # Download surface data file
    atm_exp_logger.debug(
        dedent(
            """\
            _ghg_surface_satellite_yearly_data called with arguments
            data_variable: %s
            years: %s
            months: %s
            var_name: %s
            shapes: %s
            add_satellite_observations: %s
            """
        ),
        data_variable,
        years,
        months,
        var_name,
        shapes,
        add_satellite_observations,
    )
    surface_data = InversionOptimisedGreenhouseGas(
        data_variables=data_variable,
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    surface_data.download()
    # Read data as dataset
    df_surface = surface_data.read_dataset()
    df_surface = df_surface.squeeze(dim="time_aggregation")
    if add_satellite_observations:
        satellite_data = InversionOptimisedGreenhouseGas(
            data_variables=data_variable,
            quantity="surface_flux",
            input_observations="satellite",
            time_aggregation="monthly_mean",
            year=years,
            month=months,
        )
        satellite_data.download()
        # Read data as dataset
        df_satellite = satellite_data.read_dataset()
        df_satellite = df_satellite.squeeze(dim="time_aggregation")
        df_total = xr.concat([df_surface, df_satellite], dim="input_observations")
    else:
        df_total = df_surface
    # Convert units
    df_total[var_name] = GHGConfig.convert_units_array(
        df_total[var_name], data_variable, "surface_flux", "monthly_mean"
    )
    # Check only needed years and months are present
    df_total = df_total.where(
        df_total["time.year"].isin([int(y) for y in years]), drop=True
    ).where(df_total["time.month"].isin([int(m) for m in months]), drop=True)
    # Clip countries
    if not shapes.empty():
        df_total = clip_and_concat_shapes(df_total, shapes)
    else:
        df_total = df_total.expand_dims({"label": [""]})
    with xr.set_options(keep_attrs=True):
        if data_variable != "nitrous_oxide":
            # Multiply fluxes over full area
            df_total = _ghg_flux_over_full_area(df_total, var_name)
            # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
            df_total = df_total.sortby("time").sum(dim=["longitude", "latitude"])
            da_converted_agg = (
                df_total[var_name]
                .resample(time="YS")
                .map(confidence_interval, dim="time")
                .rename({"time": "Year"})
            )
            da_converted_agg.name = var_name
            da_converted_agg.attrs = df_total[var_name].attrs
            da_converted_agg.attrs["units"] = "kg year-1"
        else:
            df_total = df_total.sortby("time").mean(dim=["longitude", "latitude"])
            da_converted_agg = (
                df_total[var_name]
                .resample(time="YS")
                .map(confidence_interval, dim="time")
                .rename({"time": "Year"})
            )
            da_converted_agg.name = var_name
            da_converted_agg.attrs = df_total[var_name].attrs
            da_converted_agg.attrs["units"] = "kg m-2 year-1"
    # Pandas is easier to use for plotting
    return da_converted_agg


def ghg_surface_satellite_yearly_plot(
    data_variable: str,
    var_name: str,
    years: set[str] | list[str],
    months: set[str] | list[str],
    title: str,
    shapes: Selection = Selection(),
    add_satellite_observations: bool = True,
) -> go.Figure:
    """Generates a yearly mean plot with CI for a quantity from the CAMS Global Greenhouse Gas Inversion dataset.

    Note that we are only considering **surface_flux** quantities in this function.

    Arguments:
        data_variable (str): data variable (greenhouse gas) to be plotted.
            Can be one among: 'carbon_dioxide', 'methane, 'nitrous_oxide'
        var_name (str | list[str]): use a single var_name if the plot only
            shows one input_observations category ('surface').
            Use a list with values corresponding respectively to 'surface'
            and 'satellite' if add_satellite_observations is true.
            Example: ['flux_apos', 'flux_apos_bio']
        years (list[str]): list of years (in YYYY format) to plot the data for
        months (list[str]): list of month (in MM format) to plot the data for
        title (str): plot title
        shapes (Selection): GenericShapeSelection or EntitySelection with
        add_satellite_observations (bool): show 'satellite' input_observations
            data along with 'surface' (only available for carbon_dioxide data
            variable).
    """
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=invalid-name
    atm_exp_logger.debug(
        dedent(
            f"""\
    ghg_surface_satellite_yearly_plot called with arguments
    data_variable: {data_variable}
    years: {years}
    months: {months}
    title: {title}
    var_name: {var_name}
    shapes: {shapes}
    add_satellite_observations: {add_satellite_observations}
    """
        )
    )
    da_converted_agg = _ghg_surface_satellite_yearly_data(
        data_variable, years, months, var_name, shapes, add_satellite_observations
    )
    # Pandas is easier to use for plotting
    df_pandas = (
        da_converted_agg.to_dataframe()
        .unstack("ci")
        .droplevel(axis=1, level=0)
        .reset_index(["label", "input_observations"])
        .rename({"mean": "value"}, axis=1)
    )
    return line_with_ci_subplots(
        df_pandas,
        da_converted_agg.attrs["units"],
        title,
        add_ci=True,
        color="input_observations",
    )
