# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

import pytest
from click.testing import CliRunner

from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.cli.main import main


def test_yearly(mocker):
    mocked_anomalies = mocker.patch(
        "atmospheric_explorer.cli.plotting.yearly_flux.ghg_surface_satellite_yearly_plot"
    )
    runner = CliRunner()
    runner.invoke(
        main,
        [
            "plot",
            "yearly-flux",
            "--data-variable",
            "carbon_dioxide",
            "--var-name",
            "flux_foss",
            "--years",
            "2019,2020",
            "--months",
            "01",
            "--title",
            "Test",
            "--output-file",
            "test.png",
        ],
        catch_exceptions=False,
    )
    mocked_anomalies.assert_called_once_with(
        data_variable="carbon_dioxide",
        var_name="flux_foss",
        years=["2019", "2020"],
        months=("01",),
        title="Test",
        shapes=EntitySelection(),
        add_satellite_observations=False,
    )


def test_yearly_entities_error(mocker):
    with pytest.raises(ValueError):
        mocker.patch(
            "atmospheric_explorer.cli.plotting.yearly_flux.ghg_surface_satellite_yearly_plot"
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
                "--title",
                "Test",
                "--output-file",
                "test.png",
                "--entities",
                "Italy,Germany",
            ],
            catch_exceptions=False,
        )
