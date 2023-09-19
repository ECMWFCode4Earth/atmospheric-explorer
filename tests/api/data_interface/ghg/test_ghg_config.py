# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

import numpy as np
import xarray as xr

from atmospheric_explorer.api.data_interface.ghg.ghg_config import GHGConfig


def test_singleton():
    object_first = GHGConfig.get_config()
    object_second = GHGConfig.get_config()
    assert id(object_first) == id(object_second)


def test_get_constants():
    constants = GHGConfig.get_config()
    assert len(constants["variables"]) == 3
    var_dict = constants["variables"]["carbon_dioxide"]["mean_column"]["instantaneous"][
        0
    ]
    assert var_dict["conversion"]["conversion_factor"] == (28.97 / 44.01 * 1e6)
    assert var_dict["conversion"]["convert_unit"] == "ppmv"


def test_convert_units_array():
    const = GHGConfig.get_config()["variables"]["carbon_dioxide"]["mean_column"][
        "instantaneous"
    ][0]
    # generate test data
    vals = [10, 20, 30]
    coords = [1, 2, 3]
    data = xr.DataArray(vals, dims=("x",), coords={"x": coords}, name="XCO2")
    data.attrs["units"] = "test"
    data.attrs["second"] = "attribute"
    # convert data
    converted_data = GHGConfig.convert_units_array(
        data, "carbon_dioxide", "mean_column", "instantaneous"
    )
    assert converted_data.attrs["units"] == const["conversion"]["convert_unit"]
    converted_data.attrs.pop("units")
    data.attrs.pop("units")
    assert converted_data.attrs == data.attrs
    for coord, val in data.coords.items():
        assert (converted_data.coords[coord].values == val.values).all()
    check_vals = np.array(vals) * const["conversion"]["conversion_factor"]
    assert (converted_data.values == check_vals).all()
