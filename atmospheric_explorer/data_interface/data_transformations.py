"""\
Data transformations needed for the plotting api
"""
from functools import singledispatch

import numpy as np
import statsmodels.stats.api as sms
import xarray as xr
from shapely.geometry import mapping

from atmospheric_explorer.shapefile import ShapefilesDownloader


def clip_and_concat_countries(
    data_frame: xr.Dataset, countries: list[str]
) -> xr.Dataset:
    """Clips data_frame keeping only countries specified. Countries must be a list of country names"""
    # Download shapefile
    sh_downloader = ShapefilesDownloader(resolution="10m", instance="countries")
    sh_dataframe = sh_downloader.get_as_dataframe()
    # all_touched=True questo parametro include tutti i pixel toccati dal poligono definito
    # se False include solo i pixel il cui centro è incluso nel poligono
    # approvato all_touched=True
    df_clipped_concat = data_frame.rio.clip(
        sh_dataframe[sh_dataframe["ADMIN"] == countries[0]].geometry.apply(mapping),
        sh_dataframe.crs,
        drop=True,
        all_touched=True,
    )
    df_clipped_concat = df_clipped_concat.expand_dims({"admin": [countries[0]]})
    for country in countries[1:]:
        df_clipped = data_frame.rio.clip(
            sh_dataframe[sh_dataframe["ADMIN"] == country].geometry.apply(mapping),
            sh_dataframe.crs,
            drop=True,
            all_touched=True,
        )
        df_clipped = df_clipped.expand_dims({"admin": [country]})
        df_clipped_concat = xr.concat(
            [df_clipped_concat, df_clipped], dim="admin", combine_attrs="override"
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
