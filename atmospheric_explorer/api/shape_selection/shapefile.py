"""Module to manage shapefiles.

This module defines a class that donwloads, extracts and saves one or more shapefiles.
"""

from __future__ import annotations

import os.path
import zipfile
from textwrap import dedent

import geopandas as gpd
import requests
import requests.utils

from atmospheric_explorer.api.cache import Cached, Parameters
from atmospheric_explorer.api.local_folder import get_local_folder
from atmospheric_explorer.api.loggers import atm_exp_logger
from atmospheric_explorer.api.os_utils import create_folder
from atmospheric_explorer.api.shape_selection.config import map_level_shapefile_mapping


class ShapefileParameters(Parameters):
    # pylint: disable = too-few-public-methods
    """Parameters for the Natural Earth Data shapefile."""

    def __init__(
        self: ShapefileParameters,
        resolution: str = "50m",
        map_type: str = "cultural",
        info_type: str = "admin",
        depth: int = 0,
        instance: str = "map_subunits",
    ):  # pylint: disable=too-many-arguments
        self.resolution = resolution
        self.map_type = map_type
        self.info_type = info_type
        self.depth = depth
        self.instance = instance

    def subset(self: ShapefileParameters, other: ShapefileParameters) -> bool:
        res = (
            self.resolution == other.resolution
            and self.map_type == other.map_type
            and self.info_type == other.info_type
            and self.depth == other.depth
            and self.instance == other.instance
        )
        atm_exp_logger.debug("Subset result: %s\nself: %s\nother: %s", res, self, other)
        return res


