"""\
Module to keep all mapping of data variables for the Streamlit application.
"""
from atmospheric_explorer.units_conversion import get_constants

const = get_constants()
# EAC4 mappings and data variables list
eac4_sl_data_variable_var_name_mapping = {
    s: const[s]["var_name"]
    for s in const.sections()
    if const[s]["database"] == "eac4" and const[s]["type"] == "single_level"
}
eac4_sl_data_variable_default_plot_title_mapping = {
    s: const[s]["default_title"]
    for s in const.sections()
    if const[s]["database"] == "eac4" and const[s]["type"] == "single_level"
}
eac4_sl_data_variables = list(eac4_sl_data_variable_var_name_mapping.keys())
eac4_ml_data_variable_var_name_mapping = {
    s: const[s]["var_name"]
    for s in const.sections()
    if const[s]["database"] == "eac4" and const[s]["type"] == "multi_level"
}
eac4_ml_data_variable_default_plot_title_mapping = {
    s: const[s]["default_title"]
    for s in const.sections()
    if const[s]["database"] == "eac4" and const[s]["type"] == "multi_level"
}
eac4_ml_data_variables = list(eac4_ml_data_variable_var_name_mapping.keys())
eac4_pressure_levels = [
    "1",
    "2",
    "3",
    "5",
    "7",
    "10",
    "20",
    "30",
    "50",
    "70",
    "100",
    "150",
    "200",
    "250",
    "300",
    "400",
    "500",
    "600",
    "700",
    "800",
    "850",
    "900",
    "925",
    "950",
    "1000",
]
eac4_model_levels = [str(m_level) for m_level in range(1, 61, 1)]
eac4_times = [f"{h:02}:00" for h in range(0, 24, 3)]
# GHG mappings and data variables list
# ! We are only considering surface_flux quantities
# carbon_dioxide var_names are lists corresponding respectively to
# [surface, satellite] var_names
ghg_data_variable_var_name_mapping = {
    "carbon_dioxide": [
        "flux_foss",
        "flux_apos_bio",
        "flux_apos_ocean",
        "flux_apri_bio",
        "flux_apri_ocean",
    ],
    "methane": [
        "ch4_emis_total",
        "ch4_emis_biomass_burning",
    ],
    "nitrous_oxide": ["N2O"],
}

ghg_data_variable_default_plot_title_mapping = {
    s: const[s]["default_title"]
    for s in const.sections()
    if const[s]["database"] == "ghg"
}

ghg_data_variables = list(ghg_data_variable_var_name_mapping.keys())
