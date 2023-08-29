"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from textwrap import dedent

import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.data_transformations import (
    clip_and_concat_shapes,
    shifting_long,
)
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting.plot_utils import sequential_colorscale_bar

logger = get_logger("atmexp")


def _eac4_hovmoeller_data(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    resampling: str,
    shapes: gpd.GeoDataFrame | None,
    pressure_level: list[str] | None = None,
    model_level: list[str] | None = None,
) -> xr.Dataset:
    # pylint: disable=too-many-arguments
    if pressure_level is not None:
        data = EAC4Instance(
            data_variables=data_variable,
            pressure_level=pressure_level,
            dates_range=dates_range,
            time_values=time_values,
        )
    elif model_level is not None:
        data = EAC4Instance(
            data_variables=data_variable,
            model_level=model_level,
            dates_range=dates_range,
            time_values=time_values,
        )
    else:
        data = EAC4Instance(
            data_variables=data_variable,
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
        df_down[var_name]
        .resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
        .mean(dim="longitude")
    )
    if (pressure_level or model_level) is not None:
        df_agg = df_agg.mean(dim="latitude").sortby("level")
        df_agg = df_agg.assign_coords(
            {"level": [str(c) for c in df_agg.coords["level"].values]}
        )
    return EAC4Config.convert_units_array(df_agg, data_variable)


def eac4_hovmoeller_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    title: str,
    pressure_level: list[str] | None = None,
    model_level: list[str] | None = None,
    resampling: str = "1MS",
    base_colorscale: list[str] = None,
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
            title: {title}
            pressure_level: {pressure_level}
            model_level: {model_level}
            resampling: {resampling}
            base_colorscale: {base_colorscale}
            shapes: {shapes}
            """
        )
    )
    df_converted = _eac4_hovmoeller_data(
        data_variable=data_variable,
        var_name=var_name,
        dates_range=dates_range,
        time_values=time_values,
        resampling=resampling,
        shapes=shapes,
        pressure_level=pressure_level,
        model_level=model_level,
    )
    fig = px.imshow(df_converted.T, origin="lower")
    fig.update_xaxes(title="Month")
    if pressure_level is not None:
        fig.update_yaxes(
            autorange="reversed", title="Pressure Level [hPa]", type="category"
        )
        if base_colorscale is None:
            base_colorscale = px.colors.sequential.RdBu_r
    elif model_level is not None:
        fig.update_yaxes(autorange="reversed", title="Model Level", type="category")
        if base_colorscale is None:
            base_colorscale = px.colors.sequential.RdBu_r
    else:
        fig.update_yaxes(title="Latitude [degrees]")
        if base_colorscale is None:
            base_colorscale = px.colors.sequential.Turbo
    colorscale, colorbar = sequential_colorscale_bar(
        df_converted.values.flatten(), base_colorscale
    )
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "font": {"size": 19},
        },
        coloraxis={"colorscale": colorscale, "colorbar": colorbar},
    )
    return fig
