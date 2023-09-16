"""Config for EAC4 APIs."""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import xarray as xr

from atmospheric_explorer.api.data_interface.dataset_config_parser import (
    DatasetConfigParser,
)
from atmospheric_explorer.api.loggers import atm_exp_logger
from atmospheric_explorer.api.singleton import Singleton


class EAC4Config(DatasetConfigParser, metaclass=Singleton):
    # pylint: disable=too-few-public-methods
    """This class is needed to implement a singleton pattern so that config is loaded only once."""

    def __init__(self):
        super().__init__(filename="eac4/eac4_config.yaml")

    @classmethod
    def convert_units_array(
        cls, array: xr.DataArray, data_variable: str
    ) -> xr.DataArray:
        """Converts an xarray.DataArray from its original units to the units specified in the eac4_config.yaml file."""
        conf = cls.get_config()["variables"][data_variable]
        conv_f = float(conf["conversion"]["conversion_factor"])
        atm_exp_logger.debug(
            "Converting array %s to unit %s with factor %f",
            array.name,
            conf["conversion"]["convert_unit"],
            conv_f,
        )
        res = array * conv_f
        res.attrs = array.attrs
        res.attrs["units"] = conf["conversion"]["convert_unit"]
        return res
