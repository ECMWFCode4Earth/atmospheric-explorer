"""\
Module for creating Anomalies plots through UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import eac4_anomalies_plot
from atmospheric_explorer.ui.session_state import (
    EAC4AnomaliesSessionStateKeys,
    GeneralSessionStateKeys,
    eac4_data_variable_default_plot_title_mapping,
    eac4_data_variable_var_name_mapping,
)
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()

# Get mapped var_name and plot_title from dictionary.
# var_name cannot be changed in the UI, while plot_title can be changed.
mapped_var_name = eac4_data_variable_var_name_mapping[
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE]
]
mapped_plot_title = eac4_data_variable_default_plot_title_mapping[
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE]
]

# Set default SessionState values
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE not in st.session_state:
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE
    ] = datetime(2022, 1, 1)
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE not in st.session_state:
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE] = datetime(
        2022, 12, 31
    )
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES not in st.session_state:
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES] = ["00:00"]
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE not in st.session_state:
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
    ] = "total_column_nitrogen_dioxide"
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_VAR_NAME not in st.session_state:
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_VAR_NAME
    ] = mapped_var_name
if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_PLOT_TITLE not in st.session_state:
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_PLOT_TITLE
    ] = mapped_plot_title

with st.form("filters"):
    logger.info("Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE
    ] = start_date_col.date_input(
        "Start date",
        value=st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE],
    )
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE
    ] = end_date_col.date_input(
        "End date",
        value=st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE],
    )
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES] = sorted(
        st.multiselect(
            "Times",
            [f"{h:02}:00" for h in range(0, 24, 3)],
            st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES],
        )
    )
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
    ] = st.selectbox(
        "Data variable",
        ["total_column_nitrogen_dioxide"],
    )
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_VAR_NAME
    ] = mapped_var_name
    st.text(f"Var name: {mapped_var_name}")
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_PLOT_TITLE
    ] = st.text_input(
        "Plot title",
        st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_PLOT_TITLE],
    )

    submitted = st.form_submit_button("Generate plot")

build_sidebar()
if submitted:
    start_date = st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE
    ]
    end_date = st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE]
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    time_values = st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES]
    shapes = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
    data_variable = st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
    ]
    var_name = st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_VAR_NAME]
    plot_title = st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_PLOT_TITLE
    ]
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
                Building Anomalies plot with parameters
                Data variable: {data_variable}
                Var name: {var_name}
                Shapes: {shapes}
                Dates range: {dates_range}
                Times: {time_values}
                Title: {plot_title}
                """
                )
            )
            st.plotly_chart(
                eac4_anomalies_plot(
                    data_variable=data_variable,
                    var_name=var_name,
                    dates_range=dates_range,
                    time_values=time_values,
                    title=plot_title,
                    shapes=shapes.dataframe
                ),
                use_container_width=True,
            )
