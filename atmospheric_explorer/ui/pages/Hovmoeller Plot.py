"""\
Module for creating Hovmoeller plots through UI
"""
# pylint: disable=invalid-name
from datetime import datetime
from textwrap import dedent

import streamlit as st

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.plotting.hovmoller import eac4_hovmoeller_plot
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


def _year_filters():
    start_date_col, end_date_col, _ = st.columns([1, 1, 3])
    start_date_col.date_input("Start date", key=HovmSessionStateKeys.HOVM_START_DATE)
    end_date_col.date_input("End date", key=HovmSessionStateKeys.HOVM_END_DATE)


def _times_filter():
    st.selectbox(
        label="Times",
        options=eac4_times,
        key=HovmSessionStateKeys.HOVM_TIME,
    )


def _y_axis_filter():
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
            st.multiselect(
                label="Pressure Level",
                options=eac4_pressure_levels,
                key=HovmSessionStateKeys.HOVM_P_LEVELS,
            )
        case "Model Level":
            st.multiselect(
                label="Model Level",
                options=eac4_model_levels,
                key=HovmSessionStateKeys.HOVM_M_LEVELS,
            )


def _var_filters():
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
    title = st.text_input(
        label="Plot title",
        value=title_mapping[st.session_state[HovmSessionStateKeys.HOVM_DATA_VARIABLE]],
    )
    return v_name, title


def _filters():
    with st.expander("Filters", expanded=True):
        logger.info("Adding filters")
        _year_filters()
        _times_filter()
        _y_axis_filter()
        return _var_filters()


# Page
_init()
var_name, plot_title = _filters()
build_sidebar()
if st.button("Generate plot"):
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
                    logger.debug(
                        dedent(
                            f"""\
                        Building Hovmoeller plot with parameters
                        Y axis: {y_axis}
                        Variable: {data_variable}
                        Var name: {var_name}
                        Shapes: {shapes}
                        Dates range: {dates_range}
                        Times: {time_values}
                        Title: {plot_title}
                        """
                        )
                    )
                    st.plotly_chart(
                        eac4_hovmoeller_plot(
                            data_variable=data_variable,
                            var_name=var_name,
                            dates_range=dates_range,
                            time_values=time_values,
                            title=plot_title,
                            shapes=shapes.dataframe,
                        ),
                        use_container_width=True,
                    )
                case "Pressure Level":
                    levels = st.session_state[HovmSessionStateKeys.HOVM_P_LEVELS]
                    logger.debug(
                        dedent(
                            f"""\
                            Building Hovmoeller plot with parameters
                            Y axis: {y_axis}
                            Variable: {data_variable}
                            Var name: {var_name}
                            Shapes: {shapes}
                            Dates range: {dates_range}
                            Times: {time_values}
                            Levels: {levels}
                            Title: {plot_title}
                        """
                        )
                    )
                    if levels:
                        st.plotly_chart(
                            eac4_hovmoeller_plot(
                                data_variable=data_variable,
                                var_name=var_name,
                                dates_range=dates_range,
                                time_values=time_values,
                                pressure_level=levels,
                                title=plot_title,
                                shapes=shapes.dataframe,
                            ),
                            use_container_width=True,
                        )
                case "Model Level":
                    levels = st.session_state[HovmSessionStateKeys.HOVM_M_LEVELS]
                    logger.debug(
                        dedent(
                            f"""\
                            Building Hovmoeller plot with parameters
                            Y axis: {y_axis}
                            Variable: {data_variable}
                            Var name: {var_name}
                            Shapes: {shapes}
                            Dates range: {dates_range}
                            Times: {time_values}
                            Levels: {levels}
                            Title: {plot_title}
                        """
                        )
                    )
                    if levels:
                        st.plotly_chart(
                            eac4_hovmoeller_plot(
                                data_variable=data_variable,
                                var_name=var_name,
                                dates_range=dates_range,
                                time_values=time_values,
                                model_level=levels,
                                title=plot_title,
                                shapes=shapes.dataframe,
                            ),
                            use_container_width=True,
                        )
