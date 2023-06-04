# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import glob
import os
import tempfile

import pytest

from atmospheric_explorer.shapefile import ShapefileDownloader


def test__save_shapefile_to_zip():
    sh_down = ShapefileDownloader()
    with pytest.raises(ValueError):
        sh_down._save_shapefile_to_zip()


def test__rename_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        shp_dir = f"{tmpdir}/test_shapefile"
        os.makedirs(shp_dir)
        _, name = tempfile.mkstemp(suffix=".shp", dir=shp_dir)
        sh_down = ShapefileDownloader()
        sh_down.instance = "test"
        sh_down.data_dir = tmpdir
        sh_down._rename_file(name)
        files = glob.glob(f"{shp_dir}/*")
        filename = files[0].split(os.path.sep)[-1]
        assert len(files) == 1
        assert filename == "test_shapefile.shp"
