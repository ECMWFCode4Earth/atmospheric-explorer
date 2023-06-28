"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from math import ceil

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.cams_interfaces import (
    EAC4Instance,
    InversionOptimisedGreenhouseGas,
)
from atmospheric_explorer.data_transformations import shifting_long_EAC4  # verificare
from atmospheric_explorer.data_transformations import (
    clip_and_concat_countries,
    confidence_interval,
)
from atmospheric_explorer.units_conversion import convert_units_array
from atmospheric_explorer.utils import hex_to_rgb


def add_ci(
    fig: go.Figure,
    trace: go.Figure,
    data_frame: pd.DataFrame,
    countries: list[str],
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
    data_frame: pd.DataFrame,
    admins: list[str],
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
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "font": {"size": 19},
        },
        height=110 * len(admins),
        hovermode="closest",
    )
    fig.update_traces(mode="lines+markers")
    fig.update_traces(selector=-13, showlegend=True)
    fig.update_traces(selector=-1, showlegend=True)
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
    df_surface = surface_data.read_dataset(var_name=var_name)
    df_satellite = satellite_data.read_dataset(var_name=var_name)
    df_total = xr.concat([df_surface, df_satellite], dim="input_observations").squeeze()
    df_total = df_total.rio.write_crs("EPSG:4326")
    # Clip countries
    df_total = clip_and_concat_countries(df_total, countries)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df_total = df_total.sortby("time").mean(dim=["longitude", "latitude"])
    # Convert units
    da_converted = convert_units_array(df_total[var_name], data_variable)
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
    col_num: int = 2,
    var_name: str = "flux_foss",
) -> go.Figure:
    """Generate a yearly mean plot with CI for a quantity from the CAMS Global Greenhouse Gas Inversion dataset"""
    # pylint: disable=too-many-arguments
    # pylint: disable=invalid-name
    da_converted_agg = _ghg_surface_satellite_yearly_data(
        data_variable, countries, years, months, var_name
    )
    df_pandas = (
        da_converted_agg.to_dataframe()
        .unstack("ci")
        .droplevel(axis=1, level=0)
        .reset_index(["admin", "input_observations"])
    )
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
) -> go.Figure:
    """Generate a Hovmoeller plot (latitude vs. months) for a quantity from the Global Reanalysis EAC4 dataset.

    TODO: discretize colorbar"""
    # pylint: disable=too-many-arguments
    data = EAC4Instance(
        data_variable,
        "netcdf",
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = xr.open_dataset(data.file_full_path)
    df_down = df_down.rio.write_crs("EPSG:4326")
    df_agg = (
        df_down.resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
    )
    df_converted = convert_units_array(df_agg[var_name], data_variable)
    fig = px.imshow(df_converted.T, color_continuous_scale="Jet", origin="lower")
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
        }
    )
    return fig


def eac4_hovmoeller_levels_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    pressure_level: list[str],  # non metto i model level
    countries: list[str],
    title: str,
    resampling: str = "1MS",  # non se se vogliamo mantenere mese come time step fissato
) -> go.Figure:
    """Generate a vertical Hovmoeller plot (levels vs time) for a quantity from the Global Reanalysis EAC4 dataset."""
    # pylint: disable=too-many-arguments
    data = EAC4Instance(
        data_variable,
        "netcdf",
        pressure_level=pressure_level,
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()

    df_down = xr.open_dataset(data.file_full_path)
    df_down = df_down.rio.write_crs("EPSG:4326")
    df_shift = shifting_long_EAC4(df_down)
    df_clipped = clip_and_concat_countries(df_shift, countries).sel(admin=countries[0])
    df_agg = (
        df_clipped.resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
        .mean(dim="latitude")
        .sortby("level")
    )
    df_converted = convert_units_array(df_agg[var_name], data_variable)
    fig = px.imshow(df_converted.T, color_continuous_scale="RdBu_r", origin="lower")
    fig.update_xaxes(title="Month")  # non so se fissiamo month
    fig.update_yaxes(type="log", autorange="reversed", title="Levels[hPa]")
    fig.update_layout(
        title={
            "text": f"{title} [{df_converted.attrs['units']}]",
            "x": 0.45,
            "y": 0.95,
            "automargin": True,
            "yref": "container",
            "font": {"size": 19},
        }
    )
    return fig


PlotType = Enum("PlotType", ["time_series", "hovmoeller"])


class PlottingInterface(ABC):
    """Generic interface for all plotting APIs"""

    _plot_type: PlotType

    def __init__(
        self: PlottingInterface,
        _data_variable: str,
        _var_name: str,
        _time_period: str,
    ):
        self.data_variable = _data_variable
        self.var_name = _var_name
        self.time_period = _time_period

    @property
    def data_variable(self: PlottingInterface) -> str:
        """Data variable name"""
        return self._data_variable

    @data_variable.setter
    def data_variable(
        self: PlottingInterface,
        data_variable_input: str,
    ) -> None:
        self._data_variable = data_variable_input

    @abstractmethod
    def plot(self: PlottingInterface):
        """Returns a plot"""
        raise NotImplementedError("Method not implemented")


class TimeSeriesPlotInstance(PlottingInterface):
    """Time series plot object"""

    _plot_type: PlotType = PlotType.time_series

    # def __init__(
    #     self: PlottingInterface,
    #     data_variable: str,
    #     var_name: str,
    #     time_period: str,
    # ):
    #     super().__init__(data_variable, var_name, time_period)

    def plot(
        self: TimeSeriesPlotInstance,
    ) -> go.Figure:
        fig = px.line()
        return fig
