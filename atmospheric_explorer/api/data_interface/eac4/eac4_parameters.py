"""This module collects classes to easily interact with data downloaded from CAMS ADS."""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from textwrap import dedent

from atmospheric_explorer.api.data_interface.cams_interface import CAMSParameters
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger


class EAC4Parameters(CAMSParameters):
    # pylint: disable=line-too-long
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
        """Initializes EAC4Parameters instance.

        Attributes:
            data_variables (set[str] | list[str]): data varaibles to be downloaded from CAMS,
                see https://confluence.ecmwf.int/display/CKB/CAMS%3A+Reanalysis+data+documentation#heading-CAMSglobalreanalysisEAC4Parameterlistings
            dates_range (str): range of dates to consider, provided as a 'start/end' string with dates in ISO format
            time_values (set[str] | list[str]): times in 'HH:MM' format. A set or a list of values can be provided.
                Accepted values are [00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00]
            area (list[int]): latitude-longitude area box to be considered, provided as a list of four values
                [NORTH, WEST, SOUTH, EAST]. If not provided, full area will be considered
            pressure_level (set[str] | list[str] | None): pressure levels to be considered for multilevel variables.
                Can be a set or a list of levels, see documentation linked above for all possible values.
            model_level (set[str] | list[str] | None): model levels to be considered for multilevel variables.
                Can be a set or a list of levels, chosen in a range from 1 to 60.
                See documentation linked above for all possible values.
        """
        super().__init__(data_variables)
        self.dates_range = dates_range
        self.time_values = set(time_values)
        self.area = area
        self.pressure_level = (
            set(pressure_level) if pressure_level is not None else pressure_level
        )
        self.model_level = set(model_level) if model_level is not None else model_level

    def __repr__(self) -> str:
        """Parameters representation."""
        return dedent(
            f"""\
        data_variables: {self.data_variables}
        dates_range: {self.dates_range}
        time_values: {self.time_values}
        area: {self.area}
        pressure_level: {self.pressure_level}
        model_level: {self.model_level}
        """
        )

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

    def subset(self: EAC4Parameters, other: EAC4Parameters) -> bool:
        # pylint: disable = protected-access
        """Return true if the parameters of this instance are equal or a subset of other.

        Attributes:
            other (EAC4Parameters): the other instance of EAC4Parameters to be compared with self
        """
        res = (
            self._data_variables.issubset(other._data_variables)
            and EAC4Parameters.dates_issubset(self.dates_range, other.dates_range)
            and self.time_values.issubset(other.time_values)
            and EAC4Parameters.area_issubset(self.area, other.area)
            and EAC4Parameters.pressure_issubset(
                self.pressure_level, other.pressure_level
            )
            and EAC4Parameters.model_issubset(self.model_level, other.model_level)
        )
        atm_exp_logger.debug("Subset result: %s\nself: %s\nother: %s", res, self, other)
        return res

    def build_call_body(self: EAC4Parameters) -> dict:
        """Build the CDSAPI call body."""
        call_body = super().build_call_body()
        call_body["date"] = self.dates_range
        call_body["time"] = list(self.time_values)
        if self.area is not None:
            call_body["area"] = self.area
        if self.pressure_level is not None:
            call_body["pressure_level"] = list(self.pressure_level)
        if self.model_level is not None:
            call_body["model_level"] = list(self.model_level)
        atm_exp_logger.debug("Call body for %s:\n%s", self, call_body)
        return call_body
