"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from math import ceil, log10
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.data_interface.ghg import InversionOptimisedGreenhouseGas
from atmospheric_explorer.data_interface.data_transformations import (
    clip_and_concat_countries,
    confidence_interval,
    shifting_long,
)
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import hex_to_rgb

logger = get_logger("atmexp")


def sequential_colorscale_bar(
    values: list[float] | list[int], colors: list[str]
) -> tuple[list, dict]:
    """Compute a sequential colorscale and colorbar form a list of values and a list of colors"""
    vals = np.array(values)
    vals.sort()
    separators = np.linspace(vals.min(), vals.max(), len(colors) + 1)
    separators_scaled = np.linspace(0, 1, len(colors) + 1)
    color_scale_custom = []
    for i, color in enumerate(colors):
        color_scale_custom.append([separators_scaled[i], color])
        color_scale_custom.append([separators_scaled[i + 1], color])
    tickvals = [
        np.mean(separators[k : k + 2]) for k in range(len(separators) - 1)
    ]  # position of tick text
    if separators.max() < (len(separators) - 1):
        n_decimals = int(
            round(1 - log10(separators.max() / (len(separators) - 1)), 0)
        )  # number of decimals needed to distinguish color levels
        ticktext = (
            [f"<{separators[1]:.{n_decimals}f}"]
            + [
                f"{separators[k]:.{n_decimals}f}-{separators[k+1]:.{n_decimals}f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.{n_decimals}f}"]
        )
    else:
        ticktext = (
            [f"<{separators[1]:.0f}"]
            + [
                f"{separators[k]:.0f}-{separators[k+1]:.0f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.0f}"]
        )
    colorbar_custom = {"thickness": 25, "tickvals": tickvals, "ticktext": ticktext}
    return color_scale_custom, colorbar_custom


def add_ci(
    fig: go.Figure,
    trace: go.Figure,
    data_frame: pd.DataFrame,
    countries: list[str],
) -> None:
    """Add confidence intervals to a plotly trace"""
    line_color = ",".join([str(n) for n in hex_to_rgb(trace.line.color)])
    if len(countries) > 1:
        country = list(filter(lambda c: c in trace.hovertemplate, countries))[0]
    else:
        country = countries[0]
    country_index = countries.index(country)
    total_rows = ceil(len(countries) / 2)
    country_row = total_rows - country_index // 2
    country_col = country_index % 2 + 1
    df_country = data_frame[data_frame["admin"] == country]
    times = df_country.index.tolist()
    y1_lower = df_country["lower"].to_list()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=y1_lower,
            line_color=f"rgba({line_color}, 0)",
            fill=None,
            fillcolor=f"rgba({line_color}, 0.2)",
            showlegend=False,
            mode="lines",
            name=f"CI {trace.legendgroup}",
            legendgroup=f"CI {trace.legendgroup}",
            hovertemplate="Lower: %{y}<extra></extra>",
            hoverlabel={"bgcolor": f"rgba({line_color}, 0.2)"},
        ),
        row=country_row,
        col=country_col,
    )
    y1_upper = df_country["upper"].to_list()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=y1_upper,
            line_color=f"rgba({line_color}, 0)",
            fill="tonexty",
            fillcolor=f"rgba({line_color}, 0.2)",
            showlegend=False,
            mode="lines",
            name=f"CI {trace.legendgroup}",
            legendgroup=f"CI {trace.legendgroup}",
            hoverinfo="name+text+y",
            hovertemplate="Upper: %{y}<extra></extra>",
            hoverlabel={"bgcolor": f"rgba({line_color}, 0.2)"},
        ),
        row=country_row,
        col=country_col,
    )


def line_with_ci_subplots(
    data_frame: pd.DataFrame,
    countries: list[str],
    col_num: int,
    unit: str,
    title: str,
) -> go.Figure:
    """\
    Facet line plot on countries/administrative entinties.
    This function plots the yearly mean of a quantity along with its CI.

    Parameters:
        data_frame (pd.DataFrame): pandas dataframe with (at least) columns
                                    'admin','input_observations','mean','lower','upper'
        countries (list[str]): list of countries/administrative entities that must be considered in the facet plot
        col_num (int): number of maximum columns in the facet plot
        unit (str): unit of measure
        title (str): plot title
    """
    fig = px.line(
        data_frame=data_frame,
        y="mean",
        color="input_observations",
        facet_col="admin",
        facet_col_wrap=col_num,
        facet_col_spacing=0.04,
        facet_row_spacing=0.15 if len(countries) > 3 else 0.2,
        category_orders={
            "admin": countries,
            "input_observations": ["surface", "satellite"],
        },
        color_discrete_sequence=px.colors.qualitative.D3,
    )
    fig.for_each_trace(
        lambda tr: add_ci(
            fig,
            tr,
            data_frame[data_frame["input_observations"] == tr.legendgroup],
            countries,
        )
    )
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("admin=")[-1], font={"size": 14})
    )
    fig.update_yaxes(title=unit, col=1)
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(showticklabels=True, matches=None)
    total_rows = ceil(len(countries) / 2)
    if len(countries) % 2 != 0:
        fig.update_xaxes(title="Year", col=2, row=total_rows)
    base_height = 220 if len(countries) >= 3 else 300
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "font": {"size": 19},
        },
        height=base_height * total_rows,
        hovermode="closest",
    )
    fig.update_traces(mode="lines+markers")
    fig.update_traces(
        selector=-2 * len(countries) - 1, showlegend=True
    )  # legend for ci
    fig.update_traces(selector=-1, showlegend=True)  # legend for ci
    return fig


