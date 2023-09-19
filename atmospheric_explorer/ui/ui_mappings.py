"""\
Module to keep all mapping of data variables for the Streamlit application.
"""
from atmospheric_explorer.api.data_interface.eac4 import EAC4Config
from atmospheric_explorer.api.data_interface.ghg import GHGConfig

# EAC4 mappings and data variables list
eac4_config = EAC4Config.get_config()
eac4_times = eac4_config["time_values"]
eac4_pressure_levels = eac4_config["pressure_levels"]
eac4_model_levels = eac4_config["model_levels"]
eac4_sl_data_variable_var_name_mapping = {
    k: v["short_name"]
    for k, v in eac4_config["variables"].items()
    if v["var_type"] == "single_level"
}
eac4_sl_data_variable_default_plot_title_mapping = {
    k: v["long_name"]
    for k, v in eac4_config["variables"].items()
    if v["var_type"] == "single_level"
}
eac4_sl_data_variables = list(eac4_sl_data_variable_var_name_mapping.keys())
eac4_ml_data_variable_var_name_mapping = {
    k: v["short_name"]
    for k, v in eac4_config["variables"].items()
    if v["var_type"] == "multi_level"
}
eac4_ml_data_variable_default_plot_title_mapping = {
    k: v["long_name"]
    for k, v in eac4_config["variables"].items()
    if v["var_type"] == "multi_level"
}
eac4_ml_data_variables = list(eac4_ml_data_variable_var_name_mapping.keys())
ghg_config = GHGConfig.get_config()
ghg_data_variable_var_name_mapping = {
    k: [
        var["var_name"]
        for var in v["surface_flux"]["monthly_mean"]
        if "area" not in var["var_name"]
    ]
    for k, v in ghg_config["variables"].items()
}
ghg_data_variable_default_plot_title_mapping = {
    k: [
        var["long_name"]
        for var in v["surface_flux"]["monthly_mean"]
        if "area" not in var["var_name"]
    ]
    for k, v in ghg_config["variables"].items()
}
ghg_data_variables = list(ghg_data_variable_var_name_mapping.keys())
