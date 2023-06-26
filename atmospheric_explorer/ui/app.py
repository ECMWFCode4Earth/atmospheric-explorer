"""\
Module for building the UI
"""
import time

import streamlit as st
from streamlit_folium import st_folium

from atmospheric_explorer.shapefile import ShapefilesDownloader
from atmospheric_explorer.ui.utils import build_folium_map, update_session

st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)


@st.cache_data
def get_shapefile():
    """Get and cache the shapefile"""
    return ShapefilesDownloader().get_as_dataframe()


PROGRESS_BAR = st.progress(0, "Starting app")
st.title("Atmospheric Explorer")
PROGRESS_BAR.progress(0.2, "Reading world shapefile")
shapefile = get_shapefile()

if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_state" not in st.session_state:
    st.session_state["selected_state"] = "Italy"

PROGRESS_BAR.progress(0.4, "Selecting country")
country_polygon = shapefile[shapefile["ADMIN"] == st.session_state["selected_state"]][
    "geometry"
]

center_clicked = None  # pylint: disable=invalid-name
if st.session_state["last_object_clicked"]:
    center_clicked = st.session_state["last_object_clicked"]

time.sleep(1)
PROGRESS_BAR.progress(0.6, "Adding filters and sidebar")
start_date_col, end_date_col, _ = st.columns([1, 1, 3])
st.session_state["start_date"] = start_date_col.date_input(
    "Start date", value=st.session_state.get("start_date")
)
st.session_state["end_date"] = end_date_col.date_input(
    "End date", value=st.session_state.get("end_date")
)
with st.sidebar:
    st.write(f"Selected country: {st.session_state['selected_state']}")
    st.write(f"Dates: {st.session_state['start_date']}/{st.session_state['end_date']}")
PROGRESS_BAR.progress(0.8, "Building map")
folium_map, countries_polygons = build_folium_map(shapefile, country_polygon)
out_event = st_folium(
    folium_map,
    feature_group_to_add=countries_polygons,
    key="folium_map",
    center=center_clicked,
    returned_objects=["last_active_drawing", "last_object_clicked"],
    height=700,
    width=1500,
)
update_session(out_event)
PROGRESS_BAR.progress(1.0, "Done")
PROGRESS_BAR.empty()
