"""This module collects classes to easily interact with GHG data downloaded from CAMS ADS."""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
import zipfile
from datetime import datetime
from glob import glob

import numpy as np
import xarray as xr

from atmospheric_explorer.api.config import CRS
from atmospheric_explorer.api.data_interface.cams_interface import CAMSDataInterface
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.os_manager import create_folder, remove_folder

logger = get_logger("atmexp")


class InversionOptimisedGreenhouseGas(CAMSDataInterface):
    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    """Interface for CAMS global inversion-optimised greenhouse gas fluxes and concentrations dataset.

    See https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview
    for a full list of parameters and more details about the dataset
    """

    dataset_name: str = "cams-global-greenhouse-gas-inversion"
    dataset_dir: str = os.path.join(CAMSDataInterface.data_folder, dataset_name)
    file_format = "zip"
    file_ext = "zip"

    def __init__(
        self: InversionOptimisedGreenhouseGas,
        data_variables: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
        year: str | set[str] | list[str],
        month: str | set[str] | list[str],
        files_dir: str | None = None,
        version: str = "latest",
    ):
        """Initializes InversionOptimisedGreenhouseGas instance.

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
        super().__init__(data_variables)
        self.quantity = quantity
        self.input_observations = input_observations
        self.time_aggregation = time_aggregation
        self.year = year
        self.month = month
        self.version = version
        self.files_dirname = files_dir if files_dir is not None else f"data_{self._id}"
        self.files_dir_path = os.path.join(self.dataset_dir, self.files_dirname)
        if os.path.exists(self.dataset_dir):
            remove_folder(self.dataset_dir)
        self.file_full_path = self.files_dirname
        create_folder(self.files_dir_path)
        logger.info("Created folder %s", self.files_dir_path)

    @property
    def file_full_path(self: InversionOptimisedGreenhouseGas) -> str:
        """Name of the saved file."""
        return self._file_full_path

    @file_full_path.setter
    def file_full_path(self: InversionOptimisedGreenhouseGas, filename: str) -> None:
        """Name of the saved file."""
        self._file_full_path = os.path.join(
            self.files_dir_path, f"{filename}.{self.file_ext}"
        )

    @property
    def year(self: InversionOptimisedGreenhouseGas) -> str | list[str]:
        """Year is internally represented as a set, use this property to set/get its value."""
        return list(self._year) if isinstance(self._year, set) else self._year

    @year.setter
    def year(
        self: InversionOptimisedGreenhouseGas, year: str | set[str] | list[str]
    ) -> None:
        if isinstance(year, list):
            year = set(year)
        self._year = year

    @property
    def month(self: InversionOptimisedGreenhouseGas) -> str | list[str]:
        """Month is internally represented as a set, use this property to set/get its value."""
        return list(self._month) if isinstance(self._month, set) else self._month

    @month.setter
    def month(
        self: InversionOptimisedGreenhouseGas, month: str | set[str] | list[str]
    ) -> None:
        if isinstance(month, list):
            month = set(month)
        self._month = month

    def _build_call_body(self: InversionOptimisedGreenhouseGas) -> dict:
        """Builds the CDS API call body."""
        call_body = super()._build_call_body()
        call_body.update(
            {
                "version": self.version,
                "quantity": self.quantity,
                "input_observations": self.input_observations,
                "time_aggregation": self.time_aggregation,
                "year": self.year,
                "month": self.month,
            }
        )
        return call_body

    def download(self: InversionOptimisedGreenhouseGas) -> None:
        """Downloads the dataset and saves it to file specified in filename.

        Uses cdsapi to interact with CAMS ADS.
        This function also extracts the netcdf file inside the zip file, which is then deleted.
        """
        super()._download(self.file_full_path)
        # This dataset downloads zipfiles with possibly multiple netcdf files inside
        # We must extract it
        zip_filename = self.file_full_path
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            self.file_format = "netcdf"
            self.file_ext = "nc"
            zip_ref.extractall(self.files_dir_path)
            logger.info(
                "Extracted file %s to folder %s",
                self.file_full_path,
                self.files_dir_path,
            )
        self.file_full_path = "*"
        logger.info("Updated file_full_path to wildcard path %s", self.file_full_path)
        # Remove zip file
        os.remove(zip_filename)
        logger.info("Removed %s", zip_filename)

    @staticmethod
    def _align_dims(dataset: xr.Dataset, dim: str, values: list) -> xr.Dataset:
        if dim not in dataset.dims:
            return dataset.expand_dims({dim: values})
        return dataset

    def _simplify_dataset(self: InversionOptimisedGreenhouseGas, dataset: xr.Dataset):
        if self.data_variables == "methane":
            dataset = dataset.drop(
                ["longitude_bounds", "latitude_bounds", "time_bounds"]
            )
            dataset = dataset.rename({"cell_area": "area"})
        dataset = InversionOptimisedGreenhouseGas._align_dims(
            dataset,
            "time_aggregation",
            np.array([self.time_aggregation], dtype="object"),
        )
        dataset = InversionOptimisedGreenhouseGas._align_dims(
            dataset,
            "input_observations",
            np.array([self.input_observations], dtype="object"),
        )
        return dataset.rio.write_crs(CRS)

    def read_dataset(
        self: InversionOptimisedGreenhouseGas,
    ) -> xr.Dataset:
        """Returns data as an xarray.Dataset.

        This function reads multi-file datasets where each file corresponds to a time variable,
        but the file themselves may miss the time dimension. It adds a time dimension for each file
        that's missing it and concats all files into a dataset.
        """
        logger.debug("Reading files iteratively from path %s", self.file_full_path)
        # Create dataset from first file
        files = sorted(glob(self.file_full_path))
        dataset = xr.open_dataset(files[0])
        date_index = datetime.strptime(files[0].split("_")[-1].split(".")[0], "%Y%m")
        dataset = self._align_dims(dataset, "time", [date_index])
        for file in files[1:]:
            # Merge remaining files
            # ! This loop replaces xr.open_mfdataset(surface_data.file_full_path) that does not work
            # (because time coordinate is not included in dataframe)
            temp = xr.open_dataset(file)
            date_index = datetime.strptime(file.split("_")[-1].split(".")[0], "%Y%m")
            temp = self._align_dims(temp, "time", [date_index])
            dataset = xr.combine_by_coords([dataset, temp], combine_attrs="override")
        if isinstance(dataset, xr.DataArray):
            dataset = dataset.to_dataset()
        return self._simplify_dataset(dataset)
