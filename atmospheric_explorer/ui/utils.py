"""\
Module with utils for the UI
"""
import folium
import folium.features
import streamlit as st
from streamlit_folium import st_folium

from atmospheric_explorer.shapefile import ShapefilesDownloader


@st.cache_data
def get_shapefile():
    """Get and cache the shapefile"""
    return ShapefilesDownloader().get_as_dataframe()


def build_folium_map():
    """Build folium map in Streamlit with a layer of polygons on countries"""
    shapefile = get_shapefile()
    folium_map = folium.Map()
    folium.GeoJson(shapefile, name="geojson").add_to(folium_map)
    countries_feature_group = folium.FeatureGroup(name="Countries")
    selected_country_polygon = shapefile[
        shapefile["ADMIN"] == st.session_state.get("selected_state")
    ]["geometry"]
    countries_feature_group.add_child(
        folium.features.GeoJson(
            data=selected_country_polygon,
            style_function=lambda x: {"fillColor": "green", "color": "green"},
        )
    )
    countries_feature_group.add_to(folium_map)
    out_event = st_folium(
        folium_map,
        feature_group_to_add=countries_feature_group,
        key="folium_map",
        center=st.session_state.get("last_object_clicked"),
        returned_objects=["last_active_drawing", "last_object_clicked"],
        height=700,
        width=1500,
    )
    return out_event


def get_admin(out):
    """Get admin from folium map click event"""
    try:
        return out["last_active_drawing"]["properties"]["ADMIN"]
    except KeyError:
        return out["last_active_drawing"]["id"]


def update_session(out):
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


def build_sidebar():
    """Build sidebar"""
    with st.sidebar:
        st.write(f"Selected country: {st.session_state.get('selected_state')}")
        st.write(
            f"Dates: {st.session_state.get('start_date')}/{st.session_state.get('end_date')}"
        )
