from __future__ import annotations

from itertools import product
from typing import Generator

from atmospheric_explorer.data_interface.cams_interface.parameters_types import Parameter, SetParameter
from atmospheric_explorer.data_interface.cams_interface.cams_parameters import CAMSParameters
from atmospheric_explorer.loggers import get_logger
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import field_validator, Field

logger = get_logger("atmexp")


@pydantic_dataclass
class GHGParameters(CAMSParameters):
    data_variables: Parameter
    quantity: Parameter
    input_observations: Parameter
    time_aggregation: Parameter
    years: SetParameter
    months: SetParameter
    version: Parameter = Field(default_factory=lambda: Parameter("latest"))

    @field_validator('months', mode='before')
    def _(cls, v):
        if isinstance(v, SetParameter):
            return SetParameter(value=v.value, format_str="0>2")
        else:
            return SetParameter(value=v, format_str="0>2")

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
            and self.years.is_eq_superset(other.years)
            and self.months.is_eq_superset(other.months)
        )

    def years_months(self: GHGParameters) -> Generator[None, None, tuple[int, int]]:
        """Return the full set of (year, month) tuples"""
        return product(self.years, self.months)

    def build_call_body(self: GHGParameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            "format": self.file_format.value_api,
            "variable": self.data_variables.value_api,
            "quantity": self.quantity.value_api,
            "input_observations": self.input_observations.value_api,
            "time_aggregation": self.time_aggregation.value_api,
            "year": self.years.value_api,
            "month": self.months.value_api,
            "version": self.version.value_api,
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
                    years=SetParameter({ym[0] for ym in ym_diff}),
                    months=SetParameter({ym[1] for ym in ym_diff}),
                    version=self.version,
                )
            else:
                logger.debug("Parameters are the same")
                return None
        else:
            logger.debug("Parameters have different key variables")
            return other

    @classmethod
    def from_base_types(
        cls,
        file_format: str,
        data_variables: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
        years: str | list[str] | set[str],
        months: str | list[str] | set[str],
        version: str | None = None
    ):
        if version is None:
            return cls(
                file_format = Parameter(file_format),
                data_variables = Parameter(data_variables),
                quantity = Parameter(quantity),
                input_observations = Parameter(input_observations),
                time_aggregation = Parameter(time_aggregation),
                years = SetParameter(years),
                months = SetParameter(months)
            )
        else:
            return cls(
                file_format = Parameter(file_format),
                data_variables = Parameter(data_variables),
                quantity = Parameter(quantity),
                input_observations = Parameter(input_observations),
                time_aggregation = Parameter(time_aggregation),
                years = SetParameter(years),
                months = SetParameter(months),
                version = Parameter(version)
            )


if __name__ == "__main__":
    p1 = GHGParameters.from_base_types(
        file_format="a",
        data_variables="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4"],
        months=["1", "2"],
    )
    p2 = GHGParameters.from_base_types(
        file_format="a",
        data_variables="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=["1", "2", "3", "4", "5"],
        months=["1", "2"],
    )
    print(p1.difference(p2))
