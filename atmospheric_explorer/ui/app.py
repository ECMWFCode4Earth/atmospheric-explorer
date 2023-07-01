"""\
Module for building the UI
"""
import streamlit as st

from atmospheric_explorer.ui.utils import (
    build_folium_map,
    build_sidebar,
    update_session,
)

st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)

PROGRESS_BAR = st.progress(0, "Starting app")
st.title("Atmospheric Explorer")
PROGRESS_BAR.progress(0.2, "Checking session state")
if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_state" not in st.session_state:
    st.session_state["selected_state"] = "Italy"

PROGRESS_BAR.progress(0.5, "Adding filters")
start_date_col, end_date_col, _ = st.columns([1, 1, 3])
st.session_state["start_date"] = start_date_col.date_input(
    "Start date", value=st.session_state.get("start_date")
)
st.session_state["end_date"] = end_date_col.date_input(
    "End date", value=st.session_state.get("end_date")
)
PROGRESS_BAR.progress(0.7, "Building sidebar")
build_sidebar()
PROGRESS_BAR.progress(0.8, "Building map")
out_event = build_folium_map()
update_session(out_event)
PROGRESS_BAR.progress(1.0, "Done")
PROGRESS_BAR.empty()
