"""\
APIs for generating dynamic and static plots
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import plotly.express as px
import plotly.graph_objects as go

PlotType = Enum("PlotType", ["time_series", "hovmoeller"])


class PlottingInterface(ABC):
    """Generic interface for all plotting APIs"""

    _plot_type: PlotType

    def __init__(
        self: PlottingInterface,
        _data_variable: str,
        _var_name: str,
        _time_period: str,
    ):
        self.data_variable = _data_variable
        self.var_name = _var_name
        self.time_period = _time_period

    @property
    def data_variable(self: PlottingInterface) -> str:
        """Data variable name"""
        return self._data_variable

    @data_variable.setter
    def data_variable(
        self: PlottingInterface,
        data_variable_input: str,
    ) -> None:
        self._data_variable = data_variable_input

    @abstractmethod
    def plot(self: PlottingInterface):
        """Returns a plot"""
        raise NotImplementedError("Method not implemented")


class TimeSeriesPlotInstance(PlottingInterface):
    """Time series plot object"""

    _plot_type: PlotType = PlotType.time_series

    # def __init__(
    #     self: PlottingInterface,
    #     data_variable: str,
    #     var_name: str,
    #     time_period: str,
    # ):
    #     super().__init__(data_variable, var_name, time_period)

    def plot(
        self: TimeSeriesPlotInstance,
    ) -> go.Figure:
        fig = px.line()
        return fig
