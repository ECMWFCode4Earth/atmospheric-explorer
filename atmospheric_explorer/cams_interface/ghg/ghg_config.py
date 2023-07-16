"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import xarray as xr

from atmospheric_explorer.cams_interface.config_parser import ConfigMeta
from atmospheric_explorer.loggers import get_logger

logger = get_logger("atmexp")


class GHGConfig(metaclass=ConfigMeta, filename="ghg/ghg_config.yaml"):
    # pylint: disable=too-few-public-methods
    """\
    This class is needed to implement a singleton pattern so that
    config is loaded only once.
    """

    @classmethod
    def get_config(cls) -> dict:
        """Function to get the actual config object."""
        logger.debug("Loading ghg config")
        return cls().config

    @classmethod
    def convert_units_array(
        cls,
        array: xr.DataArray,
        data_variable: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
    ) -> xr.DataArray:
        """\
        Converts an xarray.DataArray from its original units
        to the units specified in the constants.cfg file.
        """
        conf = cls.get_config()[data_variable][quantity][input_observations][
            time_aggregation
        ]
        conv_f = float(conf["conversion_factor"])
        new_unit = conf["convert_units"]
        res = array * conv_f
        res.attrs = array.attrs
        res.attrs["units"] = new_unit
        return res
