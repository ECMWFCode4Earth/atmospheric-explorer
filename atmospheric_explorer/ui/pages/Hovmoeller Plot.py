"""\
Module for creating Hovmoeller plots through UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.api.loggers import get_logger
from atmospheric_explorer.api.plotting.hovmoller import eac4_hovmoeller_plot
from atmospheric_explorer.ui.session_state import (
    GeneralSessionStateKeys,
    HovmSessionStateKeys,
)
from atmospheric_explorer.ui.ui_mappings import (
    eac4_ml_data_variable_default_plot_title_mapping,
    eac4_ml_data_variable_var_name_mapping,
    eac4_ml_data_variables,
    eac4_model_levels,
    eac4_pressure_levels,
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
    if HovmSessionStateKeys.HOVM_START_DATE not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_START_DATE] = datetime(2022, 1, 1)
    if HovmSessionStateKeys.HOVM_END_DATE not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_END_DATE] = datetime(2022, 4, 1)
    if HovmSessionStateKeys.HOVM_TIME not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_TIME] = "00:00"
    if HovmSessionStateKeys.HOVM_YAXIS not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_YAXIS] = "Latitude"
    if HovmSessionStateKeys.HOVM_P_LEVELS not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_P_LEVELS] = [1, 2]
    if HovmSessionStateKeys.HOVM_M_LEVELS not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_M_LEVELS] = [1, 2]
    if HovmSessionStateKeys.HOVM_DATA_VARIABLE not in st.session_state:
        st.session_state[HovmSessionStateKeys.HOVM_DATA_VARIABLE] = "total_column_ozone"


def _year_selector():
    logger.debug("Setting year selector")
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    start_date_col.date_input("Start date", key=HovmSessionStateKeys.HOVM_START_DATE)
    end_date_col.date_input("End date", key=HovmSessionStateKeys.HOVM_END_DATE)


def _times_selector():
    logger.debug("Setting times selector")
    st.selectbox(
        label="Time",
        options=eac4_times,
        key=HovmSessionStateKeys.HOVM_TIME,
    )


def _y_axis_selector():
    logger.debug("Setting y axis selector")
    st.radio(
        "Vertical axis",
        ["Latitude", "Pressure Level", "Model Level"],
        index=0,
        horizontal=True,
        key=HovmSessionStateKeys.HOVM_YAXIS,
        help="Select one of the level types",
    )
    match st.session_state[HovmSessionStateKeys.HOVM_YAXIS]:
        case "Latitude":
            pass
        case "Pressure Level":
            logger.debug("Setting pressure level selector")
            st.multiselect(
                label="Pressure Level",
                options=eac4_pressure_levels,
                key=HovmSessionStateKeys.HOVM_P_LEVELS,
            )
        case "Model Level":
            logger.debug("Setting model level selector")
            st.multiselect(
                label="Model Level",
                options=eac4_model_levels,
                key=HovmSessionStateKeys.HOVM_M_LEVELS,
            )


def _var_selectors():
    logger.debug("Setting data variable and var name selectors")
    if st.session_state[HovmSessionStateKeys.HOVM_YAXIS] == "Latitude":
        all_vars = eac4_sl_data_variables
        vars_mapping = eac4_sl_data_variable_var_name_mapping
        title_mapping = eac4_sl_data_variable_default_plot_title_mapping
    else:
        all_vars = eac4_ml_data_variables
        vars_mapping = eac4_ml_data_variable_var_name_mapping
        title_mapping = eac4_ml_data_variable_default_plot_title_mapping
    st.selectbox(
        label="Data variable",
        options=all_vars,
        key=HovmSessionStateKeys.HOVM_DATA_VARIABLE,
    )
    v_name = vars_mapping[st.session_state[HovmSessionStateKeys.HOVM_DATA_VARIABLE]]
    st.text(f"Var name: {v_name}")
    logger.debug("Setting title input")
    title = st.text_input(
        label="Plot title",
        value=title_mapping[st.session_state[HovmSessionStateKeys.HOVM_DATA_VARIABLE]],
    )
    return v_name, title


def _selectors():
    logger.info("Adding selection expander")
    with st.expander("Selection", expanded=True):
        _year_selector()
        _times_selector()
        _y_axis_selector()
        return _var_selectors()


def page():
    _init()
    var_name, plot_title = _selectors()
    build_sidebar()
    if st.button("Generate plot"):
        logger.info("Generating plot")
        y_axis = st.session_state[HovmSessionStateKeys.HOVM_YAXIS]
        start_date = st.session_state[HovmSessionStateKeys.HOVM_START_DATE]
        end_date = st.session_state[HovmSessionStateKeys.HOVM_END_DATE]
        dates_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        time_values = st.session_state[HovmSessionStateKeys.HOVM_TIME]
        shapes = st.session_state[GeneralSessionStateKeys.SELECTED_SHAPES]
        data_variable = st.session_state[HovmSessionStateKeys.HOVM_DATA_VARIABLE]
        with st.container():
            with st.spinner("Downloading data and building plot"):
                match y_axis:
                    case "Latitude":
                        logger.debug("Generating Latitude plot")
                        st.plotly_chart(
                            eac4_hovmoeller_plot(
                                data_variable=data_variable,
                                var_name=var_name,
                                dates_range=dates_range,
                                time_values=time_values,
                                title=plot_title,
                                shapes=shapes,
                            ),
                            use_container_width=True,
                        )
                    case "Pressure Level":
                        logger.debug("Generating Pressure Level plot")
                        levels = st.session_state[HovmSessionStateKeys.HOVM_P_LEVELS]
                        if levels:
                            st.plotly_chart(
                                eac4_hovmoeller_plot(
                                    data_variable=data_variable,
                                    var_name=var_name,
                                    dates_range=dates_range,
                                    time_values=time_values,
                                    pressure_level=levels,
                                    title=plot_title,
                                    shapes=shapes,
                                ),
                                use_container_width=True,
                            )
                    case "Model Level":
                        logger.debug("Generating Model Level plot")
                        levels = st.session_state[HovmSessionStateKeys.HOVM_M_LEVELS]
                        if levels:
                            st.plotly_chart(
                                eac4_hovmoeller_plot(
                                    data_variable=data_variable,
                                    var_name=var_name,
                                    dates_range=dates_range,
                                    time_values=time_values,
                                    model_level=levels,
                                    title=plot_title,
                                    shapes=shapes,
                                ),
                                use_container_width=True,
                            )


if __name__ == "__main__":
    page()
