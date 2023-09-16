"""This module collects classes to easily interact with data downloaded from CAMS ADS."""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from glob import glob
from itertools import count

import cdsapi

from atmospheric_explorer.api.data_interface.cams_interface.cams_parameters import (
    CAMSParameters,
)
from atmospheric_explorer.api.local_folder import get_local_folder
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger
from atmospheric_explorer.api.os_utils import create_folder, remove_folder


class CAMSDataInterface(ABC):
    # pylint: disable=too-many-instance-attributes
    """Generic interface common to all CAMS datasets."""

    dataset_name: str | None = None
    data_folder: str = os.path.join(get_local_folder(), "data")
    _instances: list[CAMSDataInterface] = []
    _ids: count = count(0)
    file_format = None
    file_ext = None

    def __init__(self: CAMSDataInterface):
        """Initializes CAMSDataInterface instance."""
        self._id = next(self._ids)
        self._instances.append(self)
        create_folder(self.data_folder)
        atm_exp_logger.info("Created folder %s", self.data_folder)
        self.downloaded = False

    def build_call_body(self: CAMSDataInterface, parameters: CAMSParameters):
        """Build call body to be passed to cdsapi."""
        call_body = parameters.build_call_body()
        call_body["format"] = self.file_format
        return call_body

    def _download(
        self: CAMSDataInterface, parameters: CAMSParameters, file_fullpath: str
    ) -> None:
        """Download the dataset and saves it to file specified in filename.

        Uses cdsapi to interact with CAMS ADS.
        """
        client = cdsapi.Client()
        body = self.build_call_body(parameters)
        atm_exp_logger.debug("Calling cdsapi with body %s", body)
        client.retrieve(self.dataset_name, body, file_fullpath)
        atm_exp_logger.info("Finished downloading file %s", file_fullpath)
        self.downloaded = True

    @classmethod
    def list_data_files(cls) -> list:
        """Lists all files inside data folder."""
        return glob(os.path.join(CAMSDataInterface.data_folder, "**"), recursive=True)

    @classmethod
    def clear_data_files(cls) -> None:
        """Clears all files inside data folder."""
        atm_exp_logger.info("Removed data folder.")
        remove_folder(CAMSDataInterface.data_folder)

    @abstractmethod
    def read_dataset(self: CAMSDataInterface):
        """Returns the files as an xarray.Dataset."""
        raise NotImplementedError("Method not implemented")
