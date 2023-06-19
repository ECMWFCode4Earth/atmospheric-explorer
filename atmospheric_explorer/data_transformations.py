"""\
Data transformations needed for the plotting api
"""
import geopandas as gpd
import xarray as xr
from shapely.geometry import mapping

from atmospheric_explorer.shapefile import ShapefilesDownloader


def clip_and_concat_countries(
    data_frame: xr.Dataset, countries: list[str]
) -> xr.Dataset:
    """Clips data_frame keeping only countries specified. Countries must be a list of country names"""
    # Download shapefile
    sh_downloader = ShapefilesDownloader(resolution="10m", instance="countries")
    sh_downloader.download_shapefile()
    sh_dataframe = gpd.read_file(sh_downloader.shapefile_full_path, crs="EPSG:4326")
    # all_touched=True questo parametro include tutti i pixel toccati dal poligono definito
    # se False include solo i pixel il cui centro è incluso nel poligono
    # approvato all_touched=True
    df_clipped_concat = data_frame.rio.clip(
        sh_dataframe[sh_dataframe["ADMIN"] == countries[0]].geometry.apply(mapping),
        sh_dataframe.crs,
        drop=True,
        all_touched=True,
    )
    df_clipped_concat = df_clipped_concat.expand_dims({"admin": [countries[0]]})
    for country in countries[1:]:
        df_clipped = data_frame.rio.clip(
            sh_dataframe[sh_dataframe["ADMIN"] == country].geometry.apply(mapping),
            sh_dataframe.crs,
            drop=True,
            all_touched=True,
        )
        df_clipped = df_clipped.expand_dims({"admin": [country]})
        df_clipped_concat = xr.concat([df_clipped_concat, df_clipped], dim="admin")
    return df_clipped_concat
