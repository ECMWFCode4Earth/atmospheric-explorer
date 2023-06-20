"""\
APIs for generating dynamic and static plots
"""
from math import ceil

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.cams_interfaces import InversionOptimisedGreenhouseGas
from atmospheric_explorer.data_transformations import (
    clip_and_concat_countries,
    confidence_interval,
)
from atmospheric_explorer.units_conversion import convert_units_array
from atmospheric_explorer.utils import hex_to_rgb


def add_ci(
    fig: go.Figure, trace: go.Figure, data_frame: pd.DataFrame, countries: list[str]
) -> None:
    """Add confidence intervals to a plotly trace"""
    line_color = ",".join([str(n) for n in hex_to_rgb(trace.line.color)])
    admin = list(filter(lambda c: c in trace.hovertemplate, countries))[0]
    admin_index = countries.index(admin)
    admin_row = ceil((len(countries) - admin_index) / 2)
    admin_col = admin_index % 2 + 1
    df_admin = data_frame[data_frame["admin"] == admin]
    times = df_admin.index.tolist()
    y1_lower = df_admin["lower"].to_list()
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
        row=admin_row,
        col=admin_col,
    )
    y1_upper = df_admin["upper"].to_list()
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
        row=admin_row,
        col=admin_col,
    )


def line_with_ci_subplots(
    data_frame: pd.DataFrame, admins: list[str], col_num: int, unit: str, title: str
) -> go.Figure:
    """\
    Facet line plot on countries/administrative entinties.
    This function plots the yearly mean of a quantity along with its CI.

    Parameters:
        data_frame (pd.DataFrame): pandas dataframe with (at least) columns
                                    'admin','input_observations','mean','lower','upper'
        admins (list[str]): list of countries/administrative entities that must be considered in the facet plot
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
        facet_row_spacing=0.1,
        category_orders={
            "admin": admins,
            "input_observations": ["surface", "satellite"],
        },
        color_discrete_sequence=px.colors.qualitative.D3,
    )
    fig.for_each_trace(
        lambda tr: add_ci(
            fig,
            tr,
            data_frame[data_frame["input_observations"] == tr.legendgroup],
            admins,
        )
    )
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("admin=")[-1], font={"size": 14})
    )
    fig.update_yaxes(title=unit, col=1)
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(showticklabels=True, matches=None)
    fig.update_layout(
        title={"text": title, "x": 0.5, "font": {"size": 19}},
        height=110 * len(admins),
        hovermode="closest",
    )
    fig.update_traces(mode="lines+markers")
    fig.update_traces(selector=-13, showlegend=True)
    fig.update_traces(selector=-1, showlegend=True)
    return fig


def surface_satellite_yearly_plot(
    data_variable: str,
    countries: list[str],
    years: list[str],
    months: list[str],
    title: str,
    col_num: int = 2,
    var_name: str = "flux_foss",
) -> go.Figure:
    """Generate a yearly mean plot with CI for a quantity from the CAMS Global Inversion dataset"""
    # pylint: disable=too-many-arguments
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
    df_surface = surface_data.read_dataset(var_name=var_name)
    df_satellite = satellite_data.read_dataset(var_name=var_name)
    df_total = xr.concat([df_surface, df_satellite], dim="input_observations").squeeze()
    df_total = df_total.rio.write_crs("EPSG:4326")
    # Clip countries
    df_total = clip_and_concat_countries(df_total, countries)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df_total = df_total.sortby("time").mean(dim=["longitude", "latitude"])
    # Convert units
    da_converted_agg = (
        convert_units_array(df_total[var_name], data_variable)
        .resample(time="YS")
        .map(confidence_interval, dim="time")
    )
    da_converted_agg.name = var_name
    da_converted_agg.attrs = df_total[var_name].attrs
    # Pandas is easier to use for plotting
    df_pandas = (
        da_converted_agg.to_dataframe()
        .unstack("ci")
        .droplevel(axis=1, level=0)
        .reset_index(["admin", "input_observations"])
    )
    return line_with_ci_subplots(
        df_pandas, countries, col_num, da_converted_agg.attrs["units"], title
    )
