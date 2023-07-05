"""\
Module for building the UI
"""
# pylint: disable=invalid-name
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting_apis import ghg_surface_satellite_yearly_plot
from atmospheric_explorer.ui.utils import build_sidebar, local_css

logger = get_logger("atmexp")
st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)
local_css(Path(__file__).resolve().parents[1].joinpath("style.css"))

with st.form("filters"):
    logger.info("Adding filters")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    st.session_state["start_date"] = start_date_col.date_input(
        "Start date", value=st.session_state["start_date"]
    )
    st.session_state["end_date"] = end_date_col.date_input(
        "End date", value=st.session_state["end_date"]
    )
    submitted = st.form_submit_button("Generate plot")


logger.info("Building sidebar")
build_sidebar(dates=True)
if submitted:
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")
    dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
    countries = (
        st.session_state.get("selected_countries")
        if isinstance(st.session_state.get("selected_countries"), list)
        else [st.session_state.get("selected_countries")]
    )
    years = [y.strftime("%Y") for y in pd.date_range(start_date, end_date, freq="YS")]
    months = sorted(
        list({m.strftime("%m") for m in pd.date_range(start_date, end_date, freq="MS")})
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
