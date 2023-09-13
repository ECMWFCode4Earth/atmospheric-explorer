"""APIs for generating EAC4 anomalies time series plots."""
from __future__ import annotations

from textwrap import dedent

import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.api.data_interface.data_transformations import (
    clip_and_concat_shapes,
    shifting_long,
    split_time_dim,
)
from atmospheric_explorer.api.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.plot_utils import line_with_ci_subplots
from atmospheric_explorer.api.shape_selection.shape_selection import Selection

logger = get_logger("atmexp")


def _eac4_anomalies_data(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: set[str] | list[str],
    shapes: Selection = Selection(),
    resampling: str = "1MS",
) -> xr.Dataset:
    # pylint: disable=too-many-arguments
    data = EAC4Instance(
        data_variables=[data_variable],
        dates_range=dates_range,
        time_values=time_values,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = shifting_long(df_down)
    if not shapes.empty():
        df_down = clip_and_concat_shapes(df_down, shapes)
    else:
        df_down = df_down.expand_dims({"label": [""]})
    df_agg = df_down.mean(dim=["latitude", "longitude"])
    df_agg = split_time_dim(df_agg, "time")
    df_agg = df_agg.resample(dates=resampling, restore_coord_dims=True).mean(
        dim="dates"
    )
    df_agg = EAC4Config.convert_units_array(df_agg[var_name], data_variable)
    if resampling == "YS":
        return df_agg.rename({"dates": "Year"})
    return df_agg.rename({"dates": "Month"})


def eac4_anomalies_plot(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: set[str] | list[str],
    title: str,
    shapes: Selection = Selection(),
    reference_dates_range: str | None = None,
    resampling: str = "1MS",
) -> go.Figure:
    """Generate a monthly anomaly plot for a quantity from the Global Reanalysis EAC4 dataset."""
    # pylint: disable=too-many-arguments
    logger.debug(
        dedent(
            """\
            Function eac4_anomalies_plot called with arguments
            data_variable: %s
            var_name: %s
            dates_range: %s
            time_values: %s
            title: %s
            shapes: %s
            reference_dates_range: %s
            resampling: %s
            """
        ),
        data_variable,
        var_name,
        dates_range,
        time_values,
        title,
        shapes,
        reference_dates_range,
        resampling,
    )
    dataset = _eac4_anomalies_data(
        data_variable=data_variable,
        var_name=var_name,
        dates_range=dates_range,
        time_values=time_values,
        resampling=resampling,
        shapes=shapes,
    )
    if reference_dates_range is not None:
        reference_data = _eac4_anomalies_data(
            data_variable=data_variable,
            var_name=var_name,
            dates_range=reference_dates_range,
            time_values=time_values,
            resampling=resampling,
            shapes=shapes,
        )
        if resampling == "YS":
            reference_data = reference_data.mean(dim="Year")
        reference_data = reference_data.mean(dim="Month")
        with xr.set_options(keep_attrs=True):
            dataset_final = dataset - reference_data
            dataset_final.attrs = dataset.attrs
    else:
        dataset_final = dataset
    # Pandas is easier to use for plotting
    df_pandas = (
        dataset_final.to_dataframe()
        .reset_index(["label", "times"])
        .rename({var_name: "value"}, axis=1)
    )
    return line_with_ci_subplots(
        dataset=df_pandas,
        unit=dataset.attrs["units"],
        title=title,
        color="times",
    )
