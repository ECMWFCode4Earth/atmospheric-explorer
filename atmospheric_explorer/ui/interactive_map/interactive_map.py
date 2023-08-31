"""\
Module to build the interactive folium map to select countries from.
"""
import folium
import folium.features
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.shape_selection import (
    EntitySelection,
    GenericShapeSelection,
    from_out_event,
    shapefile_dataframe,
)
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys

logger = get_logger("atmexp")


def _country_hover_style(_):
    """Style used for all countries, needed for caching"""
    return {"fillColor": "red"}


def _selected_shapes_style(_) -> dict:
    """Style used for selected countries, needed for caching"""
    return {"fillColor": "green", "color": "green"}


@st.cache_data(show_spinner="Fetching world polygon...")
def world_polygon(level: str) -> folium.GeoJson:
    """Return a folium GeoJson object that adds colored polygons over all countries"""
    logger.info("Fetch world polygon")
    return folium.GeoJson(
        shapefile_dataframe(level),
        name="world_polygon",
        highlight_function=_country_hover_style,
        zoom_on_click=False,
        tooltip=folium.features.GeoJsonTooltip(fields=["label"], aliases=[""]),
    )


# @st.cache_data(show_spinner="Fetching selected state polygon...")
def selected_shapes_fgroup() -> folium.FeatureGroup:
    """Return a folium feature group that adds a colored polygon over the selected state"""
    countries_feature_group = folium.FeatureGroup(name="Countries")
    countries_feature_group.add_child(
        folium.GeoJson(
            data=st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].dataframe,
            name="selected_shapes_polygon",
            style_function=_selected_shapes_style,
            tooltip=folium.features.GeoJsonTooltip(fields=["label"], aliases=[""]),
        )
    )
    return countries_feature_group


# @st.cache_resource(show_spinner="Fetching map...")
def build_folium_map():
    """Build folium map with a layer of polygons on countries"""
    logger.info("Build folium map")
    folium_map = folium.Map()
    Draw(
        draw_options={
            "circle": False,
            "marker": False,
            "polyline": False,
            "circlemarker": False,
        },
    ).add_to(
        folium_map
    )  # draw toolbar
    if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
        world_polygon(st.session_state[GeneralSessionStateKeys.MAP_LEVEL]).add_to(
            folium_map
        )
    if not st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].empty():
        selected_shapes_fgroup().add_to(folium_map)
    return folium_map


def show_folium_map():
    """Show folium map in Streamlit"""
    logger.info("Show folium map")
    folium_map = build_folium_map()
    out_event = st_folium(
        folium_map,
        key="folium_map",
        center=st.session_state.get(GeneralSessionStateKeys.LAST_OBJECT_CLICKED),
        returned_objects=["last_active_drawing", "last_object_clicked"],
        height=800,
        width="100%",
        zoom=2,
    )
    return out_event


def update_session_map_click(out_event):
    """Update session after folium map click event"""
    if (
        out_event.get("last_object_clicked")
        != st.session_state[GeneralSessionStateKeys.LAST_OBJECT_CLICKED]
    ):
        st.session_state[GeneralSessionStateKeys.LAST_OBJECT_CLICKED] = out_event[
            "last_object_clicked"
        ]
    if out_event.get("last_active_drawing") is not None:
        if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
            selected_countries = EntitySelection.convert_selection(
                from_out_event(out_event)
            )
            sel_countries = set(selected_countries.labels)
            prev_selection = set(
                st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].labels
            )
            if sel_countries.isdisjoint(prev_selection) or sel_countries.issuperset(
                prev_selection
            ):
                st.session_state[
                    GeneralSessionStateKeys.SELECTED_SHAPES
                ] = selected_countries
                st.experimental_rerun()
        else:
            selected_shape = GenericShapeSelection.convert_selection(
                from_out_event(out_event)
            )
            prev_selection = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
            if selected_shape != prev_selection:
                st.session_state[
                    GeneralSessionStateKeys.SELECTED_SHAPES
                ] = selected_shape
                st.experimental_rerun()
