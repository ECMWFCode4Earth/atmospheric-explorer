"""APIs for generating EAC4 Hovmoeller plots."""
from __future__ import annotations

from textwrap import dedent

import plotly.graph_objects as go
import xarray as xr

from atmospheric_explorer.api.data_interface.data_transformations import (
    clip_and_concat_shapes,
    shifting_long,
)
from atmospheric_explorer.api.data_interface.eac4 import EAC4Config, EAC4Instance
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger
from atmospheric_explorer.api.plotting.plot_utils import hovmoeller_plot
from atmospheric_explorer.api.shape_selection.shape_selection import Selection


def _eac4_hovmoeller_data(
    data_variable: str,
    var_name: str,
    dates_range: str,
    time_values: str,
    resampling: str,
    shapes: Selection = Selection(),
    pressure_level: list[str] | None = None,
    model_level: list[str] | None = None,
) -> xr.Dataset:
    # pylint: disable=too-many-arguments
    data = EAC4Instance(
        data_variables=data_variable,
        dates_range=dates_range,
        time_values={time_values},
        pressure_level=pressure_level,
        model_level=model_level,
    )
    data.download()
    df_down = data.read_dataset()
    df_down = shifting_long(df_down)
    if not shapes.empty():
        df_down = clip_and_concat_shapes(df_down, shapes)
    else:
        df_down = df_down.expand_dims({"label": [""]})
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
    shapes: Selection = Selection(),
    resampling: str = "1MS",
    base_colorscale: list[str] | None = None,
) -> go.Figure:
    """Generate a vertical Hovmoeller plot (levels vs time) for a quantity from the Global Reanalysis EAC4 dataset."""
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    # pylint: disable=dangerous-default-value
    atm_exp_logger.debug(
        dedent(
            """\
            Function eac4_hovmoeller_levels_plot called with arguments
            data_variable: %s
            var_name: %s
            dates_range: %s
            time_values: %s
            title: %s
            pressure_level: %s
            model_level: %s
            shapes: %s
            resampling: %s
            base_colorscale: %s
            """
        ),
        data_variable,
        var_name,
        dates_range,
        time_values,
        title,
        pressure_level,
        model_level,
        shapes,
        resampling,
        base_colorscale,
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
