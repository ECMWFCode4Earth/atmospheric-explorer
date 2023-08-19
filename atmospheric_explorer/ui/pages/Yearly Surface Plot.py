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
from atmospheric_explorer.ui.utils import build_sidebar, page_init

logger = get_logger("atmexp")
page_init()

if GHGSessionStateKeys.GHG_START_YEAR not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_START_YEAR] = 2020
if GHGSessionStateKeys.GHG_END_YEAR not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_END_YEAR] = 2022
if GHGSessionStateKeys.GHG_MONTHS not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_MONTHS] = ["01", "02"]

with st.form("filters"):
    logger.info("Adding filters")
    start_year_col, end_year_col, _ = st.columns([1, 1, 3])
    st.session_state[GHGSessionStateKeys.GHG_START_YEAR] = start_year_col.number_input(
        "Start year", value=st.session_state[GHGSessionStateKeys.GHG_START_YEAR], step=1
    )
    st.session_state[GHGSessionStateKeys.GHG_END_YEAR] = end_year_col.number_input(
        "End year", value=st.session_state[GHGSessionStateKeys.GHG_END_YEAR], step=1
    )
    st.session_state[GHGSessionStateKeys.GHG_MONTHS] = sorted(
        st.multiselect(
            "Months",
            [f"{m:02}" for m in range(1, 13)],
            st.session_state[GHGSessionStateKeys.GHG_MONTHS],
        )
    )
    submitted = st.form_submit_button("Generate plot")

build_sidebar()
if submitted:
    years = [
        str(y)
        for y in range(
            st.session_state[GHGSessionStateKeys.GHG_START_YEAR],
            st.session_state[GHGSessionStateKeys.GHG_END_YEAR] + 1,
        )
    ]
    months = st.session_state[GHGSessionStateKeys.GHG_MONTHS]
    shapes = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
            Building first plot with parameters
            Variable: carbon_dioxide
            Shapes: {shapes}
            Years: {years}
            Month: {months}
            """
                )
            )
            st.plotly_chart(
                ghg_surface_satellite_yearly_plot(
                    data_variable="carbon_dioxide",
                    var_name="flux_foss",
                    years=years,
                    months=months,
                    title="CO2",
                    shapes=shapes.dataframe,
                ),
                use_container_width=True,
            )
