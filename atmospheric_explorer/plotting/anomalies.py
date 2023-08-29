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

logger = get_logger("atmexp")


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
        data_variables=data_variable,
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
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "font": {"size": 19},
        }
    )
    return fig
