# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import os

import pytest
import requests.exceptions

from atmospheric_explorer.api.os_manager import get_local_folder
from atmospheric_explorer.api.shapefile import ShapefilesDownloader


def test__init():
    sh_down = ShapefilesDownloader()
    root_dir = sh_down._ROOT_DIR
    assert sh_down.dst_dir == os.path.join(get_local_folder(), root_dir)
    assert sh_down.resolution == "50m"
    assert sh_down.info_type == "admin"
    assert sh_down.depth == 0
    assert sh_down.instance == "map_subunits"
    assert sh_down.shapefile_name == "ne_50m_admin_0_map_subunits"
    assert sh_down.shapefile_dir == os.path.join(
        get_local_folder(), root_dir, "ne_50m_admin_0_map_subunits"
    )
    assert (
        sh_down.shapefile_url
        == "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_map_subunits.zip"  # pylint: disable=line-too-long # noqa: E501
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
