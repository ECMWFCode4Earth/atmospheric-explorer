# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.api.data_interface.cams_interface import CAMSParameters


def test__init():
    obj = CAMSParameters({"a", "b", "c"})
    assert obj._data_variables == {"a", "b", "c"}
    assert obj.data_variables == {"a", "b", "c"}


def test_subset():
    obj = CAMSParameters(["a", "b", "d", "d"])
    obj2 = CAMSParameters(["a", "b", "d", "e"])
    assert obj.subset(obj2)
    assert not obj2.subset(obj)


def test_data_variable():
    obj = CAMSParameters(["a", "b", "d", "d"])
    assert obj.data_variables == {"a", "b", "d"}
    obj = CAMSParameters("a")
    assert obj.data_variables == "a"


def test_build_call_body():
    obj = CAMSParameters({"a", "b", "c"})
    res = obj.build_call_body()
    res["variable"] = sorted(res["variable"])
    assert res == {"variable": sorted(["a", "b", "c"])}
