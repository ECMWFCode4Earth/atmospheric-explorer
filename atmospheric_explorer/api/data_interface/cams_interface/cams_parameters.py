"""\
This module defines a generic base class to be used for the CAMS datasets parameters.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from atmospheric_explorer.api.cache import Parameters
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger


class CAMSParameters(Parameters):
    """\
    Base class to be used for CAMS dataset parameters.

    Attributes:
        data_variables (str | set[str] | list[str]): data varaibles to be downloaded from CAMS, depend on the dataset
    """

    def __init__(self, data_variables: str | set[str] | list[str]) -> None:
        atm_exp_logger.debug("Instantiating parameters object %s", type(self).__name__)
        self.data_variables = data_variables

    @property
    def data_variables(self: CAMSParameters) -> str | set[str]:
        """Time values are internally represented as a set, use this property to set/get its value"""
        return (
            self._data_variables
            if len(self._data_variables) > 1
            else next(iter(self._data_variables))
        )

    @data_variables.setter
    def data_variables(
        self: CAMSParameters, data_variables_input: str | set[str] | list[str]
    ) -> None:
        if isinstance(data_variables_input, str):
            data_variables_input = [data_variables_input]
        self._data_variables = set(data_variables_input)

    def subset(self: CAMSParameters, other: CAMSParameters):
        return self.data_variables.issubset(other.data_variables)

    def build_call_body(self: CAMSParameters) -> dict:
        """Build the CDSAPI call body"""
        return {
            "variable": list(self.data_variables)
            if isinstance(self.data_variables, set)
            else self.data_variables
        }
