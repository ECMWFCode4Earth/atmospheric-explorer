"""\
Main UI page
"""
# pylint: disable=invalid-name

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.interactive_map import (
    shapefile_dataframe,
    show_folium_map,
    update_session_map_click,
)
from atmospheric_explorer.ui.interactive_map.map_config import MapLevels, organizations
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
progress_bar.progress(0.2, "Building selectors")
with st.form("selection"):
    st.checkbox(
        label="Select entities",
        key=GeneralSessionStateKeys.SELECT_ENTITIES,
        help="Switch to the selection of political or geographical entities such as continents and countries",
    )
    if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]:
        st.selectbox(
            label="Entity level",
            options=list(MapLevels),
            index=0,
            key=GeneralSessionStateKeys.MAP_LEVEL,
            help="""\
            Switch between continents, countries etc.
            After selecting the level, click the "Update Selection" button to make the selection effective.
            """,
        )
        if st.session_state[GeneralSessionStateKeys.MAP_LEVEL] == "Organizations":
            org = st.selectbox(
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                options=organizations.keys(),
            )
            st.session_state[
                GeneralSessionStateKeys.SELECTED_SHAPES
            ] = EntitySelection.from_entities_list(organizations[org])
            st.session_state[
                GeneralSessionStateKeys.SELECTED_SHAPES_LABELS
            ] = organizations[org]
        else:
            sh_all_labels = shapefile_dataframe(
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            )["label"].unique()
            prev_sel = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
            if (
                not isinstance(prev_sel, EntitySelection)
                or prev_sel.level != st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
            ):
                new_labels = EntitySelection.convert_selection(prev_sel).labels
                st.multiselect(
                    st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                    options=sh_all_labels,
                    default=new_labels,
                    key=GeneralSessionStateKeys.SELECTED_SHAPES_LABELS,
                )
            else:
                st.multiselect(
                    st.session_state[GeneralSessionStateKeys.MAP_LEVEL],
                    options=sh_all_labels,
                    default=st.session_state[
                        GeneralSessionStateKeys.SELECTED_SHAPES_LABELS
                    ],
                    key=GeneralSessionStateKeys.SELECTED_SHAPES_LABELS,
                )
            st.session_state[
                GeneralSessionStateKeys.SELECTED_SHAPES
            ] = EntitySelection.from_entities_list(
                entities=st.session_state[
                    GeneralSessionStateKeys.SELECTED_SHAPES_LABELS
                ]
            )
    st.form_submit_button(
        "Update Selection",
        help="""\
        Update both the map and the form.
        Click to make any change in the form effective.
        """,
    )
progress_bar.progress(0.4, "Building side bar")
build_sidebar()
progress_bar.progress(0.6, "Building map")
out_event = show_folium_map()
progress_bar.progress(0.8, "Updating session")
update_session_map_click(out_event)
progress_bar.progress(1.0, "Done")
progress_bar.empty()
