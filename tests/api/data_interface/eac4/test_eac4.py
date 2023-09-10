# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

import pytest

from atmospheric_explorer.api.data_interface.eac4 import EAC4Instance
from atmospheric_explorer.api.data_interface.eac4 import EAC4Parameters


@pytest.fixture(autouse=True)
def clear_cache():
    EAC4Instance.clear_cache()
    yield
    EAC4Instance.clear_cache()


def test__init():
    obj = EAC4Instance(
        data_variables={"a", "b", "c"},
        dates_range="2021-01-01/2022-01-01",
        time_values=["00:00"],
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
        files_dir="test",
    )
    assert isinstance(obj.parameters, EAC4Parameters)
    assert obj.file_format == "netcdf"
    assert obj.files_dirname == "test"


def test_obj_creation():
    sh1 = EAC4Instance(
        data_variables=["a", "b"],
        dates_range="2021-01-01/2020-04-05",
        time_values=["00:00"],
    )
    sh2 = EAC4Instance(
        data_variables=["a", "b"],
        dates_range="2021-02-01/2020-03-05",
        time_values=["00:00"],
    )
    assert id(sh1) == id(sh2)
    assert sh1 in EAC4Instance._cache
    sh3 = EAC4Instance(
        data_variables=["d", "c"],
        dates_range="2021-01-01/2020-04-05",
        time_values=["00:00"],
    )
    assert id(sh3) != id(sh1)
