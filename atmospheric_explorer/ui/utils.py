"""\
Module with utils for the UI
"""
import folium
import folium.features
import streamlit as st


def build_folium_map(shapefile, country_polygon):
    """Build folium map in Streamlit with a layer of polygons on countries"""
    folium_map = folium.Map()
    folium.GeoJson(shapefile, name="geojson").add_to(folium_map)
    countries_polygons = folium.FeatureGroup(name="Countries")
    countries_polygons.add_child(
        folium.features.GeoJson(
            data=country_polygon,
            style_function=lambda x: {"fillColor": "green", "color": "green"},
        )
    )
    countries_polygons.add_to(folium_map)
    return folium_map, countries_polygons


def get_admin(out):
    """Get admin from folium click event"""
    try:
        return out["last_active_drawing"]["properties"]["ADMIN"]
    except KeyError:
        return out["last_active_drawing"]["id"]


def update_session(out):
    """Update session after click event"""
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
