"""\
Module for building the UI
"""

import os
from datetime import datetime

import pandas as pd
import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import (
    eac4_anomalies_plot,
    eac4_hovmoeller_latitude_plot,
    eac4_hovmoeller_levels_plot,
    ghg_surface_satellite_yearly_plot,
)
from atmospheric_explorer.ui.interactive_map import (
    show_folium_map,
    update_session_map_click,
)
from atmospheric_explorer.ui.utils import build_sidebar, local_css

logger = get_logger("atmexp")
st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)

local_css(os.path.join(os.path.dirname(__file__), "style.css"))
logger.info("Starting streamlit app")
PROGRESS_BAR = st.progress(0, "Starting streamlit app")
st.title("Atmospheric Explorer")
logger.info("Checking session state")
PROGRESS_BAR.progress(0.2, "Checking session state")
if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_state" not in st.session_state:
    st.session_state["selected_state"] = "Italy"
if "start_date" not in st.session_state:
    st.session_state["start_date"] = datetime(2020, 1, 1)
if "end_date" not in st.session_state:
    st.session_state["end_date"] = datetime(2022, 1, 1)
logger.info("Building sidebar")
PROGRESS_BAR.progress(0.3, "Building sidebar")
build_sidebar()
logger.info("Building map")
PROGRESS_BAR.progress(0.4, "Building map")
with st.form("filters"):
    logger.info("Adding filters")
    PROGRESS_BAR.progress(0.5, "Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state["start_date"] = start_date_col.date_input(
        "Start date", value=st.session_state["start_date"]
    )
    st.session_state["end_date"] = end_date_col.date_input(
        "End date", value=st.session_state["end_date"]
    )
    PROGRESS_BAR.progress(0.6, "Building interactive map")
    out_event = show_folium_map()
    submit = st.form_submit_button()
    if submit:
        update_session_map_click(out_event)
        st.experimental_rerun()
with st.expander("Plots"):
    logger.info("Building plots")
    PROGRESS_BAR.progress(0.7, "Building plots")
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    countries = (
        st.session_state.get("selected_state")
        if isinstance(st.session_state.get("selected_state"), list)
        else [st.session_state.get("selected_state")]
    )
    years = [y.strftime("%Y") for y in pd.date_range(start_date, end_date, freq="YS")]
    months = sorted(
        list({m.strftime("%m") for m in pd.date_range(start_date, end_date, freq="MS")})
    )
    with st.container():
        PROGRESS_BAR.progress(0.8, "Building plots")
        col1, col2 = st.columns(2)
        logger.debug("Building first plot")
        col1.plotly_chart(
            ghg_surface_satellite_yearly_plot(
                "carbon_dioxide", countries, years, months, "CO2", "flux_foss"
            ),
            use_container_width=True,
        )
        logger.debug("Building second plot")
        col2.plotly_chart(
            eac4_anomalies_plot(
                "total_column_nitrogen_dioxide",
                "tcno2",
                countries,
                dates_range,
                "00:00",
                "Total column NO2",
            ),
            use_container_width=True,
        )
    with st.container():
        PROGRESS_BAR.progress(0.8, "Building plots")
        col3, col4 = st.columns(2)
        logger.debug("Building first plot")
        col3.plotly_chart(
            eac4_hovmoeller_latitude_plot(
                "total_column_ozone",
                "gtco3",
                dates_range,
                "00:00",
                "Total column O3",
            ),
            use_container_width=True,
        )
        logger.debug("Building second plot")
        col4.plotly_chart(
            eac4_hovmoeller_levels_plot(
                "carbon_monoxide",
                "co",
                dates_range,
                "00:00",
                ["1", "10", "100"],
                countries,
                "CO",
            ),
            use_container_width=True,
        )
    PROGRESS_BAR.progress(0.9, "Finished building plots")
PROGRESS_BAR.progress(1.0, "Done")
PROGRESS_BAR.empty()
