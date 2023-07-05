"""\
Module with utils for the UI
"""
from pathlib import Path

import geopandas as gpd
import streamlit as st

from atmospheric_explorer.shapefile import ShapefilesDownloader


def local_css(filename: str | Path) -> None:
    """Load local css"""
    with open(filename, "r", encoding="utf-8") as style_file:
        st.markdown(f"<style>{style_file.read()}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner="Fetching shapefile...")
def shapefile_dataframe() -> gpd.GeoDataFrame:
    """Get and cache the shapefile"""
    return ShapefilesDownloader().get_as_dataframe(columns=["ADMIN", "geometry"])


def build_sidebar(dates=False):
    """Build sidebar"""
    with st.sidebar:
        if st.session_state.get("selected_countries") is not None:
            if len(st.session_state["selected_countries"]) > 3:
                selected_countries_text = (
                    f"{len(st.session_state.get('selected_countries'))} countries"
                )
            else:
                selected_countries_text = " ".join(
                    st.session_state.get("selected_countries")
                )
            st.write(f"Selected countries: {selected_countries_text}")
        if dates:
            start_date = st.session_state.get("start_date")
            end_date = st.session_state.get("end_date")
            st.write(
                f"Dates: {start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            )
