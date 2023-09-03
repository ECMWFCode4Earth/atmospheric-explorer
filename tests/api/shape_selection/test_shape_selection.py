# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
# pylint: disable=unused-argument
import geopandas as gpd
import pytest
import shapely
import shapely.geometry
from conftest import (
    CONTINENT_SELECTION,
    COUNTRIES_SELECTION,
    ENTITY_OUT_EVENT,
    GENERIC_OUT_EVENT,
    GENERIC_SELECTION,
    TEST_GEODF,
    TEST_LEVEL,
)

from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.shape_selection.shape_selection import (
    EntitySelection,
    GenericShapeSelection,
    Selection,
    from_out_event,
)


class TestSelection:
    def test_empty(self):
        sel = Selection()
        assert sel.empty()
        sel = Selection(TEST_GEODF)
        assert not sel.empty()

    def test_eq(self):
        sel1 = Selection(TEST_GEODF, SelectionLevel.GENERIC)
        assert sel1 == Selection(TEST_GEODF, SelectionLevel.GENERIC)
        assert sel1 != Selection(TEST_GEODF, SelectionLevel.CONTINENTS)

    def test_labels(self):
        df1 = gpd.GeoDataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "label": [1, 2, 3]})
        sel = Selection(df1)
        assert sorted(sel.labels) == [1, 2, 3]

    def test_labels_empty(self):
        sel = Selection()
        assert not sel.labels

    def test_get_event_label(self):
        assert Selection.get_event_label({}) is None
        event = {"last_active_drawing": {"properties": {"label": "LABEL"}}}
        assert Selection.get_event_label(event) == "LABEL"


class TestGenericShapeSelection:
    def test_init_empty(self):
        sel = GenericShapeSelection()
        assert sel.dataframe is None
        assert sel.level is None

    def test_init_notempty(self):
        sel1 = GenericShapeSelection(TEST_GEODF)
        assert sel1.dataframe.equals(TEST_GEODF)
        assert sel1.level == SelectionLevel.GENERIC

    def test_convert_shape(self):
        sel = Selection(TEST_GEODF)
        sel_conv = GenericShapeSelection.convert_selection(sel)
        assert isinstance(sel_conv, GenericShapeSelection)
        assert sel_conv.dataframe.equals(TEST_GEODF)

    def test_convert_generic(self):
        sel2 = GenericShapeSelection(dataframe=TEST_GEODF)
        sel2_conv = GenericShapeSelection.convert_selection(sel2)
        assert sel2_conv is sel2

    def test_convert_entity(self):
        sel_entity = CONTINENT_SELECTION
        sel_conv = GenericShapeSelection.convert_selection(sel_entity)
        assert isinstance(sel_conv, GenericShapeSelection)
        assert sel_conv.dataframe.equals(sel_entity.dataframe)
        assert sel_conv.level == SelectionLevel.GENERIC


