from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Generator

from atmospheric_explorer.data_interface.cams_interface.parameters_types import Parameter, ListParameter
from atmospheric_explorer.data_interface.cams_interface.cams_parameters import CAMSParameters
from atmospheric_explorer.loggers import get_logger

logger = get_logger("atmexp")


class GHGParameters(CAMSParameters):
    data_variables: Parameter
    quantity: Parameter
    input_observations: Parameter
    time_aggregation: Parameter
    year: ListParameter
    month: ListParameter
    version: Parameter = Parameter(value='latest')

    # def _key_var_eq(self, other: GHGParameters) -> bool:
    #     return (
    #         other.data_variables == self.data_variables
    #         and other.file_format == self.file_format
    #         and other.quantity == self.quantity
    #         and other.input_observations == self.input_observations
    #         and other.time_aggregation == self.time_aggregation
    #         and other.version == self.version
    #     )

    # def __eq__(self, other: GHGParameters) -> bool:
    #     return (
    #         self._key_var_eq(other)
    #         and other.years == self.years
    #         and other.months == self.months
    #     )

    # def is_eq_superset(self, other: GHGParameters) -> bool:
    #     """True if self is equal or a superset of other."""
    #     return (self == other) or (
    #         self._key_var_eq(other)
    #         and self.years.is_eq_superset(other.years)
    #         and self.months.is_eq_superset(other.months)
    #     )

    def years_months(self: GHGParameters) -> Generator[None, None, tuple[int, int]]:
        """Return the full set of (year, month) tuples"""
        return product(self.years.value, self.months.value)

    # def build_call_body(self: GHGParameters) -> dict:
    #     """Build the CDSAPI call body"""
    #     return {
    #         "format": self.file_format.value,
    #         "variable": self.data_variables.value,
    #         "quantity": self.quantity.value,
    #         "input_observations": self.input_observations.value,
    #         "time_aggregation": self.time_aggregation.value,
    #         "year": self.years.value,
    #         "month": self.months.value,
    #         "version": self.version.value,
    #     }

    def _list_difference(self, other: GHGParameters) -> dict:
        self_ym = set(self.years_months())
        other_ym = set(other.years_months())
        diff = other_ym - other_ym.intersection(self_ym)
        return {
            "years": {str(ym[0]) for ym in diff},
            "months": {str(ym[1]) for ym in diff}
        }

    # def difference(self, other: GHGParameters) -> GHGParameters | None:
    #     """Return a GHGParameters instance with all non-overlapping parameters."""
    #     if self._key_var_eq(other):
    #         logger.debug(
    #             "Parameters have the same key variables, moving to compute year and month difference"
    #         )
    #         self_ym = set(self.years_months())
    #         other_ym = set(other.years_months())
    #         ym_diff = other_ym - other_ym.intersection(self_ym)
    #         if ym_diff:
    #             logger.debug("Parameters have different years and months, returning an inclusive parameter set")
    #             return GHGParameters(
    #                 data_variables=self.data_variables,
    #                 file_format=self.file_format,
    #                 quantity=self.quantity,
    #                 input_observations=self.input_observations,
    #                 time_aggregation=self.time_aggregation,
    #                 years={str(ym[0]) for ym in ym_diff},
    #                 months={str(ym[1]) for ym in ym_diff},
    #                 version=self.version,
    #             )
    #         else:
    #             logger.debug("Parameters are the same")
    #             return None
    #     else:
    #         logger.debug("Parameters have different key variables")
    #         return other


if __name__ == "__main__":
    p1 = GHGParameters(
        file_format="a",
        data_variables="b",
        quantity="b",
        input_observations="b",
        time_aggregation="b",
        years=["1", "2", "3", "4"],
        months=["1", "2"],
    )
    p2 = GHGParameters(
        file_format="a",
        data_variables="b",
        quantity="b",
        input_observations="b",
        time_aggregation="b",
        years=["1", "2", "3", "4"],
        months=["1", "2", "3"],
    )
    print(p1.difference(p2))
