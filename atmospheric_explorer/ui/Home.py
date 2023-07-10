"""\
Main UI page
"""
# pylint: disable=invalid-name

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.interactive_map import (
    show_folium_map,
    update_session_map_click,
)
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys
from atmospheric_explorer.ui.utils import build_sidebar, page_init, shapefile_dataframe

logger = get_logger("atmexp")
page_init()

logger.info("Starting streamlit app")
progress_bar = st.progress(0.0, "Starting app")
st.title("Atmospheric Explorer")
st.subheader("Geographical selection")
logger.info("Checking session state")
progress_bar.progress(0.3, "Building selectors")
with st.form("selection"):
    st.session_state[GeneralSessionStateKeys.SELECTED_COUNTRIES] = st.multiselect(
        "Countries",
        options=shapefile_dataframe()["ADMIN"].to_list(),
        default=st.session_state.get(GeneralSessionStateKeys.SELECTED_COUNTRIES),
    )
    st.form_submit_button("Update countries")
progress_bar.progress(0.2, "Building side bar")
build_sidebar()
progress_bar.progress(0.4, "Building map")
out_event = show_folium_map()
progress_bar.progress(0.9, "Updating session")
update_session_map_click(out_event)
progress_bar.progress(1.0, "Done")
progress_bar.empty()
