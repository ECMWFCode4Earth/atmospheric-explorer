"""\
Module to keep all session state keys used inside the Streamlit application.
"""
from enum import Enum


class GeneralSessionStateKeys(Enum):
    """Enum that keeps all keys used for Streamlit session state."""

    LAST_OBJECT_CLICKED = "last_object_clicked"
    SELECTED_SHAPES = "selected_shapes"
    SELECT_COUNTRIES = "select_countries"
    LAST_ACTIVE_DRAWING = "last_active_drawing"


class EAC4AnomaliesSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for EAC4 anomalies page."""

    EAC4_ANOMALIES_START_DATE = "eac4_anomalies_start_date"
    EAC4_ANOMALIES_END_DATE = "eac4_anomalies_end_date"
    EAC4_ANOMALIES_TIMES = "eac4_anomalies_times"


class HovmSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for Hovmoeller page."""

    HOVM_START_DATE = "hovm_start_date"
    HOVM_END_DATE = "hovm_end_date"
    HOVM_TIMES = "hovm_times"
    HOVM_YAXIS = "hovm_yaxis"
    HOVM_LEVELS = "hovm_levels"


class GHGSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for GHG yearly page."""

    GHG_START_YEAR = "ghg_start_year"
    GHG_END_YEAR = "ghg_end_year"
    GHG_MONTHS = "ghg_months"
