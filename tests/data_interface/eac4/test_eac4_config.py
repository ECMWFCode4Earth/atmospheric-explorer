# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

import numpy as np
import xarray as xr

from atmospheric_explorer.data_interface.eac4.eac4_config import EAC4Config


def test_singleton():
    object_first = EAC4Config.get_config()
    object_second = EAC4Config.get_config()
    assert id(object_first) == id(object_second)


def test_get_constants():
    constants = EAC4Config.get_config()
    assert len(constants["variables"]) == 155
    assert (
        constants["variables"]["total_column_ozone"]["conversion"]["conversion_factor"]
        == 46698
    )
    assert (
        constants["variables"]["total_column_ozone"]["conversion"]["convert_unit"]
        == "DU"
    )


def test_convert_units_array():
    const = EAC4Config.get_config()["variables"]["total_column_ozone"]
    # generate test data
    vals = [10, 20, 30]
    coords = [1, 2, 3]
    data = xr.DataArray(vals, dims=("x",), coords={"x": coords})
    data.attrs["units"] = "test"
    data.attrs["second"] = "attribute"
    # convert data
    converted_data = EAC4Config.convert_units_array(data, "total_column_ozone")
    assert converted_data.attrs["units"] == const["conversion"]["convert_unit"]
    converted_data.attrs.pop("units")
    data.attrs.pop("units")
    assert converted_data.attrs == data.attrs
    for coord, val in data.coords.items():
        assert (converted_data.coords[coord].values == val.values).all()
    check_vals = np.array(vals) * const["conversion"]["conversion_factor"]
    assert (converted_data.values == check_vals).all()
