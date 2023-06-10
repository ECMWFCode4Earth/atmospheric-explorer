import cdsapi
import zipfile
import requests
import os
import sys
import glob

data_dir = os.path.dirname(sys.argv[0])

c = cdsapi.Client()
c.retrieve(
    'cams-global-reanalysis-eac4',
    {
        'format': 'netcdf',
        'variable': [
            'total_aerosol_optical_depth_1240nm', 'total_aerosol_optical_depth_469nm', 'total_aerosol_optical_depth_550nm',
            'total_aerosol_optical_depth_670nm', 'total_aerosol_optical_depth_865nm', 'total_column_carbon_monoxide',
            'total_column_ethane', 'total_column_formaldehyde', 'total_column_hydrogen_peroxide',
            'total_column_hydroxyl_radical', 'total_column_isoprene', 'total_column_methane',
            'total_column_nitric_acid', 'total_column_nitrogen_dioxide', 'total_column_nitrogen_monoxide',
            'total_column_ozone', 'total_column_peroxyacetyl_nitrate', 'total_column_propane',
            'total_column_sulphur_dioxide', 'total_column_water_vapour',
        ],
        'date': '2021-01-01/2021-01-31',
        'time': '00:00',
        'area': [
            47, 7, 36,
            18,
        ],
    },
    f'{data_dir}/italiaecmwf.nc')

# Download shapefile zip from naturalearthdata
shapefile_url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_ita.zip"
headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})
r = requests.get(shapefile_url, headers=headers)
# Save downloaded data to zip file
with open(f"{data_dir}/italy_shapefile.zip", "wb") as f:
    f.write(r.content)
# Unzip file to directory
with zipfile.ZipFile(f"{data_dir}/italy_shapefile.zip", 'r') as zip_ref:
    zip_ref.extractall(f"{data_dir}/italy_shapefile")
# Remove zip file
os.remove(f"{data_dir}/italy_shapefile.zip")
# Rename all files inside zip
for file in glob.glob(f"{data_dir}/italy_shapefile/*"):
    ext = file.split('.')[-1]
    os.rename(file, f'{data_dir}/italy_shapefile/italy_shapefile.{ext}')