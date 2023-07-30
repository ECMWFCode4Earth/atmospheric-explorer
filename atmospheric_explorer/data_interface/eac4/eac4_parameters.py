from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Generator

from atmospheric_explorer.data_interface.cams_interface.cams_interface import CAMSParameters
from atmospheric_explorer.loggers import get_logger

logger = get_logger("atmexp")


@dataclass
class EAC4Parameters(CAMSParameters):
    file_format: str
    data_variables: str | set[str] | list[str]
    _data_variables: set[str] = field(init=False, repr=False)
    dates_range: str
    _dates_range: str
    time_values: str | set[str] | list[str]
    _time_values: set[str] = field(init=False, repr=False)
    area: list[int] | None = None
    pressure_level: str | set[str] | list[str] | None = None
    _pressure_level: set[int] = field(init=False, repr=False)
    model_level: str | set[str] | list[str] | None = None
    _model_level: set[int] = field(init=False, repr=False)

    @staticmethod
    def _convert_to_intset(val: str | set[str] | list[str]) -> set[int]:
        if isinstance(val, str):
            val = [val]
        return set([int(y) for y in val])

    @property
    def data_variables(self: EAC4Parameters) -> str | list[str]:
        """data_variables is internally represented as a set of str, use this property to set/get its value"""
        return (
            list(self._data_variables)
            if len(self._data_variables) > 1
            else next(iter(self._data_variables))
        )

    @data_variables.setter
    def data_variables(self: EAC4Parameters, data_variables: str | set[str] | list[str]) -> None:
        self._data_variables = set(data_variables)

    @property
    def time_values(self: EAC4Parameters) -> str | list[str]:
        """time_values is internally represented as a set of str, use this property to set/get its value"""
        return (
            list(self._time_values)
            if len(self._time_values) > 1
            else next(iter(self._time_values))
        )

    @time_values.setter
    def time_values(self: EAC4Parameters, time_values: str | set[str] | list[str]) -> None:
        self._time_values = set(time_values)

    @property
    def pressure_level(self: EAC4Parameters) -> str | list[str]:
        """pressure_level is internally represented as a set of str, use this property to set/get its value"""
        return (
            list(self._pressure_level)
            if len(self._pressure_level) > 1
            else next(iter(self._pressure_level))
        )

    @pressure_level.setter
    def pressure_level(self: EAC4Parameters, pressure_level: str | set[str] | list[str]) -> None:
        self._pressure_level = set(pressure_level)

    @property
    def model_level(self: EAC4Parameters) -> str | list[str]:
        """model_level is internally represented as a set of str, use this property to set/get its value"""
        return (
            list(self._model_level)
            if len(self._model_level) > 1
            else next(iter(self._model_level))
        )

    @model_level.setter
    def model_level(self: EAC4Parameters, model_level: str | set[str] | list[str]) -> None:
        self._model_level = set(model_level)

    def _key_var_eq(self, other: EAC4Parameters) -> bool:
        return other.file_format == self.file_format

    def __eq__(self, other: EAC4Parameters) -> bool:
        return (
            self._key_var_eq(other)
            and other.data_variables == self.data_variables
            and other.dates_range == self.dates_range
            and other.time_values == self.time_values
            and other.area == self.area
            and other.pressure_level == self.pressure_level
            and other.model_level == self.model_level
        )

    def is_eq_superset(self, other: EAC4Parameters) -> bool:
        """True if self is equal or a superset of other."""
        return (self == other) or (
            self._key_var_eq(other)
            and self._data_variables.issuperset(other._data_variables)
            and self._data_variables.issuperset(other._data_variables)
            and self._data_variables.issuperset(other._data_variables)
            and self._data_variables.issuperset(other._data_variables)
            and self._data_variables.issuperset(other._data_variables)
            and self._data_variables.issuperset(other._data_variables)
        )

    def years_months(self: EAC4Parameters) -> Generator[None, None, tuple[int, int]]:
        """Return the full set of (year, month) tuples"""
        return product(self._years, self._months)

    def build_call_body(self: EAC4Parameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            "format": self.file_format,
            "variable": self.data_variables,
            "quantity": self.quantity,
            "input_observations": self.input_observations,
            "time_aggregation": self.time_aggregation,
            "year": self.years,
            "month": self.months,
            "version": self.version,
        }

    def difference(self, other: EAC4Parameters) -> EAC4Parameters | None:
        """Return a EAC4Parameters instance with all non-overlapping parameters."""
        if self._key_var_eq(other):
            logger.debug(
                "Parameters have the same key variables, moving to compute year and month difference"
            )
            self_ym = set(self.years_months())
            other_ym = set(other.years_months())
            ym_diff = other_ym - other_ym.intersection(self_ym)
            if ym_diff:
                logger.debug("Parameters have different years and months, returning an inclusive parameter set")
                return EAC4Parameters(
                    data_variables=self.data_variables,
                    file_format=self.file_format,
                    quantity=self.quantity,
                    input_observations=self.input_observations,
                    time_aggregation=self.time_aggregation,
                    years={str(ym[0]) for ym in ym_diff},
                    months={str(ym[1]) for ym in ym_diff},
                    version=self.version,
                )
            else:
                logger.debug("Parameters are the same")
                return None
        else:
            logger.debug("Parameters have different key variables")
            return other


if __name__ == "__main__":
    p1 = EAC4Parameters(
        file_format="a",
        data_variables="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4"],
        months=["1", "2"],
    )
    p2 = EAC4Parameters(
        file_format="a",
        data_variables="e",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4", "5"],
        months=["1", "2", "3"],
    )
    print(p1.difference(p2))
