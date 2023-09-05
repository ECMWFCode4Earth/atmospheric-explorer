# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

import pytest
from click.testing import CliRunner

from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.cli.main import main


def test_hovmoeller(mocker):
    mocked_hovm = mocker.patch(
        "atmospheric_explorer.cli.plotting.hovmoeller.eac4_hovmoeller_plot"
    )
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "hovmoeller",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "--time-value",
            "00:00",
            "--title",
            "Test",
            "--output-file",
            "test.png",
        ],
        catch_exceptions=False,
    )
    mocked_hovm.assert_called_once_with(
        data_variable="total_column_ozone",
        var_name="gtco3",
        dates_range="2021-01-01/2021-04-01",
        time_values="00:00",
        title="Test",
        pressure_level=None,
        model_level=None,
        shapes=EntitySelection(),
        resampling="1MS",
    )


def test_hovm_levels(mocker):
    mocked_hovm = mocker.patch(
        "atmospheric_explorer.cli.plotting.hovmoeller.eac4_hovmoeller_plot"
    )
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "hovmoeller",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "--time-value",
            "00:00",
            "--title",
            "Test",
            "--output-file",
            "test.png",
            "-p",
            "1",
            "-p",
            "2",
        ],
        catch_exceptions=False,
    )
    mocked_hovm.assert_called_once_with(
        data_variable="total_column_ozone",
        var_name="gtco3",
        dates_range="2021-01-01/2021-04-01",
        time_values="00:00",
        title="Test",
        pressure_level=(
            "1",
            "2",
        ),
        model_level=None,
        shapes=EntitySelection(),
        resampling="1MS",
    )


def test_hovm_levels_error(mocker):
    with pytest.raises(ValueError):
        mocker.patch(
            "atmospheric_explorer.cli.plotting.hovmoeller.eac4_hovmoeller_plot"
        )
        runner = CliRunner()
        runner.invoke(
            main,
            [
                "plot",
                "hovmoeller",
                "--data-variable",
                "total_column_ozone",
                "--dates-range",
                "2021-01-01/2021-04-01",
                "--time-value",
                "00:00",
                "--title",
                "Test",
                "--output-file",
                "test.png",
                "-p",
                "1",
                "-p",
                "2",
                "-m",
                "1",
                "-m",
                "2",
            ],
            catch_exceptions=False,
        )


def test_hovm_entities_nolevel(mocker):
    with pytest.raises(ValueError):
        mocker.patch(
            "atmospheric_explorer.cli.plotting.hovmoeller.eac4_hovmoeller_plot"
        )
        runner = CliRunner()
        runner.invoke(
            main,
            [
                "plot",
                "hovmoeller",
                "--data-variable",
                "total_column_ozone",
                "--dates-range",
                "2021-01-01/2021-04-01",
                "--time-value",
                "00:00",
                "--title",
                "Test",
                "--output-file",
                "test.png",
                "--entities",
                "Italy,Germany",
            ],
            catch_exceptions=False,
        )


def test_hovm_entities(mocker):
    mocked_entities = mocker.patch(
        "atmospheric_explorer.cli.plotting.hovmoeller.EntitySelection.from_entities_list"
    )
    mocker.patch("atmospheric_explorer.cli.plotting.hovmoeller.eac4_hovmoeller_plot")
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "hovmoeller",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "--time-value",
            "00:00",
            "--title",
            "Test",
            "--output-file",
            "test.png",
            "--entities",
            "Italy,Germany",
            "--selection-level",
            "Countries",
        ],
        catch_exceptions=False,
    )
    mocked_entities.assert_called_once_with(
        ["Italy", "Germany"], level=SelectionLevel.COUNTRIES
    )
