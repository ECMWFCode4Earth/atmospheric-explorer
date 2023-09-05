# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

import pytest
from click.testing import CliRunner

from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.cli.main import main


def test_anomalies(mocker):
    mocked_anomalies = mocker.patch(
        "atmospheric_explorer.cli.plotting.anomalies.eac4_anomalies_plot"
    )
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "anomalies",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "--time-values",
            "00:00",
            "--title",
            "Test",
            "--output-file",
            "test.png",
        ],
        catch_exceptions=False,
    )
    mocked_anomalies.assert_called_once_with(
        data_variable="total_column_ozone",
        var_name="gtco3",
        dates_range="2021-01-01/2021-04-01",
        time_values=("00:00",),
        title="Test",
        reference_dates_range=None,
        resampling="1MS",
        shapes=EntitySelection(),
    )


def test_anomalies_multi(mocker):
    mocked_anomalies = mocker.patch(
        "atmospheric_explorer.cli.plotting.anomalies.eac4_anomalies_plot"
    )
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "anomalies",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "-t",
            "00:00",
            "-t",
            "03:00",
            "--title",
            "Test",
            "--output-file",
            "test.png",
        ],
        catch_exceptions=False,
    )
    mocked_anomalies.assert_called_once_with(
        data_variable="total_column_ozone",
        var_name="gtco3",
        dates_range="2021-01-01/2021-04-01",
        time_values=(
            "00:00",
            "03:00",
        ),
        title="Test",
        reference_dates_range=None,
        resampling="1MS",
        shapes=EntitySelection(),
    )


def test_anomalies_entities_nolevel(mocker):
    with pytest.raises(ValueError):
        mocker.patch("atmospheric_explorer.cli.plotting.anomalies.eac4_anomalies_plot")
        runner = CliRunner()
        runner.invoke(
            main,
            [
                "plot",
                "anomalies",
                "--data-variable",
                "total_column_ozone",
                "--dates-range",
                "2021-01-01/2021-04-01",
                "-t",
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


def test_anomalies_entities(mocker):
    mocked_entities = mocker.patch(
        "atmospheric_explorer.cli.plotting.anomalies.EntitySelection.from_entities_list"
    )
    mocker.patch("atmospheric_explorer.cli.plotting.anomalies.eac4_anomalies_plot")
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "anomalies",
            "--data-variable",
            "total_column_ozone",
            "--dates-range",
            "2021-01-01/2021-04-01",
            "-t",
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
