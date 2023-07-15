"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

import os
from datetime import datetime

import xarray as xr

from atmospheric_explorer.cams_interface import CAMSDataInterface
from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import create_folder, get_local_folder

logger = get_logger("atmexp")


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
        time_values: str | set[str] | list[str],
        files_dir: str | None = None,
        area: list[int] | None = None,
        pressure_level: str | set[str] | list[str] | None = None,
        model_level: str | set[str] | list[str] | None = None,
    ):
        super().__init__(data_variables, file_format)
        self.dates_range = dates_range
        self.time_values = time_values
        self.area = area
        self.pressure_level = pressure_level
        self.model_level = model_level
        self.files_dirname = files_dir if files_dir is not None else f"data_{self._id}"
        self.files_dir_path = os.path.join(self._data_folder, self.files_dirname)
        create_folder(self.files_dir_path)
        logger.info("Created folder %s", self.files_dir_path)

    @property
    def file_full_path(self: EAC4Instance) -> str:
        """Name of the saved file"""
        return os.path.join(
            self.files_dir_path, f"{self.files_dirname}.{self._file_ext}"
        )

    @property
    def time_values(self: EAC4Instance) -> str | list[str]:
        """Time values are internally represented as a set, use this property to set/get its value"""
        return (
            list(self._time_values)
            if isinstance(self._time_values, set)
            else self._time_values
        )

    @time_values.setter
    def time_values(
        self: EAC4Instance, time_values: str | set[str] | list[str]
    ) -> None:
        if isinstance(time_values, list):
            time_values = set(time_values)
        self._time_values = time_values

    @property
    def pressure_level(self: EAC4Instance) -> str | list[str] | None:
        """Pressure level is internally represented as a set, use this property to set/get its value"""
        return (
            list(self._pressure_level)
            if isinstance(self._pressure_level, set)
            else self._pressure_level
        )

    @pressure_level.setter
    def pressure_level(
        self: EAC4Instance, pressure_level: str | set[str] | list[str] | None
    ) -> None:
        if isinstance(pressure_level, list):
            pressure_level = set(pressure_level)
        self._pressure_level = pressure_level

    @property
    def model_level(self: EAC4Instance) -> str | list[str] | None:
        """Model level is internally represented as a set, use this property to set/get its value"""
        return (
            list(self._model_level)
            if isinstance(self._model_level, set)
            else self._model_level
        )

    @model_level.setter
    def model_level(
        self: EAC4Instance, model_level: str | set[str] | list[str] | None
    ) -> None:
        if isinstance(model_level, list):
            model_level = set(model_level)
        self._model_level = model_level

    def _build_call_body(self: EAC4Instance) -> dict:
        """Build the CDSAPI call body"""
        call_body = super()._build_call_body()
        call_body["date"] = self.dates_range
        call_body["time"] = self.time_values
        if self.area is not None:
            call_body["area"] = self.area
        if self.pressure_level is not None:
            call_body["pressure_level"] = self.pressure_level
        if self.model_level is not None:
            call_body["model_level"] = self.model_level
        return call_body

    def download(self: EAC4Instance) -> None:
        """\
        Download the dataset and saves it to file specified in filename.
        Uses cdsapi to interact with CAMS ADS.
        """
        return super()._download(self.file_full_path)

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
        return EAC4Instance._is_subset_element(self._time_values, time_values)

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
        return EAC4Instance._is_subset_element(self._pressure_level, pressure_level)

    def _includes_model_level(
        self: EAC4Instance, model_level: str | set[str] | None
    ) -> bool:
        """Determines if the provided model levels are included in the model levels used by this object"""
        return EAC4Instance._is_subset_element(self._model_level, model_level)

    def includes(self: EAC4Instance, other: EAC4Instance) -> bool:
        # pylint: disable=protected-access
        """Determines if another object is already included in self"""
        return (
            self._includes_data_variables(other._data_variables)
            and self._includes_dates_range(other.dates_range)
            and self._includes_time_values(other._time_values)
            and self._includes_area(other.area)
            and self._includes_pressure_level(other._pressure_level)
            and self._includes_model_level(other._model_level)
        )

    def read_dataset(
        self: EAC4Instance, var_name: str | list[str] | None = None
    ) -> xr.Dataset:
        """Returns data as an xarray.Dataset"""
        if isinstance(var_name, str):
            var_name = [var_name]
        return (
            xr.open_dataset(self.file_full_path)[var_name]
            if var_name is not None
            else xr.open_dataset(self.file_full_path)
        )
