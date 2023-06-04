# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import pytest

from atmospheric_explorer.shapefile import ShapefileDownloader


def test__save_shapefile_to_zip():
    # pylint: disable=protected-access
    sh_down = ShapefileDownloader()
    with pytest.raises(ValueError):
        sh_down._save_shapefile_to_zip()
