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
from atmospheric_explorer.ui.interactive_map.shape_selection import (
    ShapeSelection,
    map_level_column_mapping,
)
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")


page_init()
logger.info("Starting streamlit app")
progress_bar = st.progress(0.0, "Starting app")
st.title("Atmospheric Explorer")
st.subheader("Geographical selection")
logger.info("Checking session state")
progress_bar.progress(0.3, "Building selectors")
with st.form("selection"):
    st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES] = st.checkbox(
        label="Select entities",
        value=st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES],
        help="Switch to the selection of political or geographical entities such as continents and countries",
    )
    if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
        st.session_state[GeneralSessionStateKeys.MAP_LEVEL] = st.selectbox(
            label="Entity level",
            options=map_level_column_mapping.keys(),
            index=list(map_level_column_mapping.keys()).index(
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            ),
        )
        sh = ShapeSelection.shapefile_dataframe(
            st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
        )
        entities = st.multiselect(
            st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
            options=sh["label"].unique(),
            default=ShapeSelection.convert_selection(
                st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES],
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
            ).labels,
        )
        st.session_state[
            GeneralSessionStateKeys.SELECTED_SHAPES
        ] = ShapeSelection.from_entities_list(
            entities, st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
        )
    st.form_submit_button("Update map")
progress_bar.progress(0.2, "Building side bar")
build_sidebar()
progress_bar.progress(0.4, "Building map")
out_event = show_folium_map()
progress_bar.progress(0.9, "Updating session")
update_session_map_click(out_event)
progress_bar.progress(1.0, "Done")
progress_bar.empty()
