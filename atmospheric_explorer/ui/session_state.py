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
    EAC4_ANOMALIES_DATA_VARIABLE = "eac4_anomalies_data_variable"
    EAC4_ANOMALIES_VAR_NAME = "eac4_anomalies_var_name"
    EAC4_ANOMALIES_PLOT_TITLE = "eac4_anomalies_title"


class HovmSessionStateKeys(Enum):
    """Enum that keeps all session state keys used for Hovmoeller page."""

    HOVM_START_DATE = "hovm_start_date"
    HOVM_END_DATE = "hovm_end_date"
    HOVM_TIMES = "hovm_times"
    HOVM_YAXIS = "hovm_yaxis"
    HOVM_LEVELS = "hovm_levels"
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


# EAC4 mappings and data variables list
eac4_data_variable_var_name_mapping = {
    "total_column_nitrogen_dioxide": "tcno2",
    "total_column_ozone": "gtco3",
}

eac4_data_variable_default_plot_title_mapping = {
    "total_column_nitrogen_dioxide": "Total column NO2",
    "total_column_ozone": "Total column O3",
}

eac4_data_variables = list(eac4_data_variable_var_name_mapping.keys())

# GHG mappings and data variables list
# ! We are only considering surface_flux quantities
# carbon_dioxide var_names are lists corresponding respectively to
# [surface, satellite] var_names
ghg_data_variable_var_name_mapping = {
    "carbon_dioxide": [
        ["flux_foss", "flux_foss"],
        ["flux_apos_bio", "flux_apos"],
    ],
    "methane": [
        "ch4_emis_total",
        "ch4_emis_biomass_burning",
    ],
    "nitrous_oxide": "N2O",
}

ghg_data_variable_default_plot_title_mapping = {
    "carbon_dioxide": "CO2",
    "methane": "CH4",
    "nitrous_oxide": "N2O",
}

ghg_data_variables = list(ghg_data_variable_var_name_mapping.keys())
