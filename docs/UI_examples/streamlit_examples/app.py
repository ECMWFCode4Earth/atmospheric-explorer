import geopandas as gpd
import pandas as pd
from io import BytesIO
import requests
import pydeck as pdk
from pydeck.types import String
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium

url_to_download    = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_map_units.zip"
headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})
r = requests.get(url_to_download, headers=headers)
shapefile = gpd.read_file(BytesIO(r.content))
shapes = shapefile['geometry']
countries = shapefile.copy()
countries.index = countries.GEOUNIT
countries['name'] = countries.GEOUNIT

# PYDECK
# geo_layer = pdk.Layer(
#     'GeoJsonLayer',
#     data = shapefile.__geo_interface__,
#     id=1,
#     pickable=True,
#     auto_highlight=True,
#     get_fill_color=[120, 0, 120, 50],
#     get_line_color=[0, 0, 0, 255],
#     lineWidthMinPixels = 0.8
# )
# text_info = pd.DataFrame({"name": ["Test"], "coordinates": [[-50.38666, 37.599787]]})
# text_layer = pdk.Layer(
#     type = "TextLayer",
#     data = text_info,
#     id=2,
#     pickable=True,
#     get_position="coordinates",
#     get_text="name",
#     get_size=24,
#     get_color=[0, 0, 0],
#     get_text_anchor=String("middle"),
#     get_alignment_baseline=String("center"),
# )
# view_state = pdk.ViewState(latitude=-1, longitude=-122.4194155, zoom=1)

# def test_click(widget_instance, payload):
#     try:
#         st.write(payload['data']['object']['properties']['ADMIN'])
#     except KeyError:
#         pass

# r = pdk.Deck(
#     map_style='road',
#     layers=[geo_layer, text_layer],
#     initial_view_state=view_state,
#     tooltip=False
# )
# r.deck_widget.on_click(test_click)
# st.pydeck_chart(r)

def folium_map():
    m = folium.Map(location=[45.5236, -122.6750], min_zoom=1)
    folium.GeoJson(shapefile.to_json(), name="geojson", tooltip='ADMIN').add_to(m)
    return m

try:
    m = folium_map()
    data = st_folium(m, key='folium_map', returned_objects=["last_active_drawing"])
    st.write(data['last_active_drawing']['properties']['ADMIN'])
except:
    pass