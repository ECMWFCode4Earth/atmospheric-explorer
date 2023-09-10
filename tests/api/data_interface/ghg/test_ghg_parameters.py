# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument


from atmospheric_explorer.api.data_interface.ghg import GHGParameters


def test__init():
    obj = GHGParameters(
        data_variables="a",
        quantity="quantity",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
    )
    assert obj.data_variables == "a"
    assert obj.quantity == "quantity"
    assert obj.input_observations == "input_observations"
    assert obj.time_aggregation == "time_aggregation"
    assert obj.year == {"2021", "2022"}
    assert obj.month == {"01", "02"}
    assert obj.version == "latest"


def test_build_call_body():
    obj = GHGParameters(
        data_variables="a",
        quantity="quantity2",
        input_observations="input_observations",
        time_aggregation="time_aggregation",
        year={"2021", "2022"},
        month={"01", "02"},
    )
    res = obj.build_call_body()
    assert res == {
        "variable": "a",
        "quantity": "quantity2",
        "input_observations": "input_observations",
        "time_aggregation": "time_aggregation",
        "year": {"2021", "2022"},
        "month": {"01", "02"},
        "version": "latest"
    }
