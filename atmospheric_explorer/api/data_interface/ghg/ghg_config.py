"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import xarray as xr

from atmospheric_explorer.api.data_interface.config_parser import ConfigMeta
from atmospheric_explorer.api.loggers import get_logger

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
        time_aggregation: str,
    ) -> xr.DataArray:
        """\
        Converts an xarray.DataArray from its original units
        to the units specified in the constants.cfg file.
        """
        var_name = array.name
        conf = list(
            filter(
                lambda a: a["var_name"] == var_name,
                cls.get_config()["variables"][data_variable][quantity][
                    time_aggregation
                ],
            )
        )[0]
        conv_f = float(conf["conversion"]["conversion_factor"])
        logger.debug(
            "Converting array %s to unit %s with factor %f",
            var_name,
            conf["conversion"]["convert_unit"],
            conv_f,
        )
        res = array * conv_f
        res.attrs = array.attrs
        res.attrs["units"] = conf["conversion"]["convert_unit"]
        return res
