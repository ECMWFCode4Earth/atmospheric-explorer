"""\
Module for building the UI
"""
# pylint: disable=invalid-name
from pathlib import Path
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import ghg_surface_satellite_yearly_plot
from atmospheric_explorer.ui.utils import build_sidebar, local_css

logger = get_logger("atmexp")
st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)
local_css(Path(__file__).resolve().parents[1].joinpath("style.css"))

if "start_year" not in st.session_state:
    st.session_state["start_year"] = 2020
if "end_year" not in st.session_state:
    st.session_state["end_year"] = 2022
if "months" not in st.session_state:
    st.session_state["months"] = ["01"]

with st.form("filters"):
    logger.info("Adding filters")
    start_year_col, end_year_col, _ = st.columns([1, 1, 3])
    st.session_state["start_year"] = start_year_col.number_input(
        "Start year", value=st.session_state["start_year"], step=1
    )
    st.session_state["end_year"] = end_year_col.number_input(
        "End year", value=st.session_state["end_year"], step=1
    )
    st.session_state["months"] = sorted(
        st.multiselect(
            "Months", [f"{m:02}" for m in range(1, 13)], st.session_state["months"]
        )
    )
    submitted = st.form_submit_button("Generate plot")


logger.info("Building sidebar")
build_sidebar()
if submitted:
    years = [
        str(y)
        for y in range(st.session_state["start_year"], st.session_state["end_year"] + 1)
    ]
    months = st.session_state["months"]
    countries = (
        st.session_state.get("selected_countries")
        if isinstance(st.session_state.get("selected_countries"), list)
        else [st.session_state.get("selected_countries")]
    )
    with st.container():
        with st.spinner("Downloading data and building plot"):
            logger.debug(
                dedent(
                    f"""\
            Building first plot with parameters
            Variable: carbon_dioxide
            Countries: {countries}
            Years: {years}
            Month: {months}
            """
                )
            )
            st.plotly_chart(
                ghg_surface_satellite_yearly_plot(
                    "carbon_dioxide", countries, years, months, "CO2", "flux_foss"
                ),
                use_container_width=True,
            )
