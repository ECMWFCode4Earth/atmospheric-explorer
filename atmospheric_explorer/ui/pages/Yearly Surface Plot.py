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
    ghg_data_variable_default_plot_title_mapping,
    ghg_data_variable_var_name_mapping,
    ghg_data_variables,
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
if GHGSessionStateKeys.GHG_DATA_VARIABLE not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] = "carbon_dioxide"
if GHGSessionStateKeys.GHG_ADD_SATELLITE not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE] = False

# Get mapped var_name and plot_title from dictionary.
# For GHG, both var_name(s) and plot_title can be changed in the UI.
mapped_var_names = ghg_data_variable_var_name_mapping[
    st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
]
mapped_plot_title = ghg_data_variable_default_plot_title_mapping[
    st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
]
if GHGSessionStateKeys.GHG_VAR_NAME not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_VAR_NAME] = mapped_var_names[0]
if GHGSessionStateKeys.GHG_PLOT_TITLE not in st.session_state:
    st.session_state[GHGSessionStateKeys.GHG_PLOT_TITLE] = mapped_plot_title

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
    st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] = st.selectbox(
        label="Data variable",
        options=ghg_data_variables,
    )
    update = st.form_submit_button("Update widgets below")

    st.session_state[GHGSessionStateKeys.GHG_VAR_NAME] = st.selectbox(
        label="Var name",
        options=mapped_var_names,
        help="Select var_name parameters. For CO2, each couple corresponds to [surface, satellite] var_names",
    )
    # NOTE: including satellite observations is currently not working (see plotting_apis.py)
    # if st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] == "carbon_dioxide":
    #     st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE] = st.checkbox(
    #         label="Include satellite observations",
    #         value=st.session_state[GHGSessionStateKeys.GHG_ADD_SATELLITE],
    #     )
    st.session_state[GHGSessionStateKeys.GHG_PLOT_TITLE] = st.text_input(
        "Plot title",
        value=mapped_plot_title,
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
    data_variable = st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
    var_name = st.session_state[GHGSessionStateKeys.GHG_VAR_NAME]
    plot_title = st.session_state[GHGSessionStateKeys.GHG_PLOT_TITLE]
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
                    var_name=var_name,
                    add_satellite_observations=add_satellite_observations,
                    years=years,
                    months=months,
                    title=plot_title,
                    shapes=shapes.dataframe,
                ),
                use_container_width=True,
            )
