# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
from atmospheric_explorer.cams_interfaces import CAMSDataInterface, EAC4Instance


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
    obj = EAC4Instance({"a", "b", "c"}, "netcdf", "2021-01-01/2021-02-01", "00:00")
    assert obj._includes_data_variables({"a", "b"})
