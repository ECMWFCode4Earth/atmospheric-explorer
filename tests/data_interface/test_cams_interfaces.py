# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from ..conftest import CAMSDataInterfaceTesting


def test__init():
    obj = CAMSDataInterfaceTesting({"a", "b", "c"})
    assert obj._data_variables == {"a", "b", "c"}
    assert obj._file_format is None
    assert obj._file_ext is None
    assert obj._dataset_name is None
    assert obj._id > 0


def test_data_variables():
    obj = CAMSDataInterfaceTesting(["a", "b", "d", "d"])
    assert obj._data_variables == {"a", "b", "d"}
    assert sorted(obj.data_variables) == ["a", "b", "d"]


def test__build_call_body():
    obj = CAMSDataInterfaceTesting({"a", "b", "c"})
    res = obj._build_call_body()
    res["variable"] = sorted(res["variable"])
    assert res == {"format": None, "variable": sorted(["a", "b", "c"])}
