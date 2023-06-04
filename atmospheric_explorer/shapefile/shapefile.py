"""\
Module to manage shapefiles.
This module defines a class that donwloads, extracts and saves one or more shapefiles.
"""

from __future__ import annotations

import glob
import logging
import logging.config
import os.path
import sys
import zipfile

import requests

from ..config import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("mainlogger")


class ShapefileDownloader:
    """This class manages the download, extraction and saving on disk of shapefiles."""

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

    def __init__(self: ShapefileDownloader):
        self.shapefile_content = None
        self.resolution = None
        self.info_type = None
        self.depth = None
        self.instance = None
        self.data_dir = os.path.dirname(sys.argv[0])

    @property
    def shapefile_dir(self: ShapefileDownloader) -> str:
        """Shapefile directory"""
        return f"{self.data_dir}/{self.instance}_shapefile"

    @property
    def shapefile_url(self: ShapefileDownloader) -> str:
        """Shapefile download url"""
        # pylint: disable=line-too-long
        return f"{self._BASE_URL}/{self.resolution}/cultural/ne_{self.resolution}_{self.info_type}_{self.depth}_{self.instance}.zip"  # noqa: E501

    def _download_shapefile(self: ShapefileDownloader) -> None:
        """Download shapefile"""
        logger.info("Downloading shapefile from %s", self.shapefile_url)
        self.shapefile_content = requests.get(
            self.shapefile_url, headers=self._HEADERS, timeout=30
        ).content

    def _save_shapefile_to_zip(self: ShapefileDownloader) -> None:
        """Save shapefile to zip file"""
        if self.shapefile_content is None:
            logger.error("No content in shapefile")
            raise ValueError("No content in shapefile")
        with open(self.shapefile_dir + ".zip", "wb") as file_zip:
            file_zip.write(self.shapefile_content)
            logger.info("Shapefile downloaded to file %s", file_zip.name)

    def _extract_to_folder(self: ShapefileDownloader):
        """Extracts shapefile zip to directory"""
        # Unzip file to directory
        filepath = self.shapefile_dir + ".zip"
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(self.shapefile_dir)
            logger.info("Shapefile extracted to %s", self.shapefile_dir)
        # Remove zip file
        os.remove(filepath)
        logger.info("Removed file %s", filepath)

    def _rename_all_shapefiles(self: ShapefileDownloader):
        """Rename all files"""
        # Rename all files inside zip
        for file in glob.glob(f"{self.shapefile_dir}/*"):
            ext = file.split(".")[-1]
            os.rename(file, f"{self.shapefile_dir}/{self.instance}_shapefile.{ext}")
            logger.debug(
                "Renamed %s to %s/%s_shapefile.%s",
                file,
                self.shapefile_dir,
                self.instance,
                ext,
            )

    def _clear_shapefile_content(self: ShapefileDownloader) -> None:
        """Clear content"""
        self.shapefile_content = None

    def download_shapefile(
        self: ShapefileDownloader,
        resolution: str,
        info_type: str,
        depth: int,
        instance: str,
    ) -> None:
        """Main function"""
        self.resolution = resolution
        self.info_type = info_type
        self.depth = depth
        self.instance = instance
        self._download_shapefile()
        self._save_shapefile_to_zip()
        self._extract_to_folder()
        self._rename_all_shapefiles()
        self._clear_shapefile_content()
