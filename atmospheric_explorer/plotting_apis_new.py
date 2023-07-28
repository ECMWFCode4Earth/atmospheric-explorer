"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import plotly.express as px
import plotly.graph_objects as go
from xarray import DataArray

from atmospheric_explorer.cams_interfaces import (
    EAC4Instance,
    InversionOptimisedGreenhouseGas,
)
from atmospheric_explorer.data_transformations import clip_and_concat_countries
from atmospheric_explorer.units_conversion import convert_units_array

PlotType = Enum("PlotType", ["time_series", "hovmoeller"])
DatasetName = Enum("DatasetName", ["eac4", "ghg"])


class EAC4Parameters:
    """Parameters for EAC4 dataset"""

    # pylint: disable=too-few-public-methods

    def __init__(
        self: EAC4Parameters,
        _data_variable: str,
        _var_name: str,
        _file_format: str,
        _dates_range: str,
        _time_values: str,
    ) -> None:
        self.data_variable = _data_variable
        self.var_name = _var_name
        self.file_format = _file_format
        self.dates_range = _dates_range
        self.time_values = _time_values


class GHGParameters:
    """Parameters for GHG dataset"""

    # pylint: disable=too-few-public-methods

    def __init__(
        self: GHGParameters,
        _data_variable: str,
        _file_format: str,
        _quantity: str,
        _input_observations: str,
        _time_aggregation: str,
        _year: list[str],
        _month: list[str],
    ) -> None:
        self.data_variable = _data_variable
        self.file_format = _file_format
        self.quantity = _quantity
        self.input_observations = _input_observations
        self.time_aggregation = _time_aggregation
        self.year = _year
        self.month = _month


class PlottingInterface(ABC):
    """Generic interface for all plotting APIs"""

    _plot_type: PlotType

    def __init__(
        self: PlottingInterface,
        _dataset_name: DatasetName,
        _eac4_parameters: EAC4Parameters,
        _ghg_parameters: GHGParameters,
        _countries: list[str],
        _title: str,
    ):
        self.dataset_name = _dataset_name
        self.title = _title
        self.countries = _countries
        # Qui sotto: puo` avere senso tenere comunque degli argomenti generici,
        # che ci sono per entrambi i dataset e possono servire sempre nei plot/dowload dati?
        match self.dataset_name:
            case DatasetName.eac4:
                self.eac4_parameters = _eac4_parameters
                self.data_variable = _eac4_parameters.data_variable
                self.var_name = _eac4_parameters.var_name
            case DatasetName.ghg:
                self.ghg_parameters = _ghg_parameters
                self.data_variable = _ghg_parameters.data_variable
                self.var_name = _ghg_parameters.var_name

    @abstractmethod
    def download_data(self: PlottingInterface):
        """Downloads data"""
        match self.dataset_name:
            case DatasetName.eac4:
                assert self.eac4_parameters is not None
                data = EAC4Instance(
                    self.eac4_parameters.data_variable,
                    "netcdf",
                    dates_range=self.eac4_parameters.dates_range,
                    time_values=self.eac4_parameters.time_values,
                )
                data.download()
            case DatasetName.ghg:
                assert self.ghg_parameters is not None
                data = InversionOptimisedGreenhouseGas(
                    data_variable=self.ghg_parameters.data_variable,
                    file_format="zip",
                    quantity=self.ghg_parameters.quantity,
                    input_observations=self.ghg_parameters.input_observations,
                    time_aggregation=self.ghg_parameters.time_aggregation,
                    year=self.ghg_parameters.year,
                    month=self.ghg_parameters.month,
                )
                data.download()
        return data.read_dataset()

    @abstractmethod
    def transform_data(self: PlottingInterface):
        """Transforms data as needed"""
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def plot(self: PlottingInterface):
        """Returns a plot"""
        raise NotImplementedError("Method not implemented")


class TimeSeriesPlotInstance(PlottingInterface):
    """Time series plot object"""

    # pylint: disable=too-many-arguments

    _plot_type: PlotType = PlotType.time_series
    _data_array: DataArray

    def __init__(
        self: PlottingInterface,
        dataset_name: DatasetName,
        title: str,
        countries: list[str],
        resampling: str,
        eac4_parameters: EAC4Parameters,
        ghg_parameters: GHGParameters,
    ):
        match dataset_name:
            case DatasetName.eac4:
                super().__init__(
                    dataset_name,
                    eac4_parameters,
                    None,
                    countries,
                    title,
                )
            case DatasetName.ghg:
                super().__init__(
                    dataset_name,
                    None,
                    ghg_parameters,
                    countries,
                    title,
                )
        self.resampling = resampling

    def download_data(self: TimeSeriesPlotInstance):
        self._data_array = super().download_data()

    def transform_data(self: TimeSeriesPlotInstance):
        df_down = self._data_array.rio.write_crs("EPSG:4326")
        df_clipped = clip_and_concat_countries(df_down, self.countries).sel(
            admin=self.countries[0]
        )
        df_agg = (
            df_clipped.mean(dim=["latitude", "longitude"])
            .resample(time=self.resampling, restore_coord_dims=True)
            .mean(dim="time")
        )
        reference_value = df_agg.mean(dim="time")
        df_converted = convert_units_array(df_agg[self.var_name], self.data_variable)
        reference_value = df_converted.mean().values
        df_anomalies = df_converted - reference_value
        df_anomalies.attrs = df_converted.attrs
        self._data_array = df_anomalies

    def plot(self: TimeSeriesPlotInstance) -> go.Figure:
        fig = px.line(
            y=self._data_array.values,
            x=self._data_array.coords["time"],
            markers="o",
        )
        fig.update_xaxes(title="Month")
        fig.update_yaxes(title=self._data_array.attrs["units"])
        fig.update_layout(
            title={
                "text": self.title,
                "x": 0.45,
                "y": 0.95,
                "automargin": True,
                "yref": "container",
                "font": {"size": 19},
            }
        )
        return fig