class ShapefilesDownloader(Cached):
    # pylint: disable=too-many-instance-attributes
    """This class manages the download, extraction and saving on disk of shapefiles.

    Shapefiles are downloaded from Natural Earth Data as zip files and then extracted into a folder.
    By default, the class download a 50m resolution "admin" shapefile for all countries in the world.

    Shapefiles will be downloaded as zip files and then extracted into a
    folder. Shapefiles are downloaded from Natural Earth Data.
    By default, the class download a 50m resolution "admin" shapefile for all
    countries in the world.
    """

    # pylint: disable=line-too-long
    # pylint: disable=too-many-instance-attributes
    _BASE_URL: str = (
        "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download"
    )
    _HEADERS = requests.utils.default_headers()
    _HEADERS.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
        }
    )
    _ROOT_DIR: str = "shapefiles"

    def __new__(
        cls: Cached,
        resolution: str = "50m",
        map_type: str = "cultural",
        info_type: str = "admin",
        depth: int = 0,
        instance: str = "map_subunits",
        timeout: int = 10,
        dst_dir: str | None = None,
    ):  # pylint: disable=too-many-arguments
        params = ShapefileParameters(
            resolution=resolution,
            map_type=map_type,
            info_type=info_type,
            depth=depth,
            instance=instance,
        )
        return Cached.__new__(ShapefilesDownloader, params)

    @Cached.init_cache
    def __init__(
        self: ShapefilesDownloader,
        resolution: str = "50m",
        map_type: str = "cultural",
        info_type: str = "admin",
        depth: int = 0,
        instance: str = "map_subunits",
        timeout: int = 10,
        dst_dir: str | None = None,
    ):  # pylint: disable=too-many-arguments
        """Initializes ShapefilesDownloader instance.

        Attributes:
            resolution (str): spatial resolution. Possible values: 10m, 50m, 110m
            map_type (str): map type, e.g. cultural, physical or raster
            info_type (str): shapefile type, e.g. admin, lakes, etc. You can check possible
                            values depending on the resolution on the webpage below
            depth (int): different info_type shapefiles can have different values.
                        Use 0 for administrative shapefiles (countries)
            instance (str): the specific shapefile to be downloaded. Example: countries_ita
            timeout (int): timeout fot the GET call to Natural Earth Data
            dst_dir (str): destination diractory for the donwloaded shapefile

        See some more details here: https://www.naturalearthdata.com/downloads/
        """
        self.parameters = ShapefileParameters(
            resolution=resolution,
            map_type=map_type,
            info_type=info_type,
            depth=depth,
            instance=instance,
        )
        self.timeout = timeout
        self.dst_dir = (
            dst_dir
            if dst_dir is not None
            else os.path.join(get_local_folder(), self._ROOT_DIR)
        )
        self._downloaded = False
        create_folder(self.dst_dir)
        atm_exp_logger.info("Created folder %s to save shapefiles", self.dst_dir)
        atm_exp_logger.debug(
            dedent(
                """\
                Created ShapefilesDownloader object with attributes
                resolution: %s
                map_type: %s
                info_type: %s
                depth: %s
                instance: %s
                timeout: %s
                dst_dir: %s
                """
            ),
            resolution,
            map_type,
            info_type,
            depth,
            instance,
            self.timeout,
            self.dst_dir,
        )

    @property
    def shapefile_name(self: ShapefilesDownloader) -> str:
        """Shapefile name"""
        if self.parameters.map_type == "physical":
            return f"ne_{self.parameters.resolution}_{self.parameters.info_type}"
        return f"ne_{self.parameters.resolution}_{self.parameters.info_type}_{self.parameters.depth}_{self.parameters.instance}"  # noqa: E501

    @property
    def shapefile_dir(self: ShapefilesDownloader) -> str:
        """Shapefile directory."""
        return os.path.join(self.dst_dir, self.shapefile_name)

    @property
    def shapefile_full_path(self: ShapefilesDownloader) -> str:
        """Shapefile full path."""
        return os.path.join(self.shapefile_dir, f"{self.shapefile_name}.shp")

    @property
    def shapefile_url(self: ShapefilesDownloader) -> str:
        """Shapefile download url."""
        # pylint: disable=line-too-long
        return f"{self._BASE_URL}/{self.parameters.resolution}/{self.parameters.map_type}/{self.shapefile_name}.zip"

    def _download_shapefile(self: ShapefilesDownloader) -> bytes:
        """Download shapefiles and returns their content in bytes."""
        atm_exp_logger.info("Downloading shapefiles from %s", self.shapefile_url)
        try:
            response = requests.get(
                self.shapefile_url, headers=self._HEADERS, timeout=self.timeout
            )
        except requests.exceptions.Timeout as err:
            atm_exp_logger.error("Shapefile download timed out.\n%s", err)
            raise requests.exceptions.Timeout(
                dedent(
                    f"""\
                    Shapefile download timed out.
                    Please check the shapefile URL or
                    increase the timeout parameter (current value {self.timeout}s)
                    """
                )
            )

        if response.status_code != 200:
            atm_exp_logger.error(
                "Failed to download shapefile, a wrong URL has been provided.\n%s",
                response.text,
            )
            raise requests.exceptions.InvalidURL(
                "Failed to download shapefile, a wrong URL has been provided."
            )
        return response.content

    def _download_shapefile_to_zip(self: ShapefilesDownloader) -> None:
        """Saves shapefiles to zip file."""
        with open(self.shapefile_dir + ".zip", "wb") as file_zip:
            file_zip.write(self._download_shapefile())
            atm_exp_logger.info("Shapefiles saved into file %s", file_zip.name)

    def _extract_to_folder(self: ShapefilesDownloader):
        """Extracts shapefile zip to directory.

        The directory will have the same name of the original zip file.
        """
        # Unzip file to directory
        filepath = self.shapefile_dir + ".zip"
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(self.shapefile_dir)
            atm_exp_logger.info("Shapefile extracted to %s", self.shapefile_dir)
        # Remove zip file
        os.remove(filepath)
        atm_exp_logger.info("Removed file %s", filepath)

    def download(self: ShapefilesDownloader) -> None:
        """Downloads and extracts shapefiles."""
        self._download_shapefile_to_zip()
        self._extract_to_folder()
        self._downloaded = True

    def _read_as_dataframe(self: ShapefilesDownloader) -> gpd.GeoDataFrame:
        """Returns shapefile as geopandas dataframe."""
        atm_exp_logger.debug("Reading %s as dataframe", self.shapefile_full_path)
        return gpd.read_file(self.shapefile_full_path)

    def get_as_dataframe(self: ShapefilesDownloader) -> gpd.GeoDataFrame:
        """Returns shapefile as geopandas dataframe, also downloads shapefile if needed."""
        if not self._downloaded:
            atm_exp_logger.info(
                "Shapefile not downloaded, downloading it from Natural Earth Data"
            )
            self.download()
        else:
            atm_exp_logger.info(
                "Shapefile already downloaded in %s", self.shapefile_full_path
            )
        return self._read_as_dataframe()


def dissolve_shapefile_level(level: str) -> gpd.GeoDataFrame:
    """Gets shapefile and dissolves it on a selection level"""
    atm_exp_logger.debug("Dissolve shapefile to level %s", level)
    col = map_level_shapefile_mapping[level]
    sh_df = ShapefilesDownloader(instance="map_subunits").get_as_dataframe()
    sh_df = sh_df[[col, "geometry"]].rename({col: "label"}, axis=1)
    return sh_df.dissolve(by="label").reset_index()
