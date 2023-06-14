"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
import zipfile
from abc import ABC, abstractmethod
from datetime import datetime
from glob import glob
from itertools import count
from typing import Any

import cdsapi

from atmospheric_explorer.utils import get_local_folder


class CAMSDataInterface(ABC):
    # pylint: disable=too-many-instance-attributes
    """\
    Generic interface common to all CAMS datasets.

    Attributes:
        data_variables (str | list[str]): data varaibles to be downloaded from CAMS, depend on the dataset
        file_format (str): format for the downloaded data, e.g. 'netcdf', 'grib', 'zip' etc.
        filename (str | None): file where to save the data. If not provided will be built using file_format and
            with a dinamically generated name
    """

    _dataset_name: str | None = None
    _data_folder: str = os.path.join(get_local_folder(), "data")
    _instances: list[CAMSDataInterface] = []
    _ids: count = count(len(glob(os.path.join(_data_folder, "*"))))

    def __init__(
        self: CAMSDataInterface,
        data_variables: str | set[str] | list[str],
        file_format: str,
        filename: str | None = None,
    ):
        self._id = next(self._ids)
        self._instances.append(self)
        if isinstance(data_variables, list):
            data_variables = set(data_variables)
        self.data_variables = data_variables
        self.file_format = file_format
        self._filename = filename
        self._create_folder()

    @property
    def _file_ext(self: CAMSDataInterface):
        """Extension of the saved file"""
        match (self.file_format):
            case "netcdf":
                return "nc"
            case _:
                return self.file_format

    @property
    def _file_fullpath(self: CAMSDataInterface):
        """Full path of the saved file"""
        return os.path.join(self._data_folder, self.filename)

    @property
    def filename(self: CAMSDataInterface):
        """Name of the saved file"""
        return (
            self._filename
            if self._filename is not None
            else f"data_{self._id}.{self._file_ext}"
        )

    @classmethod
    def _create_folder(cls):
        """Create data folder if it doensn't exists"""
        if not os.path.exists(cls._data_folder):
            os.makedirs(cls._data_folder)

    def _build_call_body(self: CAMSDataInterface) -> dict:
        """Build the CDSAPI call body"""
        call_body = {"format": self.file_format, "variable": list(self.data_variables)}
        return call_body

    def _download(self: CAMSDataInterface) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        client = cdsapi.Client()
        client.retrieve(
            self._dataset_name, self._build_call_body(), self._file_fullpath
        )

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
    ):
        """Determines if the object data variables include the input data variables"""
        return CAMSDataInterface._is_subset_element(self.data_variables, data_variables)

    @abstractmethod
    def includes(self: CAMSDataInterface, other: CAMSDataInterface):
        """Determines if another object is already included in self"""
        raise NotImplementedError("Method not implemented")


