# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import os

import pytest
import requests.exceptions

from atmospheric_explorer.shapefile import ShapefilesDownloader
from atmospheric_explorer.utils import get_local_folder


def test__init():
    sh_down = ShapefilesDownloader()
    root_dir = sh_down._ROOT_DIR
    assert sh_down.dst_dir == os.path.join(get_local_folder(), root_dir)
    assert sh_down.resolution == "10m"
    assert sh_down.info_type == "admin"
    assert sh_down.depth == 0
    assert sh_down.instance == "countries"
    assert sh_down.shapefile_name == "ne_10m_admin_0_countries"
    assert sh_down.shapefile_dir == os.path.join(
        get_local_folder(), root_dir, "ne_10m_admin_0_countries"
    )
    assert (
        sh_down.shapefile_url
        == "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip"  # pylint: disable=line-too-long # noqa: E501
    )


def test_timeout(mock_get_timeout):
    sh_down = ShapefilesDownloader()
    with pytest.raises(requests.exceptions.Timeout):
        sh_down.download()


def test_wrong_url():
    sh_down = ShapefilesDownloader()
    sh_down.instance = "cont"
    with pytest.raises(requests.exceptions.InvalidURL):
        sh_down.download()
