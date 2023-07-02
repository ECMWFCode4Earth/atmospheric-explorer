"""\
Module for building the UI
"""

import pandas as pd
import streamlit as st

from atmospheric_explorer.plotting_apis import (
    eac4_anomalies_plot,
    ghg_surface_satellite_yearly_plot,
)
from atmospheric_explorer.ui.utils import build_sidebar, show_folium_map, update_session

st.set_page_config(
    page_title="Atmospheric Explorer", page_icon=":earth_africa:", layout="wide"
)

PROGRESS_BAR = st.progress(0, "Starting app")
st.title("Atmospheric Explorer")
PROGRESS_BAR.progress(0.2, "Checking session state")
if "last_object_clicked" not in st.session_state:
    st.session_state["last_object_clicked"] = [42, 13]
if "selected_state" not in st.session_state:
    st.session_state["selected_state"] = "Italy"

PROGRESS_BAR.progress(0.5, "Adding filters")
start_date_col, end_date_col, _ = st.columns([1, 1, 3])
st.session_state["start_date"] = start_date_col.date_input(
    "Start date", value=st.session_state.get("start_date")
)
st.session_state["end_date"] = end_date_col.date_input(
    "End date", value=st.session_state.get("end_date")
)
PROGRESS_BAR.progress(0.7, "Building sidebar")
build_sidebar()
PROGRESS_BAR.progress(0.8, "Building map")
out_event = show_folium_map()
update_session(out_event)
PROGRESS_BAR.progress(1.0, "Done")
PROGRESS_BAR.empty()
with st.expander("Plots"):
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")
    countries = (
        st.session_state.get("selected_state")
        if isinstance(st.session_state.get("selected_state"), list)
        else [st.session_state.get("selected_state")]
    )
    years = [y.strftime("%Y") for y in pd.date_range(start_date, end_date, freq="YS")]
    months = list(
        {m.strftime("%m") for m in pd.date_range(start_date, end_date, freq="MS")}
    )
    with st.container():
        col1, col2 = st.columns(2)
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
        col2.plotly_chart(
            eac4_anomalies_plot(
                "total_column_nitrogen_dioxide",
                "tcno2",
                countries,
                f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}",
                "00:00",
                "total_column_nitrogen_dioxide",
            )
        )
