# tests/test_map.py

import pytest
from folium_wrapper import Map
import pandas as pd
import geopandas as gpd
import folium
import os


def test_map_initialization():
    mymap = Map(location=[0, 0], zoom_start=2)
    assert isinstance(mymap.map, folium.Map)
    assert mymap.map.location == [0, 0]
    
def test_add_circle_markers_from_df():
    # Sample DataFrame
    data = {
        'latitude': [10, 20, 30],
        'longitude': [40, 50, 60],
        'value': [1, 2, 3],
        'color': ['red', 'green', 'blue'],
        'radius': [5, 10, 15]
    }
    df = pd.DataFrame(data)
    
    mymap = Map(location=[20, 50], zoom_start=5)
    mymap.add_circle_markers_from_df(
        df,
        lat_col='latitude',
        lon_col='longitude',
        color='color',
        radius='radius',
        popup='value',
        fill=True,
        fill_color='color'
    )
    
    # Assert that markers were added to the map
    assert len(mymap.map._children) > 1  # At least one marker added

def test_add_circle_markers_from_geodf():
    # Sample GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'value': [1, 2],
        'color': ['purple', 'orange'],
        'radius': [7, 14]
    }, geometry=gpd.points_from_xy([10, 20], [40, 50])) # type: ignore
    gdf.set_crs(epsg=4326, inplace=True)
    
    mymap = Map()
    mymap.add_circle_markers_from_df(
        gdf,
        color='color',
        radius='radius',
        popup='value',
        fill=True,
        fill_color='color'
    )
    
    # Assert that markers were added
    assert len(mymap.map._children) > 1

def test_add_circle_markers_missing_columns():
    df = pd.DataFrame({
        'lat': [10],
        'lon': [20]
    })
    mymap = Map()
    with pytest.raises(KeyError):
        mymap.add_circle_markers_from_df(df, lat_col='latitude', lon_col='longitude')

def test_add_angles_from_df_missing_angle_col():
    df = pd.DataFrame({
        'latitude': [10],
        'longitude': [20],
        'angle_missing': [45]
    })
    mymap = Map()
    with pytest.raises(ValueError):
        mymap.add_angles_from_df(df, angle_col='angle', lat_col='latitude', lon_col='longitude')
