# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

import pytest

from atmospheric_explorer.api.data_interface.ghg import (
    GHGParameters,
    InversionOptimisedGreenhouseGas,
)


@pytest.fixture(autouse=True)
def clear_cache():
    InversionOptimisedGreenhouseGas.clear_cache()
    yield
    InversionOptimisedGreenhouseGas.clear_cache()


def test__init():
    obj = InversionOptimisedGreenhouseGas(
        data_variables={"a", "b", "c"},
        quantity="quantity",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
        files_dir="test",
    )
    assert isinstance(obj.parameters, GHGParameters)
    assert obj.file_format == "zip"
    assert obj.files_dirname == "test"


def test_obj_creation():
    sh1 = InversionOptimisedGreenhouseGas(
        data_variables={"a", "b", "c"},
        quantity="quantity",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
    )
    sh2 = InversionOptimisedGreenhouseGas(
        data_variables={"a", "b", "c"},
        quantity="quantity",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
    )
    assert id(sh1) == id(sh2)
    assert sh1 in InversionOptimisedGreenhouseGas._cache
    sh3 = InversionOptimisedGreenhouseGas(
        data_variables={"a", "b", "d"},
        quantity="quantity2",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
    )
    assert id(sh3) != id(sh1)
