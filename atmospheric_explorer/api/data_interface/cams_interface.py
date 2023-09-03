"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from itertools import count

import cdsapi

from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.os_manager import create_folder, get_local_folder

logger = get_logger("atmexp")


class CAMSDataInterface(ABC):
    # pylint: disable=too-many-instance-attributes
    """\
    Generic interface common to all CAMS datasets.

    Attributes:
        data_variables (str | list[str]): data varaibles to be downloaded from CAMS, depend on the dataset
    """

    dataset_name: str | None = None
    data_folder: str = os.path.join(get_local_folder(), "data")
    _instances: list[CAMSDataInterface] = []
    _ids: count = count(0)
    file_format = None
    file_ext = None

    def __init__(self: CAMSDataInterface, data_variables: str | set[str] | list[str]):
        self._id = next(self._ids)
        self._instances.append(self)
        self.data_variables = data_variables
        create_folder(self.data_folder)
        logger.info("Created folder %s", self.data_folder)

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

    def _build_call_body(self: CAMSDataInterface) -> dict:
        """Build the CDSAPI call body"""
        return {"format": self.file_format, "variable": self.data_variables}

    def _download(self: CAMSDataInterface, file_fullpath: str) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        client = cdsapi.Client()
        body = self._build_call_body()
        logger.debug("Calling cdsapi with body %s", body)
        client.retrieve(self.dataset_name, body, file_fullpath)
        logger.info("Finished downloading file %s", file_fullpath)

    @abstractmethod
    def read_dataset(self: CAMSDataInterface):
        """Returns the files as an xarray.Dataset"""
        raise NotImplementedError("Method not implemented")
