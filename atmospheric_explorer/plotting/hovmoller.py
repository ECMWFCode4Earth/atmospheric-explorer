"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from textwrap import dedent

import geopandas as gpd
import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.data_transformations import (
    clip_and_concat_shapes,
    shifting_long,
)
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting.plot_utils import hovmoeller_plot

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
    data = EAC4Instance(
        data_variables=data_variable,
        dates_range=dates_range,
        time_values=time_values,
        pressure_level=pressure_level,
        model_level=model_level,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = shifting_long(df_down)
    if shapes is not None:
        df_down = clip_and_concat_shapes(df_down, shapes)
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
    df_agg = df_agg.rename({"time": "Month" if resampling == "1MS" else "Year"})
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
    base_colorscale: list[str] | None = None,
    shapes: gpd.GeoDataFrame | None = None,
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
    return hovmoeller_plot(
        df_converted,
        title=title,
        pressure_level=pressure_level,
        model_level=model_level,
        base_colorscale=base_colorscale,
    )
