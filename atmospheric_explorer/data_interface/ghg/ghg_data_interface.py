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

from atmospheric_explorer.data_interface import CAMSDataInterface
from atmospheric_explorer.data_interface.cache import Base, cache_engine
from atmospheric_explorer.data_interface.ghg.ghg_cache import GHGCacheTable
from atmospheric_explorer.data_interface.ghg.ghg_parameters import GHGParameters
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder, get_local_folder

logger = get_logger("atmexp")


class GHGDataInterface(CAMSDataInterface):
    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    """\
    Interface for CAMS global inversion-optimised greenhouse gas fluxes and concentrations dataset.
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
    _dataset_name: str = "cams-global-greenhouse-gas-inversion"
    _data_folder: str = os.path.join(
        get_local_folder(), "data", "global_greenhouse_gas_inversion"
    )

    def __init__(
        self: GHGDataInterface,
        data_variables: str,
        file_format: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
        years: str | set[str] | list[str],
        months: str | set[str] | list[str],
        files_dir: str | None = None,
        version: str = "latest",
    ):
        super().__init__()
        self.parameters = GHGParameters(
            data_variables=data_variables,
            file_format=file_format,
            quantity=quantity,
            input_observations=input_observations,
            time_aggregation=time_aggregation,
            years=years,
            months=months,
            version=version,
        )
        self._update_parameters()
        if self._diff_parameters is not None:
            logger.info("The parameter specified are not fully cached, creating variables to manage files")
            self.file_format = self.parameters.file_format
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
    def file_full_path(self: GHGDataInterface) -> str:
        """Name of the saved file"""
        return self._file_full_path

    @file_full_path.setter
    def file_full_path(self: GHGDataInterface, filename: str) -> None:
        """Name of the saved file"""
        self._file_full_path = os.path.join(
            self.files_dir_path, f"{filename}.{self.file_ext()}"
        )

    @staticmethod
    def _get_cached_parameters(params: GHGParameters) -> GHGParameters | None:
        """Return cached parameters with the same key variables as the ones in params."""
        rows = GHGCacheTable.get_rows(params)
        logger.debug("Cached parameters: %s", rows)
        if rows:
            return GHGParameters(
                data_variables=rows[0].data_variables,
                file_format=rows[0].file_format,
                quantity=rows[0].quantity,
                input_observations=rows[0].input_observations,
                time_aggregation=rows[0].time_aggregation,
                years={r.year for r in rows},
                months={r.month for r in rows},
            )
        return None

    def file_ext(self: GHGDataInterface) -> str:
        """Extension of the saved file"""
        match (self.file_format):
            case "netcdf":
                return "nc"
            case _:
                return self.file_format

    def _update_parameters(self: GHGDataInterface) -> None:
        self._cached_parameters = self._get_cached_parameters(self.parameters)
        if self._cached_parameters is not None:
            logger.info("Some data points are already cached, updating parameters")
            self._diff_parameters = self._cached_parameters.difference(self.parameters)
        else:
            logger.info("No data points are cached, updating parameters")
            self._diff_parameters = self.parameters

    def _extracts_zip(self: GHGDataInterface) -> None:
        # This dataset downloads zipfiles with possibly multiple netcdf files inside
        # We must extract it
        zip_filename = self.file_full_path
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            ext = zip_ref.filelist[0].filename.split(".")[-1]
            self.file_format = "netcdf" if ext == "nc" else ext
            zip_ref.extractall(self.files_dir_path)
            logger.debug(
                "Extracted file %s to folder %s",
                self.file_full_path,
                self.files_dir_path,
            )
        self.file_full_path = "*"
        logger.debug("Updated file_full_path to wildcard path %s", self.file_full_path)
        # Remove zip file
        os.remove(zip_filename)
        logger.debug("Removed %s", zip_filename)

    def download(self: GHGDataInterface) -> None:
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
            self._extracts_zip()
            GHGCacheTable.cache(self._diff_parameters, self.file_full_path)
            self._update_parameters()
        else:
            logger.info("The parameters specified are already cached, skipping download.")

    def _get_all_files(self: GHGDataInterface) -> set[str]:
        files = set()
        for file in GHGCacheTable.get_files([self.parameters]):
            files.update(set(glob(file)))
        logger.debug("Fetching all files associated with parameters: %s", files)
        return files

    def _read_dataset_no_time_coord(
        self: GHGDataInterface, files: set[str]
    ) -> xr.Dataset:
        """\
        Returns data as an xarray.Dataset.

        This function reads multi-file datasets where each file corresponds to a time variable,
        but the file themselves have no time variable inside. It adds a time variable for each file
        and concat all files into a dataset.
        """
        # Create dataset from first file
        files = sorted(list(files))
        logger.debug("Reading files as xarray.Dataset: %s", files)
        date_index = datetime.strptime(files[0].split("_")[-1].split(".")[0], "%Y%m")
        data_frame = xr.open_dataset(files[0])
        data_frame = data_frame.expand_dims({"time": [date_index]})
        for file in files[1:]:
            # Merge remaining files
            # ! This loop replaces xr.open_mfdataset(surface_data.file_full_path) that does not work
            # (because time coordinate is not included in dataframe)
            date_index = datetime.strptime(file.split("_")[-1].split(".")[0], "%Y%m")
            temp = xr.open_dataset(file)
            temp = temp.expand_dims({"time": [date_index]})
            data_frame = xr.combine_by_coords(
                [data_frame, temp], combine_attrs="override"
            )
        data_frame = data_frame.expand_dims(
            {
                "input_observations": [self.parameters.input_observations],
                "time_aggregation": [self.parameters.time_aggregation],
            }
        )
        if isinstance(data_frame, xr.DataArray):
            data_frame = data_frame.to_dataset()
        return data_frame

    def read_dataset(self: GHGDataInterface) -> xr.Dataset:
        """Returns data as an xarray.Dataset"""
        # Create dataframe with first file
        files = self._get_all_files()
        try:
            logger.debug("Reading files using xarray.open_mfdataset")
            return xr.open_mfdataset(files)
        except ValueError:
            logger.debug(
                "Reading with xarray.open_mfdataset failed, switching to reading files iteratively"
            )
            return self._read_dataset_no_time_coord(files)


if __name__ == "__main__":
    Base.metadata.drop_all(cache_engine)
    Base.metadata.create_all(cache_engine)
    d1 = GHGDataInterface(
        version="latest",
        file_format="zip",
        data_variables="nitrous_oxide",
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        years=["2000", "2001"],
        months=["1", "2"],
    )
    d1._download()
    d2 = GHGDataInterface(
        version="latest",
        file_format="zip",
        data_variables="nitrous_oxide",
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        years=["2000", "2001"],
        months=["1", "2"],
    )
    d2._download()
    print(d2.read_dataset())
