"""\
Config and global variables used in tests
"""
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
from __future__ import annotations

import geopandas as gpd
import pytest
import requests
import shapely
import shapely.geometry

import atmospheric_explorer.api.shape_selection.shape_selection
from atmospheric_explorer.api.config import CRS
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import (
    EntitySelection,
    GenericShapeSelection,
)
from atmospheric_explorer.api.shape_selection.shapefile import ShapefilesDownloader

TEST_GEODF = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
TEST_LEVEL = SelectionLevel.CONTINENTS
ENTITY_OUT_EVENT = {
    "last_active_drawing": {
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-163.601758, -82.968555],
                        [-163.602197, -82.927344],
                        [-163.634326, -82.902246],
                        [-163.703906, -82.879297],
                        [-163.735303, -82.856836],
                        [-163.795947, -82.842676],
                    ]
                ]
            ],
        },
        "properties": {"label": "Antarctica"},
    }
}
GENERIC_OUT_EVENT = {
    "last_active_drawing": {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [69.257813, 61.773123],
                    [110.039063, 67.609221],
                    [114.257813, 33.72434],
                    [61.875, 42.293564],
                    [69.257813, 61.773123],
                ]
            ],
        },
    }
}
CONTINENT_SELECTION = EntitySelection(
    dataframe=gpd.GeoDataFrame(
        {
            "label": ["Antartica", "Africa", "Europe"],
            "geometry": [
                shapely.geometry.MultiPolygon(
                    [shapely.box(0, 0, 2, 2), shapely.box(2, 2, 4, 4)]
                ),
                shapely.geometry.MultiPolygon(
                    [shapely.box(-1, -1, -2, -2), shapely.box(-2, -2, -3, -4)]
                ),
                shapely.geometry.MultiPolygon(
                    [shapely.box(5, 4, 10, 10), shapely.box(-10, -10, -20, -20)]
                ),
            ],
        },
        crs=CRS,
    ),
    level=SelectionLevel.CONTINENTS,
)
COUNTRIES_SELECTION = EntitySelection(
    dataframe=gpd.GeoDataFrame(
        {
            "label": ["Italy", "Germany"],
            "geometry": [
                shapely.geometry.MultiPolygon(
                    [shapely.box(5, 5, 6, 6), shapely.box(7, 7, 8, 8)]
                ),
                shapely.geometry.MultiPolygon(
                    [shapely.box(-11, -11, -13, -13), shapely.box(-14, -14, -16, -16)]
                ),
            ],
        },
        crs=CRS,
    ),
    level=SelectionLevel.COUNTRIES,
)
GENERIC_SELECTION = GenericShapeSelection(
    dataframe=gpd.GeoDataFrame(
        {
            "label": ["generic shape"],
            "geometry": [
                shapely.geometry.Polygon(
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0))
                )
            ],
        },
        crs=CRS,
    )
)
SUBUNITS_GEODATAFRAME = gpd.GeoDataFrame(
    {
        "CONTINENT": ["Europe", "Europe", "Europe", "Europe", "Europe", "Africa"],
        "ADMIN": ["Italy", "Italy", "Italy", "Italy", "Germany", "Morocco"],
        "SUBUNIT": ["Italy", "Sicily", "Sardinia", "Pantelleria", "Germany", "Morocco"],
        "geometry": [
            shapely.geometry.MultiPolygon(
                [shapely.box(5, 5, 6, 6), shapely.box(7, 7, 8, 8)]
            ),
            shapely.geometry.MultiPolygon(
                [shapely.box(5, 5, 6, 6), shapely.box(7, 7, 8, 8)]
            ),
            shapely.geometry.MultiPolygon(
                [shapely.box(5, 5, 6, 6), shapely.box(7, 7, 8, 8)]
            ),
            shapely.geometry.MultiPolygon(
                [shapely.box(5, 5, 6, 6), shapely.box(7, 7, 8, 8)]
            ),
            shapely.geometry.MultiPolygon(
                [shapely.box(-11, -11, -13, -13), shapely.box(-14, -14, -16, -16)]
            ),
            shapely.geometry.MultiPolygon(
                [shapely.box(-57, -58, -59, -60), shapely.box(9, 9, 10, 10)]
            ),
        ],
    },
    crs=CRS,
)


@pytest.fixture(autouse=True)
def clear_cache():
    ShapefilesDownloader.clear_cache()
    yield
    ShapefilesDownloader.clear_cache()


@pytest.fixture
def mock_dissolve(monkeypatch):
    def mock_dissolve_shapefile(level, *args, **kwargs):
        if level == SelectionLevel.CONTINENTS:
            return CONTINENT_SELECTION.dataframe
        return COUNTRIES_SELECTION.dataframe

    monkeypatch.setattr(
        atmospheric_explorer.api.shape_selection.shape_selection,
        "dissolve_shapefile_level",
        mock_dissolve_shapefile,
    )


@pytest.fixture
def mock_shapefile(monkeypatch):
    def mock_shp(*args, **kwargs):
        return SUBUNITS_GEODATAFRAME

    monkeypatch.setattr(
        atmospheric_explorer.api.shape_selection.shape_selection.ShapefilesDownloader,
        "get_as_dataframe",
        mock_shp,
    )


@pytest.fixture
def mock_get_timeout(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture
def mock_get_invalid_url(monkeypatch):
    def mock_get(*args, **kwargs):
        resp = requests.Response()
        resp.status_code = 400
        return resp

    monkeypatch.setattr(requests, "get", mock_get)
