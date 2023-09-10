# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.api.data_interface.cams_interface import CAMSDataInterface
from atmospheric_explorer.api.data_interface.cams_interface import CAMSParameters


class CAMSDataInterfaceTesting(CAMSDataInterface):
    """Mock class used to instantiate CAMSDataInterface so that it can be tested"""

    def read_dataset(self: CAMSDataInterface):
        pass


def test__init():
    obj = CAMSDataInterfaceTesting()
    assert obj.file_format is None
    assert obj.file_ext is None
    assert obj.dataset_name is None
    assert obj._id == 0


def test__build_call_body():
    obj = CAMSDataInterfaceTesting()
    res = obj.build_call_body(CAMSParameters({"a", "b", "c"}))
    res["variable"] = sorted(res["variable"])
    assert res == {"format": None, "variable": sorted(["a", "b", "c"])}
