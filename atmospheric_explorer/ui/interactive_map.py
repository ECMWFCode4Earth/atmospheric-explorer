"""\
Module with utils for the UI
"""
import folium
import folium.features
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from atmospheric_explorer.ui.utils import shapefile_dataframe


def world_polygon() -> folium.GeoJson:
    """Return a folium GeoJson object that adds colored polygons over all countries"""
    return folium.GeoJson(shapefile_dataframe(), name="world_polygon")


def selected_state_style(_) -> dict:
    """This function is needed because streamlit can't cache lambdas"""
    return {"fillColor": "green", "color": "green"}


def selected_state_fgroup(selected_state: str | None) -> folium.FeatureGroup:
    """Return a folium feature group that adds a colored polygon over the selected state"""
    shapefile = shapefile_dataframe()
    selected_country_polygon = shapefile[shapefile["ADMIN"] == selected_state][
        "geometry"
    ]
    countries_feature_group = folium.FeatureGroup(name="Countries")
    countries_feature_group.add_child(
        folium.GeoJson(
            data=selected_country_polygon,
            name="selected_state_polygon",
            style_function=selected_state_style,
        )
    )
    return countries_feature_group


def build_folium_map(selected_state: str | None):
    """Build folium map with a layer of polygons on countries"""
    folium_map = folium.Map()
    Draw().add_to(folium_map)
    world_polygon().add_to(folium_map)
    selected_state_fgroup(selected_state).add_to(folium_map)
    return folium_map


def show_folium_map():
    """Show folium map in Streamlit"""
    folium_map = build_folium_map(st.session_state.get("selected_state"))
    out_event = st_folium(
        folium_map,
        key="folium_map",
        center=st.session_state.get("last_object_clicked"),
        returned_objects=["last_active_drawing", "last_object_clicked"],
        height=700,
        width="100%",
    )
    return out_event


def get_admin(out):
    """Get admin from folium map click event"""
    try:
        return out["last_active_drawing"]["properties"]["ADMIN"]
    except KeyError:
        return out["last_active_drawing"]["id"]


def update_session_map_click(out):
    """Update session after folium map click event"""
    if out["last_active_drawing"] is not None:
        admin = get_admin(out)
        if admin != st.session_state["selected_state"]:
            st.session_state["selected_state"] = admin
    if (
        out["last_object_clicked"]
        and out["last_object_clicked"] != st.session_state["last_object_clicked"]
    ):
        st.session_state["last_object_clicked"] = out["last_object_clicked"]
        st.experimental_rerun()
