"""\
Module for building the UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import (
    eac4_hovmoeller_latitude_plot,
    eac4_hovmoeller_levels_plot,
)
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()

if "hovm_start_date" not in st.session_state:
    st.session_state["hovm_start_date"] = datetime(2022, 1, 1)
if "hovm_end_date" not in st.session_state:
    st.session_state["hovm_end_date"] = datetime(2022, 12, 31)
if "hovm_times" not in st.session_state:
    st.session_state["hovm_times"] = ["00:00"]
if "hovm_yaxis" not in st.session_state:
    st.session_state["hovm_yaxis"] = "Latitude"
if "hovm_levels" not in st.session_state:
    st.session_state["hovm_levels"] = []

with st.form("filters"):
    logger.info("Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state["hovm_start_date"] = start_date_col.date_input(
        "Start date", value=st.session_state["hovm_start_date"]
    )
    st.session_state["hovm_end_date"] = end_date_col.date_input(
        "End date", value=st.session_state["hovm_end_date"]
    )
    st.session_state["hovm_times"] = sorted(
        st.multiselect(
            "Times",
            [f"{h:02}:00" for h in range(0, 24, 3)],
            st.session_state["hovm_times"],
        )
    )

    match st.radio(
        "Vertical axis", ["Latitude", "Pressure Level", "Model Level"], index=0
    ):
        case "Latitude":
            st.session_state["hovm_yaxis"] = "Latitude"
        case "Pressure Level":
            st.session_state["hovm_yaxis"] = "Pressure Level"
            st.session_state["hovm_levels"] = sorted(
                st.multiselect(
                    "Pressure Level",
                    [
                        "1",
                        "2",
                        "3",
                        "5",
                        "7",
                        "10",
                        "20",
                        "30",
                        "50",
                        "70",
                        "100",
                        "150",
                        "200",
                        "250",
                        "300",
                        "400",
                        "500",
                        "600",
                        "700",
                        "800",
                        "850",
                        "900",
                        "925",
                        "950",
                        "1000",
                    ],
                    st.session_state["hovm_levels"],
                ),
                key=int,
            )
        case "Model Level":
            st.session_state["hovm_yaxis"] = "Model Level"
            st.session_state["hovm_levels"] = sorted(
                st.multiselect(
                    "Model Level",
                    [str(m_level) for m_level in range(1, 61, 1)],
                    st.session_state["hovm_levels"],
                ),
                key=int,
            )
    submitted = st.form_submit_button("Generate plot")

build_sidebar()
if submitted:
    start_date = st.session_state["hovm_start_date"]
    end_date = st.session_state["hovm_end_date"]
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    time_values = st.session_state["hovm_times"]
    levels = st.session_state["hovm_levels"]
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
                Levels: {levels}
                """
                )
            )
            match st.session_state["hovm_yaxis"]:
                case "Latitude":
                    st.plotly_chart(
                        eac4_hovmoeller_latitude_plot(
                            "total_column_ozone",
                            "gtco3",
                            dates_range,
                            time_values,
                            "Total columns O3",
                        ),
                        use_container_width=True,
                    )
                case "Pressure Level":
                    if st.session_state["hovm_levels"]:
                        st.plotly_chart(
                            eac4_hovmoeller_levels_plot(
                                "carbon_monoxide",
                                "co",
                                dates_range,
                                time_values,
                                st.session_state["hovm_levels"],
                                countries,
                                "CO",
                            ),
                            use_container_width=True,
                        )
