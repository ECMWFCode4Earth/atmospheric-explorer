"""\
Module for creating Hovmoeller plots through UI
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
from atmospheric_explorer.ui.session_state import (
    GeneralSessionStateKeys,
    HovmSessionStateKeys,
)
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()

if HovmSessionStateKeys.HOVM_START_DATE not in st.session_state:
    st.session_state[HovmSessionStateKeys.HOVM_START_DATE] = datetime(2022, 1, 1)
if HovmSessionStateKeys.HOVM_END_DATE not in st.session_state:
    st.session_state[HovmSessionStateKeys.HOVM_END_DATE] = datetime(2022, 12, 31)
if HovmSessionStateKeys.HOVM_TIMES not in st.session_state:
    st.session_state[HovmSessionStateKeys.HOVM_TIMES] = ["00:00"]
if HovmSessionStateKeys.HOVM_YAXIS not in st.session_state:
    st.session_state[HovmSessionStateKeys.HOVM_YAXIS] = "Latitude"
if HovmSessionStateKeys.HOVM_LEVELS not in st.session_state:
    st.session_state[HovmSessionStateKeys.HOVM_LEVELS] = []

with st.form("filters"):
    logger.info("Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state[HovmSessionStateKeys.HOVM_START_DATE] = start_date_col.date_input(
        "Start date", value=st.session_state[HovmSessionStateKeys.HOVM_START_DATE]
    )
    st.session_state[HovmSessionStateKeys.HOVM_END_DATE] = end_date_col.date_input(
        "End date", value=st.session_state[HovmSessionStateKeys.HOVM_END_DATE]
    )
    st.session_state[HovmSessionStateKeys.HOVM_TIMES] = sorted(
        st.multiselect(
            "Times",
            [f"{h:02}:00" for h in range(0, 24, 3)],
            st.session_state[HovmSessionStateKeys.HOVM_TIMES],
        )
    )

    match st.radio(
        "Vertical axis",
        ["Latitude", "Pressure Level", "Model Level"],
        index=0,
        horizontal=True,
        help="Select one of the levels and click the form button to show the level selection widget",
    ):
        case "Latitude":
            st.session_state[HovmSessionStateKeys.HOVM_YAXIS] = "Latitude"
        case "Pressure Level":
            st.session_state[HovmSessionStateKeys.HOVM_YAXIS] = "Pressure Level"
            st.session_state[HovmSessionStateKeys.HOVM_LEVELS] = sorted(
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
                    [],
                ),
                key=int,
            )
        case "Model Level":
            st.session_state[HovmSessionStateKeys.HOVM_YAXIS] = "Model Level"
            st.session_state[HovmSessionStateKeys.HOVM_LEVELS] = sorted(
                st.multiselect(
                    "Model Level",
                    [str(m_level) for m_level in range(1, 61, 1)],
                    [],
                ),
                key=int,
            )
    submitted = st.form_submit_button("Generate plot")

build_sidebar()
if submitted:
    start_date = st.session_state[HovmSessionStateKeys.HOVM_START_DATE]
    end_date = st.session_state[HovmSessionStateKeys.HOVM_END_DATE]
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    time_values = st.session_state[HovmSessionStateKeys.HOVM_TIMES]
    levels = st.session_state[HovmSessionStateKeys.HOVM_LEVELS]
    shapes = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
                Building first plot with parameters
                Variable: carbon_dioxide
                Countries: {shapes}
                Dates range: {dates_range}
                Times: {time_values}
                Levels: {levels}
                """
                )
            )
            match st.session_state[HovmSessionStateKeys.HOVM_YAXIS]:
                case "Latitude":
                    st.plotly_chart(
                        eac4_hovmoeller_latitude_plot(
                            data_variable="total_column_ozone",
                            var_name="gtco3",
                            dates_range=dates_range,
                            time_values=time_values,
                            title="Total columns O3",
                        ),
                        use_container_width=True,
                    )
                case "Pressure Level":
                    if st.session_state[HovmSessionStateKeys.HOVM_LEVELS]:
                        st.plotly_chart(
                            eac4_hovmoeller_levels_plot(
                                data_variable="carbon_monoxide",
                                var_name="co",
                                dates_range=dates_range,
                                time_values=time_values,
                                pressure_level=st.session_state[
                                    HovmSessionStateKeys.HOVM_LEVELS
                                ],
                                title="CO",
                                shapes=shapes.dataframe,
                            ),
                            use_container_width=True,
                        )