def _ghg_surface_satellite_yearly_data(
    data_variable: str,
    countries: list[str],
    years: list[str],
    months: list[str],
    var_name: str = "flux_foss",
) -> xr.DataArray | xr.Dataset:
    # pylint: disable=too-many-arguments
    # pylint: disable=invalid-name
    # Download surface data file
    surface_data = InversionOptimisedGreenhouseGas(
        data_variables=data_variable,
        file_format="zip",
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    surface_data.download()
    satellite_data = InversionOptimisedGreenhouseGas(
        data_variables=data_variable,
        file_format="zip",
        quantity="surface_flux",
        input_observations="satellite",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    satellite_data.download()
    # Read data as dataset
    df_surface = surface_data.read_dataset()
    df_satellite = satellite_data.read_dataset()
    df_total = xr.concat([df_surface, df_satellite], dim="input_observations").squeeze()
    df_total = df_total.rio.write_crs("EPSG:4326")
    # Clip countries
    df_clipped = clip_and_concat_countries(df_total, countries)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df_final = df_clipped.sortby("time").mean(dim=["longitude", "latitude"])
    # Convert units
    da_converted = df_final[var_name]
    # STILL MISSING: Convert units per month to units per year/aggregation level?
    da_converted.attrs["units"] = df_total[var_name].units
    da_converted_agg = (
        da_converted.resample(time="YS")
        .map(confidence_interval, dim="time")
        .rename({"time": "Year"})
    )
    da_converted_agg.name = var_name
    da_converted_agg.attrs = da_converted.attrs
    # Pandas is easier to use for plotting
    return da_converted_agg


def ghg_surface_satellite_yearly_plot(
    data_variable: str,
    countries: list[str],
    years: list[str],
    months: list[str],
    title: str,
    var_name: str = "flux_foss",
) -> go.Figure:
    """Generate a yearly mean plot with CI for a quantity from the CAMS Global Greenhouse Gas Inversion dataset"""
    # pylint: disable=too-many-arguments
    # pylint: disable=invalid-name
    logger.debug(
        dedent(
            f"""\
    ghg_surface_satellite_yearly_plot called with arguments
    data_variable: {data_variable}
    countries: {countries}
    years: {years}
    months: {months}
    title: {title}
    var_name: {var_name}
    """
        )
    )
    da_converted_agg = _ghg_surface_satellite_yearly_data(
        data_variable, countries, years, months, var_name
    )
    df_pandas = (
        da_converted_agg.to_dataframe()
        .unstack("ci")
        .droplevel(axis=1, level=0)
        .reset_index(["admin", "input_observations"])
    )
    col_num = 2 if len(countries) >= 2 else 1
    return line_with_ci_subplots(
        df_pandas, countries, col_num, da_converted_agg.attrs["units"], title
    )


def eac4_anomalies_plot(
    data_variable: str,
    var_name: str,
    countries: list[str],
    dates_range: str,
    time_values: str,
    title: str,
    resampling: str = "1MS",
) -> go.Figure:
    """Generate a monthly anomaly plot for a quantity from the Global Reanalysis EAC4 dataset.

    TODO: pass reference period as parameter. We are currently considering the
    same date range for data as reference period.
    TODO: add facet plot functionality"""
    # pylint: disable=too-many-arguments
    logger.debug(
        dedent(
            f"""\
    eac4_anomalies_plot called with arguments
    data_variable: {data_variable}
    var_name: {var_name}
    countries: {countries}
    dates_range: {dates_range}
    time_values: {time_values}
    title: {title}
    resampling: {resampling}
    """
        )
    )
    data = EAC4Instance(
        data_variable,
        "netcdf",
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = xr.open_dataset(data.file_full_path)
    df_down = df_down.rio.write_crs("EPSG:4326")
    df_clipped = clip_and_concat_countries(df_down, countries).sel(admin=countries[0])
    df_agg = (
        df_clipped.mean(dim=["latitude", "longitude"])
        .resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
    )
    reference_value = df_agg.mean(dim="time")
    df_converted = EAC4Config.convert_units_array(df_agg[var_name], data_variable)
    reference_value = df_converted.mean().values
    df_anomalies = df_converted - reference_value
    df_anomalies.attrs = df_converted.attrs
    fig = px.line(y=df_anomalies.values, x=df_anomalies.coords["time"], markers="o")
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title=df_anomalies.attrs["units"])
    fig.update_layout(
        title={
            "text": title,
            "x": 0.45,
            "y": 0.95,
            "automargin": True,
            "yref": "container",
            "font": {"size": 19},
        }
    )
    return fig


def eac4_hovmoeller_latitude_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    title: str,
    resampling: str = "1MS",
    base_colorscale: list[str] = px.colors.sequential.Turbo,
) -> go.Figure:
    """Generate a Hovmoeller plot (latitude vs. months) for a quantity from the Global Reanalysis EAC4 dataset."""
    # pylint: disable=too-many-arguments
    # pylint: disable=dangerous-default-value
    logger.debug(
        dedent(
            f"""\
    eac4_hovmoeller_latitude_plot called with arguments
    data_variable: {data_variable}
    var_name: {var_name}
    dates_range: {dates_range}
    time_values: {time_values}
    title: {title}
    resampling: {resampling}
    base_colorscale: {base_colorscale}
    """
        )
    )
    data = EAC4Instance(
        data_variable,
        "netcdf",
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = df_down.rio.write_crs("EPSG:4326")
    df_down = shifting_long(df_down)
    df_agg = (
        df_down.resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
    )
    df_converted = EAC4Config.convert_units_array(df_agg[var_name], data_variable)
    colorscale, colorbar = sequential_colorscale_bar(
        df_converted.values.flatten(), base_colorscale
    )
    fig = px.imshow(df_converted.T, origin="lower")
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Latitude [degrees]")
    fig.update_layout(
        title={
            "text": f"{title} [{df_converted.attrs['units']}]",
            "x": 0.45,
            "y": 0.95,
            "automargin": True,
            "yref": "container",
            "font": {"size": 19},
        },
        coloraxis={"colorscale": colorscale, "colorbar": colorbar},
    )
    return fig


# Generate a vertical Hovmoeller plot (levels vs time) for a quantity from the Global Reanalysis EAC4 dataset.
def eac4_hovmoeller_levels_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    pressure_level: list[str],  # non metto i model level
    countries: list[str],
    title: str,
    resampling: str = "1MS",
    base_colorscale: list[str] = px.colors.sequential.RdBu_r,
) -> go.Figure:
    """Hoevmoeller plot of EAC4 multilevel variables, time vs pressure level"""
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=dangerous-default-value
    logger.debug(
        dedent(
            f"""\
    eac4_hovmoeller_levels_plot called with arguments
    data_variable: {data_variable}
    var_name: {var_name}
    dates_range: {dates_range}
    time_values: {time_values}
    pressure_level: {pressure_level}
    countries: {countries}
    title: {title}
    resampling: {resampling}
    base_colorscale: {base_colorscale}
    """
        )
    )
    data = EAC4Instance(
        data_variable,
        "netcdf",
        pressure_level=pressure_level,
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = df_down.rio.write_crs("EPSG:4326")
    df_down = shifting_long(df_down)
    df_clipped = clip_and_concat_countries(df_down, countries).sel(admin=countries[0])
    df_agg = (
        df_clipped.resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
        .mean(dim="latitude")
        .sortby("level")
    )
    df_converted = EAC4Config.convert_units_array(df_agg[var_name], data_variable)
    df_converted = df_converted.assign_coords(
        {"level": [str(c) for c in df_converted.coords["level"].values]}
    )
    colorscale, colorbar = sequential_colorscale_bar(
        df_converted.values.flatten(), base_colorscale
    )
    fig = px.imshow(df_converted.T, origin="lower")
    fig.update_xaxes(
        title="Month"
    )  # TODO Change this based on resampling # pylint: disable=fixme
    fig.update_yaxes(autorange="reversed", title="Levels[hPa]")
    fig.update_layout(
        title={
            "text": f"{title} [{df_converted.attrs['units']}]",
            "x": 0.45,
            "y": 0.95,
            "automargin": True,
            "yref": "container",
            "font": {"size": 19},
        },
        coloraxis={"colorscale": colorscale, "colorbar": colorbar},
    )
    return fig
