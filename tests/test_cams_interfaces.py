# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

from atmospheric_explorer.cams_interfaces import (
    CAMSDataInterface,
    EAC4Instance,
    InversionOptimisedGreenhouseGas,
)

from .conftest import CAMSDataInterfaceTesting


class TestCAMSDataInterface:
    def test__init(self):
        obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf", "test")
        assert obj.data_variables == {"a", "b", "c"}
        assert obj.file_format == "netcdf"
        assert obj._filename == "test"
        obj = CAMSDataInterfaceTesting(["a", "b", "d", "d"], "netcdf")
        assert obj.data_variables == {"a", "b", "d"}

    def test__is_subset_element(self):
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

    def test__includes_data_variables(self):
        obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf")
        assert obj._includes_data_variables({"a", "b"})

    def test__build_call_body(self):
        obj = CAMSDataInterfaceTesting({"a", "b", "c"}, "netcdf")
        res = obj._build_call_body()
        res["variable"] = sorted(res["variable"])
        assert res == {"format": "netcdf", "variable": sorted(["a", "b", "c"])}


class TestEAC4Instance:
    def test__build_call_body(self):
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

    def test__includes_dates_range(self):
        obj = EAC4Instance(
            {"a", "b", "c"},
            "netcdf",
            "2021-01-01/2022-01-01",
            "00:00",
        )
        assert obj._includes_dates_range("2021-02-01/2021-11-01")
        assert not obj._includes_dates_range("2020-02-01/2022-11-01")
        assert not obj._includes_dates_range("2021-02-01/2022-11-01")

    def test__includes_area(self):
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

    def test_includes(self):
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


class TestInversionOptimisedGreenhouseGas:
    def test__build_call_body(self):
        obj = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "netcdf",
            "quantity",
            "input_observations",
            "time_aggregation",
            {"2000", "2001"},
            {"01", "02"},
            version="latest",
        )
        res = obj._build_call_body()
        res["variable"] = sorted(res["variable"])
        res["year"] = sorted(res["year"])
        res["month"] = sorted(res["month"])
        assert res == {
            "format": "netcdf",
            "variable": sorted(["a", "b", "c"]),
            "quantity": "quantity",
            "input_observations": "input_observations",
            "time_aggregation": "time_aggregation",
            "year": sorted(["2000", "2001"]),
            "month": sorted(["01", "02"]),
            "version": "latest",
        }

    def test_includes(self):
        obj1 = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "netcdf",
            "quantity",
            "input_observations",
            "time_aggregation",
            {"2000", "2001"},
            {"01", "02"},
            version="latest",
        )
        obj2 = InversionOptimisedGreenhouseGas(
            {"a", "b"},
            "netcdf",
            "quantity",
            "input_observations",
            "time_aggregation",
            {
                "2000",
            },
            {
                "01",
            },
            version="latest",
        )
        obj3 = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "netcdf",
            "quantity",
            "input_observations",
            "time_aggregation",
            {"2000", "2001"},
            {"01", "02"},
            version="21",
        )
        assert obj1.includes(obj2)
        assert not obj1.includes(obj3)
