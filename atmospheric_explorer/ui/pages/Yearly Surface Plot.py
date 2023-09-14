"""\
Module for creating GHG plots through UI
"""
# pylint: disable=invalid-name
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.yearly_flux import (
    ghg_surface_satellite_yearly_plot,
)
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


def _init():
    page_init()
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


def _year_selectors():
    logger.debug("Setting years selector")
    start_year_col, end_year_col, _ = st.columns([1, 1, 3])
    start_year_col.number_input(
        "Start year", key=GHGSessionStateKeys.GHG_START_YEAR, step=1
    )
    end_year_col.number_input("End year", key=GHGSessionStateKeys.GHG_END_YEAR, step=1)


def _months_selectors():
    logger.debug("Setting months selector")
    st.checkbox(label="All Months", key=GHGSessionStateKeys.GHG_ALL_MONTHS)
    if not st.session_state[GHGSessionStateKeys.GHG_ALL_MONTHS]:
        st.multiselect(
            label="Months",
            options=[f"{m:02}" for m in range(1, 13)],
            key=GHGSessionStateKeys.GHG_MONTHS,
        )
    else:
        st.session_state[GHGSessionStateKeys.GHG_MONTHS] = [
            f"{m:02}" for m in range(1, 13)
        ]


def _vars_selectors():
    logger.debug("Setting data variable selector")
    st.selectbox(
        label="Data variable",
        options=ghg_data_variables,
        key=GHGSessionStateKeys.GHG_DATA_VARIABLE,
    )
    if st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] == "carbon_dioxide":
        logger.debug("Setting satellite selector")
        st.checkbox(
            label="Include satellite observations",
            key=GHGSessionStateKeys.GHG_ADD_SATELLITE,
        )
    elif st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE] == "nitrous_oxide":
        st.warning(
            "Please be aware that nitrous_oxide dataset is missing the cell area,\
            so values will be shown as average flux (kg m-2) instead of total amount (kg)"
        )


def _selectors():
    logger.info("Adding selection expander")
    with st.expander("Selection", expanded=True):
        _year_selectors()
        _months_selectors()
        _vars_selectors()
        var_names = ghg_data_variable_var_name_mapping[
            st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
        ]
        v_name = st.selectbox(
            label="Var name",
            options=var_names,
            help="Select var_name inside dataset",
        )
        idx = var_names.index(v_name)
        logger.debug("Setting title input")
        title = st.text_input(
            "Plot title",
            value=ghg_data_variable_default_plot_title_mapping[
                st.session_state[GHGSessionStateKeys.GHG_DATA_VARIABLE]
            ][idx],
        )
    return v_name, title


def page():
    _init()
    var_name, plot_title = _selectors()
    build_sidebar()
    if st.button("Generate plot"):
        logger.info("Generating plot")
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
                st.plotly_chart(
                    ghg_surface_satellite_yearly_plot(
                        data_variable=data_variable,
                        years=years,
                        months=months,
                        title=plot_title,
                        var_name=var_name,
                        shapes=shapes,
                        add_satellite_observations=(
                            add_satellite_observations and data_variable == "carbon_dioxide"
                        ),
                    ),
                    use_container_width=True,
                )


if __name__ == "__main__":
    page()
