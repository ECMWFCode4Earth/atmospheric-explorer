"""\
Module for building the UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from pathlib import Path

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map import (
    show_folium_map,
    update_session_map_click,
)
from atmospheric_explorer.ui.utils import build_sidebar, local_css, shapefile_dataframe

logger = get_logger("atmexp")
st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)

# Load css style file
local_css(Path(__file__).resolve().parents[0].joinpath("style.css"))

logger.info("Starting streamlit app")
progress_bar = st.progress(0.0, "Starting app")
st.title("Atmospheric Explorer")
st.subheader("Geographical selection")
logger.info("Checking session state")
progress_bar.progress(0.1, "Checking session state")
if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_countries" not in st.session_state:
    st.session_state["selected_countries"] = ["Italy"]
if "start_date" not in st.session_state:
    st.session_state["start_date"] = datetime(2020, 1, 1)
if "end_date" not in st.session_state:
    st.session_state["end_date"] = datetime(2022, 1, 1)
logger.info("Building sidebar")
progress_bar.progress(0.2, "Building side bar")
build_sidebar()
progress_bar.progress(0.3, "Building selectors")
with st.form("selection"):
    st.session_state["selected_countries"] = st.multiselect(
        "Countries",
        options=shapefile_dataframe()["ADMIN"].to_list(),
        default=st.session_state.get("selected_countries"),
    )
    st.form_submit_button("Update countries")
progress_bar.progress(0.4, "Building map")
out_event = show_folium_map()
progress_bar.progress(0.9, "Updating session")
update_session_map_click(out_event)
progress_bar.progress(1.0, "Done")
progress_bar.empty()
