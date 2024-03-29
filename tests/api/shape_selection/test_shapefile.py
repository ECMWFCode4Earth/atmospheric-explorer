# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import os

import pytest
import requests.exceptions

from atmospheric_explorer.api.os_manager import get_local_folder
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shapefile import (
    ShapefilesDownloader,
    dissolve_shapefile_level,
)


def test_cache():
    assert not ShapefilesDownloader._cache
    sh1 = ShapefilesDownloader.__new__(ShapefilesDownloader)
    sh2 = ShapefilesDownloader.__new__(ShapefilesDownloader)
    ShapefilesDownloader.cache(sh1)
    ShapefilesDownloader.cache(sh2)
    assert len(ShapefilesDownloader._cache) == 2
    assert ShapefilesDownloader._cache[0] is sh1
    assert ShapefilesDownloader._cache[1] is sh2


def test_find_cache():
    sh1 = ShapefilesDownloader(
        resolution="10m",
        map_type="cultural",
        info_type="admin",
        depth=0,
        instance="countries",
    )
    assert (
        ShapefilesDownloader.find_cache(
            resolution="10m",
            map_type="cultural",
            info_type="admin",
            depth=0,
            instance="countries",
        )
        is sh1
    )
    assert (
        ShapefilesDownloader.find_cache(
            resolution="50m",
            map_type="cultural",
            info_type="admin",
            depth=0,
            instance="countries",
        )
        is None
    )


def test_is_cached():
    sh1 = ShapefilesDownloader()
    assert ShapefilesDownloader.is_cached(sh1)
    assert not ShapefilesDownloader.is_cached(
        ShapefilesDownloader.__new__(ShapefilesDownloader, instance="countries")
    )


def test_clear_cache():
    ShapefilesDownloader()
    assert len(ShapefilesDownloader._cache) > 0
    ShapefilesDownloader.clear_cache()
    assert not ShapefilesDownloader._cache


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
