import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from unittest.mock import patch
import importlib.resources
# Import your Geo_Algorithms class
from folium_wrapper import Geo_Algorithms 


# Mock GPS data
mock_gps_data = pd.DataFrame({
    'latitude': [49.9, 50.05, 50.1, 50.15],
    'longitude': [7.9, 8.05, 8.1, 8.15],
    'richtung': [0, 90, 180, 270],  # Assuming 'richtung' is a column used in your code
    # Include any other necessary columns
})


# Test for _create_buffers
def test_create_buffers():
    geo_algo = Geo_Algorithms()
    gdf_tunnel_entry, gdf_tunnel_exit = geo_algo._create_buffers()

    # Assertions
    assert isinstance(gdf_tunnel_entry, gpd.GeoDataFrame), "gdf_tunnel_entry should be a GeoDataFrame"
    assert isinstance(gdf_tunnel_exit, gpd.GeoDataFrame), "gdf_tunnel_exit should be a GeoDataFrame"
    assert 'buffer' in gdf_tunnel_entry.columns, "gdf_tunnel_entry should have a 'buffer' column"
    assert 'buffer' in gdf_tunnel_exit.columns, "gdf_tunnel_exit should have a 'buffer' column"
    assert not gdf_tunnel_entry['buffer'].isnull().any(), "Buffers should not be null in gdf_tunnel_entry"
    assert not gdf_tunnel_exit['buffer'].isnull().any(), "Buffers should not be null in gdf_tunnel_exit"
