"""\
Module to manage shapefiles.
This module defines a class that donwloads, extracts and saves one or more shapefiles.
"""

from __future__ import annotations

import os.path
import zipfile
from textwrap import dedent

import geopandas as gpd
import requests
import requests.utils

from .loggers import get_logger
from .utils import create_folder, get_local_folder

logger = get_logger("atmexp")


class ShapefilesDownloader:
    """\
    This class manages the download, extraction and saving on disk of
    shapefiles. Shapefiles will be downloaded as zip files and then extracted into a folder.
    Shapefiles are downloaded from Natural Earth Data.
    By default, the class download a 50m resolution "admin" shapefile for all countries in the world.

    Attributes:
        shapefiles_content (bytes): downloaded shapefile
        dst_dir (str): directory where the downloaded shapefile will be saved
        resolution (str): spatial resolution. Possible values: 10m, 50m, 110m
        info_type (str): shapefile type, e.g. admin, lakes, etc. You can check possible
                         values depending on the resolution on the webpage below
        depth (int): different info_type shapefiles can have different values.
                     Use 0 for administrative shapefiles (countries)
        instance (str): the specific shapefile to be downloaded. Example: countries_ita


    See some more details here: https://www.naturalearthdata.com/downloads/
    """

    # pylint: disable=line-too-long
    _BASE_URL = (
        "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download"
    )
    _HEADERS = requests.utils.default_headers()
    _HEADERS.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",  # noqa: E501
        }
    )
    _ROOT_DIR = "shapefiles"

    def __init__(
        self: ShapefilesDownloader,
        dst_dir: str | None = None,
        resolution: str = "50m",
        map_type: str = "cultural",
        info_type: str = "admin",
        depth: int = 0,
        instance: str = "map_subunits",
        timeout: int = 10,
    ):  # pylint: disable=too-many-arguments
        self.dst_dir = (
            dst_dir
            if dst_dir is not None
            else os.path.join(get_local_folder(), self._ROOT_DIR)
        )
        self.resolution = resolution
        self.map_type = map_type
        self.info_type = info_type
        self.depth = depth
        self.instance = instance
        self.timeout = timeout
        logger.debug(
            dedent(
                """\
                Created ShapefilesDownloader object with attributes
                dst_dir: %s
                resolution: %s
                info_type: %s
                depth: %s
                instance: %s
                """
            ),
            self.dst_dir,
            self.resolution,
            self.info_type,
            self.depth,
            self.instance,
        )
        create_folder(self.dst_dir)
        logger.info("Created folder %s to save shapefiles", self.dst_dir)

    @property
    def shapefile_name(self: ShapefilesDownloader) -> str:
        """Shapefile directory"""
        if self.map_type == "physical":
            return f"ne_{self.resolution}_{self.info_type}"
        return f"ne_{self.resolution}_{self.info_type}_{self.depth}_{self.instance}"

    @property
    def shapefile_dir(self: ShapefilesDownloader) -> str:
        """Shapefile directory"""
        return os.path.join(self.dst_dir, self.shapefile_name)

    @property
    def shapefile_full_path(self: ShapefilesDownloader) -> str:
        """Shapefile directory"""
        return os.path.join(self.shapefile_dir, f"{self.shapefile_name}.shp")

    @property
    def shapefile_url(self: ShapefilesDownloader) -> str:
        """Shapefile download url"""
        # pylint: disable=line-too-long
        return f"{self._BASE_URL}/{self.resolution}/{self.map_type}/{self.shapefile_name}.zip"  # noqa: E501

    def _download_shapefile(self: ShapefilesDownloader) -> bytes:
        """Download shapefiles and returns their content in bytes"""
        logger.info("Downloading shapefiles from %s", self.shapefile_url)
        try:
            response = requests.get(
                self.shapefile_url, headers=self._HEADERS, timeout=self.timeout
            )
        except requests.exceptions.Timeout as err:
            logger.error("Shapefile download timed out.\n%s", err)
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
            logger.error(
                "Failed to download shapefile, a wrong URL has been provided.\n%s",
                response.text,
            )
            raise requests.exceptions.InvalidURL(
                "Failed to download shapefile, a wrong URL has been provided."
            )
        return response.content

    def _download_shapefile_to_zip(self: ShapefilesDownloader) -> None:
        """Save shapefiles to zip file"""
        with open(self.shapefile_dir + ".zip", "wb") as file_zip:
            file_zip.write(self._download_shapefile())
            logger.info("Shapefiles downloaded to file %s", file_zip.name)

    def _extract_to_folder(self: ShapefilesDownloader):
        """\
        Extracts shapefile zip to directory.
        The directory will have the same name of the original zip file
        """
        # Unzip file to directory
        filepath = self.shapefile_dir + ".zip"
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(self.shapefile_dir)
            logger.info("Shapefile extracted to %s", self.shapefile_dir)
        # Remove zip file
        os.remove(filepath)
        logger.info("Removed file %s", filepath)

    def download(self: ShapefilesDownloader) -> None:
        """Download and extracts shapefiles"""
        self._download_shapefile_to_zip()
        self._extract_to_folder()

    def _read_as_dataframe(self: ShapefilesDownloader) -> gpd.GeoDataFrame:
        """Return shapefile as geopandas dataframe"""
        logger.debug("Reading %s as dataframe", self.shapefile_full_path)
        return gpd.read_file(self.shapefile_full_path)

    def get_as_dataframe(self: ShapefilesDownloader) -> gpd.GeoDataFrame:
        """Return shapefile as geopandas dataframe, also downloads shapefile if needed"""
        if not os.path.exists(self.shapefile_full_path):
            logger.info("Shapefile not found, downloading it from Natural Earth Data")
            self.download()
        else:
            logger.info("Found shapefile %s, reading it", self.shapefile_full_path)
        return self._read_as_dataframe()
