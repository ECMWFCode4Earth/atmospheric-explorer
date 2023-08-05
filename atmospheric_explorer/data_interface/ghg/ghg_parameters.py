from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Generator

from atmospheric_explorer.data_interface.cams_interface import CAMSParameters
from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import computed_field, field_validator

logger = get_logger("atmexp")


@pydantic_dataclass
class GHGParameters(CAMSParameters):
    file_format: str
    data_variables: str
    quantity: str
    input_observations: str
    time_aggregation: str
    years: set[int]
    months: set[int]
    version: str = "latest"

    @field_validator('years', 'months', mode='before')
    def _(cls: GHGParameters, value: str | set[str] | list[str]) -> set[int]:
        if isinstance(value, str):
            value = [value]
        return {int(v) for v in value}

    @computed_field
    @property
    def years_api(self: GHGParameters) -> str | list[str]:
        """Years is internally represented as a set of ints, use this property to set/get its value"""
        return (
            [str(y) for y in self.years]
            if len(self.years) > 1
            else str(next(iter(self.years)))
        )

    @computed_field
    @property
    def months_api(self: GHGParameters) -> str | list[str]:
        """Months is internally represented as a set of ints, use this property to set/get its value"""
        return (
            [f"{m:02}" for m in self.months]
            if len(self.months) > 1
            else f"{next(iter(self.months)):02}"
        )

    def _point_var_eq(self, other: GHGParameters) -> bool:
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
            self._point_var_eq(other)
            and other.years == self.years
            and other.months == self.months
        )

    def is_eq_superset(self, other: GHGParameters) -> bool:
        """True if self is equal or a superset of other."""
        return (self == other) or (
            self._point_var_eq(other)
            and self.years.issuperset(other.years)
            and self.months.issuperset(other.months)
        )

    def years_months(self: GHGParameters) -> Generator[None, None, tuple[int, int]]:
        """Return the full set of (year, month) tuples"""
        return product(self.years, self.months)

    def build_call_body(self: GHGParameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            "format": self.file_format,
            "variable": self.data_variables,
            "quantity": self.quantity,
            "input_observations": self.input_observations,
            "time_aggregation": self.time_aggregation,
            "year": self.years_api,
            "month": self.months_api,
            "version": self.version,
        }

    def _ym_difference(self, other: GHGParameters) -> set:
        """Return the list with all remaining year-month tuples."""
        self_ym = set(self.years_months())
        other_ym = set(other.years_months())
        return other_ym - other_ym.intersection(self_ym)

    def difference(self, other: GHGParameters) -> GHGParameters | None:
        """Return a GHGParameters instance with all non-overlapping parameters."""
        if self._point_var_eq(other):
            logger.debug(
                "Parameters have the same key variables, moving to compute year and month difference"
            )
            ym_diff = self._ym_difference(other)
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
