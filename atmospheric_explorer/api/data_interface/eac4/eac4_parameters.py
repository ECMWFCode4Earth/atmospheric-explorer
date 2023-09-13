"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from atmospheric_explorer.api.data_interface.cams_interface import CAMSParameters
from atmospheric_explorer.api.loggers import get_logger
from textwrap import dedent

logger = get_logger("atmexp")


class EAC4Parameters(CAMSParameters):
    """Parameters for EAC4 dataset."""

    def __init__(
        self: EAC4Parameters,
        data_variables: set[str] | list[str],
        dates_range: str,
        time_values: set[str] | list[str],
        area: list[int] | None = None,
        pressure_level: set[str] | list[str] | None = None,
        model_level: set[str] | list[str] | None = None,
    ) -> None:
        super().__init__(data_variables)
        self.dates_range = dates_range
        self.time_values = set(time_values)
        self.area = area
        self.pressure_level = (
            set(pressure_level) if pressure_level is not None else pressure_level
        )
        self.model_level = set(model_level) if model_level is not None else model_level

    def __repr__(self) -> str:
        return dedent(f"""\
        data_variables: {self.data_variables}
        dates_range: {self.dates_range}
        time_values: {self.time_values}
        area: {self.area}
        pressure_level: {self.pressure_level}
        model_level: {self.model_level}
        """)

    @staticmethod
    def dates_issubset(date_range1, date_range2):
        """Check if the first date range is a subset of the second date range."""
        start1, end1 = date_range1.strip().split("/")
        start2, end2 = date_range2.strip().split("/")
        return start1 >= start2 and end1 <= end2

    @staticmethod
    def _is_subset_none(arg1, arg2) -> bool | None:
        """Returns wether either one or both arguments are None. If no argument is None, returns None."""
        if (arg1 or arg2) is None:
            return arg1 is None and arg2 is None
        return None

    @staticmethod
    def area_issubset(area1: list, area2: list) -> bool:
        """Check if the first area is a subset of the second area."""
        res = EAC4Parameters._is_subset_none(area1, area2)
        if res is not None:
            return res
        north1, west1, south1, east1 = area1
        north2, west2, south2, east2 = area2
        return (
            north1 <= north2 and east1 >= east2 and west1 <= west2 and south1 >= south2
        )

    @staticmethod
    def pressure_issubset(pl1: set | None, pl2: set | None) -> bool:
        """Check if the first pressure level is a subset of the second pressure level."""
        res = EAC4Parameters._is_subset_none(pl1, pl2)
        if res is not None:
            return res
        return pl1.issubset(pl2)

    @staticmethod
    def model_issubset(ml1: set | None, ml2: set | None) -> bool:
        """Check if the first model level is a subset of the second model level."""
        res = EAC4Parameters._is_subset_none(ml1, ml2)
        if res is not None:
            return res
        return ml1.issubset(ml2)

    def subset(self: EAC4Parameters, obj: EAC4Parameters) -> bool:
        return (
            self._data_variables.issubset(obj._data_variables)
            and EAC4Parameters.dates_issubset(self.dates_range, obj.dates_range)
            and self.time_values.issubset(obj.time_values)
            and EAC4Parameters.area_issubset(self.area, obj.area)
            and EAC4Parameters.pressure_issubset(
                self.pressure_level, obj.pressure_level
            )
            and EAC4Parameters.model_issubset(self.model_level, obj.model_level)
        )

    def build_call_body(self: EAC4Parameters) -> dict:
        """Build the CDSAPI call body"""
        call_body = super().build_call_body()
        call_body["date"] = self.dates_range
        call_body["time"] = list(self.time_values)
        if self.area is not None:
            call_body["area"] = self.area
        if self.pressure_level is not None:
            call_body["pressure_level"] = list(self.pressure_level)
        if self.model_level is not None:
            call_body["model_level"] = list(self.model_level)
        return call_body
