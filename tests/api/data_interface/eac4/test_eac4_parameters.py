# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.api.data_interface.eac4 import EAC4Parameters


def test_is_subset_none():
    assert not EAC4Parameters._is_subset_none(None, "test")
    assert not EAC4Parameters._is_subset_none("test", None)
    assert EAC4Parameters._is_subset_none(None, None)
    assert EAC4Parameters._is_subset_none("test", "test") is None


def test_dates_subset():
    dsfirst = "2021-01-01/2021-04-01"
    dssecond = "2022-01-01/2022-04-01"
    assert not EAC4Parameters.dates_issubset(dsfirst, dssecond)
    dsthird = "2021-02-01/2021-02-04"
    assert EAC4Parameters.dates_issubset(dsthird, dsfirst)
    dsfourth = "2021-02-01/2022-02-04"
    assert not EAC4Parameters.dates_issubset(dsfourth, dsfirst)


def test_area_subset():
    arfirst = [10, 10, -10, -10]
    arsecond = [120, 120, 110, 110]
    assert not EAC4Parameters.area_issubset(arfirst, arsecond)
    arthird = [5, 5, -5, -5]
    assert EAC4Parameters.area_issubset(arthird, arfirst)
    arfourth = [5, 5, -15, -5]
    assert not EAC4Parameters.area_issubset(arfourth, arfirst)


def test_pressure_subset():
    plfirst = {1, 2, 3}
    plsecond = {1, 2, 3, 4, 5}
    assert EAC4Parameters.pressure_issubset(plfirst, plsecond)
    assert not EAC4Parameters.pressure_issubset(plsecond, plfirst)


def test_model_subset():
    mlfirst = {1, 2, 3}
    mlsecond = {1, 2, 3, 4, 5}
    assert EAC4Parameters.model_issubset(mlfirst, mlsecond)
    assert not EAC4Parameters.model_issubset(mlsecond, mlfirst)


def test__init():
    obj = EAC4Parameters(
        data_variables={"a", "b", "c"},
        dates_range="2021-01-01/2022-01-01",
        time_values=["00:00"],
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
    )
    assert obj._data_variables == {"a", "b", "c"}
    assert obj.dates_range == "2021-01-01/2022-01-01"
    assert obj.time_values == {"00:00"}
    assert obj.area == [0, 0, 0, 0]
    assert obj.pressure_level == {"1", "2"}
    assert obj.model_level == {"1", "2"}


def test__build_call_body():
    obj = EAC4Parameters(
        data_variables={"a", "b", "c"},
        dates_range="2021-01-01/2022-01-01",
        time_values=["00:00"],
        area=[0, 0, 0, 0],
        pressure_level={"1", "2"},
        model_level={"1", "2"},
    )
    res = obj.build_call_body()
    res["variable"] = sorted(res["variable"])
    res["pressure_level"] = sorted(res["pressure_level"])
    res["model_level"] = sorted(res["model_level"])
    assert res == {
        "variable": sorted(["a", "b", "c"]),
        "date": "2021-01-01/2022-01-01",
        "time": ["00:00"],
        "area": [0, 0, 0, 0],
        "pressure_level": sorted(["1", "2"]),
        "model_level": sorted(["1", "2"]),
    }
