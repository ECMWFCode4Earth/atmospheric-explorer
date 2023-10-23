# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import os

import pytest
import requests.exceptions

from atmospheric_explorer.api.local_folder import get_local_folder
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shapefile import (
    ShapefileParameters,
    ShapefilesDownloader,
    dissolve_shapefile_level,
)


def test_param_init():
    sh_down = ShapefileParameters()
    assert sh_down.resolution == "50m"
    assert sh_down.map_type == "cultural"
    assert sh_down.info_type == "admin"
    assert sh_down.depth == 0
    assert sh_down.instance == "map_subunits"


def test_param_subset():
    sh_down = ShapefileParameters()
    sh_down2 = ShapefileParameters()
    assert sh_down.subset(sh_down2)
    sh_down3 = ShapefileParameters(resolution="10m")
    assert not sh_down.subset(sh_down3)


def test_init():
    sh_down = ShapefilesDownloader()
    assert sh_down.dst_dir == os.path.join(get_local_folder(), sh_down._ROOT_DIR)
    assert not sh_down._downloaded
    assert sh_down.shapefile_name == "ne_50m_admin_0_map_subunits"
    assert sh_down.shapefile_dir == os.path.join(
        get_local_folder(), sh_down._ROOT_DIR, "ne_50m_admin_0_map_subunits"
    )
    assert (
        sh_down.shapefile_url
        == "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_map_subunits.zip"  # pylint: disable=line-too-long # noqa: E501
    )


def test_obj_creation():
    sh1 = ShapefilesDownloader()
    sh2 = ShapefilesDownloader()
    assert id(sh1) == id(sh2)
    assert sh1 in ShapefilesDownloader._cache
    sh3 = ShapefilesDownloader(instance="countries")
    assert id(sh3) != id(sh1)


def test_timeout(mock_get_timeout):
    with pytest.raises(requests.exceptions.Timeout):
        sh_down = ShapefilesDownloader()
        sh_down.download()


def test_wrong_url(mock_get_invalid_url):
    with pytest.raises(requests.exceptions.InvalidURL):
        sh_down = ShapefilesDownloader(instance="cont")
        sh_down.download()


def test_dissolve_shapefile_level(mock_shapefile):
    sh_df = dissolve_shapefile_level(SelectionLevel.CONTINENTS)
    assert len(sh_df) == 2
    assert sorted(sh_df.columns) == ["geometry", "label"]
    assert sorted(sh_df["label"]) == ["Africa", "Europe"]
