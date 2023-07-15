# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.cams_interface.eac4 import EAC4Instance


def test__init():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
        "2021-01-01/2022-01-01",
        "00:00",
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
        files_dir="test",
    )
    assert obj._data_variables == {"a", "b", "c"}
    assert obj.file_format == "netcdf"
    assert obj.dates_range == "2021-01-01/2022-01-01"
    assert obj.time_values == "00:00"
    assert obj.area == [0, 0, 0, 0]
    assert obj._pressure_level == {"1", "2"}
    assert obj._model_level == {"1", "2"}
    assert obj.files_dirname == "test"


def test_time_values():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
        "2021-01-01/2022-01-01",
        ["00:00", "00:00", "03:00"],
    )
    assert obj._time_values == {"00:00", "03:00"}
    assert isinstance(obj.time_values, list)
    assert sorted(obj.time_values) == ["00:00", "03:00"]


def test_pressure_level():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
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
        "netcdf",
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
        "netcdf",
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


def test__includes_dates_range():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
        "2021-01-01/2022-01-01",
        "00:00",
    )
    assert obj._includes_dates_range("2021-02-01/2021-11-01")
    assert not obj._includes_dates_range("2020-02-01/2022-11-01")
    assert not obj._includes_dates_range("2021-02-01/2022-11-01")


def test__includes_area():
    obj = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
        "2021-01-01/2022-01-01",
        "00:00",
        area=[80, -170, -80, 170],
    )
    assert obj._includes_area([80, -160, -80, 170])
    assert not obj._includes_area([90, -160, -90, 170])
    assert not obj._includes_area(None)
    obj = EAC4Instance(
        {"a", "b", "c"}, "netcdf", "2021-01-01/2022-01-01", "00:00", area=None
    )
    assert obj._includes_area([80, -160, -80, 170])
    assert obj._includes_area(None)


def test_includes():
    obj1 = EAC4Instance(
        {"a", "b", "c"},
        "netcdf",
        "2021-01-01/2022-01-01",
        {"00:00", "03:00"},
        area=None,
    )
    obj2 = EAC4Instance(
        {"a", "b"},
        "netcdf",
        "2021-02-01/2021-11-01",
        "00:00",
        area=[60, -170, -80, 170],
    )
    obj3 = EAC4Instance(
        {"a", "d"},
        "netcdf",
        "2021-02-01/2021-11-01",
        "00:00",
        area=[60, -170, -80, 170],
    )
    assert obj1.includes(obj2)
    assert not obj1.includes(obj3)
