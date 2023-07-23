# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from conftest import CAMSDataInterfaceTesting

from atmospheric_explorer.data_interface import CAMSDataInterface


def test__init():
    obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf")
    assert obj._data_variables == {"a", "b", "c"}
    assert obj.file_format == "netcdf"


def test_data_variables():
    obj = CAMSDataInterfaceTesting(["a", "b", "d", "d"], "netcdf")
    assert obj._data_variables == {"a", "b", "d"}
    assert sorted(obj.data_variables) == ["a", "b", "d"]


def test__is_subset_element():
    assert CAMSDataInterface._is_subset_element({"a", "b", "c"}, {"a", "b"})
    assert not CAMSDataInterface._is_subset_element({"a", "b", "c"}, {"e", "d"})
    assert CAMSDataInterface._is_subset_element({"a", "b", "c"}, "a")
    assert not CAMSDataInterface._is_subset_element({"a", "b", "c"}, "d")
    assert CAMSDataInterface._is_subset_element({"a", "b", "c", None}, None)
    assert not CAMSDataInterface._is_subset_element({"a", "b", "c"}, None)
    assert not CAMSDataInterface._is_subset_element("a", {"a", "b"})
    assert CAMSDataInterface._is_subset_element("a", "a")
    assert not CAMSDataInterface._is_subset_element("a", "d")
    assert CAMSDataInterface._is_subset_element(None, None)


def test__includes_data_variables():
    obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf")
    assert obj._includes_data_variables({"a", "b"})
    assert not obj._includes_data_variables({"a", "d"})


def test__build_call_body():
    obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf")
    res = obj._build_call_body()
    res["variable"] = sorted(res["variable"])
    assert res == {"format": "netcdf", "variable": sorted(["a", "b", "c"])}
