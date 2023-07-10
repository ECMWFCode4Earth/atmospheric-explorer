"""\
Module for creating Anomalies plots through UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import eac4_anomalies_plot
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()

if "eac4_anomalies_start_date" not in st.session_state:
    st.session_state["eac4_anomalies_start_date"] = datetime(2022, 1, 1)
if "eac4_anomalies_end_date" not in st.session_state:
    st.session_state["eac4_anomalies_end_date"] = datetime(2022, 12, 31)
if "eac4_anomalies_times" not in st.session_state:
    st.session_state["eac4_anomalies_times"] = ["00:00"]

with st.form("filters"):
    logger.info("Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state["eac4_anomalies_start_date"] = start_date_col.date_input(
        "Start date", value=st.session_state["eac4_anomalies_start_date"]
    )
    st.session_state["eac4_anomalies_end_date"] = end_date_col.date_input(
        "End date", value=st.session_state["eac4_anomalies_end_date"]
    )
    st.session_state["eac4_anomalies_times"] = sorted(
        st.multiselect(
            "Times",
            [f"{h:02}:00" for h in range(0, 24, 3)],
            st.session_state["eac4_anomalies_times"],
        )
    )
    submitted = st.form_submit_button("Generate plot")

build_sidebar()
if submitted:
    start_date = st.session_state["eac4_anomalies_start_date"]
    end_date = st.session_state["eac4_anomalies_end_date"]
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    time_values = st.session_state["eac4_anomalies_times"]
    countries = st.session_state["selected_countries"]
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
                Building first plot with parameters
                Variable: carbon_dioxide
                Countries: {countries}
                Dates range: {dates_range}
                Times: {time_values}
                """
                )
            )
            st.plotly_chart(
                eac4_anomalies_plot(
                    "total_column_nitrogen_dioxide",
                    "tcno2",
                    countries,
                    dates_range,
                    time_values,
                    "Total Column NO2",
                ),
                use_container_width=True,
            )
