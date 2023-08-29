"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from math import log10
from textwrap import dedent

import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.data_transformations import (
    clip_and_concat_shapes,
    shifting_long,
)
from atmospheric_explorer.loggers import get_logger

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
    logger.debug("Separators for colorbar: %s", separators)
    if (separators.max() - separators.min()) < (len(separators) - 1):
        n_decimals = int(
            round(1 - log10(separators.max() / (len(separators) - 1)), 0)
        )  # number of decimals needed to distinguish color levels
        logger.debug("Colorbar decimals: %i", n_decimals)
        ticktext = (
            [f"<{separators[1]:.{n_decimals}f}"]
            + [
                f"{separators[k]:.{n_decimals}f}-{separators[k+1]:.{n_decimals}f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.{n_decimals}f}"]
        )
    else:
        logger.debug("Colorbar decimals: 0")
        ticktext = (
            [f"<{separators[1]:.0f}"]
            + [
                f"{separators[k]:.0f}-{separators[k+1]:.0f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.0f}"]
        )
    colorbar_custom = {
        "thickness": 25,
        "tickvals": tickvals,
        "ticktext": ticktext,
        "xpad": 0,
    }
    return color_scale_custom, colorbar_custom


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
    colorscale, colorbar = _sequential_colorscale_bar(
        df_converted.values.flatten(), base_colorscale
    )
    fig.update_layout(
        title={
            "text": title,
            "x": 0.45,
            "y": 0.95,
            "automargin": True,
            "yref": "container",
            "font": {"size": 19},
        },
        coloraxis={"colorscale": colorscale, "colorbar": colorbar},
    )
    return fig
