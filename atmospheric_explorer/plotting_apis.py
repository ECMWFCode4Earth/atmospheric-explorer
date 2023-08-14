"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

import re
from math import ceil, log10
from textwrap import dedent

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.cams_interfaces import (
    EAC4Instance,
    InversionOptimisedGreenhouseGas,
)
from atmospheric_explorer.data_transformations import (
    clip_and_concat_shapes,
    confidence_interval,
    shifting_long,
)
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.units_conversion import convert_units_array
from atmospheric_explorer.utils import hex_to_rgb

logger = get_logger("atmexp")


def _sequential_colorscale_bar(
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


def _add_ci(
    fig: go.Figure,
    trace: go.Figure,
    data_frame: pd.DataFrame,
    labels: list[str],
) -> None:
    """Add confidence intervals to a plotly trace"""
    line_color = ",".join([str(n) for n in hex_to_rgb(trace.line.color)])
    if len(labels) > 1:
        regex = re.compile("label=(.+?)(?=<br>)")
        label = regex.search(trace.hovertemplate)[1]
    else:
        label = labels[0]
    label_index = labels.index(label)
    total_rows = ceil(len(labels) / 2)
    label_row = total_rows - label_index // 2
    label_col = label_index % 2 + 1
    df_label = data_frame[data_frame["label"] == label]
    times = df_label.index.tolist()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=df_label["lower"].to_list(),
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
        row=label_row,
        col=label_col,
    )
    fig.add_trace(
        go.Scatter(
            x=times,
            y=df_label["upper"].to_list(),
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
        row=label_row,
        col=label_col,
    )


def line_with_ci_subplots(
    data_frame: pd.DataFrame, col_num: int, unit: str, title: str
) -> go.Figure:
    """\
    Facet line plot on countries/administrative entinties.
    This function plots the yearly mean of a quantity along with its CI.

    Parameters:
        data_frame (pd.DataFrame): pandas dataframe with (at least) columns
                                    'label','input_observations','mean','lower','upper'
        countries (list[str]): list of countries/administrative entities that must be considered in the facet plot
        col_num (int): number of maximum columns in the facet plot
        unit (str): unit of measure
        title (str): plot title
    """
    labels = sorted(data_frame["label"].unique())
    colors = sorted(data_frame["color"].unique())
    if len(labels) > 1:
        fig = px.line(
            data_frame=data_frame,
            y="value",
            color="color",
            facet_col="label",
            facet_col_wrap=col_num,
            facet_col_spacing=0.04,
            facet_row_spacing=0.15 if len(labels) > 3 else 0.2,
            color_discrete_sequence=px.colors.qualitative.D3,
            category_orders={"color": colors, "label": labels},
        )
    else:
        fig = px.line(
            data_frame=data_frame,
            y="value",
            color="color",
            color_discrete_sequence=px.colors.qualitative.D3,
            category_orders={"color": colors},
        )
    fig.for_each_trace(
        lambda tr: _add_ci(
            fig,
            tr,
            data_frame[data_frame["color"] == tr.legendgroup],
            labels,
        )
    )
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("label=")[-1], font={"size": 14})
    )
    fig.update_yaxes(title=unit, col=1)
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(showticklabels=True, matches=None)
    total_rows = ceil(len(labels) / 2)
    if len(labels) % 2 != 0:
        fig.update_xaxes(title="Year", col=2, row=total_rows)
    base_height = 220 if len(labels) >= 3 else 300
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
    fig.update_traces(selector=-2 * len(labels) - 1, showlegend=True)  # legend for ci
    fig.update_traces(selector=-1, showlegend=True)  # legend for ci
    return fig


