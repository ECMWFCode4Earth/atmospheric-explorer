"""\
Module to manage selections done on the folium map.
"""
from __future__ import annotations

from functools import wraps

import geopandas as gpd
from geopandas.testing import assert_geodataframe_equal
from shapely.geometry import shape
from shapely.ops import unary_union

from atmospheric_explorer.api.config import CRS
from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.shape_selection.config import (
    SelectionLevel,
    map_level_shapefile_mapping,
)
from atmospheric_explorer.api.shape_selection.shapefile import (
    ShapefilesDownloader,
    dissolve_shapefile_level,
)

logger = get_logger("atmexp")


def selection_empty(func):
    """Decorator to add a check for an empty selection."""

    @wraps(func)
    def wrapper(cls, selection: Selection, *args, **kwargs):
        if not selection.empty():
            return func(cls, selection, *args, **kwargs)
        return cls()

    return wrapper


class Selection:
    """Selection interface"""

    def __init__(
        self,
        dataframe: gpd.GeoDataFrame | None = None,
        level: SelectionLevel | None = None,
    ):
        self.dataframe = dataframe
        self.level = level

    def empty(self) -> bool:
        """Return True if the selection is empty."""
        return self.dataframe is None

    def __repr__(self) -> str:
        return repr(self.dataframe)

    def __eq__(self, other: Selection) -> bool:
        if not self.empty():
            try:
                assert_geodataframe_equal(self.dataframe, other.dataframe)
            except AssertionError:
                return False
            return self.level == other.level
        return self.dataframe == other.dataframe and self.level == other.level

    @property
    def labels(self) -> list[str]:
        """Selection labels, useful when countries are selected."""
        if not self.empty():
            return list(self.dataframe["label"].unique())
        return []

    @staticmethod
    def get_event_label(out_event) -> str | None:
        """Get label from folium map click event"""
        if out_event.get("last_active_drawing") is not None:
            if out_event["last_active_drawing"].get("properties") is not None:
                return out_event["last_active_drawing"]["properties"].get("label")
        return None


class GenericShapeSelection(Selection):
    """Class to manage generic shape selections on the interactive map."""

    def __init__(self, dataframe: gpd.GeoDataFrame | None = None):
        super().__init__(dataframe, None)
        if dataframe is not None:
            self.level = SelectionLevel.GENERIC
        logger.debug(
            """\
        Created GenericShapeSelection with dataframe %s
        """,
            dataframe,
        )

    @classmethod
    @selection_empty
    def convert_selection(cls, shape_selection: Selection) -> GenericShapeSelection:
        """Converts selections between types (shape vs entity)."""
        if not isinstance(shape_selection, GenericShapeSelection):
            return cls(dataframe=shape_selection.dataframe)
        return shape_selection


class EntitySelection(Selection):
    """Class to manage entity selections on the interactive map."""

    def __init__(
        self,
        dataframe: gpd.GeoDataFrame | None = None,
        level: SelectionLevel | None = None,
    ):
        super().__init__(dataframe, level)
        if self.level == SelectionLevel.GENERIC:
            raise ValueError("EntitySelection cannot have level SelectionLevel.GENERIC")
        logger.debug(
            """\
        Created EntitySelection with dataframe %s and level %s
        """,
            dataframe,
            level,
        )

    @classmethod
    @selection_empty
    def from_generic_selection(
        cls, generic_shape_selection: GenericShapeSelection, level: SelectionLevel
    ) -> EntitySelection:
        """\
        Generate an EntitySelection object encompassing entitities that are touched by
        the generic_shape_selection objects passed.

        It assumes the generic_shape_selection argument is a generic shape.
        """
        if not isinstance(generic_shape_selection, GenericShapeSelection):
            raise ValueError(
                "Parameter generic_shape_selection must be a GenericShapeSelection instance"
            )
        shapefile = dissolve_shapefile_level(level)
        selected_geometry = unary_union(generic_shape_selection.dataframe["geometry"])
        return cls(
            dataframe=(
                shapefile[
                    ~selected_geometry.intersection(shapefile["geometry"]).is_empty
                ].reset_index(drop=True)
            ),
            level=level,
        )

    @classmethod
    def from_entities_list(
        cls, entities: list[str], level: SelectionLevel
    ) -> EntitySelection:
        """Generate an EntitySelection object from a list of entities, shapes are taken from the shapefile."""
        if entities:
            sh_df = dissolve_shapefile_level(level)
            sh_df = sh_df[sh_df["label"].isin(entities)]
            return cls(dataframe=sh_df, level=level)
        return cls()

    @classmethod
    @selection_empty
    def from_entity_selection(
        cls, entity_selection: EntitySelection, level: SelectionLevel
    ):
        """Convert an EntitySelection object to a new SelectionLevel."""
        if not isinstance(entity_selection, EntitySelection):
            raise ValueError(
                "Parameter entity_selection must be a EntitySelection instance"
            )
        col_from = map_level_shapefile_mapping[entity_selection.level]
        col_to = map_level_shapefile_mapping[level]
        if entity_selection.level == level or col_from == col_to:
            return cls(dataframe=entity_selection.dataframe, level=level)
        sh_df = ShapefilesDownloader(instance="map_subunits").get_as_dataframe()[
            [col_from, col_to]
        ]
        sh_df = sh_df.merge(
            entity_selection.dataframe,
            how="inner",
            left_on=col_from,
            right_on="label",
        )
        return cls.from_entities_list(list(sh_df[col_to].unique()), level)

    @classmethod
    def convert_selection(
        cls, shape_selection: Selection, level: SelectionLevel
    ) -> EntitySelection:
        """Converts selections between levels and types (shape vs entity)."""
        if isinstance(shape_selection, EntitySelection):
            return cls.from_entity_selection(shape_selection, level)
        if isinstance(shape_selection, GenericShapeSelection):
            return cls.from_generic_selection(shape_selection, level)
        return shape_selection


def from_out_event(out_event, level: SelectionLevel) -> Selection:
    """Generate a GenericShapeSelection/EntitySelection object from an output event generated by streamlit_folium."""
    admin = Selection.get_event_label(out_event)
    if admin is not None:
        return EntitySelection(
            dataframe=gpd.GeoDataFrame(
                {
                    "label": [admin],
                    "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
                },
                crs=CRS,
            ),
            level=level,
        )
    return GenericShapeSelection(
        dataframe=gpd.GeoDataFrame(
            {
                "label": ["generic shape"],
                "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
            },
            crs=CRS,
        )
    )
