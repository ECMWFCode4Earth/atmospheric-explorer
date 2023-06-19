from math import ceil

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import rioxarray
import statsmodels.stats.api as sms
import xarray as xr
from plotly.subplots import make_subplots
from shapely.geometry import mapping

from atmospheric_explorer.cams_interfaces import (
    EAC4Instance,
    InversionOptimisedGreenhouseGas,
)
from atmospheric_explorer.shapefile import ShapefilesDownloader
from atmospheric_explorer.units_conversion import convert_units_array


def clip_and_concat_countries(df, countries):
    # Download shapefile
    sh_down = ShapefilesDownloader(resolution="10m", instance="countries")
    sh_down.download_shapefile()
    sh = gpd.read_file(sh_down.shapefile_full_path, crs="EPSG:4326")
    # all_touched=True questo parametro include tutti i pixel toccati dal poligono definito, se False include solo i pixel il cui centro è incluso nel poligono
    # approvato all_touched=True
    df_clipped_concat = df.rio.clip(
        sh[sh["ADMIN"] == countries[0]].geometry.apply(mapping),
        sh.crs,
        drop=True,
        all_touched=True,
    )[["flux_foss"]]
    df_clipped_concat = df_clipped_concat.expand_dims({"admin": [countries[0]]})
    for c in countries[1:]:
        df_clipped = df.rio.clip(
            sh[sh["ADMIN"] == c].geometry.apply(mapping),
            sh.crs,
            drop=True,
            all_touched=True,
        )[["flux_foss"]]
        df_clipped = df_clipped.expand_dims({"admin": [c]})
        df_clipped_concat = xr.concat([df_clipped_concat, df_clipped], dim="admin")
    return df_clipped_concat


def line_with_ci_subplots(df, countries, col_num, unit, title=None):
    fig = make_subplots(
        rows=ceil(len(countries) / 2),
        cols=col_num if len(countries) >= col_num else len(countries),
        subplot_titles=countries,
        horizontal_spacing=0.04,
        vertical_spacing=0.1,
    )
    for i, admin in enumerate(countries):
        r = i // 2 + 1
        c = i % 2 + 1
        df_admin = df[df["admin"] == admin]
        times = df_admin.index.tolist()
        times_rev = times[::-1]
        y1 = df_admin["mean"].to_list()
        y1_upper = df_admin["upper"].to_list()
        y1_lower = df_admin["lower"].to_list()
        y1_lower = y1_lower[::-1]
        fig.add_trace(
            go.Scatter(
                x=times + times_rev,
                y=y1_upper + y1_lower,
                fill="toself",
                fillcolor="rgba(0,100,200,0.2)",
                line_color="rgba(0,100,200,0.2)",
                showlegend=False,
                mode="lines",
            ),
            row=r,
            col=c,
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=y1,
                line_color="rgb(0,100,200)",
                name=admin,
                mode="lines+markers",
                showlegend=False,
            ),
            row=r,
            col=c,
        )
    last_axes = [f"y{i}" for i in range(len(countries) + 1)[-2:]]
    fig.update_xaxes(title="Years", selector=lambda a: a.anchor in last_axes)
    fig.update_yaxes(title=unit, col=1)
    fig.update_layout(
        title={"text": title, "x": 0.5, "font": {"size": 19}},
        height=110 * len(countries),
    )
    return fig


