import streamlit as st
import cdsapi
import os
import sys
import requests
import zipfile
import glob
from streamlit_folium import st_folium
import geopandas as gpd
import folium
from io import BytesIO

st.title("Atmospheric Explorer POC")
with st.sidebar:
    st.title("Atmospheric Explorer POC")
progress = st.text("Create data folder")
data_dir = os.path.dirname(sys.argv[0]) + '/.data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Download earth shapefile zip from naturalearthdata
if not os.path.exists(f"{data_dir}/world_shapefile.zip"):
    progress.text("Download world shapefile")
    shapefile_url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    r = requests.get(shapefile_url, headers=headers)
    # Save downloaded data to zip file
    with open(f"{data_dir}/world_shapefile.zip", "wb") as f:
        f.write(r.content)
# # Unzip file to directory
# with zipfile.ZipFile(f"{data_dir}/world_shapefile.zip", 'r') as zip_ref:
#     zip_ref.extractall(f"{data_dir}/world_shapefile")
# # Remove zip file
# os.remove(f"{data_dir}/world_shapefile.zip")
# # Rename all files inside zip
# for file in glob.glob(f"{data_dir}/world_shapefile/*"):
#     ext = file.split('.')[-1]
#     os.rename(file, f'{data_dir}/world_shapefile/world_shapefile.{ext}')

# # Download CAMS data
# st.write("Download CAMS data")
# c = cdsapi.Client()
# c.retrieve(
#     'cams-global-reanalysis-eac4',
#     {
#         'format': 'netcdf',
#         'variable': [
#             'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm', 'total_aerosol_optical_depth_550nm',
#             'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm', 'total_column_carbon_monoxide',
#             'total_column_ethane', 'total_column_formaldehyde', 'total_column_hydrogen_peroxide',
#             'total_column_hydroxyl_radical', 'total_column_isoprene', 'total_column_methane',
#             'total_column_nitric_acid', 'total_column_nitrogen_dioxide', 'total_column_nitrogen_monoxide',
#             'total_column_ozone', 'total_column_peroxyacetyl_nitrate', 'total_column_propane',
#             'total_column_sulphur_dioxide', 'total_column_water_vapour',
#         ],
#         'date': '2021-01-01/2021-01-31',
#         'time': '00:00',
#         'area': [
#             47, 7, 36,
#             18,
#         ],
#     },
#     f'{data_dir}/italiaecmwf.nc')

progress.text("Reading world shapefile")
if os.path.exists(f"{data_dir}/world_shapefile.zip"):
    shapefile = gpd.read_file(f"{data_dir}/world_shapefile.zip")
else:
    shapefile = gpd.read_file("https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_ita.zip")
shapes = shapefile['geometry']
countries = shapefile.copy()
countries.index = countries.GEOUNIT
countries['name'] = countries.GEOUNIT

def folium_map():
    m = folium.Map()
    folium.GeoJson(shapefile.to_json(), name="geojson", tooltip='ADMIN').add_to(m)
    # if selection:
    #     folium.GeoJson(selection.to_json(), name="geojson_selection").add_to(m)
    return m

progress.text("Done")
try:
    m = folium_map()
    st.session_state['country_selection'] = st_folium(m, key='folium_map', returned_objects=["last_active_drawing"])
    with st.sidebar:
        st.write(f"Selected country: {st.session_state['country_selection']['last_active_drawing']['properties']['ADMIN']}")
except:
    pass

st.write("Plots")