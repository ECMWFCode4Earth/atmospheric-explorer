"""\
Module with utils for the UI
"""
from pathlib import Path

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.interactive_map.map_config import MapLevels
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
        st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES] = True
    if GeneralSessionStateKeys.MAP_LEVEL not in st.session_state:
        st.session_state[GeneralSessionStateKeys.MAP_LEVEL] = MapLevels.CONTINENTS
    if GeneralSessionStateKeys.SELECTED_SHAPES not in st.session_state:
        st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES] = EntitySelection()


def build_sidebar():
    """Build sidebar"""
    logger.info("Building sidebar")
    level_name = st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
    with st.sidebar:
        if not st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].empty():
            if (
                st.session_state[GeneralSessionStateKeys.MAP_LEVEL]
                == MapLevels.ORGANIZATIONS
            ):
                labels = set(
                    [st.session_state[GeneralSessionStateKeys.SELECTED_ORGANIZATION]]
                )
            else:
                labels = set(
                    st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES].labels
                )
            if len(labels) > 3:
                selected_shapes_text = f"{len(labels)} {level_name.lower()}"
            else:
                selected_shapes_text = "<br>" + "<br>".join(labels)
            descr = (
                f"Selected {level_name.lower()}: {selected_shapes_text}"
                if st.session_state[GeneralSessionStateKeys.SELECT_ENTITIES]
                else "Selected generic shape"
            )
            st.write(descr, unsafe_allow_html=True)
        else:
            st.write("No selection")
