"""\
Main UI page
"""
# pylint: disable=invalid-name

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.custom_mappings import organizations
from atmospheric_explorer.ui.interactive_map.interactive_map import (
    map_levels,
    show_folium_map,
    update_session_map_click,
)
from atmospheric_explorer.ui.interactive_map.shape_selection import EntitySelection
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
    st.checkbox(
        label="Select entities",
        value=st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES],
        key=GeneralSessionStateKeys.SELECT_ENTITIES,
        help="Switch to the selection of political or geographical entities such as continents and countries",
    )
    if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
        st.selectbox(
            label="Entity level",
            options=map_levels,
            index=0,
            key=GeneralSessionStateKeys.MAP_LEVEL
        )
        if st.session_state[GeneralSessionStateKeys.MAP_LEVEL] == "Organizations":
            org = st.selectbox(
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                options=organizations.keys(),
            )
            st.session_state[
                GeneralSessionStateKeys.SELECTED_SHAPES
            ] = EntitySelection.from_entities_list(
                entities=organizations[org],
                level="Countries"
            )
            st.session_state["entities"] = organizations[org]
        else:
            sh = EntitySelection.shapefile_dataframe(
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            )
            prev_sel = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
            if (
                not isinstance(prev_sel, EntitySelection) or
                prev_sel.level != st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            ):
                new_sel = EntitySelection.convert_selection(
                    shape_selection=prev_sel,
                    level=st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                )
                st.multiselect(
                    st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                    options = sh["label"].unique(),
                    default = new_sel.labels,
                    key = 'entities'
                )
            else:
                st.multiselect(
                    st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                    options = sh["label"].unique(),
                    default = st.session_state['entities'],
                    key = 'entities'
                )
            st.session_state[
                GeneralSessionStateKeys.SELECTED_SHAPES
            ] = EntitySelection.from_entities_list(
                entities=st.session_state['entities'],
                level=st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
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
