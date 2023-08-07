from __future__ import annotations

from atmospheric_explorer.data_interface.cams_interface.parameters_types import SetParameter, DateIntervalParameter, IntSetParameter
from atmospheric_explorer.data_interface.cams_interface.cams_parameters import CAMSParameters
from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from datetime import datetime
from itertools import pairwise, groupby

logger = get_logger("atmexp")


@pydantic_dataclass
class EAC4Parameters(CAMSParameters):
    data_variables: SetParameter
    dates_range: DateIntervalParameter
    time_values: SetParameter
    pressure_level: IntSetParameter | None = None
    model_level: IntSetParameter | None = None

    def __eq__(self, other: EAC4Parameters) -> bool:
        return (
            other.data_variables == self.data_variables
            and other.dates_range == self.dates_range
            and other.time_values == self.time_values
            and other.pressure_level == self.pressure_level
            and other.model_level == self.model_level
        )

    def is_eq_superset(self, other: EAC4Parameters) -> bool:
        """True if self is equal or a superset of other."""
        return (self == other) or (
            self.data_variables.is_eq_superset(other.data_variables)
            and self.dates_range.is_eq_superset(other.dates_range)
            and self.time_values.is_eq_superset(other.time_values)
            and self.pressure_level.is_eq_superset(other.pressure_level)
            and self.model_level.is_eq_superset(other.model_level)
        )

    def build_call_body(self: EAC4Parameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            "variable": self.data_variables.value_api,
            "dates": self.dates_range.value_api,
            "times": self.time_values.value_api,
            "pressure_level": self.pressure_level.value_api,
            "model_level": self.model_level.value_api
        }

    def _data_diff(self, other: EAC4Parameters) -> SetParameter | None:
        if other.data_variables.is_eq_superset(self.data_variables):
            return None
        return self.data_variables.difference(other.data_variables)

    def _dates_diff(self, other: EAC4Parameters) -> DateIntervalParameter | None:
        if other.dates_range.is_eq_superset(self.dates_range):
            return None
        return self.dates_range.difference(other.dates_range)

    def _times_diff(self, other: EAC4Parameters) -> SetParameter | None:
        if other.time_values.is_eq_superset(self.time_values):
            return None
        return self.time_values.difference(other.time_values)

    def _pl_diff(self, other: EAC4Parameters) -> SetParameter | None:
        if other.pressure_level.is_eq_superset(self.pressure_level):
            return None
        return self.pressure_level.difference(other.pressure_level)

    def _ml_diff(self, other: EAC4Parameters) -> SetParameter | None:
        if other.model_level.is_eq_superset(self.model_level):
            return None
        return self.model_level.difference(other.model_level)

    def difference(self, other: EAC4Parameters) -> SetParameter | None:
        """Return a EAC4Parameters instance with all non-overlapping parameters."""
        if other.is_eq_superset(self):
            return None
        else:
            logger.debug(
                "Parameters have the same data variables, moving to compute difference"
            )
            dv_diff = self._data_diff(other)
            dates_diff = self._dates_diff(other)
            times_diff = self._times_diff(other)
            pl_diff = self._pl_diff(other)
            ml_diff = self._ml_diff(other)
            if dv_diff is not None:
                logger.debug(
                    "Parameters have different data variables"
                )
                if (dates_diff or times_diff or pl_diff or ml_diff) is not None:
                    logger.debug(
                        "Other parameters area different, downloading strict superset"
                    )
                    return EAC4Parameters(
                        data_variables=self.data_variables.merge(other.data_variables),
                        dates_range=self.dates_range.merge(other.dates_range),
                        time_values=self.time_values.merge(other.time_values),
                        pressure_level=self.pressure_level.merge(other.pressure_level),
                        model_level=self.model_level.merge(other.model_level)
                    )
                else:
                    logger.debug(
                        "Other parameters are the same, downloading only the new data variables"
                    )
                    return EAC4Parameters(
                        data_variables=dv_diff,
                        dates_range=self.dates_range,
                        time_values=self.time_values,
                        pressure_level=self.pressure_level,
                        model_level=self.model_level
                    )
            else:
                logger.debug("Data variables are the same, computing differences")
                return EAC4Parameters(
                    data_variables=self.data_variables,
                    dates_range=dates_diff if dates_diff is not None else self.dates_range,
                    time_values=times_diff if times_diff is not None else self.time_values,
                    pressure_level=pl_diff if pl_diff is not None else self.pressure_level,
                    model_level=ml_diff if ml_diff is not None else self.model_level
                )

    @classmethod
    def from_base_types(
        cls,
        data_variables: str | set[str] | list[str],
        dates_range: str,
        time_values: str | set[str] | list[str],
        pressure_level: str | set[str] | list[str] | None = None,
        model_level: str | set[str] | list[str] | None = None,
    ) -> EAC4Parameters:
        return cls(
            data_variables = SetParameter(data_variables),
            dates_range = DateIntervalParameter(dates_range),
            time_values = SetParameter(time_values),
            pressure_level = IntSetParameter(pressure_level) if pressure_level is not None else None,
            model_level = IntSetParameter(model_level) if model_level is not None else None
        )
    
    @classmethod
    def merge(cls, parameters: list[EAC4Parameters]) -> EAC4Parameters:
        dv = set()
        pl = set()
        ml = set()
        times = set()
        dates = parameters[0].dates_range
        for p in parameters:
            dv.update(p.data_variables.value)
            pl.update(p.pressure_level.value if p.pressure_level is not None else [-1])
            ml.update(p.model_level.value if p.model_level is not None else [-1])
            times.update(p.time_values.value)
            dates = dates.merge(p.dates_range)
        return cls(
            data_variables=SetParameter(dv),
            dates_range=dates,
            time_values=SetParameter(times),
            pressure_level=IntSetParameter(pl),
            model_level=IntSetParameter(ml)
        )


if __name__ == "__main__":
    p1 = EAC4Parameters.from_base_types(
        data_variables="b",
        dates_range="2021-01-01/2021-02-01",
        time_values=["00:00"],
        pressure_level=["1", "2", "3", "4"],
        model_level=["1", "2"],
    )
    p2 = EAC4Parameters.from_base_types(
        data_variables="b",
        dates_range="2021-01-01/2022-01-05",
        time_values=["00:00"],
        pressure_level=["1", "2", "3", "4"],
        model_level=["1", "2"],
    )
    print(p2.difference(p1))
