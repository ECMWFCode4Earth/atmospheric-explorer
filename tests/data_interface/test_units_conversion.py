# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
# import numpy as np
import pytest

from atmospheric_explorer.data_interface.config_parser import OperationParser
from atmospheric_explorer.exceptions import OperationNotAllowed

# import xarray as xr


def test_arithmetic_eval():
    parser = OperationParser()
    assert parser.arithmetic_eval("1+1") == 2
    assert parser.arithmetic_eval("1-1") == 0
    assert parser.arithmetic_eval("1/2") == 0.5
    assert parser.arithmetic_eval("2*2.5") == 5
    assert parser.arithmetic_eval("15%11") == 4


def test_arithmetic_unsupported():
    with pytest.raises(OperationNotAllowed):
        parser = OperationParser()
        parser.arithmetic_eval("2**2")


# def test_singleton():
#     object_first = get_constants()
#     object_second = get_constants()
#     assert id(object_first) == id(object_second)


# def test_get_constants():
#     constants = get_constants()
#     assert len(constants.sections()) == 158
#     assert constants["total_column_ozone"]["factor"] == "46698"
#     assert constants["total_column_ozone"]["unit"] == "DU"


# def test_convert_units_array():
#     const = get_constants()["total_column_ozone"]
#     # generate test data
#     vals = [10, 20, 30]
#     coords = [1, 2, 3]
#     data = xr.DataArray(vals, dims=("x",), coords={"x": coords})
#     data.attrs["units"] = "test"
#     data.attrs["second"] = "attribute"
#     # convert data
#     converted_data = convert_units_array(data, "total_column_ozone")
#     assert converted_data.attrs["units"] == const["unit"]
#     converted_data.attrs.pop("units")
#     data.attrs.pop("units")
#     assert converted_data.attrs == data.attrs
#     for coord, val in data.coords.items():
#         assert (converted_data.coords[coord].values == val.values).all()
#     check_vals = np.array(vals) * const.getfloat("factor")
#     assert (converted_data.values == check_vals).all()
