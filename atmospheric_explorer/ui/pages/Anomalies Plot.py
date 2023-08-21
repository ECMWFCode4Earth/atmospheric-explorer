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
)
from atmospheric_explorer.ui.ui_mappings import (
    eac4_sl_data_variable_default_plot_title_mapping,
    eac4_sl_data_variable_var_name_mapping,
    eac4_sl_data_variables,
    eac4_times,
)
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")


def _init():
    page_init()
    # Set default SessionState values
    if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE not in st.session_state:
        st.session_state[
            EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE
        ] = datetime(2022, 1, 1)
    if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE not in st.session_state:
        st.session_state[
            EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE
        ] = datetime(2022, 12, 31)
    if EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES not in st.session_state:
        st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES] = ["00:00"]
    if (
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
        not in st.session_state
    ):
        st.session_state[
            EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
        ] = "total_column_nitrogen_dioxide"


def _dates_filters():
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE
    ] = start_date_col.date_input(
        label="Start date",
        value=st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_START_DATE],
    )
    st.session_state[
        EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE
    ] = end_date_col.date_input(
        label="End date",
        value=st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_END_DATE],
    )


def _times_filters():
    st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES] = sorted(
        st.multiselect(
            label="Times",
            options=eac4_times,
            default=st.session_state[
                EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_TIMES
            ],
        )
    )


def _filters():
    with st.expander("Filters", expanded=True):
        logger.info("Adding filters")
        _dates_filters()
        _times_filters()
        st.session_state[
            EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
        ] = st.selectbox(label="Data variable", options=eac4_sl_data_variables)
        v_name = eac4_sl_data_variable_var_name_mapping[
            st.session_state[EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE]
        ]
        st.text(f"Var name: {v_name}")
        title = st.text_input(
            label="Plot title",
            value=eac4_sl_data_variable_default_plot_title_mapping[
                st.session_state[
                    EAC4AnomaliesSessionStateKeys.EAC4_ANOMALIES_DATA_VARIABLE
                ]
            ],
        )
    return v_name, title


_init()
var_name, plot_title = _filters()
build_sidebar()
if st.button("Generate plot"):
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
                    shapes=shapes.dataframe,
                ),
                use_container_width=True,
            )
