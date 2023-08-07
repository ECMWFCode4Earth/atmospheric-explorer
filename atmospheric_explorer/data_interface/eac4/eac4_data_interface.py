"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
import zipfile
from datetime import datetime
from glob import glob

import xarray as xr

from atmospheric_explorer.data_interface.cams_interface.cams_interface import CAMSDataInterface
from atmospheric_explorer.data_interface.cache import Base, cache_engine, CachingStatus
from atmospheric_explorer.data_interface.eac4.eac4_cache import EAC4CacheTable
from atmospheric_explorer.data_interface.eac4.eac4_parameters import EAC4Parameters
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder, get_local_folder
import shutil
from itertools import groupby

logger = get_logger("atmexp")


class EAC4DataInterface(CAMSDataInterface):
    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    """\
    Interface for EAC4 dataset.
    See https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview
    for a full list of parameters and more details about the dataset

    Attributes:
        data_variables (str | list[str]): data varaibles to be downloaded from CAMS,
            see https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview
        file_format (str): format for the downloaded data, can be either 'zip' or 'tar.gz'
        quantity (str): quantity, can be one of ['mean_column', 'surface_flux', 'concentration']
        input_observations (str): input observations, can be one of ['surface', 'satellite', 'surface_satellite']
        time_aggregation (str): time aggregation, can be one of ['instantaneous', 'daily_mean', 'monthly_mean']
        year (str | list[str]): single year or list of years, in 'YYYY' format
        month (str | list[str]): single month or list of months, in 'MM' format
        filename (str | None): file where to save the data. If not provided will be built using file_format and
            with a dinamically generated name
        version (str): version of the dataset, default is 'latest'
    """
    _dataset_name: str = "cams-global-reanalysis-eac4"
    _data_folder: str = os.path.join(
        get_local_folder(), "data", "eac4"
    )
    _file_format = "netcdf"
    _file_ext = "nc"

    def __init__(
        self: EAC4DataInterface,
        data_variables: str,
        dates_range: str,
        time_values: str | set[str] | list[str],
        pressure_level: str | set[str] | list[str] | None = None,
        model_level: str | set[str] | list[str] | None = None,
        files_dir: str | None = None,
    ):
        super().__init__()
        self.parameters = EAC4Parameters.from_base_types(
            data_variables=data_variables,
            dates_range=dates_range,
            time_values=time_values,
            pressure_level=pressure_level,
            model_level=model_level,
        )
        self._cache_status = CachingStatus.UNCACHED
        self._update_parameters()
        if self._diff_parameters is not None:
            logger.info("The parameter specified are not fully cached, creating variables to manage files")
            self.files_dirname = (
                files_dir if files_dir is not None else f"data_{self._id}"
            )
            self.files_dir_path = os.path.join(self._data_folder, self.files_dirname)
            self.file_full_path = self.files_dirname
            create_folder(self.files_dir_path)
            logger.debug("Created folder %s", self.files_dir_path)
        else:
            logger.info("The parameter specified are fully cached")

    @property
    def file_full_path(self: EAC4DataInterface) -> str:
        """Name of the saved file"""
        return self._file_full_path

    @file_full_path.setter
    def file_full_path(self: EAC4DataInterface, filename: str) -> None:
        """Name of the saved file"""
        self._file_full_path = os.path.join(
            self.files_dir_path, f"{filename}.{self._file_ext}"
        )

    @staticmethod
    def _get_cached_parameters(params: EAC4Parameters) -> list(EAC4Parameters) | None:
        """Return cached parameters with the same key variables as the ones in params."""
        rows = EAC4CacheTable.get_rows(params)
        logger.debug("Cached parameters: %s", rows)
        if rows:
            res = []
            param_groups = [[c for _, c in g] for _, g in groupby(rows, key=lambda x: x['param_id'])]
            for params in param_groups:
                date_start = min([p.day for p in params])
                date_end = max([p.day for p in params])
                res.append(EAC4Parameters.from_base_types(
                    data_variables={r.data_variables for r in rows},
                    dates_range=f"{date_start}/{date_end}",
                    time_values={r.time for r in rows},
                    pressure_level={r.pressure_level for r in rows},
                    model_level={r.model_level for r in rows},
                ))
                return res
        return None

    def _clear_data(self: EAC4DataInterface):
        if self._diff_parameters.is_eq_superset(self.parameters):
            files = EAC4CacheTable.get_files([self._diff_parameters])
            for file in files:
                dir = os.path.dirname(file)
                if os.path.exists(dir):
                    shutil.rmtree(dir)
            EAC4CacheTable.delete_rows([self._diff_parameters])

    def _update_parameters(self: EAC4DataInterface) -> None:
        self._cached_parameters = self._get_cached_parameters(self.parameters)
        if self._cached_parameters is not None:
            logger.info("Some data points are already cached, updating parameters")
            self._diff_parameters = self.parameters.difference(self._cached_parameters)
            if self._diff_parameters is None:
                self._cache_status = CachingStatus.FULLY_CACHED
            elif self._diff_parameters.is_eq_superset(self.parameters):
                self._cache_status = CachingStatus.UNCACHED
            else:
                self._cache_status = CachingStatus.PARTIALLY_CACHED
        else:
            logger.info("No data points are cached, updating parameters")
            self._cache_status = CachingStatus.UNCACHED
            self._diff_parameters = self.parameters

    def download(self: EAC4DataInterface) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.

        This function also extracts the netcdf file inside the zip file, which is then deleted.
        """
        # Download only remaining parameters
        if self._diff_parameters is not None:
            logger.info("Downloading non-cached parameters: %s", self._diff_parameters)
            super()._download(self._diff_parameters, self.file_full_path)
            # This dataset downloads zipfiles with possibly multiple netcdf files inside
            # We must extract it
            self._clear_data()
            EAC4CacheTable.cache(self._diff_parameters, self.file_full_path)
            self._update_parameters()
        else:
            logger.info("The parameters specified are already cached, skipping download.")

    def _get_all_files(self: EAC4DataInterface) -> set[str]:
        files = set()
        for file in EAC4CacheTable.get_files([self.parameters]):
            files.update(set(glob(file)))
        logger.debug("Fetching all files associated with parameters: %s", files)
        return files

    def read_dataset(self: EAC4DataInterface) -> xr.Dataset:
        """Returns data as an xarray.Dataset"""
        # Create dataframe with first file
        files = self._get_all_files()
        return xr.open_mfdataset(files)


if __name__ == "__main__":
    Base.metadata.drop_all(cache_engine)
    Base.metadata.create_all(cache_engine)
    d1 = EAC4DataInterface(
        data_variables="a",
        dates_range="2020-01-01/2020-03-01",
        time_values=["00:00"],
    )
    d1.download()
    print(EAC4CacheTable.get_rows())
    d2 = EAC4DataInterface(
        data_variables="a",
        dates_range="2020-01-01/2021-03-01",
        time_values=["00:00"],
    )
    d2.download()
    print(EAC4CacheTable.get_rows())
