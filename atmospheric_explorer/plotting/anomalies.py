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
from atmospheric_explorer.plotting.plot_utils import line_with_ci_subplots

logger = get_logger("atmexp")


def _eac4_anomalies_data(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    resampling: str = "1MS",
    shapes: gpd.GeoDataFrame | None = None,
) -> xr.Dataset:
    # pylint: disable=too-many-arguments
    data = EAC4Instance(
        data_variables=data_variable,
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = shifting_long(df_down)
    if shapes is not None:
        df_down = clip_and_concat_shapes(df_down, shapes)
    df_agg = (
        df_down.mean(dim=["latitude", "longitude"])
        .resample(time=resampling, restore_coord_dims=True)
        .mean(dim="time")
    )
    reference_value = df_agg.mean(dim="time")
    df_converted = EAC4Config.convert_units_array(df_agg[var_name], data_variable)
    reference_value = df_converted.mean().values
    with xr.set_options(keep_attrs=True):
        df_anomalies = df_converted - reference_value
        df_anomalies.attrs = df_converted.attrs
    return df_anomalies


def eac4_anomalies_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    title: str,
    resampling: str = "1MS",
    shapes: gpd.GeoDataFrame | None = None,
) -> go.Figure:
    """Generate a monthly anomaly plot for a quantity from the Global Reanalysis EAC4 dataset.

    TODO: pass reference period as parameter. We are currently considering the
    same date range for data as reference period.
    """
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
    dataset = _eac4_anomalies_data(
        data_variable=data_variable,
        var_name=var_name,
        dates_range=dates_range,
        time_values=time_values,
        resampling=resampling,
        shapes=shapes,
    )
    # Pandas is easier to use for plotting
    df_pandas = (
        dataset.to_dataframe()
        .reset_index(["label"])
        .assign(color="anomalies")
        .rename({var_name: "value"}, axis=1)
    )
    return line_with_ci_subplots(
        dataset=df_pandas, unit=dataset.attrs["units"], title=title
    )
