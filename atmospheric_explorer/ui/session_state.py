"""\
Module to keep all session state keys used inside the Streamlit application.
"""
from enum import Enum


class GeneralSessionStateKeys(Enum):
    """Enum that keeps all keys used for Streamlit session state."""

    LAST_OBJECT_CLICKED = "last_object_clicked"
    SELECTED_SHAPES = "selected_shapes"
    SELECT_ENTITIES = "select_entities"
    LAST_ACTIVE_DRAWING = "last_active_drawing"
    MAP_LEVEL = "map_level"
    SELECTED_ORGANIZATION = "selected_organization"


class EAC4AnomaliesSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for EAC4 anomalies page."""

    EAC4_ANOMALIES_START_DATE = "eac4_anomalies_start_date"
    EAC4_ANOMALIES_END_DATE = "eac4_anomalies_end_date"
    EAC4_ANOMALIES_TIMES = "eac4_anomalies_times"
    EAC4_ANOMALIES_DATA_VARIABLE = "eac4_anomalies_data_variable"
    EAC4_ANOMALIES_VAR_NAME = "eac4_anomalies_var_name"
    EAC4_ANOMALIES_PLOT_TITLE = "eac4_anomalies_title"
    EAC4_USE_REFERENCE = "eac4_use_reference"
    EAC4_REFERENCE_START_DATE = "eac4_reference_start_date"
    EAC4_REFERENCE_END_DATE = "eac4_reference_end_date"


class HovmSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for Hovmoeller page."""

    HOVM_START_DATE = "hovm_start_date"
    HOVM_END_DATE = "hovm_end_date"
    HOVM_TIME = "hovm_time"
    HOVM_YAXIS = "hovm_yaxis"
    HOVM_P_LEVELS = "hovm_p_levels"
    HOVM_M_LEVELS = "hovm_m_levels"
    HOVM_DATA_VARIABLE = "hovm_data_variable"
    HOVM_VAR_NAME = "hovm_var_name"
    HOVM_PLOT_TITLE = "hovm_title"


class GHGSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for GHG yearly page."""

    GHG_START_YEAR = "ghg_start_year"
    GHG_END_YEAR = "ghg_end_year"
    GHG_MONTHS = "ghg_months"
    GHG_DATA_VARIABLE = "ghg_data_variable"
    GHG_VAR_NAME = "ghg_var_name"
    GHG_PLOT_TITLE = "ghg_title"
    GHG_ADD_SATELLITE = "ghg_add_satellite"
    GHG_ALL_MONTHS = "ghg_all_months"
