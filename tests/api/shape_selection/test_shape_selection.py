# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import geopandas as gpd

from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import (
    GenericShapeSelection,
    Selection,
)


class TestSelection:
    def test_empty(self):
        sel = Selection()
        assert sel.empty()
        sel = Selection(gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3]}))
        assert not sel.empty()

    def test_selection_eq(self):
        df1 = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
        sel1 = Selection(df1, SelectionLevel.GENERIC)
        assert sel1 == Selection(df1, SelectionLevel.GENERIC)
        assert sel1 != Selection(df1, SelectionLevel.CONTINENTS)

    def test_labels(self):
        df1 = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "label": [1, 2, 3]})
        sel = Selection(df1)
        assert sorted(sel.labels) == [1, 2, 3]

    def test_get_event_label(self):
        assert Selection.get_event_label({}) is None
        event = {"last_active_drawing": {"properties": {"label": "LABEL"}}}
        assert Selection.get_event_label(event) == "LABEL"


class TestGenericShapeSelection:
    def test_init(self):
        df1 = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
        sel1 = GenericShapeSelection(df1)
        assert sel1.dataframe.equals(df1)
        assert sel1.level == SelectionLevel.GENERIC

    def test_convert_shape(self):
        df1 = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
        sel1 = Selection(df1)
        sel1_conv = GenericShapeSelection.convert_selection(sel1)
        assert isinstance(sel1_conv, GenericShapeSelection)
        assert sel1_conv.dataframe.equals(sel1.dataframe)
        sel2 = GenericShapeSelection(dataframe=df1)
        sel2_conv = GenericShapeSelection.convert_selection(sel2)
        assert sel2_conv is sel2