class TestEntitySelection:
    def test_init(self):
        sel1 = EntitySelection(dataframe=TEST_GEODF, level=SelectionLevel.CONTINENTS)
        assert sel1.dataframe.equals(TEST_GEODF)
        assert sel1.level == SelectionLevel.CONTINENTS

    def test_init_nolevel(self):
        with pytest.raises(ValueError):
            EntitySelection(dataframe=TEST_GEODF, level=SelectionLevel.GENERIC)

    def test_from_generic_selection_empty(self):
        gen = GenericShapeSelection()
        ent_sel = EntitySelection.from_generic_selection(gen, TEST_LEVEL)
        assert ent_sel.empty()

    def test_from_generic_selection(self, mock_dissolve):
        gen_shape = GENERIC_SELECTION
        ent_sel = EntitySelection.from_generic_selection(
            gen_shape, SelectionLevel.CONTINENTS
        )
        assert isinstance(ent_sel, EntitySelection)
        assert len(ent_sel.dataframe) == 1
        assert sorted(ent_sel.labels) == ["Antartica"]

    def test_from_generic_selection_error(self):
        with pytest.raises(ValueError):
            ent_shape = CONTINENT_SELECTION
            EntitySelection.from_generic_selection(ent_shape, SelectionLevel.CONTINENTS)

    def test_from_entities_list_empty(self):
        sel = EntitySelection.from_entities_list([], level=SelectionLevel.CONTINENTS)
        assert sel.empty()

    def test_from_entities_list(self, mock_dissolve):
        continents = ["Africa", "Europe"]
        sel = EntitySelection.from_entities_list(
            continents, level=SelectionLevel.CONTINENTS
        )
        assert sorted(sel.dataframe.columns) == ["geometry", "label"]
        assert all(
            list(
                isinstance(c, shapely.geometry.MultiPolygon)
                for c in sel.dataframe["geometry"]
            )
        )
        assert sorted(sel.labels) == continents

    def test_from_entity_selection_empty(self):
        ent_sel1 = EntitySelection()
        ent_sel2 = EntitySelection.from_entity_selection(ent_sel1, TEST_LEVEL)
        assert ent_sel2.empty()

    def test_from_entity_selection_samelevel(self):
        ent_sel1 = CONTINENT_SELECTION
        ent_sel1.level = SelectionLevel.COUNTRIES
        ent_sel2 = EntitySelection.from_entity_selection(
            ent_sel1, level=SelectionLevel.COUNTRIES
        )
        assert ent_sel2.dataframe.equals(ent_sel1.dataframe)
        assert ent_sel2.level == SelectionLevel.COUNTRIES

    def test_from_entity_selection_samecol(self):
        ent_sel1 = COUNTRIES_SELECTION
        ent_sel1.level = SelectionLevel.COUNTRIES_SUB
        ent_sel2 = EntitySelection.from_entity_selection(
            ent_sel1, level=SelectionLevel.ORGANIZATIONS
        )
        assert ent_sel2.dataframe.equals(ent_sel1.dataframe)
        assert ent_sel2.level == SelectionLevel.ORGANIZATIONS

    def test_from_entity_selection(self, mocker, mock_shapefile):
        mocked_fel = mocker.patch(
            "atmospheric_explorer.api.shape_selection.shape_selection.EntitySelection.from_entities_list"
        )
        ent_sel = COUNTRIES_SELECTION
        EntitySelection.from_entity_selection(ent_sel, level=SelectionLevel.CONTINENTS)
        mocked_fel.assert_called_once_with(["Europe"], SelectionLevel.CONTINENTS)

    def test_from_entity_selection_error(self):
        with pytest.raises(ValueError):
            EntitySelection.from_entity_selection(
                GenericShapeSelection(TEST_GEODF), TEST_LEVEL
            )

    def test_convert_selection_generic(self, mocker):
        mocked_fgs = mocker.patch(
            "atmospheric_explorer.api.shape_selection.shape_selection.EntitySelection.from_generic_selection"
        )
        gen_shape = GENERIC_SELECTION
        EntitySelection.convert_selection(gen_shape, TEST_LEVEL)
        mocked_fgs.assert_called_once_with(gen_shape, TEST_LEVEL)

    def test_convert_selection_entity(self, mocker):
        mocked_fes = mocker.patch(
            "atmospheric_explorer.api.shape_selection.shape_selection.EntitySelection.from_entity_selection"
        )
        ent_sel = CONTINENT_SELECTION
        EntitySelection.convert_selection(ent_sel, SelectionLevel.COUNTRIES)
        mocked_fes.assert_called_once_with(ent_sel, SelectionLevel.COUNTRIES)


def test_from_out_event_entity():
    sel = from_out_event(ENTITY_OUT_EVENT, level=SelectionLevel.CONTINENTS)
    assert isinstance(sel, EntitySelection)
    assert len(sel.dataframe) == 1
    assert sel.labels == ["Antarctica"]
    assert sel.level == SelectionLevel.CONTINENTS
    assert isinstance(sel.dataframe.geometry.iloc[0], shapely.geometry.MultiPolygon)


def test_from_out_event_generic():
    sel = from_out_event(GENERIC_OUT_EVENT, level=TEST_LEVEL)
    assert isinstance(sel, GenericShapeSelection)
    assert len(sel.dataframe) == 1
    assert sel.labels == ["generic shape"]
    assert sel.level == SelectionLevel.GENERIC
    assert isinstance(sel.dataframe.geometry.iloc[0], shapely.geometry.Polygon)
