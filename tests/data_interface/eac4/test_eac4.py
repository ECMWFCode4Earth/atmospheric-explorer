# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.data_interface.eac4 import EAC4Instance


def test__init():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "2021-01-01/2022-01-01",
        "00:00",
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
        files_dir="test",
    )
    assert obj._data_variables == {"a", "b", "c"}
    assert obj._file_format == "netcdf"
    assert obj.dates_range == "2021-01-01/2022-01-01"
    assert obj.time_values == "00:00"
    assert obj.area == [0, 0, 0, 0]
    assert obj._pressure_level == {"1", "2"}
    assert obj._model_level == {"1", "2"}
    assert obj.files_dirname == "test"


def test_time_values():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "2021-01-01/2022-01-01",
        ["00:00", "00:00", "03:00"],
    )
    assert obj._time_values == {"00:00", "03:00"}
    assert isinstance(obj.time_values, list)
    assert sorted(obj.time_values) == ["00:00", "03:00"]


def test_pressure_level():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "2021-01-01/2022-01-01",
        "00:00",
        pressure_level=["1", "2", "2", "3"],
    )
    assert obj._pressure_level == {"1", "2", "3"}
    assert isinstance(obj.pressure_level, list)
    assert sorted(obj.pressure_level) == ["1", "2", "3"]


def test_model_level():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "2021-01-01/2022-01-01",
        "00:00",
        model_level=["1", "2", "2", "3"],
    )
    assert obj._model_level == {"1", "2", "3"}
    assert isinstance(obj.model_level, list)
    assert sorted(obj.model_level) == ["1", "2", "3"]


def test__build_call_body():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "2021-01-01/2022-01-01",
        "00:00",
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
    )
    res = obj._build_call_body()
    res["variable"] = sorted(res["variable"])
    res["pressure_level"] = sorted(res["pressure_level"])
    res["model_level"] = sorted(res["model_level"])
    assert res == {
        "format": "netcdf",
        "variable": sorted(["a", "b", "c"]),
        "date": "2021-01-01/2022-01-01",
        "time": "00:00",
        "area": [0, 0, 0, 0],
        "pressure_level": sorted(["1", "2"]),
        "model_level": sorted(["1", "2"]),
    }
