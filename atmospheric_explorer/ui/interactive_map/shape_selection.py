"""\
Module to manage selections done on the folium map.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import geopandas as gpd
import streamlit as st
from shapely.geometry import shape
from shapely.ops import unary_union

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.shapefile import ShapefilesDownloader
from atmospheric_explorer.ui.interactive_map.map_config import (
    map_level_shapefile_mapping,
)
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys

logger = get_logger("atmexp")


@st.cache_data(show_spinner="Fetching shapefile...")
def shapefile_dataframe(level: str) -> gpd.GeoDataFrame:
    """Get and cache the shapefile"""
    col = map_level_shapefile_mapping[level]
    sh_df = ShapefilesDownloader(instance="map_subunits")
    sh_df = sh_df.get_as_dataframe()[[col, "geometry"]].rename({col: "label"}, axis=1)
    return sh_df.dissolve(by="label").reset_index()


class Selection(ABC):
    """Selection interface"""

    crs = "EPSG:4326"

    def __init__(self, dataframe: gpd.GeoDataFrame | None = None):
        self.dataframe = dataframe

    def empty(self) -> bool:
        """Return True if the selection is empty."""
        return self.dataframe is None

    def __repr__(self) -> str:
        return repr(self.dataframe)

    def __eq__(self, other: Selection) -> bool:
        if not self.empty():
            return self.dataframe.equals(other.dataframe)
        return self.dataframe == other.dataframe

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

    @classmethod
    @abstractmethod
    def convert_selection(cls, shape_selection: Selection):
        """Conversion between selection types."""
        raise NotImplementedError("A selection must have a convert_selection method!")


class GenericShapeSelection(Selection):
    """Class to manage generic shape selections on the interactive map."""

    @classmethod
    def convert_selection(cls, shape_selection: Selection) -> GenericShapeSelection:
        """Converts selections between types (shape vs entity)."""
        if isinstance(shape_selection, EntitySelection):
            return cls(dataframe=shape_selection.dataframe)
        return shape_selection


class EntitySelection(Selection):
    """Class to manage entity selections on the interactive map."""

    def __init__(
        self, dataframe: gpd.GeoDataFrame | None = None, level: str | None = None
    ):
        super().__init__(dataframe)
        self.level = level

    @classmethod
    def from_entities_list(
        cls, entities: list[str], level: str | None = None
    ) -> EntitySelection:
        """Generate an EntitySelection object from a list of entities, shapes are taken from the shapefile."""
        if entities:
            if level is None:
                level = st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            sh_df = shapefile_dataframe(level)
            sh_df = sh_df[sh_df["label"].isin(entities)]
            return cls(dataframe=sh_df, level=level)
        return cls()

    @classmethod
    def entities_from_generic_shape(
        cls, shape_selection: GenericShapeSelection, level: str | None = None
    ) -> EntitySelection:
        """\
        Generate an EntitySelection object encompassing entitities that are touched by
        the shape_selection objects passed.

        It assumes the shape_selection argument is a generic shape.
        """
        if not shape_selection.empty():
            if not isinstance(shape_selection, GenericShapeSelection):
                raise ValueError("Selection must be a generic shape selection")
            if level is None:
                level = st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            shapefile = shapefile_dataframe(level)
            selected_geometry = unary_union(shape_selection.dataframe["geometry"])
            return cls(
                dataframe=(
                    shapefile[
                        ~selected_geometry.intersection(shapefile["geometry"]).is_empty
                    ].reset_index(drop=True)
                ),
                level=level,
            )
        return cls()

    @classmethod
    def convert_selection(cls, shape_selection: Selection) -> EntitySelection:
        """Converts selections between levels and types (shape vs entity)."""
        if not shape_selection.empty():
            level = st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            if isinstance(shape_selection, EntitySelection):
                col_from = map_level_shapefile_mapping[shape_selection.level]
                col_to = map_level_shapefile_mapping[level]
                if level == shape_selection.level or col_from == col_to:
                    return cls(dataframe=shape_selection.dataframe, level=level)
                sh_df = ShapefilesDownloader(
                    instance="map_subunits"
                ).get_as_dataframe()[[col_from, col_to]]
                sh_df = sh_df.merge(
                    shape_selection.dataframe,
                    how="inner",
                    left_on=col_from,
                    right_on="label",
                )
                return cls.from_entities_list(list(sh_df[col_to].unique()), level)
            if isinstance(shape_selection, GenericShapeSelection):
                return cls.entities_from_generic_shape(shape_selection, level)
            return shape_selection
        return cls()


def from_out_event(out_event) -> Selection:
    """Generate a GenericShapeSelection/EntitySelection object from an output event generated by streamlit_folium."""
    admin = Selection.get_event_label(out_event)
    if admin is not None:
        return EntitySelection(
            dataframe=gpd.GeoDataFrame(
                {
                    "label": [admin] if admin is not None else ["generic shape"],
                    "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
                },
                crs=Selection.crs,
            ),
            level=st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
        )
    return GenericShapeSelection(
        dataframe=gpd.GeoDataFrame(
            {
                "label": ["generic shape"],
                "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
            },
            crs=Selection.crs,
        )
    )
