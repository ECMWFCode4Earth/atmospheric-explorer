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

import cdsapi

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder, get_local_folder

logger = get_logger("atmexp")


class CAMSParameters(ABC):
    @abstractmethod
    def build_call_body(self: CAMSParameters):
        raise NotImplementedError("Method not implemented")


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
    ):
        self._id = next(self._ids)
        self._instances.append(self)
        create_folder(self._data_folder)
        logger.info("Created folder %s", self._data_folder)

    def _download(
        self: CAMSDataInterface, parameters: CAMSParameters, file_fullpath: str
    ) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        client = cdsapi.Client()
        client.retrieve(self._dataset_name, parameters.build_call_body(), file_fullpath)
        logger.info("Finished downloading file %s", file_fullpath)

    @abstractmethod
    def read_dataset(self: CAMSDataInterface):
        """Returns the files as an xarray.Dataset"""
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def download(self: CAMSDataInterface):
        """Returns the files as an xarray.Dataset"""
        raise NotImplementedError("Method not implemented")
