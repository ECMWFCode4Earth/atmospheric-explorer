# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

import numpy as np
import xarray as xr

from atmospheric_explorer.api.data_interface.data_transformations import (
    confidence_interval,
)


def test_conf_interval_array():
    lst = [-1, 0, 1]
    res = confidence_interval(lst)
    assert (np.round(res, 3) == [-2.484, 0, 2.484]).all()
    array = np.array([-1, 0, 1])
    res = confidence_interval(array)
    assert (np.round(res, 3) == [-2.484, 0, 2.484]).all()


def test_conf_interval_nan():
    array = np.array([np.nan, -1, 0, 1])
    res = confidence_interval(array)
    assert (np.round(res, 3) == [-2.484, 0, 2.484]).all()
    array = np.array([np.nan, np.nan, np.nan])
    res = confidence_interval(array)
    assert np.isnan(res).all()


def test_conf_interval_xarray():
    array = xr.DataArray(
        [[-1, 0, 1], [-1, 0, 1]], dims=["x", "y"], coords=[[1, 2], [3, 4, 5]]
    )
    res = confidence_interval(array, dim="y")
    expected = xr.DataArray(
        [[-2.484, 0, 2.484], [-2.484, 0, 2.484]],
        dims=["x", "ci"],
        coords=[[1, 2], ["lower", "mean", "upper"]],
    )
    assert (np.round(res, 3) == expected).all()
