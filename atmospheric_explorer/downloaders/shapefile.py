from __future__ import annotations
import requests
import sys
import os.path
import zipfile
import glob
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


class ShapefileDownloader:
    _BASE_URL = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download"
    _HEADERS = requests.utils.default_headers()
    _HEADERS.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })

    def __init__(self:ShapefileDownloader):
        self.shapefile_content = None
        self.resolution = None
        self.info_type = None
        self.depth = None
        self.instance = None
        self.data_dir = os.path.dirname(sys.argv[0])

    @property
    def shapefile_dir(self:ShapefileDownloader) -> str:
        return f"{self.data_dir}/{self.instance}_shapefile"

    @property
    def shapefile_url(self:ShapefileDownloader) -> str:
        return f"{self._BASE_URL}/{self.resolution}/cultural/ne_{self.resolution}_{self.info_type}_{self.depth}_{self.instance}.zip"

    def _download_shapefile(self:ShapefileDownloader) -> None:
        logger.info(f"Downloading shapefile from {self.shapefile_url}")
        self.shapefile_content = requests.get(self.shapefile_url, headers=self._HEADERS).content
    
    def _save_shapefile_to_zip(self:ShapefileDownloader) -> None:
        if self.shapefile_content is None:
            logger.error("No content in shapefile")
            raise Exception("No content in shapefile")
        with open(self.shapefile_dir + ".zip", "wb") as f:
            f.write(self.shapefile_content)
            logger.info(f"Shapefile downloaded to file {f.name}")

    def _extract_to_folder(self:ShapefileDownloader):
        # Unzip file to directory
        filepath = self.shapefile_dir + ".zip"
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(self.shapefile_dir)
            logger.info(f"Shapefile extracted to {self.shapefile_dir}")
        # Remove zip file
        os.remove(filepath)
        logger.info(f"Removed file {filepath}")
    
    def _rename_all_shapefiles(self:ShapefileDownloader):
        # Rename all files inside zip
        for file in glob.glob(f"{self.shapefile_dir}/*"):
            ext = file.split('.')[-1]
            os.rename(file, f'{self.shapefile_dir}/{self.instance}_shapefile.{ext}')
            logger.info("Renamed all shapefiles")
    
    def _clear_shapefile_content(self:ShapefileDownloader) -> None:
        self.shapefile_content = None

    def download_shapefile(self:ShapefileDownloader, resolution:str, info_type:str, depth:int, instance:str) -> None:
        self.resolution = resolution
        self.info_type = info_type
        self.depth = depth
        self.instance = instance
        self._download_shapefile()
        self._save_shapefile_to_zip()
        self._extract_to_folder()
        self._rename_all_shapefiles()
        self._clear_shapefile_content()
