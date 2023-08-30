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


def _init():
    page_init()
    if "used_form" not in st.session_state:
        st.session_state["used_form"] = False
    if "select_entities_helper" not in st.session_state:
        st.session_state["select_entities_helper"] = st.session_state[
            GeneralSessionStateKeys.SELECT_ENTITIES
        ]
    if "map_level_helper" not in st.session_state:
        st.session_state["map_level_helper"] = st.session_state[
            GeneralSessionStateKeys.MAP_LEVEL
        ]
    if "selected_shapes_labels" not in st.session_state:
        st.session_state["selected_shapes_labels"] = st.session_state[
            GeneralSessionStateKeys.SELECTED_SHAPES
        ].labels


def _selectors_org():
    org = st.selectbox(
        st.session_state["map_level_helper"],
        options=organizations.keys(),
    )
    st.session_state[
        GeneralSessionStateKeys.SELECTED_SHAPES
    ] = EntitySelection.from_entities_list(organizations[org])
    st.session_state["selected_shapes_labels"] = st.session_state[
        GeneralSessionStateKeys.SELECTED_SHAPES
    ].labels


def _selectors_no_org():
    if st.session_state["used_form"]:
        st.session_state[
            GeneralSessionStateKeys.SELECTED_SHAPES
        ] = EntitySelection.from_entities_list(
            st.session_state["selected_shapes_labels"]
        )
    else:
        st.session_state["selected_shapes_labels"] = st.session_state[
            GeneralSessionStateKeys.SELECTED_SHAPES
        ].labels
    st.session_state["used_form"] = False
    sh_all_labels = shapefile_dataframe(st.session_state["map_level_helper"])[
        "label"
    ].unique()
    st.multiselect(
        st.session_state["map_level_helper"],
        options=sh_all_labels,
        key="selected_shapes_labels",
    )
    st.write(st.session_state["selected_shapes_labels"])


def selectors():
    """Selectors for the Home page."""

    def _used_form():
        st.session_state["used_form"] = True

    with st.form("selectors"):
        st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES] = st.checkbox(
            label="Select entities",
            key="select_entities_helper",
            help="Switch to the selection of political or geographical entities such as continents and countries",
        )
        if st.session_state["select_entities_helper"]:
            if (
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
                != st.session_state["map_level_helper"]
            ):
                st.session_state[
                    GeneralSessionStateKeys.SELECTED_SHAPES
                ] = EntitySelection()
                st.session_state["selected_shapes_labels"] = []
            st.session_state[GeneralSessionStateKeys.MAP_LEVEL] = st.selectbox(
                label="Entity level",
                options=list(MapLevels),
                key="map_level_helper",
                help="""\
                Switch between continents, countries etc.
                After selecting the level, click the "Update Selection" button to make the selection effective.
                """,
            )
            if st.session_state["map_level_helper"] == "Organizations":
                _selectors_org()
            else:
                _selectors_no_org()
        st.form_submit_button(
            "Update Selection",
            help="""\
            Update both the map and the form.
            Click to make any change in the form effective.
            """,
            on_click=_used_form,
        )


_init()
logger.info("Starting streamlit app")
progress_bar = st.progress(0.0, "Starting app")
st.title("Atmospheric Explorer")
st.subheader("Geographical selection")
logger.info("Checking session state")
progress_bar.progress(0.2, "Building selectors")
selectors()
progress_bar.progress(0.4, "Building side bar")
build_sidebar()
progress_bar.progress(0.6, "Building map")
out_event = show_folium_map()
progress_bar.progress(0.8, "Updating session")
update_session_map_click(out_event)
progress_bar.progress(1.0, "Done")
progress_bar.empty()
