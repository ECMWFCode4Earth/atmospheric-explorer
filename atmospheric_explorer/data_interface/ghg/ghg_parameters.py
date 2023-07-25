from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Generator

from atmospheric_explorer.data_interface.cams_interface import CAMSParameters
from atmospheric_explorer.loggers import get_logger

logger = get_logger("atmexp")


@dataclass
class GHGParameters(CAMSParameters):
    file_format: str
    data_variables: str
    quantity: str
    input_observations: str
    time_aggregation: str
    years: str | set[str] | list[str]
    _years: set[int] = field(init=False, repr=False)
    months: str | set[str] | list[str]
    _months: set[int] = field(init=False, repr=False)
    version: str = "latest"

    @staticmethod
    def _convert_to_intset(val: str | set[str] | list[str]) -> set[int]:
        if isinstance(val, str):
            val = [val]
        return set([int(y) for y in val])

    @property
    def years(self: GHGParameters) -> str | list[str]:
        """Years is internally represented as a set of ints, use this property to set/get its value"""
        return (
            [str(y) for y in self._years]
            if len(self._years) > 1
            else str(next(iter(self._years)))
        )

    @years.setter
    def years(self: GHGParameters, years: str | set[str] | list[str]) -> None:
        self._years = self._convert_to_intset(years)

    @property
    def months(self: GHGParameters) -> str | list[str]:
        """Months is internally represented as a set of ints, use this property to set/get its value"""
        return (
            [f"{m:02}" for m in self._months]
            if len(self._months) > 1
            else f"{next(iter(self._months)):02}"
        )

    @months.setter
    def months(self: GHGParameters, months: str | set[str] | list[str]) -> None:
        self._months = self._convert_to_intset(months)

    def _key_var_eq(self, other: GHGParameters) -> bool:
        return (
            other.data_variables == self.data_variables
            and other.file_format == self.file_format
            and other.quantity == self.quantity
            and other.input_observations == self.input_observations
            and other.time_aggregation == self.time_aggregation
            and other.version == self.version
        )

    def __eq__(self, other: GHGParameters) -> bool:
        return (
            self._key_var_eq(other)
            and other._years == self._years
            and other._months == self._months
        )

    def is_eq_superset(self, other: GHGParameters) -> bool:
        """True if self is equal or a superset of other."""
        return (self == other) or (
            self._key_var_eq(other)
            and self._years.issuperset(other._years)
            and self._months.issuperset(other._months)
        )

    def years_months(self: GHGParameters) -> Generator[None, None, tuple[int, int]]:
        """Return the full set of (year, month) tuples"""
        return product(self._years, self._months)

    def build_call_body(self: GHGParameters) -> dict:
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

    def difference(self, other: GHGParameters) -> GHGParameters | None:
        """Return a GHGParameters instance with all non-overlapping parameters."""
        if self._key_var_eq(other):
            logger.debug(
                "Parameters have the same key variables, moving to compute year and month difference"
            )
            self_ym = set(self.years_months())
            other_ym = set(other.years_months())
            ym_diff = other_ym - other_ym.intersection(self_ym)
            if ym_diff:
                logger.debug("Parameters have different years and months, returning an inclusive parameter set")
                return GHGParameters(
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
    p1 = GHGParameters(
        file_format="a",
        data_variables="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4"],
        months=["1", "2"],
    )
    p2 = GHGParameters(
        file_format="a",
        data_variables="e",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4", "5"],
        months=["1", "2", "3"],
    )
    print(p1.difference(p2))
