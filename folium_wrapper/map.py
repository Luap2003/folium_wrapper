# myfoliumwrapper/map.py

import folium
import pandas as pd
import geopandas as gpd
from typing import Union, Optional

class Map:
    def __init__(self, location=None, zoom_start=10, tiles='OpenStreetMap', **kwargs):
        if location is None:
            location = [0, 0]
        self.map = folium.Map(location=location, zoom_start=zoom_start, tiles=tiles, **kwargs)
    
    def add_circle_markers_from_df(
        self,
        df: Union[pd.DataFrame, gpd.GeoDataFrame],
        lat_col: Optional[str] = None,
        lon_col: Optional[str] = None,
        slice_obj: Optional[slice] = None,
        **kwargs
    ):
        """
        Adds circle markers to the map from a DataFrame or GeoDataFrame.

        Parameters:
        - df (DataFrame or GeoDataFrame): The data source.
        - lat_col (str, optional): Column name for latitude.
        - lon_col (str, optional): Column name for longitude.
        - slice_obj (slice, optional): A slice object to slice the DataFrame.
        - **kwargs: Additional arguments for folium.CircleMarker (can be scalar or column names).
        """
        # Apply slicing if slice_obj is provided
        if slice_obj is not None:
            df = df.iloc[slice_obj]

        # Determine if df is a GeoDataFrame
        is_geodf = isinstance(df, gpd.GeoDataFrame)

        # If GeoDataFrame and lat_col/lon_col not provided, extract coordinates from geometry
        if is_geodf and lat_col is None and lon_col is None:
            # Ensure geometry column is present and of Point type
            if df.geometry.is_empty.any():
                raise ValueError("GeoDataFrame contains empty geometries.")
            if not all(df.geometry.geom_type == 'Point'):
                raise ValueError("All geometries must be of Point type.")

            # Extract latitude and longitude from geometry
            df = df.copy()  # To avoid modifying the original DataFrame
            df['longitude'] = df.geometry.x
            df['latitude'] = df.geometry.y
            lat_col = 'latitude'
            lon_col = 'longitude'

        elif lat_col is None or lon_col is None:
            raise ValueError("lat_col and lon_col must be provided unless df is a GeoDataFrame with Point geometries.")

        # Separate scalar kwargs from those that are column-based
        scalar_kwargs = {}
        column_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str) and value in df.columns:
                column_kwargs[key] = value
            else:
                scalar_kwargs[key] = value

        for _, row in df.iterrows():
            marker_kwargs = scalar_kwargs.copy()
            for key, col in column_kwargs.items():
                marker_kwargs[key] = row[col]

            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                **marker_kwargs
            ).add_to(self.map)

    def add_angles_from_df(
        self,
        df: Union[pd.DataFrame, gpd.GeoDataFrame],
        angle_col: str,
        lat_col: Optional[str] = None,
        lon_col: Optional[str] = None,
        slice_obj: Optional[Union[slice, pd.Series]] = None,
        icon: str = 'arrow-up',
        prefix: str = 'fa',
        **kwargs
    ):
        """
        Adds markers with rotated icons to the map from a DataFrame or GeoDataFrame.

        Parameters:
        - df (DataFrame or GeoDataFrame): The data source.
        - angle_col (str): Column name for the angle (in degrees).
        - lat_col (str, optional): Column name for latitude. Required if df is a DataFrame.
        - lon_col (str, optional): Column name for longitude. Required if df is a DataFrame.
        - slice_obj (slice or Series, optional): A slice object or boolean Series to filter the DataFrame.
        - icon (str): Icon name (default is 'arrow-up').
        - prefix (str): Icon prefix, e.g., 'fa' for Font Awesome or 'glyphicon'.
        - **kwargs: Additional arguments for folium.Marker.

        Notes:
        - The angle should be in degrees.
        - If df is a GeoDataFrame with Point geometries, lat_col and lon_col can be omitted.
        - Ensure df is in WGS84 (EPSG:4326) coordinate reference system.
        """
        # Validate angle_col
        if angle_col not in df.columns:
            raise ValueError(f"Angle column '{angle_col}' not found in DataFrame.")

        # Apply slicing or boolean indexing
        if slice_obj is not None:
            df = df.loc[slice_obj]

        # Determine if df is a GeoDataFrame
        is_geodf = isinstance(df, gpd.GeoDataFrame)
 
        # If GeoDataFrame and lat_col/lon_col not provided, extract coordinates from geometry
        if is_geodf and lat_col is None and lon_col is None:
            if df.geometry.is_empty.any():
                raise ValueError("GeoDataFrame contains empty geometries.")
            if not all(df.geometry.geom_type == 'Point'):
                raise ValueError("All geometries must be of Point type.")

            # Extract latitude and longitude from geometry
            df = df.copy()
            df['longitude'] = df.geometry.x
            df['latitude'] = df.geometry.y
            lat_col = 'latitude'
            lon_col = 'longitude'

        elif lat_col is None or lon_col is None:
            raise ValueError("lat_col and lon_col must be provided unless df is a GeoDataFrame with Point geometries.")

        # Iterate over the DataFrame and add markers
        for _, row in df.iterrows():
            angle = row[angle_col]
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                icon=folium.Icon(icon=icon, prefix=prefix, angle=angle),
                **kwargs
            ).add_to(self.map)
        
    
    def save(self, filename):
        """Saves the map to an HTML file."""
        self.map.save(filename)