class EAC4Instance(CAMSDataInterface):
    # TODO: add multilevel variable parameters  # pylint: disable=fixme
    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    """\
    Interface for CAMS global reanalysis (EAC4) and
    CAMS global reanalysis (EAC4) monthly averaged fields datasets.
    See https://confluence.ecmwf.int/display/CKB/CAMS%3A+Reanalysis+data+documentation#heading-CAMSglobalreanalysisEAC4Parameterlistings
    for a full list of parameters and more details about the dataset

    Attributes:
        data_variables (str | list[str]): data varaibles to be downloaded from CAMS,
            see https://confluence.ecmwf.int/display/CKB/CAMS%3A+Reanalysis+data+documentation#heading-CAMSglobalreanalysisEAC4Parameterlistings
        file_format (str): format for the downloaded data, can be either 'netcdf' or 'grib'
        dates_range (str): range of dates to consider, provided as a 'start/end' string with dates in ISO format
        time_values (str | list[str]): time in 'HH:MM' format. One value or a list of values can be provided.
            Accepted values are [00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00]
        filename (str | None): file where to save the data. If not provided will be built using file_format and
            with a dinamically generated name
        area (list[int]): latitude-longitude area box to be considered, provided as a list of four values
            [NORTH, WEST, SOUTH, EAST]. If not provided, full area will be considered
        pressure_level (str | list[str] | None): pressure levels to be considered for multilevel variables.
            Can be a single level or a list of levels, see documentation linked above for all possible values.
        model_level (str | list[str] | None): model levels to be considered for multilevel variables.
            Can be a single level or a list of levels, chosen in a range from 1 to 60.
            See documentation linked above for all possible values.
    """
    _dataset_name: str = "cams-global-reanalysis-eac4"
    _data_folder: str = os.path.join(get_local_folder(), "data", "eac4")

    def __init__(
        self,
        data_variables: str | set[str] | list[str],
        file_format: str,
        dates_range: str,
        time_values: str | set[str],
        filename: str | None = None,
        area: list[int] | None = None,
        pressure_level: str | set[str] | None = None,
        model_level: str | set[str] | None = None,
    ):
        super().__init__(data_variables, file_format, filename)
        self.dates_range = dates_range
        self.time_values = time_values
        self.area = area
        self.pressure_level = pressure_level
        self.model_level = model_level

    def _build_call_body(self: EAC4Instance) -> dict:
        """Build the CDSAPI call body"""
        call_body = super()._build_call_body()
        call_body["date"] = self.dates_range
        call_body["time"] = (
            list(self.time_values)
            if isinstance(self.time_values, set)
            else self.time_values
        )
        if self.area is not None:
            call_body["area"] = self.area
        if self.pressure_level is not None:
            call_body["pressure_level"] = (
                list(self.pressure_level)
                if isinstance(self.pressure_level, set)
                else self.pressure_level
            )
        if self.model_level is not None:
            call_body["model_level"] = (
                list(self.model_level)
                if isinstance(self.model_level, set)
                else self.model_level
            )
        return call_body

    def download(self: EAC4Instance) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        return super()._download()

    def _includes_dates_range(self: EAC4Instance, dates_range_input: str) -> bool:
        """Determines if the provided dates range is included in the dates range used by this object"""
        start_date, end_date = map(
            lambda d: datetime.strptime(d, "%Y-%m-%d"), self.dates_range.split("/")
        )
        start_date_input, end_date_input = map(
            lambda d: datetime.strptime(d, "%Y-%m-%d"), dates_range_input.split("/")
        )
        return (start_date <= start_date_input) and (end_date >= end_date_input)

    def _includes_time_values(self: EAC4Instance, time_values: str | set[str]) -> bool:
        """Determines if the provided time values are included in the time values used by this object"""
        return EAC4Instance._is_subset_element(self.time_values, time_values)

    def _includes_area(self: EAC4Instance, area: list[int] | None) -> bool:
        """Determines if the provided area is included in the area used by this object"""
        if self.area is not None:
            if area is not None:
                for direction, value in enumerate(self.area):
                    if abs(area[direction]) > abs(value):
                        return False
                return True
            return False
        return True

    def _includes_pressure_level(
        self: EAC4Instance, pressure_level: str | set[str] | None
    ) -> bool:
        """Determines if the provided pressure levels are included in the pressure levels used by this object"""
        return EAC4Instance._is_subset_element(self.pressure_level, pressure_level)

    def _includes_model_level(
        self: EAC4Instance, model_level: str | set[str] | None
    ) -> bool:
        """Determines if the provided model levels are included in the model levels used by this object"""
        return EAC4Instance._is_subset_element(self.model_level, model_level)

    def includes(self: EAC4Instance, other: EAC4Instance) -> bool:
        """Determines if another object is already included in self"""
        return (
            self._includes_data_variables(other.data_variables)
            and self._includes_dates_range(other.dates_range)
            and self._includes_time_values(other.time_values)
            and self._includes_area(other.area)
            and self._includes_pressure_level(other.pressure_level)
            and self._includes_model_level(other.model_level)
        )


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
    _data_folder: str = os.path.join(
        get_local_folder(), "data", "global_greenhouse_gas_inversion"
    )

    def __init__(
        self: InversionOptimisedGreenhouseGas,
        data_variables: str | set[str] | list[str],
        file_format: str,
        quantity: str,
        input_observations: str,
        time_aggregation: str,
        year: str | set[str],
        month: str | set[str],
        filename: str | None = None,
        version: str = "latest",
    ):
        super().__init__(data_variables, file_format, filename)
        self.quantity = quantity
        self.input_observations = input_observations
        self.time_aggregation = time_aggregation
        self.year = year
        self.month = month
        self.version = version

    def _build_call_body(self: InversionOptimisedGreenhouseGas) -> dict:
        """Build the CDSAPI call body"""
        call_body = super()._build_call_body()
        call_body["version"] = self.version
        call_body["quantity"] = self.quantity
        call_body["input_observations"] = self.input_observations
        call_body["time_aggregation"] = self.time_aggregation
        call_body["year"] = self.year
        call_body["month"] = self.month
        return call_body

    def download(self: InversionOptimisedGreenhouseGas) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.

        This function also extracts the netcdf file inside the zip file, which is then deleted.
        """
        super()._download()
        # This dataset downloads zipfiles with just 1 netcdf file inside
        # We must extract it
        zip_filename = self._file_fullpath
        with zipfile.ZipFile(self._file_fullpath, "r") as zip_ref:
            self._filename = zip_ref.filelist[0].filename
            ext = self._filename.split(".")[-1]
            self.file_format = "netcdf" if ext == "nc" else ext
            zip_ref.extractall(self._data_folder)
        # Remove zip file
        os.remove(zip_filename)
        # Change file format to consider extracted netcdf file
        self.file_format = "netcdf"

    def _includes_year(
        self: InversionOptimisedGreenhouseGas, year: str | set[str]
    ) -> bool:
        """Determines if the provided year(s) are included in the year(s) used by this object"""
        return InversionOptimisedGreenhouseGas._is_subset_element(self.year, year)

    def _includes_month(
        self: InversionOptimisedGreenhouseGas, month: str | set[str]
    ) -> bool:
        """Determines if the provided month(s) are included in the month(s) used by this object"""
        return InversionOptimisedGreenhouseGas._is_subset_element(self.month, month)

    def includes(
        self: InversionOptimisedGreenhouseGas, other: InversionOptimisedGreenhouseGas
    ) -> bool:
        """Determines if another object is already included in self"""
        return (
            self._includes_data_variables(other.data_variables)
            and (self.quantity == other.quantity)
            and (self.input_observations == other.input_observations)
            and (self.time_aggregation == other.time_aggregation)
            and self._includes_year(other.year)
            and self._includes_month(other.month)
            and (self.version == other.version)
        )
