"""\
Module with utils for the UI
"""
import geopandas as gpd
import streamlit as st

from atmospheric_explorer.shapefile import ShapefilesDownloader


def local_css(filename: str) -> None:
    """Load local css"""
    with open(filename, "r", encoding="utf-8") as style_file:
        st.markdown(f"<style>{style_file.read()}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner="Fetching shapefile...")
def shapefile_dataframe() -> gpd.GeoDataFrame:
    """Get and cache the shapefile"""
    return ShapefilesDownloader().get_as_dataframe(columns=["ADMIN", "geometry"])


def build_sidebar():
    """Build sidebar"""
    with st.sidebar:
        st.write(f"Selected country: {st.session_state.get('selected_state')}")
        st.write(
            f"Dates: {st.session_state.get('start_date')}/{st.session_state.get('end_date')}"
        )
