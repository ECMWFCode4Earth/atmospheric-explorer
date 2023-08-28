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
import rioxarray
import numpy as np
from atmospheric_explorer.config import crs

from atmospheric_explorer.data_interface import CAMSDataInterface
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder

logger = get_logger("atmexp")


class InversionOptimisedGreenhouseGas(CAMSDataInterface):
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
    _file_format = "zip"
    _file_ext = "zip"

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
        super().__init__(data_variables)
        self.quantity = quantity
        self.input_observations = input_observations
        self.time_aggregation = time_aggregation
        self.year = year
        self.month = month
        self.version = version
        self.files_dirname = files_dir if files_dir is not None else f"data_{self._id}"
        self.files_dir_path = os.path.join(
            self._data_folder, self._dataset_name, self.files_dirname
        )
        self.file_full_path = self.files_dirname
        create_folder(self.files_dir_path)
        logger.info("Created folder %s", self.files_dir_path)

    @property
    def file_full_path(self: InversionOptimisedGreenhouseGas) -> str:
        """Name of the saved file"""
        return self._file_full_path

    @file_full_path.setter
    def file_full_path(self: InversionOptimisedGreenhouseGas, filename: str) -> None:
        """Name of the saved file"""
        self._file_full_path = os.path.join(
            self.files_dir_path, f"{filename}.{self._file_ext}"
        )

    @property
    def year(self: InversionOptimisedGreenhouseGas) -> str | list[str]:
        """Year is internally represented as a set, use this property to set/get its value"""
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
        """Month is internally represented as a set, use this property to set/get its value"""
        return list(self._month) if isinstance(self._month, set) else self._month

    @month.setter
    def month(
        self: InversionOptimisedGreenhouseGas, month: str | set[str] | list[str]
    ) -> None:
        if isinstance(month, list):
            month = set(month)
        self._month = month

    def _build_call_body(self: InversionOptimisedGreenhouseGas) -> dict:
        """Build the CDSAPI call body"""
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
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.

        This function also extracts the netcdf file inside the zip file, which is then deleted.
        """
        super()._download(self.file_full_path)
        # This dataset downloads zipfiles with possibly multiple netcdf files inside
        # We must extract it
        zip_filename = self.file_full_path
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            self._file_format = "netcdf"
            self._file_ext = "nc"
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

    def _read_dataset_no_time_coord(
        self: InversionOptimisedGreenhouseGas,
    ) -> xr.Dataset:
        """\
        Returns data as an xarray.Dataset.

        This function reads multi-file datasets where each file corresponds to a time variable,
        but the file themselves have no time variable inside. It adds a time variable for each file
        and concat all files into a dataset.
        """
        # Create dataset from first file
        files = sorted(glob(self.file_full_path))
        date_index = datetime.strptime(files[0].split("_")[-1].split(".")[0], "%Y%m")
        data_frame = xr.open_dataset(files[0])
        data_frame = data_frame.expand_dims({"time": [date_index]})
        for file in files[1:]:
            # Merge remaining files
            # ! This loop replaces xr.open_mfdataset(surface_data.file_full_path) that does not work
            # (because time coordinate is not included in dataframe)
            date_index = datetime.strptime(file.split("_")[-1].split(".")[0], "%Y%m")
            temp = xr.open_dataset(file).expand_dims({"time": [date_index]})
            data_frame = xr.combine_by_coords(
                [data_frame, temp], combine_attrs="override"
            )
        data_frame = data_frame.expand_dims(
            {
                "input_observations": [self.input_observations],
                "time_aggregation": [self.time_aggregation],
            }
        )
        if isinstance(data_frame, xr.DataArray):
            data_frame = data_frame.to_dataset()
        return data_frame

    @staticmethod
    def _align_dims(data_frame: xr.Dataset, dim: str, values: list) -> xr.Dataset:
        if dim not in data_frame.dims:
            return data_frame.expand_dims({dim: values})
        return data_frame

    def _simplify_dataset(self: InversionOptimisedGreenhouseGas, dataset: xr.Dataset):
        if self.data_variables == "methane":
            dataset = dataset.drop(['longitude_bounds', 'latitude_bounds', 'time_bounds'])
            dataset = dataset.rename({'cell_area': 'area'})
        dataset = InversionOptimisedGreenhouseGas._align_dims(dataset, "time_aggregation", np.array([self.time_aggregation], dtype='object'))
        dataset = InversionOptimisedGreenhouseGas._align_dims(dataset, "input_observations", np.array([self.input_observations], dtype='object'))
        return dataset.rio.write_crs(crs)

    def read_dataset(self: InversionOptimisedGreenhouseGas) -> xr.Dataset:
        """Returns data as an xarray.Dataset"""
        # Dataset MUST have time dimension
        # Read first file to check dimensions
        files = sorted(glob(self.file_full_path))
        dataset = xr.open_dataset(files[0])
        if "time" in dataset.dims:
            logger.debug("Reading files using xarray.open_mfdataset")
            dataset = xr.open_mfdataset(self.file_full_path)
        else:
            logger.debug("Reading files iteratively")
            dataset = self._read_dataset_no_time_coord()
        return self._simplify_dataset(dataset)
