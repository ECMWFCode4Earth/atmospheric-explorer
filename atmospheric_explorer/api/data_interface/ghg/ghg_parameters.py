"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from atmospheric_explorer.api.data_interface.cams_interface import CAMSParameters
from atmospheric_explorer.api.loggers import get_logger

logger = get_logger("atmexp")


class GHGParameters(CAMSParameters):
    def __init__(
        self: GHGParameters,
        data_variables: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
        year: set[str] | list[str],
        month: set[str] | list[str],
        version: str = "latest",
    ):
        super().__init__(data_variables)
        self.quantity = quantity
        self.input_observations = input_observations
        self.time_aggregation = time_aggregation
        self.year = set(year)
        self.month = set(month)
        self.version = version

    def subset(self: GHGParameters, obj: GHGParameters):
        return (
            self.data_variables == obj.data_variables
            and self.quantity == obj.quantity
            and self.input_observations == obj.input_observations
            and self.time_aggregation == obj.time_aggregation
            and self.year.issubset(obj.year)
            and self.month.issubset(obj.month)
            and self.version == obj.version
        )

    def build_call_body(self: GHGParameters) -> dict:
        """Build the CDSAPI call body"""
        call_body = super().build_call_body()
        call_body.update(
            {
                "version": self.version,
                "quantity": self.quantity,
                "input_observations": self.input_observations,
                "time_aggregation": self.time_aggregation,
                "year": self.year,
                "month": self.month,
            }
        )
        return call_body