def _ghg_surface_satellite_yearly_data(
    data_variable: str,
    years: list[str],
    months: list[str],
    var_name: str,
    shapes: gpd.GeoDataFrame | None,
    add_satellite_observations: bool = False,
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
    # Read data as dataset
    df_surface = surface_data.read_dataset()
    df_surface[var_name] = df_surface[var_name] * df_surface["area"]
    if add_satellite_observations:
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
        df_satellite = satellite_data.read_dataset()
        df_satellite[var_name] = df_satellite[var_name] * df_satellite["area"]
        df_total = xr.concat([df_surface, df_satellite], dim="input_observations").squeeze()
    else:
        df_total = df_surface
    df_total = df_total.rio.write_crs("EPSG:4326")
    # Check only needed years and months are present
    df_total = df_total.where(
        df_total["time.year"].isin([int(y) for y in years]), drop=True
    ).where(df_total["time.month"].isin([int(m) for m in months]), drop=True)
    # Clip countries
    if shapes is not None:
        df_total = clip_and_concat_shapes(df_total, shapes)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df_total = df_total.sortby("time").sum(dim=["longitude", "latitude"])
    # Convert units
    da_converted = convert_units_array(df_total[var_name], data_variable)
    da_converted_agg = (
        da_converted.resample(time="YS")
        .map(confidence_interval, dim="time")
        .rename({"time": "Year", "input_observations": "color"})
    )
    da_converted_agg.name = var_name
    da_converted_agg.attrs = da_converted.attrs
    # Pandas is easier to use for plotting
    return da_converted_agg


def ghg_surface_satellite_yearly_plot(
    data_variable: str,
    years: list[str],
    months: list[str],
    title: str,
    var_name: str = "flux_foss",
    shapes: gpd.GeoDataFrame | None = None,
    add_satellite_observations: bool = True,
) -> go.Figure:
    """\
    Generate a yearly mean plot with CI for a quantity from the CAMS Global Greenhouse Gas Inversion dataset.
    Note that we are only considering **surface_flux** quantities in this function.

    Parameters:
        data_variable (str): data variable (greenhouse gas) to be plotted.
            Can be one among: 'carbon_dioxide', 'methane, 'nitrous_oxide'
        countries (list[str]): list of country names to plot the data for
        years (list[str]): list of years (in YYYY format) to plot the data for
        months (list[str]): list of month (in MM format) to plot the data for
        title (str): plot title
        add_satellite_observations (bool): show 'satellite' input_observations
            data along with 'surface' (only available for carbon_dioxide data
            variable).
        var_name (str | list[str]): use a single var_name if the plot only
            shows one input_observations category ('surface').
            Use a list with values corresponding respectively to 'surface'
            and 'satellite' if add_satellite_observations is true.
            Example: ['flux_apos', 'flux_apos_bio']
    """
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=invalid-name
    logger.debug(
        dedent(
            f"""\
    ghg_surface_satellite_yearly_plot called with arguments
    data_variable: {data_variable}
    shapes: {shapes}
    years: {years}
    months: {months}
    title: {title}
    var_name: {var_name}
    """
        )
    )
    da_converted_agg = _ghg_surface_satellite_yearly_data(
        data_variable,
        years,
        months,
        var_name,
        shapes,
        add_satellite_observations
    )
    # Clip countries
    if shapes is not None:
        col_num = 2 if len(shapes) >= 2 else 1
    else:
        col_num = 1
    # Pandas is easier to use for plotting
    df_pandas = (
        da_converted_agg.to_dataframe()
        .unstack("ci")
        .droplevel(axis=1, level=0)
        .reset_index(["label", "color"])
        .rename({"mean": "value"}, axis=1)
    )
    return line_with_ci_subplots(
        df_pandas, col_num, da_converted_agg.attrs["units"], title
    )


def eac4_anomalies_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    title: str,
    resampling: str = "1MS",
    shapes: gpd.GeoDataFrame = None,
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
    shapes: {shapes}
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
    df_down = shifting_long(df_down)
    df_down = df_down.rio.write_crs("EPSG:4326")
    if shapes is not None:
        df_down = clip_and_concat_shapes(df_down, shapes).sel(
            label=shapes.iloc[0]["label"]
        )
    df_agg = (
        df_down.mean(dim=["latitude", "longitude"])
        .resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
    )
    reference_value = df_agg.mean(dim="time")
    df_converted = convert_units_array(df_agg[var_name], data_variable)
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
    df_converted = convert_units_array(df_agg[var_name], data_variable)
    colorscale, colorbar = _sequential_colorscale_bar(
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


def eac4_hovmoeller_levels_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    pressure_level: list[str],
    title: str,
    resampling: str = "1MS",
    base_colorscale: list[str] = px.colors.sequential.RdBu_r,
    shapes: gpd.GeoDataFrame = None,
) -> go.Figure:
    """Generate a vertical Hovmoeller plot (levels vs time) for a quantity from the Global Reanalysis EAC4 dataset."""
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
    shapes: {shapes}
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
    if shapes is not None:
        df_down = clip_and_concat_shapes(df_down, shapes).sel(
            label=shapes.iloc[0]["label"]
        )
    df_agg = (
        df_down.resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
        .mean(dim="latitude")
        .sortby("level")
    )
    df_converted = convert_units_array(df_agg[var_name], data_variable)
    df_converted = df_converted.assign_coords(
        {"level": [str(c) for c in df_converted.coords["level"].values]}
    )
    colorscale, colorbar = _sequential_colorscale_bar(
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
