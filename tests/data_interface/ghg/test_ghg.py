# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument

from atmospheric_explorer.data_interface.ghg import InversionOptimisedGreenhouseGas


def test__init():
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


def test_year():
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


def test_month():
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


def test__build_call_body():
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
