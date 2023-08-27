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

logger = get_logger("atmexp")


@st.cache_data(show_spinner="Fetching shapefile...")
def shapefile_dataframe(level: str) -> gpd.GeoDataFrame:
    """Get and cache the shapefile"""
    col = map_level_shapefile_mapping[level]
    sh_df = ShapefilesDownloader(instance="map_subunits")
    sh_df = sh_df.get_as_dataframe()[[col, "geometry"]].rename({col: "label"}, axis=1)
    return sh_df.dissolve(by="label").reset_index()


class Selection(ABC):
    _crs = "EPSG:4326"

    def __init__(self, dataframe: gpd.GeoDataFrame):
        self.dataframe = dataframe

    def __repr__(self) -> str:
        return repr(self.dataframe)

    def __eq__(self, other: Selection) -> bool:
        return self.dataframe.equals(other.dataframe)

    @property
    def labels(self) -> list[str]:
        """Selection labels, useful when countries are selected."""
        return self.dataframe["label"].unique()

    @staticmethod
    def get_event_label(out_event) -> str | None:
        """Get label from folium map click event"""
        if out_event.get("last_active_drawing") is not None:
            if out_event["last_active_drawing"].get("properties") is not None:
                return out_event["last_active_drawing"]["properties"].get("label")
        return None

    @classmethod
    @abstractmethod
    def from_out_event(cls, out_event, **kwargs):
        """Generate a ShapeSelection object from an output event generated by streamlit_folium."""
        raise NotImplementedError("A selection must have a from_out_event method!")

    @abstractmethod
    def convert_selection(self, other: Selection, **kwargs) -> Selection:
        raise NotImplementedError("A selection must have a convert_selection method!")


class GenericShapeSelection(Selection):
    """Class to manage generic shape selections on the interactive map."""

    @classmethod
    def from_out_event(cls, out_event, **kwargs) -> GenericShapeSelection:
        """Generate a ShapeSelection object from an output event generated by streamlit_folium."""
        admin = cls.get_event_label(out_event)
        if admin is not None:
            raise ValueError("The click event is for an entity!")
        return cls(
            dataframe=gpd.GeoDataFrame(
                {
                    "label": ["generic shape"],
                    "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
                },
                crs=cls._crs,
            )
        )

    @classmethod
    def convert_selection(
        cls, shape_selection: Selection, **kwargs
    ) -> GenericShapeSelection:
        """Converts selections between types (shape vs entity)."""
        if isinstance(shape_selection, EntitySelection):
            return cls(dataframe=shape_selection.dataframe)
        return shape_selection


class EntitySelection(Selection):
    """Class to manage entity selections on the interactive map."""

    def __init__(self, dataframe: gpd.GeoDataFrame, level: str):
        super().__init__(dataframe)
        self.level = level

    @classmethod
    def from_entities_list(cls, entities: list[str], level: str) -> EntitySelection:
        """Generate a ShapeSelection object from a list of entities, shapes are taken from the shapefile."""
        sh_df = shapefile_dataframe(level)
        sh_df = sh_df[sh_df["label"].isin(entities)]
        return cls(dataframe=sh_df, level=level)

    @classmethod
    def entities_from_generic_shape(
        cls, shape_selection: GenericShapeSelection, level: str
    ) -> EntitySelection:
        """\
        Generate a ShapeSelection object encompassing entitities that are touched by the shape_selection objects passed.
        It assumes the shape_selection argument is a generic shape.
        """
        if not isinstance(shape_selection, GenericShapeSelection):
            raise ValueError("Selection must be a generic shape selection")
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

    @classmethod
    def from_out_event(cls, out_event, **kwargs) -> EntitySelection:
        """Generate a ShapeSelection object from an output event generated by streamlit_folium."""
        admin = cls.get_event_label(out_event)
        level = kwargs.get("level")
        if admin is None:
            raise ValueError("The click event is for a generic shape!")
        if level is None:
            raise ValueError("Expected the level!")
        return cls(
            dataframe=gpd.GeoDataFrame(
                {
                    "label": [admin] if admin is not None else ["generic shape"],
                    "geometry": [shape(out_event["last_active_drawing"]["geometry"])],
                },
                crs=cls._crs,
            ),
            level=level,
        )

    @classmethod
    def convert_selection(cls, shape_selection: Selection, **kwargs) -> EntitySelection:
        """Converts selections between levels and types (shape vs entity)."""
        level = kwargs.get("level")
        if level is None:
            raise ValueError("Expected the level!")
        if isinstance(shape_selection, EntitySelection):
            col_from = map_level_shapefile_mapping[shape_selection.level]
            col_to = map_level_shapefile_mapping[level]
            if level == shape_selection.level or col_from == col_to:
                return cls(dataframe=shape_selection.dataframe, level=level)
            sh_df = ShapefilesDownloader(instance="map_subunits").get_as_dataframe()[
                [col_from, col_to]
            ]
            sh_df = sh_df.merge(
                shape_selection.dataframe,
                how="inner",
                left_on=col_from,
                right_on="label",
            )
            return cls.from_entities_list(sh_df[col_to].unique(), level)
        elif isinstance(shape_selection, GenericShapeSelection):
            return cls.entities_from_generic_shape(shape_selection, level)
        return shape_selection
