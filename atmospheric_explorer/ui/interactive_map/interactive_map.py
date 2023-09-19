"""\
Module to build the interactive folium map to select countries from on the Homepage.
"""
import folium
import folium.features
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.shape_selection.shape_selection import (
    EntitySelection,
    GenericShapeSelection,
    from_out_event,
)
from atmospheric_explorer.api.shape_selection.shapefile import dissolve_shapefile_level
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
    """\
    Return a folium.GeoJson object that adds colored polygons over all continents/countries in the interactive map.\
    """
    logger.info("Building world polygons")
    return folium.GeoJson(
        dissolve_shapefile_level(level),
        name="world_polygon",
        highlight_function=_country_hover_style,
        zoom_on_click=False,
        tooltip=folium.features.GeoJsonTooltip(fields=["label"], aliases=[""]),
    )


# @st.cache_data(show_spinner="Fetching selected state polygon...")
def selected_entities_fgroup() -> folium.FeatureGroup:
    """\
    Return a folium.FeatureGroup that adds a colored polygon over the selected entities.
    """
    logger.info("Building selected entities polygons")
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


def build_folium_map() -> folium.Map:
    """\
    Build the interactive folium map with (if enabled) a layer of polygons on entities.\
    """
    logger.info("Building folium map")
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
        selected_entities_fgroup().add_to(folium_map)
    return folium_map


def show_folium_map() -> dict:
    """\
    Render the folium map inside Streamlit.
    Returns the output event generated when clicking or drawing shapes on the map.\
    """
    logger.info("Rendering folium map")
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
    """\
    When clicking or drawing on the map, an output event is generated and passed as an argument to this function.
    This function takes care of parsing the event and selecting the clicked entity or, if entities are not enabled,
    the generic shape.\
    """
    if (
        out_event.get("last_object_clicked")
        != st.session_state[GeneralSessionStateKeys.LAST_OBJECT_CLICKED]
    ):
        logger.debug("Updating last object clicked in session state")
        st.session_state[GeneralSessionStateKeys.LAST_OBJECT_CLICKED] = out_event[
            "last_object_clicked"
        ]
    if out_event.get("last_active_drawing") is not None:
        logger.debug("Updating last selected shape in session state")
        sel = from_out_event(
            out_event, level=st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
        )
        if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
            logger.debug("Last selected shape is an entity")
            selected_countries = EntitySelection.convert_selection(
                shape_selection=sel,
                level=st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
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
            logger.debug("Last selected shape is a generic shape")
            selected_shape = GenericShapeSelection.convert_selection(sel)
            prev_selection = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
            if selected_shape != prev_selection:
                st.session_state[
                    GeneralSessionStateKeys.SELECTED_SHAPES
                ] = selected_shape
                st.experimental_rerun()
