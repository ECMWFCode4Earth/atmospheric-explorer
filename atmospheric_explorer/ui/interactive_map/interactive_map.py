"""\
Module to build the interactive folium map to select countries from.
"""
import folium
import folium.features
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.country_selection import (
    countries_selection,
)
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys
from atmospheric_explorer.ui.utils import shapefile_dataframe

logger = get_logger("atmexp")


def _country_hover_style(_):
    """Style used for all countries, needed for caching"""
    return {"fillColor": "red"}


def _selected_countries_style(_) -> dict:
    """Style used for selected countries, needed for caching"""
    return {"fillColor": "green", "color": "green"}


@st.cache_data(show_spinner="Fetching world polygon...")
def world_polygon() -> folium.GeoJson:
    """Return a folium GeoJson object that adds colored polygons over all countries"""
    logger.info("Fetch world polygon")
    return folium.GeoJson(
        shapefile_dataframe(),
        name="world_polygon",
        highlight_function=_country_hover_style,
        zoom_on_click=False,
        tooltip=folium.features.GeoJsonTooltip(fields=["ADMIN"], aliases=[""]),
    )


@st.cache_data(show_spinner="Fetching selected state polygon...")
def selected_countries_fgroup(
    selected_countries: list[str] | None,
) -> folium.FeatureGroup:
    """Return a folium feature group that adds a colored polygon over the selected state"""
    logger.info("Fetch %s polygon", selected_countries)
    shapefile = shapefile_dataframe()
    selected_countries_polygons = shapefile[shapefile["ADMIN"].isin(selected_countries)]
    countries_feature_group = folium.FeatureGroup(name="Countries")
    countries_feature_group.add_child(
        folium.GeoJson(
            data=selected_countries_polygons,
            name="selected_countries_polygon",
            style_function=_selected_countries_style,
            tooltip=folium.features.GeoJsonTooltip(fields=["ADMIN"], aliases=[""]),
        )
    )
    return countries_feature_group


@st.cache_resource(show_spinner="Fetching map...")
def build_folium_map(selected_countries: list[str] | None):
    """Build folium map with a layer of polygons on countries"""
    logger.info("Build folium map")
    folium_map = folium.Map()
    Draw(
        export=True,
        draw_options={
            "circle": False,
            "marker": False,
            "polyline": False,
            "circlemarker": False,
        },
    ).add_to(
        folium_map
    )  # draw toolbar
    world_polygon().add_to(folium_map)
    selected_countries_fgroup(selected_countries).add_to(folium_map)
    return folium_map


def show_folium_map():
    """Show folium map in Streamlit"""
    logger.info("Show folium map")
    folium_map = build_folium_map(
        st.session_state.get(GeneralSessionStateKeys.SELECTED_COUNTRIES)
    )
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
        selected_countries = countries_selection(out_event)
        prev_selection = set(
            st.session_state[GeneralSessionStateKeys.SELECTED_COUNTRIES]
        )
        if selected_countries.isdisjoint(
            prev_selection
        ) or selected_countries.issuperset(prev_selection):
            st.session_state[GeneralSessionStateKeys.SELECTED_COUNTRIES] = sorted(
                list(selected_countries)
            )
            st.experimental_rerun()
