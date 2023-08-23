# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.data_interface.eac4 import EAC4Instance
from atmospheric_explorer.data_interface.ghg import InversionOptimisedGreenhouseGas

from ..conftest import CAMSDataInterfaceTesting


class TestCAMSDataInterface:
    def test__init(self):
        obj = CAMSDataInterfaceTesting({"a", "b", "c"})
        assert obj._data_variables == {"a", "b", "c"}
        assert obj._file_format is None

    def test_data_variables(self):
        obj = CAMSDataInterfaceTesting(["a", "b", "d", "d"])
        assert obj._data_variables == {"a", "b", "d"}
        assert sorted(obj.data_variables) == ["a", "b", "d"]

    def test__build_call_body(self):
        obj = CAMSDataInterfaceTesting({"a", "b", "c"})
        res = obj._build_call_body()
        res["variable"] = sorted(res["variable"])
        assert res == {"format": None, "variable": sorted(["a", "b", "c"])}


class TestEAC4Instance:
    def test__init(self):
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

    def test_time_values(self):
        obj = EAC4Instance(
            {"a", "b", "c"},
            "2021-01-01/2022-01-01",
            ["00:00", "00:00", "03:00"],
        )
        assert obj._time_values == {"00:00", "03:00"}
        assert isinstance(obj.time_values, list)
        assert sorted(obj.time_values) == ["00:00", "03:00"]

    def test_pressure_level(self):
        obj = EAC4Instance(
            {"a", "b", "c"},
            "2021-01-01/2022-01-01",
            "00:00",
            pressure_level=["1", "2", "2", "3"],
        )
        assert obj._pressure_level == {"1", "2", "3"}
        assert isinstance(obj.pressure_level, list)
        assert sorted(obj.pressure_level) == ["1", "2", "3"]

    def test_model_level(self):
        obj = EAC4Instance(
            {"a", "b", "c"},
            "2021-01-01/2022-01-01",
            "00:00",
            model_level=["1", "2", "2", "3"],
        )
        assert obj._model_level == {"1", "2", "3"}
        assert isinstance(obj.model_level, list)
        assert sorted(obj.model_level) == ["1", "2", "3"]

    def test__build_call_body(self):
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


class TestInversionOptimisedGreenhouseGas:
    def test__init(self):
        obj = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "quantity",
            "input_observations",
            "time_aggregation",
            {"2021", "2022"},
            {"01", "02"},
            files_dir="test",
        )
        assert obj._data_variables == {"a", "b", "c"}
        assert obj._file_format == "zip"
        assert obj.quantity == "quantity"
        assert obj.input_observations == "input_observations"
        assert obj.time_aggregation == "time_aggregation"
        assert obj._year == {"2021", "2022"}
        assert obj._month == {"01", "02"}
        assert obj.files_dirname == "test"
        assert obj.version == "latest"

    def test_year(self):
        obj = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "quantity",
            "input_observations",
            "time_aggregation",
            ["2021", "2022", "2023", "2022"],
            "01",
        )
        assert obj._year == {"2021", "2022", "2023"}
        assert sorted(obj.year) == sorted(["2021", "2022", "2023"])

    def test_month(self):
        obj = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
            "quantity",
            "input_observations",
            "time_aggregation",
            "2021",
            ["01", "02", "03", "02"],
        )
        assert obj._month == {"01", "02", "03"}
        assert sorted(obj.month) == sorted(["01", "02", "03"])

    def test__build_call_body(self):
        obj = InversionOptimisedGreenhouseGas(
            {"a", "b", "c"},
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
            "format": "zip",
            "variable": sorted(["a", "b", "c"]),
            "quantity": "quantity",
            "input_observations": "input_observations",
            "time_aggregation": "time_aggregation",
            "year": sorted(["2000", "2001"]),
            "month": sorted(["01", "02"]),
            "version": "latest",
        }