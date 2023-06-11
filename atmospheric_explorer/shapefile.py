"""\
Module to manage shapefiles.
This module defines a class that donwloads, extracts and saves one or more shapefiles.
"""

from __future__ import annotations

import os.path
import zipfile
from textwrap import dedent

import requests
import requests.utils

from .loggers import _main_logger as logger
from .utils import get_local_folder


class ShapefilesDownloader:
    """\
    This class manages the download, extraction and saving on disk of
    shapefiles.
    Shapefiles will be downloaded as zip files and then extracted via
    different class methods.

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
        info_type: str = "admin",
        depth: int = 0,
        instance: str = "countries",
    ):  # pylint: disable=too-many-arguments
        self.shapefiles_content = None
        self.dst_dir = (
            dst_dir
            if dst_dir is not None
            else os.path.join(get_local_folder(), self._ROOT_DIR)
        )
        self.resolution = resolution
        self.info_type = info_type
        self.depth = depth
        self.instance = instance
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
        if not os.path.exists(self.dst_dir):
            os.makedirs(self.dst_dir)
            logger.info("Created folder %s to save shapefiles", self.dst_dir)

    @property
    def shapefiles_name(self: ShapefilesDownloader) -> str:
        """Shapefile directory"""
        return f"ne_{self.resolution}_{self.info_type}_{self.depth}_{self.instance}"

    @property
    def shapefiles_dir(self: ShapefilesDownloader) -> str:
        """Shapefile directory"""
        return os.path.join(self.dst_dir, self.shapefiles_name)

    @property
    def shapefiles_url(self: ShapefilesDownloader) -> str:
        """Shapefile download url"""
        # pylint: disable=line-too-long
        return f"{self._BASE_URL}/{self.resolution}/cultural/{self.shapefiles_name}.zip"  # noqa: E501

    def _download_shapefiles(self: ShapefilesDownloader) -> None:
        """Download shapefile as a zip"""
        logger.info("Downloading shapefiles from %s", self.shapefiles_url)
        self.shapefiles_content = requests.get(
            self.shapefiles_url, headers=self._HEADERS, timeout=30
        ).content

    def _save_shapefiles_to_zip(self: ShapefilesDownloader) -> None:
        """Save shapefile to zip file"""
        if self.shapefiles_content is None:
            logger.error("No content in shapefile")
            raise ValueError("No content in shapefile")
        with open(self.shapefiles_dir + ".zip", "wb") as file_zip:
            file_zip.write(self.shapefiles_content)
            logger.info("Shapefiles downloaded to file %s", file_zip.name)

    def _extract_to_folder(self: ShapefilesDownloader):
        """\
        Extracts shapefile zip to directory.
        The directory will have the same name of the original zip file"""
        # Unzip file to directory
        filepath = self.shapefiles_dir + ".zip"
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(self.shapefiles_dir)
            logger.info("Shapefile extracted to %s", self.shapefiles_dir)
        # Remove zip file
        os.remove(filepath)
        logger.info("Removed file %s", filepath)

    def _clear_shapefiles_content(self: ShapefilesDownloader) -> None:
        """Clear content"""
        self.shapefiles_content = None

    def download_shapefile(self: ShapefilesDownloader) -> None:
        """Download and extracts shapefiles"""
        self._download_shapefiles()
        self._save_shapefiles_to_zip()
        self._extract_to_folder()
        self._clear_shapefiles_content()