def plot_line_with_ci(quantity, countries, years, months, title, col_num=2):
    var_name = "flux_foss"
    # Download surface data file
    surface_data = InversionOptimisedGreenhouseGas(
        data_variables=quantity,
        file_format="zip",
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    surface_data.download()
    # Download satellite data file
    satellite_data = InversionOptimisedGreenhouseGas(
        data_variables=quantity,
        file_format="zip",
        quantity="surface_flux",
        input_observations="satellite",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    satellite_data.download()
    # Read data as dataset
    df_surface = surface_data.read_dataset(var_name=var_name)
    df_satellite = satellite_data.read_dataset(var_name=var_name)
    df = xr.combine_by_coords([df_surface, df_satellite], combine_attrs="override")
    df = df.rio.write_crs("EPSG:4326")
    # Clip countries
    df = clip_and_concat_countries(df, countries)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df = (
        df.where(~df[var_name].isnull(), drop=True)
        .sortby("time")
        .mean(dim=["longitude", "latitude"])
    )
    # Convert units
    da_converted = convert_units_array(df[var_name], quantity)
    unit = da_converted.attrs["units"]
    # Xarray doesn't cover all pandas functionalities, we need to convert it to a pandas dataframe
    df_pandas = pd.DataFrame(
        da_converted.to_pandas().unstack(), columns=[var_name]
    ).reset_index()
    df_pandas["year"] = df_pandas["time"].dt.year
    df_pandas = df_pandas.groupby(["year", "admin"]).agg(
        mean=(var_name, "mean"),
        ci=(var_name, lambda d: sms.DescrStatsW(d).tconfint_mean()),
    )
    df_pandas.reset_index("admin", inplace=True)
    df_pandas[["lower", "upper"]] = pd.DataFrame(
        df_pandas["ci"].to_list(), index=df_pandas.index
    )
    # Generate subplots
    return line_with_ci_subplots(df_pandas, countries, col_num, unit, title)


### SAME FUNCTIONS WITH PLOTLY EXPRESS


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


def add_ci(fig, trace, df, countries):
    linecolor = ",".join([str(n) for n in hex_to_rgb(trace.line.color)])
    for i, admin in enumerate(countries):
        r = ceil((len(countries) - i) / 2)
        c = i % 2 + 1
        df_admin = df[df["admin"] == admin]
        times = df_admin.index.tolist()
        times_rev = times[::-1]
        y1_upper = df_admin["upper"].to_list()
        y1_lower = df_admin["lower"].to_list()
        y1_lower = y1_lower[::-1]
        fig.add_trace(
            go.Scatter(
                x=times + times_rev,
                y=y1_upper + y1_lower,
                fill="toself",
                fillcolor=f"rgba({linecolor}, 0.1)",
                line_color=f"rgba({linecolor}, 0)",
                showlegend=False,
                mode="lines",
            ),
            row=r,
            col=c,
        )


def line_with_ci_subplots_express(df, countries, col_num, unit, title):
    fig = px.line(
        data_frame=df,
        y="mean",
        color="input_observations",
        facet_col="admin",
        facet_col_wrap=col_num,
        facet_col_spacing=0.04,
        facet_row_spacing=0.1,
        category_orders={"admin": countries},
    )
    fig.update_traces(mode="lines+markers")
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("admin=")[-1], font={"size": 14})
    )
    fig.for_each_trace(
        lambda tr: add_ci(
            fig, tr, df[df["input_observations"] == tr.legendgroup], countries
        )
    )
    # last_axes_anchor = [f"y{i}" for i in range(len(countries)+1)[-2:]]
    # fig.update_xaxes(title='Years', selector=lambda a: a.anchor in last_axes_anchor)
    fig.update_yaxes(title=unit, col=1)
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(showticklabels=True, matches=None)
    fig.update_layout(
        title={"text": title, "x": 0.5, "font": {"size": 19}},
        height=110 * len(countries),
    )
    return fig


def plot_line_with_ci_express(quantity, countries, years, months, title, col_num=2):
    var_name = "flux_foss"
    # Download surface data file
    surface_data = InversionOptimisedGreenhouseGas(
        data_variables=quantity,
        file_format="zip",
        quantity="surface_flux",
        input_observations="surface",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    surface_data.download()
    # Download satellite data file
    satellite_data = InversionOptimisedGreenhouseGas(
        data_variables=quantity,
        file_format="zip",
        quantity="surface_flux",
        input_observations="satellite",
        time_aggregation="monthly_mean",
        year=years,
        month=months,
    )
    satellite_data.download()
    # Read data as dataset
    df_surface = surface_data.read_dataset(var_name=var_name)
    df_satellite = satellite_data.read_dataset(var_name=var_name)
    df = xr.combine_by_coords([df_surface, df_satellite], combine_attrs="override")
    df = df.rio.write_crs("EPSG:4326")
    # Clip countries
    df = clip_and_concat_countries(df, countries)
    # Drop all values that are null over all coords, compute the mean of the remaining values over long and lat
    df = (
        df.where(~df[var_name].isnull(), drop=True)
        .sortby("time")
        .mean(dim=["longitude", "latitude"])
    )
    # Convert units
    da_converted = convert_units_array(df[var_name], quantity).squeeze(
        "time_aggregation"
    )
    unit = da_converted.attrs["units"]
    # Xarray doesn't cover all pandas functionalities, we need to convert it to a pandas dataframe
    df_pandas = pd.DataFrame(
        da_converted.stack(stacked_dim=([...])).to_pandas(), columns=[var_name]
    ).reset_index()
    df_pandas["year"] = df_pandas["time"].dt.year
    df_pandas = df_pandas.groupby(["year", "admin", "input_observations"]).agg(
        mean=(var_name, "mean"),
        ci=(var_name, lambda d: sms.DescrStatsW(d).tconfint_mean()),
    )
    df_pandas.reset_index(["admin", "input_observations"], inplace=True)
    df_pandas[["lower", "upper"]] = pd.DataFrame(
        df_pandas["ci"].to_list(), index=df_pandas.index
    )
    # Generate subplots
    return line_with_ci_subplots_express(df_pandas, countries, col_num, unit, title)
