"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from glob import glob
from itertools import count
from typing import Any

import cdsapi

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder, get_local_folder

logger = get_logger("atmexp")


class CAMSDataInterface(ABC):
    # pylint: disable=too-many-instance-attributes
    """\
    Generic interface common to all CAMS datasets.

    Attributes:
        data_variables (str | list[str]): data varaibles to be downloaded from CAMS, depend on the dataset
        file_format (str): format for the downloaded data, e.g. 'netcdf', 'grib', 'zip' etc.
        filename (str | None): file where to save the data. If not provided will be built using file_format and
            with a dynamically generated name
    """

    _dataset_name: str | None = None
    _data_folder: str = os.path.join(get_local_folder(), "data")
    _instances: list[CAMSDataInterface] = []
    _ids: count = count(len(glob(os.path.join(_data_folder, "*"))))

    def __init__(
        self: CAMSDataInterface,
        data_variables: str | set[str] | list[str],
        file_format: str,
    ):
        self._id = next(self._ids)
        self._instances.append(self)
        self.data_variables = data_variables
        self.file_format = file_format
        create_folder(self._data_folder)
        logger.info("Created folder %s", self._data_folder)

    @property
    def data_variables(self: CAMSDataInterface) -> str | list[str]:
        """Time values are internally represented as a set, use this property to set/get its value"""
        return (
            list(self._data_variables)
            if isinstance(self._data_variables, set)
            else self._data_variables
        )

    @data_variables.setter
    def data_variables(
        self: CAMSDataInterface, data_variables_input: str | set[str] | list[str]
    ) -> None:
        if isinstance(data_variables_input, list):
            data_variables_input = set(data_variables_input)
        self._data_variables = data_variables_input

    @property
    def _file_ext(self: CAMSDataInterface) -> str:
        """Extension of the saved file"""
        match (self.file_format):
            case "netcdf":
                return "nc"
            case _:
                return self.file_format

    def _build_call_body(self: CAMSDataInterface) -> dict:
        """Build the CDSAPI call body"""
        call_body = {"format": self.file_format, "variable": self.data_variables}
        return call_body

    def _download(self: CAMSDataInterface, file_fullpath: str) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        client = cdsapi.Client()
        client.retrieve(self._dataset_name, self._build_call_body(), file_fullpath)
        logger.info("Finished downloading file %s", file_fullpath)

    @staticmethod
    def _is_subset_element(
        arg1: Any | set[Any] | None, arg2: Any | set[Any] | None
    ) -> bool:
        """Utility function. This function"""
        if isinstance(arg1, set):
            if isinstance(arg2, set):
                return arg2.issubset(arg1)
            return arg2 in arg1
        return arg1 == arg2

    def _includes_data_variables(
        self: CAMSDataInterface, data_variables: str | set[str]
    ) -> bool:
        """Determines if the object data variables include the input data variables"""
        return CAMSDataInterface._is_subset_element(
            self._data_variables, data_variables
        )

    @abstractmethod
    def includes(self: CAMSDataInterface, other: CAMSDataInterface):
        """Determines if another object is already included in self"""
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def read_dataset(self: CAMSDataInterface):
        """Returns the files as an xarray.Dataset"""
        raise NotImplementedError("Method not implemented")
