"""\
Module with utils for the UI
"""
from pathlib import Path

import geopandas as gpd
import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.shapefile import ShapefilesDownloader
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
    if GeneralSessionStateKeys.SELECTED_COUNTRIES not in st.session_state:
        st.session_state[GeneralSessionStateKeys.SELECTED_COUNTRIES] = ["Italy"]


@st.cache_data(show_spinner="Fetching shapefile...")
def shapefile_dataframe() -> gpd.GeoDataFrame:
    """Get and cache the shapefile"""
    return ShapefilesDownloader().get_as_dataframe()[["ADMIN", "geometry"]]


def build_sidebar():
    """Build sidebar"""
    logger.info("Building sidebar")
    with st.sidebar:
        if st.session_state.get(GeneralSessionStateKeys.SELECTED_COUNTRIES) is not None:
            countries = st.session_state[GeneralSessionStateKeys.SELECTED_COUNTRIES]
            if len(countries) > 3:
                selected_countries_text = f"{len(countries)} countries"
            else:
                selected_countries_text = "<br>" + "<br>".join(
                    st.session_state.get(GeneralSessionStateKeys.SELECTED_COUNTRIES)
                )
            st.write(
                f"Selected countries: {selected_countries_text}", unsafe_allow_html=True
            )
