"""\
Data transformations needed for the plotting api
"""
from functools import singledispatch

import numpy as np
import statsmodels.stats.api as sms
import xarray as xr
from shapely.geometry import mapping

from shapely import Polygon, MultiPolygon


def clip_and_concat_shapes(
    data_frame: xr.Dataset,
    shapes_dict: dict[str, Polygon | MultiPolygon]
) -> xr.Dataset:
    """Clips data_frame keeping only shapes specified. Shapes_dict must be a dict of labels and shapes."""
    # Download shapefile

    # all_touched=True questo parametro include tutti i pixel toccati dal poligono definito
    # se False include solo i pixel il cui centro è incluso nel poligono
    # approvato all_touched=True
    df_clipped_concat = xr.Dataset(coords={"_shape_label":[]})
    for labels, shapes in shapes_dict.items():
        df_clipped = data_frame.rio.clip(
            [mapping(shapes)],
            drop=True,
            all_touched=True,
        )
        df_clipped = df_clipped.expand_dims({"_shape_label": [labels]})
        df_clipped_concat = xr.concat(
            [df_clipped_concat, df_clipped], dim="_shape_label", combine_attrs="override"
        )
    return df_clipped_concat


@singledispatch
def confidence_interval(array: list | np.ndarray) -> np.ndarray:
    """Compute the confidence interval for an array of samples"""
    if isinstance(array, list):
        array = np.array(array)
    array_nonan = array[~np.isnan(array)]
    if array_nonan.size > 0:
        array = array_nonan
    lower, upper = sms.DescrStatsW(array).tconfint_mean()
    return np.array([lower, np.mean(array), upper])


@confidence_interval.register
def _(array: xr.DataArray, dim: str) -> xr.DataArray:
    """\
    Compute the confidence interval for an xarray.DataArray over a dimension.
    This function preserves all other dimensions and can be used in resamples and groupby with map.
    """
    all_dims = list(array.dims)
    index = all_dims.index(dim)
    keep_dims = all_dims.copy()
    keep_dims.remove(dim)
    return xr.DataArray(
        np.apply_along_axis(confidence_interval, index, array.values),
        dims=[*keep_dims, "ci"],
        coords=[*[array.coords[d] for d in keep_dims], ["lower", "mean", "upper"]],
    )


def shifting_long(data_set=xr.Dataset) -> xr.Dataset:
    """Shifts longitude to range -180+180"""
    return data_set.assign_coords(
        longitude=((data_set.longitude + 180) % 360) - 180
    ).sortby("longitude")
