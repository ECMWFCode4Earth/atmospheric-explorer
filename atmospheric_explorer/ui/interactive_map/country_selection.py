"""\
Module to extract selected countries from the folium map click event.
"""
from shapely.geometry import shape

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.ui.utils import shapefile_dataframe

logger = get_logger("atmexp")


def get_admin(out_event) -> str | None:
    """Get admin from folium map click event"""
    if out_event.get("last_active_drawing") is not None:
        if out_event["last_active_drawing"].get("properties") is not None:
            return out_event["last_active_drawing"]["properties"].get("ADMIN")
    return None


def countries_selection(out_event: dict) -> dict:
    """\
    Select one or more countries based on the type of event returned by folium.

    If the event has the ADMIN key, this will be interpreted as a country polygon
    and ADMIN will be used to select the exact country.

    If the event doesn't have the ADMIN key, this will be interpreted as a free polygon.
    All countries which intersect such polygon will be returned.
    """
    if out_event.get("last_active_drawing") is not None:
        shapefile = shapefile_dataframe()
        polygon = shape(out_event["last_active_drawing"]["geometry"])
        admin = get_admin(out_event)
        if admin is not None:
            return {
                admin:shapefile[shapefile["ADMIN"] == admin].geometry.iloc[0]
            }
        sh_filtered = shapefile[~polygon.intersection(shapefile["geometry"]).is_empty]
        return {
            admin:sh_filtered[sh_filtered["ADMIN"] == admin].geometry.iloc[0]
            for admin in sh_filtered["ADMIN"]
        }
    return dict()
