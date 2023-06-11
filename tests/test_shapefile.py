# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import pytest

from atmospheric_explorer.shapefile import ShapefilesDownloader


def test__init():
    sh_down = ShapefilesDownloader()
    assert sh_down.shapefiles_content is None
    assert sh_down.dst_dir == "./.data/shapefiles"
    assert sh_down.resolution == "50m"
    assert sh_down.info_type == "admin"
    assert sh_down.depth == 0
    assert sh_down.instance == "countries"
    assert sh_down.shapefiles_name == "ne_50m_admin_0_countries"
    assert sh_down.shapefiles_dir == "./.data/shapefiles/ne_50m_admin_0_countries"
    assert (
        sh_down.shapefiles_url
        == "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip"  # pylint: disable=line-too-long # noqa: E501
    )


def test__save_shapefile_to_zip():
    sh_down = ShapefilesDownloader()
    with pytest.raises(ValueError):
        sh_down._save_shapefiles_to_zip()
