"""\
Module with utils for the UI
"""
from pathlib import Path

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.interactive_map import map_levels
from atmospheric_explorer.ui.interactive_map.shape_selection import EntitySelection
from atmospheric_explorer.ui.session_state import GeneralSessionStateKeys

logger = get_logger("atmexp")


def local_css(filename: str | Path) -> None:
    """Load local css"""
    with open(filename, "r", encoding="utf-8") as style_file:
        st.markdown(f"<style>{style_file.read()}</style>", unsafe_allow_html=True)


def page_init():
    """Page initialization"""
    st.set_page_config(
        page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
    )
    local_css(Path(__file__).resolve().parent.joinpath("style.css"))
    if GeneralSessionStateKeys.LAST_OBJECT_CLICKED not in st.session_state:
        st.session_state[GeneralSessionStateKeys.LAST_OBJECT_CLICKED] = [42, 13]
    if GeneralSessionStateKeys.SELECT_ENTITIES not in st.session_state:
        st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES] = False
    if GeneralSessionStateKeys.MAP_LEVEL not in st.session_state:
        st.session_state[GeneralSessionStateKeys.MAP_LEVEL] = list(map_levels)[2]
    if GeneralSessionStateKeys.SELECTED_SHAPES not in st.session_state:
        st.session_state[
            GeneralSessionStateKeys.SELECTED_SHAPES
        ] = EntitySelection.from_entities_list(
            ["Italy"], st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
        )


def build_sidebar():
    """Build sidebar"""
    logger.info("Building sidebar")
    with st.sidebar:
        if st.session_state.get(GeneralSessionStateKeys.SELECTED_SHAPES) is not None:
            shapes = set(
                st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].labels
            )
            if len(shapes) > 3:
                selected_shapes_text = f"{len(shapes)} countries"
            else:
                selected_shapes_text = "<br>" + "<br>".join(
                    st.session_state.get(GeneralSessionStateKeys.SELECTED_SHAPES).labels
                )
            descr = (
                f"Selected countries: {selected_shapes_text}"
                if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]
                else "Selected generic shape"
            )
            st.write(descr, unsafe_allow_html=True)
