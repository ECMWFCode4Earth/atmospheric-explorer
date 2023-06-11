import os
import sys
import time

import folium
import folium.features
import geopandas as gpd
import requests
import requests.utils
import streamlit as st
from streamlit_folium import st_folium

PROGRESS_BAR = st.progress(0)


def download_shapefile(data_dir):
    SHAPEFILE_URL = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
    if not os.path.exists(f"{data_dir}/world_shapefile.zip"):
        headers = requests.utils.default_headers()
        headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
            }
        )
        r = requests.get(SHAPEFILE_URL, headers=headers)
        # Save downloaded data to zip file
        with open(f"{data_dir}/world_shapefile.zip", "wb") as f:
            f.write(r.content)


@st.cache_data
def load_shapefile(data_dir):
    shapefile = gpd.read_file(f"{data_dir}/world_shapefile.zip")
    shapefile.index = shapefile.GEOUNIT
    shapefile["name"] = shapefile.GEOUNIT
    return shapefile


def get_country_polygon(shapefile: gpd.GeoDataFrame, country: str):
    return shapefile[shapefile["ADMIN"] == country]["geometry"]


st.title("Atmospheric Explorer POC")
with st.sidebar:
    st.title("Atmospheric Explorer POC")

PROGRESS_BAR.progress(0.2, "Create data folder and download shapefile")
data_dir = os.path.dirname(sys.argv[0]) + "/.data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
PROGRESS_BAR.progress(0.4, "Download world shapefile")
download_shapefile(data_dir)
PROGRESS_BAR.progress(0.6, "Reading world shapefile")
shapefile = load_shapefile(data_dir)

if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_state" not in st.session_state:
    st.session_state["selected_state"] = "Italy"

country_polygon = get_country_polygon(shapefile, st.session_state["selected_state"])
with st.sidebar:
    st.write(f"Selected country: {st.session_state['selected_state']}")

center = None
if st.session_state["last_object_clicked"]:
    center = st.session_state["last_object_clicked"]

PROGRESS_BAR.progress(1.0, "Done")
time.sleep(1)
PROGRESS_BAR.empty()
m = folium.Map()
folium.GeoJson(shapefile, name="geojson").add_to(m)
fg = folium.FeatureGroup(name="Countries")
fg.add_child(
    folium.features.GeoJson(
        data=country_polygon,
        style_function=lambda x: {"fillColor": "green", "color": "green"},
    )
)
fg.add_to(m)

col1, col2 = st.columns(2)
with col1:
    out = st_folium(
        m,
        feature_group_to_add=fg,
        key="folium_map",
        center=center,
        returned_objects=["last_active_drawing", "last_object_clicked"],
    )
with col2:
    st.write(out)

if (
    out["last_active_drawing"] is not None
    and out["last_active_drawing"]["id"] != st.session_state["selected_state"]
):
    try:
        st.session_state["selected_state"] = out["last_active_drawing"]["properties"][
            "ADMIN"
        ]
    except KeyError:
        st.session_state["selected_state"] = out["last_active_drawing"]["id"]

if (
    out["last_object_clicked"]
    and out["last_object_clicked"] != st.session_state["last_object_clicked"]
):
    st.session_state["last_object_clicked"] = out["last_object_clicked"]
    st.experimental_rerun()
