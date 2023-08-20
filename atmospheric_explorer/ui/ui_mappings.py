"""\
Module to keep all mapping of data variables for the Streamlit application.
"""

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
    "carbon_dioxide": "CO2",
    "methane": "CH4",
    "nitrous_oxide": "N2O",
}

ghg_data_variables = list(ghg_data_variable_var_name_mapping.keys())
