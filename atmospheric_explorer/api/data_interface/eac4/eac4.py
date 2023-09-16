"""This module collects classes to easily interact with EAC4 data downloaded from CAMS ADS."""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os

import xarray as xr

from atmospheric_explorer.api.cache import Cached
from atmospheric_explorer.api.config import CRS
from atmospheric_explorer.api.data_interface.cams_interface import CAMSDataInterface
from atmospheric_explorer.api.data_interface.eac4.eac4_parameters import EAC4Parameters
from atmospheric_explorer.api.loggers import atm_exp_logger
from atmospheric_explorer.api.os_utils import create_folder


class EAC4Instance(CAMSDataInterface, Cached):
    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    """Interface for CAMS global reanalysis (EAC4) and CAMS global reanalysis (EAC4) monthly averaged fields datasets.

    See https://confluence.ecmwf.int/display/CKB/CAMS%3A+Reanalysis+data+documentation#heading-CAMSglobalreanalysisEAC4Parameterlistings
    for a full list of parameters and more details about the dataset.
    """
    dataset_name: str = "cams-global-reanalysis-eac4"
    dataset_dir: str = os.path.join(CAMSDataInterface.data_folder, dataset_name)
    file_format = "netcdf"
    file_ext = "nc"

    def __new__(
        cls: Cached,
        data_variables: set[str] | list[str],
        dates_range: str,
        time_values: set[str] | list[str],
        files_dir: str | None = None,
        area: list[int] | None = None,
        pressure_level: set[str] | list[str] | None = None,
        model_level: set[str] | list[str] | None = None,
    ):
        params = EAC4Parameters(
            data_variables=data_variables,
            dates_range=dates_range,
            time_values=time_values,
            area=area,
            pressure_level=pressure_level,
            model_level=model_level,
        )
        return Cached.__new__(EAC4Instance, params)

    @Cached.init_cache
    def __init__(
        self,
        data_variables: set[str] | list[str],
        dates_range: str,
        time_values: set[str] | list[str],
        files_dir: str | None = None,
        area: list[int] | None = None,
        pressure_level: set[str] | list[str] | None = None,
        model_level: set[str] | list[str] | None = None,
    ):
        """Initializes EAC4Instance instance.

        Attributes:
            data_variables (set[str] | list[str]): data varaibles to be downloaded from CAMS,
                see https://confluence.ecmwf.int/display/CKB/CAMS%3A+Reanalysis+data+documentation#heading-CAMSglobalreanalysisEAC4Parameterlistings
            dates_range (str): range of dates to consider, provided as a 'start/end' string with dates in ISO format
            time_values (set[str] | list[str]): times in 'HH:MM' format. A set or a list of values can be provided.
                Accepted values are [00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00]
            files_dir (str | None): directory where to save the data. If not provided will be built using
                a dinamically generated name
            area (list[int]): latitude-longitude area box to be considered, provided as a list of four values
                [NORTH, WEST, SOUTH, EAST]. If not provided, full area will be considered
            pressure_level (set[str] | list[str] | None): pressure levels to be considered for multilevel variables.
                Can be a set or a list of levels, see documentation linked above for all possible values.
            model_level (set[str] | list[str] | None): model levels to be considered for multilevel variables.
                Can be a set or a list of levels, chosen in a range from 1 to 60.
                See documentation linked above for all possible values.
        """
        super().__init__()
        self.parameters = EAC4Parameters(
            data_variables=data_variables,
            dates_range=dates_range,
            time_values=time_values,
            area=area,
            pressure_level=pressure_level,
            model_level=model_level,
        )
        self.files_dirname = files_dir if files_dir is not None else f"data_{self._id}"
        self.files_dir_path = os.path.join(self.dataset_dir, self.files_dirname)
        if not os.path.exists(self.files_dir_path):
            create_folder(self.files_dir_path)
        atm_exp_logger.info("Created folder %s", self.files_dir_path)

    @property
    def file_full_path(self: EAC4Instance) -> str:
        """Name of the saved file."""
        return os.path.join(
            self.files_dir_path, f"{self.files_dirname}.{self.file_ext}"
        )

    def download(self: EAC4Instance) -> None:
        """Downloads the dataset and saves it to file specified in filename.

        Uses cdsapi to interact with CAMS ADS.
        """
        atm_exp_logger.info("Downloading dataset %s", self)
        if not self.downloaded:
            super()._download(self.parameters, self.file_full_path)

    def _simplify_dataset(self: EAC4Instance, dataset: xr.Dataset):
        return dataset.rio.write_crs(CRS)

    def read_dataset(self: EAC4Instance) -> xr.Dataset:
        """Returns data as an xarray.Dataset."""
        return self._simplify_dataset(xr.open_dataset(self.file_full_path))
