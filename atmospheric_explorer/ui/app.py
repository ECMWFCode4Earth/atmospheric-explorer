"""\
Module for building the UI
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import (
    eac4_anomalies_plot,
    ghg_surface_satellite_yearly_plot,
)
from atmospheric_explorer.ui.utils import (
    build_sidebar,
    show_folium_map,
    update_session_after_click,
)

logger = get_logger("atmexp")
st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)


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
logger.info("Adding filters")
PROGRESS_BAR.progress(0.3, "Adding filters")
start_date_col, end_date_col, _ = st.columns([1, 1, 3])
st.session_state["start_date"] = start_date_col.date_input(
    "Start date", value=st.session_state["start_date"]
)
st.session_state["end_date"] = end_date_col.date_input(
    "End date", value=st.session_state["end_date"]
)
logger.info("Building sidebar")
PROGRESS_BAR.progress(0.4, "Building sidebar")
build_sidebar()
logger.info("Building map")
PROGRESS_BAR.progress(0.5, "Building map")
out_event = show_folium_map()
update_session_after_click(out_event)
with st.expander("Plots"):
    logger.info("Building plots")
    PROGRESS_BAR.progress(0.6, "Building plots")
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
        PROGRESS_BAR.progress(0.7, "Building plots")
        col1, col2 = st.columns(2)
        logger.debug("Building first plot")
        col1.plotly_chart(
            ghg_surface_satellite_yearly_plot(
                "carbon_dioxide",
                countries,
                years,
                months,
                "Fossil CO2 flux",
                "flux_foss",
            )
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
            )
        )
    # PROGRESS_BAR.progress(0.8, "Building plots")
    # with st.container():
    #     col3, col4 = st.columns(2)
    #     col3.plotly_chart(
    #         ghg_surface_satellite_yearly_plot(
    #             "carbon_dioxide",
    #             countries,
    #             years,
    #             months,
    #             "Fossil CO2 flux",
    #             "flux_foss",
    #         )
    #     )
    #     col4.plotly_chart(
    #         eac4_anomalies_plot(
    #             "total_column_nitrogen_dioxide",
    #             "tcno2",
    #             countries,
    #             dates_range,
    #             "00:00",
    #             "Total column NO2",
    #         )
    #     )
PROGRESS_BAR.progress(1.0, "Done")
PROGRESS_BAR.empty()
