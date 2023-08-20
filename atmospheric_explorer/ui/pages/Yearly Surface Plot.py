"""\
Module for creating GHG plots through UI
"""
# pylint: disable=invalid-name
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import ghg_surface_satellite_yearly_plot
from atmospheric_explorer.ui.session_state import (
    GeneralSessionStateKeys,
    GHGSessionStateKeys,
)
from atmospheric_explorer.ui.ui_mappings import (
    ghg_data_variable_default_plot_title_mapping,
    ghg_data_variable_var_name_mapping,
    ghg_data_variables,
)
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()


def _init():
    if GHGSessionStateKeys.GHG_START_YEAR not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_START_YEAR] = 2020
    if GHGSessionStateKeys.GHG_END_YEAR not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_END_YEAR] = 2022
    if GHGSessionStateKeys.GHG_MONTHS not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_MONTHS] = [
            f"{m:02}" for m in range(1, 13)
        ]
    if GHGSessionStateKeys.GHG_DATA_VARIABLE not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] = "carbon_dioxide"
    if GHGSessionStateKeys.GHG_ADD_SATELLITE not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE] = False
    if GHGSessionStateKeys.GHG_ALL_MONTHS not in st.session_state:
        st.session_state[GHGSessionStateKeys.GHG_ALL_MONTHS] = True


def _year_filter():
    start_year_col, end_year_col, _ = st.columns([1, 1, 3])
    st.session_state[GHGSessionStateKeys.GHG_START_YEAR] = start_year_col.number_input(
        "Start year", value=st.session_state[GHGSessionStateKeys.GHG_START_YEAR], step=1
    )
    st.session_state[GHGSessionStateKeys.GHG_END_YEAR] = end_year_col.number_input(
        "End year", value=st.session_state[GHGSessionStateKeys.GHG_END_YEAR], step=1
    )


def _months_filter():
    st.session_state[GHGSessionStateKeys.GHG_ALL_MONTHS] = st.checkbox(
        label="All Months", value=st.session_state[GHGSessionStateKeys.GHG_ALL_MONTHS]
    )
    if not st.session_state[GHGSessionStateKeys.GHG_ALL_MONTHS]:
        st.session_state[GHGSessionStateKeys.GHG_MONTHS] = sorted(
            st.multiselect(
                label="Months",
                options=[f"{m:02}" for m in range(1, 13)],
                default=st.session_state[GHGSessionStateKeys.GHG_MONTHS],
            )
        )
    else:
        st.session_state[GHGSessionStateKeys.GHG_MONTHS] = [
            f"{m:02}" for m in range(1, 13)
        ]


def _vars_filter():
    st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] = st.selectbox(
        label="Data variable", options=ghg_data_variables
    )
    if st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] == "carbon_dioxide":
        st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE] = st.checkbox(
            label="Include satellite observations",
            value=st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE],
        )


def _filters():
    with st.expander("Filters", expanded=True):
        logger.info("Adding filters")
        _year_filter()
        _months_filter()
        _vars_filter()
        v_name = st.selectbox(
            label="Var name",
            options=ghg_data_variable_var_name_mapping[
                st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
            ],
            help="Select var_name inside dataset",
        )
        title = st.text_input(
            "Plot title",
            value=ghg_data_variable_default_plot_title_mapping[
                st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
            ],
        )
    return v_name, title


_init()
var_name, plot_title = _filters()
build_sidebar()
if st.button("Generate plot"):
    years = [
        str(y)
        for y in range(
            st.session_state[GHGSessionStateKeys.GHG_START_YEAR],
            st.session_state[GHGSessionStateKeys.GHG_END_YEAR] + 1,
        )
    ]
    months = st.session_state[GHGSessionStateKeys.GHG_MONTHS]
    shapes = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
    data_variable = st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
    add_satellite_observations = st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE]
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
            Building first plot with parameters
            Variable: {data_variable}
            Var name: {var_name}
            Shapes: {shapes}
            Years: {years}
            Month: {months}
            Title: {plot_title}
            Add satellite observations: {add_satellite_observations}
            """
                )
            )
            st.plotly_chart(
                ghg_surface_satellite_yearly_plot(
                    data_variable=data_variable,
                    years=years,
                    months=months,
                    title=plot_title,
                    var_name=var_name,
                    shapes=shapes.dataframe,
                    add_satellite_observations=add_satellite_observations,
                ),
                use_container_width=True,
            )
